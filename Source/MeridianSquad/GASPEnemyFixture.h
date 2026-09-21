#pragma once

#include "CoreMinimal.h"
#include "PhysicsControlDummy.h"
#include "MoverSimulationTypes.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "GASPEnemyFixture.generated.h"

class APawn;
class UMoverComponent;
class UCapsuleComponent;
class UAnimInstance;

UENUM(BlueprintType)
enum class EGASPEnemyAuthority : uint8
{
    Locomotion, Recovery, Falling, Down, GettingUp, Dead
};

/** Logical combat fixture. Its adopted GASP pawn owns the visible mesh, capsule and Mover.
 * Reuses the retained recovery solver without a second visible mannequin or hit path. */
UCLASS()
class MERIDIANSQUAD_API AGASPEnemyFixture : public APhysicsControlDummy, public IMoverInputProducerInterface
{
    GENERATED_BODY()
public:
    AGASPEnemyFixture();
    virtual void Tick(float DeltaSeconds) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void ResetDummy() override;
    virtual FString GetDummyState(bool IncludeContacts = true) const override;
    virtual float ReceiveBullet(int64 ShotId, float Damage, const FVector& Direction, const FHitResult& Hit,
        double ContactTime, double BirthTime, uint64 CombatFrame) override;
    virtual void ApplyExternalDisturbance(FVector Impulse, FVector WorldPoint, FName Bone = "pelvis") override;
    virtual void ProduceInput_Implementation(int32 SimTimeMs, FMoverInputCmdContext& InputCmdResult) override;

    /** Persistent command, gated by physical authority. No perception or autonomous decision. */
    UFUNCTION(BlueprintCallable, Category="Enemy|Movement")
    void SetMovementCommand(FVector WorldDirection, bool bWalk = true);
    UFUNCTION(BlueprintCallable, Category="Enemy|Movement")
    void StopMovementCommand();
    /** Extension point for MSQ-70/99/100; no weapon is created or fired here. */
    UFUNCTION(BlueprintCallable, Category="Enemy|Combat")
    void SetHandOccupancy(bool bLeftOccupied, bool bRightOccupied);
    UFUNCTION(BlueprintPure, Category="Enemy|Movement")
    APawn* GetMovementPawn() const { return Foundation; }

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Enemy")
    TObjectPtr<APawn> Foundation;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Enemy")
    EGASPEnemyAuthority Authority = EGASPEnemyAuthority::Locomotion;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Enemy|Movement")
    bool bWalkCommand = true;
    UPROPERTY(BlueprintReadOnly, Category="Enemy|Combat")
    bool bLeftHandOccupied = false;
    UPROPERTY(BlueprintReadOnly, Category="Enemy|Combat")
    bool bRightHandOccupied = false;

    FVector GetMovementIntent() const;
    FTransform GetRagdollAnchor(const FTransform& SampleAnchor) const;
    bool AllowsSamplePhysics() const;
    void EnforceSampleLimits();
    static AGASPEnemyFixture* FromFoundation(const AActor* Actor);

protected:
    virtual void UpdateBalance(float DeltaSeconds) override;
    virtual void RegisterDisturbance(FName Bone, const FVector& Impulse, float Amount) override;
    virtual void EnterFall(const TCHAR* Reason) override;
    virtual bool BeginGetUp() override;
    virtual void BoundRecoveryDrives(float DeltaSeconds) override;
    virtual void SetVisibleAnimationPose() override;
    virtual FVector StepJointLimits(FName Bone) const override;
    virtual void PrepareStepLanding(FName Bone, FTransform& Target) const override;

private:
    UPROPERTY() TObjectPtr<USkeletalMeshComponent> UnusedLegacyBody;
    UPROPERTY() TObjectPtr<UPhysicsControlComponent> UnusedLegacyControls;
    UPROPERTY() TObjectPtr<UMoverComponent> Mover;
    UPROPERTY() TObjectPtr<UCapsuleComponent> Capsule;
    UPROPERTY() TObjectPtr<UAnimInstance> FoundationAnimation;
    UPROPERTY() TArray<TObjectPtr<UObject>> FoundationInputProducers;
    FVector MovementCommand = FVector::ZeroVector;
    FVector StandingPelvisOffset = FVector::ZeroVector;
    TArray<FName> SampleControls;
    bool bAdopted = false;
    bool bSampleTransition = false;
    bool bHadGetUpMontage = false;
    bool bPendingGetUp = false;
    float AdoptionSeconds = 0;
    float GetUpSeconds = 0;
    int32 AuthorityChanges = 0;
    FString LastSelectedMontage;
    TMap<FString,int32> ArmTrunkContacts;
    float PeakArmTrunkImpulse = 0;
    UFUNCTION()
    void OnFoundationContact(UPrimitiveComponent* HitComponent, AActor* OtherActor,
        UPrimitiveComponent* OtherComponent, FVector NormalImpulse, const FHitResult& Hit);
    bool AdoptFoundation();
    void CaptureStandingBasis(bool bNeutral);
    void TakeRecoveryAuthority();
    void ReleaseRecoveryAuthority();
    void DisableSampleControls();
    void BoundSampleControls();
    void SetPoseOverride(bool bActive, const FPoseSnapshot* Snapshot = nullptr);
    void CallFoundation(FName Function, const TMap<FString,FString>& Arguments = {});
    void SetSourceProfile(FName Profile);
    void SetAuthority(EGASPEnemyAuthority NewAuthority);
};

/** Explicit seams used by the task-scoped copies of the GASP graphs. */
UCLASS()
class MERIDIANSQUAD_API UGASPEnemyFoundationLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintPure, Category="Enemy|GASP")
    static bool AllowSamplePhysics(AActor* Foundation);
    UFUNCTION(BlueprintPure, Category="Enemy|GASP")
    static bool AllowSampleGetUp(AActor* Foundation);
    UFUNCTION(BlueprintPure, Category="Enemy|GASP")
    static FVector CommandedMovement(AActor* Foundation);
    UFUNCTION(BlueprintPure, Category="Enemy|GASP")
    static bool CommandedWalk(AActor* Foundation);
    UFUNCTION(BlueprintPure, Category="Enemy|GASP")
    static FTransform RagdollAnchor(AActor* Foundation, const FTransform& SampleAnchor);
    UFUNCTION(BlueprintCallable, Category="Enemy|GASP")
    static void EnforceSampleLimits(AActor* Foundation);
};
