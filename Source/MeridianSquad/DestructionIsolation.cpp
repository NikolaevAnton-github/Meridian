#include "DestructionIsolation.h"

#include "Dom/JsonObject.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "HAL/PlatformMisc.h"
#include "ProfilingDebugging/CpuProfilerTrace.h"
#include "UObject/UnrealType.h"

namespace
{
constexpr TCHAR VendorClassPath[] = TEXT("/Game/NextGenDestruction/Blueprints/Actors/BP_BreakableObject.BP_BreakableObject_C");
enum class EIsolationMode { Reference, ProfileObserve, ProfileBatch, CollisionOff };
struct FPropRegistration
{
    TWeakObjectPtr<UDestructionIsolationBridge> Bridge;
    TArray<FScriptDelegate> RemovedCollisionDelegates;
    TArray<TSharedPtr<FJsonValue>> BindingDescriptions;
};
TWeakObjectPtr<UWorld> ActiveWorld;
EIsolationMode ActiveMode = EIsolationMode::Reference;
FString ModeName = TEXT("reference");
TMap<TWeakObjectPtr<UGeometryCollectionComponent>, FPropRegistration> Props;
int64 ReceivedEvents = 0, ForwardedEvents = 0, QueuedEvents = 0, PendingEvents = 0;
int64 PeakPendingEvents = 0, BatchCalls = 0, BatchBoneIds = 0, FlushesWithWork = 0;
int32 ConfiguredProps = 0, SuppressedBindings = 0, SetupFailures = 0;

TArray<FName> OwnerBreakBindings(UGeometryCollectionComponent* Component)
{
    TArray<FName> Names;
    if (AActor* Owner = Component->GetOwner())
        for (TFieldIterator<UFunction> It(Owner->GetClass()); It; ++It)
            if (Component->OnChaosBreakEvent.Contains(Owner, It->GetFName())) Names.Add(It->GetFName());
    return Names;
}

bool ValidateBreakFunction(UFunction* Function)
{
    if (!Function || Function->Script.IsEmpty()) return false;
    TArray<FProperty*> Parameters;
    for (TFieldIterator<FProperty> It(Function); It; ++It)
        if (It->HasAnyPropertyFlags(CPF_Parm)) Parameters.Add(*It);
    const FStructProperty* Event = Parameters.Num() == 1 ? CastField<FStructProperty>(Parameters[0]) : nullptr;
    return Event && Event->Struct == FChaosBreakEvent::StaticStruct()
        && !Event->HasAnyPropertyFlags(CPF_ReturnParm)
        && (!Event->HasAnyPropertyFlags(CPF_OutParm) || Event->HasAnyPropertyFlags(CPF_ConstParm));
}

void ClearCounters()
{
    ReceivedEvents = ForwardedEvents = QueuedEvents = PendingEvents = 0;
    PeakPendingEvents = BatchCalls = BatchBoneIds = FlushesWithWork = 0;
    ConfiguredProps = SuppressedBindings = SetupFailures = 0;
}

void RestoreProps()
{
    for (auto& Entry : Props)
    {
        if (UDestructionIsolationBridge* Bridge = Entry.Value.Bridge.Get())
        {
            Bridge->Restore();
            if (AActor* Owner = Bridge->GetOwner()) Owner->RemoveInstanceComponent(Bridge);
            Bridge->DestroyComponent();
        }
        if (UGeometryCollectionComponent* Component = Entry.Key.Get())
            for (const FScriptDelegate& Delegate : Entry.Value.RemovedCollisionDelegates)
                Component->OnChaosPhysicsCollision.AddUnique(Delegate);
    }
    Props.Reset();
}
}

UDestructionIsolationBridge::UDestructionIsolationBridge()
{
    PrimaryComponentTick.bCanEverTick = false;
}

