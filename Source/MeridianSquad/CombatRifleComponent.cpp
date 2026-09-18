#include "CombatRifleComponent.h"
#include "CombatProjectileWorld.h"
#include "OpeningLobbyCharacter.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Components/SkeletalMeshComponent.h"
#include "EnhancedInputComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "InputAction.h"
#include "Serialization/JsonSerializer.h"
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
void SetInt(UObject* Object, FName Name, int32 Value)
{
    if (auto* P = Object ? FindFProperty<FIntProperty>(Object->GetClass(), Name) : nullptr)
        P->SetPropertyValue_InContainer(Object, Value);
}
void Call(UObject* Object, FName Name)
{
    if (UFunction* Function = Object ? Object->FindFunction(Name) : nullptr) Object->ProcessEvent(Function, nullptr);
}
}

void UCombatReloadCommitNotify::BranchingPointNotify(FBranchingPointNotifyPayload& Payload)
{
    if (Payload.SkelMeshComponent)
        if (auto* Rifle = Payload.SkelMeshComponent->GetOwner()->FindComponentByClass<UCombatRifleComponent>())
            Rifle->CommitReload(Payload.SkelMeshComponent, Payload.SequenceAsset, Payload.MontageInstanceID);
}
UCombatRifleComponent::UCombatRifleComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.TickGroup = TG_PrePhysics;
}
UAnimMontage* UCombatRifleComponent::ConfigMontage(FName Name) const
{
    return Cast<UAnimMontage>(ObjectValue(ObjectValue(Character, TEXT("WeaponConfig")), Name));
}
void UCombatRifleComponent::InitializeRifle()
{
    if (bReady) return;
    Character = Cast<AOpeningLobbyCharacter>(GetOwner());
    if (!Character || !ObjectValue(Character, TEXT("CurrentWeaponActor"))) return;
    MagazineCapacity = FMath::Clamp(MagazineCapacity, 1, 30);
    Magazine = MagazineCapacity;
    Reserve = FMath::Clamp(InitialReserve, 0, 9999);
    for (const FName Key : {FName(TEXT("Reload")), FName(TEXT("ReloadEmpty")), FName(TEXT("ReloadQuick"))})
    {
        auto* Source = ConfigMontage(FName(TEXT("FP_") + Key.ToString()));
        if (!Source) continue;
        auto* Copy = DuplicateObject<UAnimMontage>(Source, this, FName(TEXT("Combat_") + Key.ToString()));
        Copy->SetFlags(RF_Transient);
        Copy->ClearFlags(RF_Public | RF_Standalone);
        int32 Replaced = 0;
        for (auto& Event : Copy->Notifies)
            if (Event.NotifyName.ToString().Contains(TEXT("UnlockActions")))
            {
                Event.Notify = NewObject<UCombatReloadCommitNotify>(Copy);
                Event.NotifyName = TEXT("CombatReloadTransfer");
                Event.MontageTickType = EMontageNotifyTickType::BranchingPoint;
                Event.NotifyTriggerChance = 1.f;
                CommitTimes.Add(Key, Event.GetTime());
                ++Replaced;
            }
        if (ensureMsgf(Replaced == 1, TEXT("Reload must contain exactly one hands unlock/transfer event")))
        {
            Copy->RefreshCacheData();
            ReloadMontages.Add(Key, Copy);
        }
    }
    AddTickPrerequisiteActor(Character);
    Character->GetMesh()->AddTickPrerequisiteComponent(this);
    bReady = true;
    SyncPresentation();
}
void UCombatRifleComponent::BindInput(UEnhancedInputComponent* Input)
{
    const FString Base = TEXT("/Game/InfimaGames/TacticalFPSAnimations/Common/Core/Inputs/IA_TFA_");
    auto LoadAction = [&](const TCHAR* Name)
    {
        return LoadObject<UInputAction>(nullptr, *(Base + Name + TEXT(".IA_TFA_") + Name));
    };
    const auto* Fire = LoadAction(TEXT("Fire"));
    const auto* Mode = LoadAction(TEXT("FireModeSwitch"));
    const auto* Reload = LoadAction(TEXT("Reload_MagCheck"));
    const auto* Quick = LoadAction(TEXT("Reload_Quick"));
    const auto* Empty = LoadAction(TEXT("Reload_Empty"));
    TArray<uint32> Handles;
    for (const auto& Binding : Input->GetActionEventBindings())
        if (Binding->GetAction() == Fire || Binding->GetAction() == Mode || Binding->GetAction() == Reload ||
            Binding->GetAction() == Quick || Binding->GetAction() == Empty) Handles.Add(Binding->GetHandle());
    for (uint32 Handle : Handles) Input->RemoveBindingByHandle(Handle);
    Input->BindAction(Fire, ETriggerEvent::Started, this, &UCombatRifleComponent::FirePressed);
    Input->BindAction(Fire, ETriggerEvent::Completed, this, &UCombatRifleComponent::FireReleased);
    Input->BindAction(Fire, ETriggerEvent::Canceled, this, &UCombatRifleComponent::FireReleased);
    Input->BindAction(Mode, ETriggerEvent::Started, this, &UCombatRifleComponent::ChangeFireMode);
    Input->BindAction(Quick, ETriggerEvent::Started, this, &UCombatRifleComponent::QuickReload);
    Input->BindAction(Empty, ETriggerEvent::Started, this, &UCombatRifleComponent::EmergencyReload);
    Input->BindAction(Reload, ETriggerEvent::Triggered, this, &UCombatRifleComponent::InspectMagazine);
    Input->BindAction(Reload, ETriggerEvent::Canceled, this, &UCombatRifleComponent::ReloadTap);
    Input->BindAction(Reload, ETriggerEvent::Completed, this, &UCombatRifleComponent::ReloadReleased);
    static_cast<UInputComponent*>(Input)->BindKey(EKeys::F6, IE_Pressed, this, &UCombatRifleComponent::ResetTargets);
}
bool UCombatRifleComponent::CanAct() const
{
    return bReady && !bReloading && !Flag(Character, TEXT("bIsBusy")) &&
        !Flag(Character, TEXT("bIsRunning")) && !Flag(Character, TEXT("bIsSprinting"));
}
bool UCombatRifleComponent::PlayPair(UAnimMontage* Hands, UAnimMontage* Weapon)
{
    if (!Hands || !Character || !Character->GetMesh()->GetAnimInstance()) return false;
    UFunction* Function = Character->FindFunction(TEXT("PlaySyncedMontage"));
    if (!Function) return false;
    FStructOnScope Params(Function);
    for (const auto& Pair : {TPair<FName, UAnimMontage*>(TEXT("FP_Character_Montage"), Hands),
                            TPair<FName, UAnimMontage*>(TEXT("FP_Weapon_Montage"), Weapon)})
        if (auto* P = FindFProperty<FObjectPropertyBase>(Function, Pair.Key))
            P->SetObjectPropertyValue_InContainer(Params.GetStructMemory(), Pair.Value);
    Character->ProcessEvent(Function, Params.GetStructMemory());
    return Character->GetMesh()->GetAnimInstance()->Montage_IsActive(Hands);
}
void UCombatRifleComponent::FirePressed()
{
    if (bFireHeld) return;
    bFireHeld = true;
    bDryForPress = false;
    TryShot();
}
void UCombatRifleComponent::FireReleased()
{
    bFireHeld = false;
    bDryForPress = false;
    SetInt(Character, TEXT("RecoilRampCount"), 0);
}
bool UCombatRifleComponent::TryShot()
{
    const double Now = GetWorld()->GetTimeSeconds();
    if (!CanAct() || Now + 1.e-6 < NextShotTime)
    {
        ++BlockedShotCount;
        return false;
    }
    if (Magazine <= 0)
    {
        StatusText = Reserve > 0 ? TEXT("EMPTY  |  R: RELOAD") : TEXT("EMPTY  |  NO RESERVE");
        if (!bDryForPress && Now >= NextDryTime)
        {
            bDryForPress = true;
            NextDryTime = Now + .3;
            if (PlayPair(ConfigMontage(TEXT("FP_FireEmpty")), nullptr)) ++DryFireCount;
        }
        return false;
    }
    if (!Simulation.IsValid()) Simulation = ACombatProjectileWorld::Find(GetWorld());
    if (!Simulation.IsValid()) { StatusText = TEXT("PROJECTILE SIMULATION UNAVAILABLE"); return false; }
    FVector View;
    FRotator Rotation;
    Character->GetActorEyesViewPoint(View, Rotation);
    if (const auto* PC = Cast<APlayerController>(Character->GetController())) PC->GetPlayerViewPoint(View, Rotation);
    const FVector Forward = Rotation.Vector();
    const FVector Muzzle = View + Rotation.RotateVector(FVector(55, 12, -8));
    FCollisionQueryParams Query(SCENE_QUERY_STAT(CombatAim), true);
    Simulation->BuildQuery(Query, Character);
    FHitResult AimHit, CoverHit;
    const bool bAimHit = GetWorld()->LineTraceSingleByChannel(AimHit, View, View + Forward * 30000.f, ECC_Visibility, Query);
    const FVector AimPoint = bAimHit ? AimHit.ImpactPoint : View + Forward * 30000.f;
    const bool bCover = GetWorld()->SweepSingleByChannel(CoverHit, View, Muzzle, FQuat::Identity, ECC_Visibility,
        FCollisionShape::MakeSphere(.5f), Query);
    // Never spawn a bullet beyond nearby cover. These queries aim the launch;
    // they do not apply damage. Collision only occurs in the finite-flight step.
    const bool bVeryNear = bAimHit && FVector::DotProduct(AimPoint - View, Forward) < 55.f;
    const FVector Start = bCover || bVeryNear ? View : Muzzle;
    FVector Direction = bCover ? (Muzzle - View).GetSafeNormal() : (AimPoint - Start).GetSafeNormal();
    if (Direction.IsNearlyZero()) Direction = Forward;
    const int64 Id = Simulation->Launch(Character, Start, Direction * FMath::Clamp(BulletSpeed, 1.f, 200000.f), Damage);
    if (!Id) { StatusText = TEXT("PROJECTILE CAPACITY  |  WAIT"); return false; }
    // Reservation succeeded: this is the only ammunition-decrementing path.
    --Magazine;
    ++ShotCount;
    LastShotId = Id;
    LastShotTime = Now;
    const double Interval = FMath::Max(.05f, ShotInterval);
    // Retain the 85 ms source timer phase at normal frame rates, but never
    // replay a backlog of shots after a hitch or an action lock.
    NextShotTime = Now - NextShotTime <= Interval ? NextShotTime + Interval : Now + Interval;
    SyncPresentation();
    PlayPair(ConfigMontage(bAutomatic ? TEXT("FP_FireAuto") : TEXT("FP_FireSemi")), ConfigMontage(TEXT("FP_WEP_Fire")));
    Call(Character, TEXT("AddRecoil"));
    Call(Character, TEXT("SpawnMuzzleFlash"));
    StatusText.Empty();
    return true;
}
void UCombatRifleComponent::ChangeFireMode()
{
    if (!CanAct() || bFireHeld) return;
    bAutomatic = !bAutomatic;
    SyncPresentation();
    PlayPair(ConfigMontage(TEXT("FP_FireMode")), nullptr);
}
bool UCombatRifleComponent::RequestReload(bool Quick)
{
    if (!CanAct()) return false;
    if (Magazine >= MagazineCapacity || Reserve <= 0)
    {
        StatusText = Reserve <= 0 ? TEXT("NO RESERVE") : TEXT("MAGAZINE FULL");
        return false;
    }
    // Empty state always selects bolt-handling animation, including Q and E.
    const FName Key = Magazine == 0 ? TEXT("ReloadEmpty") : Quick ? TEXT("ReloadQuick") : TEXT("Reload");
    const auto* Found = ReloadMontages.Find(Key);
    if (!Found || !PlayPair(*Found, ConfigMontage(FName(TEXT("FP_WEP_") + Key.ToString())))) return false;
    ActiveReload = *Found;
    auto* Instance = Character->GetMesh()->GetAnimInstance()->GetActiveInstanceForMontage(ActiveReload);
    if (!Instance) return false;
    ReloadInstanceId = Instance->GetInstanceID();
    bReloading = true;
    bTransferDone = false;
    ++ReloadCount;
    StatusText = TEXT("RELOADING");
    return true;
}
void UCombatRifleComponent::CommitReload(USkeletalMeshComponent* Mesh, UAnimSequenceBase* Animation, int32 InstanceId)
{
    if (!bReloading || bTransferDone || !Character || Mesh != Character->GetMesh() ||
        Animation != ActiveReload || InstanceId != ReloadInstanceId) return;
    bTransferDone = true;
    const int32 Transfer = FMath::Min(FMath::Max(0, MagazineCapacity - Magazine), FMath::Max(0, Reserve));
    Magazine += Transfer;
    Reserve -= Transfer;
    TransferredRounds += Transfer;
    ++TransferCount;
    bReloading = false;
    SetFlag(Character, TEXT("bIsBusy"), false);
    StatusText.Empty();
    SyncPresentation();
}
void UCombatRifleComponent::CancelReload()
{
    if (!bReloading || !Character) return;
    bReloading = false;
    ++CanceledReloadCount;
    ReloadInstanceId = INDEX_NONE;
    auto* Anim = Character->GetMesh()->GetAnimInstance();
    const bool OwnsLock = Anim && (Anim->GetCurrentActiveMontage() == ActiveReload || !Anim->GetCurrentActiveMontage());
    if (Anim) Anim->Montage_Stop(.12f, ActiveReload);
    if (OwnsLock)
    {
        SetFlag(Character, TEXT("bIsBusy"), false);
        Call(Character, TEXT("StopWeaponAnimation"));
    }
    RestoreMagazines();
    SyncPresentation();
    StatusText = TEXT("RELOAD CANCELED");
}
void UCombatRifleComponent::QuickReload() { RequestReload(true); }
void UCombatRifleComponent::EmergencyReload() { RequestReload(false); }
void UCombatRifleComponent::ReloadTap()
{
    if (!bInspectForPress) RequestReload(false);
    bInspectForPress = false;
}
void UCombatRifleComponent::ReloadReleased() { bInspectForPress = false; }
void UCombatRifleComponent::InspectMagazine()
{
    if (bInspectForPress) return;
    bInspectForPress = true;
    if (CanAct()) PlayPair(ConfigMontage(TEXT("FP_MagCheck")), ConfigMontage(TEXT("FP_WEP_MagCheck")));
}
void UCombatRifleComponent::SyncPresentation()
{
    if (!Character) return;
    if (auto* Weapon = Cast<AActor>(ObjectValue(Character, TEXT("CurrentWeaponActor"))))
    {
        // Its only source Tick was the demo underflow refill. The property now
        // mirrors authoritative state for the existing magazine AnimBPs.
        Weapon->SetActorTickEnabled(false);
        SetInt(Weapon, TEXT("AmmoCount"), Magazine);
    }
    if (auto* P = FindFProperty<FByteProperty>(Character->GetClass(), TEXT("CurrentFireMode")))
        P->SetPropertyValue_InContainer(Character, bAutomatic ? 2 : 1);
}
void UCombatRifleComponent::RestoreMagazines()
{
    UObject* Weapon = ObjectValue(Character, TEXT("CurrentWeaponActor"));
    UFunction* Function = Weapon ? Weapon->FindFunction(TEXT("SetMagazineVisibility")) : nullptr;
    if (!Function) return;
    for (bool ReserveMagazine : {false, true})
    {
        FStructOnScope Params(Function);
        if (auto* P = FindFProperty<FBoolProperty>(Function, TEXT("bVisible")))
            P->SetPropertyValue_InContainer(Params.GetStructMemory(), !ReserveMagazine);
        if (auto* P = FindFProperty<FBoolProperty>(Function, TEXT("bIsReserve")))
            P->SetPropertyValue_InContainer(Params.GetStructMemory(), ReserveMagazine);
        Weapon->ProcessEvent(Function, Params.GetStructMemory());
    }
}
void UCombatRifleComponent::RetireProps()
{
    const double Now = FPlatformTime::Seconds();
    TArray<AActor*> Assembly;
    Character->GetAttachedActors(Assembly, true, true);
    Assembly.Add(Character);
    for (AActor* Actor : Assembly)
        for (UActorComponent* Component : Actor->GetComponents())
            if (Component->GetClass()->GetName() == TEXT("NiagaraComponent") && !EffectBirths.Contains(Component))
                EffectBirths.Add(Component, Now);
    // Authored flashes auto-destroy normally. These independent real-time caps
    // remain a safety net even if a future world stop freezes presentation VFX.
    for (auto It = EffectBirths.CreateIterator(); It; ++It)
        if (!It.Key().IsValid() || Now - It.Value() > 4.0)
        {
            if (It.Key().IsValid()) It.Key()->DestroyComponent();
            It.RemoveCurrent();
        }
    while (EffectBirths.Num() > 64)
    {
        TWeakObjectPtr<UActorComponent> Oldest;
        double Time = TNumericLimits<double>::Max();
        for (const auto& Entry : EffectBirths) if (Entry.Value < Time) { Oldest = Entry.Key; Time = Entry.Value; }
        if (Oldest.IsValid()) Oldest->DestroyComponent();
        EffectBirths.Remove(Oldest);
    }
    for (TActorIterator<AActor> It(GetWorld()); It; ++It)
        if (It->GetClass()->GetName().StartsWith(TEXT("BP_TFA_Physics")))
        {
            if (!PropBirths.Contains(*It)) PropBirths.Add(*It, Now);
            for (UActorComponent* Component : It->GetComponents())
                if (auto* Part = Cast<UPrimitiveComponent>(Component)) Part->SetCollisionResponseToChannel(ECC_Visibility, ECR_Ignore);
        }
    for (auto It = PropBirths.CreateIterator(); It; ++It)
        if (!It.Key().IsValid() || Now - It.Value() > 8.0)
        {
            if (It.Key().IsValid()) It.Key()->Destroy();
            It.RemoveCurrent();
        }
    while (PropBirths.Num() > 64)
    {
        TWeakObjectPtr<AActor> Oldest;
        double Time = TNumericLimits<double>::Max();
        for (const auto& Entry : PropBirths) if (Entry.Value < Time) { Oldest = Entry.Key; Time = Entry.Value; }
        if (Oldest.IsValid()) Oldest->Destroy();
        PropBirths.Remove(Oldest);
    }
}
void UCombatRifleComponent::TickComponent(float Delta, ELevelTick TickType, FActorComponentTickFunction* TickFunction)
{
    Super::TickComponent(Delta, TickType, TickFunction);
    if (!bReady) return;
    if (bReloading)
    {
        auto* Anim = Character->GetMesh()->GetAnimInstance();
        auto* Instance = Anim ? Anim->GetMontageInstanceForID(ReloadInstanceId) : nullptr;
        if (!Instance || !Instance->IsActive() || Instance->IsStopped()) CancelReload();
        else SetFlag(Character, TEXT("bIsBusy"), true);
    }
    if (bFireHeld && bAutomatic && !bDryForPress && GetWorld()->GetTimeSeconds() >= NextShotTime) TryShot();
    SyncPresentation();
    RetireProps();
}
void UCombatRifleComponent::ResetTargets()
{
    if (auto* World = ACombatProjectileWorld::Find(GetWorld())) World->ResetTargets();
}
void UCombatRifleComponent::ClearTransientFeedback()
{
    TArray<AActor*> Assembly;
    if (Character)
    {
        Character->GetAttachedActors(Assembly, true, true);
        Assembly.Add(Character);
    }
    for (AActor* Actor : Assembly)
    {
        TInlineComponentArray<UActorComponent*> Parts(Actor);
        for (UActorComponent* Part : Parts)
            if (Part->GetClass()->GetName() == TEXT("NiagaraComponent")) Part->DestroyComponent();
    }
    for (TActorIterator<AActor> It(GetWorld()); It; ++It)
        if (It->GetClass()->GetName().StartsWith(TEXT("BP_TFA_Physics"))) It->Destroy();
    PropBirths.Reset();
    EffectBirths.Reset();
}
void UCombatRifleComponent::EndPlay(const EEndPlayReason::Type Reason)
{
    bFireHeld = false;
    bReloading = false;
    PropBirths.Reset();
    EffectBirths.Reset();
    ReloadMontages.Reset();
    Super::EndPlay(Reason);
}
bool UCombatRifleComponent::ProbeAmmo(int32 Rounds, int32 Spare)
{
#if WITH_EDITOR
    if (GetWorld()->WorldType == EWorldType::PIE && bReady && !bReloading && !bFireHeld)
    {
        Magazine = FMath::Clamp(Rounds, 0, MagazineCapacity);
        Reserve = FMath::Clamp(Spare, 0, 9999);
        SyncPresentation();
        return true;
    }
#endif
    return false;
}
void UCombatRifleComponent::ProbeDuplicateNotify()
{
#if WITH_EDITOR
    if (GetWorld()->WorldType == EWorldType::PIE && bTransferDone)
        CommitReload(Character->GetMesh(), ActiveReload, ReloadInstanceId);
#endif
}
FString UCombatRifleComponent::GetRifleState() const
{
    auto Root = MakeShared<FJsonObject>();
    Root->SetNumberField(TEXT("magazine"), Magazine);
    Root->SetNumberField(TEXT("reserve"), Reserve);
    Root->SetBoolField(TEXT("automatic"), bAutomatic);
    Root->SetBoolField(TEXT("reloading"), bReloading);
    Root->SetBoolField(TEXT("transfer_done"), bTransferDone);
    Root->SetBoolField(TEXT("fire_held"), bFireHeld);
    Root->SetNumberField(TEXT("shots"), ShotCount);
    Root->SetNumberField(TEXT("dry_fire"), DryFireCount);
    Root->SetNumberField(TEXT("reloads"), ReloadCount);
    Root->SetNumberField(TEXT("transfers"), TransferCount);
    Root->SetNumberField(TEXT("transferred_rounds"), TransferredRounds);
    Root->SetNumberField(TEXT("canceled_reloads"), CanceledReloadCount);
    Root->SetNumberField(TEXT("blocked_shots"), BlockedShotCount);
    Root->SetNumberField(TEXT("last_shot_id"), LastShotId);
    Root->SetNumberField(TEXT("last_shot_time"), LastShotTime);
    Root->SetNumberField(TEXT("props"), PropBirths.Num());
    Root->SetNumberField(TEXT("effects"), EffectBirths.Num());
    Root->SetNumberField(TEXT("reload_instance"), ReloadInstanceId);
    Root->SetStringField(TEXT("reload_montage"), ActiveReload ? ActiveReload->GetName() : TEXT(""));
    Root->SetStringField(TEXT("status"), StatusText);
    auto Times = MakeShared<FJsonObject>();
    for (const auto& Entry : CommitTimes) Times->SetNumberField(Entry.Key.ToString(), Entry.Value);
    Root->SetObjectField(TEXT("commit_times"), Times);
    FString Result;
    FJsonSerializer::Serialize(Root, TJsonWriterFactory<>::Create(&Result));
    return Result;
}
