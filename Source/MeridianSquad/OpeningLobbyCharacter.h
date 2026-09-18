#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "OpeningLobbyCharacter.generated.h"

class UCameraComponent;
class UAnimMontage;

/** Collision-aware lobby adapter for the supplied rifle gameplay Blueprints. */
UCLASS()
class MERIDIANSQUAD_API AOpeningLobbyCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    AOpeningLobbyCharacter();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void CalcCamera(float DeltaSeconds, FMinimalViewInfo& OutResult) override;
    virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
    virtual void Landed(const FHitResult& Hit) override;
    virtual void OnStartCrouch(float HalfHeightAdjust, float ScaledHalfHeightAdjust) override;
    virtual void OnEndCrouch(float HalfHeightAdjust, float ScaledHalfHeightAdjust) override;

    UFUNCTION(BlueprintCallable, Category="Lobby|Verification")
    bool ProbeKey(FName KeyName, float Amount, bool Pressed);
    UFUNCTION(BlueprintPure, Category="Lobby|Verification")
    FString GetProbeState() const;
    UFUNCTION(BlueprintCallable, Category="Lobby|Verification")
    bool ProbeFixture(FName Kind);

private:
    UPROPERTY(VisibleAnywhere, Category="Camera")
    TObjectPtr<UCameraComponent> FirstPersonCamera;
    UPROPERTY()
    TObjectPtr<UAnimMontage> JumpMontage;
    float AnimationTime = 0.f;
    float CameraHeight = 82.f;
    int32 MoveBindingSamples = 0;
    int32 LookBindingSamples = 0;
    int32 JumpStarts = 0;
    int32 Landings = 0;
    bool bJumpPresentation = false;
    bool bSourceReady = false;
    bool bCrouchRequested = false;
    uint8 ReportedStance = 0;
    void MoveForward(float Value);
    void MoveRight(float Value);
    void LookYaw(float Value);
    void LookPitch(float Value);
    void JumpPressed();
    void JumpReleased();
    void ToggleCameraAnimation();
    void RestoreMeshAnchor();
    void ConfigureAssembly();
    void CallSource(FName Function);
};
