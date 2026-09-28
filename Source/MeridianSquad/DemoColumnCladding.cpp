#include "DemoColumnCladding.h"
#include "DemoColumnScatter.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "PhysicalMaterials/PhysicalMaterial.h"
#include "Engine/World.h"
#include "GeometryCollection/GeometryCollectionComponent.h"
#include "GeometryCollection/GeometryCollectionObject.h"
#include "GeometryCollection/GeometryCollection.h"
#include "GeometryCollection/GeometryCollectionAlgo.h"
#include "GeometryCollection/GeometryCollectionEngineRemoval.h"
#include "GeometryCollectionProxyData.h"
#include "PhysicsProxy/GeometryCollectionPhysicsProxy.h"
#include "Chaos/PhysicsObjectCollisionInterface.h"
#include "Chaos/Convex.h"
#include "PhysicsEngine/PhysicsObjectExternalInterface.h"
#include "Engine/CollisionProfile.h"
#include "Serialization/JsonSerializer.h"

namespace
{
const FName TileTag(TEXT("DemoColumnCladding"));
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
    bRefinedExperiment = GetOwner()->ActorHasTag(TEXT("DemoColumnRefined07"));
    bCoarseExperiment = GetOwner()->ActorHasTag(TEXT("DemoColumnCoarse06"));
    bSurfaceExperiment = bCoarseExperiment || GetOwner()->ActorHasTag(TEXT("DemoColumnSurface05"));
    Data = LoadObject<UDemoColumnCladdingData>(nullptr, bRefinedExperiment
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
    GroupByTile.Init(INDEX_NONE, Count);
    InstanceByTile.Init(INDEX_NONE, Count);
    Hits.Init(0, Count);
    LastWorld.SetNum(Count);
    Velocities.Init(FVector::ZeroVector, Count);
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
    }
}

void UDemoColumnCladding::BeginPlay()
{
    Super::BeginPlay();
    Initialize();
    if (Concrete)
    {
        if (bRefinedExperiment)
            if (auto* Heavy = LoadObject<UPhysicalMaterial>(nullptr, TEXT("/Game/Experiments/DemoTiledColumn01/Correction07/PM_HeavyConcrete07.PM_HeavyConcrete07")))
                Concrete->SetPhysMaterialOverride(Heavy);
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
            Concrete->bAllowRemovalOnSleep = true;
            const auto Rest = Concrete->GetRestCollection()->GetGeometryCollection();
            ConcreteAge.Init(-1.f, Rest->Transform.Num());
            ConcreteStillTime.Init(0.f, Rest->Transform.Num());
            for (int32 B = 0; B < Rest->Transform.Num(); ++B)
                if (Rest->SimulationType[B] == FGeometryCollection::FST_Rigid && Rest->Children[B].IsEmpty()) ConcreteLeaves.Add(B);
        }
    }
}

