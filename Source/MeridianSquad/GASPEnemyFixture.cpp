#include "GASPEnemyFixture.h"
#include "CombatProjectileWorld.h"
#include "DummyRecoveryAnimInstance.h"
#include "PhysicsControlComponent.h"
#include "MoverComponent.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimSequence.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "GameFramework/Pawn.h"
#include "PhysicsEngine/BodyInstance.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/PhysicsConstraintTemplate.h"
#include "PhysicsEngine/SkeletalBodySetup.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/StructOnScope.h"
#include "UObject/UnrealType.h"

namespace
{
const TCHAR* FoundationPath = TEXT("/GASPEnemyFoundation01/Blueprints/SandboxCharacter_Mover_Ragdoll.SandboxCharacter_Mover_Ragdoll_C");
const TCHAR* IdlePath = TEXT("/GASPEnemyFoundation01/Characters/UEFN_Mannequin/Animations/Idle/M_Neutral_Stand_Idle_Loop.M_Neutral_Stand_Idle_Loop");
const TCHAR* ScopedPhysicsPath = TEXT("/GASPEnemyFoundation01/Characters/UEFN_Mannequin/Rigs/PA_MSQ98_Recovery.PA_MSQ98_Recovery");

TSharedPtr<FJsonValue> Vector98(FVector V)
{
    return MakeShared<FJsonValueArray>(TArray<TSharedPtr<FJsonValue>>{
        MakeShared<FJsonValueNumber>(V.X), MakeShared<FJsonValueNumber>(V.Y), MakeShared<FJsonValueNumber>(V.Z)});
}
}

UGASPEnemyPhysicsTick::UGASPEnemyPhysicsTick()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.TickGroup = TG_PrePhysics;
}

void UGASPEnemyPhysicsTick::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    if (TickType == LEVELTICK_All)
        if (auto* Enemy = Cast<AGASPEnemyFixture>(GetOwner())) Enemy->UpdateFoundationPhysics(DeltaTime);
}

AGASPEnemyFixture::AGASPEnemyFixture()
{
    // The inherited mesh/control subobjects retain the old class's construction contract.
    // They never simulate or render in this adopted foundation.
    UnusedLegacyBody = Body;
    UnusedLegacyControls = PhysicsControl;
    UnusedLegacyBody->SetVisibility(false, true);
    UnusedLegacyBody->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    UnusedLegacyBody->SetComponentTickEnabled(false);
    UnusedLegacyControls->SetComponentTickEnabled(false);
    FoundationPhysicsTick = CreateDefaultSubobject<UGASPEnemyPhysicsTick>(TEXT("FoundationPhysicsTick"));
    FoundationPhysicsTick->AddTickPrerequisiteActor(this);
    ConfigureReactionProfile(1);
}

AGASPEnemyFixture* AGASPEnemyFixture::FromFoundation(const AActor* Actor)
{
    return Actor ? Cast<AGASPEnemyFixture>(Actor->GetOwner()) : nullptr;
}

void AGASPEnemyFixture::SetAuthority(EGASPEnemyAuthority NewAuthority)
{
    if (Authority == NewAuthority) return;
    Authority = NewAuthority;
    ++AuthorityChanges;
    UpdateRagdollLegLimits(0.f);
}

bool AGASPEnemyFixture::AllowsSamplePhysics() const
{
    return bSampleTransition || Authority == EGASPEnemyAuthority::Locomotion || Authority == EGASPEnemyAuthority::GettingUp;
}

void AGASPEnemyFixture::SetMovementCommand(FVector WorldDirection, bool bWalk)
{
    if (WorldDirection.ContainsNaN()) return;
    MovementCommand = WorldDirection.GetSafeNormal2D();
    bWalkCommand = bWalk;
}

void AGASPEnemyFixture::StopMovementCommand() { MovementCommand = FVector::ZeroVector; }
void AGASPEnemyFixture::SetHandOccupancy(bool bLeftOccupied, bool bRightOccupied)
{
    bLeftHandOccupied = bLeftOccupied;
    bRightHandOccupied = bRightOccupied;
}

FVector AGASPEnemyFixture::GetMovementIntent() const
{
    return bReady && !IsDead() && Authority == EGASPEnemyAuthority::Locomotion ? MovementCommand : FVector::ZeroVector;
}

void AGASPEnemyFixture::ProduceInput_Implementation(int32 SimTimeMs, FMoverInputCmdContext& InputCmdResult)
{
    // Keep GASP's input production and custom payloads, then repair the handoff
    // before Mover caches the command and the sample reuses its orientation.
    for (UObject* Producer : FoundationInputProducers)
        if (IsValid(Producer))
            IMoverInputProducerInterface::Execute_ProduceInput(Producer, SimTimeMs, InputCmdResult);

    if (!Foundation || !Mover || Mover->GetMovementModeName() != TEXT("Ragdoll")) return;
    auto* Inputs = InputCmdResult.InputCollection.FindMutableDataByType<FCharacterDefaultInputs>();
    if (Inputs && Inputs->OrientationIntent.IsNearlyZero())
    {
        // GASP's parent orientation switch has no Ragdoll branch. Once Walking
        // is queued, the child's Ragdoll override stops, leaving a zero vector.
        // The next idle Walking input converts that zero to +X and turns around.
        Inputs->OrientationIntent = Foundation->GetActorForwardVector();
        // Idle orientation reads this Blueprint cache, not Mover's last command.
        if (auto* Cached = FindFProperty<FStructProperty>(Foundation->GetClass(), TEXT("MoverDefaultInputs_PreSim")))
            if (Cached->Struct == FCharacterDefaultInputs::StaticStruct())
                Cached->ContainerPtrToValuePtr<FCharacterDefaultInputs>(Foundation)->OrientationIntent = Inputs->OrientationIntent;
    }
}

