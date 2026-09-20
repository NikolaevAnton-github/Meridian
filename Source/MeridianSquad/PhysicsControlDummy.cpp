#include "PhysicsControlDummy.h"
#include "CombatProjectileWorld.h"
#include "PhysicsControlComponent.h"
#include "DummyRecoveryAnimInstance.h"
#include "Animation/AnimSequence.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/SkeletalBodySetup.h"
#include "PhysicsEngine/BodyInstance.h"
#include "PhysicsEngine/PhysicsConstraintTemplate.h"
#include "Physics/PhysicsInterfaceCore.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
TSharedPtr<FJsonValue> VJson(const FVector& V)
{
    return MakeShared<FJsonValueArray>(TArray<TSharedPtr<FJsonValue>>{
        MakeShared<FJsonValueNumber>(V.X), MakeShared<FJsonValueNumber>(V.Y), MakeShared<FJsonValueNumber>(V.Z)});
}
TSharedPtr<FJsonValue> QJson(const FQuat& Q)
{
    return MakeShared<FJsonValueArray>(TArray<TSharedPtr<FJsonValue>>{MakeShared<FJsonValueNumber>(Q.X),
        MakeShared<FJsonValueNumber>(Q.Y), MakeShared<FJsonValueNumber>(Q.Z), MakeShared<FJsonValueNumber>(Q.W)});
}
bool CapsuleHit(const FVector& Start, const FVector& End, double Radius, double HalfHeight, double& Time)
{
    const double H = FMath::Max(0.0, HalfHeight - Radius);
    if (FVector::DistSquared(Start, FVector(0, 0, FMath::Clamp(Start.Z, -H, H))) <= Radius * Radius)
    { Time = 0; return true; }
    const FVector D = End - Start;
    double First = 2;
    auto Roots = [&](double A, double B, double C, auto Accept)
    {
        const double Disc = B * B - 4 * A * C;
        if (A < 1.e-12 || Disc < 0) return;
        const double Root = FMath::Sqrt(Disc);
        for (double T : {(-B - Root) / (2 * A), (-B + Root) / (2 * A)})
            if (T >= 0 && T <= 1 && T < First && Accept(T)) First = T;
    };
    Roots(D.X * D.X + D.Y * D.Y, 2 * (Start.X * D.X + Start.Y * D.Y),
        Start.X * Start.X + Start.Y * Start.Y - Radius * Radius,
        [&](double T) { return FMath::Abs(Start.Z + D.Z * T) <= H; });
    for (double Z : {-H, H})
    {
        const FVector S = Start - FVector(0, 0, Z);
        Roots(D.SizeSquared(), 2 * FVector::DotProduct(S, D), S.SizeSquared() - Radius * Radius, [](double) { return true; });
    }
    Time = First;
    return First <= 1;
}
bool BoxHit(const FVector& Start, const FVector& End, const FVector& Extent, double& Time)
{
    double Lo = 0, Hi = 1;
    for (int32 Axis = 0; Axis < 3; ++Axis)
    {
        const double D = End[Axis] - Start[Axis];
        if (FMath::Abs(D) < 1.e-12) { if (FMath::Abs(Start[Axis]) > Extent[Axis]) return false; }
        else
        {
            double A = (-Extent[Axis] - Start[Axis]) / D, B = (Extent[Axis] - Start[Axis]) / D;
            if (A > B) Swap(A, B);
            Lo = FMath::Max(Lo, A); Hi = FMath::Min(Hi, B);
            if (Lo > Hi) return false;
        }
    }
    Time = Lo;
    return true;
}
}

