#include "PhysicsControlDummy.h"
#include "CombatProjectileWorld.h"
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
    case EDummyBalanceState::Stepping: return TEXT("STEPPING");
    default: return TEXT("CORPSE");
    }
}

void APhysicsControlDummy::ResetBalance()
{
    PendingFallImpact = {};
    PendingFallRotation = {};
    bFallRotationApplied = false;
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
    ResetStepping();
    ResetRecoverability();
}

void APhysicsControlDummy::DisableBalanceDrives()
{
    RecoveringControls.Reset();
    for (FName Name : Controls) PhysicsControl->SetControlEnabled(Name, false);
}

void APhysicsControlDummy::EnterFall(const TCHAR* Reason)
{
    if (IsDead()) return;
    const bool bNewFall = BalanceState != EDummyBalanceState::Falling && BalanceState != EDummyBalanceState::Down;
    if (BalanceState == EDummyBalanceState::GettingUp) ++InterruptedGetUps;
    if (BalanceState != EDummyBalanceState::Falling && BalanceState != EDummyBalanceState::Down) ++Falls;
    BalanceState = EDummyBalanceState::Falling;
    StateSeconds = SettledSeconds = 0;
    BalanceReason = Reason;
    ActiveGetUp = nullptr;
    CancelStep();
    Body->bPauseAnims = true;
    DisableBalanceDrives();
    Body->WakeAllRigidBodies();
    if (bNewFall && PendingFallImpact.Deadline >= GetWorld()->GetTimeSeconds())
    {
        if (auto* BI = Body->GetBodyInstance(PendingFallImpact.Bone))
        {
            const FVector Point = BI->GetUnrealWorldTransform().TransformPosition(PendingFallImpact.LocalPoint);
            Body->AddImpulseAtLocation(PendingFallImpact.BonusImpulse, Point, PendingFallImpact.Bone);
            if (PendingFallImpact.bAllowRotation && !bFallRotationApplied)
                PendingFallRotation = PendingFallImpact;
            if (PendingFallImpact.Contact)
            {
                const FVector& Bonus = PendingFallImpact.BonusImpulse;
                PendingFallImpact.Contact->SetField(TEXT("fall_bonus_impulse"), MakeShared<FJsonValueArray>(
                    TArray<TSharedPtr<FJsonValue>>{MakeShared<FJsonValueNumber>(Bonus.X),
                        MakeShared<FJsonValueNumber>(Bonus.Y), MakeShared<FJsonValueNumber>(Bonus.Z)}));
                PendingFallImpact.Contact->SetNumberField(TEXT("impulse_count"), 2);
            }
        }
    }
    PendingFallImpact = {};
    // The fully simulated current visible pose and velocities remain authoritative.
}

