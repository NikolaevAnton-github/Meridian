#include "NGDPropComponent.h"
#include "DestructionCollisionPolicy.h"
#include "GeometryCollection/GeometryCollectionComponent.h"
#include "Engine/Engine.h"
#include "Engine/LatentActionManager.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "ChaosSolversModule.h"
#include "PBDRigidsSolver.h"
#include "Physics/Experimental/PhysScene_Chaos.h"
#include "PhysicsField/PhysicsFieldComponent.h"
#include "PhysicsProxy/PerSolverFieldSystem.h"
#include "GameFramework/PlayerController.h"
#include "InputKeyEventArgs.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInterface.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Serialization/JsonSerializer.h"
#include "TimerManager.h"
#include "UObject/StructOnScope.h"
#include "UObject/UnrealType.h"

namespace
{
constexpr TCHAR VendorClass[] = TEXT("/Game/NextGenDestruction/Blueprints/Actors/BP_BreakableObject.BP_BreakableObject_C");
constexpr TCHAR VendorField[] = TEXT("/Game/NextGenDestruction/Blueprints/Actors/BP_DestructionField.BP_DestructionField_C");
UFunction* ImpactFunction(AActor* Actor)
{
    if (!Actor) return nullptr;
    for (TFieldIterator<UFunction> It(Actor->GetClass()); It; ++It)
    {
        FString Name = It->GetName().Replace(TEXT(" "), TEXT(""));
        if (Name == TEXT("BulletImpact")) return *It;
    }
    return nullptr;
}
FStructProperty* HitParameter(UFunction* Function)
{
    if (!Function) return nullptr;
    for (TFieldIterator<FProperty> It(Function); It; ++It)
        if (It->HasAnyPropertyFlags(CPF_Parm))
            if (auto* P = CastField<FStructProperty>(*It); P && P->Struct == FHitResult::StaticStruct()) return P;
    return nullptr;
}
FObjectPropertyBase* DataProperty(AActor* Actor)
{
    return Actor ? FindFProperty<FObjectPropertyBase>(Actor->GetClass(), TEXT("DataAsset")) : nullptr;
}
TMap<int32, TObjectPtr<UMaterialInterface>> ReadMaterialOverrides(AActor* Actor)
{
    TMap<int32, TObjectPtr<UMaterialInterface>> Result;
    auto* P = FindFProperty<FMapProperty>(Actor->GetClass(), TEXT("Material Overrides"));
    auto* Key = P ? CastField<FIntProperty>(P->KeyProp) : nullptr;
    auto* Value = P ? CastField<FObjectPropertyBase>(P->ValueProp) : nullptr;
    if (!Key || !Value) return Result;
    FScriptMapHelper Map(P, P->ContainerPtrToValuePtr<void>(Actor));
    for (int32 I = 0; I < Map.GetMaxIndex(); ++I) if (Map.IsValidIndex(I))
        Result.Add(Key->GetPropertyValue(Map.GetKeyPtr(I)), Cast<UMaterialInterface>(Value->GetObjectPropertyValue(Map.GetValuePtr(I))));
    return Result;
}
void WriteMaterialOverrides(AActor* Actor, const TMap<int32, TObjectPtr<UMaterialInterface>>& Overrides)
{
    auto* P = FindFProperty<FMapProperty>(Actor->GetClass(), TEXT("Material Overrides"));
    auto* Key = P ? CastField<FIntProperty>(P->KeyProp) : nullptr;
    auto* Value = P ? CastField<FObjectPropertyBase>(P->ValueProp) : nullptr;
    if (!ensure(Key && Value)) return;
    FScriptMapHelper Map(P, P->ContainerPtrToValuePtr<void>(Actor));
    Map.EmptyValues();
    for (const auto& Entry : Overrides)
    {
        const int32 I = Map.AddDefaultValue_Invalid_NeedsRehash();
        Key->SetPropertyValue(Map.GetKeyPtr(I), Entry.Key);
        Value->SetObjectPropertyValue(Map.GetValuePtr(I), Entry.Value);
    }
    Map.Rehash();
}
void CancelWork(AActor* Actor)
{
    if (!IsValid(Actor) || !Actor->GetWorld()) return;
    Actor->GetWorld()->GetLatentActionManager().RemoveActionsForObject(Actor);
    Actor->GetWorld()->GetTimerManager().ClearAllTimersForObject(Actor);
}
void CancelQueuedFields(UWorld* World, const TArray<FName>& Names)
{
    if (!World || Names.IsEmpty()) return;
    // Destroying a FieldSystemComponent only removes persistent commands. Its already
    // queued transient strain/velocity otherwise reaches a replacement collection.
    if (UPhysicsFieldComponent* Fields = World->PhysicsField)
    {
        for (const bool GPU : {false, true})
        {
            const auto Buffer = GPU ? EFieldCommandBuffer::GPUFieldBuffer : EFieldCommandBuffer::CPUWriteBuffer;
            const TArray<FFieldSystemCommand> Commands = Fields->TransientCommands[uint8(Buffer)];
            for (const auto& Command : Commands)
                if (Names.Contains(Command.CommandName)) Fields->RemoveTransientCommand(Command, GPU);
        }
    }
    if (FPhysScene* Scene = World->GetPhysicsScene())
    {
        TArray<Chaos::FPhysicsSolverBase*> Solvers{Scene->GetSolver()};
        if (auto* Module = FChaosSolversModule::GetModule()) Module->GetSolversMutable(World, Solvers);
        for (auto* Solver : Solvers) if (Solver)
            Solver->CastHelper([&Names](auto& Concrete)
            {
                Concrete.EnqueueCommandImmediate([Solver = &Concrete, OwnedNames = Names]()
                {
                    // Runs after the vendor's queued additions on this solver. Never clear
                    // another actor's fields or mutate solver arrays from the game thread.
                    auto& Commands = Solver->GetPerSolverField().GetTransientCommands();
                    const int32 Removed = Commands.RemoveAll([&](const FFieldSystemCommand& Command)
                    { return OwnedNames.Contains(Command.CommandName); });
                    if (Removed) UE_LOG(LogTemp, Display, TEXT("NGD retired %d owned transient solver commands"), Removed);
                });
            });
    }
}
FString Json(const TSharedRef<FJsonObject>& Object)
{
    FString Out;
    FJsonSerializer::Serialize(Object, TJsonWriterFactory<>::Create(&Out));
    return Out;
}
void VectorField(const TSharedRef<FJsonObject>& Object, const TCHAR* Name, const FVector& V)
{
    Object->SetArrayField(Name, {MakeShared<FJsonValueNumber>(V.X), MakeShared<FJsonValueNumber>(V.Y), MakeShared<FJsonValueNumber>(V.Z)});
}
}

