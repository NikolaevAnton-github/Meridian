#include "LobbyFacingPool.h"
#include "DemoColumnCladding.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "HAL/IConsoleManager.h"

namespace
{
TAutoConsoleVariable<int32> SharedFacing(TEXT("msq.Lobby.SharedFacing"), 2,
    TEXT("Lobby facing at spawn: 0 original, 1 three-column pilot, 2 spatial groups. No asset changes."));
}

FIntPoint ULobbyFacingPool::CellFor(const UDemoColumnCladding* Owner)
{
    const FVector P = Owner->GetOwner()->GetActorLocation();
    return FIntPoint(FMath::FloorToInt((P.X + 1000.) / 2000.), FMath::FloorToInt(P.Y / 1360.));
}

bool ULobbyFacingPool::ShouldPool(const UDemoColumnCladding* Owner)
{
    const int32 Mode = SharedFacing.GetValueOnGameThread();
    return Owner->GetWorld()->IsGameWorld() && Owner->GetOwner()->ActorHasTag(TEXT("LobbyColumns01")) &&
        (Mode >= 2 || (Mode == 1 && CellFor(Owner) == FIntPoint(-1, -1)));
}

int32 ULobbyFacingPool::FindGroup(const FKey& Key)
{
    if (const int32* Found = GroupLookup.Find(Key)) return *Found;
    if (!IsValid(RenderActor))
    {
        FActorSpawnParameters Params;
        Params.ObjectFlags |= RF_Transient;
        Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
        RenderActor = GetWorld()->SpawnActor<AActor>(Params);
        if (!RenderActor) return INDEX_NONE;
        RenderActor->Tags.Add(TEXT("LobbyFacingRenderOnly"));
    }
    const int32 Index = FreeGroups.IsEmpty() ? Groups.AddDefaulted() : FreeGroups.Pop(EAllowShrinking::No);
    FGroup& Group = Groups[Index];
    Group.Key = Key;
    auto* Part = NewObject<UInstancedStaticMeshComponent>(RenderActor, NAME_None, RF_Transient);
    Part->SetStaticMesh(Key.Mesh.Get());
    Part->SetMobility(EComponentMobility::Movable);
    Part->SetWorldTransform(FTransform::Identity);
    Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Part->SetCanEverAffectNavigation(false);
    Part->SetRemoveSwap();
    Part->ComponentTags.Add(TEXT("LobbyFacingRenderOnly"));
    RenderActor->AddInstanceComponent(Part);
    Part->RegisterComponent();
    Group.Part = Part;
    GroupLookup.Add(Key, Index);
    return Index;
}

uint64 ULobbyFacingPool::Add(UDemoColumnCladding* Owner, int32 Tile,
    UInstancedStaticMeshComponent* Source, const FTransform& World)
{
    if (!Source || !Source->GetStaticMesh()) return 0;
    // This lane only uses the audited mesh-default materials. A future override
    // must keep its original renderer rather than silently merging unlike parts.
    for (int32 I = 0; I < Source->GetNumMaterials(); ++I)
        if (Source->GetMaterial(I) != Source->GetStaticMesh()->GetMaterial(I)) return 0;
    const int32 G = FindGroup({CellFor(Owner), Source->GetStaticMesh()});
    if (G == INDEX_NONE) return 0;
    auto& Group = Groups[G];
    const uint64 Handle = NextHandle++;
    const int32 Instance = Group.Part->AddInstance(World, true);
    Group.Handles.Add(Handle);
    Entries.Add(Handle, {Owner, Tile, G, Instance});
    return Handle;
}

void ULobbyFacingPool::RemoveInstance(int32 G, int32 Instance)
{
    auto& Group = Groups[G];
    if (auto* Part = Group.Part.Get()) Part->RemoveInstance(Instance);
    Group.Handles.RemoveAtSwap(Instance, EAllowShrinking::No);
    if (Group.Handles.IsValidIndex(Instance)) Entries.FindChecked(Group.Handles[Instance]).Instance = Instance;
    if (Group.Handles.IsEmpty())
    {
        if (auto* Part = Group.Part.Get()) Part->DestroyComponent();
        Group.Part.Reset();
        GroupLookup.Remove(Group.Key);
        FreeGroups.Add(G);
    }
}

void ULobbyFacingPool::Update(UDemoColumnCladding* Owner, uint64 Handle, const FTransform& World)
{
    FEntry* Entry = Entries.Find(Handle);
    if (!Entry || Entry->Owner != Owner) return;
    const FKey OldKey = Groups[Entry->Group].Key;
    const FIntPoint Cell = CellFor(Owner);
    if (Cell != OldKey.Cell)
    {
        // Moving a column must not stretch a previously local render group.
        const int32 G = FindGroup({Cell, OldKey.Mesh});
        if (G == INDEX_NONE) return;
        RemoveInstance(Entry->Group, Entry->Instance);
        Entry->Group = G;
        Entry->Instance = Groups[G].Part->AddInstance(World, true);
        Groups[G].Handles.Add(Handle);
    }
    else if (auto* Part = Groups[Entry->Group].Part.Get())
        Part->UpdateInstanceTransform(Entry->Instance, World, true, true, true);
}

void ULobbyFacingPool::Remove(UDemoColumnCladding* Owner, uint64 Handle)
{
    const FEntry* Entry = Entries.Find(Handle);
    if (!Entry || Entry->Owner != Owner) return;
    RemoveInstance(Entry->Group, Entry->Instance);
    Entries.Remove(Handle);
}

void ULobbyFacingPool::RemoveOwner(UDemoColumnCladding* Owner)
{
    TArray<uint64> Handles;
    for (const auto& Pair : Entries) if (Pair.Value.Owner == Owner) Handles.Add(Pair.Key);
    for (uint64 Handle : Handles) Remove(Owner, Handle);
}

bool ULobbyFacingPool::Matches(const UDemoColumnCladding* Owner, uint64 Handle, const FTransform& World) const
{
    const FEntry* Entry = Entries.Find(Handle);
    if (!Entry || Entry->Owner != Owner) return false;
    const auto& Group = Groups[Entry->Group];
    const auto* Part = Group.Part.Get();
    FTransform Actual;
    return Part && Group.Handles.IsValidIndex(Entry->Instance) && Group.Handles[Entry->Instance] == Handle &&
        Part->GetInstanceTransform(Entry->Instance, Actual, true) && Actual.Equals(World, .001f) &&
        !Part->IsQueryCollisionEnabled() && Part->CastShadow && Part->IsVisible();
}

void ULobbyFacingPool::Deinitialize()
{
    if (IsValid(RenderActor)) RenderActor->Destroy();
    RenderActor = nullptr;
    Entries.Reset();
    Groups.Reset();
    FreeGroups.Reset();
    GroupLookup.Reset();
    Super::Deinitialize();
}
