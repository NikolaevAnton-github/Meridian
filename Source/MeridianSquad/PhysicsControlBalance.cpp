#include "PhysicsControlDummy.h"
#include "PhysicsControlComponent.h"
#include "DummyRecoveryAnimInstance.h"
#include "Animation/AnimSequence.h"
#include "Components/SkeletalMeshComponent.h"
#include "PhysicsEngine/BodyInstance.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/PhysicsConstraintTemplate.h"
#include "PhysicsEngine/SkeletalBodySetup.h"
#include "Engine/World.h"
#include "Dom/JsonObject.h"

namespace
{
bool IsLeg(const FString& Bone)
{
    return Bone.StartsWith(TEXT("thigh")) || Bone.StartsWith(TEXT("calf")) || Bone.StartsWith(TEXT("foot"));
}
}

FString APhysicsControlDummy::GetBalanceLabel() const
{
    switch (BalanceState)
    {
    case EDummyBalanceState::Standing: return TEXT("STANDING");
    case EDummyBalanceState::LosingBalance: return TEXT("UNSTEADY");
    case EDummyBalanceState::Falling: return TEXT("FALLING");
    case EDummyBalanceState::Down: return TEXT("DOWN");
    case EDummyBalanceState::GettingUp: return TEXT("GETTING UP");
    default: return TEXT("CORPSE");
    }
}

void APhysicsControlDummy::ResetBalance()
{
    BalanceState = EDummyBalanceState::Standing;
    Instability = StateSeconds = LeftLegDisabled = RightLegDisabled = 0;
    NoSupportSeconds = SettledSeconds = PoseLeanDegrees = PelvisDrop = 0;
    SinceDisturbance = 10;
    Falls = GetUps = InterruptedGetUps = UsableFeet = 0;
    LeanDirection = FVector::ZeroVector;
    StandingForward = Home.GetRotation().GetForwardVector();
    ActiveGetUp = nullptr;
    FallenSnapshot = FPoseSnapshot(); IdleSnapshot = FPoseSnapshot(); GetUpEndPose.Reset();
    SnapshotFirstError = 0;
    bRecoveryFloor = bRecoveryClear = false;
    BalanceReason = TEXT("reset");
}

void APhysicsControlDummy::DisableBalanceDrives()
{
    RecoveringControls.Reset();
    for (FName Name : Controls) PhysicsControl->SetControlEnabled(Name, false);
}

void APhysicsControlDummy::EnterFall(const TCHAR* Reason)
{
    if (IsDead()) return;
    if (BalanceState == EDummyBalanceState::GettingUp) ++InterruptedGetUps;
    if (BalanceState != EDummyBalanceState::Falling && BalanceState != EDummyBalanceState::Down) ++Falls;
    BalanceState = EDummyBalanceState::Falling;
    StateSeconds = SettledSeconds = 0;
    BalanceReason = Reason;
    ActiveGetUp = nullptr;
    Body->bPauseAnims = true;
    DisableBalanceDrives();
    Body->WakeAllRigidBodies();
    // The fully simulated current visible pose and velocities remain authoritative.
}

void APhysicsControlDummy::RegisterDisturbance(FName Bone, const FVector& Impulse, float Amount)
{
    if (IsDead()) return;
    SinceDisturbance = SettledSeconds = 0;
    Instability = FMath::Min(2.f, Instability + FMath::Max(0.f, Amount));
    LeanDirection = (LeanDirection * .3f + Impulse.GetSafeNormal2D()).GetSafeNormal2D();
    const FString Name = Bone.ToString();
    if (IsLeg(Name))
    {
        if (Name.EndsWith(TEXT("_l"))) LeftLegDisabled = FMath::Clamp(LegDisableSeconds, .1f, 20.f);
        if (Name.EndsWith(TEXT("_r"))) RightLegDisabled = FMath::Clamp(LegDisableSeconds, .1f, 20.f);
    }
    if (BalanceState == EDummyBalanceState::GettingUp) EnterFall(TEXT("recovery interrupted by disturbance"));
    else if (LeftLegDisabled > 0 && RightLegDisabled > 0) EnterFall(TEXT("both legs unavailable"));
    else if (Instability >= FMath::Max(.1f, FallThreshold)) EnterFall(TEXT("accumulated disturbance"));
    else if (BalanceState == EDummyBalanceState::Standing) BalanceState = EDummyBalanceState::LosingBalance;
}