bool UDestructionIsolationBridge::Initialize(UGeometryCollectionComponent* Component, bool bBatch)
{
    check(IsInGameThread());
    if (bInstalled || !IsValid(Component) || !Component->GetOwner()
        || Component->GetOwner()->GetClass()->GetPathName() != VendorClassPath) return false;
    AActor* Owner = Component->GetOwner();
    const TArray<FName> Names = OwnerBreakBindings(Component);
    // The current hash-verified vendor graph has one break handler. Reject other
    // binding topologies rather than guessing their invocation order or signature.
    int32 OwnerBindings = 0;
    for (UObject* Target : Component->OnChaosBreakEvent.GetAllObjects()) OwnerBindings += Target == Owner;
    if (Names.Num() != 1 || OwnerBindings != 1 || !ValidateBreakFunction(Owner->FindFunction(Names[0]))) return false;
    Collection = Component;
    bBatchEvents = bBatch;
    OriginalBreakDelegates = Component->OnChaosBreakEvent;
    for (UObject* Target : Component->OnChaosBreakEvent.GetAllObjects())
        if (Target != Owner) OriginalBreakDelegates.RemoveAll(Target);
    OriginalBinding.BindUFunction(Owner, Names[0]);
    Collection->OnChaosBreakEvent.Remove(OriginalBinding);
    Collection->OnChaosBreakEvent.AddUniqueDynamic(this, &UDestructionIsolationBridge::OnBreak);
    bInstalled = true;
    return true;
}

void UDestructionIsolationBridge::Forward(const FChaosBreakEvent& Event)
{
    TRACE_CPUPROFILER_EVENT_SCOPE(DP02_ForwardBreakEvent);
    OriginalBreakDelegates.Broadcast(Event);
    ++ForwardedEvents;
}

void UDestructionIsolationBridge::OnBreak(const FChaosBreakEvent& Event)
{
    check(IsInGameThread());
    if (!bInstalled || Event.Component != Collection) return;
    ++ReceivedEvents;
    if (bBatchEvents)
    {
        Pending.Add(Event);
        ++QueuedEvents;
        ++PendingEvents;
        PeakPendingEvents = FMath::Max(PeakPendingEvents, PendingEvents);
    }
    else Forward(Event);
}

void UDestructionIsolationBridge::Flush()
{
    check(IsInGameThread());
    if (!bInstalled || Pending.IsEmpty()) return;
    TRACE_CPUPROFILER_EVENT_SCOPE(DP02_ProfileBatchFlush);
    TArray<FChaosBreakEvent> Events = MoveTemp(Pending);
    Pending.Reset();
    PendingEvents -= Events.Num();
    TSet<int32> Indices;
    for (const FChaosBreakEvent& Event : Events) Indices.Add(Event.Index);
    // The current vendor break graph always writes this profile on Event.Index.
    // Replayed original callbacks retain all side effects; identical profile writes
    // then become native no-ops. Timing/order differences remain diagnostic limits.
    Collection->SetPerParticleCollisionProfileName(Indices, TEXT("IgnoreCharChaos"));
    ++BatchCalls;
    BatchBoneIds += Indices.Num();
    for (const FChaosBreakEvent& Event : Events) Forward(Event);
}

void UDestructionIsolationBridge::Restore()
{
    check(IsInGameThread());
    if (!bInstalled) return;
    bInstalled = false;
    // Normal reset flushes first. EndPlay discards work for an already retiring prop.
    PendingEvents -= Pending.Num();
    Pending.Reset();
    if (IsValid(Collection))
    {
        Collection->OnChaosBreakEvent.RemoveDynamic(this, &UDestructionIsolationBridge::OnBreak);
        Collection->OnChaosBreakEvent.AddUnique(OriginalBinding);
    }
    OriginalBreakDelegates.Clear();
    OriginalBinding.Unbind();
    Collection = nullptr;
}

void UDestructionIsolationBridge::EndPlay(const EEndPlayReason::Type Reason)
{
    Restore();
    Super::EndPlay(Reason);
}

