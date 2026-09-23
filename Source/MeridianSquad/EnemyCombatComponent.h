#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "CombatAIObservation.h"
#include "EnemyCombatComponent.generated.h"

class AGASPEnemyFixture;
class USoundBase;
class UNiagaraSystem;
class FJsonObject;

UENUM(BlueprintType)
enum class EEnemyCombatState : uint8
{
    Disabled, Idle, Acquire, Pursue, Aim, Burst, Reload, Search, Return, Blocked, Recovery, Dead
};

/** Small, single-opponent policy. Distances are cm and times are world seconds. */
USTRUCT(BlueprintType)
struct FEnemyCombatTuning
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float SightRange = 2400.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float SightHalfAngle = 100.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float SightInterval = .12f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float AcquireSeconds = .65f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float AttackRange = 1000.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float AimSeconds = .65f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float AimToleranceDegrees = 6.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float ShotInterval = .18f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 BurstSize = 3;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float BurstPause = 1.1f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 MagazineCapacity = 12;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float ReloadSeconds = 2.6f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float BulletSpeed = 14000.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float BulletDamage = 10.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float SpreadDegrees = .6f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float SearchSeconds = 4.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float PursuitSeconds = 12.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float ReturnSeconds = 12.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float RetryCooldown = 5.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float NavigationRadius = 2800.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float NavigationCell = 80.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float MaxStepHeight = 30.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float MaxSlopeDegrees = 40.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float RepathSeconds = .8f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 MaxPathExpansions = 1200;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float StuckSeconds = 1.8f;
};

/** Decisions feed the adopted Mover command. Physical recovery keeps sole authority. */
UCLASS(ClassGroup=(Combat), meta=(BlueprintSpawnableComponent))
class MERIDIANSQUAD_API UEnemyCombatComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UEnemyCombatComponent();
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Enemy|Combat") FEnemyCombatTuning Tuning;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Enemy|Combat") bool bEnabled = false;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Enemy|Combat") EEnemyCombatState State = EEnemyCombatState::Disabled;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Enemy|Combat") int32 Magazine = 12;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Enemy|Combat") int32 Shots = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Enemy|Combat") int32 Reloads = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Enemy|Combat") int32 Acquisitions = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Enemy|Combat") int32 PathFailures = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Enemy|Combat") bool bTargetVisible = false;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Enemy|Combat") FString Reason;
    UFUNCTION(BlueprintCallable, Category="Enemy|Combat") void SetEnabled(bool bEnable);
    UFUNCTION(BlueprintPure, Category="Enemy|Combat") FString GetCombatState() const;
    FString GetLabel() const;
    void ResetCombat(FVector HomeGround, FRotator HomeRotation);
    void AdvanceCombat(float DeltaSeconds);
    void SuspendForPhysics(bool bDead);
    void StopCombat();
    // Set once from the explicit placement slot before deferred FinishSpawning.
    void SetStableSpawnIndex(uint32 Index) { StableSpawnIndex = Index; }
    CombatAI::InputSnapshot CaptureDecisionInput() const;

private:
    AGASPEnemyFixture* Enemy() const;
    TWeakObjectPtr<APawn> Target;
    FVector Home = FVector::ZeroVector;
    FRotator HomeFacing = FRotator::ZeroRotator;
    FVector LastKnownGround = FVector::ZeroVector;
    FVector LastKnownAim = FVector::ZeroVector;
    FVector PathGoal = FVector::ZeroVector;
    FVector ProgressPosition = FVector::ZeroVector;
    TArray<FVector> Path;
    int32 PathIndex = 0;
    int32 FailedAttempts = 0;
    int32 BurstRemaining = 0;
    int32 PathPlans = 0;
    int32 LastPathExpanded = 0;
    int32 ObstructionAttempts = 0;
    int64 LastShotId = 0;
    bool bHasMemory = false;
    double LastSeen = -1000;
    double StateStarted = 0;
    double NextSight = 0;
    double NextShot = 0;
    double ReadyAt = 0;
    double IgnoreSightUntil = 0;
    double NextRepath = 0;
    double LastProgress = 0;
    double FlashUntil = 0;
    double ObstructedSince = -1;
    FVector LastMuzzle = FVector::ZeroVector;
    FVector LastBarrel = FVector::ForwardVector;
    FRandomStream Spread;
    uint32 StableSpawnIndex = 0;
    uint32 EncounterSeed = CombatAI::DefaultEncounterSeed;
    uint32 Seed = 0;
    uint64 EncounterGeneration = 0;
    uint64 SightEventId = 0;
    double CaptureDeltaSeconds = 0;
    CombatAI::PathOutcome LastPathOutcome = CombatAI::PathOutcome::None;
    CombatAI::TraceRing DecisionTrace;
    void RecordTrace(CombatAI::Event Kind, const TCHAR* Why);
    void RecordPath(CombatAI::PathOutcome Outcome, const TCHAR* Why);
    void AppendObservationStatus(const TSharedRef<FJsonObject>& Root) const;
    bool TryObservePlayer();
    UPROPERTY() TObjectPtr<USoundBase> ShotSound;
    UPROPERTY() TObjectPtr<UNiagaraSystem> MuzzleEffect;
    void ChangeState(EEnemyCombatState NewState, const TCHAR* Why);
    void ClearIntent();
    bool ObservePlayer();
    bool CanShoot(FVector& Muzzle, FVector& Direction, bool& bObstructed) const;
    bool Fire(double Now);
    void StartReturn(const TCHAR* Why);
    bool FollowPath(FVector Goal, float Acceptance, double Now);
    bool PlanPath(FVector Goal, float Acceptance);
    void ContinuePath();
    bool GroundPoint(FVector Reference, FVector& Ground, const FCollisionQueryParams& Query) const;
    bool WalkSegment(FVector Start, FVector End, const FCollisionQueryParams& Query) const;
    FVector Feet() const;
    void CapsuleSize(float& Radius, float& HalfHeight) const;
    void NavigationQuery(FCollisionQueryParams& Query) const;
    struct FPathNode
    {
        FIntPoint Cell;
        FVector Ground;
        float Cost = TNumericLimits<float>::Max();
        int32 Parent = INDEX_NONE;
        bool bClosed = false;
        bool bWalkable = false;
    };
    TArray<FPathNode> Nodes;
    TArray<int32> OpenNodes;
    TMap<FIntPoint, int32> CellNodes;
    bool bPlanning = false;
    bool bPlanFailed = false;
    float PathAcceptance = 80;
    float PathCell = 80;
    double PlanStarted = 0;
};
