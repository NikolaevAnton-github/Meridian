#include "DemoColumnCladding.h"
#include "DemoColumnScatter.h"
#include "LobbyFacingPool.h"
#include "NGDPropComponent.h"
#include "DestructionFragmentWorld.h"
#include "ProfilingDebugging/CsvProfiler.h"
#include "HAL/IConsoleManager.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/BoxComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "PhysicalMaterials/PhysicalMaterial.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GeometryCollection/GeometryCollectionComponent.h"
#include "GeometryCollection/GeometryCollectionObject.h"
#include "GeometryCollection/GeometryCollection.h"
#include "GeometryCollection/GeometryCollectionAlgo.h"
#include "GeometryCollection/GeometryCollectionEngineRemoval.h"
#include "GeometryCollectionProxyData.h"
#include "PhysicsProxy/GeometryCollectionPhysicsProxy.h"
#include "Chaos/PhysicsObjectCollisionInterface.h"
#include "Chaos/Convex.h"
#include "Chaos/GeometryQueries.h"
#include "Chaos/Box.h"
#include "PhysicsEngine/PhysicsObjectExternalInterface.h"
#include "Engine/CollisionProfile.h"
#include "Serialization/JsonSerializer.h"

CSV_DEFINE_CATEGORY(LobbyColumns, true);

namespace
{
const FName TileTag(TEXT("DemoColumnCladding"));
TAutoConsoleVariable<int32> ActiveFacing(TEXT("msq.Lobby.ActiveFacing"), 1,
    TEXT("Update lobby tile poses only when their carrier moves; keep fracture and debris support checks live."));
constexpr TCHAR TileDataPath[] = TEXT("/Game/Experiments/DemoTiledColumn01/Correction03/DA_Cladding03.DA_Cladding03");
constexpr TCHAR VariedTileDataPath[] = TEXT("/Game/Experiments/DemoTiledColumn01/Correction04/DA_Cladding04.DA_Cladding04");

bool ConcreteBottom(const Chaos::FPBDRigidParticle* Particle, FVector& Bottom)
{
    if (!Particle || !Particle->GetGeometry()) return false;
    Bottom = FVector(0., 0., DBL_MAX);
    const FTransform Body(Particle->GetR(), Particle->GetX());
    Particle->GetGeometry()->VisitLeafObjects([&](const Chaos::FImplicitObject* Shape,
        const Chaos::FRigidTransform3& Local, int32, int32, int32)
    {
        if (const auto* Convex = Shape->GetObject<Chaos::FConvex>())
            for (const auto& Vertex : Convex->GetVertices())
            {
                const FVector Point = Body.TransformPosition(Local.TransformPosition(FVector(Vertex)));
                if (Point.Z < Bottom.Z) Bottom = Point;
            }
    });
    return Bottom.Z != DBL_MAX;
}
}

UDemoColumnCladding::UDemoColumnCladding()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.TickGroup = TG_PostPhysics;
}

void UDemoColumnCladding::Initialize()
{
    if (!Groups.IsEmpty()) return;
    static uint64 NextFragmentOwner = 1; // GT only; never recycled, even across world recreation.
    FragmentOwner = NextFragmentOwner++;
    if (const auto* Prop = GetOwner()->FindComponentByClass<UNGDPropComponent>())
        FragmentGeneration = uint32(Prop->ResetGeneration);
    bStackingExperiment = GetOwner()->ActorHasTag(TEXT("DemoColumnStacking08"));
    bRefinedExperiment = GetOwner()->ActorHasTag(TEXT("DemoColumnRefined07"));
    bCoarseExperiment = GetOwner()->ActorHasTag(TEXT("DemoColumnCoarse06"));
    bSurfaceExperiment = bCoarseExperiment || GetOwner()->ActorHasTag(TEXT("DemoColumnSurface05"));
    Data = LoadObject<UDemoColumnCladdingData>(nullptr, GetOwner()->ActorHasTag(TEXT("LobbyColumns01"))
        ? TEXT("/Game/OpeningLobby/LobbyColumns01/DA_Cladding01.DA_Cladding01") : bStackingExperiment
        ? TEXT("/Game/Experiments/DemoTiledColumn01/Correction08/DA_Cladding08.DA_Cladding08") : bRefinedExperiment
        ? TEXT("/Game/Experiments/DemoTiledColumn01/Correction07/DA_Cladding07.DA_Cladding07") : bCoarseExperiment
        ? TEXT("/Game/Experiments/DemoTiledColumn01/Correction06/DA_Cladding06.DA_Cladding06") : bSurfaceExperiment
        ? TEXT("/Game/Experiments/DemoTiledColumn01/Correction05/DA_Cladding05.DA_Cladding05")
        : GetOwner()->ActorHasTag(TEXT("DemoColumnCladding04")) ? VariedTileDataPath : TileDataPath);
    Concrete = GetOwner()->FindComponentByClass<UGeometryCollectionComponent>();
    if (!Data || !Concrete) return;
    // PIE duplicates the saved editor preview. Rebuild its instance mapping once.
    TArray<UInstancedStaticMeshComponent*> Existing;
    GetOwner()->GetComponents(Existing);
    for (auto* Part : Existing) if (Part->ComponentHasTag(TileTag)) Part->DestroyComponent();
    const int32 Count = Data->Tiles.Num();
    NextLooseLocal = Count;
    GroupByTile.Init(INDEX_NONE, Count);
    InstanceByTile.Init(INDEX_NONE, Count);
    Hits.Init(0, Count);
    TileStateRevisions.Init(1, Count);
    TilePoseRevisions.Init(1, Count);
    LastWorld.SetNum(Count);
    Velocities.Init(FVector::ZeroVector, Count);
    RenderHandles.Init(0, Count);
    CompactSectionByTile.Init(INDEX_NONE, Count);
    if (ULobbyFacingPool::ShouldPool(this)) FacingPool = GetWorld()->GetSubsystem<ULobbyFacingPool>();
    if (FacingPool)
        CompactData=LoadObject<UDemoColumnCompactData>(nullptr,
            TEXT("/Game/OpeningLobby/DestructionScaling01/Candidate01/DA_CompactFacing.DA_CompactFacing"),nullptr,LOAD_NoWarn);
    if (CompactData && CompactData->Source != Data) CompactData=nullptr;
    CarrierByTile.Init(INDEX_NONE, Count);
    CarrierRelative.SetNum(Count);
    CarriedTiles.Init(false, Count);
    if (bCoarseExperiment && Concrete->GetRestCollection())
    {
        const auto Rest = Concrete->GetRestCollection()->GetGeometryCollection();
        GeometryCollectionAlgo::GlobalMatrices(Rest->Transform, Rest->Parent, RestBones);
    }
    TMap<UStaticMesh*, int32> MeshGroups;
    for (int32 I = 0; I < Count; ++I)
    {
        const auto& Tile = Data->Tiles[I];
        for (const int32 Support : Tile.SupportBones) TilesBySupport.FindOrAdd(Support).Add(I);
        if (!Tile.Mesh) continue;
        if (bRefinedExperiment && Tile.AreaCm2 >= 30.f && Tile.AreaCm2 <= 300.f)
        {
            const FVector Extent = Tile.Mesh->GetBounds().BoxExtent;
            if (FMath::Min(Extent.Y, Extent.Z) > 1.f && FMath::Max(Extent.Y, Extent.Z) / FMath::Min(Extent.Y, Extent.Z) < 2.5f)
                ChipTemplates.Add(I);
        }
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
        CarrierByTile[I] = Tile.Bone;
        CarrierRelative[I] = Tile.RelativeToBone;
        TilesByCarrier.FindOrAdd(Tile.Bone).Add(I);
    }
    if (FacingPool && CompactData)
    {
        CompactHandles.Init(0,CompactData->Sections.Num());
        for (int32 S=0; S<CompactData->Sections.Num(); ++S)
        {
            const auto& Section=CompactData->Sections[S];
            auto* Source=NewObject<UStaticMeshComponent>(GetOwner(),NAME_None,RF_Transient);
            Source->SetStaticMesh(Section.Mesh);
            CompactHandles[S]=FacingPool->AddDebris(this,-2-S,Source,Concrete->GetComponentTransform());
            if (CompactHandles[S])
                for (const int32 Tile : Section.Tiles) if (CompactSectionByTile.IsValidIndex(Tile)) CompactSectionByTile[Tile]=S;
        }
    }
    if (FacingPool)
        for (auto& Group : Groups)
        {
            bool bComplete = true;
            for (const int32 Tile : Group.Tiles)
            {
                if (CompactSectionByTile[Tile]!=INDEX_NONE) continue;
                RenderHandles[Tile] = FacingPool->Add(this, Tile, Group.Instances, LastWorld[Tile]);
                bComplete &= RenderHandles[Tile] != 0;
            }
            if (bComplete)
            {
                Group.Instances->SetVisibility(false);
                Group.Instances->SetCastShadow(false);
            }
            else
                for (const int32 Tile : Group.Tiles)
                {
                    FacingPool->Remove(this, RenderHandles[Tile]);
                    RenderHandles[Tile] = 0;
                }
        }
}

