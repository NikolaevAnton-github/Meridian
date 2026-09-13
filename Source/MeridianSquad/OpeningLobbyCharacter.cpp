#include "OpeningLobbyCharacter.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/InputComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputKeyEventArgs.h"

AOpeningLobbyCharacter::AOpeningLobbyCharacter()
{
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
}

void AOpeningLobbyCharacter::SetupPlayerInputComponent(UInputComponent* Input)
{
    Super::SetupPlayerInputComponent(Input);
    Input->BindAxis(TEXT("LobbyForward"), this, &AOpeningLobbyCharacter::MoveForward);
    Input->BindAxis(TEXT("LobbyRight"), this, &AOpeningLobbyCharacter::MoveRight);
    Input->BindAxis(TEXT("LobbyYaw"), this, &AOpeningLobbyCharacter::LookYaw);
    Input->BindAxis(TEXT("LobbyPitch"), this, &AOpeningLobbyCharacter::LookPitch);
    Input->BindAction(TEXT("LobbyJump"), IE_Pressed, this, &ACharacter::Jump);
    Input->BindAction(TEXT("LobbyJump"), IE_Released, this, &ACharacter::StopJumping);
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
            if (Key == EKeys::MouseX || Key == EKeys::MouseY || Key == EKeys::W || Key == EKeys::A || Key == EKeys::S || Key == EKeys::D || Key == EKeys::SpaceBar)
                return PC->InputKey(FInputKeyEventArgs::CreateSimulated(Key, Key.IsAxis1D() ? IE_Axis : (Pressed ? IE_Pressed : IE_Released), Amount));
        }
    }
#endif
    return false;
}

FString AOpeningLobbyCharacter::GetProbeState() const
{
    const UCharacterMovementComponent* M = GetCharacterMovement();
    return FString::Printf(TEXT("{\"walking\":%s,\"falling\":%s,\"gravity_scale\":%.3f,\"gravity_z\":%.3f,\"walkable_floor\":%s,\"floor_distance\":%.3f,\"capsule_radius\":%.3f,\"capsule_half_height\":%.3f,\"eye_above_capsule_bottom\":%.3f,\"fov\":%.3f,\"move_binding_samples\":%d,\"look_binding_samples\":%d}"),
        M->IsMovingOnGround() ? TEXT("true") : TEXT("false"), M->IsFalling() ? TEXT("true") : TEXT("false"), M->GravityScale, M->GetGravityZ(),
        M->CurrentFloor.IsWalkableFloor() ? TEXT("true") : TEXT("false"), M->CurrentFloor.FloorDist,
        GetCapsuleComponent()->GetScaledCapsuleRadius(), GetCapsuleComponent()->GetScaledCapsuleHalfHeight(),
        FirstPersonCamera->GetRelativeLocation().Z + GetCapsuleComponent()->GetScaledCapsuleHalfHeight(), FirstPersonCamera->FieldOfView, MoveBindingSamples, LookBindingSamples);
}
