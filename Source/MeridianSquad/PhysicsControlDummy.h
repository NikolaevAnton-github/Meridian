#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Animation/PoseSnapshot.h"
#include "PhysicsControlDummy.generated.h"

class UPhysicsControlComponent;
class USkeletalMeshComponent;
class UTextRenderComponent;
class UAnimSequence;
class UPrimitiveComponent;
class FJsonValue;
class FJsonObject;

/** Primitive geometry from PA_Mannequin, transformed by the actual Chaos body. */
struct FDummyShape
{
    FName Bone;
    FTransform Transform;
    FVector Extent = FVector::ZeroVector;
    float Radius = 0;
    float HalfHeight = 0;
    bool bBox = false;
};

struct FDummyPose
{
    TArray<FDummyShape> Shapes;
    uint64 Epoch = 0;
};

UENUM(BlueprintType)
enum class EDummyBalanceState : uint8
{
    Standing, LosingBalance, Falling, Down, GettingUp, Dead, Stepping
};

/** Physical mannequin with support-gated pose assistance and interruptible recovery. */
UCLASS()
class MERIDIANSQUAD_API APhysicsControlDummy : public AActor
{
    GENERATED_BODY()
public:
    APhysicsControlDummy();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Physics Dummy")
    TObjectPtr<USkeletalMeshComponent> Body;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Physics Dummy")
    TObjectPtr<UPhysicsControlComponent> PhysicsControl;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float MaxHealth = 100.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float LimbAngularStrength = 8.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float PoseLinearStrength = 4.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float TrunkAngularStrength = 8.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float SupportStrength = 20.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float DriveDampingRatio = 1.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float HitRecoverySeconds = .3f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float BulletImpulse = 900.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float MaxImpulseVelocity = 180.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning", meta=(ClampMin="0", ClampMax="1"))
    float UpperBodyFallRotationRatio = .75f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning", meta=(ClampMin="0", ClampMax="400"))
    float UpperBodyFallLegSpeed = 300.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float HitStrengthMultiplier = .2f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float HitHoldSeconds = 0.f;
    UPROPERTY(BlueprintReadOnly, Category="Physics Dummy")
    int32 ReactionProfile = 0;
    /** Configure before FinishSpawning; profile zero retains the historical probe default. */
    void ConfigureReactionProfile(int32 Number);
    UPROPERTY(BlueprintReadOnly, Category="Physics Dummy")
    float Health = 100.f;
    UPROPERTY(BlueprintReadOnly, Category="Physics Dummy")
    int32 Deaths = 0;
    UPROPERTY(BlueprintReadOnly, Category="Physics Dummy")
    int32 PhysicalHits = 0;

    UPROPERTY(BlueprintReadOnly, Category="Physics Dummy|Balance")
    EDummyBalanceState BalanceState = EDummyBalanceState::Standing;
    UPROPERTY(BlueprintReadOnly, Category="Physics Dummy|Balance")
    float Instability = 0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Balance")
    float InstabilityPerHit = .42f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Balance")
    float InstabilityRecoveryRate = .30f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Balance")
    float RecoveryDelay = .75f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Balance")
    float LegDisableSeconds = 2.5f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Balance")
    float SupportReach = 2.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Balance")
    float FallThreshold = 1.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Balance")
    float MaxLeanDegrees = 48.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Balance")
    float SettleSeconds = .85f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Balance")
    float GetUpBlendSeconds = .75f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Stepping")
    float StepTriggerInstability = .32f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Stepping")
    float StepLength = 30.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Stepping")
    float StepMaxReach = 40.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Stepping")
    float StepLift = 11.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Stepping")
    float StepTransferSeconds = .18f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Stepping")
    float StepSwingSeconds = .42f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Stepping")
    float StepSettleSeconds = .28f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Stepping")
    float StepCooldown = 1.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Stepping")
    float StepFootStrength = 24.f;

