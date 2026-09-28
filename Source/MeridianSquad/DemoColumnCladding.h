#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Engine/DataAsset.h"
#include "DemoColumnCladding.generated.h"

class UStaticMesh;
class UInstancedStaticMeshComponent;
class UGeometryCollectionComponent;

USTRUCT()
struct FDemoColumnTile
{
    GENERATED_BODY()
    UPROPERTY() TObjectPtr<UStaticMesh> Mesh;
    UPROPERTY() FTransform RestTransform;
    UPROPERTY() FTransform RelativeToBone;
    UPROPERTY() int32 Bone = INDEX_NONE;
    UPROPERTY() bool bBonded = false;
    UPROPERTY() float AreaCm2 = 0.f;
    // Every concrete surface intersecting this tile's footprint (coarse variant).
    UPROPERTY() TArray<int32> SupportBones;
};

/** Separate facing for the owner's demo-column experiment; never edits the vendor collection. */
UCLASS()
class MERIDIANSQUAD_API UDemoColumnCladdingData : public UDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY() TArray<FDemoColumnTile> Tiles;
    UPROPERTY() TArray<int32> SurfaceBones;
};

USTRUCT()
struct FDemoColumnTileGroup
{
    GENERATED_BODY()
    UPROPERTY(Transient) TObjectPtr<UInstancedStaticMeshComponent> Instances;
    TArray<int32> Tiles;
};

UCLASS(ClassGroup=(Destruction))
class MERIDIANSQUAD_API UDemoColumnCladding : public UActorComponent
{
    GENERATED_BODY()
public:
    UDemoColumnCladding();
    void Initialize();
    UFUNCTION(BlueprintPure, Category="Destruction|Experiments")
    FString GetState() const;
    // The experiment consumes its facing and concrete contacts exactly once.
    bool HandleImpact(FHitResult& Hit);
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    UPROPERTY(Transient) TObjectPtr<UDemoColumnCladdingData> Data;
    UPROPERTY(Transient) TObjectPtr<UGeometryCollectionComponent> Concrete;
    UPROPERTY(Transient) TArray<FDemoColumnTileGroup> Groups;
    UPROPERTY(Transient) TArray<TObjectPtr<AActor>> Debris;
    TArray<int32> GroupByTile;
    TArray<int32> InstanceByTile;
    TArray<uint8> Hits;
    TArray<FTransform> LastWorld;
    TArray<FVector> Velocities;
    TMap<TWeakObjectPtr<AActor>, float> DebrisStillTime;
    TSet<TWeakObjectPtr<AActor>> RetainedTiles;
    TMap<TWeakObjectPtr<AActor>, FVector> RetainedTileSupport;
    TSet<int32> RetainedConcrete;
    TSet<int32> PendingConcrete;
    TSet<int32> RemovedConcrete;
    TArray<int32> ConcreteLeaves;
    TArray<float> ConcreteAge;
    TArray<float> ConcreteStillTime;
    float DebrisPollTime = 0.f;
    bool bSurfaceExperiment = false;
    bool bCoarseExperiment = false;
    bool bEndingPlay = false;
    int32 ConcreteImpacts = 0;
    int32 LastConcreteBone = INDEX_NONE;
    int32 ProtectedCoreImpacts = 0;
    TArray<int32> CarrierByTile;
    TArray<FTransform> CarrierRelative;
    TArray<FTransform> RestBones;
    TArray<bool> CarriedTiles;
    TSet<int32> ReleasedConcrete;
    TMap<int32, int32> CarriedGroupByOriginal;
    uint32 ImpactSerial = 0;
    void Detach(int32 Tile, const FVector& Push);
    void DamageConcrete(const FHitResult& Hit);
    FVector FacingScatter(int32 Tile, const FHitResult& Hit) const;
    void UpdateDebris(float DeltaTime);
    int32 RetentionSlotsUsed() const;
    void CarryTiles(int32 Bone);
    bool RemoveTileInstance(int32 Tile);
    bool HasStaticSupport(const FVector& Bottom) const;
};
