#include "DemoColumnCladding.h"
#include "DemoColumnScatter.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "GeometryCollection/GeometryCollectionComponent.h"
#include "GeometryCollection/GeometryCollectionObject.h"
#include "Serialization/JsonSerializer.h"

namespace
{
const FName TileTag(TEXT("DemoColumnCladding"));
constexpr TCHAR TileDataPath[] = TEXT("/Game/Experiments/DemoTiledColumn01/Correction03/DA_Cladding03.DA_Cladding03");
constexpr TCHAR VariedTileDataPath[] = TEXT("/Game/Experiments/DemoTiledColumn01/Correction04/DA_Cladding04.DA_Cladding04");
}

UDemoColumnCladding::UDemoColumnCladding()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.TickGroup = TG_PostPhysics;
}

void UDemoColumnCladding::Initialize()
{
    if (!Groups.IsEmpty()) return;
    Data = LoadObject<UDemoColumnCladdingData>(nullptr, GetOwner()->ActorHasTag(TEXT("DemoColumnCladding04")) ? VariedTileDataPath : TileDataPath);
    Concrete = GetOwner()->FindComponentByClass<UGeometryCollectionComponent>();
    if (!Data || !Concrete) return;
    // PIE duplicates the saved editor preview. Rebuild its instance mapping once.
    TArray<UInstancedStaticMeshComponent*> Existing;
    GetOwner()->GetComponents(Existing);
    for (auto* Part : Existing) if (Part->ComponentHasTag(TileTag)) Part->DestroyComponent();
    const int32 Count = Data->Tiles.Num();
    GroupByTile.Init(INDEX_NONE, Count);
    InstanceByTile.Init(INDEX_NONE, Count);
    Hits.Init(0, Count);
    LastWorld.SetNum(Count);
    Velocities.Init(FVector::ZeroVector, Count);
    TMap<UStaticMesh*, int32> MeshGroups;
    for (int32 I = 0; I < Count; ++I)
    {
        const auto& Tile = Data->Tiles[I];
        if (!Tile.Mesh) continue;
        int32 GroupIndex;
        if (const auto* Found = MeshGroups.Find(Tile.Mesh)) GroupIndex = *Found;
        else
        {
            GroupIndex = Groups.AddDefaulted();
            MeshGroups.Add(Tile.Mesh, GroupIndex);
            const FName Name = MakeUniqueObjectName(GetOwner(), UInstancedStaticMeshComponent::StaticClass(),
                *FString::Printf(TEXT("Cladding_%03d"), GroupIndex));
            auto* Part = NewObject<UInstancedStaticMeshComponent>(GetOwner(), Name, RF_Transactional);
            Part->SetStaticMesh(Tile.Mesh);
            Part->SetMobility(EComponentMobility::Movable);
            Part->SetupAttachment(Concrete);
            Part->SetRelativeTransform(FTransform::Identity);
            Part->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
            Part->SetCollisionObjectType(ECC_WorldDynamic);
            Part->SetCollisionResponseToAllChannels(ECR_Ignore);
            Part->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
            Part->SetCanEverAffectNavigation(false);
            Part->ComponentTags.Add(TileTag);
            Part->SetRemoveSwap();
            GetOwner()->AddInstanceComponent(Part);
            Part->RegisterComponent();
            Groups[GroupIndex].Instances = Part;
        }
        auto& Group = Groups[GroupIndex];
        GroupByTile[I] = GroupIndex;
        InstanceByTile[I] = Group.Instances->AddInstance(Tile.RestTransform);
        Group.Tiles.Add(I);
        LastWorld[I] = Tile.RestTransform * Concrete->GetComponentTransform();
    }
}

void UDemoColumnCladding::BeginPlay()
{
    Super::BeginPlay();
    Initialize();
    if (Concrete)
    {
        AddTickPrerequisiteComponent(Concrete);
        // Enlarging the demo multiplies debris mass. Contact impacts must not
        // turn one rifle hit into a full-height secondary destruction cascade.
        Concrete->SetEnableDamageFromCollision(false);
        auto Propagation = Concrete->DamagePropagationData;
        Propagation.bEnabled = false;
        Propagation.BreakDamagePropagationFactor = 0.f;
        Propagation.ShockDamagePropagationFactor = 0.f;
        Concrete->SetDamagePropagationData(Propagation);
    }
}