FTransform AGASPEnemyFixture::GetRagdollAnchor(const FTransform& SampleAnchor) const
{
    if (!bAdopted || !Body) return SampleAnchor;
    // Walking is queued, not applied immediately. Keep the upright anchor while
    // Mover consumes the last Ragdoll input during a supported recovery exit.
    const bool bUprightExit = Authority == EGASPEnemyAuthority::Locomotion && Mover &&
        Mover->GetMovementModeName() == TEXT("Ragdoll");
    if (Authority != EGASPEnemyAuthority::Recovery && !bUprightExit)
    {
        const auto* Pelvis = Body->GetBodyInstance(TEXT("pelvis"));
        const auto* Chest = Body->GetBodyInstance(TEXT("spine_05"));
        if (!Pelvis || !Chest) return SampleAnchor;
        const FTransform P = Pelvis->GetUnrealWorldTransform(), C = Chest->GetUnrealWorldTransform();
        FVector Heading = C.GetLocation() - P.GetLocation();
        if (C.GetUnitAxis(EAxis::Y).Z > 0) Heading *= -1;
        Heading.Z = 0;
        if (Heading.IsNearlyZero()) Heading = Foundation->GetActorForwardVector();
        // After montage interruption the animation component can briefly retain
        // a different root basis. The actual Chaos bodies remain authoritative.
        return FTransform(Heading.Rotation(), P.GetLocation());
    }
    // GASP's prone-body heading projects the pelvis-to-chest axis onto the floor.
    // That projection is ill-conditioned during upright stepping. Track the
    // actual physical pelvis with the retained upright heading instead.
    FVector Location = GetPhysicalBodyLocation(TEXT("pelvis")) - StandingPelvisOffset;
    Location.Z = GetPhysicalBodyLocation(TEXT("pelvis")).Z;
    return FTransform(StandingForward.Rotation(), Location);
}

void AGASPEnemyFixture::CallFoundation(FName Function, const TMap<FString,FString>& Arguments)
{
    if (!IsValid(Foundation)) return;
    UFunction* Method = Foundation->FindFunction(Function);
    if (!Method) return;
    FStructOnScope Parameters(Method);
    for (const auto& Entry : Arguments)
        if (FProperty* Property = FindFProperty<FProperty>(Method, *Entry.Key))
            Property->ImportText_Direct(*Entry.Value, Property->ContainerPtrToValuePtr<void>(Parameters.GetStructMemory()), Foundation, PPF_None);
    Foundation->ProcessEvent(Method, Parameters.GetStructMemory());
}

void AGASPEnemyFixture::SetSourceProfile(FName Profile)
{
    TGuardValue<bool> Transition(bSampleTransition, true);
    CallFoundation(TEXT("SetPhysicsProfile"), {{TEXT("PhysicsProfile"), Profile.ToString()}});
}

void AGASPEnemyFixture::ResetDummy()
{
    ClearBalanceProbeFixtures();
    bReady = bAdopted = false;
    PreFallLegLimits.Reset();
    HandoffPose.Reset();
    HandoffSeconds = 0;
    if (IsValid(Foundation)) FoundationPhysicsTick->RemoveTickPrerequisiteActor(Foundation);
    if (IsValid(Body)) FoundationPhysicsTick->RemoveTickPrerequisiteComponent(Body);
    if (IsValid(PhysicsControl))
        for (auto& Prerequisite : PhysicsControl->PrimaryComponentTick.GetPrerequisites())
            if (auto* Tick = Prerequisite.Get())
                FoundationPhysicsTick->PrimaryComponentTick.RemovePrerequisite(Prerequisite.PrerequisiteObject.Get(), *Tick);
    if (IsValid(PhysicsControl) && !Controls.IsEmpty()) PhysicsControl->DestroyControls(Controls);
    Controls.Reset(); BodyControls.Reset(); RecoveringControls.Reset(); SampleControls.Reset();
    if (IsValid(Foundation)) Foundation->Destroy();
    Foundation = nullptr; Mover = nullptr; Capsule = nullptr; FoundationAnimation = nullptr;
    FoundationInputProducers.Reset();
    Body = UnusedLegacyBody; PhysicsControl = UnusedLegacyControls;
    SetActorTransform(Home, false, nullptr, ETeleportType::TeleportPhysics);
    Health = FMath::Clamp(MaxHealth, 1.f, 100000.f);
    Deaths = PhysicalHits = 0;
    DeathFrame = 0; DeathTime = -1;
    Contacts.Reset(); SolePoints.Reset();
    ++PoseEpoch;
    Authority = EGASPEnemyAuthority::Locomotion;
    AuthorityChanges = 0;
    AdoptionSeconds = GetUpSeconds = 0;
    bPendingGetUp = bHadGetUpMontage = false;
    LastSelectedMontage.Reset();
    ArmTrunkContacts.Reset(); PeakArmTrunkImpulse = 0;
    StopMovementCommand();
    ResetBalance();
    UClass* Class = LoadClass<APawn>(nullptr, FoundationPath);
    if (!Class) { BalanceReason = TEXT("GASP foundation class unavailable"); return; }
    FActorSpawnParameters Spawn;
    Spawn.Owner = this;
    Spawn.ObjectFlags |= RF_Transient;
    Spawn.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    FTransform Placement = Home;
    Placement.AddToTranslation(FVector(0, 0, 88));
    Foundation = GetWorld()->SpawnActor<APawn>(Class, Placement, Spawn);
    if (!Foundation) { BalanceReason = TEXT("GASP foundation spawn failed"); return; }
    Foundation->Tags.Add(TEXT("MSQ98_GASPEnemy"));
    Foundation->AddTickPrerequisiteActor(this);
    AdoptFoundation();
}