void UNGDWorldSubsystem::Initialize(FSubsystemCollectionBase& Subsystems)
{
    Super::Initialize(Subsystems);
    // Batching remains an opt-in standalone experiment; no scene timing gain was measured.
    FString Mode;
    if (!GIsEditor && GetWorld()->WorldType == EWorldType::Game &&
        FParse::Value(FCommandLine::Get(), TEXT("DestructionNotificationMode="), Mode))
    {
        bBatchNotifications = Mode == TEXT("batch");
        if (Mode != TEXT("immediate") && Mode != TEXT("batch"))
            UE_LOG(LogTemp, Warning, TEXT("Unknown DestructionNotificationMode '%s'; using immediate"), *Mode);
    }
    PostActorTickHandle = FWorldDelegates::OnWorldPostActorTick.AddUObject(this, &UNGDWorldSubsystem::PostActorTick);
    CreatePhysicsHandle = UActorComponent::GlobalCreatePhysicsDelegate.AddUObject(this, &UNGDWorldSubsystem::PhysicsCreated);
    DestroyPhysicsHandle = UActorComponent::GlobalDestroyPhysicsDelegate.AddUObject(this, &UNGDWorldSubsystem::PhysicsDestroyed);
}

void UNGDWorldSubsystem::Deinitialize()
{
    FWorldDelegates::OnWorldPostActorTick.Remove(PostActorTickHandle);
    UActorComponent::GlobalCreatePhysicsDelegate.Remove(CreatePhysicsHandle);
    UActorComponent::GlobalDestroyPhysicsDelegate.Remove(DestroyPhysicsHandle);
    for (const auto& Entry : PendingSources)
        if (auto* Source = Entry.Adapter.Get())
        {
            Source->bPendingNotification = false;
            Source->PendingChange = FNGDCollisionChange();
        }
    PendingSources.Reset();
    SourcesByCollection.Reset();
    LatestChanges.Reset();
    LatestActorChanges.Reset();
    OnCollisionChanged.Clear();
    OnCollisionChangesBatched.Clear();
    OnCollisionChangesBatchedNative.Clear();
    Super::Deinitialize();
}

