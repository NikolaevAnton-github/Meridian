#include "DestructionFragmentWorld.h"
#include "DemoColumnCladding.h"
#include "DemoColumnScatter.h"
#include "LobbyFacingPool.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Components/StaticMeshComponent.h"
#include "GeometryCollection/GeometryCollectionComponent.h"
#include "GeometryCollection/GeometryCollectionObject.h"
#include "PhysicsProxy/GeometryCollectionPhysicsProxy.h"
#include "PhysicsEngine/BodySetup.h"
#include "PhysicalMaterials/PhysicalMaterial.h"
#include "Chaos/Convex.h"
#include "Chaos/PhysicsObjectCollisionInterface.h"
#include "PhysicsEngine/PhysicsObjectExternalInterface.h"
#include "Serialization/JsonSerializer.h"
#include "ProfilingDebugging/CsvProfiler.h"
#include "Tasks/Task.h"
#include "HAL/IConsoleManager.h"

CSV_DECLARE_CATEGORY_EXTERN(LobbyColumns);

namespace
{
constexpr double CellSize = 150.;
int64 NextFragmentHandle = 1; // GT only; survives world recreation within this process.
TAutoConsoleVariable<int32> ParallelFragments(TEXT("msq.Destruction.Parallel"),1,
    TEXT("Coarse pure fragment calculations. 0 serial, 1 parallel above threshold, 2 compare both."));
struct FHullBatch
{
    TArray<FDestructionHullInput> Inputs;
    TArray<FDestructionHullOutput> Outputs;
};
FIntVector CellAt(const FVector& P)
{ return FIntVector(FMath::FloorToInt(P.X/CellSize), FMath::FloorToInt(P.Y/CellSize), FMath::FloorToInt(P.Z/CellSize)); }
void CopyHull(const Chaos::FImplicitObject* Geometry, TArray<FVector>& Hull)
{
    if (!Geometry) return;
    Geometry->VisitLeafObjects([&](const Chaos::FImplicitObject* Shape, const Chaos::FRigidTransform3& Local, int32, int32, int32)
    {
        if (const auto* Convex = Shape->GetObject<Chaos::FConvex>())
            for (const auto& Vertex : Convex->GetVertices()) Hull.Add(Local.TransformPosition(FVector(Vertex)));
    });
}
}

ADestructionFragmentDriver::ADestructionFragmentDriver()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickGroup = TG_PostPhysics;
    SetCanBeDamaged(false);
}
void ADestructionFragmentDriver::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (auto* Fragments = GetWorld()->GetSubsystem<UDestructionFragmentWorld>()) Fragments->Update(DeltaSeconds);
}
bool UDestructionFragmentWorld::DoesSupportWorldType(EWorldType::Type Type) const
{ return Type == EWorldType::Game || Type == EWorldType::PIE; }

void UDestructionFragmentWorld::RegisterOwner(UDemoColumnCladding* Owner)
{
    if (bTearingDown || !Owner) return;
    if (!Driver)
    {
        FActorSpawnParameters Params;
        Params.ObjectFlags |= RF_Transient;
        Driver = GetWorld()->SpawnActor<ADestructionFragmentDriver>(Params);
    }
    if (Driver) Driver->AddTickPrerequisiteComponent(Owner);
}

bool UDestructionFragmentWorld::Valid(const FRecord& Record) const
{
    const auto* Owner = Record.Owner.Get();
    return Owner && !Owner->GetOwner()->IsActorBeingDestroyed() &&
        Record.Stamp.Id.Owner == Owner->GetFragmentOwner() &&
        Record.Stamp.Id.Generation == Owner->GetFragmentGeneration() &&
        (Record.Actor.IsValid() || Record.Concrete.IsValid());
}

int64 UDestructionFragmentWorld::RegisterConcrete(UDemoColumnCladding* Owner, UGeometryCollectionComponent* Concrete, int32 Bone)
{
    check(IsInGameThread());
    RegisterOwner(Owner);
    const FDestructionFragmentId Id{Owner->GetFragmentOwner(), Owner->GetFragmentGeneration(), -2-Bone};
    if (const int64* Found = Identity.Find(Id)) return *Found;
    FRecord R;
    R.Handle = NextFragmentHandle++; R.Stamp = {Id, 1, 1}; R.Owner = Owner; R.Concrete = Concrete; R.Bone = Bone;
    R.Guard = MakeShared<FDestructionCommandGuard, ESPMode::ThreadSafe>();
    Identity.Add(Id, R.Handle);
    const int64 Handle = R.Handle;
    Records.Add(Handle, MoveTemp(R));
    return Handle;
}