void UDemoColumnCladding::BeginPlay()
{
    Super::BeginPlay();
    Initialize();
    if (bStackingExperiment)
    {
        FragmentWorld = GetWorld()->GetSubsystem<UDestructionFragmentWorld>();
        if (FragmentWorld) FragmentWorld->RegisterOwner(this);
    }
    DebrisMaterial = LoadObject<UPhysicalMaterial>(nullptr,
        TEXT("/Game/Experiments/DemoTiledColumn01/Correction07/PM_HeavyConcrete07.PM_HeavyConcrete07"));
    if (Concrete)
    {
        if (bRefinedExperiment)
            if (auto* Heavy = LoadObject<UPhysicalMaterial>(nullptr, TEXT("/Game/Experiments/DemoTiledColumn01/Correction07/PM_HeavyConcrete07.PM_HeavyConcrete07")))
                Concrete->SetPhysMaterialOverride(Heavy);
        if (bStackingExperiment)
        {
            const auto Rest = Concrete->GetRestCollection()->GetGeometryCollection();
            FBox Bounds(ForceInit);
            for (int32 G = 0; G < Rest->BoundingBox.Num(); ++G)
                Bounds += Rest->BoundingBox[G].TransformBy(RestBones[Rest->TransformIndex[G]]);
            CoreBarrier = NewObject<UBoxComponent>(GetOwner(), TEXT("ProtectedCoreCollision"));
            CoreBarrier->SetMobility(EComponentMobility::Movable);
            CoreBarrier->SetupAttachment(Concrete);
            CoreBarrier->SetBoxExtent(FVector(34.5,34.5,Bounds.GetExtent().Z));
            CoreBarrier->SetRelativeLocation(FVector(0,0,Bounds.GetCenter().Z));
            CoreBarrier->SetCollisionEnabled(ECollisionEnabled::PhysicsOnly);
            CoreBarrier->SetCollisionObjectType(ECC_WorldStatic);
            CoreBarrier->SetCollisionResponseToAllChannels(ECR_Ignore);
            CoreBarrier->SetCollisionResponseToChannel(ECC_PhysicsBody,ECR_Block);
            CoreBarrier->SetCanEverAffectNavigation(false);
            GetOwner()->AddInstanceComponent(CoreBarrier);
            CoreBarrier->RegisterComponent();
        }
        AddTickPrerequisiteComponent(Concrete);
        // Enlarging the demo multiplies debris mass. Contact impacts must not
        // turn one rifle hit into a full-height secondary destruction cascade.
        Concrete->SetEnableDamageFromCollision(false);
        auto Propagation = Concrete->DamagePropagationData;
        Propagation.bEnabled = false;
        Propagation.BreakDamagePropagationFactor = 0.f;
        Propagation.ShockDamagePropagationFactor = 0.f;
        Concrete->SetDamagePropagationData(Propagation);
        if (bSurfaceExperiment)
        {
            // Debris must clear the remainder instead of lodging in its hulls.
            // Keep floor, pawn and weapon responses; no debris-to-debris contacts.
            Concrete->SetCollisionResponseToChannel(ECC_Destructible, ECR_Ignore);
            // The candidate asset has RemoveOnMaxSleep disabled. Keep this
            // component permission for explicit per-piece decay rendering only.
            Concrete->bAllowRemovalOnBreak = false;
            Concrete->bAllowRemovalOnSleep = !FragmentWorld;
            const auto Rest = Concrete->GetRestCollection()->GetGeometryCollection();
            ConcreteAge.Init(-1.f, Rest->Transform.Num());
            ConcreteStillTime.Init(0.f, Rest->Transform.Num());
            for (int32 B = 0; B < Rest->Transform.Num(); ++B)
                if (Rest->SimulationType[B] == FGeometryCollection::FST_Rigid && Rest->Children[B].IsEmpty())
                { ConcreteLeaves.Add(B); ConcreteLeafSet.Add(B); }
        }
    }
}

void UDemoColumnCladding::Detach(int32 TileIndex, const FVector& Push)
{
    if (!Data || !InstanceByTile.IsValidIndex(TileIndex) || InstanceByTile[TileIndex] == INDEX_NONE) return;
    const FTransform Pose = LastWorld[TileIndex];
    if (Pose.GetScale3D().GetAbsMin() < .02f) return;
    FActorSpawnParameters Params;
    Params.Owner = GetOwner();
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    auto* Actor = FragmentWorld ? FragmentWorld->Acquire(this, Data->Tiles[TileIndex].Mesh, DebrisMaterial, Pose, TileIndex)
        : GetWorld()->SpawnActor<AStaticMeshActor>(AStaticMeshActor::StaticClass(), Pose, Params);
    if (!Actor) return;
    if (!RemoveTileInstance(TileIndex))
    {
        if (FragmentWorld) FragmentWorld->Return(Actor); else Actor->Destroy();
        return;
    }
    auto* Part = Actor->GetStaticMeshComponent();
    Part->SetMobility(EComponentMobility::Movable);
    Part->SetStaticMesh(Data->Tiles[TileIndex].Mesh);
    Part->SetWorldTransform(Pose);
    Part->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    Part->SetCollisionObjectType(ECC_PhysicsBody);
    Part->SetCollisionResponseToAllChannels(ECR_Ignore);
    Part->SetCollisionResponseToChannel(ECC_WorldStatic, ECR_Block);
    if (FragmentWorld) Part->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
    if (bStackingExperiment)
    {
        Part->SetCollisionResponseToChannel(ECC_PhysicsBody, ECR_Block);
        Part->SetUseCCD(true);
        Part->SetPhysMaterialOverride(Concrete->GetBodyInstance() ? Concrete->GetBodyInstance()->GetSimplePhysicalMaterial() : nullptr);
        if (!Data->Tiles[TileIndex].Shards.IsEmpty())
        {
            WholeTileSources.Add(Actor,TileIndex);
            Part->SetNotifyRigidBodyCollision(true);
            Part->OnComponentHit.AddDynamic(this,&UDemoColumnCladding::OnLooseTileImpact);
        }
    }
    Part->SetCanEverAffectNavigation(false);
    Part->SetSimulatePhysics(true);
    Part->SetPhysicsLinearVelocity(Velocities[TileIndex] + Push);
    FRandomStream Spin(HashCombineFast(GetTypeHash(TileIndex), ImpactSerial + 9173u));
    Part->SetPhysicsAngularVelocityInDegrees(Spin.VRand() * Spin.FRandRange(280.f, 720.f));
    Actor->SetLifeSpan(FragmentWorld ? 0.f : 12.f);
    Debris.Add(Actor);
}

bool UDemoColumnCladding::RemoveTileInstance(int32 TileIndex)
{
    if (!InstanceByTile.IsValidIndex(TileIndex) || InstanceByTile[TileIndex] == INDEX_NONE) return false;
    if (!ExpandCompactSection(TileIndex)) return false;
    auto& Group = Groups[GroupByTile[TileIndex]];
    const int32 Instance = InstanceByTile[TileIndex];
    const int32 MovedTile = Group.Tiles.Last();
    if (!Group.Instances->RemoveInstance(Instance)) return false;
    if (FacingPool && RenderHandles[TileIndex])
    {
        FacingPool->Remove(this, RenderHandles[TileIndex]);
        RenderHandles[TileIndex] = 0;
    }
    Group.Tiles.RemoveAtSwap(Instance);
    if (Instance < Group.Tiles.Num()) InstanceByTile[MovedTile] = Instance;
    InstanceByTile[TileIndex] = INDEX_NONE;
    ++TileStateRevisions[TileIndex];
    const int32 Carrier = CarrierByTile[TileIndex];
    if (auto* Tiles = TilesByCarrier.Find(Carrier))
    {
        Tiles->RemoveSingleSwap(TileIndex, EAllowShrinking::No);
        if (Tiles->IsEmpty())
        {
            TilesByCarrier.Remove(Carrier);
            LastCarrierWorld.Remove(Carrier);
            MovingCarriersLastTick.Remove(Carrier);
        }
    }
    return true;
}

bool UDemoColumnCladding::ExpandCompactSection(int32 Tile)
{
    if (!CompactSectionByTile.IsValidIndex(Tile) || CompactSectionByTile[Tile]==INDEX_NONE) return true;
    const int32 Section=CompactSectionByTile[Tile];
    for (const int32 I : CompactData->Sections[Section].Tiles)
    {
        if (InstanceByTile[I]==INDEX_NONE || RenderHandles[I]) continue;
        auto* Part=Groups[GroupByTile[I]].Instances.Get();
        Part->SetCastShadow(true);
        RenderHandles[I]=FacingPool->Add(this,I,Part,LastWorld[I]);
        Part->SetCastShadow(false);
        if (!RenderHandles[I])
        {
            for (const int32 J : CompactData->Sections[Section].Tiles)
            { FacingPool->Remove(this,RenderHandles[J]); RenderHandles[J]=0; }
            UE_LOG(LogTemp,Error,TEXT("Compact facing expansion failed for section %d"),Section);
            return false;
        }
    }
    FacingPool->Remove(this,CompactHandles[Section]); CompactHandles[Section]=0;
    for (const int32 I : CompactData->Sections[Section].Tiles) CompactSectionByTile[I]=INDEX_NONE;
    return true;
}