bool AGASPEnemyFixture::AdoptFoundation()
{
    if (bAdopted) return true;
    if (!IsValid(Foundation)) return false;
    auto* Mesh = Foundation->FindComponentByClass<USkeletalMeshComponent>();
    auto* Drives = Foundation->FindComponentByClass<UPhysicsControlComponent>();
    auto* Movement = Foundation->FindComponentByClass<UMoverComponent>();
    if (!Mesh || !Drives || !Movement || !Mesh->GetAnimInstance() || Drives->GetAllControlNames().IsEmpty()) return false;
    Body = Mesh; PhysicsControl = Drives; Mover = Movement;
    Capsule = Foundation->FindComponentByClass<UCapsuleComponent>();
    FoundationAnimation = Body->GetAnimInstance();
    if (auto* Asset = LoadObject<UPhysicsAsset>(nullptr, ScopedPhysicsPath))
        if (Body->GetPhysicsAsset() != Asset) Body->SetPhysicsAsset(Asset);
    Body->SetForcedLOD(1);
    Body->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    Body->SetNotifyRigidBodyCollision(true);
    Body->SetAllBodiesNotifyRigidBodyCollision(true);
    Body->OnComponentHit.AddUniqueDynamic(this, &AGASPEnemyFixture::OnBodyContact);
    Body->OnComponentHit.AddUniqueDynamic(this, &AGASPEnemyFixture::OnFoundationContact);
    PhysicsControl->AddTickPrerequisiteActor(this);
    // Use Physics Control's supported manual update seam. The extra tick keeps
    // the same animation -> targets -> drives order, with no double update.
    FoundationPhysicsTick->AddTickPrerequisiteActor(Foundation);
    FoundationPhysicsTick->AddTickPrerequisiteComponent(Body);
    PhysicsControl->SetComponentTickEnabled(false);
    SampleControls = PhysicsControl->GetAllControlNames();
    BoundSampleControls();
    Idle = LoadObject<UAnimSequence>(nullptr, IdlePath);
    PoseSource->SetSkeletalMesh(Body->GetSkeletalMeshAsset());
    PoseSource->SetAnimInstanceClass(UDummyRecoveryAnimInstance::StaticClass());
    Body->TickAnimation(0, false);
    Body->RefreshBoneTransforms();
    UnsupportedShapes = 0;
    for (const auto& Setup : Body->GetPhysicsAsset()->SkeletalBodySetups)
        UnsupportedShapes += Setup->AggGeom.ConvexElems.Num() + Setup->AggGeom.TaperedCapsuleElems.Num();
    for (FName Bone : {FName("pelvis"), FName("spine_05"), FName("foot_l"), FName("foot_r")})
        if (!Body->GetBodyInstance(Bone)) return false;
    CalibrateSoles();
    CaptureStandingBasis(true);
    IsolateSelfCollision();
    bAdopted = bReady = Idle && !SolePoints.IsEmpty() && UnsupportedShapes == 0;
    if (bAdopted)
    {
        // A dedicated producer owns the order rather than relying on the order
        // of independent component producers in UMoverComponent.
        FoundationInputProducers = Mover->InputProducers;
        Mover->InputProducer = this;
        Mover->InputProducers = {this};
    }
    BalanceReason = bReady ? TEXT("GASP locomotion owns animation and Mover") : TEXT("GASP body calibration incomplete");
    return bAdopted;
}

void AGASPEnemyFixture::CaptureStandingBasis(bool bNeutral)
{
    if (bNeutral && Idle)
    {
        TMap<FName,FTransform> Unused;
        SampleAnimation(Idle, 0, Body->GetComponentTransform(), Unused);
        RememberStandingSkeleton(PoseSource, true);
    }
    StandingPose.Reset();
    for (const auto& Setup : Body->GetPhysicsAsset()->SkeletalBodySetups)
        if (const auto* BI = Body->GetBodyInstance(Setup->BoneName))
            StandingPose.Add(Setup->BoneName, BI->GetUnrealWorldTransform());
    ReferencePose = StandingPose;
    SupportTarget = StandingPose.FindRef(TEXT("pelvis"));
    RememberStandingSkeleton(Body, false);
    StandingForward = Foundation->GetActorForwardVector();
}

void AGASPEnemyFixture::DisableSampleControls()
{
    for (FName Name : SampleControls) PhysicsControl->SetControlEnabled(Name, false);
}

void AGASPEnemyFixture::BoundSampleControls()
{
    for (FName Name : SampleControls)
    {
        FPhysicsControlData Data;
        if (!PhysicsControl->GetControlData(Name, Data)) continue;
        float Mass = 1;
        for (const auto& Setup : Body->GetPhysicsAsset()->SkeletalBodySetups)
            if (Name == Setup->BoneName || Name.ToString().EndsWith(TEXT("_") + Setup->BoneName.ToString()))
                if (const auto* BI = Body->GetBodyInstance(Setup->BoneName)) Mass = BI->GetBodyMass();
        Data.MaxForce = Mass * 3500.f;
        Data.MaxTorque = Mass * 180000.f;
        PhysicsControl->SetControlData(Name, Data);
    }
}