void APhysicsControlDummy::ApplyPendingFallRotation()
{
    const FPendingFallImpact Accent = PendingFallRotation;
    PendingFallRotation = {};
    if (!bReady || bFallRotationApplied || !Accent.bAllowRotation ||
        (BalanceState != EDummyBalanceState::Falling && BalanceState != EDummyBalanceState::Dead)) return;
    const FName Bone = Accent.Bone;
    if (Bone != TEXT("spine_03") && Bone != TEXT("spine_04") && Bone != TEXT("spine_05") &&
        Bone != TEXT("clavicle_l") && Bone != TEXT("clavicle_r")) return;
    if (Accent.BonusImpulse.ContainsNaN() || !FMath::IsFinite(UpperBodyFallRotationRatio) ||
        !FMath::IsFinite(UpperBodyFallLegSpeed)) return;
    const FVector ShotDirection = Accent.BonusImpulse.GetSafeNormal2D();
    if (ShotDirection.IsNearlyZero() || Accent.BonusImpulse.GetSafeNormal().SizeSquared2D() < .25) return;

    auto* Chest = Body->GetBodyInstance(TEXT("spine_05"));
    auto* Pelvis = Body->GetBodyInstance(TEXT("pelvis"));
    auto* Left = Body->GetBodyInstance(TEXT("calf_l"));
    auto* Right = Body->GetBodyInstance(TEXT("calf_r"));
    if (!Chest || !Pelvis || !Left || !Right || !Chest->IsInstanceSimulatingPhysics() ||
        !Left->IsInstanceSimulatingPhysics() || !Right->IsInstanceSimulatingPhysics()) return;
    const FVector Torso = Chest->GetCOMPosition() - Pelvis->GetCOMPosition();
    if (Torso.Z < 20.f || Torso.GetSafeNormal().Z < .5f) return;
    const float LeftMass = Left->GetBodyMass(), RightMass = Right->GetBodyMass(), ChestMass = Chest->GetBodyMass();
    if (!FMath::IsFinite(LeftMass) || !FMath::IsFinite(RightMass) || !FMath::IsFinite(ChestMass) ||
        LeftMass <= 0.f || RightMass <= 0.f || ChestMass <= 0.f) return;

    // The legs move together; the equal chest reaction adds a couple with zero net impulse.
    // Cap the whole pair before splitting it so neither reaction is independently clipped.
    const float LegMass = LeftMass + RightMass;
    const float SpeedCap = FMath::Clamp(UpperBodyFallLegSpeed, 0.f, 400.f);
    const float Magnitude = FMath::Min(static_cast<float>(Accent.BonusImpulse.Size()) *
        FMath::Clamp(UpperBodyFallRotationRatio, 0.f, 1.f), FMath::Min(LegMass, ChestMass) * SpeedCap);
    if (Magnitude <= 0.f) return;
    const FVector LegImpulse = (-ShotDirection + FVector::UpVector * .65f).GetSafeNormal() * Magnitude;
    Body->WakeAllRigidBodies();
    Body->AddImpulseAtLocation(LegImpulse * (LeftMass / LegMass), Left->GetCOMPosition(), TEXT("calf_l"));
    Body->AddImpulseAtLocation(LegImpulse * (RightMass / LegMass), Right->GetCOMPosition(), TEXT("calf_r"));
    Body->AddImpulseAtLocation(-LegImpulse, Chest->GetCOMPosition(), TEXT("spine_05"));
    bFallRotationApplied = true;
    if (Accent.Contact)
    {
        Accent.Contact->SetField(TEXT("fall_rotation_leg_impulse"), MakeShared<FJsonValueArray>(
            TArray<TSharedPtr<FJsonValue>>{MakeShared<FJsonValueNumber>(LegImpulse.X),
                MakeShared<FJsonValueNumber>(LegImpulse.Y), MakeShared<FJsonValueNumber>(LegImpulse.Z)}));
        Accent.Contact->SetNumberField(TEXT("fall_rotation_impulse_count"), 3);
    }
}

void APhysicsControlDummy::RegisterDisturbance(FName Bone, const FVector& Impulse, float Amount)
{
    if (IsDead()) return;
    SinceDisturbance = SettledSeconds = 0;
    Instability = FMath::Min(2.f, Instability + FMath::Max(0.f, Amount));
    LeanDirection = (LeanDirection * .3f + Impulse.GetSafeNormal2D()).GetSafeNormal2D();
    LastStepImpulse = Impulse;
    if (StepPhase && !bAdaptiveReplanPending)
    {
        bAdaptiveReplanPending = true;
        AdaptiveReplanAge = 0;
    }
    // The request clock belongs to the recovery, not to the latest bullet.
    if (!bStepRequested) StepRequestSeconds = 0;
    bStepRequested = true;
    const FString Name = Bone.ToString();
    if (IsLeg(Name))
    {
        DisturbedFoot = Name.EndsWith(TEXT("_l")) ? TEXT("foot_l") : TEXT("foot_r");
    }
    if (BalanceState == EDummyBalanceState::GettingUp) EnterFall(TEXT("recovery interrupted by disturbance"));
    else if (BalanceState == EDummyBalanceState::Standing) BalanceState = EDummyBalanceState::LosingBalance;
}