void APhysicsControlDummy::ApplyExternalDisturbance(FVector Impulse, FVector WorldPoint, FName Bone)
{
    auto* BI = Body->GetBodyInstance(Bone);
    if (!bReady || !BI || Impulse.ContainsNaN() || WorldPoint.ContainsNaN()) return;
    Impulse = Impulse.GetClampedToMaxSize(FMath::Min(18000.f, BI->GetBodyMass() * 700.f));
    if (Impulse.IsNearlyZero()) return;
    RegisterDisturbance(Bone, Impulse, Impulse.Size() / 5000.f);
    Body->WakeAllRigidBodies();
    Body->AddImpulseAtLocation(Impulse, WorldPoint, Bone);
}

bool APhysicsControlDummy::FindFloor(const FVector& Point, float Depth, FHitResult& Hit) const
{
    FCollisionQueryParams Query(SCENE_QUERY_STAT(DummySupport), false, this);
    return GetWorld()->LineTraceSingleByObjectType(Hit, Point + FVector(0,0,8), Point - FVector(0,0,Depth),
        FCollisionObjectQueryParams(ECC_WorldStatic), Query) && Hit.ImpactNormal.Z >= .65;
}

bool APhysicsControlDummy::RecoverySpace(const FVector& Center, float& FloorZ) const
{
    FHitResult Hit;
    if (!FindFloor(Center, 120, Hit)) return false;
    FloorZ = Hit.ImpactPoint.Z;
    // A small, reasonably level footprint, not a single ray that accepts a ledge.
    for (FVector Offset : {FVector(24,0,0), FVector(-24,0,0), FVector(0,24,0), FVector(0,-24,0)})
    {
        FHitResult Foot;
        if (!FindFloor(FVector(Center.X, Center.Y, FloorZ + 35) + Offset, 55, Foot) ||
            FMath::Abs(Foot.ImpactPoint.Z - FloorZ) > 12) return false;
    }
    FCollisionQueryParams Query(SCENE_QUERY_STAT(DummyRecoverySpace), false, this);
    return !GetWorld()->OverlapBlockingTestByChannel(FVector(Center.X,Center.Y,FloorZ + 101), FQuat::Identity,
        ECC_WorldStatic, FCollisionShape::MakeCapsule(29, 90), Query);
}

void APhysicsControlDummy::SampleAnimation(UAnimSequence* Animation, float Time, const FTransform& Origin,
    TMap<FName,FTransform>& Pose)
{
    PoseSource->SetWorldTransform(Origin);
    auto* Anim = CastChecked<UDummyRecoveryAnimInstance>(PoseSource->GetAnimInstance());
    Anim->Sequence = Animation;
    Anim->SequenceTime = FMath::Clamp(Time, 0.f, Animation->GetPlayLength());
    Anim->StartAlpha = 1;
    Anim->EndAlpha = 0;
    Anim->MotionOffsetZ = 0;
    PoseSource->TickAnimation(0, false);
    PoseSource->RefreshBoneTransforms();
    Pose.Reset();
    for (const auto& Entry : StandingPose) Pose.Add(Entry.Key, PoseSource->GetSocketTransform(Entry.Key));
}

