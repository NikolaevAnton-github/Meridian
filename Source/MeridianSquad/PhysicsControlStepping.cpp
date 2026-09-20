#include "PhysicsControlDummy.h"
#include "DummyRecoveryAnimInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "PhysicsEngine/BodyInstance.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/SkeletalBodySetup.h"
#include "Dom/JsonObject.h"

namespace
{
float Smooth(float Value) { return FMath::SmoothStep(0.f, 1.f, FMath::Clamp(Value, 0.f, 1.f)); }
FVector Flat(FVector Value) { Value.Z = 0; return Value; }
FVector AnklePosition(const USkeletalMeshComponent* Mesh, FName Bone)
{ return Mesh->GetBodyInstance(Bone)->GetUnrealWorldTransform().GetLocation(); }
bool FootBox(const USkeletalMeshComponent* Mesh, FName Bone, const FTransform& Foot, FTransform& Box, FVector& Extent)
{
    const auto* Asset = Mesh->GetPhysicsAsset();
    const int32 Index = Asset->FindBodyIndex(Bone);
    if (Index == INDEX_NONE || Asset->SkeletalBodySetups[Index]->AggGeom.BoxElems.Num() != 1) return false;
    const auto& Shape = Asset->SkeletalBodySetups[Index]->AggGeom.BoxElems[0];
    Box = Shape.GetTransform() * Foot;
    Extent = FVector(Shape.X, Shape.Y, Shape.Z) * .5;
    return true;
}
TSharedPtr<FJsonValue> StepVector(const FVector& V)
{
    return MakeShared<FJsonValueArray>(TArray<TSharedPtr<FJsonValue>>{
        MakeShared<FJsonValueNumber>(V.X), MakeShared<FJsonValueNumber>(V.Y), MakeShared<FJsonValueNumber>(V.Z)});
}
}

void APhysicsControlDummy::RememberStandingSkeleton(const USkeletalMeshComponent* Mesh)
{
    StandingBones.Reset();
    for (int32 I = 0; I < Mesh->GetNumBones(); ++I)
        StandingBones.Add(Mesh->GetSocketTransform(Mesh->GetBoneName(I)));
}

void APhysicsControlDummy::CancelStep()
{
    StepPhase = 0;
    bStepRequested = false;
    StepNoSupportSeconds = 0;
}

void APhysicsControlDummy::ResetStepping()
{
    CancelStep();
    StepSeconds = StepCooldownRemaining = StepSupportDrift = StepPeakSupportDrift = 0;
    EpisodeSteps = StepsStarted = StepsCompleted = StepsRejected = 0;
    SwingFoot = PlantedFoot = NAME_None;
    SwingStart = SwingDestination = PlantedTarget = FTransform::Identity;
    PlantedActualStart = FVector::ZeroVector;
    StepDirection = StepBodyDirection = LastStepImpulse = StepDisplacement = StepTransfer = FVector::ZeroVector;
    StepStartBones.Reset(); StepEntryBones.Reset(); StepOutputBones.Reset();
    StepReason = TEXT("reset");
}

