#include "OpeningLobbyCharacter.h"
#include "CombatMovement.h"
#include "CombatRifleComponent.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/InputComponent.h"
#include "Components/LightComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMeshActor.h"
#include "EnhancedInputSubsystems.h"
#include "EnhancedInputComponent.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputKeyEventArgs.h"
#include "UObject/UnrealType.h"

namespace
{
constexpr float OrdinaryJumpZVelocity = 320.f;
constexpr float FastJumpMultiplier = 1.1f;
// Authored contact sound is at .39249; the impact dip peaks near .49.
// .30 is still flight. Only collision may advance into the contact/recovery portion.
constexpr float JumpFlightHoldTime = .30f;
constexpr float JumpContactStartTime = .38f;

bool Flag(const UObject* Object, FName Name)
{
    const FBoolProperty* P = Object ? FindFProperty<FBoolProperty>(Object->GetClass(), Name) : nullptr;
    return P && P->GetPropertyValue_InContainer(Object);
}
void SetFlag(UObject* Object, FName Name, bool Value)
{
    if (FBoolProperty* P = FindFProperty<FBoolProperty>(Object->GetClass(), Name)) P->SetPropertyValue_InContainer(Object, Value);
}
UObject* ObjectValue(const UObject* Object, FName Name)
{
    const FObjectPropertyBase* P = Object ? FindFProperty<FObjectPropertyBase>(Object->GetClass(), Name) : nullptr;
    return P ? P->GetObjectPropertyValue_InContainer(Object) : nullptr;
}
uint8 ByteValue(const UObject* Object, FName Name)
{
    const FByteProperty* P = Object ? FindFProperty<FByteProperty>(Object->GetClass(), Name) : nullptr;
    return P ? P->GetPropertyValue_InContainer(Object) : 0;
}
void SetByte(UObject* Object, FName Name, uint8 Value)
{
    if (FByteProperty* P = FindFProperty<FByteProperty>(Object->GetClass(), Name)) P->SetPropertyValue_InContainer(Object, Value);
}
template<typename T> void SetStruct(UObject* Object, FName Name, const T& Value)
{
    if (FStructProperty* P = FindFProperty<FStructProperty>(Object->GetClass(), Name))
        *P->ContainerPtrToValuePtr<T>(Object) = Value;
}
void Shadowless(UPrimitiveComponent* Part, bool FirstPerson)
{
    Part->SetCastShadow(false);
    Part->bCastDynamicShadow = false;
    Part->bCastStaticShadow = false;
    Part->bCastHiddenShadow = false;
    Part->bCastContactShadow = false;
    Part->bAffectDynamicIndirectLighting = false;
    Part->bAffectDistanceFieldLighting = false;
    if (FirstPerson)
    {
        Part->SetFirstPersonPrimitiveType(EFirstPersonPrimitiveType::FirstPerson);
        Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Part->SetGenerateOverlapEvents(false);
    }
    else Part->SetFirstPersonPrimitiveType(EFirstPersonPrimitiveType::None);
}
}

AOpeningLobbyCharacter::AOpeningLobbyCharacter()
{
    PrimaryActorTick.bCanEverTick = true;
    GetCapsuleComponent()->InitCapsuleSize(34.f, 88.f);
    BaseEyeHeight = 82.f;
    CrouchedEyeHeight = 50.f;
    bUseControllerRotationYaw = true;
    auto* Movement = GetCharacterMovement();
    Movement->bOrientRotationToMovement = false;
    Movement->MaxWalkSpeed = CombatMovement::BaseSpeed;
    Movement->MaxWalkSpeedCrouched = 180.f;
    Movement->MaxAcceleration = 1800.f;
    Movement->BrakingDecelerationWalking = 1800.f;
    Movement->GravityScale = 1.f;
    Movement->MaxStepHeight = 35.f;
    Movement->JumpZVelocity = OrdinaryJumpZVelocity;
    Movement->GetNavAgentPropertiesRef().bCanCrouch = true;
    Movement->SetCrouchedHalfHeight(56.f);
    FirstPersonCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FirstPersonCamera"));
    FirstPersonCamera->SetupAttachment(GetCapsuleComponent());
    FirstPersonCamera->SetRelativeLocation(FVector(0, 0, 82));
    FirstPersonCamera->bUsePawnControlRotation = true;
    FirstPersonCamera->FieldOfView = 90.f;
    FirstPersonCamera->bEnableFirstPersonScale = true;
    FirstPersonCamera->FirstPersonScale = .3f;
    CombatRifle = CreateDefaultSubobject<UCombatRifleComponent>(TEXT("CombatRifle"));
}