AStaticMeshActor* UDestructionFragmentWorld::Allocate(const FPoolKey& Key)
{
    FActorSpawnParameters Params;
    Params.ObjectFlags |= RF_Transient;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    auto* Actor = GetWorld()->SpawnActor<AStaticMeshActor>(Params);
    if (!Actor) { ++AllocationFailures; UE_LOG(LogTemp, Error, TEXT("Fragment allocation failed")); return nullptr; }
    Actor->Tags.Add(TEXT("DestructionFragmentBody"));
    auto* Part = Actor->GetStaticMeshComponent();
    Part->SetMobility(EComponentMobility::Movable);
    Part->SetStaticMesh(Key.Mesh.Get());
    Part->SetPhysMaterialOverride(Key.Material.Get());
    Part->SetCanEverAffectNavigation(false);
    Part->SetCollisionObjectType(ECC_PhysicsBody);
    Part->SetCollisionResponseToAllChannels(ECR_Ignore);
    Part->SetCollisionResponseToChannel(ECC_WorldStatic, ECR_Block);
    Part->SetCollisionResponseToChannel(ECC_PhysicsBody, ECR_Block);
    Part->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
    Part->SetUseCCD(true);
    Part->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    Part->SetSimulatePhysics(true);
    Part->PutAllRigidBodiesToSleep();
    // Keep the compatible body allocated off-scene; no active collision or queries.
    Part->SetCollisionResponseToAllChannels(ECR_Ignore);
    Part->SetWorldLocation(FVector(0,0,-1000000), false, nullptr, ETeleportType::TeleportPhysics);
    Part->SetCollisionEnabled(ECollisionEnabled::PhysicsOnly);
    Part->SetHiddenInGame(true);
    Allocations.Add(Actor);
    PoolKeys.Add(Actor, Key);
    CachedResources.AddUnique(Key.Mesh.Get());
    if (Key.Material.IsValid()) CachedResources.AddUnique(Key.Material.Get());
    return Actor;
}

AStaticMeshActor* UDestructionFragmentWorld::Acquire(UDemoColumnCladding* Owner, UStaticMesh* Mesh,
    UPhysicalMaterial* Material, const FTransform& Pose, int32 Local)
{
    check(IsInGameThread());
    if (bTearingDown || !Owner || !Mesh) return nullptr;
    RegisterOwner(Owner);
    const FPoolKey Key{Mesh, Material};
    auto& Available = Free.FindOrAdd(Key);
    AStaticMeshActor* Actor = nullptr;
    for (int32 I=Available.Num()-1; I>=0 && !Actor; --I)
    {
        auto* Candidate=Available[I].Get();
        if (!Candidate) { Available.RemoveAtSwap(I,EAllowShrinking::No); continue; }
        if (ReuseAfterFrame.FindRef(Candidate)>GFrameCounter) continue;
        Actor=Candidate; Available.RemoveAtSwap(I,EAllowShrinking::No);
    }
    if (Actor) ++Reused;
    else { Actor = Allocate(Key); ++Grown; }
    if (!Actor) return nullptr;
    // A small, finite prewarm. Capacity may grow without evicting live fragments.
    if (Allocations.Num() < 24 && Available.IsEmpty())
        if (auto* Spare = Allocate(Key)) Available.Add(Spare);
    Actor->SetOwner(Owner->GetOwner());
    Actor->SetLifeSpan(0.f);
    auto* Part = Actor->GetStaticMeshComponent();
    Part->OnComponentHit.Clear();
    Part->SetStaticMesh(Mesh);
    Part->EmptyOverrideMaterials();
    Part->SetOverlayMaterial(nullptr);
    Part->SetPhysMaterialOverride(Material);
    Part->SetRenderCustomDepth(false);
    Part->SetCustomDepthStencilValue(0);
    Part->SetReceivesDecals(true);
    Part->bReverseCulling=false;
    Part->SetEnableGravity(true);
    Part->SetNotifyRigidBodyCollision(false);
    Part->SetHiddenInGame(false);
    Part->SetVisibility(true);
    Part->SetCastShadow(true);
    Part->SetSimulatePhysics(true);
    Part->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    Part->SetCollisionResponseToAllChannels(ECR_Ignore);
    Part->SetCollisionResponseToChannel(ECC_WorldStatic, ECR_Block);
    Part->SetCollisionResponseToChannel(ECC_PhysicsBody, ECR_Block);
    Part->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
    Part->SetWorldTransform(Pose, false, nullptr, ETeleportType::TeleportPhysics);
    Part->SetPhysicsLinearVelocity(FVector::ZeroVector);
    Part->SetPhysicsAngularVelocityInRadians(FVector::ZeroVector);
    Part->WakeAllRigidBodies();
    FRecord R;
    R.Handle = NextFragmentHandle++;
    R.Stamp = {{Owner->GetFragmentOwner(), Owner->GetFragmentGeneration(), Local}, 1, 1};
    R.Owner = Owner; R.Actor = Actor; R.Pose = Pose;
    R.Guard = MakeShared<FDestructionCommandGuard, ESPMode::ThreadSafe>();
    const FString HullKey=Mesh->GetPathName();
    if (const auto* Cached=HullCache.Find(HullKey)) R.Hull=*Cached;
    else
    {
        auto Hull=MakeShared<TArray<FVector>,ESPMode::ThreadSafe>();
        if (const auto* Setup = Mesh->GetBodySetup())
        {
            for (const auto& Convex : Setup->AggGeom.ConvexElems)
                for (const FVector& V : Convex.VertexData) Hull->Add(Convex.GetTransform().TransformPosition(V));
            for (const auto& Box : Setup->AggGeom.BoxElems)
                for (int32 X : {-1,1}) for (int32 Y : {-1,1}) for (int32 Z : {-1,1})
                    Hull->Add(Box.GetTransform().TransformPosition(FVector(X*Box.X,Y*Box.Y,Z*Box.Z)*.5));
            // Curved/mixed representations use the exact engine support query.
            if (!Setup->AggGeom.SphereElems.IsEmpty() || !Setup->AggGeom.SphylElems.IsEmpty() ||
                !Setup->AggGeom.TaperedCapsuleElems.IsEmpty()) Hull->Reset();
        }
        R.Hull=Hull; HullCache.Add(HullKey,R.Hull);
    }
    Identity.Add(R.Stamp.Id, R.Handle);
    LooseLookup.Add(Part, R.Handle);
    Records.Add(R.Handle, MoveTemp(R));
    return Actor;
}