void UNGDWorldSubsystem::PostActorTick(UWorld* World, ELevelTick TickType, float DeltaSeconds)
{
    if (World == GetWorld()) FlushPending();
}

void UNGDWorldSubsystem::PhysicsDestroyed(UActorComponent* Component)
{
    const auto* Entry = SourcesByCollection.Find(Component);
    auto* Source = Entry ? Entry->Get() : nullptr;
    if (!Source || Source->bRetiring || Source->bPhysicsRecreating) return;
    Source->bPhysicsRecreating = true;
    Source->PhysicsRecreationBounds = Source->PreviousBounds + Source->Collection->Bounds.GetBox();
    Source->PhysicsRecreationBounds += CancelPending(Source);
    ++Source->ResetNotificationInvalidations;
}

void UNGDWorldSubsystem::PhysicsCreated(UActorComponent* Component)
{
    const auto* Entry = SourcesByCollection.Find(Component);
    auto* Source = Entry ? Entry->Get() : nullptr;
    if (!Source || Source->bRetiring || !Source->bPhysicsRecreating) return;
    Source->bPhysicsRecreating = false;
    Source->AdapterLifetimeId = ++NextLifetimeId;
    Source->LastNotificationFrame = MAX_uint64;
    ++Source->CollisionRevision;
    ++Source->ResetGeneration;
    ++Source->PhysicsRecreations;
    const FBox Previous = Source->PhysicsRecreationBounds;
    Source->PhysicsRecreationBounds = FBox(ForceInit);
    // The component address/path can be unchanged while its particle/proxy lifetime is new.
    Publish(Source, Source->MakeChange(TEXT("reset"), Previous));
}

void UNGDWorldSubsystem::Publish(UNGDPropComponent* Source, const FNGDCollisionChange& Change)
{
    // The legacy last-value map remains synchronous, including its copied-ObjectId behavior.
    LatestChanges.Add(Change.ObjectId, Change);
    const bool bQueue = bBatchNotifications && Change.Reason == TEXT("break");
    if (bQueue)
    {
        ++Source->QueuedNotificationChanges;
        if (Source->bPendingNotification)
        {
            Source->PendingChange.ChangedBounds += Change.ChangedBounds;
            Source->PendingChange.CollisionRevision = Change.CollisionRevision;
            Source->PendingChange.ChangeCount += Change.ChangeCount;
        }
        else
        {
            Source->PendingChange = Change;
            Source->bPendingNotification = true;
            PendingSources.Add({Source, Source->Collection.Get(), Source->AdapterLifetimeId});
        }
    }
    // Queue first: a legacy listener can reset/destroy the source during this exact callback.
    if (OnCollisionChanged.IsBound())
    {
        ++Source->LegacyNotificationPublications;
        OnCollisionChanged.Broadcast(Change);
    }
    if (!bQueue && !Source->bRetiring && !Source->bPhysicsRecreating && Source->AdapterLifetimeId == Change.AdapterLifetimeId)
        PublishBatch(Source, Change);
}

void UNGDWorldSubsystem::PublishBatch(UNGDPropComponent* Source, const FNGDCollisionChange& Change)
{
    if (Source->bRetiring || Source->bPhysicsRecreating || Source->AdapterLifetimeId != Change.AdapterLifetimeId) return;
    // A synchronous legacy listener may have recursively published a later revision.
    const auto* Latest = LatestActorChanges.Find(Change.ActorPath);
    if (Latest && Latest->AdapterLifetimeId == Change.AdapterLifetimeId &&
        Latest->CollisionRevision > Change.CollisionRevision) return;
    LatestActorChanges.Add(Change.ActorPath, Change);
    ++Source->PublishedNotificationBatches;
    Source->PublishedNotificationChanges += Change.ChangeCount;
    OnCollisionChangesBatched.Broadcast(Change);
    if (!Source->bRetiring && !Source->bPhysicsRecreating && Source->AdapterLifetimeId == Change.AdapterLifetimeId)
        OnCollisionChangesBatchedNative.Broadcast(Change);
}