bool APhysicsControlDummy::StepPlacement(FName Bone, FTransform& Foot, float FloorReference) const
{
    // First trial: nearly planar, static floors (<= 5 degrees, <= 2 cm height change).
    // A footprint, not just an ankle ray, must be supported. No stairs/edge bridging.
    FTransform Box;
    FVector Extent;
    if (!FootBox(Body, Bone, Foot, Box, Extent)) return false;
    FHitResult Center;
    FVector P = Box.GetLocation();
    P.Z = FloorReference + 12;
    if (!FindFloor(P, 24, Center) || Center.ImpactNormal.Z < .996f ||
        FMath::Abs(Center.ImpactPoint.Z - FloorReference) > 2) return false;
    const float Floor = Center.ImpactPoint.Z;
    for (float X : {-1.f, 1.f}) for (float Y : {-1.f, 1.f}) for (float Z : {-1.f, 1.f})
    {
        FHitResult Corner;
        FVector CornerPoint = Box.TransformPosition(Extent * FVector(X, Y, Z));
        CornerPoint.Z = P.Z;
        if (!FindFloor(CornerPoint, 24, Corner) || Corner.ImpactNormal.Z < .996f ||
            FMath::Abs(Corner.ImpactPoint.Z - Floor) > 1) return false;
    }
    // Preserve the calibrated ankle-to-sole offset, including the idle foot rotation.
    Foot.AddToTranslation(FVector(0, 0, Floor - FloorReference));
    FootBox(Body, Bone, Foot, Box, Extent);
    Box.AddToTranslation(FVector(0, 0, Floor + .5f - ShapeBottom(Bone, Foot)));
    FCollisionQueryParams Query(SCENE_QUERY_STAT(DummyStepPlacement), false, this);
    return !GetWorld()->OverlapAnyTestByObjectType(Box.GetLocation(), Box.GetRotation(),
        FCollisionObjectQueryParams(ECC_WorldStatic), FCollisionShape::MakeBox(Extent), Query);
}

bool APhysicsControlDummy::StepPathClear(const FTransform& Start, const FTransform& End) const
{
    FCollisionQueryParams Query(SCENE_QUERY_STAT(DummyStepPath), false, this);
    const FCollisionObjectQueryParams Objects(ECC_WorldStatic);
    FTransform Box;
    FVector Extent;
    if (!FootBox(Body, SwingFoot, Start, Box, Extent)) return false;
    const FQuat Rotation = Box.GetRotation();
    // Sweep the actual calibrated foot box, including its offset from the ankle.
    // A 0.5 cm contact margin keeps the supporting floor out of the clearance query.
    const FVector ClearanceOffset(0, 0, GroundHeight + .5f - ShapeBottom(SwingFoot, Start));
    FVector Previous = Box.GetLocation() + ClearanceOffset;
    for (int32 I = 1; I <= 12; ++I)
    {
        const float Alpha = I / 12.f;
        FVector P = Box.GetLocation() + ClearanceOffset + (End.GetLocation() - Start.GetLocation()) * Smooth(Alpha);
        P.Z += FMath::Sin(PI * Alpha) * FMath::Clamp(StepLift, 5.f, 18.f);
        FHitResult Hit;
        if (GetWorld()->SweepSingleByObjectType(Hit, Previous, P, Rotation, Objects,
            FCollisionShape::MakeBox(Extent), Query)) return false;
        Previous = P;
    }
    const FVector Pelvis = StandingPose.FindChecked(TEXT("pelvis")).GetLocation();
    const FVector Delta = Flat(End.GetLocation() - Start.GetLocation()) * .5f;
    for (int32 I = 0; I <= 4; ++I)
    {
        const FVector P = Pelvis + Delta * (I / 4.f);
        FHitResult Floor;
        if (!FindFloor(FVector(P.X, P.Y, GroundHeight + 12), 24, Floor) || Floor.ImpactNormal.Z < .996f ||
            FMath::Abs(Floor.ImpactPoint.Z - GroundHeight) > 2) return false;
        if (GetWorld()->OverlapAnyTestByObjectType(FVector(P.X, P.Y, GroundHeight + 100),
            FQuat::Identity, Objects, FCollisionShape::MakeCapsule(25, 88), Query)) return false;
    }
    return true;
}

