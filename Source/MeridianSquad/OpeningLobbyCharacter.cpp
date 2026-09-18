#include "OpeningLobbyCharacter.h"
#include "PurchasedArmsAnimInstance.h"
#include "Animation/AnimSequence.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/InputComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "UObject/ConstructorHelpers.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputKeyEventArgs.h"

namespace
{
void ConfigurePresentation(UPrimitiveComponent* Component)
{
    Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Component->SetGenerateOverlapEvents(false);
    Component->SetCastShadow(false);
    Component->bCastDynamicShadow = false;
    Component->bCastStaticShadow = false;
    Component->bCastHiddenShadow = false;
    Component->bCastContactShadow = false;
    Component->bAffectDynamicIndirectLighting = false;
    Component->bAffectDistanceFieldLighting = false;
    Component->SetOnlyOwnerSee(true);
    Component->SetFirstPersonPrimitiveType(EFirstPersonPrimitiveType::FirstPerson);
}

template<typename T> T* PurchasedAsset(const FString& RelativePath)
{
    ConstructorHelpers::FObjectFinder<T> Asset(*(TEXT("/Game/InfimaGames/TacticalFPSAnimations/") + RelativePath));
    return Asset.Object;
}
}

AOpeningLobbyCharacter::AOpeningLobbyCharacter()
{
    PrimaryActorTick.bCanEverTick = true;
    GetCapsuleComponent()->InitCapsuleSize(34.f, 88.f);
    BaseEyeHeight = 82.f;
    bUseControllerRotationYaw = true;
    GetCharacterMovement()->bOrientRotationToMovement = false;
    GetCharacterMovement()->MaxWalkSpeed = 360.f;
    GetCharacterMovement()->MaxAcceleration = 1800.f;
    GetCharacterMovement()->BrakingDecelerationWalking = 1800.f;
    GetCharacterMovement()->GravityScale = 1.f;
    GetCharacterMovement()->MaxStepHeight = 35.f;
    GetCharacterMovement()->JumpZVelocity = 320.f;
    FirstPersonCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FirstPersonCamera"));
    FirstPersonCamera->SetupAttachment(GetCapsuleComponent());
    FirstPersonCamera->SetRelativeLocation(FVector(0.f, 0.f, 82.f));
    FirstPersonCamera->bUsePawnControlRotation = true;
    FirstPersonCamera->FieldOfView = 90.f;
    FirstPersonCamera->bEnableFirstPersonScale = true;
    FirstPersonCamera->FirstPersonScale = .3f;

    USkeletalMeshComponent* Arms = GetMesh();
    Arms->SetupAttachment(FirstPersonCamera);
    Arms->SetRelativeLocation(FVector(-.663123f, 0.f, -162.5751f));
    Arms->SetRelativeRotation(FRotator(0.f, -90.f, 0.f));
    Arms->SetSkeletalMeshAsset(PurchasedAsset<USkeletalMesh>(TEXT("Common/Characters/Mannequins/Meshes/SKM_FP_Manny_Simple")));
    Arms->SetAnimInstanceClass(UPurchasedArmsAnimInstance::StaticClass());
    ConfigurePresentation(Arms);

    const FString MeshRoot = TEXT("Weapons/AssaultRifle/Meshes/");
    Rifle = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("PurchasedRifle"));
    Rifle->SetupAttachment(Arms, TEXT("ik_hand_gun"));
    Rifle->SetSkeletalMeshAsset(PurchasedAsset<USkeletalMesh>(MeshRoot + TEXT("SK_TFA_AR")));
    Rifle->SetAnimInstanceClass(UPurchasedArmsAnimInstance::StaticClass());
    MainMagazine = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("MainMagazine"));
    MainMagazine->SetupAttachment(Rifle, TEXT("SOCKET_Magazine"));
    ReserveMagazine = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("ReserveMagazine"));
    ReserveMagazine->SetupAttachment(Rifle, TEXT("SOCKET_Magazine_Reserve"));
    for (USkeletalMeshComponent* Magazine : {MainMagazine.Get(), ReserveMagazine.Get()})
        Magazine->SetSkeletalMeshAsset(PurchasedAsset<USkeletalMesh>(MeshRoot + TEXT("SK_TFA_AR_Magazine")));
    ReserveMagazine->SetVisibility(false);
    Handguard = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RifleHandguard"));
    Handguard->SetupAttachment(Rifle, TEXT("SOCKET_Handguard"));
    Handguard->SetStaticMesh(PurchasedAsset<UStaticMesh>(MeshRoot + TEXT("SM_TFA_AR_Handguard_Default")));
    RearSight = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RifleRearSight"));
    RearSight->SetupAttachment(Rifle, TEXT("SOCKET_Sight_Rear"));
    RearSight->SetStaticMesh(PurchasedAsset<UStaticMesh>(MeshRoot + TEXT("SM_TFA_AR_ATT_Sight_Rear")));
    FrontSight = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RifleFrontSight"));
    FrontSight->SetupAttachment(Handguard, TEXT("SOCKET_Sight_Front"));
    FrontSight->SetStaticMesh(PurchasedAsset<UStaticMesh>(MeshRoot + TEXT("SM_TFA_AR_ATT_Sight_Front")));
    for (UPrimitiveComponent* Part : TArray<UPrimitiveComponent*>{Rifle.Get(), MainMagazine.Get(), ReserveMagazine.Get(), Handguard.Get(), RearSight.Get(), FrontSight.Get()})
        ConfigurePresentation(Part);
    for (USkeletalMeshComponent* Part : {Arms, Rifle.Get(), MainMagazine.Get(), ReserveMagazine.Get()})
    {
        Part->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
        Part->bEnableUpdateRateOptimizations = false;
    }

    const FString FP = TEXT("Weapons/AssaultRifle/Animations/Character/FP/");
    for (const FString& Stance : {FString(TEXT("Standing")), FString(TEXT("Aimed"))})
        for (const FString& Motion : {FString(TEXT("Idle")), FString(TEXT("Walk_F")), FString(TEXT("Walk_B")), FString(TEXT("Walk_Strafe_L")), FString(TEXT("Walk_Strafe_R"))})
            LocomotionClips.Add(PurchasedAsset<UAnimSequence>(FP + TEXT("Locomotion/A_TFA_FP_AR_") + Motion + TEXT("_Loop_") + Stance));
    BasePoses.Add(PurchasedAsset<UAnimSequence>(FP + TEXT("Poses/A_TFA_FP_AR_Idle_Pose_Standing")));
    BasePoses.Add(PurchasedAsset<UAnimSequence>(FP + TEXT("Poses/A_TFA_FP_AR_Aim_Pose")));
    for (const FString& Suffix : {FString(), FString(TEXT("_Aimed"))})
    {
        ReloadClips.Add(PurchasedAsset<UAnimSequence>(FP + TEXT("Combat/A_TFA_FP_AR_Reload") + Suffix));
        RifleReloadClips.Add(PurchasedAsset<UAnimSequence>(TEXT("Weapons/AssaultRifle/Animations/Weapon/FP/A_TFA_FP_WEP_AR_Reload") + Suffix));
    }
}