FBox UNGDWorldSubsystem::CancelPending(UNGDPropComponent* Source)
{
    FBox Bounds(ForceInit);
    if (Source->bPendingNotification)
    {
        Bounds = Source->PendingChange.ChangedBounds;
        Source->InvalidatedNotificationChanges += Source->PendingChange.ChangeCount;
        Source->LifetimeInvalidatedNotificationChanges += Source->PendingChange.ChangeCount;
        Source->bPendingNotification = false;
        Source->PendingChange = FNGDCollisionChange();
    }
    PendingSources.RemoveAll([Source](const FPendingSource& Entry)
    { return Entry.Adapter == Source && Entry.LifetimeId == Source->AdapterLifetimeId; });
    if (const auto* Latest = LatestActorChanges.Find(Source->ActorPath);
        Latest && Latest->AdapterLifetimeId == Source->AdapterLifetimeId)
        LatestActorChanges.Remove(Source->ActorPath);
    return Bounds;
}

void UNGDWorldSubsystem::FlushPending()
{
    if (bFlushing || PendingSources.IsEmpty()) return;
    TGuardValue<bool> Guard(bFlushing, true);
    // Detach the queue before callbacks. Reentrant new work belongs to a later flush.
    TArray<FPendingSource> Sources = MoveTemp(PendingSources);
    PendingSources.Reset();
    for (const auto& Entry : Sources)
    {
        auto* Source = Entry.Adapter.Get();
        if (!Source || Source->bRetiring || Source->bPhysicsRecreating || !Source->bPendingNotification ||
            Source->AdapterLifetimeId != Entry.LifetimeId) continue;
        if (Source->Collection != Entry.Collection.Get())
        {
            CancelPending(Source);
            continue;
        }
        if (Source->LastNotificationFrame == GFrameCounter)
        {
            PendingSources.Add(Entry);
            continue;
        }
        FNGDCollisionChange Change = MoveTemp(Source->PendingChange);
        Source->PendingChange = FNGDCollisionChange();
        Source->bPendingNotification = false;
        Source->LastNotificationFrame = GFrameCounter;
        PublishBatch(Source, Change);
    }
}

void UNGDPropComponent::CancelPendingFields(UWorld* World, const TArray<FName>& Names)
{
    CancelQueuedFields(World, Names);
}