bool APhysicsControlDummy::BeginGetUp()
{
    if (IsDead() || !GetUpBack || !GetUpStomach || LeftLegDisabled > 0 || RightLegDisabled > 0) return false;
    const FTransform ActualPelvis = Body->GetBodyInstance(TEXT("pelvis"))->GetUnrealWorldTransform();
    // A twisted pelvis can face the opposite way to the trunk after a leg fall.
    // Classify the torso's anatomical front from its actual shoulder/hip plane.
    const FVector TrunkUp = GetPhysicalBodyLocation(TEXT("spine_05")) - ActualPelvis.GetLocation();
    const FVector TrunkLeft = GetPhysicalBodyLocation(TEXT("clavicle_l")) - GetPhysicalBodyLocation(TEXT("clavicle_r"));
    const bool FaceUp = FVector::CrossProduct(TrunkUp, TrunkLeft).Z >= 0;
    ActiveGetUp = FaceUp ? GetUpBack : GetUpStomach;
    TMap<FName,FTransform> First;
    SampleAnimation(ActiveGetUp, 0, FTransform::Identity, First);
    const FVector SourceAxis = (First.FindChecked(TEXT("head")).GetLocation() - First.FindChecked(TEXT("pelvis")).GetLocation()).GetSafeNormal2D();
    FVector ActualAxis = (GetPhysicalBodyLocation(TEXT("head")) - ActualPelvis.GetLocation()).GetSafeNormal2D();
    if (ActualAxis.IsNearlyZero()) ActualAxis = Home.GetRotation().GetForwardVector() * (FaceUp ? -1 : 1);
    const float Yaw = ActualAxis.Rotation().Yaw - SourceAxis.Rotation().Yaw;
    const FQuat Rotation = FRotator(0, Yaw, 0).Quaternion();
    FVector Origin = ActualPelvis.GetLocation() - Rotation.RotateVector(First.FindChecked(TEXT("pelvis")).GetLocation());
    // Align the complete first pose's collision envelope to the measured floor.
    // This is an animation-target placement, never a teleport of the fallen body.
    Origin.Z = GroundHeight + .15f - PoseBottom(First);
    RecoveryRoot = FTransform(Rotation, Origin);
    SampleAnimation(ActiveGetUp, ActiveGetUp->GetPlayLength(), RecoveryRoot, GetUpEndPose);
    float EndFloor;
    if (!RecoverySpace(GetUpEndPose.FindChecked(TEXT("pelvis")).GetLocation(), EndFloor) || FMath::Abs(EndFloor - GroundHeight) > 12)
    {
        ActiveGetUp = nullptr; BalanceReason = TEXT("get-up destination blocked or unsupported"); return false;
    }
    const FVector EndPelvis = GetUpEndPose.FindChecked(TEXT("pelvis")).GetLocation();
    const FVector Side = GetUpEndPose.FindChecked(TEXT("thigh_l")).GetLocation() - GetUpEndPose.FindChecked(TEXT("thigh_r")).GetLocation();
    TMap<FName,FTransform> IdlePose;
    SampleAnimation(Idle, 0, FTransform::Identity, IdlePose);
    const FVector IdleSide = IdlePose.FindChecked(TEXT("thigh_l")).GetLocation() - IdlePose.FindChecked(TEXT("thigh_r")).GetLocation();
    const FQuat IdleRotation = FRotator(0, Side.Rotation().Yaw - IdleSide.Rotation().Yaw, 0).Quaternion();
    SampleAnimation(Idle, 0, FTransform(IdleRotation,FVector::ZeroVector), IdlePose);
    FVector IdleOffset = EndPelvis - IdlePose.FindChecked(TEXT("pelvis")).GetLocation();
    IdleOffset.Z = EndFloor + .15f - FMath::Min(SoleBottom(PoseSource,true), SoleBottom(PoseSource,false));
    RecoveredIdleRoot = FTransform(IdleRotation, IdleOffset);
    SampleAnimation(Idle, 0, RecoveredIdleRoot, IdlePose);
    PoseSource->SnapshotPose(IdleSnapshot);
    IdleSnapshot.LocalTransforms[0] = (IdleSnapshot.LocalTransforms[0] * RecoveredIdleRoot).GetRelativeTransform(RecoveryRoot);
    // Capture the post-physics full skeleton, including fingers/toes/non-body bones.
    // Both components stay forced to LOD0 from construction through capture/playback.
    Body->SnapshotPose(FallenSnapshot);
    if (!FallenSnapshot.bIsValid || FallenSnapshot.LocalTransforms.Num() != Body->GetNumBones())
    { ActiveGetUp = nullptr; BalanceReason = TEXT("incomplete skeletal snapshot"); return false; }
    FallenSnapshot.LocalTransforms[0] = (FallenSnapshot.LocalTransforms[0] * Body->GetComponentTransform()).GetRelativeTransform(RecoveryRoot);
    TMap<FName,FTransform> SnapshotTargets;
    EvaluateRecoveryPose(0, 0, 0, SnapshotTargets);
    SnapshotFirstError = 0;
    for (const auto& Entry : SnapshotTargets)
        SnapshotFirstError = FMath::Max(SnapshotFirstError, static_cast<float>(FVector::Distance(Entry.Value.GetLocation(), Body->GetSocketLocation(Entry.Key))));
    BalanceState = EDummyBalanceState::GettingUp;
    BalanceReason = FaceUp ? TEXT("Mixamo back") : TEXT("Mixamo stomach");
    StateSeconds = 0;
    RecoveringControls.Reset();
    return true;
}