void AOpeningLobbyCharacter::BeginPlay()
{
    Super::BeginPlay();
    // One owner clock, then arms, rifle and socket-attached magazine transforms.
    GetMesh()->AddTickPrerequisiteActor(this);
    Rifle->AddTickPrerequisiteComponent(GetMesh());
    MainMagazine->AddTickPrerequisiteComponent(Rifle);
    ReserveMagazine->AddTickPrerequisiteComponent(Rifle);
    ReloadDuration = ReloadClips[0] ? ReloadClips[0]->GetPlayLength() : 0.f;
}

void AOpeningLobbyCharacter::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    AnimationTime += DeltaSeconds;
    const FVector LocalVelocity = GetActorRotation().UnrotateVector(GetVelocity()) / GetCharacterMovement()->MaxWalkSpeed;
    MoveBlend = FMath::Vector2DInterpTo(MoveBlend, FVector2D(LocalVelocity.X, LocalVelocity.Y), DeltaSeconds, 12.f);
    if (bReloading)
    {
        ReloadTime = FMath::Min(ReloadTime + DeltaSeconds, ReloadDuration);
        if (ReloadTime >= ReloadDuration)
        {
            bReloading = false;
            ++ReloadCompletions;
        }
    }
    if (!bReloading) AimAlpha = FMath::FInterpConstantTo(AimAlpha, bAimRequested ? 1.f : 0.f, DeltaSeconds, 5.f);
    // Fit the supplied iron sights to the fixed lobby camera without changing eye height or FOV.
    GetMesh()->SetRelativeLocation(FVector(-.663123f, 0.f, -162.5751f + .85f * (bReloading ? ReloadAimAlpha : AimAlpha)));
    // The two authored weapon sockets carry the hand-off; no vendor notify objects or dropped actors.
    MainMagazine->SetVisibility(!bReloading || ReloadTime < 2.520381f);
    ReserveMagazine->SetVisibility(bReloading && ReloadTime >= .455137f);
}

void AOpeningLobbyCharacter::CalcCamera(float DeltaSeconds, FMinimalViewInfo& OutResult)
{
    Super::CalcCamera(DeltaSeconds, OutResult);
    // The scaled first-person presentation needs a close plane to retain wrists and the rear sight.
    OutResult.PerspectiveNearClipPlane = .1f;
}

void AOpeningLobbyCharacter::AimPressed() { bAimRequested = true; }
void AOpeningLobbyCharacter::AimReleased() { bAimRequested = false; }
void AOpeningLobbyCharacter::Reload()
{
    if (bReloading || ReloadDuration <= 0.f) return;
    bReloading = true;
    ReloadTime = 0.f;
    ReloadAimAlpha = AimAlpha;
    ++ReloadStarts;
}