UNGDPropComponent::UNGDPropComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}
void UNGDPropComponent::BeginPlay()
{
    Super::BeginPlay();
    InitialTransform = GetOwner()->GetActorTransform();
    SourceMaterialOverrides = ReadMaterialOverrides(GetOwner());
    if (auto* P = DataProperty(GetOwner())) SourceData = P->GetObjectPropertyValue_InContainer(GetOwner());
    Collection = GetOwner()->FindComponentByClass<UGeometryCollectionComponent>();
    bReady = Collection && SourceData && !ObjectId.IsNone() && HitParameter(ImpactFunction(GetOwner()));
    if (!bReady)
    {
        UE_LOG(LogTemp, Error, TEXT("NGD adapter unavailable: %s"), *GetOwner()->GetPathName());
        return;
    }
    Collection->SetNotifyBreaks(true);
    Collection->OnChaosBreakEvent.AddUniqueDynamic(this, &UNGDPropComponent::OnBreak);
    CollisionPolicy = NewObject<UDestructionCollisionPolicy>(GetOwner(), NAME_None, RF_Transient);
    GetOwner()->AddInstanceComponent(CollisionPolicy);
    CollisionPolicy->RegisterComponent();
    CollisionPolicy->Initialize(Collection);
    PreviousBounds = Collection->Bounds.GetBox();
    ActorPath = FName(*GetOwner()->GetPathName());
    AdapterPath = FName(*GetPathName());
    CollectionPath = FName(*Collection->GetPathName());
    AdapterLifetimeId = ++GetWorld()->GetSubsystem<UNGDWorldSubsystem>()->NextLifetimeId;
    GetWorld()->GetSubsystem<UNGDWorldSubsystem>()->SourcesByCollection.Add(Collection.Get(), this);
    Publish(ResetGeneration ? TEXT("reset") : TEXT("initial"), ResetBounds.IsValid ? ResetBounds : PreviousBounds);
}
FNGDCollisionChange UNGDPropComponent::MakeChange(FName Reason, const FBox& Previous)
{
    const FBox Current = Collection->Bounds.GetBox();
    FNGDCollisionChange Change;
    Change.ObjectId = ObjectId;
    Change.ActorPath = ActorPath;
    Change.AdapterPath = AdapterPath;
    Change.CollectionPath = CollectionPath;
    Change.AdapterLifetimeId = AdapterLifetimeId;
    Change.FirstCollisionRevision = CollisionRevision;
    Change.CollisionRevision = CollisionRevision;
    Change.ResetGeneration = ResetGeneration;
    Change.ChangedBounds = Previous + Current;
    Change.Reason = Reason;
    PreviousBounds = Current;
    return Change;
}
void UNGDPropComponent::Publish(FName Reason, const FBox& Previous)
{
    if (!Collection || !GetWorld()) return;
    GetWorld()->GetSubsystem<UNGDWorldSubsystem>()->Publish(this, MakeChange(Reason, Previous));
}
void UNGDPropComponent::OnBreak(const FChaosBreakEvent& Event)
{
    if (bRetiring || bPhysicsRecreating || !bReady || Event.Component != Collection) return;
    ++BreakEvents;
    ++CollisionRevision;
    Publish(TEXT("break"), PreviousBounds);
}
bool UNGDPropComponent::ReceiveBullet(int64 ShotId, const FHitResult& Hit)
{
    if (!bReady || bRetiring || bPhysicsRecreating || ShotId <= 0 || Hit.GetActor() != GetOwner() || RecentShots.Contains(ShotId)) return true;
    UFunction* Function = ImpactFunction(GetOwner());
    FStructProperty* Parameter = HitParameter(Function);
    if (!Parameter) return true;
    // The finite sweep already selected and consumed this bullet. Never retrace or send PointDamage too.
    if (RecentShots.Num() == 64) RecentShots.RemoveAt(0);
    RecentShots.Add(ShotId);
    LastShotId = ShotId;
    ++DeliveredHits;
    FStructOnScope Params(Function);
    Parameter->CopyCompleteValue(Parameter->ContainerPtrToValuePtr<void>(Params.GetStructMemory()), &Hit);
    // The vendor defaults (no radius override) retain per-source strain, anchoring and impulse choices.
    Fields.RemoveAll([](const TWeakObjectPtr<AActor>& Field) { return !Field.IsValid(); });
    const FDelegateHandle Handle = GetWorld()->AddOnActorSpawnedHandler(FOnActorSpawned::FDelegate::CreateLambda([this](AActor* Spawned)
    {
        if (Spawned && Spawned->GetClass()->GetPathName() == VendorField)
        {
            Fields.Add(Spawned);
            if (FieldNames.Num() == 64) FieldNames.RemoveAt(0);
            FieldNames.Add(Spawned->GetFName());
        }
    }));
    GetOwner()->ProcessEvent(Function, Params.GetStructMemory());
    GetWorld()->RemoveOnActorSpawnedHandler(Handle);
    UE_LOG(LogTemp, Display, TEXT("NGD impact id=%s generation=%d shot=%lld item=%d location=%s"),
        *ObjectId.ToString(), ResetGeneration, ShotId, Hit.Item, *Hit.ImpactPoint.ToString());
    return true;
}
void UNGDPropComponent::Retire()
{
    if (bRetiring) return;
    bRetiring = true;
    bReady = false;
    if (auto* Subsystem = GetWorld() ? GetWorld()->GetSubsystem<UNGDWorldSubsystem>() : nullptr)
    {
        Subsystem->CancelPending(this);
        Subsystem->SourcesByCollection.Remove(Collection.Get());
    }
    if (Collection) Collection->OnChaosBreakEvent.RemoveDynamic(this, &UNGDPropComponent::OnBreak);
    if (CollisionPolicy) CollisionPolicy->Restore();
    CancelWork(GetOwner());
    for (const auto& Field : Fields) if (Field.IsValid())
    {
        CancelWork(Field.Get());
        Field->Destroy();
    }
    Fields.Reset();
    CancelQueuedFields(GetWorld(), FieldNames);
    FieldNames.Reset();
}
void UNGDPropComponent::EndPlay(const EEndPlayReason::Type Reason)
{
    Retire();
    Super::EndPlay(Reason);
}
void UNGDPropComponent::ResetAll(UWorld* World)
{
    if (!World || !World->IsGameWorld()) return;
    TArray<UNGDPropComponent*> Props;
    for (TActorIterator<AActor> It(World); It; ++It)
        if (auto* C = It->FindComponentByClass<UNGDPropComponent>(); C && !C->bRetiring) Props.Add(C);
    for (UNGDPropComponent* C : Props)
    {
        if (!C->SourceData) continue;
        UObject* Data = C->SourceData;
        const auto MaterialOverrides = C->SourceMaterialOverrides;
        const FTransform Transform = C->InitialTransform;
        const FName Id = C->ObjectId;
        const int32 Generation = C->ResetGeneration + 1, Revision = C->CollisionRevision + 1;
        FBox PriorBounds = C->Collection ? C->Collection->Bounds.GetBox() : C->PreviousBounds;
        PriorBounds += C->PhysicsRecreationBounds;
        // Reset supersedes the pending old-lifetime signal but must retain every swept envelope.
        if (auto* Subsystem = World->GetSubsystem<UNGDWorldSubsystem>())
            PriorBounds += Subsystem->CancelPending(C);
        ++C->ResetNotificationInvalidations;
        C->Retire();
        // Destroying the whole vendor instance retires its physics proxy, latent sound work,
        // per-particle collision overrides and delegate targets together.
        C->GetOwner()->SetActorEnableCollision(false);
        C->GetOwner()->Destroy();
        if (auto* Replacement = UNGDTools::Spawn(World, Data, Transform, Id, Generation, Revision, PriorBounds, MaterialOverrides))
        {
            auto* NewAdapter = Replacement->FindComponentByClass<UNGDPropComponent>();
            NewAdapter->ResetNotificationInvalidations = C->ResetNotificationInvalidations;
            NewAdapter->InvalidatedNotificationChanges = C->InvalidatedNotificationChanges;
        }
        else
            UE_LOG(LogTemp, Error, TEXT("NGD reset failed: %s"), *Id.ToString());
    }
}
FString UNGDPropComponent::GetState() const
{
    auto O = MakeShared<FJsonObject>();
    O->SetStringField(TEXT("id"), ObjectId.ToString());
    O->SetStringField(TEXT("actor"), GetOwner()->GetPathName());
    O->SetBoolField(TEXT("ready"), bReady);
    O->SetStringField(TEXT("data_asset"), SourceData ? SourceData->GetPathName() : TEXT(""));
    O->SetNumberField(TEXT("collision_revision"), CollisionRevision);
    O->SetNumberField(TEXT("reset_generation"), ResetGeneration);
    O->SetNumberField(TEXT("delivered_hits"), DeliveredHits);
    O->SetNumberField(TEXT("break_events"), BreakEvents);
    O->SetNumberField(TEXT("last_shot"), LastShotId);
    auto Notifications = MakeShared<FJsonObject>();
    const auto* Subsystem = GetWorld() ? GetWorld()->GetSubsystem<UNGDWorldSubsystem>() : nullptr;
    Notifications->SetStringField(TEXT("mode"), Subsystem && Subsystem->UsesBatchedNotifications() ? TEXT("batch") : TEXT("immediate"));
    Notifications->SetStringField(TEXT("actor_path"), ActorPath.ToString());
    Notifications->SetStringField(TEXT("adapter_path"), AdapterPath.ToString());
    Notifications->SetStringField(TEXT("collection_path"), CollectionPath.ToString());
    Notifications->SetNumberField(TEXT("adapter_lifetime_id"), double(AdapterLifetimeId));
    Notifications->SetNumberField(TEXT("raw_break_callbacks"), BreakEvents);
    Notifications->SetNumberField(TEXT("queued_changes"), double(QueuedNotificationChanges));
    Notifications->SetNumberField(TEXT("pending_changes"), bPendingNotification ? PendingChange.ChangeCount : 0);
    Notifications->SetNumberField(TEXT("published_batches"), double(PublishedNotificationBatches));
    Notifications->SetNumberField(TEXT("published_changes"), double(PublishedNotificationChanges));
    Notifications->SetNumberField(TEXT("legacy_publications"), double(LegacyNotificationPublications));
    Notifications->SetNumberField(TEXT("reset_invalidations"), double(ResetNotificationInvalidations));
    Notifications->SetNumberField(TEXT("invalidated_changes"), double(InvalidatedNotificationChanges));
    Notifications->SetNumberField(TEXT("lifetime_invalidated_changes"), double(LifetimeInvalidatedNotificationChanges));
    Notifications->SetNumberField(TEXT("physics_recreations"), PhysicsRecreations);
    Notifications->SetBoolField(TEXT("physics_recreating"), bPhysicsRecreating);
    O->SetObjectField(TEXT("notifications"), Notifications);
    if (CollisionPolicy) O->SetObjectField(TEXT("collision_policy"), CollisionPolicy->Snapshot());
    auto Overrides = MakeShared<FJsonObject>();
    for (const auto& Entry : SourceMaterialOverrides)
        Overrides->SetStringField(FString::FromInt(Entry.Key), Entry.Value ? Entry.Value->GetPathName() : TEXT(""));
    O->SetObjectField(TEXT("material_overrides"), Overrides);
    O->SetNumberField(TEXT("live_fields"), Fields.FilterByPredicate([](const auto& F){ return F.IsValid(); }).Num());
    if (Collection)
    {
        VectorField(O, TEXT("bounds_min"), Collection->Bounds.GetBox().Min);
        VectorField(O, TEXT("bounds_max"), Collection->Bounds.GetBox().Max);
        O->SetStringField(TEXT("collision_profile"), Collection->GetCollisionProfileName().ToString());
        O->SetBoolField(TEXT("root_broken"), Collection->IsRootBroken());
        TArray<TSharedPtr<FJsonValue>> Materials;
        for (int32 I = 0; I < Collection->GetNumMaterials(); ++I)
            Materials.Add(MakeShared<FJsonValueString>(Collection->GetMaterial(I) ? Collection->GetMaterial(I)->GetPathName() : TEXT("")));
        O->SetArrayField(TEXT("materials"), Materials);
    }
    return Json(O);
}
AActor* UNGDTools::Spawn(UWorld* World, UObject* DataAsset, const FTransform& Transform, FName Id, int32 Generation, int32 Revision, FBox PriorBounds,
    const TMap<int32, TObjectPtr<UMaterialInterface>>& MaterialOverrides)
{
    if (!World || !DataAsset || Id.IsNone() || !DataAsset->GetPathName().StartsWith(TEXT("/Game/NextGenDestruction/Blueprints/DataAssets/Destructible/"))) return nullptr;
    UClass* Class = LoadClass<AActor>(nullptr, VendorClass);
    if (!Class) return nullptr;
    AActor* Actor = World->SpawnActorDeferred<AActor>(Class, Transform, nullptr, nullptr, ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
    if (!Actor) return nullptr;
    auto* P = DataProperty(Actor);
    if (!P || !DataAsset->IsA(P->PropertyClass)) { Actor->Destroy(); return nullptr; }
    P->SetObjectPropertyValue_InContainer(Actor, DataAsset);
    // Apply before construction so the vendor initializes the same visual
    // variant after reset, including demo instances with material overrides.
    if (!MaterialOverrides.IsEmpty()) WriteMaterialOverrides(Actor, MaterialOverrides);
    auto* C = NewObject<UNGDPropComponent>(Actor, TEXT("NGDIntegration"), RF_Transactional);
    C->ObjectId = Id;
    C->ResetGeneration = Generation;
    C->CollisionRevision = Revision;
    C->ResetBounds = PriorBounds;
    Actor->AddInstanceComponent(C);
    C->RegisterComponent();
    Actor->Tags.Add(TEXT("NGD01"));
    Actor->FinishSpawning(Transform);
#if WITH_EDITOR
    if (!World->IsGameWorld())
    {
        Actor->SetActorLabel(Id.ToString());
        Actor->SetFolderPath(TEXT("NGD01_DemoProps"));
        Actor->MarkPackageDirty();
    }
#endif
    return Actor;
}
AActor* UNGDTools::SpawnProp(UObject* Context, UObject* DataAsset, FVector Location, FRotator Rotation, FName ObjectId)
{
    return Spawn(GEngine->GetWorldFromContextObject(Context, EGetWorldErrorMode::ReturnNull), DataAsset, FTransform(Rotation, Location), ObjectId, 0, 0);
}
AActor* UNGDTools::SpawnPropWithMaterials(UObject* Context, UObject* DataAsset, FVector Location, FRotator Rotation, FName ObjectId,
    const TMap<int32, UMaterialInterface*>& MaterialOverrides)
{
    TMap<int32, TObjectPtr<UMaterialInterface>> Overrides;
    for (const auto& Entry : MaterialOverrides) Overrides.Add(Entry.Key, Entry.Value);
    return Spawn(GEngine->GetWorldFromContextObject(Context, EGetWorldErrorMode::ReturnNull), DataAsset,
        FTransform(Rotation, Location), ObjectId, 0, 0, FBox(ForceInit), Overrides);
}
bool UNGDTools::RifleInput(UObject* Context, bool bPressed)
{
    UWorld* W = GEngine->GetWorldFromContextObject(Context, EGetWorldErrorMode::ReturnNull);
    APlayerController* PC = W && W->IsGameWorld() ? UGameplayStatics::GetPlayerController(W, 0) : nullptr;
    return PC && PC->InputKey(FInputKeyEventArgs(nullptr, FInputDeviceId::CreateFromInternalId(0),
        EKeys::LeftMouseButton, bPressed ? IE_Pressed : IE_Released, bPressed ? 1.f : 0.f, false, FPlatformTime::Cycles64()));
}
bool UNGDTools::AimPlayer(UObject* Context, FVector Target)
{
    UWorld* W = GEngine->GetWorldFromContextObject(Context, EGetWorldErrorMode::ReturnNull);
    APlayerController* PC = W && W->IsGameWorld() ? UGameplayStatics::GetPlayerController(W, 0) : nullptr;
    if (!PC || !PC->GetPawn()) return false;
    FVector Location; FRotator Rotation;
    PC->GetPlayerViewPoint(Location, Rotation);
    PC->SetControlRotation((Target - Location).Rotation());
    return true;
}
FString UNGDTools::Sweep(UObject* Context, FVector Start, FVector End, float Radius)
{
    auto O = MakeShared<FJsonObject>();
    UWorld* W = GEngine->GetWorldFromContextObject(Context, EGetWorldErrorMode::ReturnNull);
    if (!W || !FMath::IsFinite(Radius) || Radius <= 0 || Start.ContainsNaN() || End.ContainsNaN()) return TEXT("{}");
    FCollisionQueryParams Query(SCENE_QUERY_STAT(NGDVerification), false);
    if (auto* PC = UGameplayStatics::GetPlayerController(W, 0)) Query.AddIgnoredActor(PC->GetPawn());
    FHitResult Hit;
    const bool Blocked = W->SweepSingleByChannel(Hit, Start, End, FQuat::Identity, ECC_Visibility, FCollisionShape::MakeSphere(Radius), Query);
    O->SetBoolField(TEXT("blocked"), Blocked);
    O->SetStringField(TEXT("actor"), Hit.GetActor() ? Hit.GetActor()->GetName() : TEXT(""));
    O->SetNumberField(TEXT("item"), Hit.Item);
    VectorField(O, TEXT("impact"), Hit.ImpactPoint);
    VectorField(O, TEXT("normal"), Hit.ImpactNormal);
    O->SetNumberField(TEXT("radius"), Radius);
    return Json(O);
}
