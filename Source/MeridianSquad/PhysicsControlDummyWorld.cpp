#include "CombatProjectileWorld.h"
#include "GASPEnemyFixture.h"
#include "GASPALSLocomotionFixture.h"
#include "EnemyCombatComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/WorldSettings.h"
#include "Kismet/GameplayStatics.h"

void ACombatProjectileWorld::SetPhysicsDummyEnabled(bool Enabled)
{
    bEnablePhysicsDummy = Enabled;
    if (!Enabled)
    {
        ClearProjectiles();
        for (APhysicsControlDummy* Dummy : PhysicsDummies) if (IsValid(Dummy)) Dummy->Destroy();
        PhysicsDummies.Reset();
        PreviousDummies.Reset(); FrameStartDummies.Reset(); FrameEndDummies.Reset();
        SetPhysicsPreviewScale(1);
        return;
    }
    PhysicsDummies.RemoveAll([](const auto& Dummy) { return !IsValid(Dummy); });
    const int32 Count = bEnemyCombatMode ? 1 : 3;
    if (PhysicsDummies.Num() != Count)
    {
        for (APhysicsControlDummy* Dummy : PhysicsDummies) if (IsValid(Dummy)) Dummy->Destroy();
        PhysicsDummies.Reset();
        FActorSpawnParameters Params;
        Params.ObjectFlags |= RF_Transient;
        Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
        Params.bDeferConstruction = true;
        for (int32 I = 0; I < Count; ++I)
        {
            // Retain the three fixture slots and reaction profiles on the GASP foundation.
            const FTransform Placement(FRotator(0, 180, 0), FVector(-950, -320 + I * 320, 0));
            auto* Dummy = GetWorld()->SpawnActor<AGASPALSLocomotionFixture>(AGASPALSLocomotionFixture::StaticClass(), Placement, Params);
            if (!Dummy) continue;
            Dummy->ConfigureReactionProfile(I + 1);
            Dummy->Combat->SetStableSpawnIndex(static_cast<uint32>(I));
            Dummy->Combat->bEnabled = bEnemyCombatMode;
            Dummy->FinishSpawning(Placement);
            PhysicsDummies.Add(Dummy);
        }
        RecordCapsules();
    }
}
void ACombatProjectileWorld::SetEnemyCombatMode(bool bCombat)
{
    SetPhysicsDummyEnabled(false);
    bEnemyCombatMode = bCombat;
    ResetTargets();
    SetPhysicsDummyEnabled(true);
}
TMap<TWeakObjectPtr<APhysicsControlDummy>, FDummyPose> ACombatProjectileWorld::SampleDummies() const
{
    TMap<TWeakObjectPtr<APhysicsControlDummy>, FDummyPose> Result;
    for (TActorIterator<APhysicsControlDummy> It(GetWorld()); It; ++It)
        if (It->IsReady()) Result.Add(*It, It->SamplePhysicalPose());
    return Result;
}
TMap<TWeakObjectPtr<APhysicsControlDummy>, FDummyPose> ACombatProjectileWorld::DummiesAt(double Time) const
{
    auto Result = FrameEndDummies;
    const double Alpha = FrameEnd > FrameStart ? FMath::Clamp((Time - FrameStart) / (FrameEnd - FrameStart), 0.0, 1.0) : 1.0;
    for (auto& Entry : Result)
    {
        const auto* Dummy = Entry.Key.Get();
        // Chaos has already completed this rendered frame. Death changes motors, not bodies.
        // Later contacts in this same processing interval hold the actual transition pose;
        // we cannot reconstruct post-impulse subframe Chaos motion that has not been simulated.
        if (!Dummy || (Dummy->DeathFrame == FrameSerial && Time >= Dummy->DeathTime)) continue;
        const auto* Before = FrameStartDummies.Find(Entry.Key);
        if (!Before || Before->Epoch != Entry.Value.Epoch || Before->Shapes.Num() != Entry.Value.Shapes.Num()) continue;
        for (int32 I = 0; I < Entry.Value.Shapes.Num(); ++I)
        {
            auto& T = Entry.Value.Shapes[I].Transform;
            const auto& Old = Before->Shapes[I].Transform;
            // Discontinuous/reset poses are sampled at the new boundary; no teleport sweep.
            if (FVector::DistSquared(Old.GetLocation(), T.GetLocation()) > FMath::Square(250.0)) continue;
            T.SetLocation(FMath::Lerp(Old.GetLocation(), T.GetLocation(), Alpha));
            T.SetRotation(FQuat::Slerp(Old.GetRotation(), T.GetRotation(), Alpha));
        }
    }
    return Result;
}
void ACombatProjectileWorld::SetPhysicsPreviewScale(float Scale)
{
    if (!FMath::IsFinite(Scale)) return;
    RequestedPreviewScale = bEnablePhysicsDummy && Scale < 1.f ? FMath::Clamp(PreviewWorldRate, .1f, .9f) : 1.f;
}
void ACombatProjectileWorld::ApplyPreviewTime()
{
    if (RequestedPreviewScale == ActivePreviewScale) return;
    if (RequestedPreviewScale == 1.f) { RestorePreviewTime(); return; }
    if (!bOwnsPreviewTime)
    {
        PreviewPlayer = UGameplayStatics::GetPlayerCharacter(GetWorld(), 0);
        if (!PreviewPlayer.IsValid()) { RequestedPreviewScale = 1; return; }
        SavedWorldDilation = GetWorld()->GetWorldSettings()->TimeDilation;
        SavedPlayerDilation = PreviewPlayer->CustomTimeDilation;
        SavedManagerDilation = CustomTimeDilation;
        SavedProjectileScale = ProjectileTimeScale;
        bOwnsPreviewTime = true;
    }
    // The manager keeps a continuous compensated clock for finite flight/history.
    // Rifle cadence follows world time; player movement retains its faster clock.
    // Rate changes never rebase shot debt.
    UGameplayStatics::SetGlobalTimeDilation(GetWorld(), SavedWorldDilation * RequestedPreviewScale);
    PlayerActionRate = RequestedPreviewScale;
    PreviewPlayer->CustomTimeDilation = SavedPlayerDilation * FMath::Clamp(PreviewPlayerRate, .1f, 1.f) / RequestedPreviewScale;
    CustomTimeDilation = SavedManagerDilation / RequestedPreviewScale;
    ProjectileTimeScale = SavedProjectileScale * RequestedPreviewScale;
    ActivePreviewScale = RequestedPreviewScale;
    SyncPreviewPresentation();
}
void ACombatProjectileWorld::SyncPreviewPresentation()
{
    if (!bOwnsPreviewTime || !PreviewPlayer.IsValid()) return;
    TArray<AActor*> Attached;
    PreviewPlayer->GetAttachedActors(Attached, true, true);
    for (AActor* Actor : Attached)
    {
        // Separate weapon/magazine actors own their mesh ticks. They must share
        // the hands' clock; detached physical props deliberately keep world time.
        if (!SavedPresentationDilation.Contains(Actor)) SavedPresentationDilation.Add(Actor, Actor->CustomTimeDilation);
        Actor->CustomTimeDilation = SavedPresentationDilation.FindChecked(Actor) * FMath::Clamp(PreviewPlayerRate, .1f, 1.f) / ActivePreviewScale;
    }
    for (auto It = SavedPresentationDilation.CreateIterator(); It; ++It)
        if (!It.Key().IsValid() || !Attached.Contains(It.Key().Get()))
        {
            if (It.Key().IsValid()) It.Key()->CustomTimeDilation = It.Value();
            It.RemoveCurrent();
        }
}
void ACombatProjectileWorld::RestorePreviewTime()
{
    if (bOwnsPreviewTime)
    {
        UGameplayStatics::SetGlobalTimeDilation(GetWorld(), SavedWorldDilation);
        if (PreviewPlayer.IsValid()) PreviewPlayer->CustomTimeDilation = SavedPlayerDilation;
        CustomTimeDilation = SavedManagerDilation;
        ProjectileTimeScale = SavedProjectileScale;
    }
    bOwnsPreviewTime = false;
    for (const auto& Entry : SavedPresentationDilation)
        if (Entry.Key.IsValid()) Entry.Key->CustomTimeDilation = Entry.Value;
    SavedPresentationDilation.Reset();
    PlayerActionRate = 1.f;
    PreviewPlayer.Reset();
    RequestedPreviewScale = ActivePreviewScale = 1;
}