void AOpeningLobbyCharacter::SetupPlayerInputComponent(UInputComponent* Input)
{
    Super::SetupPlayerInputComponent(Input);
    Input->BindAxis(TEXT("LobbyForward"), this, &AOpeningLobbyCharacter::MoveForward);
    Input->BindAxis(TEXT("LobbyRight"), this, &AOpeningLobbyCharacter::MoveRight);
    Input->BindAxis(TEXT("LobbyYaw"), this, &AOpeningLobbyCharacter::LookYaw);
    Input->BindAxis(TEXT("LobbyPitch"), this, &AOpeningLobbyCharacter::LookPitch);
    Input->BindAction(TEXT("LobbyAim"), IE_Pressed, this, &AOpeningLobbyCharacter::AimPressed);
    Input->BindAction(TEXT("LobbyAim"), IE_Released, this, &AOpeningLobbyCharacter::AimReleased);
    Input->BindAction(TEXT("LobbyReload"), IE_Pressed, this, &AOpeningLobbyCharacter::Reload);
}

void AOpeningLobbyCharacter::MoveForward(float Value)
{
    if (Controller && !FMath::IsNearlyZero(Value))
    {
        ++MoveBindingSamples;
        AddMovementInput(FRotationMatrix(FRotator(0, Controller->GetControlRotation().Yaw, 0)).GetUnitAxis(EAxis::X), Value);
    }
}
void AOpeningLobbyCharacter::MoveRight(float Value)
{
    if (Controller && !FMath::IsNearlyZero(Value))
    {
        ++MoveBindingSamples;
        AddMovementInput(FRotationMatrix(FRotator(0, Controller->GetControlRotation().Yaw, 0)).GetUnitAxis(EAxis::Y), Value);
    }
}
void AOpeningLobbyCharacter::LookYaw(float Value)
{
    if (!FMath::IsNearlyZero(Value)) { ++LookBindingSamples; AddControllerYawInput(Value); }
}
void AOpeningLobbyCharacter::LookPitch(float Value)
{
    if (!FMath::IsNearlyZero(Value)) { ++LookBindingSamples; AddControllerPitchInput(Value); }
}

bool AOpeningLobbyCharacter::ProbeKey(FName KeyName, float Amount, bool Pressed)
{
#if WITH_EDITOR
    if (GetWorld() && GetWorld()->WorldType == EWorldType::PIE)
    {
        if (APlayerController* PC = Cast<APlayerController>(Controller))
        {
            const FKey Key(KeyName);
            if (Key.IsValid())
                return PC->InputKey(FInputKeyEventArgs::CreateSimulated(Key, Key.IsAxis1D() ? IE_Axis : (Pressed ? IE_Pressed : IE_Released), Amount));
        }
    }
#endif
    return false;
}

FString AOpeningLobbyCharacter::GetProbeState() const
{
    const UCharacterMovementComponent* M = GetCharacterMovement();
    return FString::Printf(TEXT("{\"walking\":%s,\"falling\":%s,\"gravity_scale\":%.3f,\"gravity_z\":%.3f,\"walkable_floor\":%s,\"floor_distance\":%.3f,\"capsule_radius\":%.3f,\"capsule_half_height\":%.3f,\"eye_above_capsule_bottom\":%.3f,\"fov\":%.3f,\"move_binding_samples\":%d,\"look_binding_samples\":%d,\"aim_requested\":%s,\"aim_alpha\":%.6f,\"reloading\":%s,\"reload_time\":%.6f,\"reload_aim_alpha\":%.6f,\"reload_starts\":%d,\"reload_completions\":%d,\"animation_time\":%.6f,\"move_blend\":[%.6f,%.6f]}"),
        M->IsMovingOnGround() ? TEXT("true") : TEXT("false"), M->IsFalling() ? TEXT("true") : TEXT("false"), M->GravityScale, M->GetGravityZ(),
        M->CurrentFloor.IsWalkableFloor() ? TEXT("true") : TEXT("false"), M->CurrentFloor.FloorDist,
        GetCapsuleComponent()->GetScaledCapsuleRadius(), GetCapsuleComponent()->GetScaledCapsuleHalfHeight(),
        FirstPersonCamera->GetRelativeLocation().Z + GetCapsuleComponent()->GetScaledCapsuleHalfHeight(), FirstPersonCamera->FieldOfView, MoveBindingSamples, LookBindingSamples,
        bAimRequested ? TEXT("true") : TEXT("false"), AimAlpha, bReloading ? TEXT("true") : TEXT("false"), ReloadTime, ReloadAimAlpha,
        ReloadStarts, ReloadCompletions, AnimationTime, MoveBlend.X, MoveBlend.Y);
}
