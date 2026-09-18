#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CombatProjectileWorld.generated.h"

class ACharacter;
class ACombatTarget;

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
    bool ProbeCover(FName Kind);

    int64 Launch(AActor* Shooter, const FVector& Position, const FVector& Velocity, float Damage);
    void ClearProjectiles();
    void BuildQuery(FCollisionQueryParams& Query, const AActor* Ignore = nullptr) const;
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
        bool bLaunchClear = false;
        bool bFirstAdvance = true;
        TMap<TWeakObjectPtr<ACharacter>, FCapsuleSample> BirthCapsules;
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
    float ProjectileTimeScale = 1.f;
    int64 NextShotId = 1;
    int32 LaunchedCount = 0;
    int32 RejectedCount = 0;
    uint64 ResetGeneration = 0;
    bool bAdvancing = false;
    bool bProbeResetPending = false;
    int32 ProbeResetCallbacks = 0;
    FVector ProbeSpawnPosition = FVector::ZeroVector;
    UFUNCTION()
    void ProbeHitReset(int64 ShotId, FName ShooterIdentity, AActor* Shooter, AActor* Victim,
        float Damage, FVector Position, bool bSelfHit);
    void Advance(float WorldDelta, double RealNow);
    void RecordCapsules();
    void ResolveHit(const FBullet& Bullet, const FHitResult& Hit, double Now);
};
