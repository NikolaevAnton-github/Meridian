#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Subsystems/WorldSubsystem.h"
#include "Chaos/ChaosGameplayEventDispatcher.h"
#include "NGDPropComponent.generated.h"

class UGeometryCollectionComponent;

/** Initial collision contract. Bounds are conservative envelopes, not a navigation rebuild. */
USTRUCT(BlueprintType)
struct FNGDCollisionChange
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly) FName ObjectId;
    UPROPERTY(BlueprintReadOnly) int32 CollisionRevision = 0;
    UPROPERTY(BlueprintReadOnly) int32 ResetGeneration = 0;
    UPROPERTY(BlueprintReadOnly) FBox ChangedBounds = FBox(ForceInit);
    UPROPERTY(BlueprintReadOnly) FName Reason;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNGDChanged, const FNGDCollisionChange&, Change);

/** World lifetime subscription survives replacement of a reset vendor actor. */
UCLASS()
class MERIDIANSQUAD_API UNGDWorldSubsystem : public UWorldSubsystem
{
    GENERATED_BODY()
public:
    UPROPERTY(BlueprintAssignable) FNGDChanged OnCollisionChanged;
    UPROPERTY(BlueprintReadOnly) TMap<FName, FNGDCollisionChange> LatestChanges;
    void Publish(const FNGDCollisionChange& Change);
};

/** Opt-in adapter on unmodified BP_BreakableObject instances. Owns no fracture art. */
UCLASS(ClassGroup=(Combat), meta=(BlueprintSpawnableComponent))
class MERIDIANSQUAD_API UNGDPropComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UNGDPropComponent();
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Destruction") FName ObjectId;
    UPROPERTY(BlueprintReadOnly, Transient) int32 CollisionRevision = 0;
    UPROPERTY(BlueprintReadOnly, Transient) int32 ResetGeneration = 0;
    UPROPERTY(BlueprintReadOnly, Transient) int32 DeliveredHits = 0;
    UPROPERTY(BlueprintReadOnly, Transient) int32 BreakEvents = 0;
    UPROPERTY(BlueprintReadOnly, Transient) int64 LastShotId = 0;
    UPROPERTY(BlueprintReadOnly, Transient) bool bReady = false;

    // Returns true for a managed prop, including an invalid/duplicate request: fail closed.
    bool ReceiveBullet(int64 ShotId, const FHitResult& Hit);
    static void ResetAll(UWorld* World);
    UFUNCTION(BlueprintPure, Category="Destruction") FString GetState() const;
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    friend class UNGDTools;
    UPROPERTY(Transient) TObjectPtr<UGeometryCollectionComponent> Collection;
    UPROPERTY(Transient) TObjectPtr<UObject> SourceData;
    UPROPERTY(Transient) TArray<TWeakObjectPtr<AActor>> Fields;
    FTransform InitialTransform;
    FBox PreviousBounds = FBox(ForceInit);
    FBox ResetBounds = FBox(ForceInit);
    TArray<int64> RecentShots;
    TArray<FName> FieldNames;
    bool bRetiring = false;
    UFUNCTION() void OnBreak(const FChaosBreakEvent& Event);
    void Publish(FName Reason, const FBox& Previous);
    void Retire();
};

/** Bounded placement and PIE evidence helpers; shots still use player input and the real rifle. */
UCLASS()
class MERIDIANSQUAD_API UNGDTools : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="Destruction", meta=(WorldContext="Context"))
    static AActor* SpawnProp(UObject* Context, UObject* DataAsset, FVector Location, FRotator Rotation, FName ObjectId);
    UFUNCTION(BlueprintCallable, Category="Destruction|Verification", meta=(WorldContext="Context"))
    static bool RifleInput(UObject* Context, bool bPressed);
    UFUNCTION(BlueprintCallable, Category="Destruction|Verification", meta=(WorldContext="Context"))
    static bool AimPlayer(UObject* Context, FVector Target);
    UFUNCTION(BlueprintCallable, Category="Destruction|Verification", meta=(WorldContext="Context"))
    static FString Sweep(UObject* Context, FVector Start, FVector End, float Radius = .5f);
    static AActor* Spawn(UWorld* World, UObject* DataAsset, const FTransform& Transform, FName Id, int32 Generation, int32 Revision, FBox PriorBounds = FBox(ForceInit));
};