bool UDestructionFragmentWorld::IsManaged(const AActor* Actor) const
{ return Actor && PoolKeys.Contains(const_cast<AActor*>(Actor)); }

AStaticMeshActor* UDestructionFragmentWorld::SpawnVerificationFragment(UDemoColumnCladding* Owner, UStaticMesh* Mesh,FTransform Pose)
{
#if WITH_EDITOR
    if (GetWorld()->WorldType!=EWorldType::PIE || !Owner || Owner->GetWorld()!=GetWorld()) return nullptr;
    return Acquire(Owner,Mesh,nullptr,Pose,NextVerificationLocal--);
#else
    return nullptr;
#endif
}

void UDestructionFragmentWorld::InvalidateDependents(FRecord& Record)
{
    TArray<int64> Pending = Record.Dependents.Array();
    Record.Dependents.Reset();
    // Only direct contacts wake here. Their transition propagates through the
    // dependency graph on the next safe snapshot, without a recursive stack.
    for (const int64 Handle : Pending)
        if (auto* Dependent = Records.Find(Handle))
        {
            Dependent->Supports.Remove(Record.Handle);
            Dependent->bSupportDirty = true;
            if (Dependent->State == EDestructionFragmentState::Asleep)
                Command(Handle, 4, FVector::ZeroVector, FVector::ZeroVector, FTransform::Identity);
        }
}

void UDestructionFragmentWorld::Forget(int64 Handle)
{
    FRecord* Record = Records.Find(Handle);
    if (!Record) return;
    Record->Guard->Valid.Store(false);
    InvalidateDependents(*Record);
    for (const int64 Support : Record->Supports)
        if (auto* Other = Records.Find(Support)) Other->Dependents.Remove(Handle);
    for (const FIntVector& Cell : Record->Cells)
        if (auto* Items = Spatial.Find(Cell)) { Items->Remove(Handle); if (Items->IsEmpty()) Spatial.Remove(Cell); }
    if (const auto* Actor = Record->Actor.Get()) LooseLookup.Remove(Actor->GetStaticMeshComponent());
    if (Record->RenderHandle)
        GetWorld()->GetSubsystem<ULobbyFacingPool>()->Remove(Record->Owner.Get(),Record->RenderHandle);
    Identity.Remove(Record->Stamp.Id);
    Records.Remove(Handle);
}

void UDestructionFragmentWorld::Return(AActor* Actor)
{
    auto* MeshActor = Cast<AStaticMeshActor>(Actor);
    const auto* Key = PoolKeys.Find(Actor);
    if (!MeshActor || !Key) return;
    auto* Part = MeshActor->GetStaticMeshComponent();
    const int64* Handle = LooseLookup.Find(Part);
    if (!Handle) return; // Double-return is harmless.
    Forget(*Handle);
    Part->OnComponentHit.Clear();
    Part->SetNotifyRigidBodyCollision(false);
    MeshActor->SetLifeSpan(0.f);
    MeshActor->SetOwner(nullptr);
    Part->SetPhysicsLinearVelocity(FVector::ZeroVector);
    Part->SetPhysicsAngularVelocityInRadians(FVector::ZeroVector);
    Part->SetSimulatePhysics(true);
    Part->SetCollisionResponseToAllChannels(ECR_Ignore);
    Part->SetWorldLocation(FVector(0,0,-1000000), false, nullptr, ETeleportType::TeleportPhysics);
    Part->SetCollisionEnabled(ECollisionEnabled::PhysicsOnly);
    Part->PutAllRigidBodiesToSleep();
    Part->SetHiddenInGame(true);
    Free.FindOrAdd(*Key).Add(MeshActor);
    // Drain queued contact callbacks before this component can represent another
    // identity. Growing during quarantine is preferable to aliasing old events.
    ReuseAfterFrame.Add(MeshActor,GFrameCounter+2);
}

void UDestructionFragmentWorld::InvalidateSupport(AActor* Owner)
{
    for (auto& Pair : Records)
    {
        auto& R=Pair.Value;
        if (R.StaticSupport.IsValid() && R.StaticSupport->GetOwner()==Owner)
        {
            R.StaticSupport.Reset(); R.bSupportDirty=true; R.NextSupportCheck=0.;
            if (R.State==EDestructionFragmentState::Asleep)
                Command(R.Handle,4,FVector::ZeroVector,FVector::ZeroVector,FTransform::Identity);
        }
    }
}