    /** Capacity settings shared by enemy types; all values are bounded at use. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Recoverability")
    float RecoveryStrength = 1.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Recoverability")
    float RecoverySpeed = 1.25f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Recoverability")
    float RecoveryReactionSeconds = .10f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Recoverability")
    float RecoveryPersistenceSeconds = 2.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Recoverability")
    float RecoveryFriction = .6f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Recoverability")
    float RecoveryLegStrength = .35f;

    /** Shared non-damaging force seam for future push/explosion work; one physical impulse. */
    UFUNCTION(BlueprintCallable, Category="Physics Dummy|Balance")
    virtual void ApplyExternalDisturbance(FVector Impulse, FVector WorldPoint, FName Bone = "pelvis");
    UFUNCTION(BlueprintPure, Category="Physics Dummy|Balance")
    FString GetBalanceLabel() const;
    /** Editor-only physical floor/ceiling fixtures for the bounded transition checks. */
    UFUNCTION(BlueprintCallable, Category="Physics Dummy|Verification")
    bool ProbeBalanceEnvironment(const FString& Operation);

    UFUNCTION(BlueprintCallable, Category="Physics Dummy")
    virtual void ResetDummy();
    UFUNCTION(BlueprintPure, Category="Physics Dummy|Verification")
    virtual FString GetDummyState(bool IncludeContacts = true) const;
    UFUNCTION(BlueprintPure, Category="Physics Dummy|Verification")
    FVector GetPhysicalBodyLocation(FName Bone) const;

