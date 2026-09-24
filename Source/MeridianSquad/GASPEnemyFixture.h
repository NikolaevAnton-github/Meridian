#pragma once

#include "CombatAIMobile.h"

#include "CoreMinimal.h"
#include "PhysicsControlDummy.h"
#include "Components/ActorComponent.h"
#include "MoverSimulationTypes.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "GameFramework/Controller.h"
#include "GASPEnemyFixture.generated.h"

class APawn;
class UMoverComponent;
class UCapsuleComponent;
class UAnimInstance;
class UEnemyCombatComponent;

/** Observed animation state shared by locomotion adapters and combat consumers. */
struct FEnemyRiflePose
{
    bool bValid = false;
    float Layer = 0, Aim = 0, Lean = 0;
};

/** Candidate geometry in feet-relative, horizontal rifle-heading coordinates. */
struct FEnemyCoverAnatomy
{
    bool bRequired = false;
    TArray<FVector> Points; // Head, chest, firing hand, muzzle.
    FVector Pivot = FVector::ZeroVector;
    bool IsValid() const { return Points.Num()==4; }
};

/** Supplies the fixture's control rotation to GASP without player input. */
UCLASS()
class AGASPEnemyCommandController : public AController
{
    GENERATED_BODY()
};

/** Runs the adopted controls after animation, with an optional recovery target blend. */
UCLASS()
class UGASPEnemyPhysicsTick : public UActorComponent
{
    GENERATED_BODY()
public:
    UGASPEnemyPhysicsTick();
    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;
};

UENUM(BlueprintType)
enum class EGASPEnemyAuthority : uint8
{
    Locomotion, Recovery, Falling, Down, GettingUp, Dead
};

UENUM(BlueprintType)
enum class EGASPALSRifleStance : uint8
{
    Relax, Ready, Aim
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
        double ContactTime, double BirthTime, uint64 CombatFrame,
        float FallImpulseMultiplier = 1.f, float DeathImpulseMultiplier = 1.f) override;
    virtual void ApplyExternalDisturbance(FVector Impulse, FVector WorldPoint, FName Bone = "pelvis") override;
    virtual void ProduceInput_Implementation(int32 SimTimeMs, FMoverInputCmdContext& InputCmdResult) override;

    /** Persistent movement command, gated by physical authority. */
    UFUNCTION(BlueprintCallable, Category="Enemy|Movement")
    void SetMovementCommand(FVector WorldDirection, bool bWalk = true);
    UFUNCTION(BlueprintCallable, Category="Enemy|Movement")
    void StopMovementCommand();
    /** Occupancy seam retained for later combat/disarming/gesture work. */
    UFUNCTION(BlueprintCallable, Category="Enemy|Combat")
    void SetHandOccupancy(bool bLeftOccupied, bool bRightOccupied);
    UFUNCTION(BlueprintCallable, Category="Enemy|Combat")
    void SetRifleHeld(bool bHeld);
    UFUNCTION(BlueprintPure, Category="Enemy|Combat")
    bool IsRifleHeld() const { return bRifleHeld && IsValid(Rifle); }
    UFUNCTION(BlueprintPure, Category="Enemy|Combat")
    USkeletalMeshComponent* GetHeldWeapon() const { return IsRifleHeld() ? Rifle.Get() : nullptr; }
    UFUNCTION(BlueprintCallable, Category="Enemy|Rifle")
    void SetRifleStance(EGASPALSRifleStance NewStance);
    UFUNCTION(BlueprintCallable, Category="Enemy|Rifle")
    void SetRifleAimTarget(FVector WorldTarget);
    UFUNCTION(BlueprintCallable, Category="Enemy|Rifle")
    void SetRifleFollowPlayer(bool bFollow);
    UFUNCTION(BlueprintCallable, Category="Enemy|Movement")
    void SetCrouchCommand(bool bCrouch);
    UFUNCTION(BlueprintPure, Category="Enemy|Movement")
    virtual bool IsMovementCrouched() const;
    virtual FVector GetRifleAimDirection() const;
    virtual float GetRifleMovementAlpha() const;
    virtual CombatAI::FireMotion GetFireMotion() const;
    virtual FEnemyRiflePose GetRiflePose() const;
    virtual FEnemyCoverAnatomy GetCoverAnatomy(bool bCrouched) const { return {}; }
    virtual void SetRifleLean(float Degrees, bool bImmediate = false);
    float RifleLeanTarget = 0;
    UFUNCTION(BlueprintPure, Category="Enemy|Movement")
    APawn* GetMovementPawn() const { return Foundation; }

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Enemy")
    TObjectPtr<APawn> Foundation;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Enemy|Combat")
    TObjectPtr<UEnemyCombatComponent> Combat;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Enemy|Combat")
    bool bRifleHeld = true;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Enemy")
    EGASPEnemyAuthority Authority = EGASPEnemyAuthority::Locomotion;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Enemy|Movement")
    bool bWalkCommand = true;
    UPROPERTY(BlueprintReadOnly, Category="Enemy|Combat")
    bool bLeftHandOccupied = false;
    UPROPERTY(BlueprintReadOnly, Category="Enemy|Combat")
    bool bRightHandOccupied = false;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Enemy|Rifle")
    EGASPALSRifleStance RifleStance = EGASPALSRifleStance::Ready;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Enemy|Rifle")
    TObjectPtr<USkeletalMeshComponent> Rifle;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Enemy|Movement")
    bool bCrouchCommand = false;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Enemy|Rifle")
    bool bRifleFollowPlayer = false;

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

protected:
    friend class UGASPEnemyPhysicsTick;
    UPROPERTY() TObjectPtr<UGASPEnemyPhysicsTick> FoundationPhysicsTick;
    UPROPERTY() TObjectPtr<USkeletalMeshComponent> UnusedLegacyBody;
    UPROPERTY() TObjectPtr<UPhysicsControlComponent> UnusedLegacyControls;
    UPROPERTY() TObjectPtr<UMoverComponent> Mover;
    UPROPERTY() TObjectPtr<UCapsuleComponent> Capsule;
    UPROPERTY() TObjectPtr<UAnimInstance> FoundationAnimation;
    UPROPERTY() TObjectPtr<AGASPEnemyCommandController> CommandController;
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
    TMap<FName, FTransform> HandoffPose;
    TMap<int32, FVector> PreFallLegLimits;
    float HandoffSeconds = 0;
    FVector RifleAimTarget = FVector::ZeroVector;
    bool bHasRifleAimTarget = false;
    void UpdateRifleInput();
    void CreateRifle();
    static constexpr float HandoffDuration = .55f;
    void UpdateFoundationPhysics(float DeltaSeconds);
    void UpdateRagdollLegLimits(float DeltaSeconds);
    void BeginPoseHandoff();
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