APhysicsControlDummy::APhysicsControlDummy()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickGroup = TG_PrePhysics;
    FixtureRoot = CreateDefaultSubobject<USceneComponent>(TEXT("FixtureOrigin"));
    SetRootComponent(FixtureRoot);
    Body = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("PoweredManny"));
    Body->SetupAttachment(FixtureRoot);
    Body->SetRelativeRotation(FRotator(0, -90, 0));
    static ConstructorHelpers::FObjectFinder<USkeletalMesh> Mesh(TEXT("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple"));
    Body->SetSkeletalMesh(Mesh.Object);
    Body->SetForcedLOD(1);
    Body->SetPhysicsAsset(LoadObject<UPhysicsAsset>(nullptr, TEXT("/Game/Development/PhysicsControlRecovery01/PA_Manny_Recovery01.PA_Manny_Recovery01")));
    Body->SetAnimationMode(EAnimationMode::AnimationSingleNode);
    Body->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    Body->SetCollisionObjectType(ECC_PhysicsBody);
    Body->SetCollisionResponseToAllChannels(ECR_Ignore);
    Body->SetCollisionResponseToChannel(ECC_WorldStatic, ECR_Block);
    Body->SetCollisionResponseToChannel(ECC_PhysicsBody, ECR_Block);
    Body->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    static ConstructorHelpers::FObjectFinder<UAnimSequence> Pose(TEXT("/Game/Development/EnemyPrototype01/A_EnemyTemplate_Idle.A_EnemyTemplate_Idle"));
    Idle = Pose.Object;
    static ConstructorHelpers::FObjectFinder<UAnimSequence> Back(TEXT("/Game/Development/PhysicsControlBalance01/A_GetUp_Back.A_GetUp_Back"));
    static ConstructorHelpers::FObjectFinder<UAnimSequence> Stomach(TEXT("/Game/Development/PhysicsControlBalance01/A_GetUp_Stomach.A_GetUp_Stomach"));
    GetUpBack = Back.Object; GetUpStomach = Stomach.Object;
    PoseSource = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("RecoveryPoseSource"));
    PoseSource->SetupAttachment(FixtureRoot);
    PoseSource->SetSkeletalMesh(Mesh.Object);
    PoseSource->SetForcedLOD(1);
    PoseSource->SetAnimInstanceClass(UDummyRecoveryAnimInstance::StaticClass());
    PoseSource->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PoseSource->SetVisibility(false);
    PoseSource->SetCastShadow(false);
    PoseSource->SetComponentTickEnabled(false);
    PoseSource->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    PhysicsControl = CreateDefaultSubobject<UPhysicsControlComponent>(TEXT("LivingDrives"));
    PhysicsControl->SetupAttachment(FixtureRoot);
    PhysicsControl->AddTickPrerequisiteActor(this);
    Label = CreateDefaultSubobject<UTextRenderComponent>(TEXT("ExperimentalIdentity"));
    Label->SetupAttachment(FixtureRoot);
    Label->SetRelativeLocation(FVector(0, 0, 213));
    Label->SetWorldSize(14);
    // Screen-projected fixture labels in CombatPrototypeHUD stay legible in the dark lobby.
    Label->SetVisibility(false);
    Label->SetHorizontalAlignment(EHTA_Center);
    Label->SetTextRenderColor(FColor(110, 220, 255));
    Label->SetCastShadow(false);
}
void APhysicsControlDummy::BeginPlay()
{
    Super::BeginPlay();
    Home = GetActorTransform();
    ResetDummy();
}
void APhysicsControlDummy::ConfigureReactionProfile(int32 Number)
{
    ReactionProfile = FMath::Clamp(Number, 1, 6);
    struct FProfile { float Impulse, Velocity, Strength, Hold, Recovery; };
    static constexpr FProfile Profiles[] = {
        {1800, 260, .03f, .14f, .55f}, {2300, 300, .015f, .22f, .65f},
        {2800, 340, .009f, .30f, .75f}, {3400, 370, .008f, .36f, .85f},
        {4100, 410, .006f, .44f, 1.0f}, {4800, 450, .005f, .60f, 1.2f}};
    const auto& P = Profiles[ReactionProfile - 1];
    BulletImpulse = P.Impulse; MaxImpulseVelocity = P.Velocity;
    HitStrengthMultiplier = P.Strength; HitHoldSeconds = P.Hold; HitRecoverySeconds = P.Recovery;
}
void APhysicsControlDummy::ResetDummy()
{
    ClearBalanceProbeFixtures();
    bReady = false;
    if (auto* ScopedAsset = LoadObject<UPhysicsAsset>(nullptr, TEXT("/Game/Development/PhysicsControlRecovery01/PA_Manny_Recovery01.PA_Manny_Recovery01")))
        if (Body->GetPhysicsAsset() != ScopedAsset) Body->SetPhysicsAsset(ScopedAsset);
    if (!Controls.IsEmpty()) PhysicsControl->DestroyControls(Controls);
    Controls.Reset();
    BodyControls.Reset(); RecoveringControls.Reset();
    WidenedJoints = 0;
    if (const auto* Asset = Body->GetPhysicsAsset())
        for (int32 I = 0; I < Asset->ConstraintSetup.Num(); ++I)
            if (auto* Joint = Body->GetConstraintInstanceByIndex(I))
                Joint->RestoreAngularLimitsToDefault(Asset->ConstraintSetup[I]->DefaultInstance);
    Body->SetAllPhysicsLinearVelocity(FVector::ZeroVector);
    Body->SetAllPhysicsAngularVelocityInRadians(FVector::ZeroVector);
    Body->SetSimulatePhysics(false);
    Body->SetAllBodiesSimulatePhysics(false);
    Body->AttachToComponent(FixtureRoot, FAttachmentTransformRules::KeepRelativeTransform);
    SetActorTransform(Home, false, nullptr, ETeleportType::TeleportPhysics);
    Body->SetRelativeLocationAndRotation(FVector::ZeroVector, FRotator(0, -90, 0));
    Body->bPauseAnims = false;
    Body->PlayAnimation(Idle, true);
    Body->TickAnimation(0, false);
    Body->RefreshBoneTransforms();
    if (SolePoints.IsEmpty()) CalibrateSoles();
    FHitResult Floor;
    if (FindFloor(Home.GetLocation() + FVector(0,0,50), 150, Floor))
    {
        const float Bottom = FMath::Min(SoleBottom(Body, true), SoleBottom(Body, false));
        Body->AddWorldOffset(FVector(0,0,Floor.ImpactPoint.Z + .15f - Bottom), false, nullptr, ETeleportType::TeleportPhysics);
        Body->RefreshBoneTransforms();
    }
    ReferencePose.Reset();
    if (const auto* Asset = Body->GetPhysicsAsset())
        for (const USkeletalBodySetup* Setup : Asset->SkeletalBodySetups)
            ReferencePose.Add(Setup->BoneName, Body->GetSocketTransform(Setup->BoneName));
    SupportTarget = Body->GetSocketTransform(TEXT("pelvis"));
    StandingPose = ReferencePose;
    FPoseSnapshot StandingSnapshot;
    Body->SnapshotPose(StandingSnapshot);
    Body->SetAnimInstanceClass(UDummyRecoveryAnimInstance::StaticClass());
    auto* VisibleAnim = CastChecked<UDummyRecoveryAnimInstance>(Body->GetAnimInstance());
    VisibleAnim->bSnapshotOnly = true;
    VisibleAnim->StartPose = StandingSnapshot;
    VisibleAnim->Sequence = Idle;
    Body->TickAnimation(0, false);
    Body->RefreshBoneTransforms();
    Body->bPauseAnims = true;
    Body->SetAllBodiesSimulatePhysics(true);
    Body->SetAllBodiesPhysicsBlendWeight(1);
    IsolateSelfCollision();
    Body->bBlendPhysics = true;
    Body->SetAllPhysicsLinearVelocity(FVector::ZeroVector);
    Body->SetAllPhysicsAngularVelocityInRadians(FVector::ZeroVector);
    Health = FMath::IsFinite(MaxHealth) ? FMath::Clamp(MaxHealth, 1.f, 100000.f) : 100.f;
    Deaths = PhysicalHits = 0;
    DeathFrame = 0; DeathTime = -1;
    Contacts.Reset();
    ++PoseEpoch;
    UnsupportedShapes = 0;
    if (const auto* Asset = Body->GetPhysicsAsset())
        for (const USkeletalBodySetup* Setup : Asset->SkeletalBodySetups)
            UnsupportedShapes += Setup->AggGeom.ConvexElems.Num() + Setup->AggGeom.TaperedCapsuleElems.Num();

    FPhysicsControlData Limbs;
    Limbs.LinearStrength = FMath::Clamp(PoseLinearStrength, .1f, 15.f);
    Limbs.LinearDampingRatio = FMath::Clamp(DriveDampingRatio, .5f, 3.f);
    Limbs.AngularStrength = FMath::Clamp(LimbAngularStrength, .1f, 30.f);
    Limbs.AngularDampingRatio = FMath::Clamp(DriveDampingRatio, .5f, 3.f);
    Limbs.bUseSkeletalAnimation = false;
    Limbs.bDisableCollision = false;
    // Distributed assistance remains explicit. UpdateBalance gates EVERY drive by
    // actual support/state; falling/down/dead bodies have no enabled world springs.
    const auto* Asset = Body->GetPhysicsAsset();
    for (const auto& Entry : ReferencePose)
    {
        FName Parent = Body->GetParentBone(Entry.Key);
        while (!Parent.IsNone() && Asset->FindBodyIndex(Parent) == INDEX_NONE) Parent = Body->GetParentBone(Parent);
        const FTransform* ParentPose = ReferencePose.Find(Parent);
        if (!ParentPose) continue;
        const FTransform Relative = Entry.Value.GetRelativeTransform(*ParentPose);
        // The template's ragdoll limits can exclude the selected rifle idle pose.
        // Widen only this instance, using Epic's drive-target-aware operation.
        // Keep these limits through death so release introduces no joint-limit snap.
        const int32 JointIndex = Asset->FindConstraintIndex(Entry.Key, Parent);
        if (auto* Joint = Body->GetConstraintInstanceByIndex(JointIndex))
            if (Joint->WidenLimitsForDriveTarget(Relative.GetRotation(), Asset->ConstraintSetup[JointIndex]->DefaultInstance)) ++WidenedJoints;
        FPhysicsControlTarget LimbTarget;
        LimbTarget.TargetPosition = Entry.Value.GetLocation();
        LimbTarget.TargetOrientation = Entry.Value.Rotator();
        LimbTarget.bApplyControlPointToTarget = true;
        FPhysicsControlData Data = Limbs;
        const FString BoneName = Entry.Key.ToString();
        if (BoneName.StartsWith(TEXT("spine")) || BoneName.StartsWith(TEXT("neck")) || BoneName == TEXT("head") || BoneName.StartsWith(TEXT("clavicle")))
            Data.AngularStrength = FMath::Clamp(TrunkAngularStrength, .1f, 30.f);
        const FName Name = PhysicsControl->CreateControl(nullptr, NAME_None, Body, Entry.Key, Data, LimbTarget, TEXT("Living"), TEXT("Pose_"));
        if (!Name.IsNone()) { Controls.Add(Name); BodyControls.Add(Entry.Key, Name); }
    }
    FPhysicsControlData Support;
    Support.LinearStrength = Support.AngularStrength = FMath::Clamp(SupportStrength, 1.f, 30.f);
    Support.LinearDampingRatio = Support.AngularDampingRatio = Limbs.AngularDampingRatio;
    Support.bUseSkeletalAnimation = false;
    FPhysicsControlTarget Target;
    Target.TargetPosition = SupportTarget.GetLocation();
    Target.TargetOrientation = SupportTarget.Rotator();
    Target.bApplyControlPointToTarget = true;
    const FName SupportName = PhysicsControl->CreateControl(nullptr, NAME_None, Body, TEXT("pelvis"), Support, Target,
        TEXT("Support"), TEXT("Fixture_"));
    if (!SupportName.IsNone()) Controls.Add(SupportName);
    PelvisControl = SupportName;
    PhysicsControl->SetComponentTickEnabled(true);
    PhysicsControl->UpdateTargetCaches(0);
    PhysicsControl->UpdateControls(0);
    Body->WakeAllRigidBodies();
    bReady = Controls.Num() > 1 && !SupportName.IsNone() && UnsupportedShapes == 0;
    ResetBalance();
    UpdateLabel();
}
void APhysicsControlDummy::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    for (auto It = RecoveringControls.CreateIterator(); It; ++It)
    {
        It.Value() = FMath::Max(0.f, It.Value() - DeltaSeconds);
        const float Alpha = FMath::Clamp(1.f - It.Value() / FMath::Clamp(HitRecoverySeconds, .1f, 1.5f), 0.f, 1.f);
        FPhysicsControlMultiplier Multiplier;
        const float Strength = FMath::Lerp(FMath::Clamp(HitStrengthMultiplier, .005f, 1.f), 1.f, Alpha);
        Multiplier.LinearStrengthMultiplier = FVector(Strength);
        Multiplier.AngularStrengthMultiplier = Strength;
        PhysicsControl->SetControlMultiplier(It.Key(), Multiplier);
        if (It.Value() == 0) It.RemoveCurrent();
    }
    UpdateBalance(DeltaSeconds);
    // Chaos inactivity decides sleep; recovery only starts after measured settling.
    UpdateLabel();
}
void APhysicsControlDummy::UpdateLabel()
{
    Label->SetText(FText::FromString(FString::Printf(TEXT("%d  |  %.0f HP\n%s"), ReactionProfile, Health,
        !bReady ? TEXT("SETUP FAILED") : IsDead() ? TEXT("CORPSE") : TEXT("PHYSICS CONTROL"))));
}
FVector APhysicsControlDummy::GetPhysicalBodyLocation(FName Bone) const
{
    if (const auto* BI = Body->GetBodyInstance(Bone)) return BI->GetCOMPosition();
    return Body->GetComponentLocation();
}
FDummyPose APhysicsControlDummy::SamplePhysicalPose() const
{
    FDummyPose Pose;
    Pose.Epoch = PoseEpoch;
    if (!bReady || IsActorBeingDestroyed()) return Pose;
    const auto* Asset = Body->GetPhysicsAsset();
    if (!Asset) return Pose;
    for (const USkeletalBodySetup* Setup : Asset->SkeletalBodySetups)
    {
        const auto* BI = Body->GetBodyInstance(Setup->BoneName);
        if (!BI || !BI->IsValidBodyInstance()) continue;
        const FTransform World = BI->GetUnrealWorldTransform();
        for (const auto& Shape : Setup->AggGeom.SphylElems)
            Pose.Shapes.Add({Setup->BoneName, Shape.GetTransform() * World, FVector::ZeroVector,
                Shape.Radius, Shape.Length * .5f + Shape.Radius, false});
        for (const auto& Shape : Setup->AggGeom.SphereElems)
            Pose.Shapes.Add({Setup->BoneName, Shape.GetTransform() * World, FVector::ZeroVector, Shape.Radius, Shape.Radius, false});
        for (const auto& Shape : Setup->AggGeom.BoxElems)
            Pose.Shapes.Add({Setup->BoneName, Shape.GetTransform() * World, FVector(Shape.X, Shape.Y, Shape.Z) * .5, 0, 0, true});
    }
    return Pose;
}
bool APhysicsControlDummy::TracePhysicalPose(const FDummyPose& Before, const FDummyPose& After,
    const FVector& Start, const FVector& End, float Radius, FHitResult& Hit) const
{
    double First = 2;
    for (int32 Index = 0; Index < After.Shapes.Num(); ++Index)
    {
        const auto& Shape = After.Shapes[Index];
        const FTransform& Old = Before.Epoch == After.Epoch && Before.Shapes.IsValidIndex(Index) ? Before.Shapes[Index].Transform : Shape.Transform;
        const FVector A = Old.InverseTransformPosition(Start), B = Shape.Transform.InverseTransformPosition(End);
        double T;
        // Translation is continuous. Rotation uses each interval endpoint's local frame;
        // this chord approximation is bounded by the coordinator's 10 ms segments.
        const bool Found = Shape.bBox ? BoxHit(A, B, Shape.Extent + FVector(Radius), T) :
            CapsuleHit(A, B, Shape.Radius + Radius, Shape.HalfHeight + Radius, T);
        if (!Found || T >= First) continue;
        First = T;
        const FVector Center = FMath::Lerp(Start, End, T);
        const FQuat Rotation = FQuat::Slerp(Old.GetRotation(), Shape.Transform.GetRotation(), T);
        const FVector Local = FMath::Lerp(A, B, T);
        FVector Normal;
        if (Shape.bBox)
        {
            const FVector D = Local.GetAbs() - Shape.Extent;
            const int32 Axis = D.X > D.Y ? (D.X > D.Z ? 0 : 2) : (D.Y > D.Z ? 1 : 2);
            Normal = FVector::ZeroVector; Normal[Axis] = FMath::Sign(Local[Axis]);
        }
        else Normal = (Local - FVector(0, 0, FMath::Clamp(Local.Z, -double(Shape.HalfHeight - Shape.Radius), double(Shape.HalfHeight - Shape.Radius)))).GetSafeNormal();
        Normal = Rotation.RotateVector(Normal).GetSafeNormal(UE_DOUBLE_SMALL_NUMBER, (Start - End).GetSafeNormal());
        const FVector Contact = Center - Normal * Radius;
        Hit = FHitResult(const_cast<APhysicsControlDummy*>(this), Body, Contact, Normal);
        Hit.Location = Center; Hit.ImpactPoint = Contact; Hit.Time = T;
        Hit.Distance = FVector::Distance(Start, Center);
        Hit.BoneName = Shape.Bone; Hit.bBlockingHit = true;
    }
    return First <= 1;
}
TSharedPtr<FJsonObject> APhysicsControlDummy::BodyState() const
{
    auto Result = MakeShared<FJsonObject>();
    const auto* Asset = Body->GetPhysicsAsset();
    if (!Asset) return Result;
    for (const USkeletalBodySetup* Setup : Asset->SkeletalBodySetups)
        if (const auto* BI = Body->GetBodyInstance(Setup->BoneName))
        {
            auto Row = MakeShared<FJsonObject>();
            const FTransform T = BI->GetUnrealWorldTransform();
            Row->SetField(TEXT("position"), VJson(T.GetLocation()));
            Row->SetField(TEXT("center_of_mass"), VJson(BI->GetCOMPosition()));
            Row->SetField(TEXT("rotation"), QJson(T.GetRotation()));
            if (!IsDead())
            {
                const FTransform Target = ReferencePose.FindRef(Setup->BoneName);
                Row->SetField(TEXT("target_position"), VJson(Target.GetLocation()));
                Row->SetField(TEXT("target_rotation"), QJson(Target.GetRotation()));
            }
            Row->SetField(TEXT("linear_velocity"), VJson(BI->GetUnrealWorldVelocity()));
            Row->SetField(TEXT("angular_velocity"), VJson(BI->GetUnrealWorldAngularVelocityInRadians()));
            Row->SetNumberField(TEXT("mass"), BI->GetBodyMass());
            Row->SetBoolField(TEXT("awake"), BI->IsInstanceAwake());
            Row->SetBoolField(TEXT("simulating"), BI->IsInstanceSimulatingPhysics());
            Result->SetObjectField(Setup->BoneName.ToString(), Row);
        }
    return Result;
}
float APhysicsControlDummy::ReceiveBullet(int64 ShotId, float Damage, const FVector& Direction, const FHitResult& Hit,
    double ContactTime, double BirthTime, uint64 CombatFrame)
{
    auto* BI = Body->GetBodyInstance(Hit.BoneName);
    if (!bReady || !BI || !FMath::IsFinite(Damage) || Damage <= 0 || Direction.ContainsNaN()) return 0;
    auto Row = MakeShared<FJsonObject>();
    Row->SetNumberField(TEXT("shot"), ShotId);
    Row->SetNumberField(TEXT("birth_time"), BirthTime);
    Row->SetNumberField(TEXT("contact_time"), ContactTime);
    Row->SetNumberField(TEXT("combat_frame"), CombatFrame);
    Row->SetStringField(TEXT("bone"), Hit.BoneName.ToString());
    Row->SetField(TEXT("contact"), VJson(Hit.ImpactPoint));
    Row->SetField(TEXT("direction"), VJson(Direction));
    Row->SetBoolField(TEXT("was_dead"), IsDead());
    Row->SetObjectField(TEXT("before"), BodyState());
    const auto* CombatWorld = ACombatProjectileWorld::Find(GetWorld());
    // Suppress health loss only; physical impacts and balance disturbances still run.
    const bool bImmortal = CombatWorld && CombatWorld->bImmortalDummies;
    const float Applied = IsDead() || bImmortal ? 0.f : FMath::Min(Health, Damage);
    Health = FMath::Max(0.f, Health - Applied);
    if (!IsDead() && Health == 0)
    {
        ++Deaths;
        BalanceState = EDummyBalanceState::Dead;
        BalanceReason = TEXT("health depleted");
        ActiveGetUp = nullptr;
        DeathFrame = CombatFrame; DeathTime = ContactTime;
        // Remove the motors only. Existing bodies, pose and momentum survive untouched.
        if (!Controls.IsEmpty()) PhysicsControl->DestroyControls(Controls);
        Controls.Reset();
        BodyControls.Reset(); RecoveringControls.Reset();
        PhysicsControl->SetComponentTickEnabled(false);
        Body->bPauseAnims = true;
    }
    else if (!IsDead() && (BalanceState == EDummyBalanceState::Standing || BalanceState == EDummyBalanceState::LosingBalance))
    {
        // Briefly soften the struck region's pose springs. Physical joints and the
        // pelvis support stay active; recovery uses world time, including the preview.
        const FString Bone = Hit.BoneName.ToString();
        for (const auto& Entry : BodyControls)
        {
            const FString Part = Entry.Key.ToString();
            const bool SameSide = (Bone.EndsWith(TEXT("_l")) && Part.EndsWith(TEXT("_l"))) ||
                (Bone.EndsWith(TEXT("_r")) && Part.EndsWith(TEXT("_r")));
            const bool Arm = Bone.Contains(TEXT("arm")) || Bone.StartsWith(TEXT("hand"));
            const bool Leg = Bone.StartsWith(TEXT("thigh")) || Bone.StartsWith(TEXT("calf")) || Bone.StartsWith(TEXT("foot"));
            const bool UpperBody = Part.StartsWith(TEXT("spine")) || Part.StartsWith(TEXT("neck")) || Part == TEXT("head") ||
                Part.StartsWith(TEXT("clavicle")) || Part.Contains(TEXT("arm")) || Part.StartsWith(TEXT("hand"));
            const bool Region = Entry.Key == Hit.BoneName || (SameSide && Arm && (Part.Contains(TEXT("arm")) || Part.StartsWith(TEXT("hand")) ||
                (ReactionProfile > 0 && Part.StartsWith(TEXT("clavicle"))))) ||
                (SameSide && Leg && (Part.StartsWith(TEXT("thigh")) || Part.StartsWith(TEXT("calf")) || Part.StartsWith(TEXT("foot")))) ||
                ((!Arm && !Leg) && (ReactionProfile > 0 ? UpperBody :
                    (Part.StartsWith(TEXT("spine")) || Part.StartsWith(TEXT("neck")) || Part == TEXT("head"))));
            if (Region)
            {
                RecoveringControls.Add(Entry.Value, FMath::Clamp(HitRecoverySeconds, .1f, 1.5f) + FMath::Clamp(HitHoldSeconds, 0.f, .6f));
                FPhysicsControlMultiplier Multiplier;
                Multiplier.LinearStrengthMultiplier = FVector(FMath::Clamp(HitStrengthMultiplier, .005f, 1.f));
                Multiplier.AngularStrengthMultiplier = Multiplier.LinearStrengthMultiplier.X;
                PhysicsControl->SetControlMultiplier(Entry.Value, Multiplier);
            }
        }
    }
    Row->SetObjectField(TEXT("after_release"), BodyState());
    const float Magnitude = FMath::Min(FMath::Clamp(BulletImpulse, 0.f, 5000.f),
        BI->GetBodyMass() * FMath::Clamp(MaxImpulseVelocity, 0.f, 450.f));
    const FVector Impulse = Direction.GetSafeNormal() * Magnitude;
    if (!IsDead()) RegisterDisturbance(Hit.BoneName, Impulse, InstabilityPerHit);
    Body->WakeAllRigidBodies();
    Body->AddImpulseAtLocation(Impulse, Hit.ImpactPoint, Hit.BoneName);
    ++PhysicalHits;
    Row->SetField(TEXT("impulse"), VJson(Impulse));
    Row->SetNumberField(TEXT("impulse_count"), 1);
    Row->SetNumberField(TEXT("health"), Health);
    Row->SetNumberField(TEXT("deaths"), Deaths);
    Row->SetNumberField(TEXT("controls"), Controls.Num());
    Row->SetObjectField(TEXT("after_impulse"), BodyState());
    if (Contacts.Num() == 32) Contacts.RemoveAt(0);
    Contacts.Add(MakeShared<FJsonValueObject>(Row));
    UpdateLabel();
    return Applied;
}
FString APhysicsControlDummy::GetDummyState(bool IncludeContacts) const
{
    auto Root = MakeShared<FJsonObject>();
    Root->SetStringField(TEXT("name"), GetName());
    AddBalanceState(Root);
    Root->SetNumberField(TEXT("profile"), ReactionProfile);
    Root->SetNumberField(TEXT("impulse_cap"), FMath::Clamp(BulletImpulse, 0.f, 5000.f));
    Root->SetNumberField(TEXT("velocity_cap"), FMath::Clamp(MaxImpulseVelocity, 0.f, 450.f));
    Root->SetNumberField(TEXT("hit_strength"), FMath::Clamp(HitStrengthMultiplier, .005f, 1.f));
    Root->SetNumberField(TEXT("hit_hold"), FMath::Clamp(HitHoldSeconds, 0.f, .6f));
    Root->SetNumberField(TEXT("hit_recovery"), FMath::Clamp(HitRecoverySeconds, .1f, 1.5f));
    double JointGap = 0, RawChaosGap = 0, LockedJointGap = 0;
    int32 LockedJointCount = 0;
    TArray<TSharedPtr<FJsonValue>> JointRows;
    if (const auto* Asset = Body->GetPhysicsAsset())
        for (int32 I = 0; I < Asset->ConstraintSetup.Num(); ++I)
            if (const auto* Joint = Body->GetConstraintInstanceByIndex(I))
            {
                const auto& Constraint = Joint->GetPhysicsConstraintRef();
                if (Constraint.IsValid())
                    RawChaosGap = FMath::Max(RawChaosGap, FVector::Distance(
                        FPhysicsInterface::GetGlobalPose(Constraint, EConstraintFrame::Frame1).GetLocation(),
                        FPhysicsInterface::GetGlobalPose(Constraint, EConstraintFrame::Frame2).GetLocation()));
                // Retain both anchor calculations for diagnosis; neither changes physics.
                const auto* Child = Body->GetBodyInstance(Joint->ConstraintBone1);
                const auto* Parent = Body->GetBodyInstance(Joint->ConstraintBone2);
                if (Child && Parent)
                {
                    const double Gap = FVector::Distance(
                        (Joint->GetRefFrame(EConstraintFrame::Frame1) * Child->GetUnrealWorldTransform()).GetLocation(),
                        (Joint->GetRefFrame(EConstraintFrame::Frame2) * Parent->GetUnrealWorldTransform()).GetLocation());
                    JointGap = FMath::Max(JointGap, Gap);
                    // The source asset also has two free calf-to-pelvis constraints.
                    // Their separated anchors are not a violation of a positional lock.
                    if (Joint->GetLinearXMotion() == LCM_Locked && Joint->GetLinearYMotion() == LCM_Locked &&
                        Joint->GetLinearZMotion() == LCM_Locked)
                    {
                        LockedJointGap = FMath::Max(LockedJointGap, Gap);
                        ++LockedJointCount;
                    }
                    if (IncludeContacts)
                    {
                        auto Row = MakeShared<FJsonObject>();
                        Row->SetStringField(TEXT("child"),Joint->ConstraintBone1.ToString());
                        Row->SetStringField(TEXT("parent"),Joint->ConstraintBone2.ToString());
                        Row->SetNumberField(TEXT("gap"),Gap);
                        Row->SetBoolField(TEXT("valid"),Constraint.IsValid());
                        Row->SetNumberField(TEXT("linear_x"),static_cast<int32>(Joint->GetLinearXMotion()));
                        Row->SetNumberField(TEXT("linear_y"),static_cast<int32>(Joint->GetLinearYMotion()));
                        Row->SetNumberField(TEXT("linear_z"),static_cast<int32>(Joint->GetLinearZMotion()));
                        Row->SetField(TEXT("local_anchor1"),VJson(Joint->GetRefFrame(EConstraintFrame::Frame1).GetLocation()));
                        Row->SetField(TEXT("local_anchor2"),VJson(Joint->GetRefFrame(EConstraintFrame::Frame2).GetLocation()));
                        JointRows.Add(MakeShared<FJsonValueObject>(Row));
                    }
                }
            }
    Root->SetNumberField(TEXT("max_joint_anchor_gap_cm"), JointGap);
    Root->SetNumberField(TEXT("raw_chaos_joint_pose_gap_cm"), RawChaosGap);
    Root->SetNumberField(TEXT("max_locked_joint_anchor_gap_cm"), LockedJointGap);
    Root->SetNumberField(TEXT("locked_joint_count"), LockedJointCount);
    if (IncludeContacts) Root->SetArrayField(TEXT("joints"),JointRows);
    Root->SetBoolField(TEXT("ready"), bReady);
    Root->SetNumberField(TEXT("health"), Health);
    Root->SetNumberField(TEXT("deaths"), Deaths);
    Root->SetNumberField(TEXT("physical_hits"), PhysicalHits);
    Root->SetNumberField(TEXT("epoch"), PoseEpoch);
    Root->SetNumberField(TEXT("unsupported_shapes"), UnsupportedShapes);
    Root->SetNumberField(TEXT("widened_instance_joints"), WidenedJoints);
    Root->SetNumberField(TEXT("recovering_controls"), RecoveringControls.Num());
    Root->SetNumberField(TEXT("shape_count"), SamplePhysicalPose().Shapes.Num());
    Root->SetNumberField(TEXT("death_time"), DeathTime);
    Root->SetNumberField(TEXT("death_frame"), DeathFrame);
    Root->SetField(TEXT("home"), VJson(Home.GetLocation()));
    Root->SetField(TEXT("support_target"), VJson(SupportTarget.GetLocation()));
    Root->SetObjectField(TEXT("bodies"), BodyState());
    TArray<TSharedPtr<FJsonValue>> DriveRows;
    for (FName Name : Controls)
    {
        auto Row = MakeShared<FJsonObject>();
        FPhysicsControlData Data;
        PhysicsControl->GetControlData(Name, Data);
        Row->SetStringField(TEXT("name"), Name.ToString());
        Row->SetBoolField(TEXT("enabled"), PhysicsControl->GetControlEnabled(Name));
        Row->SetBoolField(TEXT("animation_target"), Data.bUseSkeletalAnimation);
        Row->SetNumberField(TEXT("linear_strength"), Data.LinearStrength);
        Row->SetNumberField(TEXT("angular_strength"), Data.AngularStrength);
        Row->SetNumberField(TEXT("damping_ratio"), Data.AngularDampingRatio);
        FPhysicsControlMultiplier Multiplier;
        PhysicsControl->GetControlMultiplier(Name, Multiplier);
        Row->SetNumberField(TEXT("strength_multiplier"), Multiplier.AngularStrengthMultiplier);
        DriveRows.Add(MakeShared<FJsonValueObject>(Row));
    }
    Root->SetArrayField(TEXT("controls"), DriveRows);
    if (IncludeContacts) Root->SetArrayField(TEXT("contacts"), Contacts);
    FString Result;
    FJsonSerializer::Serialize(Root, TJsonWriterFactory<>::Create(&Result));
    return Result;
}
void APhysicsControlDummy::EndPlay(const EEndPlayReason::Type Reason)
{
    ClearBalanceProbeFixtures();
    if (!Controls.IsEmpty()) PhysicsControl->DestroyControls(Controls);
    Controls.Reset(); Contacts.Reset(); bReady = false;
    Super::EndPlay(Reason);
}
