#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "GameFramework/Actor.h"
#include "DestructionFragmentState.h"
#include "DestructionFragmentWorld.generated.h"

class UDemoColumnCladding;
class UGeometryCollectionComponent;
class UStaticMesh;
class UStaticMeshComponent;
class UPrimitiveComponent;
class UPhysicalMaterial;
class AStaticMeshActor;
class ULobbyFacingPool;

UCLASS(Transient, NotBlueprintable)
class MERIDIANSQUAD_API ADestructionFragmentDriver : public AActor
{
    GENERATED_BODY()
public:
    ADestructionFragmentDriver();
    virtual void Tick(float DeltaSeconds) override;
};

/** World-owned physical fragments. Render instances never own collision or identity. */
UCLASS()
class MERIDIANSQUAD_API UDestructionFragmentWorld : public UWorldSubsystem
{
    GENERATED_BODY()
public:
    virtual bool DoesSupportWorldType(EWorldType::Type Type) const override;
    void RegisterOwner(UDemoColumnCladding* Owner);
    int64 RegisterConcrete(UDemoColumnCladding* Owner, UGeometryCollectionComponent* Concrete, int32 Bone);
    AStaticMeshActor* Acquire(UDemoColumnCladding* Owner, UStaticMesh* Mesh,
        UPhysicalMaterial* Material, const FTransform& Pose, int32 Local);
    void Return(AActor* Actor);
    void RemoveOwner(UDemoColumnCladding* Owner);
    void InvalidateSupport(AActor* Owner);
    void Update(float DeltaSeconds);
    virtual void Deinitialize() override;
    UFUNCTION(BlueprintCallable, Category="Destruction|Fragments")
    int64 Select(UPrimitiveComponent* Component, int32 Item) const;
    UFUNCTION(BlueprintCallable, Category="Destruction|Fragments")
    FString Impulse(int64 Handle, FVector DeltaVelocity);
    UFUNCTION(BlueprintCallable, Category="Destruction|Fragments")
    FString Hold(int64 Handle);
    UFUNCTION(BlueprintCallable, Category="Destruction|Fragments")
    FString MoveHeld(int64 Handle, FTransform Pose);
    UFUNCTION(BlueprintCallable, Category="Destruction|Fragments")
    FString Release(int64 Handle, FVector Velocity, FVector AngularVelocity);
    UFUNCTION(BlueprintPure, Category="Destruction|Fragments")
    FString GetState() const;
    UFUNCTION(BlueprintCallable, Category="Destruction|Verification", meta=(DevelopmentOnly))
    AStaticMeshActor* SpawnVerificationFragment(UDemoColumnCladding* Owner, UStaticMesh* Mesh, FTransform Pose);
    bool IsManaged(const AActor* Actor) const;

private:
    struct FRecord
    {
        int64 Handle = 0;
        FDestructionFragmentStamp Stamp;
        TWeakObjectPtr<UDemoColumnCladding> Owner;
        TWeakObjectPtr<AStaticMeshActor> Actor;
        TWeakObjectPtr<UGeometryCollectionComponent> Concrete;
        int32 Bone = INDEX_NONE;
        EDestructionFragmentState State = EDestructionFragmentState::Awake;
        FTransform Pose;
        FBox Bounds = FBox(ForceInit);
        FVector Velocity = FVector::ZeroVector;
        FVector Bottom = FVector::ZeroVector;
        TSharedPtr<const TArray<FVector>, ESPMode::ThreadSafe> Hull;
        TArray<FIntVector> Cells;
        TSet<int64> Dependents;
        TSet<int64> Supports;
        TWeakObjectPtr<UPrimitiveComponent> StaticSupport;
        FTransform SupportPose;
        FTransform DependencyPose;
        uint64 RenderHandle = 0;
        bool bSupportDirty = true;
        bool bObserved = false;
        TSharedPtr<FDestructionCommandGuard, ESPMode::ThreadSafe> Guard;
        double NextSupportCheck = 0.;
        float StillTime = 0.f;
        bool bSupported = false;
        FVector AngularVelocity = FVector::ZeroVector;
    };
    struct FPoolKey
    {
        TWeakObjectPtr<UStaticMesh> Mesh;
        TWeakObjectPtr<UPhysicalMaterial> Material;
        bool operator==(const FPoolKey& Other) const { return Mesh == Other.Mesh && Material == Other.Material; }
        friend uint32 GetTypeHash(const FPoolKey& Key)
        { return HashCombineFast(GetTypeHash(Key.Mesh), GetTypeHash(Key.Material)); }
    };
    UPROPERTY(Transient) TObjectPtr<ADestructionFragmentDriver> Driver;
    UPROPERTY(Transient) TArray<TObjectPtr<AStaticMeshActor>> Allocations;
    UPROPERTY(Transient) TArray<TObjectPtr<UObject>> CachedResources;
    TMap<FPoolKey, TArray<TWeakObjectPtr<AStaticMeshActor>>> Free;
    TMap<TWeakObjectPtr<AActor>, FPoolKey> PoolKeys;
    TMap<TWeakObjectPtr<AActor>, uint64> ReuseAfterFrame;
    TMap<int64, FRecord> Records;
    TMap<FDestructionFragmentId, int64> Identity;
    TMap<TWeakObjectPtr<UPrimitiveComponent>, int64> LooseLookup;
    TMap<FIntVector, TSet<int64>> Spatial;
    TMap<FString, TSharedPtr<const TArray<FVector>, ESPMode::ThreadSafe>> HullCache;
    TMap<TWeakObjectPtr<UGeometryCollectionComponent>, TArray<FDestructionLeafCommand>> PendingCommands;
    bool bCollectingCommands = false;
    uint64 Reused = 0, Grown = 0, SupportTests = 0, WakeCommands = 0;
    uint64 PoseChanges = 0, SleepingSkipped = 0, AllocationFailures = 0;
    uint64 ParallelJobs = 0, RejectedResults = 0, SerialComparisons = 0;
    int32 NextVerificationLocal = MAX_int32;
    bool bTearingDown = false;
    AStaticMeshActor* Allocate(const FPoolKey& Key);
    void Forget(int64 Handle);
    void InvalidateDependents(FRecord& Record);
    void UpdateSpatial(FRecord& Record);
    bool FindSupport(FRecord& Record);
    bool Valid(const FRecord& Record) const;
    FString Command(int64 Handle, uint8 Operation, const FVector& Velocity,
        const FVector& AngularVelocity, const FTransform& Pose);
};
