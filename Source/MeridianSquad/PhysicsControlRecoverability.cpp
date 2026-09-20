#include "PhysicsControlDummy.h"
#include "CombatProjectileWorld.h"
#include "PhysicsControlComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "PhysicsEngine/BodyInstance.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/SkeletalBodySetup.h"
#include "Engine/World.h"
#include "Dom/JsonObject.h"

namespace
{
FVector Flat97(FVector V) { V.Z = 0; return V; }
TSharedPtr<FJsonValue> Vector97(const FVector& V)
{
    return MakeShared<FJsonValueArray>(TArray<TSharedPtr<FJsonValue>>{
        MakeShared<FJsonValueNumber>(V.X), MakeShared<FJsonValueNumber>(V.Y), MakeShared<FJsonValueNumber>(V.Z)});
}
double Cross97(const FVector& A, const FVector& B, const FVector& C)
{ return (B.X-A.X)*(C.Y-A.Y)-(B.Y-A.Y)*(C.X-A.X); }
// Small convex support hull from the contact-feasible footprint corners.
FVector Outside97(TArray<FVector> Points, const FVector& P)
{
    if (Points.Num() < 2) return FVector(1000,0,0);
    if (Points.Num() == 2) return Flat97(P-FMath::ClosestPointOnSegment(P,Points[0],Points[1]));
    Points.Sort([](const FVector& A, const FVector& B) { return A.X == B.X ? A.Y < B.Y : A.X < B.X; });
    TArray<FVector> Hull;
    for (const FVector& V : Points)
    {
        while (Hull.Num() >= 2 && Cross97(Hull[Hull.Num()-2], Hull.Last(), V) <= 0) Hull.Pop(EAllowShrinking::No);
        Hull.Add(V);
    }
    const int32 Lower = Hull.Num();
    for (int32 I = Points.Num()-2; I >= 0; --I)
    {
        while (Hull.Num() > Lower && Cross97(Hull[Hull.Num()-2], Hull.Last(), Points[I]) <= 0) Hull.Pop(EAllowShrinking::No);
        Hull.Add(Points[I]);
    }
    bool Inside = true;
    FVector Closest = Hull[0];
    double Distance = TNumericLimits<double>::Max();
    for (int32 I = 1; I < Hull.Num(); ++I)
    {
        Inside &= Cross97(Hull[I-1], Hull[I], P) >= -.01;
        const FVector Q = FMath::ClosestPointOnSegment(P, Hull[I-1], Hull[I]);
        const double D = FVector::DistSquared2D(P,Q);
        if (D < Distance) { Distance = D; Closest = Q; }
    }
    return Inside ? FVector::ZeroVector : Flat97(P-Closest);
}
}

void APhysicsControlDummy::ResetRecoverability()
{
    RecoveryFeet[0] = FRecoveryFoot(); RecoveryFeet[1] = FRecoveryFoot();
    RecoveryCOM = RecoveryVelocity = CapturePoint = CaptureError = FVector::ZeroVector;
    RecoveryInvalidSeconds = RecoveryNoProgressSeconds = RecoveryStableSeconds = StepRequestSeconds = 0;
    CaptureDistance = RequiredReach = BodyAngularSpeed = RecoveryEffortRatio = 0;
    RecoveryBestError = GroundContactAge = 1000;
    RecoveryForceLimit = RecoveryTorqueLimit = 0;
    DisturbedFoot = NAME_None;
    LegContacts.Reset();
    bRecoveryFeasible = true;
    bRecoverySampled = false;
    RecoveryReason = TEXT("awaiting physical contact");
}