void AOpeningLobbyCharacter::CallSource(FName Name)
{
    if (UFunction* Function = FindFunction(Name)) ProcessEvent(Function, nullptr);
}

void AOpeningLobbyCharacter::BeginPlay()
{
    Super::BeginPlay();
    auto* Movement = GetCharacterMovement();
    GetCapsuleComponent()->SetCapsuleSize(34.f, 88.f);
    Movement->SetMovementMode(MOVE_Walking);
    Movement->MaxAcceleration = 1800.f;
    Movement->BrakingDecelerationWalking = 1800.f;
    Movement->GravityScale = 1.f;
    Movement->MaxStepHeight = 35.f;
    Movement->JumpZVelocity = OrdinaryJumpZVelocity;
    Movement->GetNavAgentPropertiesRef().bCanCrouch = true;
    Movement->SetCrouchedHalfHeight(56.f);
    bUseControllerRotationYaw = true;
    GetMesh()->AttachToComponent(FirstPersonCamera, FAttachmentTransformRules::KeepRelativeTransform);
    GetMesh()->SetRelativeLocation(FVector(-.663123f, 0.f, -162.5751f));
    GetMesh()->SetRelativeRotation(FRotator(0,-90,0));
    GetMesh()->SetSkeletalMeshAsset(LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/InfimaGames/TacticalFPSAnimations/Common/Characters/Mannequins/Meshes/SKM_FP_Manny_Simple.SKM_FP_Manny_Simple")));
    GetMesh()->SetAnimInstanceClass(LoadClass<UAnimInstance>(nullptr, TEXT("/Game/InfimaGames/TacticalFPSAnimations/Common/Core/Characters/ABP_TFA_FP_BaseCharacter.ABP_TFA_FP_BaseCharacter_C")));
    GetMesh()->AddTickPrerequisiteActor(this);
    // Despite its name, the supplied AnimBP bool blends the head to reference pose when true.
    // Keep that lock on by default; L releases it and selects the authored head camera.
    SetFlag(this, TEXT("bAnimateCamera"), true);
    if (auto* SourceCamera = Cast<UCameraComponent>(ObjectValue(this, TEXT("CameraFP"))))
        SourceCamera->SetFieldOfView(90.f);
    CallSource(TEXT("SpawnWeapon"));
    bSourceReady = ObjectValue(this, TEXT("CurrentWeaponActor")) != nullptr;
    if (auto* PC = Cast<APlayerController>(Controller))
    {
        EnableInput(PC);
        if (auto* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
            if (auto* Mapping = LoadObject<UInputMappingContext>(nullptr, TEXT("/Game/InfimaGames/TacticalFPSAnimations/Common/Core/Inputs/IMC_TFA_Default.IMC_TFA_Default")))
                Subsystem->AddMappingContext(Mapping, 0);
    }
    if (auto* SourceJump = LoadObject<UAnimMontage>(nullptr, TEXT("/Game/InfimaGames/TacticalFPSAnimations/Weapons/AssaultRifle/Animations/Character/FP/Locomotion/AM_TFA_FP_AR_Jump_Full.AM_TFA_FP_AR_Jump_Full")))
    {
        // A per-pawn presentation montage owns neither the source action lock nor ADS.
        // Keep authored poses/foley and immutable asset bytes. In particular, an old
        // jump must never unlock a newer fire/reload montage when interrupted.
        JumpMontage = DuplicateObject<UAnimMontage>(SourceJump, this, TEXT("LobbyJump"));
        JumpMontage->SetFlags(RF_Transient);
        JumpMontage->ClearFlags(RF_Public | RF_Standalone);
        JumpMontage->Notifies.RemoveAll([](const FAnimNotifyEvent& Notify)
        {
            return Notify.NotifyName == TEXT("ANS_BlockADS_C") || Notify.NotifyName == TEXT("AN_UnlockActions_C");
        });
    }
    ConfigureAssembly();
    CombatRifle->InitializeRifle();
}

void AOpeningLobbyCharacter::ConfigureAssembly()
{
    TArray<AActor*> Attached;
    GetAttachedActors(Attached, true, true);
    Attached.Add(this);
    for (AActor* Actor : Attached)
    {
        for (UActorComponent* Component : Actor->GetComponents())
        {
            if (auto* Light = Cast<ULightComponent>(Component)) Light->SetVisibility(false);
            if (auto* Part = Cast<UPrimitiveComponent>(Component); Part && Part != GetCapsuleComponent())
            {
                Shadowless(Part, true);
                if (auto* Skinned = Cast<USkeletalMeshComponent>(Part))
                {
                    Skinned->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
                    Skinned->bEnableUpdateRateOptimizations = false;
                    if (Skinned != GetMesh()) Skinned->AddTickPrerequisiteComponent(GetMesh());
                }
            }
        }
    }
    // Dropped casings, magazines and syringe props keep source physics but cast no shadows.
    for (TActorIterator<AActor> It(GetWorld()); It; ++It)
        if (It->GetClass()->GetPathName().Contains(TEXT("BP_TFA_Physics")))
            for (UActorComponent* Component : It->GetComponents())
                if (auto* Part = Cast<UPrimitiveComponent>(Component)) Shadowless(Part, false);
}

void AOpeningLobbyCharacter::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    AnimationTime += DeltaSeconds;
    if (!bSourceReady) return;
    auto* Movement = GetCharacterMovement();
    // Reconcile after all input callbacks, including a same-frame fire release.
    // Otherwise a held Shift can briefly enter Run End before running resumes.
    UpdateFastMovement();
    const auto* AnimInstance = GetMesh()->GetAnimInstance();
    const auto* JumpInstance = AnimInstance && JumpMontage ? AnimInstance->GetInstanceForMontage(JumpMontage) : nullptr;
    const bool bHasJumpPose = JumpInstance && (JumpInstance->IsActive() || JumpInstance->GetWeight() > ZERO_ANIMWEIGHT_THRESH);
    if (bHasJumpPose && (Flag(this, TEXT("bIsRunning")) || Flag(this, TEXT("bIsSprinting"))))
        bProtectJumpPose = true;
    if (!bJumpPresentation && !bHasJumpPose && !Flag(this, TEXT("bIsAiming")) &&
        !Flag(this, TEXT("bIsBusy")) && !bAirborneFireHeld)
        bProtectJumpPose = false;
    const uint8 RequestedStance = ByteValue(this, TEXT("CurrentStance"));
    if (RequestedStance != ReportedStance) bCrouchRequested = RequestedStance == 1;
    if (bCrouchRequested) Crouch(); else UnCrouch();
    // A blocked stand request remains pending while the source graph follows the achieved capsule stance.
    ReportedStance = bIsCrouched ? 1 : 0;
    SetByte(this, TEXT("CurrentStance"), ReportedStance);
    FTransform CrouchOffset = FTransform::Identity;
    if (bIsCrouched && !Flag(this, TEXT("bIsAiming")))
        if (UObject* Config = ObjectValue(this, TEXT("WeaponConfig")))
            if (const FStructProperty* P = FindFProperty<FStructProperty>(Config->GetClass(), TEXT("OffsetCrouch")))
                CrouchOffset = *P->ContainerPtrToValuePtr<FTransform>(Config);
    SetStruct(this, TEXT("TargetCrouchOffset"), CrouchOffset);
    Movement->MaxWalkSpeed = Flag(this, TEXT("bIsSprinting")) ? 720.f : Flag(this, TEXT("bIsRunning")) ? 540.f : CombatMovement::BaseSpeed;
    if (bJumpPresentation && Movement->IsFalling())
    {
        // Releasing the speed key in flight must not brake away the takeoff momentum.
        // This only retains a speed cap; CharacterMovement still owns velocity and collision.
        Movement->MaxWalkSpeed = FMath::Max(Movement->MaxWalkSpeed, JumpPlanarSpeed);
    }
    Movement->MaxWalkSpeedCrouched = 180.f;
    const FVector Local = GetActorRotation().UnrotateVector(GetVelocity());
    // Source blend-space axes are strafe/forward; 100 and 200 are animation units.
    const float Scale = Flag(this, TEXT("bIsRunning")) ? 200.f / 540.f : 100.f / 360.f;
    SetStruct(this, TEXT("SimulatedVelocity"), FVector(Local.Y * Scale, Local.X * Scale, 0));
    SetFlag(this, TEXT("bIsWalking"), Local.Size2D() > 1.f);
    if (Local.Size2D() <= 1.f && Movement->IsMovingOnGround())
    {
        // Held enhanced inputs request speed again when movement resumes; a wall stop must not run in place.
        SetFlag(this, TEXT("bIsRunning"), false);
        SetFlag(this, TEXT("bIsSprinting"), false);
    }
    CallSource(TEXT("Procedural Offsets"));
    if (bJumpPresentation && JumpMontage)
    {
        // Clamp BEFORE the next mesh tick, including a long frame, so neither
        // a pose nor a landing notify can overshoot into impact while airborne.
        if (auto* Anim = GetMesh()->GetAnimInstance())
            if (Anim->Montage_IsActive(JumpMontage) &&
                Anim->Montage_GetPosition(JumpMontage) + DeltaSeconds >= JumpFlightHoldTime)
            {
                Anim->Montage_SetPosition(JumpMontage, JumpFlightHoldTime);
                Anim->Montage_Pause(JumpMontage);
            }
    }
    CameraHeight = FMath::FInterpTo(CameraHeight, bIsCrouched ? 50.f : 82.f, DeltaSeconds, 14.f);
    FirstPersonCamera->SetRelativeLocation(FVector(0, 0, CameraHeight));
    if (const auto* SourceCamera = Cast<UCameraComponent>(ObjectValue(this, TEXT("CameraFP"))))
        FirstPersonCamera->FieldOfView = SourceCamera->FieldOfView;
    // CharacterMovement adjusts the inherited mesh during crouch. Restore its camera-space contract.
    RestoreMeshAnchor();
    ConfigureAssembly();
}

void AOpeningLobbyCharacter::CalcCamera(float DeltaSeconds, FMinimalViewInfo& OutResult)
{
    FirstPersonCamera->GetCameraView(DeltaSeconds, OutResult);
    if (!Flag(this, TEXT("bAnimateCamera")))
        if (const auto* SourceCamera = Cast<UCameraComponent>(ObjectValue(this, TEXT("CameraFP"))))
        {
            OutResult.Location = SourceCamera->GetComponentLocation();
            OutResult.Rotation = SourceCamera->GetComponentRotation();
        }
    OutResult.PerspectiveNearClipPlane = .1f;
    // Notify-spawned primitives also receive the policy before this frame is rendered.
    ConfigureAssembly();
}

void AOpeningLobbyCharacter::RestoreMeshAnchor()
{
    GetMesh()->SetRelativeLocation(FVector(-.663123f, 0.f, -162.5751f));
    GetMesh()->SetRelativeRotation(FRotator(0,-90,0));
}
void AOpeningLobbyCharacter::OnStartCrouch(float A, float B)
{
    Super::OnStartCrouch(A, B);
    RestoreMeshAnchor();
}
void AOpeningLobbyCharacter::OnEndCrouch(float A, float B)
{
    Super::OnEndCrouch(A, B);
    RestoreMeshAnchor();
}
void AOpeningLobbyCharacter::ToggleCameraAnimation()
{
    SetFlag(this, TEXT("bAnimateCamera"), !Flag(this, TEXT("bAnimateCamera")));
}

void AOpeningLobbyCharacter::JumpPressed()
{
    auto* Movement = GetCharacterMovement();
    if (Flag(this, TEXT("bIsBusy")) || bIsCrouched || !Movement->IsMovingOnGround() || !CanJump()) return;
    // Check real input as well as achieved sprint: its .3 s enhanced hold trigger
    // and callback ordering must not leave an activation-frame hole for Space.
    const auto* PC = Cast<APlayerController>(Controller);
    if (Flag(this, TEXT("bIsSprinting")) || (PC && PC->IsInputKeyDown(EKeys::LeftAlt))) return;
    const bool bWasRunning = Flag(this, TEXT("bIsRunning"));
    const float PlanarSpeed = GetVelocity().Size2D();
    // Require achieved fast movement, not just a held key or a run request at a wall.
    const bool bFastJump = bWasRunning && PlanarSpeed > 360.f;
    Movement->JumpZVelocity = OrdinaryJumpZVelocity * (bFastJump ? FastJumpMultiplier : 1.f);
    JumpPlanarSpeed = bFastJump ? PlanarSpeed : 0.f;
    bJumpRequested = true;
    bRequestedFastJumpBase = bWasRunning;
    ++JumpRequests;
    Jump();
}

void AOpeningLobbyCharacter::OnJumped_Implementation()
{
    Super::OnJumped_Implementation();
    if (!bJumpRequested) return;
    // Jump() only queues input. Own presentation only after movement confirms
    // takeoff, so a press/release in one movement frame cannot leave a ground hold.
    bJumpRequested = false;
    ++JumpStarts;
    bJumpPresentation = true;
    bProtectJumpPose = bRequestedFastJumpBase;
    // Locomotion intent resumes from held enhanced input on the ground. Physical
    // airborne momentum is retained separately, without blocking weapon actions.
    SetFlag(this, TEXT("bIsRunning"), false);
    SetFlag(this, TEXT("bIsSprinting"), false);
    if (auto* Anim = GetMesh()->GetAnimInstance(); Anim && JumpMontage)
        Anim->Montage_Play(JumpMontage);
}
void AOpeningLobbyCharacter::CancelPendingJump()
{
    if (!bJumpRequested) return;
    bJumpRequested = false;
    bRequestedFastJumpBase = false;
    ++CanceledJumpRequests;
    JumpPlanarSpeed = 0.f;
    GetCharacterMovement()->JumpZVelocity = OrdinaryJumpZVelocity;
    // A preceding landing tail or another weapon action retains its ownership.
}
void AOpeningLobbyCharacter::JumpReleased()
{
    StopJumping();
    CancelPendingJump();
}
void AOpeningLobbyCharacter::CheckJumpInput(float DeltaTime)
{
    Super::CheckJumpInput(DeltaTime);
    if (bJumpRequested)
    {
        // Movement rejected an otherwise eligible request. OnJumped consumes a
        // successful request synchronously; never clear a confirmed flight here.
        StopJumping();
        CancelPendingJump();
    }
}
void AOpeningLobbyCharacter::Landed(const FHitResult& Hit)
{
    Super::Landed(Hit);
    ++Landings;
    LastLandingTime = GetWorld()->GetTimeSeconds();
    GetCharacterMovement()->JumpZVelocity = OrdinaryJumpZVelocity;
    JumpPlanarSpeed = 0.f;
    if (bJumpPresentation && JumpMontage)
    {
        // Resume only our still-owned presentation. A shot/reload may already
        // have replaced it; never resurrect that jump or touch the action lock.
        if (auto* Anim = GetMesh()->GetAnimInstance(); Anim && Anim->Montage_IsActive(JumpMontage))
        {
            Anim->Montage_SetPosition(JumpMontage, JumpContactStartTime);
            Anim->Montage_Resume(JumpMontage);
        }
    }
    bJumpPresentation = false;
}

bool AOpeningLobbyCharacter::NeedsOrdinaryJumpBase() const
{
    const auto* Anim = GetMesh()->GetAnimInstance();
    if (bProtectJumpPose && Anim && JumpMontage)
    {
        // Releasing the reference-pose run layer at contact would start Run End
        // over ADS/fire when those actions already replaced the jump montage.
        // This latch belongs to this jump and expires after its recovery.
        if (bJumpPresentation || bAirborneFireHeld || Flag(this, TEXT("bIsAiming")) || Flag(this, TEXT("bIsBusy"))) return true;
        // Include paused flight and the entire blend-out, after IsFalling and
        // Montage_IsActive have ended. Never alter the physical movement flags.
        if (const auto* Instance = Anim->GetInstanceForMontage(JumpMontage))
            return Instance->IsActive() || Instance->GetWeight() > ZERO_ANIMWEIGHT_THRESH;
    }
    return false;
}

void AOpeningLobbyCharacter::PawnClientRestart()
{
    Super::PawnClientRestart();
    // Blueprint delegates are installed after SetupPlayerInputComponent. Replace
    // only these two locomotion handlers after that installation, retaining the
    // source mappings, hold thresholds and ground stance/aim/busy conditions.
    auto* Input = Cast<UEnhancedInputComponent>(InputComponent);
    if (!Input || AdaptedInputComponent == Input) return;
    AdaptedInputComponent = Input;
    const auto* Run = LoadObject<UInputAction>(nullptr, TEXT("/Game/InfimaGames/TacticalFPSAnimations/Common/Core/Inputs/IA_TFA_Run.IA_TFA_Run"));
    const auto* Sprint = LoadObject<UInputAction>(nullptr, TEXT("/Game/InfimaGames/TacticalFPSAnimations/Common/Core/Inputs/IA_TFA_Sprint.IA_TFA_Sprint"));
    const auto* Fire = LoadObject<UInputAction>(nullptr, TEXT("/Game/InfimaGames/TacticalFPSAnimations/Common/Core/Inputs/IA_TFA_Fire.IA_TFA_Fire"));
    TArray<uint32> Handles;
    for (const auto& Binding : Input->GetActionEventBindings())
        if (Binding->GetAction() == Run || Binding->GetAction() == Sprint)
            Handles.Add(Binding->GetHandle());
    for (uint32 Handle : Handles) Input->RemoveBindingByHandle(Handle);
    FastInputBindings = Handles.Num();
    Input->BindAction(Run, ETriggerEvent::Triggered, this, &AOpeningLobbyCharacter::RunTriggered);
    Input->BindAction(Run, ETriggerEvent::Completed, this, &AOpeningLobbyCharacter::RunReleased);
    Input->BindAction(Run, ETriggerEvent::Canceled, this, &AOpeningLobbyCharacter::RunReleased);
    Input->BindAction(Sprint, ETriggerEvent::Triggered, this, &AOpeningLobbyCharacter::SprintTriggered);
    Input->BindAction(Sprint, ETriggerEvent::Completed, this, &AOpeningLobbyCharacter::SprintReleased);
    Input->BindAction(Sprint, ETriggerEvent::Canceled, this, &AOpeningLobbyCharacter::SprintReleased);
    // Rifle owns ammunition, cadence and reload input. Retain the airborne
    // presentation observer after replacing the source demonstration callbacks.
    CombatRifle->BindInput(Input);
    Input->BindAction(Fire, ETriggerEvent::Started, this, &AOpeningLobbyCharacter::FireStarted);
    Input->BindAction(Fire, ETriggerEvent::Completed, this, &AOpeningLobbyCharacter::FireReleased);
    Input->BindAction(Fire, ETriggerEvent::Canceled, this, &AOpeningLobbyCharacter::FireReleased);
}

bool AOpeningLobbyCharacter::CanStartFastMovement() const
{
    return !bJumpRequested && !bJumpPresentation && GetCharacterMovement()->IsMovingOnGround() &&
        ByteValue(this, TEXT("CurrentStance")) == 0 && !Flag(this, TEXT("bIsAiming")) &&
        !Flag(this, TEXT("bIsBusy")) && !bAirborneFireHeld;
}
void AOpeningLobbyCharacter::RunTriggered()
{
    bRunInputTriggered = true;
    UpdateFastMovement();
}
void AOpeningLobbyCharacter::RunReleased()
{
    bRunInputTriggered = false;
    SetFlag(this, TEXT("bIsRunning"), false);
}
void AOpeningLobbyCharacter::SprintTriggered()
{
    bSprintInputTriggered = true;
    UpdateFastMovement();
}
void AOpeningLobbyCharacter::SprintReleased()
{
    bSprintInputTriggered = false;
    SetFlag(this, TEXT("bIsSprinting"), false);
}
void AOpeningLobbyCharacter::UpdateFastMovement()
{
    if (CanStartFastMovement())
    {
        if (bRunInputTriggered) SetFlag(this, TEXT("bIsRunning"), true);
        if (bSprintInputTriggered) SetFlag(this, TEXT("bIsSprinting"), true);
    }
}
void AOpeningLobbyCharacter::FireStarted()
{
    bAirborneFireHeld = bJumpPresentation || GetCharacterMovement()->IsFalling();
}
void AOpeningLobbyCharacter::FireReleased() { bAirborneFireHeld = false; }

void AOpeningLobbyCharacter::SetupPlayerInputComponent(UInputComponent* Input)
{
    Super::SetupPlayerInputComponent(Input);
    Input->BindAxis(TEXT("LobbyForward"), this, &AOpeningLobbyCharacter::MoveForward);
    Input->BindAxis(TEXT("LobbyRight"), this, &AOpeningLobbyCharacter::MoveRight);
    Input->BindAxis(TEXT("LobbyYaw"), this, &AOpeningLobbyCharacter::LookYaw);
    Input->BindAxis(TEXT("LobbyPitch"), this, &AOpeningLobbyCharacter::LookPitch);
    Input->BindAction(TEXT("LobbyJump"), IE_Pressed, this, &AOpeningLobbyCharacter::JumpPressed);
    Input->BindAction(TEXT("LobbyJump"), IE_Released, this, &AOpeningLobbyCharacter::JumpReleased);
    Input->BindAction(TEXT("LobbyCameraAnimation"), IE_Pressed, this, &AOpeningLobbyCharacter::ToggleCameraAnimation);
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
        if (auto* PC = Cast<APlayerController>(Controller))
        {
            const FKey Key(KeyName);
            if (Key.IsValid())
                return PC->InputKey(FInputKeyEventArgs::CreateSimulated(Key, Key.IsAxis1D() ? IE_Axis : (Pressed ? IE_Pressed : IE_Released), Amount));
        }
#endif
    return false;
}
bool AOpeningLobbyCharacter::ProbeFixture(FName Kind)
{
#if WITH_EDITOR
    // Isolated PIE geometry for clearance/long-fall acceptance; it never changes the editor map.
    if (GetWorld() && GetWorld()->WorldType == EWorldType::PIE && (Kind == TEXT("ceiling") || Kind == TEXT("platform")))
    {
        FVector Location = GetActorLocation();
        const bool Platform = Kind == TEXT("platform");
        Location.Z = Platform ? 310.f : 148.f;
        auto* Fixture = GetWorld()->SpawnActor<AStaticMeshActor>(Location, FRotator::ZeroRotator);
        Fixture->SetMobility(EComponentMobility::Movable);
        Fixture->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
        Fixture->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
        Fixture->SetActorScale3D(Platform ? FVector(6,6,.2f) : FVector(3,3,.2f));
        if (Platform) SetActorLocation(Location + FVector(0,0,100), false, nullptr, ETeleportType::TeleportPhysics);
        return true;
    }
#endif
    return false;
}
FString AOpeningLobbyCharacter::GetProbeState() const
{
    const auto* M = GetCharacterMovement();
    UObject* Weapon = ObjectValue(this, TEXT("CurrentWeaponActor"));
    int32 Ammo = -1;
    if (const FIntProperty* P = Weapon ? FindFProperty<FIntProperty>(Weapon->GetClass(), TEXT("AmmoCount")) : nullptr)
        Ammo = P->GetPropertyValue_InContainer(Weapon);
    const UAnimInstance* Anim = GetMesh()->GetAnimInstance();
    const UAnimMontage* Montage = Anim ? Anim->GetCurrentActiveMontage() : nullptr;
    const FString Action = Montage ? Montage->GetName() : FString();
    const auto* JumpInstance = Anim && JumpMontage ? Anim->GetInstanceForMontage(JumpMontage) : nullptr;
    return FString::Printf(TEXT("{\"walking\":%s,\"falling\":%s,\"walkable_floor\":%s,\"floor_distance\":%.3f,\"capsule_radius\":%.3f,\"capsule_half_height\":%.3f,\"fov\":%.3f,\"move_binding_samples\":%d,\"look_binding_samples\":%d,\"animation_time\":%.6f,\"busy\":%s,\"aim_requested\":%s,\"reloading\":%s,\"reload_time\":%.6f,\"montage\":\"%s\",\"running\":%s,\"sprinting\":%s,\"crouched\":%s,\"ammo\":%d,\"fire_mode\":%d,\"grip\":%d,\"jump_starts\":%d,\"landings\":%d,\"frame\":%llu,\"aim_blocked\":%s,\"jump_pending_landing\":%s,\"jump_phase\":%.6f,\"jump_weight\":%.6f,\"jump_active\":%s,\"jump_playing\":%s,\"last_landing_time\":%.6f,\"fast_input_bindings\":%d,\"airborne_fire_held\":%s,\"jump_requests\":%d,\"canceled_jump_requests\":%d,\"jump_request_pending\":%s}"),
        M->IsMovingOnGround()?TEXT("true"):TEXT("false"), M->IsFalling()?TEXT("true"):TEXT("false"),
        M->CurrentFloor.IsWalkableFloor()?TEXT("true"):TEXT("false"), M->CurrentFloor.FloorDist,
        GetCapsuleComponent()->GetScaledCapsuleRadius(), GetCapsuleComponent()->GetScaledCapsuleHalfHeight(),
        FirstPersonCamera->FieldOfView, MoveBindingSamples, LookBindingSamples, AnimationTime,
        Flag(this,TEXT("bIsBusy"))?TEXT("true"):TEXT("false"), Flag(this,TEXT("bIsAiming"))?TEXT("true"):TEXT("false"),
        Action.Contains(TEXT("Reload"))?TEXT("true"):TEXT("false"), Montage?Anim->Montage_GetPosition(Montage):0.f,
        *Action, Flag(this,TEXT("bIsRunning"))?TEXT("true"):TEXT("false"), Flag(this,TEXT("bIsSprinting"))?TEXT("true"):TEXT("false"),
        bIsCrouched?TEXT("true"):TEXT("false"), Ammo, ByteValue(this,TEXT("CurrentFireMode")), ByteValue(this,TEXT("CurrentGrip")), JumpStarts, Landings,
        GFrameCounter, Flag(this,TEXT("bIsAimingBlocked"))?TEXT("true"):TEXT("false"), bJumpPresentation?TEXT("true"):TEXT("false"),
        JumpInstance?JumpInstance->GetPosition():0.f, JumpInstance?JumpInstance->GetWeight():0.f,
        JumpInstance && JumpInstance->IsActive()?TEXT("true"):TEXT("false"), JumpInstance && JumpInstance->IsPlaying()?TEXT("true"):TEXT("false"),
        LastLandingTime, FastInputBindings, bAirborneFireHeld?TEXT("true"):TEXT("false"),
        JumpRequests, CanceledJumpRequests, bJumpRequested?TEXT("true"):TEXT("false"));
}