void UDemoColumnCladding::CarryTiles(int32 Bone)
{
    if (!bCoarseExperiment || ReleasedConcrete.Contains(Bone) || !RestBones.IsValidIndex(Bone)) return;
    ReleasedConcrete.Add(Bone);
    if (FragmentWorld) FragmentWorld->RegisterConcrete(this, Concrete, Bone);
    const TArray<int32>* Supported = TilesBySupport.Find(Bone);
    if (!Supported) return;
    for (const int32 I : *Supported)
    {
        const auto& Tile = Data->Tiles[I];
        if (InstanceByTile[I] == INDEX_NONE || CarriedTiles[I] || !Tile.SupportBones.Contains(Bone)) continue;
        const int32 Original = GroupByTile[I];
        int32 CarriedGroup;
        if (const auto* Found = CarriedGroupByOriginal.Find(Original)) CarriedGroup = *Found;
        else
        {
            CarriedGroup = Groups.AddDefaulted();
            auto* Part = NewObject<UInstancedStaticMeshComponent>(GetOwner(),
                MakeUniqueObjectName(GetOwner(), UInstancedStaticMeshComponent::StaticClass(), TEXT("CarriedFacing")));
            Part->SetStaticMesh(Tile.Mesh);
            Part->SetMobility(EComponentMobility::Movable);
            Part->SetupAttachment(Concrete);
            Part->SetRelativeTransform(FTransform::Identity);
            Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);
            if (bRefinedExperiment)
            {
                // Ray queries keep carried/settled facing shootable without
                // restoring simulation or pawn/debris contacts.
                Part->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
                Part->SetCollisionObjectType(ECC_WorldDynamic);
                Part->SetCollisionResponseToAllChannels(ECR_Ignore);
                Part->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
                Part->ComponentTags.Add(TileTag);
            }
            Part->SetCanEverAffectNavigation(false);
            Part->SetRemoveSwap();
            GetOwner()->AddInstanceComponent(Part);
            Part->RegisterComponent();
            Groups[CarriedGroup].Instances = Part;
            CarriedGroupByOriginal.Add(Original, CarriedGroup);
        }
        if (!RemoveTileInstance(I)) continue;
        CarriedTiles[I] = true;
        ++TileStateRevisions[I];
        CarrierByTile[I] = Bone;
        CarrierRelative[I] = Tile.RestTransform.GetRelativeTransform(RestBones[Bone]);
        TilesByCarrier.FindOrAdd(Bone).Add(I);
        DirtyCarriers.Add(Bone);
        GroupByTile[I] = CarriedGroup;
        InstanceByTile[I] = Groups[CarriedGroup].Instances->AddInstance(Tile.RestTransform);
        Groups[CarriedGroup].Tiles.Add(I);
        if (FacingPool)
        {
            auto* Part=Groups[CarriedGroup].Instances.Get();
            // The source may already be hidden after pooling another instance.
            Part->SetCastShadow(true);
            RenderHandles[I]=FacingPool->Add(this,I,Part,LastWorld[I]);
            if (RenderHandles[I]) { Part->SetVisibility(false); Part->SetCastShadow(false); }
        }
    }
}

FDestructionFragmentId UDemoColumnCladding::IdentifyHit(const FHitResult& Hit) const
{
    if (bEndingPlay || Hit.GetActor() != GetOwner()) return {};
    if (bSurfaceExperiment && Hit.GetComponent()==Concrete)
    {
        int32 Bone=Hit.Item;
        if (!ConcreteLeafSet.Contains(Bone))
        {
            // Resolve the exact authored leaf while the step-start collision
            // snapshot still exists, before earlier impacts mutate this cluster.
            TArray<Chaos::FPhysicsObjectHandle> Objects;
            Objects.Reserve(ConcreteLeaves.Num());
            for (const int32 Leaf : ConcreteLeaves)
                if (!RemovedConcrete.Contains(Leaf))
                    if (auto Object=Concrete->GetPhysicsObjectById(Leaf)) Objects.Add(Object);
            auto Read=FPhysicsObjectExternalInterface::LockRead(Objects);
            Chaos::FPhysicsObjectCollisionInterface_External Collision(Read.GetInterface());
            FVector Direction=(Hit.TraceEnd-Hit.TraceStart).GetSafeNormal();
            if (Direction.IsNearlyZero()) Direction=-Hit.ImpactNormal;
            ChaosInterface::FRaycastHit Result;
            Bone=INDEX_NONE;
            if (Collision.LineTrace(Objects,Hit.ImpactPoint-Direction*8.,Hit.ImpactPoint+Direction*500.,false,Result) && Result.Actor)
                if (const auto* Particle=Result.Actor->CastToRigidParticle())
                    if (auto* Proxy=Concrete->GetPhysicsProxy())
                        Bone=Proxy->GetItemIndexFromGTParticleNoInternalCluster_External(Particle).GetItemIndex();
        }
        if (ConcreteLeafSet.Contains(Bone)) return {FragmentOwner,FragmentGeneration,-2-Bone};
        return {};
    }
    for (const auto& Group : Groups)
        if (Group.Instances == Hit.GetComponent() && Group.Tiles.IsValidIndex(Hit.Item))
            return {FragmentOwner, FragmentGeneration, Group.Tiles[Hit.Item]};
    return {};
}

bool UDemoColumnCladding::RefreshHit(const FDestructionFragmentId& Id, FHitResult& Hit) const
{
    if (bEndingPlay || Id.Owner != FragmentOwner || Id.Generation != FragmentGeneration) return false;
    if (Id.Local < -1)
    {
        const int32 Bone=-2-Id.Local;
        if (!Concrete || !ConcreteLeafSet.Contains(Bone) || RemovedConcrete.Contains(Bone)) return false;
        Hit.Component=Concrete; Hit.Item=Bone; return true;
    }
    if (!InstanceByTile.IsValidIndex(Id.Local) || InstanceByTile[Id.Local] == INDEX_NONE) return false;
    Hit.Component = Groups[GroupByTile[Id.Local]].Instances;
    Hit.Item = InstanceByTile[Id.Local];
    return true;
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
        if (bRefinedExperiment && CarriedTiles[TileIndex])
        {
            CrumbleCarriedFacing(CarrierByTile[TileIndex], Hit.ImpactPoint, Hit.ImpactNormal, true);
            return true;
        }
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
        // Facing over a protected core still responds to this shot.
        if (bCoarseExperiment && !CarriedTiles[TileIndex]) Detach(TileIndex, FacingScatter(TileIndex, Hit));
        return true;
    }
    return true;
}

