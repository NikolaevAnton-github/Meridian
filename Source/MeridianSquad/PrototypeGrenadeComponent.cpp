#include "PrototypeGrenadeComponent.h"
#include "DestructionPerfFixture.h"
#include "OpeningLobbyCharacter.h"
#include "CombatRifleComponent.h"
#include "NGDPropComponent.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/LatentActionManager.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "EnhancedInputComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/ProjectileMovementComponent.h"
#include "InputAction.h"
#include "Serialization/JsonSerializer.h"
#include "TimerManager.h"
#include "UObject/StructOnScope.h"
#include "UObject/UnrealType.h"

namespace
{
UObject* ObjectValue(const UObject* Object, FName Name)
{
    const auto* P = Object ? FindFProperty<FObjectPropertyBase>(Object->GetClass(), Name) : nullptr;
    return P ? P->GetObjectPropertyValue_InContainer(Object) : nullptr;
}
bool Flag(const UObject* Object, FName Name)
{
    const auto* P = Object ? FindFProperty<FBoolProperty>(Object->GetClass(), Name) : nullptr;
    return P && P->GetPropertyValue_InContainer(Object);
}
void SetFlag(UObject* Object, FName Name, bool Value)
{
    if (auto* P = Object ? FindFProperty<FBoolProperty>(Object->GetClass(), Name) : nullptr)
        P->SetPropertyValue_InContainer(Object, Value);
}
void Retire(AActor* Actor)
{
    if (!IsValid(Actor)) return;
    Actor->GetWorld()->GetLatentActionManager().RemoveActionsForObject(Actor);
    Actor->GetWorld()->GetTimerManager().ClearAllTimersForObject(Actor);
    Actor->Destroy();
}
}

UPrototypeGrenadeComponent::UPrototypeGrenadeComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.TickGroup = TG_PostUpdateWork;
}

void UPrototypeGrenadeComponent::Initialize()
{
    if (Character) return;
    Character = Cast<AOpeningLobbyCharacter>(GetOwner());
    if (!Character) return;
    ThrowMontage = Cast<UAnimMontage>(ObjectValue(ObjectValue(Character, TEXT("WeaponConfig")), TEXT("FP_GrenadeThrowQuick")));
    GrenadeClass = LoadClass<AActor>(nullptr, TEXT("/Game/NextGenDestruction/Blueprints/Actors/BP_Grenade.BP_Grenade_C"));
    HeldSphere = NewObject<UStaticMeshComponent>(Character, TEXT("PrototypeHeldGrenade"));
    HeldSphere->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere")));
    HeldSphere->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    HeldSphere->SetCastShadow(false);
    HeldSphere->SetFirstPersonPrimitiveType(EFirstPersonPrimitiveType::FirstPerson);
    HeldSphere->SetupAttachment(Character->GetMesh(), TEXT("hand_l"));
    HeldSphere->SetRelativeLocation(FVector(7.f, 0.f, 0.f));
    HeldSphere->SetRelativeScale3D(FVector(.15f));
    HeldSphere->SetVisibility(false);
    HeldSphere->RegisterComponent();
    AddTickPrerequisiteComponent(Character->GetMesh());
    SpawnHandle = GetWorld()->AddOnActorSpawnedHandler(FOnActorSpawned::FDelegate::CreateUObject(this, &UPrototypeGrenadeComponent::OnActorSpawned));
}

void UPrototypeGrenadeComponent::BindInput(UEnhancedInputComponent* Input)
{
    auto* Action = LoadObject<UInputAction>(nullptr, TEXT("/Game/InfimaGames/TacticalFPSAnimations/Common/Core/Inputs/IA_TFA_GrenadeThrow.IA_TFA_GrenadeThrow"));
    if (!Action) return;
    TArray<uint32> Handles;
    for (const auto& Binding : Input->GetActionEventBindings())
        if (Binding->GetAction() == Action) Handles.Add(Binding->GetHandle());
    for (uint32 Handle : Handles) Input->RemoveBindingByHandle(Handle);
    Input->BindAction(Action, ETriggerEvent::Started, this, &UPrototypeGrenadeComponent::StartThrow);
}

void UPrototypeGrenadeComponent::StartThrow()
{
    Initialize();
    if (!Character || !ThrowMontage || !GrenadeClass || ThrowInstance != INDEX_NONE ||
        Character->CombatRifle->bReloading || Flag(Character, TEXT("bIsBusy"))) return;
    Grenades.RemoveAll([](const auto& Grenade) { return !Grenade.IsValid(); });
    if (Grenades.Num() >= 8) return;
    auto* Anim = Character->GetMesh()->GetAnimInstance();
    UFunction* Function = Character->FindFunction(TEXT("PlaySyncedMontage"));
    if (!Anim || !Function) return;
    SetFlag(Character, TEXT("bIsRunning"), false);
    SetFlag(Character, TEXT("bIsSprinting"), false);
    FStructOnScope Params(Function);
    if (auto* P = FindFProperty<FObjectPropertyBase>(Function, TEXT("FP_Character_Montage")))
        P->SetObjectPropertyValue_InContainer(Params.GetStructMemory(), ThrowMontage);
    Character->ProcessEvent(Function, Params.GetStructMemory());
    if (auto* Instance = Anim->GetActiveInstanceForMontage(ThrowMontage))
    {
        ThrowInstance = Instance->GetInstanceID();
        bReleased = false;
        HeldSphere->SetVisibility(true);
        UE_LOG(LogTemp, Display, TEXT("Grenade throw started instance=%d release=%.3f"), ThrowInstance, ReleaseTime);
    }
}