void UDemoColumnCladding::Detach(int32 TileIndex, const FVector& Push)
{
    if (!Data || !InstanceByTile.IsValidIndex(TileIndex) || InstanceByTile[TileIndex] == INDEX_NONE) return;
    auto& Group = Groups[GroupByTile[TileIndex]];
    const int32 Instance = InstanceByTile[TileIndex];
    const FTransform Pose = LastWorld[TileIndex];
    const int32 MovedTile = Group.Tiles.Last();
    if (!Group.Instances->RemoveInstance(Instance)) return;
    Group.Tiles.RemoveAtSwap(Instance);
    if (Instance < Group.Tiles.Num()) InstanceByTile[MovedTile] = Instance;
    InstanceByTile[TileIndex] = INDEX_NONE;
    if (Pose.GetScale3D().GetAbsMin() < .02f) return;
    FActorSpawnParameters Params;
    Params.Owner = GetOwner();
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    auto* Actor = GetWorld()->SpawnActor<AStaticMeshActor>(AStaticMeshActor::StaticClass(), Pose, Params);
    if (!Actor) return;
    auto* Part = Actor->GetStaticMeshComponent();
    Part->SetMobility(EComponentMobility::Movable);
    Part->SetStaticMesh(Data->Tiles[TileIndex].Mesh);
    Part->SetWorldTransform(Pose);
    Part->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    Part->SetCollisionObjectType(ECC_PhysicsBody);
    Part->SetCollisionResponseToAllChannels(ECR_Ignore);
    Part->SetCollisionResponseToChannel(ECC_WorldStatic, ECR_Block);
    Part->SetCanEverAffectNavigation(false);
    Part->SetSimulatePhysics(true);
    Part->SetPhysicsLinearVelocity(Velocities[TileIndex] + Push);
    FRandomStream Spin(HashCombineFast(GetTypeHash(TileIndex), ImpactSerial + 9173u));
    Part->SetPhysicsAngularVelocityInDegrees(Spin.VRand() * Spin.FRandRange(280.f, 720.f));
    Actor->SetLifeSpan(12.f);
    Debris.Add(Actor);
}

bool UDemoColumnCladding::HandleImpact(FHitResult& Hit)
{
    ++ImpactSerial;
    if (Concrete && Hit.GetComponent() == Concrete)
    {
        DamageConcrete(Hit);
        return true;
    }
    auto* Part = Cast<UInstancedStaticMeshComponent>(Hit.GetComponent());
    if (!Data || !Part || !Part->ComponentHasTag(TileTag)) return false;
    for (auto& Group : Groups)
    {
        if (Group.Instances != Part) continue;
        if (!Group.Tiles.IsValidIndex(Hit.Item)) return true;
        const int32 TileIndex = Group.Tiles[Hit.Item];
        const auto& Tile = Data->Tiles[TileIndex];
        ++Hits[TileIndex];
        if (!Tile.bBonded || Hits[TileIndex] > 1)
        {
            Detach(TileIndex, FacingScatter(TileIndex, Hit));
            // Tiny adjacent chips can leave the same impact crater together.
            // Large pieces and bonded neighbours retain their own support.
            for (int32 I = 0; I < Data->Tiles.Num(); ++I)
            {
                const auto& Nearby = Data->Tiles[I];
                if (InstanceByTile[I] == INDEX_NONE || Nearby.bBonded || Nearby.AreaCm2 <= 0.f || Nearby.AreaCm2 > 450.f) continue;
                if (FVector::DotProduct(LastWorld[I].GetUnitAxis(EAxis::X), Hit.ImpactNormal) < .8f) continue;
                if (FVector::DistSquared(LastWorld[I].GetLocation(), Hit.ImpactPoint) < FMath::Square(24.f))
                    Detach(I, FacingScatter(I, Hit));
            }
            return true;
        }
        // Resolve the currently active Chaos body immediately behind this tile.
        // Rest leaf IDs may be disabled inside a cluster and cannot receive a
        // useful direct strain. This trace stays on this one concrete component.
        FHitResult Substrate;
        FCollisionQueryParams Query(SCENE_QUERY_STAT(DemoColumnSubstrate), false);
        if (Concrete->LineTraceComponent(Substrate, Hit.ImpactPoint + Hit.ImpactNormal * 4.f,
            Hit.ImpactPoint - Hit.ImpactNormal * 80.f, Query)) DamageConcrete(Substrate);
        return true;
    }
    return true;
}

void UDemoColumnCladding::DamageConcrete(const FHitResult& Hit)
{
    // Keep the vendor hierarchy and thresholds. Select the nearest child of
    // the actual hit body instead of relying on an unscaled spherical field to
    // reach the enlarged cluster centres. No graph propagation or global blast.
    Concrete->ApplyExternalStrain(Hit.Item, Hit.ImpactPoint, 0.f, 0, 0.f, 2000000.f);
    ApplyDemoColumnScatter(Concrete, Hit, ImpactSerial);
}