void APhysicsControlDummy::OnBodyContact(UPrimitiveComponent* HitComponent, AActor* OtherActor,
    UPrimitiveComponent* OtherComponent, FVector NormalImpulse, const FHitResult& Hit)
{
    if (!OtherComponent) return;
    if (OtherComponent->GetCollisionObjectType() == ECC_WorldStatic &&
        Hit.ImpactNormal.Z > .65 && NormalImpulse.Size() > .01)
    {
        GroundContactAge = 0;
        for (int32 I = 0; I < 2; ++I)
            if (Hit.MyBoneName == (I == 0 ? TEXT("foot_l") : TEXT("foot_r")))
            {
                RecoveryFeet[I].ContactAge = 0;
                RecoveryFeet[I].NormalImpulse = NormalImpulse.Size();
            }
    }
    if (OtherComponent != Body || NormalImpulse.Size() < .01) return;
    const FString A = Hit.MyBoneName.ToString(), B = Hit.BoneName.ToString();
    auto Leg = [](const FString& N) { return N.StartsWith(TEXT("thigh")) || N.StartsWith(TEXT("calf")) || N.StartsWith(TEXT("foot")); };
    if (!Leg(A) || !Leg(B) || A.Right(2) == B.Right(2)) return;
    auto Contact = MakeShared<FJsonObject>();
    Contact->SetNumberField(TEXT("world_time"), GetWorld()->GetTimeSeconds());
    Contact->SetStringField(TEXT("a"), A); Contact->SetStringField(TEXT("b"), B);
    Contact->SetField(TEXT("point"), Vector97(Hit.ImpactPoint));
    Contact->SetField(TEXT("normal_impulse"), Vector97(NormalImpulse));
    for (const FName Bone : {Hit.MyBoneName, Hit.BoneName})
        if (const auto* BI = Body->GetBodyInstance(Bone))
            Contact->SetField(Bone.ToString()+TEXT("_velocity"), Vector97(BI->GetUnrealWorldVelocity()));
    // A bounded diagnostic ring; collision itself is solved exclusively by Chaos.
    if (LegContacts.Num() >= 128) LegContacts.RemoveAt(0,1,EAllowShrinking::No);
    LegContacts.Add(MakeShared<FJsonValueObject>(Contact));
}

APhysicsControlDummy::FRecoveryFoot APhysicsControlDummy::MeasureFoot(FName Bone, const FRecoveryFoot& Previous) const
{
    FRecoveryFoot Result = Previous;
    Result.bUsable = Result.bContact = false;
    Result.Footprint.Reset(); Result.FootprintPoints = 0;
    const auto* BI = Body->GetBodyInstance(Bone);
    const auto* Asset = Body->GetPhysicsAsset();
    const int32 Index = Asset->FindBodyIndex(Bone);
    if (!BI || Index == INDEX_NONE) return Result;
    const auto& Shapes = Asset->SkeletalBodySetups[Index]->AggGeom.BoxElems;
    if (Shapes.Num() != 1) return Result;
    const auto& Shape = Shapes[0];
    const FTransform Actual = BI->GetUnrealWorldTransform();
    const FTransform Box = Shape.GetTransform() * Actual;
    const FVector Extent(Shape.X*.5,Shape.Y*.5,Shape.Z*.5);
    const FVector Velocity = BI->GetUnrealWorldVelocity();
    Result.Slip = Velocity.Size2D(); Result.VerticalSpeed = Velocity.Z;
    const float Bottom = ShapeBottom(Bone,Actual);
    FHitResult Floor;
    FVector Center = Box.GetLocation(); Center.Z = Bottom;
    if (!FindFloor(Center,3,Floor) || Floor.ImpactNormal.Z < .996) return Result;
    Result.Gap = Bottom-Floor.ImpactPoint.Z;
    // Actual solver contact + near-contact geometry + contact velocity. A floor
    // ray alone never carries load. Preserve sleeping contact only while close.
    Result.bContact = (Result.ContactAge < .16f || (!BI->IsInstanceAwake() && Previous.bContact)) &&
        Result.Gap >= -2.f && Result.Gap <= .8f;
    for (float X : {-1.f,1.f}) for (float Y : {-1.f,1.f}) for (float Z : {-1.f,1.f})
    {
        const FVector Corner = Box.TransformPosition(Extent*FVector(X,Y,Z));
        // Only the low face/edge can carry weight; elevated corners do not widen support.
        if (Corner.Z > Bottom+3.f) continue;
        FHitResult ContactFloor;
        if (!FindFloor(Corner,3,ContactFloor) || ContactFloor.ImpactNormal.Z < .996 ||
            FMath::Abs(ContactFloor.ImpactPoint.Z-Floor.ImpactPoint.Z) > .6f) continue;
        Result.Footprint.Add(Flat97(Corner));
        ++Result.FootprintPoints;
    }
    Result.bUsable = Result.bContact && Result.FootprintPoints >= 2 &&
        Result.Slip < 55.f && FMath::Abs(Result.VerticalSpeed) < 45.f;
    return Result;
}