void AGASPEnemyFixture::EnforceSampleLimits()
{
    // Invoked directly after every source profile write, before Chaos uses it.
    // The sample creates its controls before the wrapper can adopt them.
    if (!bAdopted) AdoptFoundation();
    if (bAdopted) BoundSampleControls();
}

FVector AGASPEnemyFixture::StepJointLimits(FName Bone) const
{
    // Fixed envelope for the adopted UEFN constraint frames. No generated target
    // enlarges it; BuildStepPose still rejects every violating intermediate pose.
    const FString Name = Bone.ToString();
    return Name.StartsWith(TEXT("thigh")) ? FVector(90,45,40) :
        Name.StartsWith(TEXT("foot")) ? FVector(25,35,75) : FVector(8,15,95);
}

void AGASPEnemyFixture::PrepareStepLanding(FName Bone, FTransform& Target) const
{
    const int32 Index = Body->GetBoneIndex(Bone);
    if (!NeutralBones.IsValidIndex(Index)) return;
    // A locomotion interruption can start with a raised/rolled swing ankle.
    // Its landing is a flat sole at the measured floor, never that airborne Z.
    // Only the target changes; bounded forces move the actual physical foot.
    Target.SetRotation(NeutralBones[Index].GetRotation());
    Target.AddToTranslation(FVector(0, 0, GroundHeight + .15f - ShapeBottom(Bone, Target)));
}

void AGASPEnemyFixture::SetPoseOverride(bool bActive, const FPoseSnapshot* Snapshot)
{
    if (!IsValid(FoundationAnimation)) return;
    if (auto* Active = FindFProperty<FBoolProperty>(FoundationAnimation->GetClass(), TEXT("MSQRecoveryActive")))
        Active->SetPropertyValue_InContainer(FoundationAnimation, bActive);
    if (Snapshot) FoundationAnimation->AddPoseSnapshot(TEXT("MSQ98Recovery")) = *Snapshot;
}

void AGASPEnemyFixture::SetVisibleAnimationPose()
{
    FPoseSnapshot Snapshot;
    PoseSource->SnapshotPose(Snapshot);
    if (Snapshot.LocalTransforms.IsEmpty()) return;
    Snapshot.LocalTransforms[0] = (Snapshot.LocalTransforms[0] * PoseSource->GetComponentTransform()).GetRelativeTransform(Body->GetComponentTransform());
    SetPoseOverride(true, &Snapshot);
    Body->bPauseAnims = false;
}

void AGASPEnemyFixture::TakeRecoveryAuthority()
{
    if (!bReady || IsDead() || Authority == EGASPEnemyAuthority::Recovery) return;
    HandoffPose.Reset();
    SetAuthority(EGASPEnemyAuthority::Recovery);
    CaptureStandingBasis(true);
    StandingPelvisOffset = GetPhysicalBodyLocation(TEXT("pelvis")) - Foundation->GetActorLocation();
    if (auto* Freeze = FindFProperty<FBoolProperty>(Foundation->GetClass(), TEXT("Ragdoll_FreezeCapsuleRotation")))
        Freeze->SetPropertyValue_InContainer(Foundation, true);
    FPoseSnapshot Snapshot;
    Body->SnapshotPose(Snapshot);
    SetPoseOverride(true, &Snapshot);
    SetSourceProfile(TEXT("Ragdoll"));
    DisableSampleControls();
    PhysicsControl->SetBodyModifiersInSetMovementType(TEXT("All"), EPhysicsMovementType::Simulated);
    Body->SetAllBodiesSimulatePhysics(true);
    Body->SetAllBodiesPhysicsBlendWeight(1);
    Body->bBlendPhysics = true;
    if (Mover) Mover->QueueNextMode(TEXT("Ragdoll"));
    BalanceState = EDummyBalanceState::Standing;
    StateSeconds = 0;
    ResetRecoverability();
    CancelStep();
    if (Controls.IsEmpty()) InitializeBalanceDrives();
    // The inherited initializer enables its normal component tick. This pawn
    // uses the manual update seam, so do not leave a second drive update active.
    PhysicsControl->SetComponentTickEnabled(false);
    IsolateSelfCollision();
    BalanceReason = TEXT("bounded native recovery owns the adopted GASP bodies");
}

void AGASPEnemyFixture::ReleaseRecoveryAuthority()
{
    if (Authority == EGASPEnemyAuthority::Recovery && FoundationAnimation)
    {
        BeginPoseHandoff();
        // GASP's Blend Out Pose state reads this snapshot on every Ragdoll exit.
        // The get-up gate skips the sample's SavePoseSnapshot for upright exits;
        // without this capture it reuses a previous fallen pose (or the ref pose)
        // as the newly enabled physical controls' animation target.
        FoundationAnimation->SavePoseSnapshot(TEXT("Ragdoll"));
    }
    DisableBalanceDrives();
    if (!Controls.IsEmpty()) PhysicsControl->DestroyControls(Controls);
    Controls.Reset(); BodyControls.Reset(); RecoveringControls.Reset();
    SetAuthority(EGASPEnemyAuthority::Locomotion);
    SetSourceProfile(TEXT("PhysicalAnimation"));
    SetPoseOverride(false);
    if (Mover) Mover->QueueNextMode(TEXT("Walking"));
    Body->bPauseAnims = false;
    BalanceState = EDummyBalanceState::Standing;
    BalanceReason = TEXT("GASP locomotion resumed at recovered location");
}

