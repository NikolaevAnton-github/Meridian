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
};

/** Separate facing for the owner's demo-column experiment; never edits the vendor collection. */
UCLASS()
class MERIDIANSQUAD_API UDemoColumnCladdingData : public UDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY() TArray<FDemoColumnTile> Tiles;
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
    uint32 ImpactSerial = 0;
    void Detach(int32 Tile, const FVector& Push);
    void DamageConcrete(const FHitResult& Hit);
    FVector FacingScatter(int32 Tile, const FHitResult& Hit) const;
};