void UDestructionFragmentWorld::RemoveOwner(UDemoColumnCladding* Owner)
{
    TArray<int64> Handles;
    for (const auto& Pair : Records) if (Pair.Value.Owner == Owner) Handles.Add(Pair.Key);
    for (const int64 Handle : Handles)
        if (auto* Record = Records.Find(Handle))
        {
            if (Record->Actor.IsValid()) Return(Record->Actor.Get());
            else Forget(Handle);
        }
    if (Driver) Driver->RemoveTickPrerequisiteComponent(Owner);
}

int64 UDestructionFragmentWorld::Select(UPrimitiveComponent* Component, int32 Item) const
{
    if (const int64* Found = LooseLookup.Find(Component)) return *Found;
    if (const auto* Concrete = Cast<UGeometryCollectionComponent>(Component))
        for (const auto& Pair : Records)
            if (Pair.Value.Concrete == Concrete && Pair.Value.Bone == Item) return Pair.Key;
    return 0;
}

FString UDestructionFragmentWorld::Command(int64 Handle, uint8 Operation, const FVector& Velocity,
    const FVector& AngularVelocity, const FTransform& Pose)
{
    FRecord* Record = Records.Find(Handle);
    if (!Record || !Valid(*Record)) return TEXT("Stale");
    if (Velocity.ContainsNaN() || AngularVelocity.ContainsNaN() || Pose.ContainsNaN()) return TEXT("InvalidInput");
    const bool Held = Record->State == EDestructionFragmentState::Held;
    if ((Operation == 2 || Operation == 3) && !Held) return TEXT("UnsupportedState");
    if ((Operation == 0 || Operation == 4 || Operation == 5) && Held) return TEXT("UnsupportedState");
    if (Operation == 1 && Held) return TEXT("Applied");
    ++Record->Stamp.StateRevision;
    Record->Guard->Revision.Store(Record->Stamp.StateRevision);
    if (auto* Actor = Record->Actor.Get())
    {
        auto* Part = Actor->GetStaticMeshComponent();
        if (Operation == 1)
        {
            Part->SetPhysicsLinearVelocity(FVector::ZeroVector);
            Part->SetPhysicsAngularVelocityInRadians(FVector::ZeroVector);
            Part->SetSimulatePhysics(false);
        }
        else if (Operation == 2)
            Part->SetWorldTransform(Pose, false, nullptr, ETeleportType::TeleportPhysics);
        else if (Operation == 5) Part->PutAllRigidBodiesToSleep();
        else
        {
            if (Operation == 3) Part->SetSimulatePhysics(true);
            Part->WakeAllRigidBodies();
            if (Operation == 0) Part->AddImpulse(Velocity, NAME_None, true);
            if (Operation == 3)
            {
                Part->SetPhysicsLinearVelocity(Velocity);
                Part->SetPhysicsAngularVelocityInRadians(AngularVelocity);
            }
        }
    }
    else if (bCollectingCommands)
        PendingCommands.FindOrAdd(Record->Concrete).Add({Record->Bone,Operation,Velocity,AngularVelocity,Pose,
            Record->Guard,Record->Stamp.StateRevision});
    else if (!CommandDemoColumnLeaf(Record->Concrete.Get(), Record->Bone, Operation, Velocity,
        AngularVelocity, Pose, Record->Guard, Record->Stamp.StateRevision)) return TEXT("Unavailable");
    Record->State = (Operation == 1 || Operation == 2) ? EDestructionFragmentState::Held :
        Operation == 5 ? EDestructionFragmentState::Asleep : EDestructionFragmentState::Awake;
    Record->bSupportDirty = Operation != 5;
    if (Operation != 5) Record->StillTime=0.f;
    if (Operation == 0 || Operation == 3 || Operation == 4) ++WakeCommands;
    if (Operation != 5) InvalidateDependents(*Record);
    return Record->Actor.IsValid() ? TEXT("Applied") : TEXT("Queued");
}

FString UDestructionFragmentWorld::Impulse(int64 Handle, FVector DeltaVelocity)
{ return Command(Handle, 0, DeltaVelocity, FVector::ZeroVector, FTransform::Identity); }
FString UDestructionFragmentWorld::Hold(int64 Handle)
{ return Command(Handle, 1, FVector::ZeroVector, FVector::ZeroVector, FTransform::Identity); }
FString UDestructionFragmentWorld::MoveHeld(int64 Handle, FTransform Pose)
{ return Command(Handle, 2, FVector::ZeroVector, FVector::ZeroVector, Pose); }
FString UDestructionFragmentWorld::Release(int64 Handle, FVector Velocity, FVector AngularVelocity)
{ return Command(Handle, 3, Velocity, AngularVelocity, FTransform::Identity); }

