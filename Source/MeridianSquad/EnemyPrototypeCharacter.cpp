#include "EnemyPrototypeCharacter.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/DamageEvents.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
TSharedPtr<FJsonValue> VectorJson(const FVector& V)
{
    return MakeShared<FJsonValueArray>(TArray<TSharedPtr<FJsonValue>>{MakeShared<FJsonValueNumber>(V.X),
        MakeShared<FJsonValueNumber>(V.Y), MakeShared<FJsonValueNumber>(V.Z)});
}
}

AEnemyPrototypeCharacter::AEnemyPrototypeCharacter()
{
    PrimaryActorTick.bCanEverTick = true;
    AutoPossessAI = EAutoPossessAI::Disabled;
    AIControllerClass = nullptr;
    GetCapsuleComponent()->InitCapsuleSize(34.f, 92.f);
    GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility, ECR_Ignore);
    GetCharacterMovement()->bRunPhysicsWithNoController = true;
    GetCharacterMovement()->MaxWalkSpeed = 95.f;
    GetCharacterMovement()->bOrientRotationToMovement = false;
    GetCharacterMovement()->bUseControllerDesiredRotation = false;
    bUseControllerRotationYaw = false;
    auto* Body = GetMesh();
    static ConstructorHelpers::FObjectFinder<USkeletalMesh> BodyAsset(TEXT("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple"));
    Body->SetSkeletalMesh(BodyAsset.Object);
    Body->SetRelativeLocation(FVector(0, 0, -92));
    Body->SetRelativeRotation(FRotator(0, -90, 0));
    Body->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Body->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    Body->SetAnimationMode(EAnimationMode::AnimationSingleNode);
    static ConstructorHelpers::FObjectFinder<UAnimSequence> Idle(TEXT("/Game/Development/EnemyPrototype01/A_EnemyTemplate_Idle.A_EnemyTemplate_Idle"));
    static ConstructorHelpers::FObjectFinder<UAnimSequence> Left(TEXT("/Game/Development/EnemyPrototype01/A_Enemy_Left.A_Enemy_Left"));
    static ConstructorHelpers::FObjectFinder<UAnimSequence> Right(TEXT("/Game/Development/EnemyPrototype01/A_Enemy_Right.A_Enemy_Right"));
    static ConstructorHelpers::FObjectFinder<UAnimSequence> Hit(TEXT("/Game/Development/EnemyPrototype01/A_EnemyTemplate_Hit.A_EnemyTemplate_Hit"));
    static ConstructorHelpers::FObjectFinder<UAnimSequence> Fire(TEXT("/Game/Development/EnemyPrototype01/A_EnemyTemplate_Fire.A_EnemyTemplate_Fire"));
    IdleAnimation = Idle.Object; LeftAnimation = Left.Object; RightAnimation = Right.Object;
    HitAnimation = Hit.Object; FireAnimation = Fire.Object;
    PreviewRifle = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("PreviewRifle"));
    PreviewRifle->SetupAttachment(Body, TEXT("hand_r"));
    static ConstructorHelpers::FObjectFinder<USkeletalMesh> Rifle(TEXT("/Game/InfimaGames/TacticalFPSAnimations/Weapons/AssaultRifle/Meshes/SK_TFA_AR.SK_TFA_AR"));
    PreviewRifle->SetSkeletalMesh(Rifle.Object);
    PreviewRifle->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Label = CreateDefaultSubobject<UTextRenderComponent>(TEXT("PrototypeStatus"));
    Label->SetupAttachment(GetCapsuleComponent());
    Label->SetRelativeLocation(FVector(0, 0, 123));
    Label->SetHorizontalAlignment(EHTA_Center);
    Label->SetWorldSize(12);
    Label->SetCastShadow(false);
}
void AEnemyPrototypeCharacter::BeginPlay()
{
    Super::BeginPlay();
    Home = GetActorTransform();
    ResetEnemy();
}
void AEnemyPrototypeCharacter::Play(UAnimSequence* Animation, bool Loop)
{
    if (Animation && CurrentAnimation != Animation)
    {
        CurrentAnimation = Animation;
        GetMesh()->PlayAnimation(Animation, Loop);
    }
}
void AEnemyPrototypeCharacter::SetPreviewMoving(bool Moving)
{
    bPreviewMoving = Moving;
    if (!Moving) GetCharacterMovement()->StopMovementImmediately();
}
void AEnemyPrototypeCharacter::PreviewFire()
{
    if (bDead || ResponseRemaining > 0 || !FireAnimation) return;
    CurrentAnimation = nullptr;
    Play(FireAnimation, false);
    ResponseRemaining = FireAnimation->GetPlayLength();
}
void AEnemyPrototypeCharacter::ResetEnemy()
{
    auto* Body = GetMesh();
    Body->SetAllPhysicsLinearVelocity(FVector::ZeroVector);
    Body->SetAllPhysicsAngularVelocityInDegrees(FVector::ZeroVector);
    Body->SetSimulatePhysics(false);
    Body->SetAllBodiesSimulatePhysics(false);
    Body->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Body->AttachToComponent(GetCapsuleComponent(), FAttachmentTransformRules::KeepRelativeTransform);
    Body->SetRelativeLocationAndRotation(FVector(0, 0, -92), FRotator(0, -90, 0));
    SetActorTransform(Home, false, nullptr, ETeleportType::TeleportPhysics);
    GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    GetCharacterMovement()->StopMovementImmediately();
    GetCharacterMovement()->SetMovementMode(MOVE_Walking);
    Health = FMath::IsFinite(MaxHealth) ? FMath::Clamp(MaxHealth, 1.f, 100000.f) : 100.f;
    Hits = Deaths = 0;
    LastRegion = NAME_None;
    bDead = bPreviewMoving = false;
    PreviewDirection = 1.f;
    ResponseRemaining = DeathAge = 0.f;
    CurrentAnimation = nullptr;
    Body->bPauseAnims = false;
    Play(IdleAnimation, true);
    Body->TickAnimation(0.f, false);
    Body->RefreshBoneTransforms();
    UpdateLabel();
}
float AEnemyPrototypeCharacter::TakeDamage(float Amount, const FDamageEvent& Event, AController* EventInstigator, AActor* Causer)
{
    if (bDead || !FMath::IsFinite(Amount) || Amount <= 0) return 0.f;
    const FPointDamageEvent* Point = Event.IsOfType(FPointDamageEvent::ClassID) ? static_cast<const FPointDamageEvent*>(&Event) : nullptr;
    LastRegion = Point ? RegionForBone(Point->HitInfo.BoneName) : FName(TEXT("unmapped"));
    const float Applied = FMath::Min(Health, Amount);
    Health -= Applied;
    ++Hits;
    CurrentAnimation = nullptr;
    if (Health > 0)
    {
        Play(HitAnimation, false);
        ResponseRemaining = HitAnimation ? HitAnimation->GetPlayLength() : .2f;
    }
    else
    {
        bDead = true;
        ++Deaths;
        GetCharacterMovement()->StopMovementImmediately();
        GetCharacterMovement()->DisableMovement();
        GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        auto* Body = GetMesh();
        Body->SetCollisionObjectType(ECC_PhysicsBody);
        Body->SetCollisionResponseToAllChannels(ECR_Ignore);
        Body->SetCollisionResponseToChannel(ECC_WorldStatic, ECR_Block);
        Body->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
        Body->SetAllBodiesSimulatePhysics(true);
        Body->SetSimulatePhysics(true);
        Body->WakeAllRigidBodies();
        if (Point) Body->AddImpulse(Point->ShotDirection.GetSafeNormal() * 120.f, TEXT("pelvis"), true);
    }
    UpdateLabel();
    return Applied;
}
void AEnemyPrototypeCharacter::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (bDead)
    {
        DeathAge += DeltaSeconds;
        if (DeathAge >= 6.f) GetMesh()->PutAllRigidBodiesToSleep();
        return;
    }
    ResponseRemaining = FMath::Max(0.f, ResponseRemaining - DeltaSeconds);
    if (ResponseRemaining > 0)
        GetCharacterMovement()->StopMovementImmediately();
    else if (bPreviewMoving)
    {
        const float Offset = GetActorLocation().Y - Home.GetLocation().Y;
        if (Offset > 100.f) PreviewDirection = -1.f;
        if (Offset < -100.f) PreviewDirection = 1.f;
        AddMovementInput(FVector(0, PreviewDirection, 0), 1.f, true);
        Play(PreviewDirection > 0 ? LeftAnimation : RightAnimation, true);
    }
    else Play(IdleAnimation, true);
}
FName AEnemyPrototypeCharacter::RegionForBone(FName Bone)
{
    const FString Name = Bone.ToString();
    if (Name == TEXT("head") || Name.StartsWith(TEXT("neck"))) return TEXT("head");
    if (Name.StartsWith(TEXT("spine"))) return TEXT("torso");
    if (Name == TEXT("pelvis")) return TEXT("pelvis");
    if (Name.StartsWith(TEXT("upperarm")) || Name.StartsWith(TEXT("lowerarm")) || Name.StartsWith(TEXT("hand")))
        return Name.EndsWith(TEXT("_l")) ? TEXT("arm_l") : TEXT("arm_r");
    if (Name.StartsWith(TEXT("thigh")) || Name.StartsWith(TEXT("calf")) || Name.StartsWith(TEXT("foot")))
        return Name.EndsWith(TEXT("_l")) ? TEXT("leg_l") : TEXT("leg_r");
    return TEXT("unmapped");
}
TArray<FEnemyHitSphere> AEnemyPrototypeCharacter::SampleHitSpheres() const
{
    TArray<FEnemyHitSphere> Result;
    if (bDead) return Result;
    const auto* Body = GetMesh();
    auto Add = [&](FName Bone, FName End, float Radius, int32 Count)
    {
        if (Body->GetBoneIndex(Bone) == INDEX_NONE || Body->GetBoneIndex(End) == INDEX_NONE) return;
        const FVector A = Body->GetBoneLocation(Bone), B = Body->GetBoneLocation(End);
        for (int32 Index = 0; Index < Count; ++Index)
            Result.Add({Bone, FMath::Lerp(A, B, (Index + .5f) / Count), Radius});
    };
    Add(TEXT("head"), TEXT("head"), 12.f, 1);
    if (!Result.IsEmpty()) Result.Last().Center += Body->GetComponentTransform().TransformVectorNoScale(FVector(0, 0, 7));
    Add(TEXT("spine_04"), TEXT("spine_05"), 19.f, 1);
    Add(TEXT("spine_02"), TEXT("spine_03"), 17.f, 1);
    Add(TEXT("pelvis"), TEXT("spine_01"), 18.f, 1);
    for (const FString Side : {TEXT("l"), TEXT("r")})
    {
        Add(FName(TEXT("upperarm_") + Side), FName(TEXT("lowerarm_") + Side), 9.f, 2);
        Add(FName(TEXT("lowerarm_") + Side), FName(TEXT("hand_") + Side), 8.f, 2);
        Add(FName(TEXT("hand_") + Side), FName(TEXT("hand_") + Side), 8.f, 1);
        Add(FName(TEXT("thigh_") + Side), FName(TEXT("calf_") + Side), 12.f, 3);
        Add(FName(TEXT("calf_") + Side), FName(TEXT("foot_") + Side), 10.f, 3);
        Add(FName(TEXT("foot_") + Side), FName(TEXT("ball_") + Side), 10.f, 1);
    }
    return Result;
}
void AEnemyPrototypeCharacter::UpdateLabel()
{
    Label->SetText(FText::FromString(bDead ? TEXT("PROTOTYPE DOWN\nF6 RESET") :
        FString::Printf(TEXT("ENEMY PROTOTYPE  %.0f / %.0f"), Health, MaxHealth)));
    Label->SetTextRenderColor(bDead ? FColor(255, 150, 85) : Hits ? FColor(255, 210, 90) : FColor(180, 240, 215));
}
FString AEnemyPrototypeCharacter::GetEnemyState() const
{
    auto Root = MakeShared<FJsonObject>();
    Root->SetNumberField(TEXT("health"), Health);
    Root->SetNumberField(TEXT("hits"), Hits);
    Root->SetNumberField(TEXT("deaths"), Deaths);
    Root->SetBoolField(TEXT("dead"), bDead);
    Root->SetBoolField(TEXT("moving"), bPreviewMoving);
    Root->SetBoolField(TEXT("simulating"), GetMesh()->IsSimulatingPhysics());
    Root->SetBoolField(TEXT("awake"), GetMesh()->IsAnyRigidBodyAwake());
    Root->SetStringField(TEXT("region"), LastRegion.ToString());
    Root->SetStringField(TEXT("animation"), CurrentAnimation ? CurrentAnimation->GetPathName() : TEXT("ragdoll"));
    Root->SetNumberField(TEXT("response_remaining"), ResponseRemaining);
    Root->SetField(TEXT("location"), VectorJson(GetActorLocation()));
    Root->SetField(TEXT("velocity"), VectorJson(GetVelocity()));
    Root->SetField(TEXT("pelvis"), VectorJson(GetMesh()->GetBoneLocation(TEXT("pelvis"))));
    TArray<TSharedPtr<FJsonValue>> Spheres;
    for (const auto& Sphere : SampleHitSpheres())
    {
        auto Row = MakeShared<FJsonObject>();
        Row->SetStringField(TEXT("bone"), Sphere.Bone.ToString());
        Row->SetStringField(TEXT("region"), RegionForBone(Sphere.Bone).ToString());
        Row->SetField(TEXT("center"), VectorJson(Sphere.Center));
        Row->SetNumberField(TEXT("radius"), Sphere.Radius);
        Spheres.Add(MakeShared<FJsonValueObject>(Row));
    }
    Root->SetArrayField(TEXT("spheres"), Spheres);
    FString Output;
    FJsonSerializer::Serialize(Root, TJsonWriterFactory<>::Create(&Output));
    return Output;
}