void AGASPEnemyFixture::BeginPoseHandoff()
{
    HandoffPose.Reset();
    HandoffSeconds = 0;
    // Start at the actual physical pose, not the old solver's ideal standing
    // target. World space preserves the pose while Mover reanchors its capsule.
    for (const auto& Setup : Body->GetPhysicsAsset()->SkeletalBodySetups)
        if (const auto* BI = Body->GetBodyInstance(Setup->BoneName))
            HandoffPose.Add(Setup->BoneName, BI->GetUnrealWorldTransform());
}

void AGASPEnemyFixture::UpdateFoundationPhysics(float DeltaSeconds)
{
    if (!bAdopted || !IsValid(PhysicsControl) || !IsValid(Body)) return;
    PhysicsControl->UpdateTargetCaches(DeltaSeconds);
    if (Authority != EGASPEnemyAuthority::Locomotion) HandoffPose.Reset();
    if (!HandoffPose.IsEmpty())
    {
        const float T = FMath::Clamp(HandoffSeconds / HandoffDuration, 0.f, 1.f);
        // Zero first and second derivatives at both ends; the destination keeps
        // following live GASP animation rather than freezing an idle pose.
        const float Alpha = T * T * T * (T * (T * 6.f - 15.f) + 10.f);
        for (const auto& Entry : HandoffPose)
        {
            const FTransform Target = PhysicsControl->GetCachedBoneTransform(Body, Entry.Key);
            FTransform Blended;
            Blended.Blend(Entry.Value, Target, Alpha);
            PhysicsControl->SetCachedBoneData(Body, Entry.Key, Blended);
        }
        HandoffSeconds += DeltaSeconds;
        if (T >= 1.f) HandoffPose.Reset();
    }
    PhysicsControl->UpdateControls(DeltaSeconds);
    UpdateRagdollLegLimits(DeltaSeconds);
}

void AGASPEnemyFixture::UpdateRagdollLegLimits(float DeltaSeconds)
{
    if (!bAdopted || !IsValid(Body) || !Body->GetPhysicsAsset()) return;
    const bool bRagdoll = Authority == EGASPEnemyAuthority::Falling ||
        Authority == EGASPEnemyAuthority::Down || Authority == EGASPEnemyAuthority::Dead;
    const auto SetLimits = [](FConstraintInstance& Joint, const FVector& Limits)
    {
        if (!FMath::IsNearlyEqual(Joint.GetAngularSwing1Limit(), static_cast<float>(Limits.X), .001f))
            Joint.SetAngularSwing1Limit(ACM_Limited, Limits.X);
        if (!FMath::IsNearlyEqual(Joint.GetAngularSwing2Limit(), static_cast<float>(Limits.Y), .001f))
            Joint.SetAngularSwing2Limit(ACM_Limited, Limits.Y);
        if (!FMath::IsNearlyEqual(Joint.GetAngularTwistLimit(), static_cast<float>(Limits.Z), .001f))
            Joint.SetAngularTwistLimit(ACM_Limited, Limits.Z);
    };
    if (!bRagdoll)
    {
        // Restore the exact recovery envelope before the sample starts its get-up.
        // This only reopens limits; no pose or body velocity is overwritten.
        for (const auto& Entry : PreFallLegLimits)
            if (auto* Joint = Body->GetConstraintInstanceByIndex(Entry.Key)) SetLimits(*Joint, Entry.Value);
        PreFallLegLimits.Reset();
        return;
    }
    const auto* Asset = Body->GetPhysicsAsset();
    const float Dt = FMath::Clamp(DeltaSeconds, 0.f, .1f);
    for (int32 Index = 0; Index < Asset->ConstraintSetup.Num(); ++Index)
    {
        const auto& Authored = Asset->ConstraintSetup[Index]->DefaultInstance;
        const FString Bone = Authored.ConstraintBone1.ToString();
        if (!Bone.StartsWith(TEXT("thigh")) && !Bone.StartsWith(TEXT("calf")) && !Bone.StartsWith(TEXT("foot"))) continue;
        auto* Joint = Body->GetConstraintInstanceByIndex(Index);
        if (!Joint || Joint->GetAngularSwing1Motion() != ACM_Limited ||
            Joint->GetAngularSwing2Motion() != ACM_Limited || Joint->GetAngularTwistMotion() != ACM_Limited ||
            Authored.GetAngularSwing1Motion() != ACM_Limited || Authored.GetAngularSwing2Motion() != ACM_Limited ||
            Authored.GetAngularTwistMotion() != ACM_Limited) continue;
        const FVector Current(Joint->GetAngularSwing1Limit(), Joint->GetAngularSwing2Limit(), Joint->GetAngularTwistLimit());
        if (!PreFallLegLimits.Contains(Index)) PreFallLegLimits.Add(Index, Current);
        const FVector Original = PreFallLegLimits.FindRef(Index);
        FVector FallLimits(Authored.GetAngularSwing1Limit(), Authored.GetAngularSwing2Limit(), Authored.GetAngularTwistLimit());
        // Narrow the hip cone only during collapse, in the existing joint frames.
        // Knee flexion uses mirrored frame bias, so retain its authored envelope.
        if (Bone.StartsWith(TEXT("thigh")))
        {
            FallLimits.X = FMath::Min(FallLimits.X, 50.0);
            FallLimits.Y = FMath::Min(FallLimits.Y, 25.0);
        }
        FVector Next;
        for (int32 Axis = 0; Axis < 3; ++Axis)
            Next[Axis] = FMath::FInterpConstantTo(Current[Axis],
                FMath::Min(Current[Axis], FMath::Min(Original[Axis], FallLimits[Axis])), Dt, 120.0);
        // Keep the asset's asymmetric frame offsets. Recovery steps widen these
        // ranges; close them gradually during collapse instead of snapping them shut.
        SetLimits(*Joint, Next);
    }
}