bool DestructionIsolation::Start(UWorld* World, const FString& Mode)
{
    check(IsInGameThread());
    if (!World || World->WorldType != EWorldType::Game || World->GetNetMode() != NM_Standalone || ActiveWorld.IsValid()) return false;
    if (Mode == TEXT("reference")) ActiveMode = EIsolationMode::Reference;
    else if (Mode == TEXT("profile_observe")) ActiveMode = EIsolationMode::ProfileObserve;
    else if (Mode == TEXT("profile_batch")) ActiveMode = EIsolationMode::ProfileBatch;
    else if (Mode == TEXT("collision_off")) ActiveMode = EIsolationMode::CollisionOff;
    else return false;
    ActiveWorld = World;
    ModeName = Mode;
    ClearCounters();
    return true;
}

void DestructionIsolation::ConfigureProp(UGeometryCollectionComponent* Component)
{
    check(IsInGameThread());
    if (!IsValid(Component) || !ActiveWorld.IsValid() || Component->GetWorld() != ActiveWorld.Get() || Props.Contains(Component)) return;
    FPropRegistration& Registration = Props.Add(Component);
    ++ConfiguredProps;
    AActor* Owner = Component->GetOwner();
    if (!Owner || (ActiveMode != EIsolationMode::Reference && Owner->GetClass()->GetPathName() != VendorClassPath))
    {
        ++SetupFailures;
        UE_LOG(LogTemp, Error, TEXT("DP02 rejected unfamiliar prop class"));
        FPlatformMisc::RequestExit(false);
        return;
    }
    TSet<UObject*> BoundObjects;
    for (UObject* Object : Component->OnChaosPhysicsCollision.GetAllObjects()) BoundObjects.Add(Object);
    for (UObject* Object : BoundObjects)
        for (TFieldIterator<UFunction> It(Object->GetClass()); It; ++It)
        {
            const FName Name = It->GetFName();
            if (!Component->OnChaosPhysicsCollision.Contains(Object, Name)) continue;
            const bool bSuppress = ActiveMode == EIsolationMode::CollisionOff && Object == Owner;
            auto Description = MakeShared<FJsonObject>();
            Description->SetStringField(TEXT("event"), TEXT("collision"));
            Description->SetStringField(TEXT("target"), Object->GetPathName());
            Description->SetStringField(TEXT("function"), Name.ToString());
            Description->SetBoolField(TEXT("suppressed"), bSuppress);
            Registration.BindingDescriptions.Add(MakeShared<FJsonValueObject>(Description));
            if (bSuppress)
            {
                FScriptDelegate Delegate;
                Delegate.BindUFunction(Object, Name);
                Registration.RemovedCollisionDelegates.Add(Delegate);
            }
        }
    for (const FScriptDelegate& Delegate : Registration.RemovedCollisionDelegates)
        Component->OnChaosPhysicsCollision.Remove(Delegate);
    SuppressedBindings += Registration.RemovedCollisionDelegates.Num();
    for (FName Name : OwnerBreakBindings(Component))
    {
        auto Description = MakeShared<FJsonObject>();
        Description->SetStringField(TEXT("event"), TEXT("break"));
        Description->SetStringField(TEXT("target"), Owner->GetPathName());
        Description->SetStringField(TEXT("function"), Name.ToString());
        Description->SetBoolField(TEXT("relayed"), ActiveMode == EIsolationMode::ProfileObserve || ActiveMode == EIsolationMode::ProfileBatch);
        Registration.BindingDescriptions.Add(MakeShared<FJsonValueObject>(Description));
    }
    if (ActiveMode == EIsolationMode::ProfileObserve || ActiveMode == EIsolationMode::ProfileBatch)
    {
        auto* Bridge = NewObject<UDestructionIsolationBridge>(Owner, NAME_None, RF_Transient);
        Owner->AddInstanceComponent(Bridge);
        Bridge->RegisterComponent();
        if (!Bridge->Initialize(Component, ActiveMode == EIsolationMode::ProfileBatch))
        {
            Owner->RemoveInstanceComponent(Bridge);
            Bridge->DestroyComponent();
            ++SetupFailures;
            UE_LOG(LogTemp, Error, TEXT("DP02 break bridge rejected class/signature/bindings: %s"), *Component->GetPathName());
            FPlatformMisc::RequestExit(false);
            return;
        }
        Registration.Bridge = Bridge;
    }
}