void APhysicsControlDummy::ApplyExternalDisturbance(FVector Impulse, FVector WorldPoint, FName Bone)
{
    auto* BI = Body->GetBodyInstance(Bone);
    if (!bReady || !BI || Impulse.ContainsNaN() || WorldPoint.ContainsNaN()) return;
    Impulse = Impulse.GetClampedToMaxSize(FMath::Min(18000.f, BI->GetBodyMass() * 700.f));
    if (Impulse.IsNearlyZero()) return;
    PendingFallImpact = {};
    PendingFallRotation = {};
    RegisterDisturbance(Bone, Impulse, Impulse.Size() / 5000.f);
    Body->WakeAllRigidBodies();
    Body->AddImpulseAtLocation(Impulse, WorldPoint, Bone);
}

bool APhysicsControlDummy::FindFloor(const FVector& Point, float Depth, FHitResult& Hit) const
{
    FCollisionQueryParams Query(SCENE_QUERY_STAT(DummySupport), false, this);
    Query.AddIgnoredActor(Body->GetOwner());
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
    Query.AddIgnoredActor(Body->GetOwner());
    return !GetWorld()->OverlapBlockingTestByChannel(FVector(Center.X,Center.Y,FloorZ + 101), FQuat::Identity,
        ECC_WorldStatic, FCollisionShape::MakeCapsule(29, 90), Query);
}

