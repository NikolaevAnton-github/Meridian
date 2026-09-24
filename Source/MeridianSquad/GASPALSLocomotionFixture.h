#pragma once

#include "CoreMinimal.h"
#include "GASPEnemyFixture.h"
#include "Animation/AnimInstance.h"
#include "GASPALSLocomotionFixture.generated.h"

class ACharacter;
class UCharacterMovementComponent;
class UPhysicsAsset;

UCLASS()
class UGASPALSPostSourceTick : public UActorComponent
{
    GENERATED_BODY()
public:
    UGASPALSPostSourceTick();
    virtual void TickComponent(float DeltaTime,ELevelTick TickType,FActorComponentTickFunction* TickFunction) override;
};

/** Retains source GASPALS graph/class identity. Adds only the existing combat lean. */
UCLASS(Transient, Blueprintable)
class MERIDIANSQUAD_API UGASPALSLocomotionAnimInstance : public UAnimInstance
{
    GENERATED_BODY()
public:
    virtual void NativeUpdateAnimation(float DeltaSeconds) override;
    UPROPERTY(BlueprintReadOnly, Category="Enemy|Locomotion") float MSQLeanDegrees = 0;
    UPROPERTY(BlueprintReadOnly, Category="Enemy|Locomotion") FRotator MSQLeanRotation = FRotator::ZeroRotator;
};

/** Combat shell around the original CMC pawn. Never ticks the legacy balance solver. */
UCLASS()
class MERIDIANSQUAD_API AGASPALSLocomotionFixture : public AGASPEnemyFixture
{
    GENERATED_BODY()
public:
    AGASPALSLocomotionFixture();
    virtual void ResetDummy() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual float ReceiveBullet(int64 ShotId, float Damage, const FVector& Direction, const FHitResult& Hit,
        double ContactTime, double BirthTime, uint64 CombatFrame,
        float FallImpulseMultiplier = 1.f, float DeathImpulseMultiplier = 1.f) override;
    virtual void ApplyExternalDisturbance(FVector Impulse, FVector WorldPoint, FName Bone = "pelvis") override;
    virtual bool IsMovementCrouched() const override;
    virtual float GetRifleMovementAlpha() const override;
    virtual CombatAI::FireMotion GetFireMotion() const override;
    virtual FEnemyRiflePose GetRiflePose() const override;
    virtual void SetRifleLean(float Degrees, bool bImmediate = false) override;
    virtual FString GetDummyState(bool IncludeContacts = true) const override;

private:
    UPROPERTY() TObjectPtr<ACharacter> Character;
    UPROPERTY() TObjectPtr<UCharacterMovementComponent> CharacterMovement;
    UPROPERTY() TObjectPtr<UClass> RifleLayerClass;
    TMap<FName, FName> LocalHitControls;
    TMap<FName, float> LocalHitRemaining;
    float RecentImpact = 0, ImpactAge = 10, RagdollSeconds = 0, SettledSeconds = 0;
    float GettingUpSeconds = 0;
    bool bHadSourceGetUp = false;
    int32 SourceGetUps = 0;
    FString SourceFailure;
    void DestroySourcePawn();
    void ApplySourceCommands();
    void ConfigureHitControls();
    void UpdateLocalHits(float DeltaSeconds);
    FName StartLocalHit(FName HitBone);
    void ClearLocalHits();
    void StartSourceRagdoll(bool bDeath);
    void UpdateSourceRecovery(float DeltaSeconds);
    bool CanSourceGetUp() const;
    void ChangeSourceAuthority(EGASPEnemyAuthority NewAuthority);
};

/** Read-only reflection for exact source graph/default evidence and focused checks. */
UCLASS()
class MERIDIANSQUAD_API UGASPALSLocomotionLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="Enemy|Locomotion|Inspection")
    static FString InspectProperties(UObject* Object);
    UFUNCTION(BlueprintCallable, Category="Enemy|Locomotion|Inspection")
    static FString InspectAnimationStates(UAnimInstance* Animation);
    UFUNCTION(BlueprintCallable, Category="Enemy|Locomotion|Inspection")
    static FString InspectPhysicsAsset(UPhysicsAsset* Asset);
};
