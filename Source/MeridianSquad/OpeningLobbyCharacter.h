#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "OpeningLobbyCharacter.generated.h"

class UCameraComponent;
class UAnimSequence;
class UStaticMeshComponent;
struct FPurchasedArmsAnimProxy;

/** Minimal purchased-arms walkthrough; no vendor gameplay framework. */
UCLASS()
class MERIDIANSQUAD_API AOpeningLobbyCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    AOpeningLobbyCharacter();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void CalcCamera(float DeltaSeconds, FMinimalViewInfo& OutResult) override;
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

    /** PIE-only test input enters the controller's normal key binding pipeline. */
    UFUNCTION(BlueprintCallable, Category="Lobby|Verification")
    bool ProbeKey(FName KeyName, float Amount, bool Pressed);

    UFUNCTION(BlueprintPure, Category="Lobby|Verification")
    FString GetProbeState() const;

private:
    friend struct FPurchasedArmsAnimProxy;
    UPROPERTY(VisibleAnywhere, Category="Camera")
    TObjectPtr<UCameraComponent> FirstPersonCamera;
    UPROPERTY(VisibleAnywhere, Category="Presentation")
    TObjectPtr<USkeletalMeshComponent> Rifle;
    UPROPERTY(VisibleAnywhere, Category="Presentation")
    TObjectPtr<USkeletalMeshComponent> MainMagazine;
    UPROPERTY(VisibleAnywhere, Category="Presentation")
    TObjectPtr<USkeletalMeshComponent> ReserveMagazine;
    UPROPERTY(VisibleAnywhere, Category="Presentation")
    TObjectPtr<UStaticMeshComponent> Handguard;
    UPROPERTY(VisibleAnywhere, Category="Presentation")
    TObjectPtr<UStaticMeshComponent> RearSight;
    UPROPERTY(VisibleAnywhere, Category="Presentation")
    TObjectPtr<UStaticMeshComponent> FrontSight;
    // Idle, forward, back, left, right, then the same five aimed clips.
    UPROPERTY()
    TArray<TObjectPtr<UAnimSequence>> LocomotionClips;
    UPROPERTY()
    TArray<TObjectPtr<UAnimSequence>> ReloadClips;
    UPROPERTY()
    TArray<TObjectPtr<UAnimSequence>> RifleReloadClips;
    UPROPERTY()
    TArray<TObjectPtr<UAnimSequence>> BasePoses;
    bool bAimRequested = false;
    bool bReloading = false;
    float AimAlpha = 0.f;
    float ReloadAimAlpha = 0.f;
    float ReloadTime = 0.f;
    float ReloadDuration = 0.f;
    float AnimationTime = 0.f;
    FVector2D MoveBlend = FVector2D::ZeroVector;
    int32 ReloadStarts = 0;
    int32 ReloadCompletions = 0;
    void AimPressed();
    void AimReleased();
    void Reload();
    void MoveForward(float Value);
    void MoveRight(float Value);
    void LookYaw(float Value);
    void LookPitch(float Value);
    int32 MoveBindingSamples = 0;
    int32 LookBindingSamples = 0;
};
