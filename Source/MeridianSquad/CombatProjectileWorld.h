#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "EnemyPrototypeCharacter.h"
#include "PhysicsControlDummy.h"
#include "CombatProjectileWorld.generated.h"

class ACharacter;
class ACombatTarget;
class UCombatRifleComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_SevenParams(FCombatBulletHit, int64, ShotId, FName, ShooterIdentity, AActor*, Shooter,
    AActor*, Victim, float, Damage, FVector, Position, bool, bSelfHit);

/** Finite-flight world simulation. The later time ability controls this clock, not the FP render scale. */
UCLASS()
class MERIDIANSQUAD_API ACombatProjectileWorld : public AActor
{
    GENERATED_BODY()
public:
    ACombatProjectileWorld();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    static ACombatProjectileWorld* Find(const UWorld* World);

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Combat|Tuning", meta=(ClampMin="1", ClampMax="256"))
    int32 MaxProjectiles = 128;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Combat|Tuning", meta=(ClampMin="0.1"))
    float MaxSimulationAge = 3.f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Combat|Tuning", meta=(ClampMin="1"))
    float MaxRealAge = 120.f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Combat|Tuning", meta=(ClampMin="1"))
    float MaxTravel = 30000.f;
    UPROPERTY(BlueprintAssignable, Category="Combat")
    FCombatBulletHit OnBulletHit;

    /** Zero preserves position, velocity and simulation age, while moving capsule contacts remain active. */
    UFUNCTION(BlueprintCallable, Category="Combat|Time")
    void SetProjectileTimeScale(float Scale);
    UFUNCTION(BlueprintPure, Category="Combat|Time")
    float GetProjectileTimeScale() const { return ProjectileTimeScale; }
    UFUNCTION(BlueprintCallable, Category="Combat|Prototype")
    void ResetTargets();
    UFUNCTION(BlueprintPure, Category="Combat|Verification")
    FString GetCombatState() const;
    UFUNCTION(BlueprintCallable, Category="Combat|Verification")
    FString ProbeBallistics();
    UFUNCTION(BlueprintCallable, Category="Combat|Verification")
    FString ProbeCorrections();
    UFUNCTION(BlueprintCallable, Category="Combat|Verification")
    FString ProbeTiming(const FString& Configuration);
    UFUNCTION(BlueprintCallable, Category="Combat|Verification")
    FString ProbeEnemy(bool bCoverOnly = false, bool bAimOnly = false);
    UFUNCTION(BlueprintCallable, Category="Combat|Verification")
    FString ProbePhysicsDummy();
    UFUNCTION(BlueprintCallable, Category="Combat|Verification")
    bool PreparePhysicsDummyFreefallProbe();
    UFUNCTION(BlueprintCallable, Category="Combat|Prototype")
    void SetPhysicsDummyEnabled(bool Enabled);
    UFUNCTION(BlueprintPure, Category="Combat|Prototype")
    bool IsPhysicsDummyEnabled() const { return bEnablePhysicsDummy; }
    /** Development preview only. Applied after this combat frame to avoid mixed clock deltas. */
    UFUNCTION(BlueprintCallable, Category="Combat|Prototype")
    void SetPhysicsPreviewScale(float Scale);
    UFUNCTION(BlueprintPure, Category="Combat|Prototype")
    float GetPhysicsPreviewScale() const { return RequestedPreviewScale; }
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Combat|Prototype")
    bool bEnablePhysicsDummy = true;
    UFUNCTION(BlueprintCallable, Category="Combat|Verification")
    bool ProbeCover(FName Kind);