void AGASPEnemyFixture::RegisterDisturbance(FName Bone, const FVector& Impulse, float Amount)
{
    if (Authority == EGASPEnemyAuthority::Locomotion) TakeRecoveryAuthority();
    APhysicsControlDummy::RegisterDisturbance(Bone, Impulse, Amount);
}

void AGASPEnemyFixture::EnterFall(const TCHAR* Reason)
{
    if (IsDead()) return;
    APhysicsControlDummy::EnterFall(Reason);
    SetAuthority(EGASPEnemyAuthority::Falling);
    if (auto* Freeze = FindFProperty<FBoolProperty>(Foundation->GetClass(), TEXT("Ragdoll_FreezeCapsuleRotation")))
        Freeze->SetPropertyValue_InContainer(Foundation, false);
    bPendingGetUp = false;
    SetPoseOverride(false);
    SetSourceProfile(TEXT("Ragdoll"));
    DisableSampleControls();
    PhysicsControl->SetBodyModifiersInSetMovementType(TEXT("All"), EPhysicsMovementType::Simulated);
    Body->SetAllBodiesSimulatePhysics(true);
    Body->SetAllBodiesPhysicsBlendWeight(1);
    Body->bPauseAnims = false;
    if (FoundationAnimation) FoundationAnimation->Montage_Stop(.1f);
    if (Mover) Mover->QueueNextMode(TEXT("Ragdoll"));
}

bool AGASPEnemyFixture::BeginGetUp()
{
    if (IsDead() || !bReady || bPendingGetUp || !bRecoveryFloor || !bRecoveryClear) return false;
    float Floor;
    if (!RecoverySpace(GetPhysicalBodyLocation(TEXT("pelvis")), Floor)) return false;
    DisableBalanceDrives();
    if (!Controls.IsEmpty()) PhysicsControl->DestroyControls(Controls);
    Controls.Reset(); BodyControls.Reset(); RecoveringControls.Reset();
    SetAuthority(EGASPEnemyAuthority::GettingUp);
    BalanceState = EDummyBalanceState::GettingUp;
    GetUpSeconds = StateSeconds = 0;
    bPendingGetUp = true;
    bHadGetUpMontage = false;
    SetPoseOverride(false);
    Body->bPauseAnims = false;
    // The copied GASP event overrides its pose history from the actual owning mesh,
    // evaluates CHT_GetUpMontages and plays its chosen montage through Mover.
    CallFoundation(TEXT("ExitRagdoll"));
    BalanceReason = TEXT("GASP supported pose-matched get-up");
    return true;
}

void AGASPEnemyFixture::UpdateBalance(float DeltaSeconds)
{
    if (!bReady || IsDead()) return;
    if (Authority == EGASPEnemyAuthority::Locomotion)
    {
        SinceDisturbance += DeltaSeconds;
        CaptureStandingBasis(false);
        return;
    }
    if (Authority == EGASPEnemyAuthority::GettingUp)
    {
        GetUpSeconds += DeltaSeconds;
        StateSeconds += DeltaSeconds;
        SinceDisturbance += DeltaSeconds;
        const FVector Pelvis = GetPhysicalBodyLocation(TEXT("pelvis"));
        FHitResult Floor;
        bRecoveryFloor = FindFloor(Pelvis, 120, Floor);
        if (bRecoveryFloor) GroundHeight = Floor.ImpactPoint.Z;
        bRecoveryClear = bRecoveryFloor && RecoverySpace(Pelvis, GroundHeight);
        if (!bRecoveryClear) { EnterFall(TEXT("GASP get-up support or clearance lost")); return; }
        UAnimMontage* Montage = FoundationAnimation ? FoundationAnimation->GetCurrentActiveMontage() : nullptr;
        if (Montage)
        {
            bHadGetUpMontage = true;
            LastSelectedMontage = Montage->GetPathName();
        }
        const FVector Upright = (GetPhysicalBodyLocation(TEXT("spine_05")) - Pelvis).GetSafeNormal();
        PoseLeanDegrees = FMath::RadiansToDegrees(FMath::Acos(FMath::Clamp(Upright.Z,-1.0,1.0)));
        if (bHadGetUpMontage && !Montage && PoseLeanDegrees < 25)
        {
            ++GetUps;
            bPendingGetUp = false;
            Instability = 0;
            CaptureStandingBasis(true);
            ReleaseRecoveryAuthority();
        }
        else if (GetUpSeconds > 10 || (!bHadGetUpMontage && GetUpSeconds > 1))
            EnterFall(TEXT("GASP get-up did not complete"));
        return;
    }
    APhysicsControlDummy::UpdateBalance(DeltaSeconds);
    if (BalanceState == EDummyBalanceState::Down) SetAuthority(EGASPEnemyAuthority::Down);
    if (Authority == EGASPEnemyAuthority::Recovery && BalanceState == EDummyBalanceState::Standing &&
        RecoveryStableSeconds > .45f && SinceDisturbance > .65f && !bStepRequested && !StepPhase)
        ReleaseRecoveryAuthority();
}

