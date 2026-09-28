#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "LobbyFacingPool.generated.h"

class UDemoColumnCladding;
class UInstancedStaticMeshComponent;
class UStaticMesh;

/** Render-only copies. Projectile queries and their item indices stay on each column. */
UCLASS()
class MERIDIANSQUAD_API ULobbyFacingPool : public UWorldSubsystem
{
    GENERATED_BODY()
public:
    static bool ShouldPool(const UDemoColumnCladding* Owner);
    uint64 Add(UDemoColumnCladding* Owner, int32 Tile, UInstancedStaticMeshComponent* Source, const FTransform& World);
    void Update(UDemoColumnCladding* Owner, uint64 Handle, const FTransform& World);
    void Remove(UDemoColumnCladding* Owner, uint64 Handle);
    void RemoveOwner(UDemoColumnCladding* Owner);
    bool Matches(const UDemoColumnCladding* Owner, uint64 Handle, const FTransform& World) const;
    virtual void Deinitialize() override;
private:
    struct FKey
    {
        FIntPoint Cell;
        TWeakObjectPtr<UStaticMesh> Mesh;
        bool operator==(const FKey& Other) const { return Cell == Other.Cell && Mesh == Other.Mesh; }
        friend uint32 GetTypeHash(const FKey& Key) { return HashCombine(GetTypeHash(Key.Cell), GetTypeHash(Key.Mesh)); }
    };
    struct FGroup
    {
        FKey Key;
        TWeakObjectPtr<UInstancedStaticMeshComponent> Part;
        TArray<uint64> Handles;
    };
    struct FEntry
    {
        TWeakObjectPtr<UDemoColumnCladding> Owner;
        int32 Tile = INDEX_NONE;
        int32 Group = INDEX_NONE;
        int32 Instance = INDEX_NONE;
    };
    UPROPERTY(Transient) TObjectPtr<AActor> RenderActor;
    TArray<FGroup> Groups;
    TArray<int32> FreeGroups;
    TMap<FKey, int32> GroupLookup;
    TMap<uint64, FEntry> Entries;
    // Never reset during a world's lifetime, including F6 and empty-pool reuse.
    uint64 NextHandle = 1;
    int32 FindGroup(const FKey& Key);
    void RemoveInstance(int32 Group, int32 Instance);
    static FIntPoint CellFor(const UDemoColumnCladding* Owner);
};