void APhysicsControlDummy::SampleAnimation(UAnimSequence* Animation, float Time, const FTransform& Origin,
    TMap<FName,FTransform>& Pose)
{
    PoseSource->SetWorldTransform(Origin);
    auto* Anim = CastChecked<UDummyRecoveryAnimInstance>(PoseSource->GetAnimInstance());
    Anim->bSnapshotOnly = false;
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
        if (IsLeg(Entry.Key.ToString())) RegionStrength = FMath::Max(RegionStrength,FMath::Clamp(RecoveryLegStrength,.15f,1.f));
        FPhysicsControlMultiplier Multiplier;
        Multiplier.LinearStrengthMultiplier = FVector(Strength * RegionStrength);
        Multiplier.AngularStrengthMultiplier = Strength * RegionStrength;
        if (BalanceState == EDummyBalanceState::Stepping && UsableFeet > 0 && bRecoveryFeasible &&
            !IsLeg(Entry.Key.ToString()))
        {
            // A supported recovery reserves bounded posture effort under a burst.
            // Translational hit compliance and each real impulse remain intact;
            // a new hit cannot continually reset all available postural effort.
            Multiplier.AngularStrengthMultiplier=Strength*FMath::Max(RegionStrength,FMath::Min(.65f,.28f*EffectiveStrength));
        }
        if ((BalanceState == EDummyBalanceState::Stepping ||
            (bStepRequested && LeftLegDisabled <= 0 && RightLegDisabled <= 0 &&
             (BalanceState == EDummyBalanceState::Standing || BalanceState == EDummyBalanceState::LosingBalance))) &&
            (Entry.Key == TEXT("foot_l") || Entry.Key == TEXT("foot_r")))
        {
            Multiplier.LinearStrengthMultiplier = FVector(RegionStrength * FMath::Clamp(StepFootStrength, 8.f, 30.f) / FMath::Clamp(PoseLinearStrength, .1f, 15.f));
            Multiplier.AngularStrengthMultiplier = RegionStrength * 2.f;
        }
        PhysicsControl->SetControlMultiplier(Name, Multiplier);
    }
    SupportTarget = Pose.FindChecked(TEXT("pelvis"));
    if (BalanceState == EDummyBalanceState::GettingUp || BalanceState == EDummyBalanceState::Stepping)
    {
        const auto* Asset = Body->GetPhysicsAsset();
        for (int32 I=0; I<Asset->ConstraintSetup.Num(); ++I)
        {
            const auto& Default = Asset->ConstraintSetup[I]->DefaultInstance;
            if (BalanceState == EDummyBalanceState::Stepping && IsLeg(Default.ConstraintBone1.ToString())) continue;
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
    StepCooldownRemaining = FMath::Max(0.f, StepCooldownRemaining - Dt);
    LeftLegDisabled = FMath::Max(0.f, LeftLegDisabled - Dt);
    RightLegDisabled = FMath::Max(0.f, RightLegDisabled - Dt);
    if (SinceDisturbance > FMath::Max(0.f, RecoveryDelay))
        Instability = FMath::Max(0.f, Instability - FMath::Max(0.f, InstabilityRecoveryRate) * Dt);
    UsableFeet = 0;
    FHitResult Floor;
    const FVector Pelvis = GetPhysicalBodyLocation(TEXT("pelvis"));
    const FVector Trunk = GetPhysicalBodyLocation(TEXT("spine_05"));
    const FVector Upright = (Trunk - Pelvis).GetSafeNormal();
    PoseLeanDegrees = FMath::RadiansToDegrees(FMath::Acos(FMath::Clamp(Upright.Z,-1.0,1.0)));
    PelvisDrop = StandingPose.FindChecked(TEXT("pelvis")).GetLocation().Z - Pelvis.Z;
    bRecoveryFloor = FindFloor(Pelvis, 120, Floor);
    if (bRecoveryFloor) GroundHeight = Floor.ImpactPoint.Z;
    bRecoveryClear = bRecoveryFloor && RecoverySpace(Pelvis, GroundHeight);
    UpdateRecoverability(Dt);

    if (BalanceState == EDummyBalanceState::Stepping)
    {
        UpdateStep(Dt);
        return;
    }

    if (BalanceState == EDummyBalanceState::Standing || BalanceState == EDummyBalanceState::LosingBalance)
    {
        {
            if (!bStanceCorrectionPending && RecoveryStableSeconds > .35f && SinceDisturbance > .5f && !bStepRequested)
            { EpisodeSteps = 0; bStepRequested = false; }
            if (bStepRequested && StepRequestSeconds >= FMath::Clamp(RecoveryReactionSeconds,.06f,.3f)/EffectiveSpeed && StepCooldownRemaining <= 0 && UsableFeet > 0)
            {
                if (BeginStep()) UpdateStep(0);
                return;
            }
            BalanceState = bStanceCorrectionPending || bStepRequested || RecoveryStableSeconds < .25f ? EDummyBalanceState::LosingBalance : EDummyBalanceState::Standing;
            auto Targets = StandingPose;
            // Physical hit softening supplies the disturbance. Do not manufacture
            // crouch/leg collapse from a bullet counter while evaluating support.
            const float Weight = 0;
            const FVector PelvisTarget = StandingPose.FindChecked(TEXT("pelvis")).GetLocation();
            const FVector Lean = LeanDirection.IsNearlyZero() ? StandingForward : LeanDirection;
            const FQuat Tilt(FVector::CrossProduct(FVector::UpVector,Lean).GetSafeNormal(), FMath::DegreesToRadians(Weight * 17.f));
            for (auto& Entry : Targets)
            {
                const FString Name = Entry.Key.ToString();
                FVector P = Entry.Value.GetLocation();
                if (Name.StartsWith(TEXT("foot"))) continue;
                if (IsLeg(Name) && bStepRequested) continue;
                if (IsLeg(Name))
                    P += Lean * (Name.StartsWith(TEXT("calf")) ? 15.f : 6.f) * Weight - FVector(0,0,Weight * (Name.StartsWith(TEXT("calf")) ? 6.f : 15.f));
                else
                {
                    P = PelvisTarget + Tilt.RotateVector(P-PelvisTarget) + Lean * Weight * 6 - FVector(0,0,Weight * (bStepRequested ? 4.f : 15.f));
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
                RememberStandingSkeleton(PoseSource);
                EpisodeSteps=0; bStepRequested=false;
                RecoveryInvalidSeconds=RecoveryNoProgressSeconds=StepRequestSeconds=0;
                RecoveryStableSeconds=.3f; RecoveryBestError=CaptureDistance;
                bRecoveryFeasible=true; DisturbedFoot=NAME_None;
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
    AddStepState(Root);
    AddRecoverabilityState(Root);
}