void UDemoColumnCladding::DamageConcrete(const FHitResult& Hit)
{
    if (bSurfaceExperiment)
    {
        ++ConcreteImpacts;
        LastConcreteBone = ConcreteLeafSet.Contains(Hit.Item) && !RemovedConcrete.Contains(Hit.Item) ? Hit.Item : INDEX_NONE;
        // The engine's generic leaf query also includes a broken root once it
        // loses its children. Its stale collision then masks the next real chip.
        // Trace only authored rigid leaves, including those in the live remainder.
        auto* Proxy = Concrete->GetPhysicsProxy();
        if (Proxy && LastConcreteBone == INDEX_NONE)
        {
            FVector Direction = (Hit.TraceEnd - Hit.TraceStart).GetSafeNormal();
            if (Direction.IsNearlyZero()) Direction = -Hit.ImpactNormal;
            const FVector Start = Hit.ImpactPoint - Direction * 8.;
            const FVector End = Hit.ImpactPoint + Direction * 500.;
            TArray<Chaos::FPhysicsObjectHandle> Objects;
            Objects.Reserve(ConcreteLeaves.Num());
            for (const int32 Bone : ConcreteLeaves)
            {
                if ((!bRefinedExperiment && (RetainedConcrete.Contains(Bone) || PendingConcrete.Contains(Bone))) || RemovedConcrete.Contains(Bone)) continue;
                if (auto* Object = Concrete->GetPhysicsObjectById(Bone)) Objects.Add(Object);
            }
            auto Interface = FPhysicsObjectExternalInterface::LockRead(Objects);
            Chaos::FPhysicsObjectCollisionInterface_External Collision(Interface.GetInterface());
            ChaosInterface::FRaycastHit LeafHit;
            if (Collision.LineTrace(Objects, Start, End, false, LeafHit) && LeafHit.Actor)
                if (const auto* Particle = LeafHit.Actor->CastToRigidParticle())
                    LastConcreteBone = Proxy->GetItemIndexFromGTParticleNoInternalCluster_External(Particle).GetItemIndex();
        }
        const bool bProtectedCore = bCoarseExperiment && LastConcreteBone != INDEX_NONE && !Data->SurfaceBones.Contains(LastConcreteBone);
        UE_LOG(LogTemp, Display, TEXT("DemoColumn target hit=%u item=%d bone=%d protected=%d point=%s"), ImpactSerial, Hit.Item, LastConcreteBone, bProtectedCore, *Hit.ImpactPoint.ToCompactString());
        if (bProtectedCore) { ++ProtectedCoreImpacts; return; }
        if (LastConcreteBone != INDEX_NONE)
        {
            if (bRefinedExperiment && ReleasedConcrete.Contains(LastConcreteBone))
            {
                CrumbleCarriedFacing(LastConcreteBone, Hit.ImpactPoint, Hit.ImpactNormal, true);
                if (FragmentWorld)
                    FragmentWorld->Impulse(FragmentWorld->Select(Concrete, LastConcreteBone),
                        (Hit.TraceEnd-Hit.TraceStart).GetSafeNormal()*120.f);
                return;
            }
            CarryTiles(LastConcreteBone);
            ReleaseDemoColumnLeaf(Concrete, LastConcreteBone, Hit, ImpactSerial);
        }
        return;
    }
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
    CSV_SCOPED_TIMING_STAT(LobbyColumns, CladdingTick);
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    if (!Data || !Concrete || !GetWorld()->IsGameWorld()) return;
    const FTransform ComponentWorld = Concrete->GetComponentTransform();
    const FTransform RootTransform = Concrete->GetRootCurrentComponentSpaceTransform();
    if (FacingPool && !ComponentWorld.Equals(LastUpdatedComponentTransform,0.f))
        for (const uint64 Handle : CompactHandles) if (Handle) FacingPool->Update(this,Handle,ComponentWorld);
    const bool bStationary = FullUpdateCount > 0 && ComponentWorld.Equals(LastUpdatedComponentTransform, .0001f) &&
        RootTransform.Equals(LastUpdatedRootTransform, .0001f);
    // Keep a cheap sentinel for external movement and fracture, including damage
    // that did not arrive through HandleImpact. Damaged columns retain the full
    // update path for carried facing, moving debris and retention maintenance.
    bIdleLastTick = bStackingExperiment && ImpactSerial == 0 && Concrete->GetRootIndex() != INDEX_NONE &&
        !Concrete->IsRootBroken() && !Concrete->IsFullyDecayed() && ReleasedConcrete.IsEmpty() &&
        Debris.IsEmpty() && CeramicDebris.IsEmpty() && bStationary && bHadStationaryUpdate;
    if (bIdleLastTick)
    {
        ++SkippedIdleUpdates;
        return;
    }
    // Run one stationary update after movement to clear tile velocities before
    // sleeping; a later shot must not inherit the column's last moving velocity.
    bHadStationaryUpdate = bStationary;
    LastUpdatedComponentTransform = ComponentWorld;
    LastUpdatedRootTransform = RootTransform;
    ++FullUpdateCount;
    const auto& Bones = Concrete->GetComponentSpaceTransforms3f();
    if (bCoarseExperiment && Concrete->GetDynamicCollection())
    {
        FGeometryCollectionDynamicStateFacade State(*Concrete->GetDynamicCollection());
        for (const int32 Bone : Data->SurfaceBones)
            if (!ReleasedConcrete.Contains(Bone) && State.HasBrokenOff(Bone) && !State.HasInternalClusterParent(Bone)) CarryTiles(Bone);
    }
    const bool bActiveFacing = GetOwner()->ActorHasTag(TEXT("LobbyColumns01")) && ActiveFacing.GetValueOnGameThread() != 0;
    TArray<int32, TInlineAllocator<768>> TilesToUpdate;
    if (bActiveFacing)
    {
        TSet<int32> MovingNow;
        for (const auto& Pair : TilesByCarrier)
        {
            const int32 Bone = Pair.Key;
            if (!Bones.IsValidIndex(Bone)) continue;
            const FTransform Pose = FTransform(Bones[Bone]) * ComponentWorld;
            const FTransform* Previous = LastCarrierWorld.Find(Bone);
            // Exact carrier equality avoids accumulating sub-tolerance movement
            // or leaving a tiny last moving velocity on an otherwise idle tile.
            const bool bChanged = !Previous || !Pose.Equals(*Previous, 0.f);
            if (bChanged) MovingNow.Add(Bone);
            if (bChanged || MovingCarriersLastTick.Contains(Bone) || DirtyCarriers.Contains(Bone) || Concrete->IsFullyDecayed())
                TilesToUpdate.Append(Pair.Value);
            else TilePoseUpdatesSkipped += Pair.Value.Num();
            LastCarrierWorld.Add(Bone, Pose);
        }
        MovingCarriersLastTick = MoveTemp(MovingNow);
        DirtyCarriers.Reset();
        // Preserve the original tile processing order even when multiple carriers
        // wake together; detach/retention randomness must not follow TMap order.
        TilesToUpdate.Sort();
    }
    else
        for (int32 I = 0; I < Data->Tiles.Num(); ++I) TilesToUpdate.Add(I);
    TSet<int32> ChangedGroups;
    for (const int32 I : TilesToUpdate)
    {
        if (InstanceByTile[I] == INDEX_NONE) continue;
        ++TilePoseUpdates;
        const auto& Tile = Data->Tiles[I];
        const int32 Bone = CarrierByTile[I];
        if (!Bones.IsValidIndex(Bone)) continue;
        FDestructionPoseInput Input;
        Input.Stamp = {{FragmentOwner, FragmentGeneration, I}, TileStateRevisions[I], TilePoseRevisions[I]};
        Input.Relative = CarrierRelative[I]; Input.Carrier = FTransform(Bones[Bone]);
        Input.Component = ComponentWorld; Input.Previous = LastWorld[I]; Input.DeltaTime = DeltaTime;
        const FDestructionPoseOutput Result = DestructionFragmentMath::Pose(Input);
        const FTransform& Local = Result.Local;
        const FTransform& World = Result.World;
        Velocities[I] = Result.Velocity;
        if (!World.Equals(LastWorld[I], 0.f)) ++TilePoseRevisions[I];
        const bool bMoved = FVector::DistSquared(Local.GetLocation(), Tile.RestTransform.GetLocation()) > FMath::Square(.8f) ||
            Local.GetRotation().AngularDistance(Tile.RestTransform.GetRotation()) > FMath::DegreesToRadians(3.f);
        if (CompactSectionByTile[I]!=INDEX_NONE && !Local.Equals(Tile.RestTransform,.0001f) && !ExpandCompactSection(I)) continue;
        if (FacingPool && RenderHandles[I] && !World.Equals(LastWorld[I], .0001f))
            FacingPool->Update(this, RenderHandles[I], World);
        LastWorld[I] = World;
        if (Concrete->IsFullyDecayed() || World.GetScale3D().GetAbsMin() < .02f)
        {
            if (CarriedTiles[I]) RemoveTileInstance(I); else Detach(I, FVector::ZeroVector);
            continue;
        }
        if (!CarriedTiles[I] && !Tile.bBonded && Concrete->IsRootBroken() && bMoved)
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
    if (bRefinedExperiment) UpdateFacingImpacts();
    if (bSurfaceExperiment) UpdateDebris(DeltaTime);
}

int32 UDemoColumnCladding::RetentionSlotsUsed() const
{
    return RetainedTiles.Num() + RetainedConcrete.Num() + PendingConcrete.Num();
}

int32 UDemoColumnCladding::RetentionSector(const FVector& Position) const
{
    const FVector Local = Concrete->GetComponentTransform().InverseTransformPosition(Position);
    return FMath::Abs(Local.X) >= FMath::Abs(Local.Y) ? (Local.X >= 0. ? 0 : 2) : (Local.Y >= 0. ? 1 : 3);
}

void UDemoColumnCladding::RetentionSectorCounts(TArray<int32>& Total, TArray<int32>& Tiles) const
{
    Total.Init(0, 4); Tiles.Init(0, 4);
    for (const auto& Weak : RetainedTiles)
        if (const auto* Actor = Weak.Get())
        {
            const int32 Sector = RetentionSector(Actor->GetActorLocation());
            ++Total[Sector]; ++Tiles[Sector];
        }
    const auto* Proxy = Concrete->GetPhysicsProxy();
    if (!Proxy) return;
    for (const auto* Bones : {&RetainedConcrete, &PendingConcrete})
        for (const int32 Bone : *Bones)
            if (const auto* Particle = Proxy->GetParticleByIndex_External(Bone))
                ++Total[RetentionSector(Particle->GetX())];
}

bool UDemoColumnCladding::MakeRetentionRoom(const FVector& Position, bool bTile)
{
    if (!bStackingExperiment) return RetentionSlotsUsed() < 50;
    const bool bTilesFull = bTile && RetainedTiles.Num() >= 48;
    if (RetentionSlotsUsed() < 80 && !bTilesFull) return true;
    // Spread replacement over time instead of clearing a visible pile at once.
    if (ReplacementsThisPoll >= 2) return false;
    auto* Proxy = Concrete->GetPhysicsProxy();
    auto* Dynamic = Concrete->GetDynamicCollection();
    if (!Proxy || !Dynamic) return false;
    TArray<int32> Counts, TileCounts;
    RetentionSectorCounts(Counts, TileCounts);
    const int32 Incoming = RetentionSector(Position);
    struct FPiece
    {
        AActor* Actor = nullptr;
        UStaticMeshComponent* Part = nullptr;
        int32 Bone = INDEX_NONE;
        FBox Bounds = FBox(ForceInit);
        FVector Bottom = FVector::ZeroVector;
        int32 Sector = 0;
        bool bRetained = false;
        double Score = 0.;
    };
    TArray<FPiece> Pieces;
    for (AActor* Actor : Debris)
        if (IsValid(Actor))
            if (auto* Part = Actor->FindComponentByClass<UStaticMeshComponent>())
            {
                FPiece Piece;
                Piece.Actor = Actor; Piece.Part = Part; Piece.Bounds = Part->Bounds.GetBox();
                const FVector Below = Part->Bounds.Origin - FVector(0, 0, 10000. + Part->Bounds.BoxExtent.Z);
                if (Part->GetClosestPointOnCollision(Below, Piece.Bottom) < 0.f) continue;
                Piece.Sector = RetentionSector(Actor->GetActorLocation());
                Piece.bRetained = RetainedTiles.Contains(Actor);
                Pieces.Add(Piece);
            }
    for (const int32 Bone : ReleasedConcrete)
    {
        if (RemovedConcrete.Contains(Bone)) continue;
        const auto* Particle = Proxy->GetParticleByIndex_External(Bone);
        FPiece Piece;
        if (!Particle || Particle->Disabled() || !ConcreteBottom(Particle, Piece.Bottom)) continue;
        const auto Box = Particle->GetGeometry()->BoundingBox();
        Piece.Bounds = FBox(FVector(Box.Min()), FVector(Box.Max())).TransformBy(FTransform(Particle->GetR(), Particle->GetX()));
        Piece.Bone = Bone; Piece.Sector = RetentionSector(Particle->GetX());
        Piece.bRetained = RetainedConcrete.Contains(Bone);
        Pieces.Add(Piece);
    }
    FVector Eye = FVector::ZeroVector;
    FRotator View = FRotator::ZeroRotator;
    const auto* Controller = GetWorld()->GetFirstPlayerController();
    if (Controller) Controller->GetPlayerViewPoint(Eye, View);
    TArray<int32> Candidates;
    for (int32 I = 0; I < Pieces.Num(); ++I)
    {
        auto& Piece = Pieces[I];
        if (!Piece.bRetained || Piece.Sector == Incoming ||
            Counts[Piece.Sector] <= FMath::Max(16, Counts[Incoming] + 1)) continue;
        // Keep 32 places available for concrete. Ceramic borrowing must also
        // improve the ceramic distribution rather than just exchange neighbours.
        if (bTilesFull && (!Piece.Actor || TileCounts[Piece.Sector] <= TileCounts[Incoming] + 1)) continue;
        const bool bBehindView = Controller && FVector::DotProduct(Piece.Bounds.GetCenter() - Eye, View.Vector()) < -Piece.Bounds.GetExtent().Size();
        Piece.Score = Counts[Piece.Sector] * 1.e12 + (bBehindView ? 1.e10 : 0.) +
            (Piece.Actor ? 1.e9 : 0.) - FMath::Min(Piece.Bounds.GetVolume(), 1.e8);
        Candidates.Add(I);
    }
    Candidates.Sort([&](int32 A, int32 B) { return Pieces[A].Score > Pieces[B].Score; });
    for (const int32 Index : Candidates)
    {
        const auto& Candidate = Pieces[Index];
        auto MaySupport = [&](const FPiece& Other)
        {
            // Match the grounding ray, including its tolerance. This also protects
            // pending concrete and loose pieces resting on the proposed victim.
            return Candidate.Bounds.ExpandBy(FVector(1., 1., 8.)).IsInsideOrOn(Other.Bottom);
        };
        bool bSupports = false;
        if (Candidate.Part)
        {
            FCollisionQueryParams Params(SCENE_QUERY_STAT(DemoRetentionSupport), false);
            for (int32 J = 0; J < Pieces.Num() && !bSupports; ++J)
                if (J != Index && MaySupport(Pieces[J]))
                {
                    FHitResult Hit;
                    bSupports = Candidate.Part->LineTraceComponent(Hit, Pieces[J].Bottom + FVector(0,0,5),
                        Pieces[J].Bottom - FVector(0,0,8), Params);
                }
        }
        else
        {
            TArray<Chaos::FPhysicsObjectHandle> Objects{Concrete->GetPhysicsObjectById(Candidate.Bone)};
            if (!Objects[0]) continue;
            auto Interface = FPhysicsObjectExternalInterface::LockRead(Objects);
            Chaos::FPhysicsObjectCollisionInterface_External Collision(Interface.GetInterface());
            for (int32 J = 0; J < Pieces.Num() && !bSupports; ++J)
                if (J != Index && MaySupport(Pieces[J]))
                {
                    ChaosInterface::FRaycastHit Hit;
                    bSupports = Collision.LineTrace(Objects, Pieces[J].Bottom + FVector(0,0,5),
                        Pieces[J].Bottom - FVector(0,0,8), false, Hit);
                }
        }
        if (bSupports) { ++RetentionSupportVetoes; continue; }
        if (Candidate.Actor)
        {
            RetainedTiles.Remove(Candidate.Actor);
            RetainedTileSupport.Remove(Candidate.Actor);
            DebrisStillTime.Remove(Candidate.Actor);
            WholeTileSources.Remove(Candidate.Actor);
            Candidate.Actor->Destroy();
        }
        else
        {
            FGeometryCollectionDecayDynamicFacade Decay(*Dynamic);
            if (!Decay.IsValid()) Decay.AddAttributes();
            Decay.SetDecay(Candidate.Bone, 1.f);
            Dynamic->MakeDirty();
            RetainedConcrete.Remove(Candidate.Bone);
            RemovedConcrete.Add(Candidate.Bone);
            Proxy->DisableParticles_External(TArray<int32>{Candidate.Bone});
        }
        ++RetentionReplacements; ++ReplacementsThisPoll; ++RetentionEvictions[Candidate.Sector];
        return true;
    }
    return false;
}

bool UDemoColumnCladding::HasStaticSupport(const FVector& Bottom) const
{
    FHitResult Hit;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(DemoColumnGround), false, GetOwner());
    return GetWorld()->LineTraceSingleByObjectType(Hit, Bottom + FVector(0, 0, 5), Bottom - FVector(0, 0, 8),
        FCollisionObjectQueryParams(ECC_WorldStatic), Params) && !Hit.bStartPenetrating && Hit.ImpactNormal.Z >= .65f;
}

