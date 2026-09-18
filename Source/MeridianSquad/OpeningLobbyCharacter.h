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
    virtual void PawnClientRestart() override;
    virtual void CheckJumpInput(float DeltaTime) override;
    virtual void OnJumped_Implementation() override;
    virtual void Landed(const FHitResult& Hit) override;
    virtual void OnStartCrouch(float HalfHeightAdjust, float ScaledHalfHeightAdjust) override;
    virtual void OnEndCrouch(float HalfHeightAdjust, float ScaledHalfHeightAdjust) override;

    UFUNCTION(BlueprintCallable, Category="Lobby|Verification")
    bool ProbeKey(FName KeyName, float Amount, bool Pressed);
    UFUNCTION(BlueprintPure, Category="Lobby|Verification")
    FString GetProbeState() const;
    UFUNCTION(BlueprintCallable, Category="Lobby|Verification")
    bool ProbeFixture(FName Kind);

    /** Keep the compatible base through a fast jump and its weapon/landing recovery. */
    bool NeedsOrdinaryJumpBase() const;

private:
    UPROPERTY(VisibleAnywhere, Category="Camera")
    TObjectPtr<UCameraComponent> FirstPersonCamera;
    UPROPERTY()
    TObjectPtr<UAnimMontage> JumpMontage;
    TWeakObjectPtr<UInputComponent> AdaptedInputComponent;
    float AnimationTime = 0.f;
    float CameraHeight = 82.f;
    float JumpPlanarSpeed = 0.f;
    float LastLandingTime = -1.f;
    int32 MoveBindingSamples = 0;
    int32 LookBindingSamples = 0;
    int32 JumpStarts = 0;
    int32 JumpRequests = 0;
    int32 CanceledJumpRequests = 0;
    int32 Landings = 0;
    int32 FastInputBindings = 0;
    bool bJumpPresentation = false;
    bool bJumpRequested = false;
    bool bRequestedFastJumpBase = false;
    bool bProtectJumpPose = false;
    bool bAirborneFireHeld = false;
    bool bRunInputTriggered = false;
    bool bSprintInputTriggered = false;
    bool bSourceReady = false;
    bool bCrouchRequested = false;
    uint8 ReportedStance = 0;
    void MoveForward(float Value);
    void MoveRight(float Value);
    void LookYaw(float Value);
    void LookPitch(float Value);
    void JumpPressed();
    void JumpReleased();
    void CancelPendingJump();
    void RunTriggered();
    void RunReleased();
    void SprintTriggered();
    void SprintReleased();
    void FireStarted();
    void FireReleased();
    bool CanStartFastMovement() const;
    void UpdateFastMovement();
    void ToggleCameraAnimation();
    void RestoreMeshAnchor();
    void ConfigureAssembly();
    void CallSource(FName Function);
};
