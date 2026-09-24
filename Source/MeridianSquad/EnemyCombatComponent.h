#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "CombatAIObservation.h"
#include "CombatAIAction.h"
#include "CombatAITactics.h"
#include "CombatAIMobile.h"
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
    // Retained floor is 6080 x 2480 cm (~6567 cm diagonal).
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float SightRange = 7000.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float SightHalfAngle = 100.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float SightInterval = .12f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float AcquireSeconds = .08f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float AttackRange = 5500.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float PreferredRange = 2800.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float AdvanceStep = 450.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float AimSeconds = .10f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float AimToleranceDegrees = 6.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float ShotInterval = .18f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 BurstSize = 3;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float BurstPause = .45f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 MagazineCapacity = 12;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float ReloadSeconds = 2.6f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float BulletSpeed = 14000.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float BulletDamage = 10.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float SpreadDegrees = .6f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float MovingSpreadDegrees = 1.6f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float CombatStrafeDistance = 180.f;
    // Retry only after a blocked corridor; successful movement has no dwell.
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float CombatMoveRest = .25f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float CoverLeanDegrees = 32.f;
    // Local inspection dwell, never an encounter/memory expiry.
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float SearchSeconds = 2.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float SearchRadius = 360.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float TacticalRadius = 650.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float TacticalReassessSeconds = 2.5f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float TacticalCommitSeconds = 4.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float TacticalProbeSeconds = 6.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float TacticalSwitchMargin = 10.f;
    // Room diagonal / retained 375 cm/s run, plus bounded planning/turning time.
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float PursuitSeconds = 24.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float ReturnSeconds = 12.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float RetryCooldown = 5.f;
    // Home (-950,-320) is <=4285 cm from every retained floor corner.
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float NavigationRadius = 4500.f;
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
    void ReceiveStimulus(const CombatAI::Stimulus& Record);
    // Future evidence producer only; the current player has no health contract.
    // Generation, known identity, provenance and a <=5s lifetime are mandatory.
    void ReceiveTargetHealth(const CombatAI::HealthKnowledge& Evidence);

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
    CombatAI::EncounterMemory Memory;
    CombatAI::Knowledge Knowledge;
    uint64 IntentEvidenceId = 0;
    bool bEvidencePending = false;
    double NextEvidenceResponse = 0;
    void ApplyEvidenceIntent(double Now);
    void AppendSensesStatus(const TSharedRef<FJsonObject>& Root) const;
    CombatAI::ActionRuntime Action;
    CombatAI::ActionRuntime MoveAction;
    CombatAI::ActionToken PathRequest;
    CombatAI::ActionToken ReloadRequest;
    CombatAI::DestinationBackoff MoveBackoff, WeaponBackoff;
    FVector SearchGoal = FVector::ZeroVector;
    FVector SearchAnchor = FVector::ZeroVector;
    FVector SearchForward = FVector::ForwardVector;
    FVector SearchLook = FVector::ZeroVector;
    CombatAI::MovePurpose MovementPurpose = CombatAI::MovePurpose::Pursuit;
    bool bRequestedWalk = true;
    double StateStarted = 0;
    double NextSight = 0;
    double NextShot = 0;
    CombatAI::ResponseGates Gates;
    CombatAI::ContactKind Contact = CombatAI::ContactKind::None;
    double ContactAt = 0, ContactDecisionAt = 0;
    double NextRepath = 0;
    double LastProgress = 0;
    double FlashUntil = 0;
    double ObstructedSince = -1;
    double ObstructionValidUntil = 0;
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
    TUniquePtr<CombatAI::TraceRing> DecisionTrace;
    void RecordTrace(CombatAI::Event Kind, const TCHAR* Why);
    void RecordPath(CombatAI::PathOutcome Outcome, const TCHAR* Why);
    void AppendObservationStatus(const TSharedRef<FJsonObject>& Root) const;
    bool TryObservePlayer();
    UPROPERTY() TObjectPtr<USoundBase> ShotSound;
    UPROPERTY() TObjectPtr<UNiagaraSystem> MuzzleEffect;
    void ChangeState(EEnemyCombatState NewState, const TCHAR* Why);
    void ClearIntent(CombatAI::ActionFailure Why = CombatAI::ActionFailure::Replaced);
    CombatAI::ActionToken EnsureAction(CombatAI::ActionKind Kind, double Now);
    CombatAI::ActionToken EnsureMoveAction(double Now);
    bool FinishMoveAction(CombatAI::ActionStatus Outcome, CombatAI::ActionFailure Why);
    void ClearMovement(CombatAI::ActionFailure Why = CombatAI::ActionFailure::Replaced);
    void AdvanceMobile(double Now, double Distance);
    bool AdvanceReload(double Now);
    CombatAI::MobilePhase MobilePhase = CombatAI::MobilePhase::None;
    FVector MobileGoal = FVector::ZeroVector;
    double MobileStarted = 0, NextMobileAt = 0;
    int32 MobileSerial = 0;
    mutable CombatAI::FireGate LastFireGate = CombatAI::FireGate::Contact;
    bool FinishAction(CombatAI::ActionToken Request, CombatAI::ActionStatus Outcome, CombatAI::ActionFailure Why);
    bool ObservePlayer();
    bool CanShoot(FVector& Muzzle, FVector& Direction, bool& bObstructed) const;
    bool MuzzleCorridorBlocked(const FVector& Muzzle) const;
    void RefreshObstruction(double Now, double Distance);
    bool Fire(double Now, CombatAI::ActionToken Request);
    void BeginSearch(const TCHAR* Why, bool bRestart = true);
    void AdvanceSearch(double Now);
    struct FCoverOption
    {
        FVector Anchor = FVector::ZeroVector, Pose = FVector::ZeroVector;
        CombatAI::CoverFeatures Features;
        double Score = CombatAI::InvalidPositionScore;
    };
    struct FTacticalPosition
    {
        FVector Ground = FVector::ZeroVector;
        CombatAI::PositionFeatures Features;
        CombatAI::PositionRating Rating;
        FVector FacingBasis = FVector::ForwardVector;
        TArray<FVector> Route;
        FBox Obstacle = FBox(ForceInit);
        bool bCrouched = false;
        uint64 EvidenceId = 0;
        std::array<FCoverOption,3> CoverOptions{};
    };
    CombatAI::TacticalContext Context;
    CombatAI::HealthKnowledge TargetHealthEvidence;
    CombatAI::AllySummary AllyRoster;
    CombatAI::RangeIntent RangeIntent = CombatAI::RangeIntent::NoWeapon;
    CombatAI::CoverPhase CoverPhase = CombatAI::CoverPhase::None;
    CombatAI::CoverGate CoverGate = CombatAI::CoverGate::None;
    CombatAI::ActionToken CoverOwner;
    FCoverOption CoverPlan;
    std::array<CombatAI::PositionHistory,3> CoverFailures;
    FVector CoverThreatGround = FVector::ZeroVector, CoverThreatAim = FVector::ZeroVector;
    double CoverStarted = 0, CoverPhaseAt = 0, CoverValidateAt = 0, NextAllyRefresh = 0;
    double NextCoverScan = 0, CoverScanAt = 0, NextAdvanceAt = 0;
    bool bCoverScan = false, bCoverScanReady = false, bEndCoverAfterReturn = false;
    int32 CoverBursts = 0;
    CombatAI::WeaponProfile WeaponProfile() const;
    void RefreshTacticalContext(double Now);
    void ResetCover(bool bHistory = false);
    void AdvanceCoverScan(double Now);
    void ChooseCover(double Now);
    void AssessCoverOptions(FTacticalPosition& Position);
    FCoverOption AssessCoverOption(FVector Anchor, FVector Pose, CombatAI::CoverSide Side);
    bool CoverProtected(FVector Ground);
    bool RefreshCoverThreat(double Now);
    bool CoverLane(FVector Ground);
    bool CoverAnatomyAt(FVector Ground, bool bCrouched, TArray<FVector>& Points, FVector& Pivot) const;
    bool CoverCapsule(FVector Ground, bool bCrouched);
    bool CoverWalk(FVector From, FVector To);
    void SetCoverPhase(CombatAI::CoverPhase Phase, double Now, const TCHAR* Why);
    void ReturnToCover(double Now, const TCHAR* Why, bool bEnd, bool bFailed);
    void FailCoverReturn(double Now, const TCHAR* Why);
    bool AdvanceCover(double Now);
    bool AdvanceLeanCover(double Now);
    bool LeanProtected(FVector Ground);
    bool LeanProposal(FVector Ground, float Degrees);
    bool LeanSweep(const TArray<FVector>& From, const TArray<FVector>& To) const;
    bool CaptureLeanPose();
    bool AchievedLeanClear() const;
    bool LeanReturned() const;
    TArray<FVector> LeanPoints() const;
    TArray<FVector> LeanNeutral;
    FVector LeanPivot = FVector::ZeroVector, LeanAxis = FVector::ForwardVector;
    bool bLeanPoseCaptured = false;
    float LeanSign() const;
    bool AdvanceWeapon(double Now, bool bFromCover);
    bool StartCoverMove(FVector Goal, double Now);
    bool PoseCapsuleSize(bool bCrouched, float& Radius, float& HalfHeight) const;
    CombatAI::TacticalAssignment Assignment;
    CombatAI::ActionToken ScanRequest;
    CombatAI::TacticalPhase TacticalPhase = CombatAI::TacticalPhase::None;
    CombatAI::PositionHistory RejectedPositions, VisitedPositions;
    TArray<FTacticalPosition> TacticalCandidates;
    FTacticalPosition HeldPosition, SelectedPosition;
    FVector ScanOrigin = FVector::ZeroVector;
    bool bTacticalScan = false, bHeldPosition = false, bSelectedPosition = false;
    int32 SurfaceIndex = 0, CandidateIndex = 0, LookSector = -1;
    CombatAI::TransferBudget Transfers;
    unsigned ViewedSectors = 0;
    int32 TacticalQueryCount = 0, TacticalPeakQueries = 0, TacticalRejected = 0;
    std::array<int32, static_cast<size_t>(CombatAI::PositionRejection::Count)> RejectionCounts{};
    double ScanStartedAt = 0, NextTacticalWork = 0, NextTacticalScan = 0;
    double HoldStartedAt = 0, NextHoldValidation = 0, NextLookAt = 0, TacticalMoveStartedAt = 0;
    FString TacticalReason;
    void ResetTactics(bool bClearHistory = true);
    void BeginTacticalScan(double Now);
    void AdvanceTacticalScan(double Now);
    void ChooseTacticalPosition(double Now);
    void RejectTacticalPosition(const FVector& Ground, CombatAI::PositionRejection Why, double Now);
    void HoldTacticalPosition(double Now);
    void SetObservationFacing(double Now);
    void AddTacticalCandidate(FVector Ground, FBox Obstacle = FBox(ForceInit));
    FTacticalPosition AssessTacticalPosition(FVector Reference, FVector From, bool bCheckRoute, bool bCrouched, FBox Obstacle = FBox(ForceInit));
    bool TacticalRoute(FVector From, FVector To, const FBox& Obstacle, TArray<FVector>& Route, double& Length, int32 Stance = -1);
    bool TacticalGround(FVector Reference, FVector& Ground, CombatAI::PositionRejection& Failure, int32 Stance = -1);
    bool TacticalWalk(FVector From, FVector To, int32 Stance = -1);
    bool TacticalTrace(FVector From, FVector To, FHitResult& Hit, ECollisionChannel Response = ECC_Visibility);
    FVector TacticalDirection(int32 Sector) const;
    void FailTactic(const TCHAR* Why, CombatAI::ActionFailure Failure, bool bWeapon);
    bool FollowPath(FVector Goal, float Acceptance, double Now, CombatAI::MovePurpose Purpose);
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