bool UDemoColumnCladding::HasDebrisSupport(const FVector& Bottom, int32 ExcludedBone, const AActor* ExcludedActor, bool bRetainedOnly) const
{
    if (HasStaticSupport(Bottom)) return true;
    if (!bStackingExperiment) return false;
    const FVector Start = Bottom + FVector(0,0,5), End = Bottom - FVector(0,0,8);
    FCollisionQueryParams Params(SCENE_QUERY_STAT(DemoColumnPile),false,GetOwner());
    if (ExcludedActor) Params.AddIgnoredActor(ExcludedActor);
    TArray<FHitResult> HitsOnPile;
    GetWorld()->LineTraceMultiByObjectType(HitsOnPile,Start,End,FCollisionObjectQueryParams(ECC_PhysicsBody),Params);
    for (const auto& Hit : HitsOnPile)
        if (!Hit.bStartPenetrating && Hit.ImpactNormal.Z >= .5f &&
            (bRetainedOnly ? RetainedTiles.Contains(Hit.GetActor()) : Debris.Contains(Hit.GetActor()))) return true;
    auto* Proxy = Concrete ? Concrete->GetPhysicsProxy() : nullptr;
    if (!Proxy) return false;
    TArray<Chaos::FPhysicsObjectHandle> Objects;
    for (const int32 Bone : bRetainedOnly ? RetainedConcrete : ReleasedConcrete)
        if (Bone != ExcludedBone && !RemovedConcrete.Contains(Bone))
        {
            const auto* Particle = Proxy->GetParticleByIndex_External(Bone);
            if (Particle && !Particle->Disabled())
                if (auto* Object = Concrete->GetPhysicsObjectById(Bone)) Objects.Add(Object);
        }
    if (Objects.IsEmpty()) return false;
    auto Interface = FPhysicsObjectExternalInterface::LockRead(Objects);
    Chaos::FPhysicsObjectCollisionInterface_External Collision(Interface.GetInterface());
    ChaosInterface::FRaycastHit Hit;
    return Collision.LineTrace(Objects,Start,End,false,Hit) && Hit.WorldNormal.Z >= .5f && Hit.Distance > .01f;
}

void UDemoColumnCladding::OnLooseTileImpact(UPrimitiveComponent* HitComponent, AActor* OtherActor,
    UPrimitiveComponent* OtherComponent, FVector NormalImpulse, const FHitResult& Hit)
{
    if (!bStackingExperiment || bEndingPlay || !HitComponent || !OtherComponent || Hit.ImpactNormal.Z < .25f) return;
    AActor* Actor = HitComponent->GetOwner();
    const int32* Source = WholeTileSources.Find(Actor);
    if (!Source || NormalImpulse.Size() / FMath::Max(HitComponent->GetMass(), .01f) < 65.f) return;
    const int32 Tile = *Source;
    const FTransform Pose = HitComponent->GetComponentTransform();
    const FVector Velocity = HitComponent->GetPhysicsLinearVelocity();
    WholeTileSources.Remove(Actor);
    Debris.Remove(Actor); CeramicDebris.Remove(Actor);
    if (FragmentWorld) FragmentWorld->Return(Actor); else Actor->Destroy();
    ++IndependentTileBreaks;
    SpawnTileShards(Tile,Pose,Velocity,Hit.ImpactNormal);
}

void UDemoColumnCladding::SpawnTileShards(int32 Tile, const FTransform& Pose, const FVector& Velocity, const FVector& Normal)
{
    TArray<FDemoColumnTileShard> Shards = Data->Tiles[Tile].Shards;
    if (Shards.IsEmpty())
    {
        FDemoColumnTileShard Whole;
        Whole.Mesh = Data->Tiles[Tile].Mesh; Whole.RelativeToTile = FTransform::Identity; Whole.AreaCm2 = Data->Tiles[Tile].AreaCm2;
        Shards.Add(Whole);
    }
    FRandomStream Random(HashCombineFast(Tile,++ImpactSerial+80117u));
    for (const auto& Shard : Shards)
    {
        CeramicDebris.RemoveAll([&](AActor* Actor) { return !IsValid(Actor) || RetainedTiles.Contains(Actor); });
        while (!FragmentWorld && CeramicDebris.Num() >= 32)
        {
            CeramicDebris[0]->Destroy();
            CeramicDebris.RemoveAt(0);
        }
        FTransform World = Shard.RelativeToTile * Pose;
        World.AddToTranslation(Normal*2.f);
        FActorSpawnParameters Params;
        Params.Owner = GetOwner();
        Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
        auto* Actor = FragmentWorld ? FragmentWorld->Acquire(this, Shard.Mesh, DebrisMaterial, World, NextLooseLocal++)
            : GetWorld()->SpawnActor<AStaticMeshActor>(AStaticMeshActor::StaticClass(),World,Params);
        if (!Actor) continue;
        auto* Part = Actor->GetStaticMeshComponent();
        Part->SetMobility(EComponentMobility::Movable);
        Part->SetStaticMesh(Shard.Mesh);
        Part->SetWorldTransform(World);
        Part->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
        Part->SetCollisionObjectType(ECC_PhysicsBody);
        Part->SetCollisionResponseToAllChannels(ECR_Ignore);
        Part->SetCollisionResponseToChannel(ECC_WorldStatic,ECR_Block);
        Part->SetCollisionResponseToChannel(ECC_PhysicsBody,ECR_Block);
        if (FragmentWorld) Part->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
        Part->SetCanEverAffectNavigation(false);
        Part->SetPhysMaterialOverride(DebrisMaterial);
        Part->SetUseCCD(true);
        Part->SetSimulatePhysics(true);
        FVector Spread = (World.GetLocation()-Pose.GetLocation()).GetSafeNormal();
        Part->SetPhysicsLinearVelocity(Velocity.GetClampedToMaxSize(120.f)*.25f + Spread*35.f + Normal*30.f + FVector(0,0,30));
        Part->SetPhysicsAngularVelocityInRadians(Random.VRand()*Random.FRandRange(1.f,2.5f));
        Actor->SetLifeSpan(FragmentWorld ? 0.f : 12.f);
        Debris.Add(Actor);
        CeramicDebris.Add(Actor);
        ++SpawnedCeramicChips;
    }
}

