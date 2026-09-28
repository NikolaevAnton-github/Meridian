#include "NGDPropComponent.h"
#include "DestructionFragmentWorld.h"
#include "DemoColumnCladding.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "GeometryCollection/GeometryCollectionComponent.h"
#include "Components/StaticMeshComponent.h"
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

void UNGDWorldSubsystem::Publish(const FNGDCollisionChange& Change)
{
    LatestChanges.Add(Change.ObjectId, Change);
    OnCollisionChanged.Broadcast(Change);
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
    // The supported column shell overlaps its retained core. Contact impulses
    // from a detached chip must not fracture the rest of that shell; the vendor
    // bullet field still supplies strain, and debris keeps physical collision.
    if (SourceData->GetPathName() == TEXT("/Game/ReinforcedColumn01/DA_RC01_Column.DA_RC01_Column") ||
        GetOwner()->ActorHasTag(TEXT("DemoColumnSurface05")) || GetOwner()->ActorHasTag(TEXT("DemoColumnCoarse06")))
    {
        Collection->SetEnableDamageFromCollision(false);
        // Fragments enclose the embedded reinforcement before they break. A
        // solver contact with those rods starts in penetration and traps debris.
        // Keep reinforcement query/pawn collision while letting fragments clear it.
        TArray<UStaticMeshComponent*> Meshes;
        GetOwner()->GetComponents(Meshes);
        for (auto* Mesh : Meshes)
            if (!Mesh->IsA<UInstancedStaticMeshComponent>())
                Mesh->SetCollisionResponseToChannel(ECC_Destructible, ECR_Ignore);
    }
    Collection->SetNotifyBreaks(true);
    Collection->OnChaosBreakEvent.AddUniqueDynamic(this, &UNGDPropComponent::OnBreak);
    PreviousBounds = Collection->Bounds.GetBox();
    Publish(ResetGeneration ? TEXT("reset") : TEXT("initial"), ResetBounds.IsValid ? ResetBounds : PreviousBounds);
}
void UNGDPropComponent::Publish(FName Reason, const FBox& Previous)
{
    if (!Collection || !GetWorld()) return;
    if (auto* Fragments=GetWorld()->GetSubsystem<UDestructionFragmentWorld>()) Fragments->InvalidateSupport(GetOwner());
    const FBox Current = Collection->Bounds.GetBox();
    FNGDCollisionChange Change;
    Change.ObjectId = ObjectId;
    Change.CollisionRevision = CollisionRevision;
    Change.ResetGeneration = ResetGeneration;
    Change.ChangedBounds = Previous + Current;
    Change.Reason = Reason;
    PreviousBounds = Current;
    GetWorld()->GetSubsystem<UNGDWorldSubsystem>()->Publish(Change);
}
void UNGDPropComponent::OnBreak(const FChaosBreakEvent& Event)
{
    if (bRetiring || !bReady || Event.Component != Collection) return;
    ++BreakEvents;
    ++CollisionRevision;
    Publish(TEXT("break"), PreviousBounds);
}
bool UNGDPropComponent::ReceiveBullet(int64 ShotId, const FHitResult& Hit)
{
    if (!bReady || bRetiring || ShotId <= 0 || Hit.GetActor() != GetOwner() || RecentShots.Contains(ShotId)) return true;
    UFunction* Function = ImpactFunction(GetOwner());
    FStructProperty* Parameter = HitParameter(Function);
    if (!Parameter) return true;
    // The finite sweep already selected and consumed this bullet. Never retrace or send PointDamage too.
    if (RecentShots.Num() == 64) RecentShots.RemoveAt(0);
    RecentShots.Add(ShotId);
    LastShotId = ShotId;
    ++DeliveredHits;
    FHitResult VendorHit = Hit;
    if (auto* Cladding = GetOwner()->FindComponentByClass<UDemoColumnCladding>(); Cladding && Cladding->HandleImpact(VendorHit))
    {
        ++CollisionRevision;
        Publish(TEXT("experiment_impact"), PreviousBounds);
        return true;
    }
    FStructOnScope Params(Function);
    Parameter->CopyCompleteValue(Parameter->ContainerPtrToValuePtr<void>(Params.GetStructMemory()), &VendorHit);
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
    if (Collection) Collection->OnChaosBreakEvent.RemoveDynamic(this, &UNGDPropComponent::OnBreak);
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
        const FBox PriorBounds = C->Collection ? C->Collection->Bounds.GetBox() : C->PreviousBounds;
        C->Retire();
        // Destroying the whole vendor instance retires its physics proxy, latent sound work,
        // per-particle collision overrides and delegate targets together.
        C->GetOwner()->SetActorEnableCollision(false);
        C->GetOwner()->Destroy();
        if (!UNGDTools::Spawn(World, Data, Transform, Id, Generation, Revision, PriorBounds, MaterialOverrides))
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
    if (!World || !DataAsset || Id.IsNone()) return nullptr;
    const FString DataPath = DataAsset->GetPathName();
    const bool bLobbyColumn = DataPath == TEXT("/Game/OpeningLobby/LobbyColumns01/DA_LobbyColumn01.DA_LobbyColumn01");
    if (!bLobbyColumn && !DataPath.StartsWith(TEXT("/Game/NextGenDestruction/Blueprints/DataAssets/Destructible/")) &&
        DataPath != TEXT("/Game/ReinforcedColumn01/DA_RC01_Column.DA_RC01_Column") &&
        DataPath != TEXT("/Game/Experiments/DemoTiledColumn01/DA_DemoTiledColumn01.DA_DemoTiledColumn01") &&
        DataPath != TEXT("/Game/Experiments/DemoTiledColumn01/Correction02/DA_DemoTiledColumn02.DA_DemoTiledColumn02") &&
        DataPath != TEXT("/Game/Experiments/DemoTiledColumn01/Correction03/DA_DemoTiledColumn03.DA_DemoTiledColumn03") &&
        DataPath != TEXT("/Game/Experiments/DemoTiledColumn01/Correction04/DA_DemoTiledColumn04.DA_DemoTiledColumn04") &&
        DataPath != TEXT("/Game/Experiments/DemoTiledColumn01/Correction05/DA_DemoTiledColumn05.DA_DemoTiledColumn05") &&
        DataPath != TEXT("/Game/Experiments/DemoTiledColumn01/Correction07/DA_DemoTiledColumn07.DA_DemoTiledColumn07") &&
        DataPath != TEXT("/Game/Experiments/DemoTiledColumn01/Correction08/DA_DemoTiledColumn08.DA_DemoTiledColumn08") &&
        DataPath != TEXT("/Game/Experiments/DemoTiledColumn01/Correction06/DA_DemoTiledColumn06.DA_DemoTiledColumn06")) return nullptr;
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
    const bool bVariedCladding = DataPath == TEXT("/Game/Experiments/DemoTiledColumn01/Correction04/DA_DemoTiledColumn04.DA_DemoTiledColumn04");
    const bool bSurfaceExperiment = DataPath == TEXT("/Game/Experiments/DemoTiledColumn01/Correction05/DA_DemoTiledColumn05.DA_DemoTiledColumn05");
    const bool bStackingExperiment = bLobbyColumn || DataPath == TEXT("/Game/Experiments/DemoTiledColumn01/Correction08/DA_DemoTiledColumn08.DA_DemoTiledColumn08");
    const bool bRefinedExperiment = bStackingExperiment || DataPath == TEXT("/Game/Experiments/DemoTiledColumn01/Correction07/DA_DemoTiledColumn07.DA_DemoTiledColumn07");
    const bool bCoarseExperiment = bRefinedExperiment || DataPath == TEXT("/Game/Experiments/DemoTiledColumn01/Correction06/DA_DemoTiledColumn06.DA_DemoTiledColumn06");
    if (bVariedCladding) Actor->Tags.Add(TEXT("DemoColumnCladding04"));
    if (bSurfaceExperiment) Actor->Tags.Add(TEXT("DemoColumnSurface05"));
    if (bCoarseExperiment) Actor->Tags.Add(TEXT("DemoColumnCoarse06"));
    if (bRefinedExperiment) Actor->Tags.Add(TEXT("DemoColumnRefined07"));
    if (bStackingExperiment) Actor->Tags.Add(TEXT("DemoColumnStacking08"));
    if (bLobbyColumn) Actor->Tags.Add(TEXT("LobbyColumns01"));
    Actor->FinishSpawning(Transform);
    if (bCoarseExperiment || bSurfaceExperiment || bVariedCladding || DataPath == TEXT("/Game/Experiments/DemoTiledColumn01/Correction03/DA_DemoTiledColumn03.DA_DemoTiledColumn03"))
    {
        // The concrete enlargement is baked. The independent vendor rebar mesh
        // still uses its original 5 m coordinates, including after F6 replacement.
        TArray<UStaticMeshComponent*> Meshes;
        Actor->GetComponents(Meshes);
        for (auto* Mesh : Meshes)
            if (Mesh->GetStaticMesh() && Mesh->GetStaticMesh()->GetName() == TEXT("SM_ConcretePillar_Square_5m_REBAR"))
            {
                // The derived lower segment is 840 cm, with 30 cm of reinforcement
                // embedded in the structural floor. Reapply on every F6 replacement.
                double RebarScaleZ = 3.6;
                if (bLobbyColumn)
                {
                    const FBox RebarBounds = Mesh->GetStaticMesh()->GetBoundingBox();
                    RebarScaleZ = 870. / RebarBounds.GetSize().Z;
                    Mesh->SetRelativeLocation(FVector(0, 0, -30. - RebarBounds.Min.Z * RebarScaleZ));
                }
                Mesh->SetRelativeScale3D(FVector(2.364, 2.364, RebarScaleZ));
            }
        // The vendor construction script swaps its default collection. In editor
        // worlds SetRestCollection does not always recreate the Nanite proxy.
        if (!World->IsGameWorld())
            if (auto* Concrete = Actor->FindComponentByClass<UGeometryCollectionComponent>()) Concrete->ReregisterComponent();
        auto* Cladding = NewObject<UDemoColumnCladding>(Actor, TEXT("DemoColumnCladding"), RF_Transactional);
        Actor->AddInstanceComponent(Cladding);
        Cladding->RegisterComponent();
        Cladding->Initialize();
    }
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