void UDestructionFragmentWorld::UpdateSpatial(FRecord& Record)
{
    for (const FIntVector& Cell : Record.Cells)
        if (auto* Items = Spatial.Find(Cell)) { Items->Remove(Record.Handle); if (Items->IsEmpty()) Spatial.Remove(Cell); }
    Record.Cells.Reset();
    if (!Record.Bounds.IsValid) return;
    const FIntVector Min = CellAt(Record.Bounds.Min), Max = CellAt(Record.Bounds.Max);
    for (int32 X=Min.X; X<=Max.X; ++X)
        for (int32 Y=Min.Y; Y<=Max.Y; ++Y)
            for (int32 Z=Min.Z; Z<=Max.Z; ++Z)
            {
                const FIntVector Cell(X,Y,Z);
                Spatial.FindOrAdd(Cell).Add(Record.Handle); Record.Cells.Add(Cell);
            }
}

bool UDestructionFragmentWorld::FindSupport(FRecord& Record)
{
    ++SupportTests;
    for (const int64 Support : Record.Supports)
        if (auto* Other = Records.Find(Support)) Other->Dependents.Remove(Record.Handle);
    Record.Supports.Reset(); Record.StaticSupport.Reset();
    const FVector Start = Record.Bottom + FVector(0,0,5), End = Record.Bottom - FVector(0,0,8);
    FCollisionQueryParams Params(SCENE_QUERY_STAT(FragmentSupport), false);
    if (Record.Actor.IsValid()) Params.AddIgnoredActor(Record.Actor.Get());
    // World queries include static and other owners' intact GC supports. Registered
    // fragments are tested individually below so self/cluster hits cannot mask them.
    FCollisionObjectQueryParams Types;
    Types.AddObjectTypesToQuery(ECC_WorldStatic); Types.AddObjectTypesToQuery(ECC_PhysicsBody);
    TArray<FHitResult> Hits;
    bool bHullSweep=false;
    if (auto* Actor=Record.Actor.Get())
    {
        bHullSweep=true;
        FComponentQueryParams ComponentParams(SCENE_QUERY_STAT(FragmentStaticSupport),Actor);
        GetWorld()->ComponentSweepMulti(Hits,Actor->GetStaticMeshComponent(),
            Record.Pose.GetLocation()+FVector(0,0,1),Record.Pose.GetLocation()-FVector(0,0,1),
            Record.Pose.GetRotation(),ComponentParams);
    }
    else GetWorld()->LineTraceMultiByObjectType(Hits, Start, End, Types, Params);
    bool Supported = false;
    for (const auto& Hit : Hits)
    {
        if (Hit.bStartPenetrating || Hit.ImpactNormal.Z < .5f || Hit.Distance < (bHullSweep ? .4f:3.5f) ||
            (!bHullSweep && Hit.Distance>6.5f)) continue;
        if (Hit.GetComponent() == Record.Concrete.Get() && Hit.Item == Record.Bone) continue;
        if (Select(Hit.GetComponent(), Hit.Item)) continue;
        Record.StaticSupport = Hit.GetComponent();
        if (Hit.GetComponent()) Record.SupportPose = Hit.GetComponent()->GetComponentTransform();
        Supported = true;
    }
    TSet<int64> Candidates;
    // A single lowest vertex can miss a real contact when two flat pieces are
    // offset by fractions of a millimetre. Index the complete support footprint;
    // an exact downward hull sweep below decides the contact, not a centre ray.
    const FIntVector Min = CellAt(Record.Bounds.Min-FVector(0,0,2)), Max = CellAt(Record.Bounds.Max);
    for (int32 X=Min.X; X<=Max.X; ++X)
        for (int32 Y=Min.Y; Y<=Max.Y; ++Y)
            for (int32 Z=Min.Z; Z<=Max.Z; ++Z)
                if (const auto* Cell = Spatial.Find(FIntVector(X,Y,Z))) Candidates.Append(*Cell);
    TArray<int64> Ordered = Candidates.Array(); Ordered.Sort();
    for (const int64 Handle : Ordered)
    {
        auto* Other = Records.Find(Handle);
        if (Handle == Record.Handle || !Other || !Valid(*Other)) continue;
        bool Contact = false;
        auto SelfObject=Record.Actor.IsValid() ? Record.Actor->GetStaticMeshComponent()->GetPhysicsObjectByName(NAME_None)
            : Record.Concrete->GetPhysicsObjectById(Record.Bone);
        auto OtherObject=Other->Actor.IsValid() ? Other->Actor->GetStaticMeshComponent()->GetPhysicsObjectByName(NAME_None)
            : Other->Concrete->GetPhysicsObjectById(Other->Bone);
        if (SelfObject && OtherObject)
        {
            TArray<Chaos::FPhysicsObjectHandle> Objects{SelfObject,OtherObject};
            auto Read=FPhysicsObjectExternalInterface::LockRead(Objects);
            auto& Interface=Read.GetInterface();
            const auto* Particle=Interface.GetParticle(SelfObject);
            if (Particle && Particle->GetGeometry())
            {
                const FTransform Body=Interface.GetTransform(SelfObject);
                Chaos::FPhysicsObjectCollisionInterface_External Collision(Interface);
                TArray<Chaos::FPhysicsObjectHandle> Targets{OtherObject};
                Particle->GetGeometry()->VisitLeafObjects([&](const Chaos::FImplicitObject* Shape,
                    const Chaos::FRigidTransform3& Local,int32,int32,int32)
                {
                    // Static meshes also contain their render triangle mesh.
                    // Chaos moving-shape sweeps accept convex query geometry;
                    // simulation uses these exact simple convex leaves as well.
                    if (!Shape->IsConvex()) return;
                    FTransform SweepPose=FTransform(Local)*Body;
                    SweepPose.AddToTranslation(FVector(0,0,1));
                    ChaosInterface::FSweepHit Hit;
                    Chaos::FSweepParameters SweepParams;
                    SweepParams.bComputeMTD=true;
                    if (Collision.ShapeSweep(Targets,*Shape,SweepPose,SweepPose.GetLocation()-FVector(0,0,2),SweepParams,Hit) &&
                        Hit.WorldNormal.Z>=.5f && Hit.Distance>=.4f) Contact=true;
                });
            }
        }
        if (Contact) { Record.Supports.Add(Handle); Other->Dependents.Add(Record.Handle); Supported = true; }
    }
    return Supported;
}