void APhysicsControlDummy::DrivePose(const TMap<FName,FTransform>& Pose, float Strength)
{
    ReferencePose = Pose;
    for (const auto& Entry : Pose)
    {
        const FName Name = Entry.Key == TEXT("pelvis") ? PelvisControl : BodyControls.FindRef(Entry.Key);
        if (Name.IsNone()) continue;
        FPhysicsControlTarget Target;
        Target.TargetPosition = Entry.Value.GetLocation();
        Target.TargetOrientation = Entry.Value.Rotator();
        Target.bApplyControlPointToTarget = true;
        PhysicsControl->SetControlTarget(Name, Target);
        float RegionStrength = 1;
        if (const float* Remaining = RecoveringControls.Find(Name))
            RegionStrength = FMath::Lerp(FMath::Clamp(HitStrengthMultiplier,.005f,1.f), 1.f,
                FMath::Clamp(1.f - *Remaining / FMath::Clamp(HitRecoverySeconds,.1f,1.5f),0.f,1.f));
        FPhysicsControlMultiplier Multiplier;
        Multiplier.LinearStrengthMultiplier = FVector(Strength * RegionStrength);
        Multiplier.AngularStrengthMultiplier = Strength * RegionStrength;
        PhysicsControl->SetControlMultiplier(Name, Multiplier);
    }
    SupportTarget = Pose.FindChecked(TEXT("pelvis"));
    if (BalanceState == EDummyBalanceState::GettingUp)
    {
        const auto* Asset = Body->GetPhysicsAsset();
        for (int32 I=0; I<Asset->ConstraintSetup.Num(); ++I)
        {
            const auto& Default = Asset->ConstraintSetup[I]->DefaultInstance;
            const FTransform* Child = Pose.Find(Default.ConstraintBone1);
            const FTransform* Parent = Pose.Find(Default.ConstraintBone2);
            if (Child && Parent)
                if (auto* Joint = Body->GetConstraintInstanceByIndex(I))
                    Joint->WidenLimitsForDriveTarget(Child->GetRelativeTransform(*Parent).GetRotation(), Default);
        }
    }
}