void AGASPEnemyFixture::BoundRecoveryDrives(float DeltaSeconds)
{
    if (Authority == EGASPEnemyAuthority::Recovery || Authority == EGASPEnemyAuthority::Falling || Authority == EGASPEnemyAuthority::Down)
    {
        DisableSampleControls();
        APhysicsControlDummy::BoundRecoveryDrives(DeltaSeconds);
    }
}

float AGASPEnemyFixture::ReceiveBullet(int64 ShotId, float Damage, const FVector& Direction, const FHitResult& Hit,
    double ContactTime, double BirthTime, uint64 CombatFrame, float FallImpulseMultiplier, float DeathImpulseMultiplier)
{
    if (!bReady || !Body->GetBodyInstance(Hit.BoneName) || !FMath::IsFinite(Damage) || Damage <= 0 || Direction.ContainsNaN()) return 0;
    if (Authority == EGASPEnemyAuthority::Locomotion) TakeRecoveryAuthority();
    const float Result = APhysicsControlDummy::ReceiveBullet(ShotId, Damage, Direction, Hit, ContactTime, BirthTime, CombatFrame,
        FallImpulseMultiplier, DeathImpulseMultiplier);
    if (IsDead())
    {
        SetAuthority(EGASPEnemyAuthority::Dead);
        DisableSampleControls();
        PhysicsControl->SetBodyModifiersInSetMovementType(TEXT("All"), EPhysicsMovementType::Simulated);
        Body->SetAllBodiesSimulatePhysics(true);
        Body->SetAllBodiesPhysicsBlendWeight(1);
        Body->bPauseAnims = true;
        bPendingGetUp = false;
        if (Mover) Mover->QueueNextMode(TEXT("Ragdoll"));
    }
    return Result;
}

void AGASPEnemyFixture::ApplyExternalDisturbance(FVector Impulse, FVector WorldPoint, FName Bone)
{
    if (!bReady || !Body->GetBodyInstance(Bone) || Impulse.ContainsNaN() || WorldPoint.ContainsNaN() || Impulse.IsNearlyZero()) return;
    if (Authority == EGASPEnemyAuthority::Locomotion) TakeRecoveryAuthority();
    APhysicsControlDummy::ApplyExternalDisturbance(Impulse, WorldPoint, Bone);
}

void AGASPEnemyFixture::Tick(float DeltaSeconds)
{
    if (!bAdopted)
    {
        AdoptionSeconds += DeltaSeconds;
        if (AdoptionSeconds < 5) AdoptFoundation();
        return;
    }
    if (IsValid(Foundation)) SetActorTransform(Foundation->GetActorTransform());
    // GASP installs its PostABPTick dependency later in BeginPlay than adoption.
    // Preserve all of those dependencies for the replacement update tick.
    for (auto& Prerequisite : PhysicsControl->PrimaryComponentTick.GetPrerequisites())
        if (auto* Tick = Prerequisite.Get())
            FoundationPhysicsTick->PrimaryComponentTick.AddPrerequisite(Prerequisite.PrerequisiteObject.Get(), *Tick);
    if (AllowsSamplePhysics()) BoundSampleControls();
    APhysicsControlDummy::Tick(DeltaSeconds);
}

void AGASPEnemyFixture::OnFoundationContact(UPrimitiveComponent* HitComponent, AActor* OtherActor,
    UPrimitiveComponent* OtherComponent, FVector NormalImpulse, const FHitResult& Hit)
{
    if (OtherComponent != Body || NormalImpulse.Size() < .01) return;
    const FString A = Hit.MyBoneName.ToString(), B = Hit.BoneName.ToString();
    auto Arm = [](const FString& N) { return N.StartsWith(TEXT("lowerarm")) || N.StartsWith(TEXT("hand")); };
    auto Trunk = [](const FString& N) { return N.StartsWith(TEXT("spine")) || N == TEXT("pelvis"); };
    if (!((Arm(A) && Trunk(B)) || (Arm(B) && Trunk(A)))) return;
    ++ArmTrunkContacts.FindOrAdd(Arm(A) ? A + TEXT("/") + B : B + TEXT("/") + A);
    PeakArmTrunkImpulse = FMath::Max(PeakArmTrunkImpulse, static_cast<float>(NormalImpulse.Size()));
}