void UDemoColumnCladding::UpdateFacingImpacts()
{
    CSV_SCOPED_TIMING_STAT(LobbyColumns, FacingImpacts);
    CeramicDebris.RemoveAll([&](AActor* Actor) { return !IsValid(Actor) || (bStackingExperiment && RetainedTiles.Contains(Actor)); });
    for (auto It = WholeTileSources.CreateIterator(); It; ++It) if (!It.Key().IsValid()) It.RemoveCurrent();
    const auto* Proxy = Concrete ? Concrete->GetPhysicsProxy() : nullptr;
    if (!Proxy) return;
    for (const int32 Bone : ReleasedConcrete)
    {
        if (GroundCrumbled.Contains(Bone) || RemovedConcrete.Contains(Bone)) continue;
        const auto* Particle = Proxy->GetParticleByIndex_External(Bone);
        if (!Particle || Particle->Disabled()) continue;
        const FVector Velocity = Particle->GetV();
        const FVector Previous = PreviousConcreteVelocity.FindRef(Bone);
        PreviousConcreteVelocity.Add(Bone, Velocity);
        FVector Bottom;
        // A downward velocity arrested at the actual collision hull is a floor
        // impact. A wall contact or a body merely passing the floor is not.
        if (Previous.Z < -100.f && Velocity.Z - Previous.Z > 60.f &&
            ConcreteBottom(Particle, Bottom) && HasDebrisSupport(Bottom,Bone,nullptr,false))
        {
            GroundCrumbled.Add(Bone);
            CrumbleCarriedFacing(Bone, Bottom, FVector::UpVector, false);
        }
    }
}

void UDemoColumnCladding::CrumbleCarriedFacing(int32 Bone, const FVector& Point, const FVector& Normal, bool bShot)
{
    if (!bRefinedExperiment || !Data || ChipTemplates.IsEmpty()) return;
    TArray<int32> Candidates;
    for (int32 I = 0; I < InstanceByTile.Num(); ++I)
        if (InstanceByTile[I] != INDEX_NONE && CarriedTiles[I] && CarrierByTile[I] == Bone)
            Candidates.Add(I);
    Candidates.Sort([&](int32 A, int32 B)
    {
        return FVector::DistSquared(LastWorld[A].GetLocation(), Point) < FVector::DistSquared(LastWorld[B].GetLocation(), Point);
    });
    const int32 Count = FMath::Min(Candidates.Num(), bShot ? 1 : bStackingExperiment ? Candidates.Num() : 2);
    if (!Count) return;
    if (bShot) ++ShotCrumbleEvents; else ++GroundCrumbleEvents;
    FRandomStream Random(HashCombineFast(GetTypeHash(Bone), ++ImpactSerial + 70117u));
    for (int32 C = 0; C < Count; ++C)
    {
        const int32 Tile = Candidates[C];
        const FTransform Pose = LastWorld[Tile];
        if (!RemoveTileInstance(Tile)) continue;
        ++CrumbledTiles;
        if (bStackingExperiment)
        {
            SpawnTileShards(Tile,Pose,Velocities[Tile],Normal);
            continue;
        }
        const FVector Half = Data->Tiles[Tile].Mesh->GetBounds().BoxExtent * Pose.GetScale3D().GetAbs();
        for (int32 K = 0; K < 5; ++K)
        {
            CeramicDebris.RemoveAll([](AActor* Actor) { return !IsValid(Actor); });
            while (CeramicDebris.Num() >= 32)
            {
                if (IsValid(CeramicDebris[0])) CeramicDebris[0]->Destroy();
                CeramicDebris.RemoveAt(0);
            }
            auto* Mesh = Data->Tiles[ChipTemplates[Random.RandRange(0, ChipTemplates.Num()-1)]].Mesh.Get();
            const FVector MeshHalf = Mesh->GetBounds().BoxExtent;
            const float Width = FMath::Clamp(FMath::Sqrt(Data->Tiles[Tile].AreaCm2 / 5.f) * Pose.GetScale3D().GetAbsMax(), 6.f, 18.f);
            const float Scale = Width / (2.f * FMath::Max(MeshHalf.Y, MeshHalf.Z));
            FVector Location = Pose.GetLocation() + Pose.GetUnitAxis(EAxis::Y) * Random.FRandRange(-Half.Y*.7f, Half.Y*.7f)
                + Pose.GetUnitAxis(EAxis::Z) * Random.FRandRange(-Half.Z*.7f, Half.Z*.7f) + Normal * 3.f;
            if (!bShot) Location.Z = FMath::Max(Location.Z, Point.Z + Width*.6f + 2.f);
            const FTransform ChipPose(Pose.GetRotation(), Location, FVector(FMath::Max(Scale, .5f), Scale, Scale));
            FActorSpawnParameters Params;
            Params.Owner = GetOwner();
            Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
            auto* Actor = GetWorld()->SpawnActor<AStaticMeshActor>(AStaticMeshActor::StaticClass(), ChipPose, Params);
            if (!Actor) continue;
            auto* Part = Actor->GetStaticMeshComponent();
            Part->SetMobility(EComponentMobility::Movable);
            Part->SetStaticMesh(Mesh);
            Part->SetWorldTransform(ChipPose);
            Part->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
            Part->SetCollisionObjectType(ECC_PhysicsBody);
            Part->SetCollisionResponseToAllChannels(ECR_Ignore);
            Part->SetCollisionResponseToChannel(ECC_WorldStatic, ECR_Block);
            Part->SetCanEverAffectNavigation(false);
            Part->SetUseCCD(true);
            Part->SetSimulatePhysics(true);
            Part->SetPhysicsLinearVelocity(Velocities[Tile].GetClampedToMaxSize(120.f)*.25f +
                Random.VRand()*Random.FRandRange(35.f, 80.f) + Normal*45.f + FVector(0,0,65));
            Part->SetPhysicsAngularVelocityInRadians(Random.VRand()*Random.FRandRange(3.f, 6.f));
            Actor->SetLifeSpan(4.f);
            CeramicDebris.Add(Actor);
            ++SpawnedCeramicChips;
        }
    }
}