void UPrototypeGrenadeComponent::TickComponent(float Delta, ELevelTick TickType, FActorComponentTickFunction* TickFunction)
{
    Super::TickComponent(Delta, TickType, TickFunction);
    if (ThrowInstance == INDEX_NONE || !Character) return;
    auto* Anim = Character->GetMesh()->GetAnimInstance();
    auto* Instance = Anim ? Anim->GetActiveInstanceForMontage(ThrowMontage) : nullptr;
    if (!Instance || Instance->GetInstanceID() != ThrowInstance || Instance->IsStopped())
    {
        ThrowInstance = INDEX_NONE;
        HeldSphere->SetVisibility(false);
        return;
    }
    // Read evaluated montage progress, never a wall-clock delay; an interrupted
    // gesture cannot emit a late grenade and slowdown follows the animation.
    if (!bReleased && Instance->GetPosition() >= ReleaseTime) Release();
}

void UPrototypeGrenadeComponent::Release()
{
    bReleased = true;
    HeldSphere->SetVisibility(false);
    FVector View;
    FRotator Rotation;
    Character->GetActorEyesViewPoint(View, Rotation);
    if (auto* PC = Cast<APlayerController>(Character->GetController())) PC->GetPlayerViewPoint(View, Rotation);
    const FVector Forward = Rotation.Vector();
    const FVector Desired = View + Forward * 65.f - FRotationMatrix(Rotation).GetUnitAxis(EAxis::Y) * 12.f - FVector(0, 0, 8.f);
    FCollisionQueryParams Query(SCENE_QUERY_STAT(GrenadeRelease), false, Character);
    TArray<AActor*> Attached;
    Character->GetAttachedActors(Attached, true, true);
    Query.AddIgnoredActors(Attached);
    FCollisionObjectQueryParams Objects(FCollisionObjectQueryParams::AllObjects);
    FHitResult Hit;
    const bool Blocked = GetWorld()->SweepSingleByObjectType(Hit, View, Desired, FQuat::Identity, Objects, FCollisionShape::MakeSphere(8.f), Query);
    if (Blocked && Hit.bStartPenetrating) return;
    const FVector Position = Blocked ? Hit.Location + Hit.Normal * 1.f : Desired;
    FActorSpawnParameters Spawn;
    Spawn.Owner = Character;
    Spawn.Instigator = Character;
    Spawn.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    AActor* Grenade = GetWorld()->SpawnActor<AActor>(GrenadeClass, Position, FRotator::ZeroRotator, Spawn);
    if (!Grenade) return;
    Grenade->Tags.Add(TEXT("PrototypeGrenade"));
    Grenade->SetLifeSpan(8.f);
    auto* Sphere = Cast<UStaticMeshComponent>(ObjectValue(Grenade, TEXT("Sphere")));
    if (!Sphere) Sphere = Grenade->FindComponentByClass<UStaticMeshComponent>();
    if (!Sphere) { Retire(Grenade); return; }
    Sphere->SetCollisionResponseToChannel(ECC_Pawn, ECR_Ignore);
    Sphere->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
    Sphere->SetCollisionResponseToChannel(ECC_Visibility, ECR_Ignore);
    Sphere->SetUseCCD(true);
    // Keep the vendor's swept bouncing projectile as the single movement owner.
    Sphere->SetSimulatePhysics(false);
    auto* Movement = Grenade->FindComponentByClass<UProjectileMovementComponent>();
    if (!Movement) { Retire(Grenade); return; }
    Movement->Velocity = Forward * ThrowSpeed + FVector(0, 0, 240.f) + Character->GetVelocity();
    Movement->bForceSubStepping = true;
    Movement->UpdateComponentVelocity();
    Grenades.Add(Grenade);
    ++Throws;
    UE_LOG(LogTemp, Display, TEXT("Grenade released count=%d position=%s"), Throws, *Position.ToString());
}

