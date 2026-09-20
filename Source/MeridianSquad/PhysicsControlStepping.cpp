#include "PhysicsControlDummy.h"
#include "DummyRecoveryAnimInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "PhysicsEngine/BodyInstance.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/SkeletalBodySetup.h"
#include "PhysicsEngine/PhysicsConstraintTemplate.h"
#include "Math/RotationMatrix.h"
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

void APhysicsControlDummy::RememberStandingSkeleton(const USkeletalMeshComponent* Mesh, bool bNeutral)
{
    StandingBones.Reset();
    for (int32 I = 0; I < Mesh->GetNumBones(); ++I)
        StandingBones.Add(Mesh->GetSocketTransform(Mesh->GetBoneName(I)));
    if (bNeutral) NeutralBones = StandingBones;
}

void APhysicsControlDummy::CancelStep()
{
    StepPhase = 0;
    bStepRequested = false;
    bStanceCorrectionPending = false;
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
    bCorrectiveStep = false;
    StepRestPelvis = FVector::ZeroVector;
    StepHeightCorrection = StepJointLimitError = 0;
    StepReason = TEXT("reset");
}

bool APhysicsControlDummy::NeedsStanceCorrection() const
{
    const FVector Left = StandingPose.FindChecked(TEXT("foot_l")).GetLocation();
    const FVector Right = StandingPose.FindChecked(TEXT("foot_r")).GetLocation();
    const FVector NeutralLeft = NeutralBones[Body->GetBoneIndex(TEXT("foot_l"))].GetLocation();
    const FVector NeutralRight = NeutralBones[Body->GetBoneIndex(TEXT("foot_r"))].GetLocation();
    // Bound deviation from this mannequin's calibrated rifle idle, not a claim
    // of universal anatomical dimensions. A remaining step can close the stance.
    const FVector Across = Flat(NeutralLeft - NeutralRight).GetSafeNormal();
    const double NeutralWidth = Flat(NeutralLeft - NeutralRight).Size();
    const double Width = FVector::DotProduct(Left - Right, Across);
    return Width > NeutralWidth + 16 || Width < NeutralWidth * .55 ||
        Flat((Left - Right) - (NeutralLeft - NeutralRight)).Size() > 36 || StepHeightCorrection < -4;
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
    if (UsableFeet < 1 || !bRecoveryFeasible)
        return Reject(TEXT("step requires feasible physical support"));
    if (StandingBones.Num() != Body->GetNumBones() || NeutralBones.Num() != Body->GetNumBones())
        return Reject(TEXT("step skeleton unavailable"));

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
    StepDirection = (BodyOffset.GetClampedToMaxSize(14) + CaptureError.GetClampedToMaxSize(20) + Flat(RecoveryVelocity)*.12f +
        LastStepImpulse.GetSafeNormal2D()*8.f).GetSafeNormal2D();
    if (!DisturbedFoot.IsNone())
    {
        const auto* FootBody=Body->GetBodyInstance(DisturbedFoot);
        const FVector Motion=Flat(FootBody->GetUnrealWorldTransform().GetLocation()-StandingPose.FindChecked(DisturbedFoot).GetLocation())+
            Flat(FootBody->GetUnrealWorldVelocity())*.12f;
        if (Motion.Size() > .5f) StepDirection=Motion.GetSafeNormal();
    }
    if (StepDirection.IsNearlyZero())
    { bStepRequested=false; StepRequestSeconds=0; StepReason=TEXT("disturbance already settled without placement"); return false; }

    const FVector Left = StandingPose.FindChecked(TEXT("foot_l")).GetLocation();
    const FVector Right = StandingPose.FindChecked(TEXT("foot_r")).GetLocation();
    // A lateral opening step uses the outside foot. Once the stance is wide, the
    // trailing foot catches up; sagittal steps also use the trailing foot. Repeated
    // episodes must not keep stretching one leg while the other remains at home.
    const float Separation = FVector::DotProduct(StepDirection, Left - Right);
    const bool Lateral = FMath::Abs(FVector::DotProduct(StepDirection, StandingForward)) < .65f;
    const bool Leading = Lateral && FMath::Abs(Separation) < 40;
    bCorrectiveStep = bStanceCorrectionPending;
    // Finish an over-wide/low stance by moving the previous support foot. The
    // newly landed foot remains fixed for the whole corrective step.
    bool bLeft = bCorrectiveStep ? PlantedFoot == TEXT("foot_l") : (Separation >= 0) == Leading;
    const bool LeftSupported = FootSupported(TEXT("foot_l")), RightSupported = FootSupported(TEXT("foot_r"));
    if (!bCorrectiveStep && DisturbedFoot == TEXT("foot_l") && RightSupported) bLeft=true;
    if (!bCorrectiveStep && DisturbedFoot == TEXT("foot_r") && LeftSupported) bLeft=false;
    if (!LeftSupported && !RightSupported) return Reject(TEXT("step lost usable foot support"));
    if (!LeftSupported) bLeft = true;
    if (!RightSupported) bLeft = false;
    SwingFoot = bLeft ? TEXT("foot_l") : TEXT("foot_r");
    PlantedFoot = bLeft ? TEXT("foot_r") : TEXT("foot_l");
    SwingStart = StandingPose.FindChecked(SwingFoot);
    const FVector ActualAnkle=AnklePosition(Body,SwingFoot);
    SwingStart.SetLocation(FVector(ActualAnkle.X,ActualAnkle.Y,SwingStart.GetLocation().Z));
    PlantedTarget = StandingPose.FindChecked(PlantedFoot);
    SwingDestination = SwingStart;
    const float Length = FMath::Min(FMath::Clamp(StepLength,12.f,40.f), EffectiveReach);
    SwingDestination.AddToTranslation(StepDirection * Length);
    const FVector NeutralLeft = NeutralBones[Body->GetBoneIndex(TEXT("foot_l"))].GetLocation();
    const FVector NeutralRight = NeutralBones[Body->GetBoneIndex(TEXT("foot_r"))].GetLocation();
    if (bCorrectiveStep)
    {
        const FVector NeutralSeparation = bLeft ? NeutralLeft - NeutralRight : NeutralRight - NeutralLeft;
        FVector Destination = PlantedTarget.GetLocation() + NeutralSeparation;
        Destination.Z = SwingStart.GetLocation().Z;
        const FVector Correction = Flat(Destination - SwingStart.GetLocation());
        // World-space subtraction can put an exact 40 cm step a few ulps over
        // 40. The 0.01 cm numerical margin does not expand the placement budget.
        if (Correction.Size() > EffectiveReach + .01f)
            return Reject(TEXT("corrective stance exceeds step reach"));
        SwingDestination.SetLocation(Destination);
        StepDirection = Correction.GetSafeNormal();
    }
    if (!StepPlacement(SwingFoot, SwingDestination, GroundHeight) || !StepPathClear(SwingStart, SwingDestination))
        return Reject(TEXT("step destination blocked or unsupported"));
    StepDisplacement = SwingDestination.GetLocation() - SwingStart.GetLocation();
    const FVector NeutralPelvis = NeutralBones[Body->GetBoneIndex(TEXT("pelvis"))].GetLocation();
    StepRestPelvis = (SwingDestination.GetLocation() + PlantedTarget.GetLocation()) * .5 +
        NeutralPelvis - (NeutralLeft + NeutralRight) * .5;
    StepStartBones = StandingBones;
    StepEntryBones.Reset();
    for (int32 I = 0; I < Body->GetNumBones(); ++I)
        StepEntryBones.Add(Body->GetSocketTransform(Body->GetBoneName(I)));
    PlantedActualStart = AnklePosition(Body, PlantedFoot);
    const FVector StanceCenter = (Left + Right) * .5f;
    StepTransfer = Flat(PlantedTarget.GetLocation() - StanceCenter).GetClampedToMaxSize(10) * .65f;
    StepSeconds = StepNoSupportSeconds = StepSupportDrift = StepPeakSupportDrift = 0;
    StepEntryCaptureDistance = CaptureDistance;
    DisturbedFoot = NAME_None;
    StepRequestSeconds = 0;
    StepPhase = 1; ++EpisodeSteps; ++StepsStarted; bStepRequested = false; bStanceCorrectionPending = false;
    StepReason = TEXT("transferring weight onto planted leg");
    // Fixed envelope for this asset's offset constraint frames. Calibrated idle
    // already needs hip swing ~58 and ankle twist ~38 degrees; the original
    // ragdoll's 55/35 limits cannot admit even a small weight transfer. Reserve
    // bounded flexion for the swing, while retaining tight knee off-axis motion.
    // These values never track or expand to fit a generated pose.
    const auto* Asset = Body->GetPhysicsAsset();
    for (int32 I = 0; I < Asset->ConstraintSetup.Num(); ++I)
    {
        const auto& Default = Asset->ConstraintSetup[I]->DefaultInstance;
        const FString Name = Default.ConstraintBone1.ToString();
        if (!Name.StartsWith(TEXT("thigh")) && !Name.StartsWith(TEXT("calf")) && !Name.StartsWith(TEXT("foot"))) continue;
        const int32 Child = Body->GetBoneIndex(Default.ConstraintBone1), Parent = Body->GetBoneIndex(Default.ConstraintBone2);
        if (Child >= 0 && Parent >= 0)
            if (auto* Joint = Body->GetConstraintInstanceByIndex(I))
            {
                Joint->WidenLimitsForDriveTarget(NeutralBones[Child].GetRelativeTransform(NeutralBones[Parent]).GetRotation(), Default);
                const bool Hip = Name.StartsWith(TEXT("thigh"));
                const bool Ankle = Name.StartsWith(TEXT("foot"));
                const bool Knee = Name.StartsWith(TEXT("calf")) && Default.ConstraintBone2.ToString().StartsWith(TEXT("thigh"));
                if (Hip || Ankle || Knee)
                {
                    Joint->SetAngularSwing1Limit(ACM_Limited, Hip ? 75.f : Ankle ? 20.f : 8.f);
                    Joint->SetAngularSwing2Limit(ACM_Limited, Hip ? 35.f : Ankle ? 30.f : 15.f);
                    Joint->SetAngularTwistLimit(ACM_Limited, Hip ? 20.f : Ankle ? 65.f : 60.f);
                }
            }
    }
    BalanceState = EDummyBalanceState::Stepping;
    BalanceReason = TEXT("bounded reactive recovery step");
    return true;
}