bool APhysicsControlDummy::BeginStep()
{
    auto Reject = [&](const TCHAR* Reason)
    {
        ++StepsRejected; StepReason = Reason; EnterFall(Reason); return false;
    };
    if (IsDead()) { CancelStep(); return false; }
    if (EpisodeSteps >= 2) return Reject(TEXT("two-step recovery budget exhausted"));
    if (LeftLegDisabled > 0 || RightLegDisabled > 0 || UsableFeet < 1)
        return Reject(TEXT("step requires usable legs and a grounded support foot"));
    if (StandingBones.Num() != Body->GetNumBones()) return Reject(TEXT("step skeleton unavailable"));

    const FVector Pelvis = AnklePosition(Body, TEXT("pelvis"));
    const FVector Chest = AnklePosition(Body, TEXT("spine_05"));
    const FVector TrunkLeft = AnklePosition(Body, TEXT("clavicle_l")) - AnklePosition(Body, TEXT("clavicle_r"));
    const FVector Facing = FVector::CrossProduct(Chest - Pelvis, TrunkLeft).GetSafeNormal2D();
    if (!Facing.IsNearlyZero()) StandingForward = Facing;
    const FVector Velocity = Body->GetBodyInstance(TEXT("pelvis"))->GetUnrealWorldVelocity();
    // Measure the live body after the impulse has had 0.10 world seconds to act.
    // Both lean/displacement and velocity contribute, in world coordinates.
    const FVector BodyOffset = Flat(Pelvis - StandingPose.FindChecked(TEXT("pelvis")).GetLocation()) +
        Flat(Chest - Pelvis) * .35f + Flat(Velocity) * .08f;
    StepBodyDirection = BodyOffset;
    StepDirection = (BodyOffset.GetClampedToMaxSize(14) + LastStepImpulse.GetSafeNormal2D() * 9).GetSafeNormal2D();
    if (StepDirection.IsNearlyZero()) return Reject(TEXT("no horizontal recovery direction"));

    const FVector Left = StandingPose.FindChecked(TEXT("foot_l")).GetLocation();
    const FVector Right = StandingPose.FindChecked(TEXT("foot_r")).GetLocation();
    // A lateral opening step uses the outside foot. Once the stance is wide, the
    // trailing foot catches up; sagittal steps also use the trailing foot. Repeated
    // episodes must not keep stretching one leg while the other remains at home.
    const float Separation = FVector::DotProduct(StepDirection, Left - Right);
    const bool Lateral = FMath::Abs(FVector::DotProduct(StepDirection, StandingForward)) < .65f;
    const bool Leading = Lateral && FMath::Abs(Separation) < 40;
    bool bLeft = (Separation >= 0) == Leading;
    const bool LeftSupported = FootSupported(TEXT("foot_l")), RightSupported = FootSupported(TEXT("foot_r"));
    if (!LeftSupported && !RightSupported) return Reject(TEXT("step lost usable foot support"));
    if (!LeftSupported) bLeft = true;
    if (!RightSupported) bLeft = false;
    SwingFoot = bLeft ? TEXT("foot_l") : TEXT("foot_r");
    PlantedFoot = bLeft ? TEXT("foot_r") : TEXT("foot_l");
    SwingStart = StandingPose.FindChecked(SwingFoot);
    PlantedTarget = StandingPose.FindChecked(PlantedFoot);
    SwingDestination = SwingStart;
    const float Length = FMath::Min(FMath::Clamp(StepLength, 12.f, 40.f), FMath::Clamp(StepMaxReach, 12.f, 45.f));
    SwingDestination.AddToTranslation(StepDirection * Length);
    if (!StepPlacement(SwingFoot, SwingDestination, GroundHeight) || !StepPathClear(SwingStart, SwingDestination))
        return Reject(TEXT("step destination blocked or unsupported"));
    StepDisplacement = SwingDestination.GetLocation() - SwingStart.GetLocation();
    StepStartBones = StandingBones;
    StepEntryBones.Reset();
    for (int32 I = 0; I < Body->GetNumBones(); ++I)
        StepEntryBones.Add(Body->GetSocketTransform(Body->GetBoneName(I)));
    PlantedActualStart = AnklePosition(Body, PlantedFoot);
    const FVector StanceCenter = (Left + Right) * .5f;
    StepTransfer = Flat(PlantedTarget.GetLocation() - StanceCenter).GetClampedToMaxSize(10) * .65f;
    StepSeconds = StepNoSupportSeconds = StepSupportDrift = StepPeakSupportDrift = 0;
    StepPhase = 1; ++EpisodeSteps; ++StepsStarted; bStepRequested = false;
    StepReason = TEXT("transferring weight onto planted leg");
    BalanceState = EDummyBalanceState::Stepping;
    BalanceReason = TEXT("bounded reactive recovery step");
    return true;
}