    int64 Launch(AActor* Shooter, const FVector& Position, const FVector& Velocity, float Damage);
    int64 LaunchTimed(AActor* Shooter, const FVector& Position, const FVector& Velocity, float Damage, double Time);
    double GetFiringClock() const { return FiringClock; }
    void ClearProjectiles();
    void BuildQuery(FCollisionQueryParams& Query, const AActor* Ignore = nullptr) const;
    bool TraceEnemyAim(const FVector& Start, const FVector& End, double Time, FHitResult& Hit) const;
    int32 GetActiveCount() const { return Bullets.Num(); }
    FString LastHitText;
    double LastHitRealTime = -100.0;
    int32 HitCount = 0;
    int32 SelfHitCount = 0;
    int32 RetiredCount = 0;
    int64 LastHitShotId = 0;
    FName LastHitShooterIdentity;
    FString LastHitSurface;
    FString LastHitMaterial;

private:
    struct FCapsuleSample
    {
        FVector Center;
        float Radius;
        float HalfHeight;
        TArray<FEnemyHitSphere> Regions;
    };
    struct FBullet
    {
        int64 Id = 0;
        TWeakObjectPtr<AActor> Shooter;
        FName ShooterIdentity;
        TWeakObjectPtr<AController> Instigator;
        FVector Position = FVector::ZeroVector;
        FVector Velocity = FVector::ZeroVector;
        float Damage = 0.f;
        float Age = 0.f;
        float Travel = 0.f;
        double Born = 0.0;
        double BirthTime = 0.0;
        uint64 EligibleFrame = 0;
        bool bLaunchClear = false;
        bool bFirstAdvance = true;
        TMap<TWeakObjectPtr<ACharacter>, FCapsuleSample> BirthCapsules;
        TMap<TWeakObjectPtr<APhysicsControlDummy>, FDummyPose> BirthDummies;
    };
    struct FImpact
    {
        FVector Position;
        FVector Normal;
        double Born;
        bool bMetal;
    };
    TArray<FBullet> Bullets;
    TArray<FImpact> Impacts;
    TMap<TWeakObjectPtr<ACharacter>, FCapsuleSample> PreviousCapsules;
    UPROPERTY(Transient)
    TArray<TObjectPtr<ACombatTarget>> Targets;
    UPROPERTY(Transient)
    TObjectPtr<AEnemyPrototypeCharacter> Enemy;
    UPROPERTY(Transient)
    TObjectPtr<APhysicsControlDummy> PhysicsDummy;
    TMap<TWeakObjectPtr<APhysicsControlDummy>, FDummyPose> PreviousDummies;
    TMap<TWeakObjectPtr<APhysicsControlDummy>, FDummyPose> FrameStartDummies;
    TMap<TWeakObjectPtr<APhysicsControlDummy>, FDummyPose> FrameEndDummies;
    float RequestedPreviewScale = 1.f;
    float ActivePreviewScale = 1.f;
    float SavedWorldDilation = 1.f;
    float SavedPlayerDilation = 1.f;
    float SavedManagerDilation = 1.f;
    float SavedProjectileScale = 1.f;
    TWeakObjectPtr<ACharacter> PreviewPlayer;
    bool bOwnsPreviewTime = false;
    void ApplyPreviewTime();
    void RestorePreviewTime();
    TMap<TWeakObjectPtr<APhysicsControlDummy>, FDummyPose> SampleDummies() const;
    TMap<TWeakObjectPtr<APhysicsControlDummy>, FDummyPose> DummiesAt(double Time) const;
    float ProjectileTimeScale = 1.f;
    int64 NextShotId = 1;
    int32 LaunchedCount = 0;
    int32 RejectedCount = 0;
    uint64 ResetGeneration = 0;
    bool bAdvancing = false;
    static constexpr double MaxFrameTime = .250;
    static constexpr double MaxStepTime = .010;
    static constexpr int32 MaxFrameSteps = 32;
    static constexpr int32 MaxFrameBirths = 6;
    double FiringClock = 0.0;
    double FrameStart = 0.0;
    double FrameEnd = 0.0;
    double LastFrameDelta = 0.0;
    double LastContactTime = -1.0;
    double DroppedTime = 0.0;
    uint64 FrameSerial = 0;
    bool bProcessingFrame = false;
    int32 LastFrameSteps = 0;
    int32 LastFrameBirths = 0;
    int32 PeakFrameSteps = 0;
    int32 OverloadFrames = 0;
    int32 GeometryBarriers = 0;
    TMap<TWeakObjectPtr<ACharacter>, FCapsuleSample> FrameStartCapsules;
    TMap<TWeakObjectPtr<ACharacter>, FCapsuleSample> FrameEndCapsules;
    struct FBlockerSample
    {
        FTransform Transform;
        FVector Extent;
    };
    TMap<TWeakObjectPtr<UPrimitiveComponent>, FBlockerSample> PreviousBlockers;
    bool bHaveBlockerSample = false;
    bool bProbeResetPending = false;
    int32 ProbeResetCallbacks = 0;
    FVector ProbeSpawnPosition = FVector::ZeroVector;
    UFUNCTION()
    void ProbeHitReset(int64 ShotId, FName ShooterIdentity, AActor* Shooter, AActor* Victim,
        float Damage, FVector Position, bool bSelfHit);
    void Advance(float WorldDelta, double RealNow);
    void AdvanceFrame(double WorldDelta, double RealNow, UCombatRifleComponent* Rifle);
    void AdvanceSegment(double StartTime, double EndTime, double RealNow);
    TMap<TWeakObjectPtr<ACharacter>, FCapsuleSample> SampleCapsules() const;
    TMap<TWeakObjectPtr<ACharacter>, FCapsuleSample> CapsulesAt(double Time) const;
    TMap<TWeakObjectPtr<UPrimitiveComponent>, FBlockerSample> SampleBlockers() const;
    bool BlockersMatch(const TMap<TWeakObjectPtr<UPrimitiveComponent>, FBlockerSample>& Samples) const;
    void RecordCapsules();
    void ResolveHit(const FBullet& Bullet, const FHitResult& Hit, double Now);
};