void DestructionIsolation::Flush()
{
    check(IsInGameThread());
    if (PendingEvents > 0) ++FlushesWithWork;
    for (auto& Entry : Props)
        if (UDestructionIsolationBridge* Bridge = Entry.Value.Bridge.Get()) Bridge->Flush();
}

void DestructionIsolation::Reset()
{
    check(IsInGameThread());
    Flush();
    RestoreProps();
    ClearCounters();
}

void DestructionIsolation::Stop()
{
    check(IsInGameThread());
    Flush();
    RestoreProps();
    ActiveWorld.Reset();
    ActiveMode = EIsolationMode::Reference;
}

TSharedRef<FJsonObject> DestructionIsolation::Snapshot()
{
    check(IsInGameThread());
    auto Result = MakeShared<FJsonObject>();
    Result->SetStringField(TEXT("mode"), ModeName);
    Result->SetStringField(TEXT("diagnostic_implementation"), TEXT("vendor_break_event_bridge_v1"));
    Result->SetBoolField(TEXT("active"), ActiveWorld.IsValid());
    Result->SetBoolField(TEXT("diagnostic_only"), ActiveMode != EIsolationMode::Reference);
    Result->SetBoolField(TEXT("setup_failed"), SetupFailures > 0);
    Result->SetNumberField(TEXT("configured_props"), ConfiguredProps);
    Result->SetNumberField(TEXT("setup_failures"), SetupFailures);
    Result->SetNumberField(TEXT("suppressed_vendor_collision_bindings"), SuppressedBindings);
    Result->SetNumberField(TEXT("break_events_received"), double(ReceivedEvents));
    Result->SetNumberField(TEXT("break_events_forwarded"), double(ForwardedEvents));
    Result->SetNumberField(TEXT("break_events_queued"), double(QueuedEvents));
    Result->SetNumberField(TEXT("pending_break_events"), double(PendingEvents));
    Result->SetNumberField(TEXT("peak_pending_break_events"), double(PeakPendingEvents));
    Result->SetNumberField(TEXT("profile_batch_calls"), double(BatchCalls));
    Result->SetNumberField(TEXT("profile_batch_bone_ids"), double(BatchBoneIds));
    Result->SetNumberField(TEXT("flushes_with_work"), double(FlushesWithWork));
    Result->SetStringField(TEXT("counter_scope"), TEXT("bridge events and explicit preapply calls; NOT measured original native profile-call counts"));
    Result->SetStringField(TEXT("batch_limit"), TEXT("per-actor event order retained; vendor break callbacks delayed until PostUpdateWork; cross-actor and other-subscriber ordering/presentation timing may change; diagnostic only"));
    Result->SetStringField(TEXT("collision_off_scope"), TEXT("vendor collision callback removed, including sound, index-0 profile writes and scheduled sleep; contacts remain enabled; outcome equivalence not assumed"));
    TArray<TSharedPtr<FJsonValue>> Bindings;
    for (const auto& Entry : Props)
    {
        auto Description = MakeShared<FJsonObject>();
        Description->SetStringField(TEXT("component"), Entry.Key.IsValid() ? Entry.Key->GetPathName() : TEXT("retired"));
        Description->SetBoolField(TEXT("break_bridge_installed"), Entry.Value.Bridge.IsValid());
        Description->SetArrayField(TEXT("bindings"), Entry.Value.BindingDescriptions);
        Bindings.Add(MakeShared<FJsonValueObject>(Description));
    }
    Result->SetArrayField(TEXT("prop_bindings"), Bindings);
    return Result;
}