void UDestructionFragmentWorld::Update(float DeltaSeconds)
{
    CSV_SCOPED_TIMING_STAT(LobbyColumns, FragmentWorld);
    if (bTearingDown) return;
    bCollectingCommands=true;
    const double Now = GetWorld()->GetTimeSeconds();
    TArray<int64> Invalid;
    TArray<int64> Changed;
    auto Batch=MakeShared<FHullBatch,ESPMode::ThreadSafe>();
    for (auto& Pair : Records)
    {
        auto& R = Pair.Value;
        if (!Valid(R)) { Invalid.Add(Pair.Key); continue; }
        FTransform Pose;
        FVector Velocity;
        bool Sleeping = false;
        if (auto* Actor = R.Actor.Get())
        {
            auto* Part = Actor->GetStaticMeshComponent();
            Sleeping = !Part->IsAnyRigidBodyAwake();
            Pose = Part->GetComponentTransform();
            Velocity = Sleeping ? FVector::ZeroVector : Part->GetPhysicsLinearVelocity();
            R.AngularVelocity=Sleeping ? FVector::ZeroVector : Part->GetPhysicsAngularVelocityInRadians();
            R.Bounds = Part->Bounds.GetBox();
        }
        else
        {
            auto* Proxy = R.Concrete->GetPhysicsProxy();
            const auto* Particle = Proxy ? Proxy->GetParticleByIndex_External(R.Bone) : nullptr;
            if (!Particle || Particle->Disabled()) continue;
            Sleeping = Particle->ObjectState() == Chaos::EObjectStateType::Sleeping;
            Pose = FTransform(Particle->GetR(), Particle->GetX());
            Velocity = Particle->GetV();
            R.AngularVelocity=Particle->GetW();
            if (!R.Hull)
            {
                const FString HullKey=FString::Printf(TEXT("%s:%d:%s"),*GetPathNameSafe(R.Concrete->GetRestCollection()),
                    R.Bone,*R.Concrete->GetComponentScale().ToString());
                if (const auto* Cached=HullCache.Find(HullKey)) R.Hull=*Cached;
                else
                {
                    auto Hull=MakeShared<TArray<FVector>,ESPMode::ThreadSafe>();
                    CopyHull(Particle->GetGeometry(),*Hull);
                    R.Hull=Hull;
                    HullCache.Add(HullKey,R.Hull);
                }
            }
            if (Particle->GetGeometry())
                R.Bounds = FBox(Particle->GetGeometry()->BoundingBox().Min(),Particle->GetGeometry()->BoundingBox().Max()).TransformBy(Pose);
        }
        const bool Moved = !R.bObserved || !Pose.Equals(R.Pose, 0.f);
        const auto State = R.State == EDestructionFragmentState::Held ? R.State :
            Sleeping ? EDestructionFragmentState::Asleep : EDestructionFragmentState::Awake;
        if (State != R.State)
        {
            ++R.Stamp.StateRevision; R.Guard->Revision.Store(R.Stamp.StateRevision);
            R.State = State; R.bSupportDirty = true; R.NextSupportCheck=0.;
        }
        if (Moved)
        {
            ++R.Stamp.PoseRevision; ++PoseChanges;
            R.Pose = Pose; R.bSupportDirty = true; Changed.Add(R.Handle);
            if (R.Hull && !R.Hull->IsEmpty()) Batch->Inputs.Add({R.Stamp,Pose,R.Hull});
            else
            {
                R.Bottom = R.Bounds.GetCenter()-FVector(0,0,R.Bounds.GetExtent().Z);
                if (auto* Actor = R.Actor.Get())
                    Actor->GetStaticMeshComponent()->GetClosestPointOnCollision(R.Bottom-FVector(0,0,10000),R.Bottom);
            }
        }
        else if (Sleeping) ++SleepingSkipped;
        R.Velocity = Velocity; R.bObserved = true;
        R.StillTime=(Velocity.SizeSquared()<25.f && R.AngularVelocity.SizeSquared()<.04f) ? R.StillTime+DeltaSeconds : 0.f;
        if (auto* Actor = R.Actor.Get(); Actor && ULobbyFacingPool::ShouldPool(R.Owner.Get()))
        {
            auto* Pool=GetWorld()->GetSubsystem<ULobbyFacingPool>();
            auto* Part=Actor->GetStaticMeshComponent();
            if (R.RenderHandle && !Pool->SourceMatches(R.Owner.Get(),R.RenderHandle,Part))
            {
                Pool->Remove(R.Owner.Get(),R.RenderHandle); R.RenderHandle=0;
                Part->SetVisibility(true); Part->SetCastShadow(true);
            }
            if (!R.RenderHandle)
            {
                R.RenderHandle=Pool->AddDebris(R.Owner.Get(),R.Stamp.Id.Local,Part,Pose);
                if (R.RenderHandle) { Part->SetVisibility(false); Part->SetCastShadow(false); }
            }
            else if (Moved) Pool->Update(R.Owner.Get(),R.RenderHandle,Pose);
        }
    }
    Batch->Outputs.SetNum(Batch->Inputs.Num());
    TArray<UE::Tasks::FTask> Jobs;
    const int32 ParallelMode=ParallelFragments.GetValueOnGameThread();
    const int32 BatchSize=64;
    const bool Parallel=ParallelMode && Batch->Inputs.Num()>=(ParallelMode==2 ? 2:128);
    for (int32 Begin=0; Begin<Batch->Inputs.Num(); Begin+=BatchSize)
    {
        const int32 End=FMath::Min(Begin+BatchSize,Batch->Inputs.Num());
        auto Calculate=[Batch,Begin,End]()
        {
            for (int32 I=Begin; I<End; ++I)
            {
                const auto& Input=Batch->Inputs[I];
                Batch->Outputs[I]={Input.Stamp,DestructionFragmentMath::LowestPoint(*Input.Hull,Input.Pose)};
            }
        };
        if (Parallel)
        {
            Jobs.Add(UE::Tasks::Launch(UE_SOURCE_LOCATION,MoveTemp(Calculate)));
            ++ParallelJobs;
        }
        else Calculate();
    }
    for (const int64 Handle : Invalid) Forget(Handle);
    // Publish every moved bound before querying any neighbours.
    for (const int64 Handle : Changed) if (auto* R=Records.Find(Handle)) UpdateSpatial(*R);
    for (const int64 Handle : Changed)
        if (auto* R=Records.Find(Handle); R && !R->Pose.Equals(R->DependencyPose,.01f))
        { InvalidateDependents(*R); R->DependencyPose=R->Pose; }
    // Jobs overlap spatial publication and urgent dependency invalidation. No
    // UObject or engine query is touched by workers. Same-frame completion keeps
    // support/hit decisions authoritative and bounds the storage lifetime.
    for (const auto& Job : Jobs) Job.Wait();
    for (int32 I=0; I<Batch->Outputs.Num(); ++I)
    {
        const auto& Result=Batch->Outputs[I];
        const int64* Handle=Identity.Find(Result.Stamp.Id);
        auto* R=Handle ? Records.Find(*Handle) : nullptr;
        if (!R || !Valid(*R)) { ++RejectedResults; continue; }
        if (!(R->Stamp==Result.Stamp))
        {
            ++RejectedResults;
            if (R->Hull) R->Bottom=DestructionFragmentMath::LowestPoint(*R->Hull,R->Pose);
            continue;
        }
        if (ParallelMode==2)
        {
            ++SerialComparisons;
            ensureAlwaysMsgf(Result.Bottom.Equals(DestructionFragmentMath::LowestPoint(*Batch->Inputs[I].Hull,
                Batch->Inputs[I].Pose),0.f),TEXT("Serial/parallel fragment output differs"));
        }
        R->Bottom=Result.Bottom;
    }
    for (auto& Pair : Records)
    {
        auto& R = Pair.Value;
        if (!R.bObserved || R.State == EDestructionFragmentState::Held) continue;
        const bool LostSupport=R.StaticSupport.IsStale() || (R.StaticSupport.IsValid() &&
            !R.SupportPose.Equals(R.StaticSupport->GetComponentTransform(),0.f));
        if (LostSupport)
        {
            R.bSupportDirty=true; R.NextSupportCheck=0.;
            if (R.State==EDestructionFragmentState::Asleep)
                Command(R.Handle,4,FVector::ZeroVector,FVector::ZeroVector,FTransform::Identity);
        }
        if (R.StillTime<.2f) continue;
        if (Now<R.NextSupportCheck) continue;
        // Stagger validation of static collision/attachment changes that do not
        // move a component. Normal sleeping contacts otherwise do no full scans.
        R.NextSupportCheck = Now + (R.State==EDestructionFragmentState::Asleep ? 5. : .25) + double(R.Handle % 17) * .003;
        R.bSupportDirty = false;
        R.bSupported=FindSupport(R);
        if (!R.bSupported && R.State==EDestructionFragmentState::Asleep)
            Command(R.Handle,4,FVector::ZeroVector,FVector::ZeroVector,FTransform::Identity);
        // Let Chaos put the entire contact island to sleep. Forcing individual
        // slow bodies asleep here fights their still-active neighbours, causing
        // sleep/wake churn and a support query on almost every frame.
    }
    GetWorld()->GetSubsystem<ULobbyFacingPool>()->Flush();
    bCollectingCommands=false;
    for (auto& Pair : PendingCommands)
        if (Pair.Key.IsValid()) CommandDemoColumnLeaves(Pair.Key.Get(),MoveTemp(Pair.Value));
    PendingCommands.Reset();
}

