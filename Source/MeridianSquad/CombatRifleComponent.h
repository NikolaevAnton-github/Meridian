#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Animation/AnimNotifies/AnimNotify.h"
#include "CombatRifleComponent.generated.h"

class AOpeningLobbyCharacter;
class ACombatProjectileWorld;
class UEnhancedInputComponent;
class UAnimMontage;
class USkeletalMeshComponent;

/** Exactly one branching notify, on the hands montage, commits a reload transaction. */
UCLASS()
class MERIDIANSQUAD_API UCombatReloadCommitNotify : public UAnimNotify
{
    GENERATED_BODY()
public:
    virtual void BranchingPointNotify(FBranchingPointNotifyPayload& Payload) override;
};

/** Authoritative ammunition and shot path, adapting the retained rifle presentation. */
UCLASS(ClassGroup=(Combat), meta=(BlueprintSpawnableComponent))
class MERIDIANSQUAD_API UCombatRifleComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UCombatRifleComponent();
    void InitializeRifle();
    void BindInput(UEnhancedInputComponent* Input);
    virtual void TickComponent(float Delta, ELevelTick TickType, FActorComponentTickFunction* TickFunction) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Combat|Tuning", meta=(ClampMin="1", ClampMax="30"))
    int32 MagazineCapacity = 30;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Combat|Tuning", meta=(ClampMin="0", ClampMax="9999"))
    int32 InitialReserve = 90;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Combat|Tuning", meta=(ClampMin="0.01"))
    float Damage = 25.f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Combat|Tuning", meta=(ClampMin="1", ClampMax="200000"))
    float BulletSpeed = 30000.f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Combat|Tuning", meta=(ClampMin="0.05"))
    float ShotInterval = .085f;
    UPROPERTY(BlueprintReadOnly, Category="Combat")
    int32 Magazine = 30;
    UPROPERTY(BlueprintReadOnly, Category="Combat")
    int32 Reserve = 90;
    UPROPERTY(BlueprintReadOnly, Category="Combat")
    bool bAutomatic = false;
    UPROPERTY(BlueprintReadOnly, Category="Combat")
    bool bReloading = false;
    UPROPERTY(BlueprintReadOnly, Category="Combat")
    FString StatusText;

    UFUNCTION(BlueprintCallable, Category="Combat")
    bool RequestReload(bool Quick = false);
    UFUNCTION(BlueprintCallable, Category="Combat")
    void CancelReload();
    UFUNCTION(BlueprintPure, Category="Combat|Verification")
    FString GetRifleState() const;
    UFUNCTION(BlueprintCallable, Category="Combat|Verification")
    bool ProbeAmmo(int32 Rounds, int32 Spare);
    UFUNCTION(BlueprintCallable, Category="Combat|Verification")
    void ProbeDuplicateNotify();
    void CommitReload(USkeletalMeshComponent* Mesh, UAnimSequenceBase* Animation, int32 InstanceId);
    void ClearTransientFeedback();

private:
    UPROPERTY(Transient)
    TObjectPtr<AOpeningLobbyCharacter> Character;
    UPROPERTY(Transient)
    TMap<FName, TObjectPtr<UAnimMontage>> ReloadMontages;
    UPROPERTY(Transient)
    TObjectPtr<UAnimMontage> ActiveReload;
    TMap<FName, float> CommitTimes;
    TWeakObjectPtr<ACombatProjectileWorld> Simulation;
    TMap<TWeakObjectPtr<AActor>, double> PropBirths;
    TMap<TWeakObjectPtr<UActorComponent>, double> EffectBirths;
    int32 ReloadInstanceId = INDEX_NONE;
    int32 ShotCount = 0;
    int32 DryFireCount = 0;
    int32 ReloadCount = 0;
    int32 TransferCount = 0;
    int32 CanceledReloadCount = 0;
    int32 TransferredRounds = 0;
    int32 BlockedShotCount = 0;
    int64 LastShotId = 0;
    double NextShotTime = 0.0;
    double NextDryTime = 0.0;
    double LastShotTime = -1.0;
    bool bFireHeld = false;
    bool bDryForPress = false;
    bool bInspectForPress = false;
    bool bReady = false;
    bool bTransferDone = false;
    bool CanAct() const;
    bool PlayPair(UAnimMontage* Hands, UAnimMontage* Weapon);
    UAnimMontage* ConfigMontage(FName Name) const;
    void SyncPresentation();
    void RestoreMagazines();
    void RetireProps();
    bool TryShot();
    void FirePressed();
    void FireReleased();
    void ChangeFireMode();
    void QuickReload();
    void EmergencyReload();
    void InspectMagazine();
    void ReloadTap();
    void ReloadReleased();
    void ResetTargets();
};