bool APhysicsControlDummy::BuildStepPose(float Transfer, float Swing, float Settle, TMap<FName,FTransform>& Pose)
{
    const auto& Skeleton = Body->GetSkeletalMeshAsset()->GetRefSkeleton();
    StepOutputBones = StepStartBones;
    const int32 PelvisIndex = Body->GetBoneIndex(TEXT("pelvis"));
    const FVector PelvisStart = StepStartBones[PelvisIndex].GetLocation();
    const float Move = Smooth(Swing);
    const float WeightShift = Smooth(Transfer) * (1 - Smooth(Swing));
    FVector Offset = StepDisplacement * (.5f * Move) + StepTransfer * WeightShift;
    Offset.Z -= 3.f * Smooth(Transfer) * (1 - Smooth(Settle));
    const FQuat Tilt(FVector::CrossProduct(FVector::UpVector, StepDirection).GetSafeNormal(),
        FMath::DegreesToRadians(5.f * Smooth(Transfer) * (1 - Smooth(Settle))));
    for (int32 I = 0; I < StepOutputBones.Num(); ++I)
    {
        auto& T = StepOutputBones[I];
        T.SetLocation(PelvisStart + Tilt.RotateVector(T.GetLocation() - PelvisStart) + Offset);
        T.SetRotation(Tilt * T.GetRotation());
        // Continuously leave the actual post-hit skeleton during weight transfer.
        FTransform Blended;
        Blended.Blend(StepEntryBones[I], T, Smooth(Transfer));
        T = Blended;
    }

    // Keep both fixed ankle targets reachable as the pelvis crosses to the new
    // stance. A small persistent knee bend avoids straight-leg overextension;
    // moving a planted foot to satisfy the solver would create visible skating.
    double HeightCorrection = 0;
    for (bool bLeft : {true, false})
    {
        const int32 H = Body->GetBoneIndex(bLeft ? TEXT("thigh_l") : TEXT("thigh_r"));
        const int32 K = Body->GetBoneIndex(bLeft ? TEXT("calf_l") : TEXT("calf_r"));
        const int32 F = Body->GetBoneIndex(bLeft ? TEXT("foot_l") : TEXT("foot_r"));
        const bool Moving = Body->GetBoneName(F) == SwingFoot;
        FVector Ankle = Moving ? FMath::Lerp(SwingStart.GetLocation(), SwingDestination.GetLocation(), Move) : PlantedTarget.GetLocation();
        if (Moving) Ankle.Z += FMath::Sin(PI * FMath::Clamp(Swing, 0.f, 1.f)) * FMath::Clamp(StepLift, 5.f, 18.f);
        const FVector Hip = StepOutputBones[H].GetLocation();
        const double Reach = FVector::Distance(StepStartBones[H].GetLocation(), StepStartBones[K].GetLocation()) +
            FVector::Distance(StepStartBones[K].GetLocation(), StepStartBones[F].GetLocation()) - 1;
        const double HorizontalSquared = FVector::DistSquared2D(Hip, Ankle);
        if (HorizontalSquared >= Reach * Reach) return false;
        HeightCorrection = FMath::Min(HeightCorrection, Ankle.Z + FMath::Sqrt(Reach * Reach - HorizontalSquared) - Hip.Z);
    }
    if (HeightCorrection < -8) return false;
    for (auto& T : StepOutputBones) T.AddToTranslation(FVector(0, 0, HeightCorrection));

    for (bool bLeft : {true, false})
    {
        const FName Thigh = bLeft ? TEXT("thigh_l") : TEXT("thigh_r");
        const FName Calf = bLeft ? TEXT("calf_l") : TEXT("calf_r");
        const FName Foot = bLeft ? TEXT("foot_l") : TEXT("foot_r");
        const int32 H = Body->GetBoneIndex(Thigh), K = Body->GetBoneIndex(Calf), F = Body->GetBoneIndex(Foot);
        FTransform Target = Foot == PlantedFoot ? PlantedTarget : SwingStart;
        if (Foot == SwingFoot)
        {
            Target.SetLocation(FMath::Lerp(SwingStart.GetLocation(), SwingDestination.GetLocation(), Move) +
                FVector(0, 0, FMath::Sin(PI * FMath::Clamp(Swing, 0.f, 1.f)) * FMath::Clamp(StepLift, 5.f, 18.f)));
        }
        const FVector Hip = StepOutputBones[H].GetLocation();
        const FVector Ankle = Target.GetLocation();
        const FVector OriginalHip = StepStartBones[H].GetLocation();
        const FVector OriginalKnee = StepStartBones[K].GetLocation();
        const FVector OriginalAnkle = StepStartBones[F].GetLocation();
        const double A = FVector::Distance(OriginalHip, OriginalKnee);
        const double B = FVector::Distance(OriginalKnee, OriginalAnkle);
        const double Distance = FVector::Distance(Hip, Ankle);
        if (Distance > A + B + .5 || Distance < FMath::Abs(A - B) + .1) return false;
        const double D = FMath::Clamp(Distance, FMath::Abs(A - B) + .1, A + B - .05);
        const FVector Axis = (Ankle - Hip).GetSafeNormal();
        FVector Bend = OriginalKnee - OriginalHip;
        Bend -= Axis * FVector::DotProduct(Bend, Axis);
        if (Bend.SizeSquared() < 1) Bend = StandingForward - Axis * FVector::DotProduct(StandingForward, Axis);
        Bend.Normalize();
        const double Along = (A*A + D*D - B*B) / (2*D);
        const FVector Knee = Hip + Axis * Along + Bend * FMath::Sqrt(FMath::Max(0., A*A - Along*Along));
        StepOutputBones[H].SetRotation(FQuat::FindBetweenNormals((OriginalKnee - OriginalHip).GetSafeNormal(),
            (Knee - Hip).GetSafeNormal()) * StepStartBones[H].GetRotation());
        StepOutputBones[K].SetLocation(Knee);
        StepOutputBones[K].SetRotation(FQuat::FindBetweenNormals((OriginalAnkle - OriginalKnee).GetSafeNormal(),
            (Ankle - Knee).GetSafeNormal()) * StepStartBones[K].GetRotation());
        StepOutputBones[F] = Target;
        // Non-physical leg children, including the toes, follow their solved parents.
        for (int32 I = H + 1; I < StepOutputBones.Num(); ++I)
        {
            if (I == K || I == F) continue;
            int32 Ancestor = Skeleton.GetParentIndex(I);
            bool Descendant = false;
            while (Ancestor >= 0)
            {
                if (Ancestor == H) { Descendant = true; break; }
                Ancestor = Skeleton.GetParentIndex(Ancestor);
            }
            if (Descendant)
            {
                const int32 Parent = Skeleton.GetParentIndex(I);
                StepOutputBones[I] = StepStartBones[I].GetRelativeTransform(StepStartBones[Parent]) * StepOutputBones[Parent];
            }
        }
    }

    FPoseSnapshot Snapshot;
    Snapshot.bIsValid = true;
    Snapshot.SkeletalMeshName = Body->GetSkeletalMeshAsset()->GetFName();
    for (int32 I = 0; I < StepOutputBones.Num(); ++I)
    {
        Snapshot.BoneNames.Add(Body->GetBoneName(I));
        const int32 Parent = Skeleton.GetParentIndex(I);
        Snapshot.LocalTransforms.Add(Parent >= 0 ? StepOutputBones[I].GetRelativeTransform(StepOutputBones[Parent]) : StepOutputBones[I]);
    }
    PoseSource->SetWorldTransform(FTransform::Identity);
    auto* Anim = CastChecked<UDummyRecoveryAnimInstance>(PoseSource->GetAnimInstance());
    Anim->StartPose = MoveTemp(Snapshot);
    Anim->bSnapshotOnly = true;
    PoseSource->TickAnimation(0, false);
    PoseSource->RefreshBoneTransforms();
    Pose.Reset();
    for (const auto& Entry : StandingPose) Pose.Add(Entry.Key, PoseSource->GetSocketTransform(Entry.Key));
    SetVisibleAnimationPose();
    return true;
}