void UDemoColumnCladding::UpdateDebris(float DeltaTime)
{
    CSV_SCOPED_TIMING_STAT(LobbyColumns, DebrisUpdate);
    if (FragmentWorld) return; // Shared reversible lifecycle replaces retention/expiry.
    DebrisPollTime += DeltaTime;
    if (DebrisPollTime < .25f) return;
    const float Elapsed = DebrisPollTime;
    const float StillStep = FMath::Min(Elapsed, .3f);
    DebrisPollTime = 0.f;
    ReplacementsThisPoll = 0;
    for (auto It = RetainedTiles.CreateIterator(); It; ++It) if (!It->IsValid()) It.RemoveCurrent();
    for (auto It = DebrisStillTime.CreateIterator(); It; ++It) if (!It.Key().IsValid()) It.RemoveCurrent();
    for (AActor* Actor : Debris)
    {
        if (!IsValid(Actor) || RetainedTiles.Contains(Actor)) continue;
        auto* Part = Actor->FindComponentByClass<UStaticMeshComponent>();
        if (!Part) continue;
        float& Still = DebrisStillTime.FindOrAdd(Actor);
        const bool bSlow = Part->GetPhysicsLinearVelocity().SizeSquared() < 25.f &&
            Part->GetPhysicsAngularVelocityInRadians().SizeSquared() < .04f;
        FVector Bottom;
        const FVector Below = Part->Bounds.Origin - FVector(0, 0, 10000. + Part->Bounds.BoxExtent.Z);
        const bool bSupported = bSlow && Part->GetClosestPointOnCollision(Below, Bottom) >= 0.f && HasDebrisSupport(Bottom,INDEX_NONE,Actor,true);
        Still = bSupported ? Still + StillStep : 0.f;
        if (bSlow && !bSupported) Part->WakeAllRigidBodies();
        if (bStackingExperiment && Still >= 1.f)
        {
            bool bOverlapping = false;
            for (const auto& Weak : RetainedTiles)
                if (const auto* Other = Weak.Get())
                    if (auto* OtherPart = Other->FindComponentByClass<UStaticMeshComponent>())
                    {
                        const FVector Normal = Part->GetComponentTransform().GetUnitAxis(EAxis::X);
                        if (!Part->Bounds.GetBox().Intersect(OtherPart->Bounds.GetBox()) ||
                            FMath::Abs(FVector::DotProduct(Normal, OtherPart->GetComponentTransform().GetUnitAxis(EAxis::X))) < .96f) continue;
                        auto* Body = Part->GetBodyInstance();
                        auto* OtherBody = OtherPart->GetBodyInstance();
                        const FVector OtherNormal = OtherPart->GetComponentTransform().GetUnitAxis(EAxis::X);
                        if (Body && OtherBody &&
                            ((Body->OverlapTestForBody(Part->GetComponentLocation()+Normal*.3, Part->GetComponentQuat(), OtherBody) &&
                              Body->OverlapTestForBody(Part->GetComponentLocation()-Normal*.3, Part->GetComponentQuat(), OtherBody)) ||
                             (OtherBody->OverlapTestForBody(OtherPart->GetComponentLocation()+OtherNormal*.3, OtherPart->GetComponentQuat(), Body) &&
                              OtherBody->OverlapTestForBody(OtherPart->GetComponentLocation()-OtherNormal*.3, OtherPart->GetComponentQuat(), Body))))
                        { bOverlapping = true; break; }
                    }
            // A sleeping contact may still penetrate. Let the solver separate it
            // or let its normal lifetime expire; never freeze that intersection.
            if (bOverlapping) { Still = 0.f; Part->WakeAllRigidBodies(); continue; }
        }
        if (Still < 1.f || !MakeRetentionRoom(Part->GetComponentLocation(), true)) continue;
        const FTransform Pose = Part->GetComponentTransform();
        Part->SetSimulatePhysics(false);
        Part->SetCollisionEnabled(bStackingExperiment ? ECollisionEnabled::QueryAndPhysics : ECollisionEnabled::NoCollision);
        Part->SetWorldTransform(Pose);
        Actor->SetLifeSpan(0.f);
        RetainedTiles.Add(Actor);
        RetainedTileSupport.Add(Actor, Bottom);
    }
    auto* Proxy = Concrete->GetPhysicsProxy();
    auto* Dynamic = Concrete->GetDynamicCollection();
    if (!Proxy || !Dynamic) return;
    FGeometryCollectionDynamicStateFacade State(*Dynamic);
    TArray<int32> Evict;
    TArray<int32> ReleasedLeaves;
    const bool bActiveFacing = bCoarseExperiment && GetOwner()->ActorHasTag(TEXT("LobbyColumns01")) && ActiveFacing.GetValueOnGameThread() != 0;
    if (bActiveFacing)
    {
        // The per-tick external-fracture sentinel populates ReleasedConcrete
        // before this poll. Keep the original ascending retention order.
        ReleasedLeaves = ReleasedConcrete.Array();
        ReleasedLeaves.Sort();
    }
    for (const int32 Bone : bActiveFacing ? ReleasedLeaves : ConcreteLeaves)
    {
        // An anchored core leaf may leave a cluster without becoming debris.
        if (bCoarseExperiment && !Data->SurfaceBones.Contains(Bone)) continue;
        if (RetainedConcrete.Contains(Bone) || PendingConcrete.Contains(Bone) || RemovedConcrete.Contains(Bone)) continue;
        const auto* Particle = Proxy->GetParticleByIndex_External(Bone);
        if (!Particle || Particle->Disabled() || !State.HasBrokenOff(Bone) || State.HasInternalClusterParent(Bone)) continue;
        float& Age = ConcreteAge[Bone];
        if (Age < 0.f) KeepDemoColumnLeafAwake(Concrete, Bone);
        Age = FMath::Max(0.f, Age) + Elapsed;
        float& Still = ConcreteStillTime[Bone];
        const bool bSlow = Particle->GetV().SizeSquared() < 25. && Particle->GetW().SizeSquared() < .04;
        FVector Bottom;
        const bool bSupported = bSlow && ConcreteBottom(Particle, Bottom) && HasDebrisSupport(Bottom,Bone,nullptr,true);
        Still = bSupported ? Still + StillStep : 0.f;
        if (bSlow && !bSupported) KeepDemoColumnLeafAwake(Concrete, Bone);
        if (Still >= 1.f && MakeRetentionRoom(Particle->GetX(), false))
        {
            PendingConcrete.Add(Bone);
            TWeakObjectPtr<UDemoColumnCladding> WeakThis(this);
            FreezeDemoColumnLeaf(Concrete, Bone, [WeakThis, Bone](bool bFrozen)
            {
                auto* Self = WeakThis.Get();
                if (!Self || Self->bEndingPlay) return;
                Self->PendingConcrete.Remove(Bone);
                if (!bFrozen) { Self->ConcreteStillTime[Bone] = 0.f; return; }
                Self->RetainedConcrete.Add(Bone);
                // The engine UI profile is query-only: Visibility blocks, all
                // physical channels overlap. It keeps exposed retained concrete
                // shootable without simulation, floor contacts or pawn blocking.
                if (Self->bStackingExperiment) ConfigureDemoColumnDebrisCollision(Self->Concrete,Bone);
                else Self->Concrete->SetPerParticleCollisionProfileName(TArray<int32>{Bone}, Self->bRefinedExperiment
                    ? FName(TEXT("UI")) : UCollisionProfile::NoCollision_ProfileName);
            });
        }
        else if (Age >= 12.f)
        {
            Evict.Add(Bone);
            RemovedConcrete.Add(Bone);
        }
    }
    if (Evict.Num())
    {
        FGeometryCollectionDecayDynamicFacade Decay(*Dynamic);
        if (!Decay.IsValid()) Decay.AddAttributes();
        for (const int32 Bone : Evict) Decay.SetDecay(Bone, 1.f);
        Dynamic->MakeDirty();
        Proxy->DisableParticles_External(MoveTemp(Evict));
    }
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
    Out->SetBoolField(TEXT("persistent_fragments"), FragmentWorld != nullptr);
    Out->SetNumberField(TEXT("fragment_owner"), double(FragmentOwner));
    Out->SetNumberField(TEXT("fragment_generation"), FragmentGeneration);
    Out->SetBoolField(TEXT("idle"), bIdleLastTick);
    Out->SetNumberField(TEXT("full_updates"), static_cast<double>(FullUpdateCount));
    Out->SetNumberField(TEXT("idle_updates_skipped"), static_cast<double>(SkippedIdleUpdates));
    int32 SharedTiles = 0, RenderMismatches = 0;
    if (FacingPool)
        for (int32 I = 0; I < RenderHandles.Num(); ++I)
            if (RenderHandles[I])
            {
                ++SharedTiles;
                FTransform QueryWorld;
                const auto* Part = Groups[GroupByTile[I]].Instances.Get();
                if (!Part || !Part->GetInstanceTransform(InstanceByTile[I], QueryWorld, true) ||
                    !FacingPool->Matches(this, RenderHandles[I], QueryWorld)) ++RenderMismatches;
            }
    Out->SetNumberField(TEXT("shared_tiles"), SharedTiles);
    int32 CompactSections=0;
    for (const uint64 Handle : CompactHandles) CompactSections+=Handle!=0;
    Out->SetNumberField(TEXT("compact_sections"),CompactSections);
    Out->SetNumberField(TEXT("render_mismatches"), RenderMismatches);
    Out->SetNumberField(TEXT("tile_pose_updates"), static_cast<double>(TilePoseUpdates));
    Out->SetNumberField(TEXT("tile_pose_updates_skipped"), static_cast<double>(TilePoseUpdatesSkipped));
    int32 QueryMappingErrors = 0;
    for (int32 G = 0; G < Groups.Num(); ++G)
        for (int32 I = 0; I < Groups[G].Tiles.Num(); ++I)
        {
            const int32 Tile = Groups[G].Tiles[I];
            if (InstanceByTile[Tile] != I || GroupByTile[Tile] != G) ++QueryMappingErrors;
        }
    Out->SetNumberField(TEXT("query_mapping_errors"), QueryMappingErrors);
    double AttachedSpeed = 0.;
    for (int32 I = 0; I < InstanceByTile.Num(); ++I)
        if (InstanceByTile[I] != INDEX_NONE && !CarriedTiles[I]) AttachedSpeed = FMath::Max(AttachedSpeed, Velocities[I].Size());
    Out->SetNumberField(TEXT("max_attached_tile_speed"), AttachedSpeed);
    Out->SetBoolField(TEXT("surface_experiment"), bSurfaceExperiment);
    Out->SetNumberField(TEXT("retained_tiles"), RetainedTiles.Num());
    Out->SetNumberField(TEXT("retained_concrete"), RetainedConcrete.Num());
    Out->SetNumberField(TEXT("retention_pending"), PendingConcrete.Num());
    Out->SetNumberField(TEXT("retention_slots"), RetentionSlotsUsed());
    Out->SetNumberField(TEXT("retention_limit"), FragmentWorld ? 0 : bStackingExperiment ? 80 : 50);
    Out->SetNumberField(TEXT("retention_replacements"), RetentionReplacements);
    Out->SetNumberField(TEXT("retention_support_vetoes"), RetentionSupportVetoes);
    if (bStackingExperiment && Concrete)
    {
        TArray<int32> Counts, TileCounts;
        RetentionSectorCounts(Counts, TileCounts);
        TArray<TSharedPtr<FJsonValue>> Sectors, CeramicSectors, Evictions;
        for (int32 I = 0; I < 4; ++I)
        {
            Sectors.Add(MakeShared<FJsonValueNumber>(Counts[I]));
            CeramicSectors.Add(MakeShared<FJsonValueNumber>(TileCounts[I]));
            Evictions.Add(MakeShared<FJsonValueNumber>(RetentionEvictions[I]));
        }
        Out->SetArrayField(TEXT("retained_by_sector"), Sectors);
        Out->SetArrayField(TEXT("retained_ceramic_by_sector"), CeramicSectors);
        Out->SetArrayField(TEXT("evictions_by_sector"), Evictions);
    }
    Out->SetNumberField(TEXT("removed_concrete"), RemovedConcrete.Num());
    Out->SetNumberField(TEXT("concrete_impacts"), ConcreteImpacts);
    Out->SetNumberField(TEXT("last_concrete_bone"), LastConcreteBone);
    Out->SetBoolField(TEXT("coarse_experiment"), bCoarseExperiment);
    Out->SetBoolField(TEXT("refined_experiment"), bRefinedExperiment);
    Out->SetBoolField(TEXT("stacking_experiment"), bStackingExperiment);
    Out->SetNumberField(TEXT("independent_tile_breaks"),IndependentTileBreaks);
    Out->SetNumberField(TEXT("ground_crumble_events"), GroundCrumbleEvents);
    Out->SetNumberField(TEXT("shot_crumble_events"), ShotCrumbleEvents);
    Out->SetNumberField(TEXT("crumbled_tiles"), CrumbledTiles);
    Out->SetNumberField(TEXT("spawned_ceramic_chips"), SpawnedCeramicChips);
    Out->SetNumberField(TEXT("active_ceramic_chips"), CeramicDebris.Num());
    Out->SetNumberField(TEXT("ceramic_templates"), ChipTemplates.Num());
    if (bCoarseExperiment && Concrete)
    {
        int32 Carried = 0, Unsupported = 0, CarriedCollision = 0, CarriedPhysics = 0, CoreMoved = 0, GroundedFacing = 0;
        TArray<TSharedPtr<FJsonValue>> Targets;
        for (int32 I = 0; I < Data->Tiles.Num(); ++I)
        {
            if (InstanceByTile[I] == INDEX_NONE) continue;
            if (CarriedTiles[I])
            {
                ++Carried;
                GroundedFacing += GroundCrumbled.Contains(CarrierByTile[I]);
                CarriedCollision += Groups[GroupByTile[I]].Instances->GetCollisionEnabled() != ECollisionEnabled::NoCollision;
                CarriedPhysics += Groups[GroupByTile[I]].Instances->IsPhysicsCollisionEnabled();
                if (bRefinedExperiment && Targets.Num() < 30)
                {
                    auto Target = MakeShared<FJsonObject>();
                    Target->SetNumberField(TEXT("tile"), I);
                    Target->SetNumberField(TEXT("bone"), CarrierByTile[I]);
                    Target->SetStringField(TEXT("position"), LastWorld[I].GetLocation().ToString());
                    Target->SetStringField(TEXT("normal"), LastWorld[I].GetUnitAxis(EAxis::X).ToString());
                    Targets.Add(MakeShared<FJsonValueObject>(Target));
                }
            }
            else
                Unsupported += Data->Tiles[I].SupportBones.ContainsByPredicate([&](int32 B) { return ReleasedConcrete.Contains(B); });
        }
        const auto& Poses = Concrete->GetComponentSpaceTransforms3f();
        for (const int32 B : ConcreteLeaves)
            if (!Data->SurfaceBones.Contains(B) && RestBones.IsValidIndex(B) && Poses.IsValidIndex(B))
                CoreMoved += !FTransform(Poses[B]).Equals(RestBones[B], .05f);
        Out->SetNumberField(TEXT("carried_tiles"), Carried);
        Out->SetNumberField(TEXT("wall_tiles"), Attached - Carried);
        Out->SetNumberField(TEXT("unsupported_wall_tiles"), Unsupported);
        Out->SetNumberField(TEXT("carried_collision_tiles"), CarriedCollision);
        Out->SetNumberField(TEXT("carried_physics_tiles"), CarriedPhysics);
        Out->SetNumberField(TEXT("grounded_facing_tiles"),GroundedFacing);
        Out->SetArrayField(TEXT("carried_targets"), Targets);
        Out->SetNumberField(TEXT("protected_core_moved"), CoreMoved);
        Out->SetNumberField(TEXT("protected_core_impacts"), ProtectedCoreImpacts);
        Out->SetNumberField(TEXT("released_concrete"), ReleasedConcrete.Num());
        int32 CorePenetrations = 0;
        if (bStackingExperiment && CoreBarrier && Concrete->GetPhysicsProxy())
        {
            const FVector Extent = CoreBarrier->GetScaledBoxExtent()-FVector(.5);
            const Chaos::TBox<Chaos::FReal,3> CoreShape(-Extent,Extent);
            const Chaos::FRigidTransform3 CorePose(CoreBarrier->GetComponentLocation(),CoreBarrier->GetComponentQuat());
            for (const int32 Bone : ReleasedConcrete)
            {
                const auto* Particle = Concrete->GetPhysicsProxy()->GetParticleByIndex_External(Bone);
                if (!Particle || Particle->Disabled() || !Particle->GetGeometry()) continue;
                CorePenetrations += Chaos::OverlapQuery(*Particle->GetGeometry(),
                    Chaos::FRigidTransform3(Particle->GetX(),Particle->GetR()),CoreShape,CorePose);
            }
        }
        Out->SetNumberField(TEXT("debris_inside_core"),CorePenetrations);
    }
    if (bSurfaceExperiment && Concrete)
    {
        int32 TileSimulating = 0, TileCollision = 0, ConcreteDynamic = 0, ConcreteCollision = 0, ConcreteInvisible = 0;
        int32 TileUnsupported = 0, ConcreteUnsupported = 0, ConcretePhysics = 0, ConcreteQuery = 0;
        TArray<UStaticMeshComponent*> RetainedParts;
        for (const auto& Weak : RetainedTiles)
            if (const auto* Actor = Weak.Get())
                if (const auto* Part = Actor->FindComponentByClass<UStaticMeshComponent>())
                {
                    RetainedParts.Add(const_cast<UStaticMeshComponent*>(Part));
                    TileSimulating += Part->IsSimulatingPhysics();
                    TileCollision += Part->GetCollisionEnabled() != ECollisionEnabled::NoCollision;
                    const FVector* Bottom = RetainedTileSupport.Find(Weak);
                    TileUnsupported += !Bottom || !HasDebrisSupport(*Bottom,INDEX_NONE,Actor,true);
                }
        const auto* Proxy = Concrete->GetPhysicsProxy();
        const auto& Transforms = Concrete->GetComponentSpaceTransforms3f();
        for (const int32 Bone : RetainedConcrete)
        {
            const auto* Particle = Proxy ? Proxy->GetParticleByIndex_External(Bone) : nullptr;
            if (Particle)
            {
                ConcreteDynamic += Particle->ObjectState() != Chaos::EObjectStateType::Kinematic;
                FVector Bottom;
                ConcreteUnsupported += !ConcreteBottom(Particle, Bottom) || !HasDebrisSupport(Bottom,Bone,nullptr,true);
                for (const auto& Shape : Particle->ShapesArray())
                {
                    ConcreteCollision += Shape->GetSimEnabled() || Shape->GetQueryEnabled();
                    ConcretePhysics += Shape->GetSimEnabled();
                    ConcreteQuery += Shape->GetQueryEnabled();
                }
            }
            ConcreteInvisible += !Particle || Particle->Disabled() || !Transforms.IsValidIndex(Bone) ||
                Transforms[Bone].GetScale3D().GetAbsMin() < .02f;
        }
        Out->SetNumberField(TEXT("retained_tile_simulating"), TileSimulating);
        Out->SetNumberField(TEXT("retained_tile_collision"), TileCollision);
        Out->SetNumberField(TEXT("retained_concrete_nonkinematic"), ConcreteDynamic);
        Out->SetNumberField(TEXT("retained_concrete_collision_shapes"), ConcreteCollision);
        Out->SetNumberField(TEXT("retained_concrete_physics_shapes"), ConcretePhysics);
        Out->SetNumberField(TEXT("retained_concrete_query_shapes"), ConcreteQuery);
        Out->SetNumberField(TEXT("retained_concrete_invisible"), ConcreteInvisible);
        Out->SetNumberField(TEXT("retained_tile_unsupported"), TileUnsupported);
        Out->SetNumberField(TEXT("retained_concrete_unsupported"), ConcreteUnsupported);
        int32 DeepOverlaps = 0;
        if (bStackingExperiment)
            for (int32 A = 0; A < RetainedParts.Num(); ++A)
                for (int32 B = A+1; B < RetainedParts.Num(); ++B)
                {
                    const auto* First = RetainedParts[A]; const auto* Second = RetainedParts[B];
                    const FVector Normal = First->GetComponentTransform().GetUnitAxis(EAxis::X);
                    if (!First->Bounds.GetBox().Intersect(Second->Bounds.GetBox()) ||
                        FMath::Abs(FVector::DotProduct(Normal,Second->GetComponentTransform().GetUnitAxis(EAxis::X))) < .96f) continue;
                    const auto* Body = First->GetBodyInstance(); auto* Other = RetainedParts[B]->GetBodyInstance();
                    if (Body && Other && Body->OverlapTestForBody(First->GetComponentLocation()+Normal*.3,First->GetComponentQuat(),Other) &&
                        Body->OverlapTestForBody(First->GetComponentLocation()-Normal*.3,First->GetComponentQuat(),Other)) ++DeepOverlaps;
                }
        Out->SetNumberField(TEXT("retained_tile_deep_overlap_pairs"),DeepOverlaps);
    }
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
    bEndingPlay = true;
    ++FragmentGeneration;
    if (FacingPool) FacingPool->RemoveOwner(this);
    if (FragmentWorld) FragmentWorld->RemoveOwner(this);
    else
    {
        for (AActor* Actor : Debris) if (IsValid(Actor)) Actor->Destroy();
        for (AActor* Actor : CeramicDebris) if (IsValid(Actor)) Actor->Destroy();
    }
    Debris.Reset();
    Super::EndPlay(Reason);
}
