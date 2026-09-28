#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Engine/DataAsset.h"
#include "DestructionFragmentState.h"
#include "DemoColumnCladding.generated.h"

class UStaticMesh;
class UInstancedStaticMeshComponent;
class UGeometryCollectionComponent;
class UPrimitiveComponent;
class UBoxComponent;
class ULobbyFacingPool;
class UDestructionFragmentWorld;
class UPhysicalMaterial;

USTRUCT()
struct FDemoColumnTileShard
{
    GENERATED_BODY()
    UPROPERTY() TObjectPtr<UStaticMesh> Mesh;
    UPROPERTY() FTransform RelativeToTile;
    UPROPERTY() float AreaCm2 = 0.f;
};

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
    UPROPERTY() TArray<FDemoColumnTileShard> Shards;
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
struct FDemoColumnCompactSection
{
    GENERATED_BODY()
    UPROPERTY() TObjectPtr<UStaticMesh> Mesh;
    UPROPERTY() TArray<int32> Tiles;
};

/** Derived render-only sections; source tiles remain the collision and fracture authority. */
UCLASS()
class MERIDIANSQUAD_API UDemoColumnCompactData : public UDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY() TObjectPtr<UDemoColumnCladdingData> Source;
    UPROPERTY() TArray<FDemoColumnCompactSection> Sections;
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
    FDestructionFragmentId IdentifyHit(const FHitResult& Hit) const;
    bool RefreshHit(const FDestructionFragmentId& Id, FHitResult& Hit) const;
    uint64 GetFragmentOwner() const { return FragmentOwner; }
    uint32 GetFragmentGeneration() const { return FragmentGeneration; }
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    uint64 FragmentOwner = 0;
    uint32 FragmentGeneration = 0;
    TArray<uint64> TileStateRevisions;
    TArray<uint64> TilePoseRevisions;
    TMap<int32, TArray<int32>> TilesBySupport;
    UPROPERTY(Transient) TObjectPtr<UDestructionFragmentWorld> FragmentWorld;
    UPROPERTY(Transient) TObjectPtr<UPhysicalMaterial> DebrisMaterial;
    int32 NextLooseLocal = 0;
    UPROPERTY(Transient) TObjectPtr<UDemoColumnCompactData> CompactData;
    TArray<int32> CompactSectionByTile;
    TArray<uint64> CompactHandles;
    bool ExpandCompactSection(int32 Tile);
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
    TSet<int32> ConcreteLeafSet;
    TArray<float> ConcreteAge;
    TArray<float> ConcreteStillTime;
    float DebrisPollTime = 0.f;
    bool bSurfaceExperiment = false;
    bool bCoarseExperiment = false;
    bool bRefinedExperiment = false;
    bool bStackingExperiment = false;
    UPROPERTY(Transient) TObjectPtr<UBoxComponent> CoreBarrier;
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
    FTransform LastUpdatedComponentTransform;
    FTransform LastUpdatedRootTransform;
    bool bHadStationaryUpdate = false;
    bool bIdleLastTick = false;
    uint64 FullUpdateCount = 0;
    uint64 SkippedIdleUpdates = 0;
    UPROPERTY(Transient) TObjectPtr<ULobbyFacingPool> FacingPool;
    TArray<uint64> RenderHandles;
    TMap<int32, TArray<int32>> TilesByCarrier;
    TMap<int32, FTransform> LastCarrierWorld;
    TSet<int32> MovingCarriersLastTick;
    TSet<int32> DirtyCarriers;
    uint64 TilePoseUpdates = 0;
    uint64 TilePoseUpdatesSkipped = 0;
    void Detach(int32 Tile, const FVector& Push);
    void DamageConcrete(const FHitResult& Hit);
    FVector FacingScatter(int32 Tile, const FHitResult& Hit) const;
    void UpdateDebris(float DeltaTime);
    int32 RetentionSlotsUsed() const;
    int32 RetentionSector(const FVector& Position) const;
    void RetentionSectorCounts(TArray<int32>& Total, TArray<int32>& Tiles) const;
    bool MakeRetentionRoom(const FVector& Position, bool bTile);
    int32 RetentionReplacements = 0;
    int32 RetentionSupportVetoes = 0;
    int32 ReplacementsThisPoll = 0;
    TArray<int32> RetentionEvictions = {0, 0, 0, 0};
    void CarryTiles(int32 Bone);
    bool RemoveTileInstance(int32 Tile);
    bool HasStaticSupport(const FVector& Bottom) const;
    void UpdateFacingImpacts();
    void CrumbleCarriedFacing(int32 Bone, const FVector& Point, const FVector& Normal, bool bShot);
    TArray<int32> ChipTemplates;
    UPROPERTY(Transient) TArray<TObjectPtr<AActor>> CeramicDebris;
    TMap<int32, FVector> PreviousConcreteVelocity;
    TSet<int32> GroundCrumbled;
    int32 GroundCrumbleEvents = 0;
    int32 ShotCrumbleEvents = 0;
    int32 CrumbledTiles = 0;
    int32 SpawnedCeramicChips = 0;
    TMap<TWeakObjectPtr<AActor>, int32> WholeTileSources;
    int32 IndependentTileBreaks = 0;
    bool HasDebrisSupport(const FVector& Bottom, int32 ExcludedBone, const AActor* ExcludedActor, bool bRetainedOnly) const;
    void SpawnTileShards(int32 Tile, const FTransform& Pose, const FVector& Velocity, const FVector& Normal);
    UFUNCTION() void OnLooseTileImpact(UPrimitiveComponent* HitComponent, AActor* OtherActor,
        UPrimitiveComponent* OtherComponent, FVector NormalImpulse, const FHitResult& Hit);
};