void APhysicsControlDummy::UpdateRecoverability(float Dt)
{
    const float EvaluationDt = bRecoverySampled ? Dt : 0;
    bRecoverySampled = true;
    const auto* World = ACombatProjectileWorld::Find(GetWorld());
    bRecoveryAssistance = World && World->bRecoveryAssistance;
    EffectiveStrength = FMath::Clamp(RecoveryStrength*(bRecoveryAssistance ? 1.5f : 1.f), .25f, 2.f);
    EffectiveSpeed = FMath::Clamp(RecoverySpeed*(bRecoveryAssistance ? 1.2f : 1.f), .5f, 1.8f);
    EffectiveReach = FMath::Clamp(StepMaxReach+(bRecoveryAssistance ? 5.f : 0.f),12.f,45.f);
    EffectivePersistence = FMath::Clamp(RecoveryPersistenceSeconds*(bRecoveryAssistance ? 1.5f : 1.f),.5f,4.f);
    UsableFeet = 0;
    TArray<FVector> Points;
    for (int32 I=0; I<2; ++I)
    {
        RecoveryFeet[I] = MeasureFoot(I == 0 ? TEXT("foot_l") : TEXT("foot_r"),RecoveryFeet[I]);
        if (RecoveryFeet[I].bUsable) { ++UsableFeet; Points.Append(RecoveryFeet[I].Footprint); }
    }
    RecoveryCOM = RecoveryVelocity = FVector::ZeroVector; RecoveryMass = 0;
    for (auto* BI : Body->Bodies)
        if (BI && BI->IsValidBodyInstance())
        {
            const float Mass=BI->GetBodyMass(); RecoveryMass+=Mass;
            RecoveryCOM += BI->GetCOMPosition()*Mass;
            RecoveryVelocity += BI->GetUnrealWorldVelocity()*Mass;
        }
    RecoveryCOM /= FMath::Max(1.f,RecoveryMass); RecoveryVelocity /= FMath::Max(1.f,RecoveryMass);
    const float Height = FMath::Clamp(static_cast<float>(RecoveryCOM.Z-GroundHeight),35.f,130.f);
    CapturePoint = Flat97(RecoveryCOM + RecoveryVelocity*FMath::Sqrt(Height/980.f));
    CaptureError = Outside97(Points,CapturePoint); CaptureDistance=CaptureError.Size();
    LandingCaptureDistance=CaptureDistance;
    if (StepPhase && UsableFeet > 0)
    {
        // The swing foot is future support, never current load-bearing support.
        // Evaluate the already validated reachable landing as well as the live
        // stance; otherwise our own weight transfer falsely appears unrecoverable.
        FTransform Destination=SwingDestination;
        if (StepPlacement(SwingFoot,Destination,GroundHeight))
        {
            const auto* Asset=Body->GetPhysicsAsset();
            const int32 Index=Asset->FindBodyIndex(SwingFoot);
            if (Index != INDEX_NONE)
                for (const auto& Shape : Asset->SkeletalBodySetups[Index]->AggGeom.BoxElems)
                {
                    const FTransform Box=Shape.GetTransform()*Destination;
                    for (float X : {-1.f,1.f}) for (float Y : {-1.f,1.f}) for (float Z : {-1.f,1.f})
                        Points.Add(Flat97(Box.TransformPosition(FVector(X*Shape.X,Y*Shape.Y,Z*Shape.Z)*.5f)));
                }
            LandingCaptureDistance=Outside97(Points,CapturePoint).Size();
        }
    }
    RecoveryAcceleration = FMath::Min(380.f*EffectiveStrength,FMath::Clamp(RecoveryFriction,.1f,1.f)*980.f);
    const float Speed = RecoveryVelocity.Size2D();
    const float Response = FMath::Clamp(RecoveryReactionSeconds,.06f,.3f)/EffectiveSpeed;
    RequiredReach = LandingCaptureDistance + Speed*Response + Speed*Speed/(2*FMath::Max(1.f,RecoveryAcceleration));
    BodyAngularSpeed = Body->GetBodyInstance(TEXT("spine_05"))->GetUnrealWorldAngularVelocityInRadians().Size();
    const bool PoweredState = BalanceState == EDummyBalanceState::Standing || BalanceState == EDummyBalanceState::LosingBalance || BalanceState == EDummyBalanceState::Stepping;
    if (!PoweredState) return;
    StepRequestSeconds = bStepRequested ? StepRequestSeconds+Dt : 0;
    NoSupportSeconds = UsableFeet == 0 ? NoSupportSeconds+EvaluationDt : 0;
    const bool Capacity = UsableFeet > 0 && RequiredReach <= EffectiveReach+3 &&
        PoseLeanDegrees < FMath::Clamp(MaxLeanDegrees,20.f,55.f) && PelvisDrop < 42 && BodyAngularSpeed < 5;
    RecoveryInvalidSeconds = Capacity ? FMath::Max(0.f,RecoveryInvalidSeconds-Dt*2) : RecoveryInvalidSeconds+EvaluationDt;
    // Hits do not replenish these timers. Only actual error reduction, quiet
    // supported settling, or a completed useful placement counts as progress.
    if (CaptureDistance < RecoveryBestError-1.f)
    { RecoveryBestError=CaptureDistance; RecoveryNoProgressSeconds=0; }
    else if (StepPhase || bStepRequested || CaptureDistance > 4) RecoveryNoProgressSeconds += Dt;
    const bool Stable = UsableFeet == 2 && CaptureDistance < 3 && Speed < 12 && PoseLeanDegrees < 16 && !StepPhase;
    RecoveryStableSeconds = Stable ? RecoveryStableSeconds+Dt : 0;
    if (RecoveryStableSeconds > .3f && !bStepRequested)
    { RecoveryNoProgressSeconds=0; RecoveryBestError=CaptureDistance; }
    if (!bStepRequested && !StepPhase && StateSeconds > .35f && (CaptureDistance > 4 || UsableFeet == 1))
    { bStepRequested=true; StepRequestSeconds=0; }
    bRecoveryFeasible = NoSupportSeconds <= .14f && RecoveryInvalidSeconds <= .20f && RecoveryNoProgressSeconds <= EffectivePersistence;
    RecoveryReason = UsableFeet == 0 ? TEXT("no load-bearing contact") : RequiredReach > EffectiveReach+3 ? TEXT("momentum exceeds reachable braking placement") :
        PoseLeanDegrees >= FMath::Clamp(MaxLeanDegrees,20.f,55.f) || PelvisDrop >= 42 || BodyAngularSpeed >= 5 ? TEXT("body rotation or height exceeds capacity") :
        RecoveryNoProgressSeconds > EffectivePersistence ? TEXT("recovery made no measurable progress") : TEXT("supported recovery remains feasible");
    if (!bRecoveryFeasible) EnterFall(*RecoveryReason);
}