void UDemoColumnCladding::Detach(int32 TileIndex, const FVector& Push)
{
    if (!Data || !InstanceByTile.IsValidIndex(TileIndex) || InstanceByTile[TileIndex] == INDEX_NONE) return;
    const FTransform Pose = LastWorld[TileIndex];
    if (!RemoveTileInstance(TileIndex)) return;
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

bool UDemoColumnCladding::RemoveTileInstance(int32 TileIndex)
{
    if (!InstanceByTile.IsValidIndex(TileIndex) || InstanceByTile[TileIndex] == INDEX_NONE) return false;
    auto& Group = Groups[GroupByTile[TileIndex]];
    const int32 Instance = InstanceByTile[TileIndex];
    const int32 MovedTile = Group.Tiles.Last();
    if (!Group.Instances->RemoveInstance(Instance)) return false;
    Group.Tiles.RemoveAtSwap(Instance);
    if (Instance < Group.Tiles.Num()) InstanceByTile[MovedTile] = Instance;
    InstanceByTile[TileIndex] = INDEX_NONE;
    return true;
}

void UDemoColumnCladding::CarryTiles(int32 Bone)
{
    if (!bCoarseExperiment || ReleasedConcrete.Contains(Bone) || !RestBones.IsValidIndex(Bone)) return;
    ReleasedConcrete.Add(Bone);
    for (int32 I = 0; I < Data->Tiles.Num(); ++I)
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
        CarrierByTile[I] = Bone;
        CarrierRelative[I] = Tile.RestTransform.GetRelativeTransform(RestBones[Bone]);
        GroupByTile[I] = CarriedGroup;
        InstanceByTile[I] = Groups[CarriedGroup].Instances->AddInstance(Tile.RestTransform);
        Groups[CarriedGroup].Tiles.Add(I);
    }
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
        LastConcreteBone = INDEX_NONE;
        // The engine's generic leaf query also includes a broken root once it
        // loses its children. Its stale collision then masks the next real chip.
        // Trace only authored rigid leaves, including those in the live remainder.
        auto* Proxy = Concrete->GetPhysicsProxy();
        if (Proxy)
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
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    if (!Data || !Concrete || !GetWorld()->IsGameWorld()) return;
    const auto& Bones = Concrete->GetComponentSpaceTransforms3f();
    const FTransform ComponentWorld = Concrete->GetComponentTransform();
    if (bCoarseExperiment && Concrete->GetDynamicCollection())
    {
        FGeometryCollectionDynamicStateFacade State(*Concrete->GetDynamicCollection());
        for (const int32 Bone : Data->SurfaceBones)
            if (!ReleasedConcrete.Contains(Bone) && State.HasBrokenOff(Bone) && !State.HasInternalClusterParent(Bone)) CarryTiles(Bone);
    }
    TSet<int32> ChangedGroups;
    for (int32 I = 0; I < Data->Tiles.Num(); ++I)
    {
        if (InstanceByTile[I] == INDEX_NONE) continue;
        const auto& Tile = Data->Tiles[I];
        const int32 Bone = CarrierByTile[I];
        if (!Bones.IsValidIndex(Bone)) continue;
        const FTransform Local = CarrierRelative[I] * FTransform(Bones[Bone]);
        const FTransform World = Local * ComponentWorld;
        Velocities[I] = ((World.GetLocation() - LastWorld[I].GetLocation()) / FMath::Max(DeltaTime, .001f)).GetClampedToMaxSize(1500.f);
        const bool bMoved = FVector::DistSquared(Local.GetLocation(), Tile.RestTransform.GetLocation()) > FMath::Square(.8f) ||
            Local.GetRotation().AngularDistance(Tile.RestTransform.GetRotation()) > FMath::DegreesToRadians(3.f);
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

bool UDemoColumnCladding::HasStaticSupport(const FVector& Bottom) const
{
    FHitResult Hit;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(DemoColumnGround), false, GetOwner());
    return GetWorld()->LineTraceSingleByObjectType(Hit, Bottom + FVector(0, 0, 5), Bottom - FVector(0, 0, 8),
        FCollisionObjectQueryParams(ECC_WorldStatic), Params) && !Hit.bStartPenetrating && Hit.ImpactNormal.Z >= .65f;
}

void UDemoColumnCladding::UpdateFacingImpacts()
{
    CeramicDebris.RemoveAll([](AActor* Actor) { return !IsValid(Actor); });
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
            ConcreteBottom(Particle, Bottom) && HasStaticSupport(Bottom))
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
    const int32 Count = FMath::Min(Candidates.Num(), bShot ? 1 : 2);
    if (!Count) return;
    if (bShot) ++ShotCrumbleEvents; else ++GroundCrumbleEvents;
    FRandomStream Random(HashCombineFast(GetTypeHash(Bone), ++ImpactSerial + 70117u));
    for (int32 C = 0; C < Count; ++C)
    {
        const int32 Tile = Candidates[C];
        const FTransform Pose = LastWorld[Tile];
        if (!RemoveTileInstance(Tile)) continue;
        ++CrumbledTiles;
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
    DebrisPollTime += DeltaTime;
    if (DebrisPollTime < .25f) return;
    const float Elapsed = DebrisPollTime;
    const float StillStep = FMath::Min(Elapsed, .3f);
    DebrisPollTime = 0.f;
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
        const bool bSupported = bSlow && Part->GetClosestPointOnCollision(Below, Bottom) >= 0.f && HasStaticSupport(Bottom);
        Still = bSupported ? Still + StillStep : 0.f;
        if (bSlow && !bSupported) Part->WakeAllRigidBodies();
        if (Still < 1.f || RetentionSlotsUsed() >= 50) continue;
        const FTransform Pose = Part->GetComponentTransform();
        Part->SetSimulatePhysics(false);
        Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);
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
    for (const int32 Bone : ConcreteLeaves)
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
        const bool bSupported = bSlow && ConcreteBottom(Particle, Bottom) && HasStaticSupport(Bottom);
        Still = bSupported ? Still + StillStep : 0.f;
        if (bSlow && !bSupported) KeepDemoColumnLeafAwake(Concrete, Bone);
        if (Still >= 1.f && RetentionSlotsUsed() < 50)
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
                Self->Concrete->SetPerParticleCollisionProfileName(TArray<int32>{Bone}, Self->bRefinedExperiment
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
    Out->SetBoolField(TEXT("surface_experiment"), bSurfaceExperiment);
    Out->SetNumberField(TEXT("retained_tiles"), RetainedTiles.Num());
    Out->SetNumberField(TEXT("retained_concrete"), RetainedConcrete.Num());
    Out->SetNumberField(TEXT("retention_pending"), PendingConcrete.Num());
    Out->SetNumberField(TEXT("retention_slots"), RetentionSlotsUsed());
    Out->SetNumberField(TEXT("removed_concrete"), RemovedConcrete.Num());
    Out->SetNumberField(TEXT("concrete_impacts"), ConcreteImpacts);
    Out->SetNumberField(TEXT("last_concrete_bone"), LastConcreteBone);
    Out->SetBoolField(TEXT("coarse_experiment"), bCoarseExperiment);
    Out->SetBoolField(TEXT("refined_experiment"), bRefinedExperiment);
    Out->SetNumberField(TEXT("ground_crumble_events"), GroundCrumbleEvents);
    Out->SetNumberField(TEXT("shot_crumble_events"), ShotCrumbleEvents);
    Out->SetNumberField(TEXT("crumbled_tiles"), CrumbledTiles);
    Out->SetNumberField(TEXT("spawned_ceramic_chips"), SpawnedCeramicChips);
    Out->SetNumberField(TEXT("active_ceramic_chips"), CeramicDebris.Num());
    Out->SetNumberField(TEXT("ceramic_templates"), ChipTemplates.Num());
    if (bCoarseExperiment && Concrete)
    {
        int32 Carried = 0, Unsupported = 0, CarriedCollision = 0, CarriedPhysics = 0, CoreMoved = 0;
        TArray<TSharedPtr<FJsonValue>> Targets;
        for (int32 I = 0; I < Data->Tiles.Num(); ++I)
        {
            if (InstanceByTile[I] == INDEX_NONE) continue;
            if (CarriedTiles[I])
            {
                ++Carried;
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
        Out->SetArrayField(TEXT("carried_targets"), Targets);
        Out->SetNumberField(TEXT("protected_core_moved"), CoreMoved);
        Out->SetNumberField(TEXT("protected_core_impacts"), ProtectedCoreImpacts);
        Out->SetNumberField(TEXT("released_concrete"), ReleasedConcrete.Num());
    }
    if (bSurfaceExperiment && Concrete)
    {
        int32 TileSimulating = 0, TileCollision = 0, ConcreteDynamic = 0, ConcreteCollision = 0, ConcreteInvisible = 0;
        int32 TileUnsupported = 0, ConcreteUnsupported = 0, ConcretePhysics = 0, ConcreteQuery = 0;
        for (const auto& Weak : RetainedTiles)
            if (const auto* Actor = Weak.Get())
                if (const auto* Part = Actor->FindComponentByClass<UStaticMeshComponent>())
                {
                    TileSimulating += Part->IsSimulatingPhysics();
                    TileCollision += Part->GetCollisionEnabled() != ECollisionEnabled::NoCollision;
                    const FVector* Bottom = RetainedTileSupport.Find(Weak);
                    TileUnsupported += !Bottom || !HasStaticSupport(*Bottom);
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
                ConcreteUnsupported += !ConcreteBottom(Particle, Bottom) || !HasStaticSupport(Bottom);
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
    for (AActor* Actor : Debris) if (IsValid(Actor)) Actor->Destroy();
    for (AActor* Actor : CeramicDebris) if (IsValid(Actor)) Actor->Destroy();
    Debris.Reset();
    Super::EndPlay(Reason);
}