FString AGASPEnemyFixture::GetDummyState(bool IncludeContacts) const
{
    if (!bAdopted) return FString::Printf(TEXT("{\"name\":\"%s\",\"ready\":false,\"gasp_adopted\":false}"), *GetName());
    TSharedPtr<FJsonObject> Root;
    FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(APhysicsControlDummy::GetDummyState(IncludeContacts)), Root);
    auto GASP = MakeShared<FJsonObject>();
    GASP->SetStringField(TEXT("authority"), StaticEnum<EGASPEnemyAuthority>()->GetNameStringByValue(static_cast<int64>(Authority)));
    GASP->SetNumberField(TEXT("authority_changes"), AuthorityChanges);
    GASP->SetStringField(TEXT("foundation"), IsValid(Foundation) ? Foundation->GetClass()->GetPathName() : TEXT(""));
    GASP->SetStringField(TEXT("mesh"), Body->GetSkeletalMeshAsset()->GetPathName());
    GASP->SetStringField(TEXT("physics_asset"), Body->GetPhysicsAsset()->GetPathName());
    GASP->SetStringField(TEXT("selected_getup"), LastSelectedMontage);
    GASP->SetField(TEXT("movement_command"), Vector98(MovementCommand));
    GASP->SetField(TEXT("movement_intent"), Vector98(GetMovementIntent()));
    GASP->SetField(TEXT("capsule_location"), Vector98(Capsule ? Capsule->GetComponentLocation() : FVector::ZeroVector));
    GASP->SetStringField(TEXT("mover_mode"), Mover ? Mover->GetMovementModeName().ToString() : TEXT(""));
    GASP->SetBoolField(TEXT("walk"), bWalkCommand);
    GASP->SetBoolField(TEXT("left_hand_occupied"), bLeftHandOccupied);
    GASP->SetBoolField(TEXT("right_hand_occupied"), bRightHandOccupied);
    int32 SourceEnabled = 0, SourceUnbounded = 0;
    for (FName Name : SampleControls)
    {
        if (!PhysicsControl->GetControlEnabled(Name)) continue;
        ++SourceEnabled;
        FPhysicsControlData Data;
        if (!PhysicsControl->GetControlData(Name, Data) || Data.MaxForce <= 0 || Data.MaxTorque <= 0) ++SourceUnbounded;
    }
    GASP->SetNumberField(TEXT("enabled_source_controls"), SourceEnabled);
    GASP->SetNumberField(TEXT("source_control_count"), SampleControls.Num());
    GASP->SetBoolField(TEXT("pose_handoff_active"), !HandoffPose.IsEmpty());
    GASP->SetNumberField(TEXT("pose_handoff_seconds"), HandoffSeconds);
    GASP->SetNumberField(TEXT("ragdoll_leg_limit_count"), PreFallLegLimits.Num());
    GASP->SetBoolField(TEXT("source_component_tick_enabled"), PhysicsControl->IsComponentTickEnabled());
    GASP->SetNumberField(TEXT("unbounded_source_controls"), SourceUnbounded);
    GASP->SetField(TEXT("capsule_velocity"), Vector98(Mover ? Mover->GetVelocity() : FVector::ZeroVector));
    GASP->SetField(TEXT("skeletal_pelvis"), Vector98(Body->GetSocketLocation(TEXT("pelvis"))));
    GASP->SetNumberField(TEXT("pelvis_blend_weight"), Body->GetBodyInstance(TEXT("pelvis"))->PhysicsBlendWeight);
    auto SelfContacts = MakeShared<FJsonObject>();
    for (const auto& Pair : ArmTrunkContacts) SelfContacts->SetNumberField(Pair.Key, Pair.Value);
    GASP->SetObjectField(TEXT("arm_trunk_contacts"), SelfContacts);
    GASP->SetNumberField(TEXT("peak_arm_trunk_impulse"), PeakArmTrunkImpulse);
    Root->SetObjectField(TEXT("gasp"), GASP);
    FString Result;
    FJsonSerializer::Serialize(Root.ToSharedRef(), TJsonWriterFactory<>::Create(&Result));
    return Result;
}

void AGASPEnemyFixture::EndPlay(const EEndPlayReason::Type Reason)
{
    if (IsValid(Body)) Body->OnComponentHit.RemoveDynamic(this, &AGASPEnemyFixture::OnBodyContact);
    if (IsValid(Body)) Body->OnComponentHit.RemoveDynamic(this, &AGASPEnemyFixture::OnFoundationContact);
    APhysicsControlDummy::EndPlay(Reason);
    if (IsValid(Foundation)) Foundation->Destroy();
    Foundation = nullptr;
}

bool UGASPEnemyFoundationLibrary::AllowSamplePhysics(AActor* Foundation)
{
    const auto* Enemy = AGASPEnemyFixture::FromFoundation(Foundation);
    return !Enemy || Enemy->AllowsSamplePhysics();
}
bool UGASPEnemyFoundationLibrary::AllowSampleGetUp(AActor* Foundation)
{
    const auto* Enemy = AGASPEnemyFixture::FromFoundation(Foundation);
    return !Enemy || Enemy->Authority == EGASPEnemyAuthority::GettingUp;
}
FVector UGASPEnemyFoundationLibrary::CommandedMovement(AActor* Foundation)
{
    const auto* Enemy = AGASPEnemyFixture::FromFoundation(Foundation);
    return Enemy ? Enemy->GetMovementIntent() : FVector::ZeroVector;
}
bool UGASPEnemyFoundationLibrary::CommandedWalk(AActor* Foundation)
{
    const auto* Enemy = AGASPEnemyFixture::FromFoundation(Foundation);
    return !Enemy || Enemy->bWalkCommand;
}
FTransform UGASPEnemyFoundationLibrary::RagdollAnchor(AActor* Foundation, const FTransform& SampleAnchor)
{
    const auto* Enemy = AGASPEnemyFixture::FromFoundation(Foundation);
    return Enemy ? Enemy->GetRagdollAnchor(SampleAnchor) : SampleAnchor;
}
void UGASPEnemyFoundationLibrary::EnforceSampleLimits(AActor* Foundation)
{
    if (auto* Enemy = AGASPEnemyFixture::FromFoundation(Foundation)) Enemy->EnforceSampleLimits();
}