    FDummyPose SamplePhysicalPose() const;
    bool TracePhysicalPose(const FDummyPose& Before, const FDummyPose& After,
        const FVector& Start, const FVector& End, float Radius, FHitResult& Hit) const;
    virtual float ReceiveBullet(int64 ShotId, float Damage, const FVector& Direction, const FHitResult& Hit,
        double ContactTime, double BirthTime, uint64 CombatFrame,
        float FallImpulseMultiplier = 1.f, float DeathImpulseMultiplier = 1.f);
    bool IsDead() const { return Deaths != 0; }
    bool IsReady() const { return bReady; }
    uint64 DeathFrame = 0;
    double DeathTime = -1;

protected:
    UPROPERTY() TObjectPtr<USceneComponent> FixtureRoot;
    UPROPERTY() TObjectPtr<UTextRenderComponent> Label;
    UPROPERTY() TObjectPtr<UAnimSequence> Idle;
    UPROPERTY() TObjectPtr<UAnimSequence> GetUpBack;
    UPROPERTY() TObjectPtr<UAnimSequence> GetUpStomach;
    UPROPERTY() TObjectPtr<UAnimSequence> ActiveGetUp;
    UPROPERTY() TObjectPtr<USkeletalMeshComponent> PoseSource;
    UPROPERTY() TObjectPtr<AActor> ProbeFloor;
    UPROPERTY() TObjectPtr<AActor> ProbeCeiling;
    void ClearBalanceProbeFixtures();
    FTransform Home;
    FTransform SupportTarget;
    TMap<FName, FTransform> ReferencePose;
    TArray<FName> Controls;
    TMap<FName, FName> BodyControls;
    TMap<FName, float> RecoveringControls;
    FPoseSnapshot FallenSnapshot;
    FPoseSnapshot IdleSnapshot;
    struct FSolePoint { FName Bone; FVector Local; };
    TArray<FSolePoint> SolePoints;
    TMap<FName, FTransform> StandingPose;
    TMap<FName, FTransform> GetUpEndPose;
    FName PelvisControl;
    FVector LeanDirection = FVector::ZeroVector;
    FVector StandingForward = FVector::ForwardVector;
    FTransform RecoveryRoot;
    FTransform RecoveredIdleRoot;
    float SnapshotFirstError = 0;
    float GetRecoveryAnimationTime() const;
    float StateSeconds = 0.f;
    float SinceDisturbance = 0.f;
    float LeftLegDisabled = 0.f;
    float RightLegDisabled = 0.f;
    float NoSupportSeconds = 0.f;
    float SettledSeconds = 0.f;
    float PoseLeanDegrees = 0.f;
    float PelvisDrop = 0.f;
    float GroundHeight = 0.f;
    int32 UsableFeet = 0;
    bool bRecoveryFloor = false;
    bool bRecoveryClear = false;
    int32 Falls = 0;
    int32 GetUps = 0;
    int32 InterruptedGetUps = 0;
    FString BalanceReason;
    // One recent bullet may accent the next committed fall; the contact follows its body.
    struct FPendingFallImpact
    {
        FName Bone;
        FVector LocalPoint = FVector::ZeroVector;
        FVector BonusImpulse = FVector::ZeroVector;
        bool bAllowRotation = false;
        double Deadline = -1;
        TSharedPtr<FJsonObject> Contact;
    };
    FPendingFallImpact PendingFallImpact;
    FPendingFallImpact PendingFallRotation;
    bool bFallRotationApplied = false;
    void ApplyPendingFallRotation();
    void ResetBalance();
    void InitializeBalanceDrives();
    virtual void UpdateBalance(float DeltaSeconds);
    virtual void RegisterDisturbance(FName Bone, const FVector& Impulse, float Amount);
    virtual void EnterFall(const TCHAR* Reason);
    void DisableBalanceDrives();
    bool FindFloor(const FVector& Point, float Depth, FHitResult& Hit) const;
    bool RecoverySpace(const FVector& Center, float& FloorZ) const;
    virtual bool BeginGetUp();
    void SampleAnimation(UAnimSequence* Animation, float Time, const FTransform& Origin, TMap<FName,FTransform>& Pose);
    void DrivePose(const TMap<FName,FTransform>& Pose, float Strength = 1.f);
    void AddBalanceState(TSharedPtr<FJsonObject> Root) const;
    struct FRecoveryFoot
    {
        bool bUsable = false;
        bool bContact = false;
        float Gap = 1000;
        float Slip = 0;
        float VerticalSpeed = 0;
        float ContactAge = 1000;
        float NormalImpulse = 0;
        int32 FootprintPoints = 0;
        TArray<FVector> Footprint;
    };
    FRecoveryFoot RecoveryFeet[2];
    FVector RecoveryCOM = FVector::ZeroVector;
    FVector RecoveryVelocity = FVector::ZeroVector;
    FVector CapturePoint = FVector::ZeroVector;
    FVector CaptureError = FVector::ZeroVector;
    float RecoveryMass = 0;
    float CaptureDistance = 0;
    float LandingCaptureDistance = 0;
    float RequiredReach = 0;
    float EffectiveStrength = 1;
    float EffectiveSpeed = 1;
    float EffectiveReach = 40;
    float EffectivePersistence = 2;
    float RecoveryAcceleration = 0;
    float BodyAngularSpeed = 0;
    float RecoveryInvalidSeconds = 0;
    float RecoveryNoProgressSeconds = 0;
    float RecoveryBestError = 1000;
    float RecoveryStableSeconds = 0;
    float StepRequestSeconds = 0;
    float GroundContactAge = 1000;
    float RecoveryEffortRatio = 0;
    float RecoveryForceLimit = 0;
    float RecoveryTorqueLimit = 0;
    float StepEntryCaptureDistance = 0;
    FName DisturbedFoot;
    bool bRecoveryFeasible = true;
    bool bRecoveryAssistance = false;
    bool bRecoverySampled = false;
    FString RecoveryReason;
    TArray<TSharedPtr<FJsonValue>> LegContacts;
    UFUNCTION()
    void OnBodyContact(UPrimitiveComponent* HitComponent, AActor* OtherActor,
        UPrimitiveComponent* OtherComponent, FVector NormalImpulse, const FHitResult& Hit);
    FRecoveryFoot MeasureFoot(FName Bone, const FRecoveryFoot& Previous) const;
    void ResetRecoverability();
    void UpdateRecoverability(float DeltaSeconds);
    virtual void BoundRecoveryDrives(float DeltaSeconds);
    void AddRecoverabilityState(TSharedPtr<FJsonObject> Root) const;
    void CalibrateSoles();
    float SoleBottom(const USkeletalMeshComponent* Mesh, bool bLeft) const;
    float ShapeBottom(FName Bone, const FTransform& Transform) const;
    float PoseBottom(const TMap<FName,FTransform>& Pose) const;
    bool FootSupported(FName Bone) const;
    void IsolateSelfCollision();
    virtual void SetVisibleAnimationPose();
    void EvaluateRecoveryPose(float Time, float Blend, float EndBlend, TMap<FName,FTransform>& Pose);
    // World-space full target skeleton. Home is reserved for explicit F6 only.
    TArray<FTransform> StandingBones;
    // Captured only from calibrated idle/reset or completed get-up, never solved steps.
    TArray<FTransform> NeutralBones;
    TArray<FTransform> StepStartBones;
    TArray<FTransform> StepEntryBones;
    TArray<FTransform> StepOutputBones;
    FName SwingFoot;
    FName PlantedFoot;
    FTransform SwingStart;
    FTransform SwingDestination;
    FTransform PlantedTarget;
    FVector PlantedActualStart = FVector::ZeroVector;
    FVector StepDirection = FVector::ZeroVector;
    FVector LastStepImpulse = FVector::ZeroVector;
    FVector StepBodyDirection = FVector::ZeroVector;
    FVector StepDisplacement = FVector::ZeroVector;
    FVector StepTransfer = FVector::ZeroVector;
    FVector StepRestPelvis = FVector::ZeroVector;
    bool bCorrectiveStep = false;
    bool bStanceCorrectionPending = false;
    float StepHeightCorrection = 0;
    float StepJointLimitError = 0;
    float StepSeconds = 0;
    float StepNoSupportSeconds = 0;
    float StepCooldownRemaining = 0;
    float StepSupportDrift = 0;
    float StepPeakSupportDrift = 0;
    // Frozen at step entry; owner tempo and measured disturbance scaling are separate.
    float AdaptiveLength = 0;
    float AdaptiveLift = 0;
    float AdaptiveUrgency = 0;
    float AdaptiveTransferTime = 0;
    float AdaptiveSwingTime = 0;
    float AdaptiveSettleTime = 0;
    float AdaptiveEntrySpeed = 0;
    float AdaptiveEntryLean = 0;
    float AdaptiveLeanExcursion = 0;
    float AdaptiveEntryDemand = 0;
    FVector AdaptiveEntryVelocity = FVector::ZeroVector;
    FVector AdaptiveReplanVelocity = FVector::ZeroVector;
    FVector AdaptiveReplanOrigin = FVector::ZeroVector;
    FVector AdaptiveReplanGoal = FVector::ZeroVector;
    float AdaptiveReplanStart = -1;
    float AdaptiveReplanAge = 0;
    float AdaptiveReplanTravel = 0;
    int32 AdaptiveReplans = 0;
    int32 AdaptiveGeometryTrials = 0;
    bool bAdaptiveReplanPending = false;
    FString AdaptiveReplanReason;
    int32 StepPhase = 0; // 0 idle, 1 transfer, 2 swing, 3 settling.
    int32 EpisodeSteps = 0;
    int32 StepsStarted = 0;
    int32 StepsCompleted = 0;
    int32 StepsRejected = 0;
    bool bStepRequested = false;
    FString StepReason;
    void ResetStepping();
    void CancelStep();
    void ResetAdaptiveStep();
    void SelectAdaptiveStep(const FVector& BodyOffset, float FootMotion);
    void ConfigureAdaptiveGeometry(float Length);
    bool ValidateStepGeometry();
    bool UpdateAdaptiveReplan(float DeltaSeconds);
    void UpdateStepRestPelvis();
    void RememberStandingSkeleton(const USkeletalMeshComponent* Mesh, bool bNeutral = true);
    bool NeedsStanceCorrection() const;
    bool BeginStep();
    virtual FVector StepJointLimits(FName Bone) const;
    virtual void PrepareStepLanding(FName Bone, FTransform& Target) const {}
    void UpdateStep(float DeltaSeconds);
    bool StepPlacement(FName Bone, FTransform& Foot, float FloorReference) const;
    bool StepPathClear(const FTransform& Start, const FTransform& End) const;
    bool BuildStepPose(float Transfer, float Swing, float Settle, TMap<FName,FTransform>& Pose, bool bApply = true);
    void AddStepState(TSharedPtr<FJsonObject> Root) const;
    uint64 PoseEpoch = 0;
    bool bReady = false;
    int32 UnsupportedShapes = 0;
    int32 WidenedJoints = 0;
    TArray<TSharedPtr<FJsonValue>> Contacts;
    void UpdateLabel();
    TSharedPtr<FJsonObject> BodyState() const;
};