void APhysicsControlDummy::BoundRecoveryDrives(float Dt)
{
    if (IsDead() || BalanceState == EDummyBalanceState::Falling || BalanceState == EDummyBalanceState::Down) return;
    const bool GetUp = BalanceState == EDummyBalanceState::GettingUp;
    const bool Supported = GetUp ? (GroundContactAge < .20f || UsableFeet > 0) : UsableFeet > 0;
    RecoveryForceLimit = RecoveryTorqueLimit = RecoveryEffortRatio = 0;
    for (const auto& Entry : ReferencePose)
    {
        const FName Name = Entry.Key == TEXT("pelvis") ? PelvisControl : BodyControls.FindRef(Entry.Key);
        auto* BI=Body->GetBodyInstance(Entry.Key);
        if (Name.IsNone() || !BI) continue;
        FPhysicsControlData Data;
        if (!PhysicsControl->GetControlData(Name,Data)) continue;
        // UE force = kg*cm/s^2, torque = kg*cm^2/s^2. Limits remain nonzero
        // even while disabled: zero in PhysicsControl means UNLIMITED.
        const float Mass=BI->GetBodyMass();
        const float Acceleration=Entry.Key == TEXT("pelvis") ? 9000.f : 3500.f;
        Data.MaxForce=Mass*Acceleration*EffectiveStrength;
        Data.MaxTorque=Mass*180000.f*EffectiveStrength;
        Data.bEnabled=Supported;
        PhysicsControl->SetControlData(Name,Data);
        RecoveryForceLimit+=Data.MaxForce; RecoveryTorqueLimit+=Data.MaxTorque;
        const float Error=FVector::Distance(Entry.Value.GetLocation(),BI->GetUnrealWorldTransform().GetLocation());
        if (Entry.Key == TEXT("pelvis"))
            RecoveryEffortRatio=FMath::Max(RecoveryEffortRatio,Error*FMath::Square(2*PI*Data.LinearStrength)/(Acceleration*EffectiveStrength));
    }
    // No contact means no powered world-space suspension, even during the
    // short classification grace. Valid single support can power a transient lift.
    if (!Supported && GetUp)
    {
        StateSeconds=FMath::Max(0.f,StateSeconds-Dt);
        if (GroundContactAge > .6f) EnterFall(TEXT("get-up lost actual ground contact"));
    }
}