void APhysicsControlDummy::UpdateBalance(float DeltaSeconds)
{
    if (!bReady || IsDead()) return;
    // Actor ticks receive world-scaled delta. No real-time timer drives support or recovery.
    const float Dt = FMath::Max(0.f, DeltaSeconds);
    StateSeconds += Dt; SinceDisturbance += Dt;
    LeftLegDisabled = FMath::Max(0.f, LeftLegDisabled - Dt);
    RightLegDisabled = FMath::Max(0.f, RightLegDisabled - Dt);
    if (SinceDisturbance > FMath::Max(0.f, RecoveryDelay))
        Instability = FMath::Max(0.f, Instability - FMath::Max(0.f, InstabilityRecoveryRate) * Dt);
    UsableFeet = 0;
    FHitResult Floor;
    if (LeftLegDisabled == 0 && FootSupported(TEXT("foot_l"))) ++UsableFeet;
    if (RightLegDisabled == 0 && FootSupported(TEXT("foot_r"))) ++UsableFeet;
    const FVector Pelvis = GetPhysicalBodyLocation(TEXT("pelvis"));
    const FVector Trunk = GetPhysicalBodyLocation(TEXT("spine_05"));
    const FVector Upright = (Trunk - Pelvis).GetSafeNormal();
    PoseLeanDegrees = FMath::RadiansToDegrees(FMath::Acos(FMath::Clamp(Upright.Z,-1.0,1.0)));
    PelvisDrop = StandingPose.FindChecked(TEXT("pelvis")).GetLocation().Z - Pelvis.Z;
    bRecoveryFloor = FindFloor(Pelvis, 120, Floor);
    if (bRecoveryFloor) GroundHeight = Floor.ImpactPoint.Z;
    bRecoveryClear = bRecoveryFloor && RecoverySpace(Pelvis, GroundHeight);

    if (BalanceState == EDummyBalanceState::Standing || BalanceState == EDummyBalanceState::LosingBalance)
    {
        NoSupportSeconds = UsableFeet == 0 ? NoSupportSeconds + Dt : 0;
        if ((LeftLegDisabled > 0 && RightLegDisabled > 0) || NoSupportSeconds > .18f)
            EnterFall(TEXT("no usable foot support"));
        else if (PoseLeanDegrees > FMath::Clamp(MaxLeanDegrees,20.f,80.f) || PelvisDrop > 52)
            EnterFall(TEXT("body exceeded recoverable deviation"));
        else
        {
            BalanceState = Instability > .08f || LeftLegDisabled > 0 || RightLegDisabled > 0 ? EDummyBalanceState::LosingBalance : EDummyBalanceState::Standing;
            auto Targets = StandingPose;
            const float Weight = FMath::Clamp(Instability / FMath::Max(.1f,FallThreshold), 0.f, 1.f);
            const FVector PelvisTarget = StandingPose.FindChecked(TEXT("pelvis")).GetLocation();
            const FVector Lean = LeanDirection.IsNearlyZero() ? Home.GetRotation().GetForwardVector() : LeanDirection;
            const FQuat Tilt(FVector::CrossProduct(FVector::UpVector,Lean).GetSafeNormal(), FMath::DegreesToRadians(Weight * 17.f));
            for (auto& Entry : Targets)
            {
                const FString Name = Entry.Key.ToString();
                FVector P = Entry.Value.GetLocation();
                if (Name.StartsWith(TEXT("foot"))) continue;
                if (IsLeg(Name))
                    P += Lean * (Name.StartsWith(TEXT("calf")) ? 15.f : 6.f) * Weight - FVector(0,0,Weight * (Name.StartsWith(TEXT("calf")) ? 6.f : 15.f));
                else
                {
                    P = PelvisTarget + Tilt.RotateVector(P-PelvisTarget) + Lean * Weight * 6 - FVector(0,0,Weight * 15);
                    Entry.Value.SetRotation(Tilt * Entry.Value.GetRotation());
                }
                Entry.Value.SetLocation(P);
            }
            DrivePose(Targets, 1.f - Weight * .28f);
            return;
        }
    }

    if (BalanceState == EDummyBalanceState::Falling || BalanceState == EDummyBalanceState::Down)
    {
        DisableBalanceDrives();
        float Speed = 0, Spin = 0;
        for (FName Bone : {FName("pelvis"),FName("spine_05"),FName("foot_l"),FName("foot_r")})
            if (auto* BI=Body->GetBodyInstance(Bone))
            { Speed=FMath::Max(Speed,static_cast<float>(BI->GetUnrealWorldVelocity().Size())); Spin=FMath::Max(Spin,static_cast<float>(BI->GetUnrealWorldAngularVelocityInRadians().Size())); }
        const bool Settled = bRecoveryFloor && Pelvis.Z - GroundHeight < 60 && Speed < 35 && Spin < 1.7;
        SettledSeconds = Settled ? SettledSeconds + Dt : 0;
        if (BalanceState == EDummyBalanceState::Falling && SettledSeconds > .25f)
        { BalanceState=EDummyBalanceState::Down; StateSeconds=0; }
        if (BalanceState == EDummyBalanceState::Down && SettledSeconds >= FMath::Max(.3f,SettleSeconds) && SinceDisturbance > 1.5f && bRecoveryClear)
            BeginGetUp();
        return;
    }

    if (BalanceState == EDummyBalanceState::GettingUp && ActiveGetUp)
    {
        float DestinationFloor;
        if (LeftLegDisabled > 0 || RightLegDisabled > 0 || !bRecoveryClear ||
            !RecoverySpace(GetUpEndPose.FindChecked(TEXT("pelvis")).GetLocation(),DestinationFloor))
        { EnterFall(TEXT("recovery support/clearance lost")); return; }
        const float BlendSeconds = FMath::Max(.2f,GetUpBlendSeconds);
        // Playback starts immediately while the snapshot blends out; no first-frame hold.
        const float MotionTime = GetRecoveryAnimationTime();
        TMap<FName,FTransform> Targets;
        const float Blend = FMath::SmoothStep(0.f,BlendSeconds,StateSeconds);
        const float EndBlend = FMath::SmoothStep(0.f,1.f,MotionTime-ActiveGetUp->GetPlayLength());
        EvaluateRecoveryPose(FMath::Min(MotionTime, ActiveGetUp->GetPlayLength()), Blend, EndBlend, Targets);
        // End in the retained idle at the recovered location/heading. The physical
        // mesh stays simulated and all targets interpolate through this handover.
        if (MotionTime >= ActiveGetUp->GetPlayLength())
        {
            if (EndBlend >= 1 && UsableFeet > 0 && PoseLeanDegrees < 25)
            {
                StandingPose=Targets; StandingForward=RecoveredIdleRoot.GetRotation().RotateVector(FVector::RightVector); Instability=0; NoSupportSeconds=0;
                BalanceState=EDummyBalanceState::Standing; StateSeconds=0;
                ++GetUps; ActiveGetUp=nullptr; BalanceReason=TEXT("recovered without health restoration");
            }
            else if (MotionTime > ActiveGetUp->GetPlayLength()+3)
            { EnterFall(TEXT("recovery could not reach standing")); return; }
        }
        DrivePose(Targets, FMath::Lerp(.15f,1.f,Blend));
    }
}

