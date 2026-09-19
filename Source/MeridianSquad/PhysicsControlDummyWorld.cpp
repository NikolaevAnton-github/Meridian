#include "CombatProjectileWorld.h"
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
        if (IsValid(PhysicsDummy)) PhysicsDummy->Destroy();
        PhysicsDummy = nullptr;
        PreviousDummies.Reset(); FrameStartDummies.Reset(); FrameEndDummies.Reset();
        SetPhysicsPreviewScale(1);
        return;
    }
    if (!IsValid(PhysicsDummy))
    {
        FActorSpawnParameters Params;
        Params.ObjectFlags |= RF_Transient;
        Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
        PhysicsDummy = GetWorld()->SpawnActor<APhysicsControlDummy>(FVector(-950, 110, 8), FRotator(0, 180, 0), Params);
        RecordCapsules();
    }
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
    RequestedPreviewScale = bEnablePhysicsDummy && Scale < .5f ? .25f : 1.f;
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
    // One scale for actual Chaos and projectile travel. The firing clock and player
    // remain at their previous rates through inverse actor time compensation.
    UGameplayStatics::SetGlobalTimeDilation(GetWorld(), SavedWorldDilation * RequestedPreviewScale);
    PreviewPlayer->CustomTimeDilation = SavedPlayerDilation / RequestedPreviewScale;
    CustomTimeDilation = SavedManagerDilation / RequestedPreviewScale;
    ProjectileTimeScale = RequestedPreviewScale;
    ActivePreviewScale = RequestedPreviewScale;
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
    PreviewPlayer.Reset();
    RequestedPreviewScale = ActivePreviewScale = 1;
}