FVector UDemoColumnCladding::FacingScatter(int32 Tile, const FHitResult& Hit) const
{
    FRandomStream Spread(HashCombineFast(GetTypeHash(Tile), ImpactSerial + 4711u));
    FVector Radial = LastWorld[Tile].GetLocation() - Hit.ImpactPoint;
    if (!Radial.Normalize()) Radial = Spread.VRand();
    const float SizeFactor = FMath::Clamp(FMath::Sqrt(700.f / FMath::Max(Data->Tiles[Tile].AreaCm2, 150.f)), .8f, 1.3f);
    return (Hit.ImpactNormal * 250.f + Radial * 200.f + FVector(0, 0, 70)) * SizeFactor;
}

void UDemoColumnCladding::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    if (!Data || !Concrete || !GetWorld()->IsGameWorld()) return;
    const auto& Bones = Concrete->GetComponentSpaceTransforms3f();
    const FTransform ComponentWorld = Concrete->GetComponentTransform();
    TSet<int32> ChangedGroups;
    for (int32 I = 0; I < Data->Tiles.Num(); ++I)
    {
        if (InstanceByTile[I] == INDEX_NONE) continue;
        const auto& Tile = Data->Tiles[I];
        if (!Bones.IsValidIndex(Tile.Bone)) continue;
        const FTransform Local = Tile.RelativeToBone * FTransform(Bones[Tile.Bone]);
        const FTransform World = Local * ComponentWorld;
        Velocities[I] = ((World.GetLocation() - LastWorld[I].GetLocation()) / FMath::Max(DeltaTime, .001f)).GetClampedToMaxSize(1500.f);
        const bool bMoved = FVector::DistSquared(Local.GetLocation(), Tile.RestTransform.GetLocation()) > FMath::Square(.8f) ||
            Local.GetRotation().AngularDistance(Tile.RestTransform.GetRotation()) > FMath::DegreesToRadians(3.f);
        LastWorld[I] = World;
        if (Concrete->IsFullyDecayed() || World.GetScale3D().GetAbsMin() < .02f)
        {
            Detach(I, FVector::ZeroVector);
            continue;
        }
        if (!Tile.bBonded && Concrete->IsRootBroken() && bMoved)
        {
            Detach(I, FVector::ZeroVector);
            continue;
        }
        auto& Group = Groups[GroupByTile[I]];
        FTransform Current;
        Group.Instances->GetInstanceTransform(InstanceByTile[I], Current);
        if (!Local.Equals(Current, .0001f))
        {
            Group.Instances->UpdateInstanceTransform(InstanceByTile[I], Local, false, false, true);
            ChangedGroups.Add(GroupByTile[I]);
        }
    }
    for (const int32 G : ChangedGroups) Groups[G].Instances->MarkRenderStateDirty();
    Debris.RemoveAll([](AActor* Actor) { return !IsValid(Actor); });
}

FString UDemoColumnCladding::GetState() const
{
    const auto Out = MakeShared<FJsonObject>();
    int32 Attached = 0, Clean = 0, Bonded = 0, HitCount = 0;
    for (int32 I = 0; I < InstanceByTile.Num(); ++I)
    {
        HitCount += Hits[I];
        if (InstanceByTile[I] == INDEX_NONE) continue;
        ++Attached;
        if (Data->Tiles[I].bBonded) ++Bonded; else ++Clean;
    }
    Out->SetNumberField(TEXT("attached"), Attached);
    Out->SetNumberField(TEXT("clean_attached"), Clean);
    Out->SetNumberField(TEXT("bonded_attached"), Bonded);
    Out->SetNumberField(TEXT("tile_hits"), HitCount);
    Out->SetNumberField(TEXT("debris"), Debris.Num());
    if (Concrete)
    {
        Out->SetBoolField(TEXT("root_broken"), Concrete->IsRootBroken());
        Out->SetStringField(TEXT("root_world"), Concrete->GetRootCurrentTransform().ToString());
        Out->SetStringField(TEXT("component_world"), Concrete->GetComponentTransform().ToString());
        const auto& Bones = Concrete->GetComponentSpaceTransforms3f();
        if (!Bones.IsEmpty()) Out->SetStringField(TEXT("root_local"), Bones[0].ToString());
    }
    FString Result;
    FJsonSerializer::Serialize(Out, TJsonWriterFactory<>::Create(&Result));
    return Result;
}

void UDemoColumnCladding::EndPlay(const EEndPlayReason::Type Reason)
{
    for (AActor* Actor : Debris) if (IsValid(Actor)) Actor->Destroy();
    Debris.Reset();
    Super::EndPlay(Reason);
}