void APhysicsControlDummy::AddBalanceState(TSharedPtr<FJsonObject> Root) const
{
    auto S=MakeShared<FJsonObject>();
    S->SetStringField(TEXT("state"),GetBalanceLabel());
    S->SetStringField(TEXT("reason"),BalanceReason);
    S->SetNumberField(TEXT("instability"),Instability);
    S->SetNumberField(TEXT("state_seconds"),StateSeconds);
    S->SetNumberField(TEXT("since_disturbance"),SinceDisturbance);
    S->SetNumberField(TEXT("left_leg_disabled"),LeftLegDisabled);
    S->SetNumberField(TEXT("right_leg_disabled"),RightLegDisabled);
    S->SetNumberField(TEXT("usable_feet"),UsableFeet);
    S->SetNumberField(TEXT("lean_degrees"),PoseLeanDegrees);
    S->SetNumberField(TEXT("pelvis_drop_cm"),PelvisDrop);
    S->SetNumberField(TEXT("settled_seconds"),SettledSeconds);
    S->SetBoolField(TEXT("recovery_floor"),bRecoveryFloor);
    S->SetBoolField(TEXT("recovery_clear"),bRecoveryClear);
    S->SetNumberField(TEXT("falls"),Falls);
    S->SetNumberField(TEXT("get_ups"),GetUps);
    S->SetNumberField(TEXT("interruptions"),InterruptedGetUps);
    S->SetStringField(TEXT("animation"),ActiveGetUp ? ActiveGetUp->GetName() : TEXT(""));
    S->SetNumberField(TEXT("animation_time"),ActiveGetUp ? FMath::Min(GetRecoveryAnimationTime(),ActiveGetUp->GetPlayLength()) : 0);
    S->SetNumberField(TEXT("snapshot_bones"),FallenSnapshot.LocalTransforms.Num());
    S->SetNumberField(TEXT("skeleton_bones"),Body->GetNumBones());
    S->SetNumberField(TEXT("snapshot_first_error_cm"),SnapshotFirstError);
    S->SetNumberField(TEXT("lod"),Body->GetPredictedLODLevel());
    S->SetNumberField(TEXT("ground_z"),GroundHeight);
    S->SetNumberField(TEXT("sole_tolerance_cm"),1.f);
    S->SetNumberField(TEXT("sole_left_z"),SoleBottom(Body,true));
    S->SetNumberField(TEXT("sole_right_z"),SoleBottom(Body,false));
    for (const TCHAR* Bone : {TEXT("foot_l"),TEXT("foot_r")})
        if (const auto* BI = Body->GetBodyInstance(Bone))
            S->SetNumberField(FString(Bone)+TEXT("_shape_bottom_z"),ShapeBottom(Bone,BI->GetUnrealWorldTransform()));
    int32 Enabled=0;
    for (FName Name:Controls) if (PhysicsControl->GetControlEnabled(Name)) ++Enabled;
    S->SetNumberField(TEXT("enabled_drives"),Enabled);
    Root->SetObjectField(TEXT("balance"),S);
}