void APhysicsControlDummy::AddRecoverabilityState(TSharedPtr<FJsonObject> Root) const
{
    auto S=MakeShared<FJsonObject>();
    S->SetBoolField(TEXT("feasible"),bRecoveryFeasible);
    S->SetStringField(TEXT("reason"),RecoveryReason);
    S->SetBoolField(TEXT("assistance"),bRecoveryAssistance);
    S->SetField(TEXT("com"),Vector97(RecoveryCOM)); S->SetField(TEXT("velocity"),Vector97(RecoveryVelocity));
    S->SetField(TEXT("capture_point"),Vector97(CapturePoint)); S->SetField(TEXT("capture_error"),Vector97(CaptureError));
    S->SetNumberField(TEXT("mass_kg"),RecoveryMass);
    S->SetNumberField(TEXT("capture_distance_cm"),CaptureDistance);
    S->SetNumberField(TEXT("landing_capture_distance_cm"),LandingCaptureDistance);
    S->SetNumberField(TEXT("required_reach_cm"),RequiredReach);
    S->SetNumberField(TEXT("reach_limit_cm"),EffectiveReach);
    S->SetNumberField(TEXT("strength"),EffectiveStrength); S->SetNumberField(TEXT("speed"),EffectiveSpeed);
    S->SetNumberField(TEXT("persistence_limit_seconds"),EffectivePersistence);
    S->SetNumberField(TEXT("acceleration_limit_cm_s2"),RecoveryAcceleration);
    S->SetNumberField(TEXT("angular_speed_rad_s"),BodyAngularSpeed);
    S->SetNumberField(TEXT("invalid_seconds"),RecoveryInvalidSeconds);
    S->SetNumberField(TEXT("no_support_seconds"),NoSupportSeconds);
    S->SetNumberField(TEXT("no_progress_seconds"),RecoveryNoProgressSeconds);
    S->SetNumberField(TEXT("request_seconds"),StepRequestSeconds);
    S->SetNumberField(TEXT("body_ground_contact_age"),GroundContactAge);
    S->SetNumberField(TEXT("force_limit_sum_kg_cm_s2"),RecoveryForceLimit);
    S->SetNumberField(TEXT("torque_limit_sum_kg_cm2_s2"),RecoveryTorqueLimit);
    S->SetNumberField(TEXT("pelvis_demand_ratio"),RecoveryEffortRatio);
    S->SetStringField(TEXT("disturbed_foot"),DisturbedFoot.ToString());
    TArray<TSharedPtr<FJsonValue>> Feet;
    for (const auto& Foot : RecoveryFeet)
    {
        auto F=MakeShared<FJsonObject>();
        F->SetBoolField(TEXT("usable"),Foot.bUsable); F->SetBoolField(TEXT("contact"),Foot.bContact);
        F->SetNumberField(TEXT("gap_cm"),Foot.Gap); F->SetNumberField(TEXT("slip_cm_s"),Foot.Slip);
        F->SetNumberField(TEXT("vertical_cm_s"),Foot.VerticalSpeed);
        F->SetNumberField(TEXT("contact_age"),Foot.ContactAge); F->SetNumberField(TEXT("normal_impulse"),Foot.NormalImpulse);
        F->SetNumberField(TEXT("footprint_points"),Foot.FootprintPoints);
        Feet.Add(MakeShared<FJsonValueObject>(F));
    }
    S->SetArrayField(TEXT("feet"),Feet); S->SetArrayField(TEXT("leg_contacts"),LegContacts);
    Root->SetObjectField(TEXT("recoverability"),S);
}
