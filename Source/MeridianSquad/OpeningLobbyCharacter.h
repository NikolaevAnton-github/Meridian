#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "OpeningLobbyCharacter.generated.h"

class UCameraComponent;

/** Minimal on-foot camera and movement for the lobby scale review. */
UCLASS()
class MERIDIANSQUAD_API AOpeningLobbyCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    AOpeningLobbyCharacter();
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

    /** PIE-only test input enters the controller's normal key binding pipeline. */
    UFUNCTION(BlueprintCallable, Category="Lobby|Verification")
    bool ProbeKey(FName KeyName, float Amount, bool Pressed);

    UFUNCTION(BlueprintPure, Category="Lobby|Verification")
    FString GetProbeState() const;

private:
    UPROPERTY(VisibleAnywhere, Category="Camera")
    TObjectPtr<UCameraComponent> FirstPersonCamera;
    void MoveForward(float Value);
    void MoveRight(float Value);
    void LookYaw(float Value);
    void LookPitch(float Value);
    int32 MoveBindingSamples = 0;
    int32 LookBindingSamples = 0;
};