void APhysicsControlDummy::UpdateStep(float DeltaSeconds)
{
    if (IsDead()) { CancelStep(); return; }
    StepSeconds += DeltaSeconds;
    StepSupportDrift = FVector::Dist2D(AnklePosition(Body, PlantedFoot), PlantedActualStart);
    StepPeakSupportDrift = FMath::Max(StepPeakSupportDrift, StepSupportDrift);
    StepNoSupportSeconds = FootSupported(PlantedFoot) ? 0 : StepNoSupportSeconds + DeltaSeconds;
    FTransform Support = PlantedTarget, Destination = SwingDestination;
    if (LeftLegDisabled > 0 || RightLegDisabled > 0 || StepNoSupportSeconds > .10f ||
        !StepPlacement(PlantedFoot, Support, GroundHeight) || !StepPlacement(SwingFoot, Destination, GroundHeight))
    { StepReason = TEXT("usable step support lost"); EnterFall(TEXT("usable step support lost")); return; }
    if (Instability >= FMath::Max(.1f, FallThreshold) || PoseLeanDegrees > FMath::Clamp(MaxLeanDegrees, 20.f, 80.f) ||
        PelvisDrop > 45 || StepSupportDrift > 5)
    { StepReason = TEXT("recovery step exceeded balance limits"); EnterFall(TEXT("recovery step exceeded balance limits")); return; }
    const float TransferTime = FMath::Clamp(StepTransferSeconds, .12f, .35f);
    const float SwingTime = FMath::Clamp(StepSwingSeconds, .25f, .75f);
    const float SettleTime = FMath::Clamp(StepSettleSeconds, .2f, .6f);
    const float Transfer = FMath::Clamp(StepSeconds / TransferTime, 0.f, 1.f);
    const float Swing = FMath::Clamp((StepSeconds - TransferTime) / SwingTime, 0.f, 1.f);
    const float Settle = FMath::Clamp((StepSeconds - TransferTime - SwingTime) / SettleTime, 0.f, 1.f);
    StepPhase = StepSeconds < TransferTime ? 1 : Swing < 1 ? 2 : 3;
    StepReason = StepPhase == 1 ? TEXT("weight transfer") : StepPhase == 2 ? TEXT("swing") : TEXT("landing and settling");
    TMap<FName,FTransform> Targets;
    if (!BuildStepPose(Transfer, Swing, Settle, Targets))
    { StepReason = TEXT("leg reach exceeded"); EnterFall(TEXT("step leg reach exceeded")); return; }
    DrivePose(Targets);
    if (Settle >= 1)
    {
        const bool Landed = FootSupported(SwingFoot) && FootSupported(PlantedFoot) &&
            FVector::Dist2D(AnklePosition(Body, SwingFoot), SwingDestination.GetLocation()) < 3 && PoseLeanDegrees < 25;
        if (Landed)
        {
            StandingPose = Targets;
            RememberStandingSkeleton(PoseSource);
            ++StepsCompleted;
            StepPhase = 0;
            Instability = FMath::Max(0.f, Instability - .30f);
            BalanceState = Instability > .08f ? EDummyBalanceState::LosingBalance : EDummyBalanceState::Standing;
            StepReason = TEXT("landed at displaced stance");
            BalanceReason = TEXT("step recovered without health restoration");
            StepCooldownRemaining = bStepRequested ? .08f : FMath::Clamp(StepCooldown, .2f, 3.f);
            // A second step needs a fresh hit or measurable residual imbalance.
            const FVector Midpoint = (GetPhysicalBodyLocation(TEXT("foot_l")) + GetPhysicalBodyLocation(TEXT("foot_r"))) * .5;
            const FVector Offset = Flat(GetPhysicalBodyLocation(TEXT("pelvis")) - Midpoint);
            if (Offset.Size() > 24 && Instability > .15f) { bStepRequested = true; StepCooldownRemaining = .08f; }
        }
        else if (StepSeconds > TransferTime + SwingTime + SettleTime + .45f)
        { StepReason = TEXT("step landing timeout"); EnterFall(TEXT("step failed to land")); }
    }
}