bool APhysicsControlDummy::BuildStepPose(float Transfer, float Swing, float Settle, TMap<FName,FTransform>& Pose)
{
    const auto& Skeleton = Body->GetSkeletalMeshAsset()->GetRefSkeleton();
    StepOutputBones = NeutralBones;
    const int32 PelvisIndex = Body->GetBoneIndex(TEXT("pelvis"));
    const FVector PelvisStart = StepStartBones[PelvisIndex].GetLocation();
    const FVector NeutralPelvis = NeutralBones[PelvisIndex].GetLocation();
    const float Move = Smooth(Swing);
    const float WeightShift = Smooth(Transfer) * (1 - Smooth(Swing));
    FVector Offset = (StepRestPelvis - PelvisStart) * Move + StepTransfer * WeightShift;
    Offset.Z -= 3.f * Smooth(Transfer) * (1 - Smooth(Settle));
    const FQuat Tilt(FVector::CrossProduct(FVector::UpVector, StepDirection).GetSafeNormal(),
        // Recenter before contact: retaining the transfer lean until after a
        // long foot placement can over-rotate the hip despite reachable ankles.
        FMath::DegreesToRadians(5.f * Smooth(Transfer) * (1 - Smooth(Swing))));
    for (int32 I = 0; I < StepOutputBones.Num(); ++I)
    {
        auto& T = StepOutputBones[I];
        T.SetLocation(PelvisStart + Tilt.RotateVector(T.GetLocation() - NeutralPelvis) + Offset);
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
        const double Reach = FVector::Distance(NeutralBones[H].GetLocation(), NeutralBones[K].GetLocation()) +
            FVector::Distance(NeutralBones[K].GetLocation(), NeutralBones[F].GetLocation()) - 1;
        const double HorizontalSquared = FVector::DistSquared2D(Hip, Ankle);
        if (HorizontalSquared >= Reach * Reach) return false;
        HeightCorrection = FMath::Min(HeightCorrection, Ankle.Z + FMath::Sqrt(Reach * Reach - HorizontalSquared) - Hip.Z);
    }
    StepHeightCorrection = HeightCorrection;
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
        const FVector OriginalHip = NeutralBones[H].GetLocation();
        const FVector OriginalKnee = NeutralBones[K].GetLocation();
        const FVector OriginalAnkle = NeutralBones[F].GetLocation();
        const double A = FVector::Distance(OriginalHip, OriginalKnee);
        const double B = FVector::Distance(OriginalKnee, OriginalAnkle);
        const double Distance = FVector::Distance(Hip, Ankle);
        if (Distance > A + B + .5 || Distance < FMath::Abs(A - B) + .1) return false;
        const double D = FMath::Clamp(Distance, FMath::Abs(A - B) + .1, A + B - .05);
        const FVector Axis = (Ankle - Hip).GetSafeNormal();
        // Remove the longitudinal component in the ORIGINAL leg frame first.
        // Projecting the whole old thigh against the NEW hip-to-ankle axis made
        // a planted knee reverse its bend as the pelvis moved behind the foot.
        const FVector OriginalAxis = (OriginalAnkle - OriginalHip).GetSafeNormal();
        const FVector OriginalBend = ((OriginalKnee - OriginalHip) - OriginalAxis *
            FVector::DotProduct(OriginalKnee - OriginalHip, OriginalAxis)).GetSafeNormal();
        const FQuat FootTurn = Target.GetRotation() * NeutralBones[F].GetRotation().Inverse();
        FVector Bend = FootTurn.RotateVector(OriginalBend);
        Bend -= Axis * FVector::DotProduct(Bend, Axis);
        if (!Bend.Normalize()) return false;
        const double Along = (A*A + D*D - B*B) / (2*D);
        const FVector Knee = Hip + Axis * Along + Bend * FMath::Sqrt(FMath::Max(0., A*A - Along*Along));
        // Map a complete anatomical frame, including roll, from the immutable
        // neutral leg. Independent shortest-arc rotations can accumulate twist.
        const FVector OriginalNormal = FVector::CrossProduct(OriginalAxis, OriginalBend).GetSafeNormal();
        const FVector Normal = FVector::CrossProduct(Axis, Bend).GetSafeNormal();
        auto SegmentRotation = [&](const FVector& Original, const FVector& Solved, int32 Index)
        {
            const FQuat From = FRotationMatrix::MakeFromXY(Original, OriginalNormal).ToQuat();
            const FQuat To = FRotationMatrix::MakeFromXY(Solved, Normal).ToQuat();
            return To * From.Inverse() * NeutralBones[Index].GetRotation();
        };
        StepOutputBones[H].SetRotation(SegmentRotation(OriginalKnee - OriginalHip, Knee - Hip, H));
        StepOutputBones[K].SetLocation(Knee);
        StepOutputBones[K].SetRotation(SegmentRotation(OriginalAnkle - OriginalKnee, Ankle - Knee, K));
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
                StepOutputBones[I] = NeutralBones[I].GetRelativeTransform(NeutralBones[Parent]) * StepOutputBones[Parent];
            }
        }
    }

    StepJointLimitError = 0;
    const auto* Asset = Body->GetPhysicsAsset();
    for (int32 I = 0; I < Asset->ConstraintSetup.Num(); ++I)
    {
        const auto& Def = Asset->ConstraintSetup[I]->DefaultInstance;
        const FString Name = Def.ConstraintBone1.ToString();
        if (!Name.StartsWith(TEXT("thigh")) && !Name.StartsWith(TEXT("calf")) && !Name.StartsWith(TEXT("foot"))) continue;
        const int32 C = Body->GetBoneIndex(Def.ConstraintBone1), P = Body->GetBoneIndex(Def.ConstraintBone2);
        if (C >= 0 && P >= 0)
            if (const auto* Joint = Body->GetConstraintInstanceByIndex(I))
            {
                const FQuat Relative = StepOutputBones[C].GetRelativeTransform(StepOutputBones[P]).GetRotation();
                const FQuat Clamped = Joint->ClampDriveTargetToLimits(Relative, true);
                StepJointLimitError = FMath::Max(StepJointLimitError, static_cast<float>(FMath::RadiansToDegrees(Relative.AngularDistance(Clamped))));
            }
    }
    if (StepJointLimitError > 3.f) return false;

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
    if (StepNoSupportSeconds > .14f ||
        !StepPlacement(PlantedFoot, Support, GroundHeight) || !StepPlacement(SwingFoot, Destination, GroundHeight))
    { StepReason = TEXT("usable step support lost"); EnterFall(TEXT("usable step support lost")); return; }
    if (!bRecoveryFeasible || StepSupportDrift > 8)
    { StepReason = TEXT("recovery step exceeded balance limits"); EnterFall(TEXT("recovery step exceeded balance limits")); return; }
    const float TransferTime = FMath::Clamp(StepTransferSeconds, .12f, .35f)/EffectiveSpeed;
    const float SwingTime = FMath::Clamp(StepSwingSeconds, .25f, .75f)/EffectiveSpeed;
    const float SettleTime = FMath::Clamp(StepSettleSeconds, .2f, .6f)/EffectiveSpeed;
    const float Transfer = FMath::Clamp(StepSeconds / TransferTime, 0.f, 1.f);
    const float Swing = FMath::Clamp((StepSeconds - TransferTime) / SwingTime, 0.f, 1.f);
    const float Settle = FMath::Clamp((StepSeconds - TransferTime - SwingTime) / SettleTime, 0.f, 1.f);
    StepPhase = StepSeconds < TransferTime ? 1 : Swing < 1 ? 2 : 3;
    StepReason = StepPhase == 1 ? TEXT("weight transfer") : StepPhase == 2 ? TEXT("swing") : TEXT("landing and settling");
    TMap<FName,FTransform> Targets;
    if (!BuildStepPose(Transfer, Swing, Settle, Targets))
    { StepReason = TEXT("leg reach or fixed joint envelope exceeded"); EnterFall(TEXT("step leg geometry infeasible")); return; }
    DrivePose(Targets);
    if (Settle >= 1)
    {
        const bool Landed = FootSupported(SwingFoot) && FootSupported(PlantedFoot) &&
            FVector::Dist2D(AnklePosition(Body, SwingFoot), SwingDestination.GetLocation()) < 3 && PoseLeanDegrees < 25;
        if (Landed)
        {
            StandingPose = Targets;
            RememberStandingSkeleton(PoseSource, false);
            ++StepsCompleted;
            if (StepDisplacement.Size2D() > 5 && CaptureDistance <= FMath::Max(5.f,StepEntryCaptureDistance+3))
            { RecoveryNoProgressSeconds=0; RecoveryBestError=CaptureDistance; }
            StepPhase = 0;
            Instability = FMath::Max(0.f, Instability - .30f);
            BalanceState = EDummyBalanceState::LosingBalance;
            RecoveryStableSeconds=0;
            StepReason = TEXT("landed at displaced stance");
            BalanceReason = TEXT("step recovered without health restoration");
            StepCooldownRemaining = bStepRequested ? .08f : FMath::Clamp(StepCooldown, .2f, 3.f);
            if (NeedsStanceCorrection())
            {
                bStanceCorrectionPending = bStepRequested = true;
                StepCooldownRemaining = .08f;
                BalanceState = EDummyBalanceState::LosingBalance;
            }
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
    S->SetNumberField(TEXT("neutral_bones"), NeutralBones.Num());
    S->SetNumberField(TEXT("height_correction_cm"), StepHeightCorrection);
    S->SetNumberField(TEXT("joint_limit_error_degrees"), StepJointLimitError);
    S->SetBoolField(TEXT("corrective"), bCorrectiveStep);
    S->SetBoolField(TEXT("stance_correction_pending"), bStanceCorrectionPending);
    S->SetField(TEXT("rest_pelvis"), StepVector(StepRestPelvis));
    TArray<TSharedPtr<FJsonValue>> Joints;
    const auto* Asset = Body->GetPhysicsAsset();
    for (int32 I = 0; I < Asset->ConstraintSetup.Num(); ++I)
        if (const auto* Joint = Body->GetConstraintInstanceByIndex(I))
        {
            const FString Name = Joint->ConstraintBone1.ToString();
            if (!Name.StartsWith(TEXT("thigh")) && !Name.StartsWith(TEXT("calf")) && !Name.StartsWith(TEXT("foot"))) continue;
            auto J = MakeShared<FJsonObject>();
            const auto& Default = Asset->ConstraintSetup[I]->DefaultInstance;
            J->SetStringField(TEXT("child"), Name);
            J->SetStringField(TEXT("parent"), Joint->ConstraintBone2.ToString());
            J->SetField(TEXT("motion_swing1_swing2_twist"), StepVector(FVector(Joint->GetAngularSwing1Motion(), Joint->GetAngularSwing2Motion(), Joint->GetAngularTwistMotion())));
            J->SetField(TEXT("authored_degrees"), StepVector(FVector(Default.GetAngularSwing1Limit(), Default.GetAngularSwing2Limit(), Default.GetAngularTwistLimit())));
            J->SetField(TEXT("effective_degrees"), StepVector(FVector(Joint->GetAngularSwing1Limit(), Joint->GetAngularSwing2Limit(), Joint->GetAngularTwistLimit())));
            // Use actual bone transforms and the exact Chaos swing convention.
            // GetCurrentSwing* uses axis twist projections, not the limit cone's
            // swing/twist decomposition, and is unsuitable for bound comparison.
            const auto* Child = Body->GetBodyInstance(Joint->ConstraintBone1);
            const auto* Parent = Body->GetBodyInstance(Joint->ConstraintBone2);
            if (Child && Parent)
            {
                FQuat Relative = (Joint->GetRefFrame(EConstraintFrame::Frame2) * Parent->GetUnrealWorldTransform()).GetRotation().Inverse() *
                    (Joint->GetRefFrame(EConstraintFrame::Frame1) * Child->GetUnrealWorldTransform()).GetRotation();
                Relative.Normalize();
                FQuat Swing, Twist;
                Relative.ToSwingTwist(FVector::ForwardVector, Swing, Twist);
                if (Swing.W < 0) Swing = Swing * -1.f;
                const FVector Angles(4 * FMath::Atan2(Swing.Z, 1 + Swing.W), 4 * FMath::Atan2(Swing.Y, 1 + Swing.W),
                    FMath::UnwindRadians(2 * FMath::Atan2(Twist.X, Twist.W)));
                J->SetField(TEXT("observed_degrees"), StepVector(Angles * (180. / PI)));
            }
            const int32 C = Body->GetBoneIndex(Joint->ConstraintBone1), P = Body->GetBoneIndex(Joint->ConstraintBone2);
            if (StepOutputBones.IsValidIndex(C) && StepOutputBones.IsValidIndex(P))
            {
                const FQuat Target = StepOutputBones[C].GetRelativeTransform(StepOutputBones[P]).GetRotation();
                J->SetNumberField(TEXT("target_clamp_error_degrees"), FMath::RadiansToDegrees(Target.AngularDistance(Joint->ClampDriveTargetToLimits(Target, true))));
            }
            Joints.Add(MakeShared<FJsonValueObject>(J));
        }
    S->SetArrayField(TEXT("leg_joints"), Joints);
    if (!SwingFoot.IsNone()) S->SetNumberField(TEXT("landing_error_cm"), FVector::Dist2D(AnklePosition(Body, SwingFoot), SwingDestination.GetLocation()));
    Root->SetObjectField(TEXT("step"), S);
}