FString UDestructionFragmentWorld::GetState() const
{
    auto Out = MakeShared<FJsonObject>();
    int32 Awake=0, Asleep=0, Held=0;
    int32 FreeCount=0,Quarantined=0,Rendered=0,RenderMismatches=0;
    for (const auto& Pair : Free)
        for (const auto& Actor : Pair.Value)
            if (Actor.IsValid()) { ++FreeCount; Quarantined+=ReuseAfterFrame.FindRef(Actor.Get())>GFrameCounter; }
    TArray<TSharedPtr<FJsonValue>> Items;
    for (const auto& Pair : Records)
    {
        const auto& R=Pair.Value;
        Awake += R.State == EDestructionFragmentState::Awake;
        Asleep += R.State == EDestructionFragmentState::Asleep;
        Held += R.State == EDestructionFragmentState::Held;
        auto Item=MakeShared<FJsonObject>();
        Item->SetNumberField(TEXT("handle"),double(R.Handle));
        Item->SetNumberField(TEXT("owner"),double(R.Stamp.Id.Owner));
        Item->SetNumberField(TEXT("generation"),R.Stamp.Id.Generation);
        Item->SetNumberField(TEXT("local"),R.Stamp.Id.Local);
        Item->SetNumberField(TEXT("state"),int32(R.State));
        Item->SetNumberField(TEXT("supports"),R.Supports.Num());
        Item->SetNumberField(TEXT("state_revision"),double(R.Stamp.StateRevision));
        Item->SetNumberField(TEXT("pose_revision"),double(R.Stamp.PoseRevision));
        Item->SetNumberField(TEXT("speed"),R.Velocity.Size());
        Item->SetStringField(TEXT("position"),R.Pose.GetLocation().ToString());
        if (R.RenderHandle)
        {
            ++Rendered;
            RenderMismatches+=!GetWorld()->GetSubsystem<ULobbyFacingPool>()->Matches(R.Owner.Get(),R.RenderHandle,R.Pose);
        }
        Items.Add(MakeShared<FJsonValueObject>(Item));
    }
    Out->SetNumberField(TEXT("active"),Records.Num()); Out->SetNumberField(TEXT("allocated"),Allocations.Num());
    Out->SetNumberField(TEXT("active_pooled"),LooseLookup.Num()); Out->SetNumberField(TEXT("free"),FreeCount);
    Out->SetNumberField(TEXT("quarantined"),Quarantined); Out->SetNumberField(TEXT("rendered_debris"),Rendered);
    Out->SetNumberField(TEXT("render_mismatches"),RenderMismatches); Out->SetNumberField(TEXT("cached_hulls"),HullCache.Num());
    Out->SetNumberField(TEXT("awake"),Awake); Out->SetNumberField(TEXT("asleep"),Asleep); Out->SetNumberField(TEXT("held"),Held);
    Out->SetNumberField(TEXT("reused"),double(Reused)); Out->SetNumberField(TEXT("grown"),double(Grown));
    Out->SetNumberField(TEXT("allocation_failures"),double(AllocationFailures));
    Out->SetNumberField(TEXT("support_tests"),double(SupportTests)); Out->SetNumberField(TEXT("wake_commands"),double(WakeCommands));
    Out->SetNumberField(TEXT("pose_changes"),double(PoseChanges)); Out->SetNumberField(TEXT("sleeping_skipped"),double(SleepingSkipped));
    Out->SetNumberField(TEXT("parallel_jobs"),double(ParallelJobs));
    Out->SetNumberField(TEXT("rejected_results"),double(RejectedResults));
    Out->SetNumberField(TEXT("serial_comparisons"),double(SerialComparisons));
    Out->SetArrayField(TEXT("fragments"),Items);
    FString Result; auto Writer=TJsonWriterFactory<>::Create(&Result); FJsonSerializer::Serialize(Out,Writer); return Result;
}

void UDestructionFragmentWorld::Deinitialize()
{
    bTearingDown = true;
    for (auto& Pair : Records) Pair.Value.Guard->Valid.Store(false);
    Records.Reset(); Identity.Reset(); LooseLookup.Reset(); Spatial.Reset(); Free.Reset(); PoolKeys.Reset(); HullCache.Reset(); ReuseAfterFrame.Reset();
    PendingCommands.Reset();
    for (AStaticMeshActor* Actor : Allocations) if (IsValid(Actor)) Actor->Destroy();
    Allocations.Reset(); CachedResources.Reset();
    if (IsValid(Driver)) Driver->Destroy();
    Driver=nullptr;
    Super::Deinitialize();
}