void APhysicsControlDummy::AddStepState(TSharedPtr<FJsonObject> Root) const
{
    auto S = MakeShared<FJsonObject>();
    S->SetStringField(TEXT("phase"), StepPhase == 1 ? TEXT("TRANSFER") : StepPhase == 2 ? TEXT("SWING") : StepPhase == 3 ? TEXT("SETTLE") : TEXT("IDLE"));
    S->SetStringField(TEXT("reason"), StepReason);
    S->SetStringField(TEXT("swing_foot"), SwingFoot.ToString());
    S->SetStringField(TEXT("support_foot"), PlantedFoot.ToString());
    S->SetNumberField(TEXT("seconds"), StepSeconds);
    S->SetNumberField(TEXT("episode_steps"), EpisodeSteps);
    S->SetNumberField(TEXT("started"), StepsStarted);
    S->SetNumberField(TEXT("completed"), StepsCompleted);
    S->SetNumberField(TEXT("rejected"), StepsRejected);
    S->SetBoolField(TEXT("requested"), bStepRequested);
    S->SetNumberField(TEXT("cooldown"), StepCooldownRemaining);
    S->SetNumberField(TEXT("support_drift_cm"), StepSupportDrift);
    S->SetNumberField(TEXT("peak_support_drift_cm"), StepPeakSupportDrift);
    S->SetNumberField(TEXT("support_drift_tolerance_cm"), 2.f);
    S->SetField(TEXT("direction"), StepVector(StepDirection));
    S->SetField(TEXT("impulse"), StepVector(LastStepImpulse));
    S->SetField(TEXT("body_direction"), StepVector(StepBodyDirection));
    S->SetField(TEXT("facing"), StepVector(StandingForward));
    S->SetField(TEXT("swing_start"), StepVector(SwingStart.GetLocation()));
    S->SetField(TEXT("destination"), StepVector(SwingDestination.GetLocation()));
    S->SetField(TEXT("plant_target"), StepVector(PlantedTarget.GetLocation()));
    S->SetField(TEXT("weight_transfer"), StepVector(StepTransfer));
    S->SetField(TEXT("stance_pelvis"), StepVector(StandingPose.FindChecked(TEXT("pelvis")).GetLocation()));
    S->SetField(TEXT("home"), StepVector(Home.GetLocation()));
    S->SetNumberField(TEXT("full_pose_bones"), StepOutputBones.Num());
    if (!SwingFoot.IsNone()) S->SetNumberField(TEXT("landing_error_cm"), FVector::Dist2D(AnklePosition(Body, SwingFoot), SwingDestination.GetLocation()));
    Root->SetObjectField(TEXT("step"), S);
}