void UPrototypeGrenadeComponent::OnActorSpawned(AActor* Actor)
{
    if (!Actor || Actor->GetClass()->GetPathName() != TEXT("/Game/NextGenDestruction/Blueprints/Actors/BP_DestructionField.BP_DestructionField_C")) return;
    for (const auto& Grenade : Grenades)
        // Latent Delay may consume the creation frame's step. Under throttled
        // PIE its completion can precede actor age 1.9s by part of one frame.
        if (Grenade.IsValid() && Grenade->GetGameTimeSinceCreation() + GetWorld()->GetDeltaSeconds() >= 1.9f &&
            FVector::DistSquared(Grenade->GetActorLocation(), Actor->GetActorLocation()) < 4.f)
        {
            Actor->SetActorScale3D(FVector(FMath::Clamp(BlastRadius, 50.f, 1000.f) / 100.f));
            Fields.RemoveAll([](const auto& Field) { return !Field.IsValid(); });
            Fields.Add(Actor);
            if (FieldNames.Num() == 64) FieldNames.RemoveAt(0);
            FieldNames.Add(Actor->GetFName());
            if (auto* Movement = Grenade->FindComponentByClass<UProjectileMovementComponent>())
            {
                Movement->StopMovementImmediately();
                Movement->Deactivate();
                Movement->SetComponentTickEnabled(false);
            }
            if (auto* Sphere = Grenade->FindComponentByClass<UStaticMeshComponent>())
            {
                Sphere->SetSimulatePhysics(false);
                Sphere->SetCollisionEnabled(ECollisionEnabled::NoCollision);
            }
            Grenade->SetLifeSpan(4.f);
            ++Explosions;
            if (Grenade->ActorHasTag(TEXT("DestructionPerf01")))
                for (TActorIterator<ADestructionPerfFixture> It(GetWorld()); It; ++It) It->MarkDetonation();
            UE_LOG(LogTemp, Display, TEXT("Grenade exploded count=%d radius=%.1f position=%s"), Explosions, BlastRadius, *Actor->GetActorLocation().ToString());
            break;
        }
}

void UPrototypeGrenadeComponent::Reset()
{
    if (Character && ThrowInstance != INDEX_NONE)
        if (auto* Anim = Character->GetMesh()->GetAnimInstance())
        {
            auto* Instance = Anim->GetActiveInstanceForMontage(ThrowMontage);
            const bool Owns = Instance && Instance->GetInstanceID() == ThrowInstance;
            ThrowInstance = INDEX_NONE;
            if (Owns)
            {
                Anim->Montage_Stop(.1f, ThrowMontage);
                SetFlag(Character, TEXT("bIsBusy"), false);
            }
        }
    ThrowInstance = INDEX_NONE;
    if (HeldSphere) HeldSphere->SetVisibility(false);
    for (const auto& Grenade : Grenades) Retire(Grenade.Get());
    for (const auto& Field : Fields) Retire(Field.Get());
    UNGDPropComponent::CancelPendingFields(GetWorld(), FieldNames);
    Grenades.Reset(); Fields.Reset(); FieldNames.Reset();
}

void UPrototypeGrenadeComponent::ResetWorld(UWorld* World)
{
    if (World) for (TActorIterator<ADestructionPerfFixture> It(World); It; ++It) It->ResetFixture();
    if (World) for (TActorIterator<AOpeningLobbyCharacter> It(World); It; ++It)
        if (auto* Component = It->FindComponentByClass<UPrototypeGrenadeComponent>()) Component->Reset();
}

bool UPrototypeGrenadeComponent::SpawnFixed(FVector Position)
{
    Initialize();
    if (!Character || !GrenadeClass) return false;
    FActorSpawnParameters Spawn;
    Spawn.Owner = Character;
    Spawn.Instigator = Character;
    Spawn.ObjectFlags |= RF_Transient;
    Spawn.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    AActor* Grenade = GetWorld()->SpawnActor<AActor>(GrenadeClass, Position, FRotator::ZeroRotator, Spawn);
    if (!Grenade) return false;
    Grenade->Tags.Add(TEXT("PrototypeGrenade"));
    Grenade->Tags.Add(TEXT("DestructionPerf01"));
    Grenade->SetLifeSpan(8.f);
    if (auto* Movement = Grenade->FindComponentByClass<UProjectileMovementComponent>())
    {
        Movement->StopMovementImmediately();
        Movement->Deactivate();
        Movement->SetComponentTickEnabled(false);
    }
    for (auto* Part : TInlineComponentArray<UPrimitiveComponent*>(Grenade))
    {
        Part->SetSimulatePhysics(false);
        Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    }
    Grenades.Add(Grenade);
    return true;
}

void UPrototypeGrenadeComponent::EndPlay(const EEndPlayReason::Type Reason)
{
    if (GetWorld()) GetWorld()->RemoveOnActorSpawnedHandler(SpawnHandle);
    Reset();
    Super::EndPlay(Reason);
}

FString UPrototypeGrenadeComponent::GetState() const
{
    auto State = MakeShared<FJsonObject>();
    State->SetNumberField(TEXT("throws"), Throws);
    State->SetNumberField(TEXT("explosions"), Explosions);
    State->SetNumberField(TEXT("throw_instance"), ThrowInstance);
    State->SetBoolField(TEXT("released"), bReleased);
    State->SetNumberField(TEXT("blast_radius"), BlastRadius);
    int32 Live = 0;
    for (const auto& Grenade : Grenades) if (Grenade.IsValid()) ++Live;
    State->SetNumberField(TEXT("live_grenades"), Live);
    FString Result;
    FJsonSerializer::Serialize(State, TJsonWriterFactory<>::Create(&Result));
    return Result;
}
