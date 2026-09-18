#include "CombatProjectileWorld.h"
#include "CombatRifleComponent.h"
#include "CombatTarget.h"
#include "OpeningLobbyCharacter.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Serialization/JsonSerializer.h"

// Focused additions to the existing PIE-only native probes. These call the
// production interval/launch/collision methods; the timestamp oracle is Python.
FString ACombatProjectileWorld::ProbeTiming(const FString& Configuration)
{
    auto Report = MakeShared<FJsonObject>();
#if WITH_EDITOR
    auto* Player = Cast<AOpeningLobbyCharacter>(UGameplayStatics::GetPlayerCharacter(GetWorld(), 0));
    auto* Rifle = Player ? Player->FindComponentByClass<UCombatRifleComponent>() : nullptr;
    TSharedPtr<FJsonObject> Config;
    if (GetWorld()->WorldType != EWorldType::PIE || !Rifle || !Rifle->bReady || bProcessingFrame ||
        bAdvancing || !Bullets.IsEmpty() || Rifle->bFireHeld || Rifle->bReloading ||
        !FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Configuration), Config))
        return TEXT("{\"error\":\"Timing probe requires quiet, initialized PIE and valid JSON\"}");
    auto Number = [&](const TCHAR* Key, double Default)
    {
        double Value = Default;
        Config->TryGetNumberField(Key, Value);
        return Value;
    };
    auto Check = [&](const TCHAR* Name, bool Value) { Report->SetBoolField(Name, Value); };
    const FTransform OriginalTransform = Player->GetActorTransform();
    const float OriginalScale = ProjectileTimeScale;
    const float OriginalInterval = Rifle->ShotInterval;
    const float OriginalSpeed = Rifle->BulletSpeed;
    const int32 OriginalCapacity = MaxProjectiles;
    const int32 OriginalMagazine = Rifle->Magazine, OriginalReserve = Rifle->Reserve;
    const bool OriginalAuto = Rifle->bAutomatic;
    const double OriginalClock = FiringClock;
    const FVector Origin(0, 8000, 12000);
    FActorSpawnParameters Params;
    Params.ObjectFlags |= RF_Transient;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    TArray<AActor*> Fixtures;
    Rifle->bTimingProbe = true;
    Rifle->bAllowedAtFrameStart = true;
    Rifle->bTimingBarrier = false;
    Rifle->bHaveViewSample = true;
    Rifle->PreviousView = Rifle->ProbeView = Origin;
    Rifle->PreviousViewRotation = Rifle->ProbeRotation = FQuat::Identity;
    Rifle->NextShotTime = Rifle->NextAllowedShotTime = 0.0;
    Rifle->NextDryTime = 0.0;
    Rifle->DryFeedbackRequests = 0;
    Rifle->RecentShots.Reset();
    Rifle->ShotCount = Rifle->FrameShotCount = Rifle->MaxFrameShotCount = 0;
    Rifle->Magazine = int32(Number(TEXT("magazine"), 30));
    Rifle->Reserve = int32(Number(TEXT("reserve"), 0));
    Rifle->ShotInterval = Number(TEXT("interval"), .085);
    Rifle->BulletSpeed = Number(TEXT("speed"), 1000);
    Rifle->bAutomatic = Number(TEXT("automatic"), 1.0) != 0.0;
    FiringClock = 0.0;
    DroppedTime = 0.0;
    OverloadFrames = GeometryBarriers = PeakFrameSteps = 0;
    SetProjectileTimeScale(Number(TEXT("scale"), 1.0));
    MaxProjectiles = int32(Number(TEXT("capacity"), 128));
    bHaveBlockerSample = false;
    FString Kind = TEXT("schedule");
    Config->TryGetStringField(TEXT("kind"), Kind);
    auto Target = [&](FVector Offset)
    {
        auto* Result = GetWorld()->SpawnActor<ACombatTarget>(Origin + Offset, FRotator::ZeroRotator, Params);
        Fixtures.Add(Result);
        return Result;
    };
    auto Wall = [&](double X)
    {
        auto* Result = GetWorld()->SpawnActor<AStaticMeshActor>(Origin + FVector(X, 0, 0), FRotator::ZeroRotator, Params);
        Fixtures.Add(Result);
        Result->SetMobility(EComponentMobility::Movable);
        Result->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
        Result->SetActorScale3D(FVector(.002, 20, 20));
        Result->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
        return Result;
    };
    auto JsonState = [](const FString& Text)
    {
        TSharedPtr<FJsonObject> Result;
        FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Text), Result);
        return Result;
    };
    if (Kind == TEXT("schedule") || Kind == TEXT("self"))
    {
        const auto& Deltas = Config->GetArrayField(TEXT("deltas"));
        const TArray<TSharedPtr<FJsonValue>>* Events = nullptr;
        Config->TryGetArrayField(TEXT("events"), Events);
        TArray<TSharedPtr<FJsonValue>> Rows, EventRows;
        const FVector Motion(Number(TEXT("view_speed"), 0.0), Number(TEXT("strafe_speed"), 0.0), 0);
        const double YawSpeed = Number(TEXT("yaw_speed"), 0.0);
        const bool bMoveShooter = Kind == TEXT("self");
        int64 OlderShot = 0;
        const int32 SelfBefore = SelfHitCount;
        if (bMoveShooter)
        {
            Player->SetActorLocation(Origin, false, nullptr, ETeleportType::TeleportPhysics);
            RecordCapsules();
            OlderShot = Launch(Player, Origin + FVector(50, 0, 0), FVector(1000, 0, 0), 25.f);
        }
        if (Number(TEXT("cover_x"), 0.0) > 0.0) Wall(Number(TEXT("cover_x"), 0.0));
        Rifle->FirePressed();
        for (int32 Frame = 0; Frame < Deltas.Num(); ++Frame)
        {
            if (Events) for (const auto& Value : *Events)
            {
                const auto Event = Value->AsObject();
                if (int32(Event->GetNumberField(TEXT("frame"))) != Frame) continue;
                const FString Type = Event->GetStringField(TEXT("type"));
                double Amount = 0.0;
                Event->TryGetNumberField(TEXT("value"), Amount);
                if (Type == TEXT("release")) Rifle->FireReleased();
                else if (Type == TEXT("press")) Rifle->FirePressed();
                else if (Type == TEXT("mode")) Rifle->ChangeFireMode();
                else if (Type == TEXT("reload"))
                {
                    const bool Accepted = Rifle->RequestReload(false);
                    Report->SetBoolField(TEXT("reload_request_accepted"), Accepted);
                }
                else if (Type == TEXT("commit"))
                {
                    Rifle->CommitReload(Player->GetMesh(), Rifle->ActiveReload, Rifle->ReloadInstanceId);
                    Rifle->ProbeDuplicateNotify();
                }
                else if (Type == TEXT("cancel")) Rifle->CancelReload();
                else if (Type == TEXT("reset")) ResetTargets();
                else if (Type == TEXT("capacity")) MaxProjectiles = int32(Amount);
                else if (Type == TEXT("scale")) SetProjectileTimeScale(Amount);
                else if (Type == TEXT("lock")) Rifle->bReloading = true;
                else if (Type == TEXT("unlock")) { Rifle->bReloading = false; Rifle->bTimingBarrier = true; }
                auto Recorded = MakeShared<FJsonObject>();
                Recorded->SetNumberField(TEXT("time"), FiringClock);
                Recorded->SetStringField(TEXT("type"), Type);
                EventRows.Add(MakeShared<FJsonValueObject>(Recorded));
            }
            const double Delta = Deltas[Frame]->AsNumber();
            const double End = FiringClock + Delta;
            Rifle->ProbeView = Origin + Motion * End;
            Rifle->ProbeRotation = FRotator(0, YawSpeed * End, 0).Quaternion();
            if (bMoveShooter) Player->SetActorLocation(Origin + Motion * End, false, nullptr, ETeleportType::TeleportPhysics);
            Rifle->bAllowedAtFrameStart = Rifle->CanAct();
            AdvanceFrame(Delta, FPlatformTime::Seconds(), Rifle);
            auto Row = MakeShared<FJsonObject>();
            Row->SetNumberField(TEXT("time"), FiringClock);
            Row->SetNumberField(TEXT("delta"), Delta);
            Row->SetNumberField(TEXT("steps"), LastFrameSteps);
            Row->SetNumberField(TEXT("attempts"), LastFrameBirths);
            Row->SetNumberField(TEXT("shots"), Rifle->ShotCount);
            Row->SetNumberField(TEXT("ammo"), Rifle->Magazine);
            Row->SetNumberField(TEXT("reserve"), Rifle->Reserve);
            Row->SetNumberField(TEXT("hits"), HitCount);
            Row->SetNumberField(TEXT("active"), Bullets.Num());
            Rows.Add(MakeShared<FJsonValueObject>(Row));
        }
        Report->SetArrayField(TEXT("frames"), Rows);
        Report->SetArrayField(TEXT("events"), EventRows);
        Report->SetNumberField(TEXT("older_shot"), OlderShot);
        Report->SetNumberField(TEXT("new_self_hits"), SelfHitCount - SelfBefore);
        Report->SetObjectField(TEXT("rifle"), JsonState(Rifle->GetRifleState()));
        Report->SetObjectField(TEXT("world"), JsonState(GetCombatState()));
    }
    else if (Kind == TEXT("contracts"))
    {
        auto* Thin = Wall(200.6);
        for (int32 Order = 0; Order < 2; ++Order)
        {
            ClearProjectiles();
            FiringClock = 0;
            int64 LaterId = 0;
            for (int32 I = 0; I < 2; ++I)
            {
                const bool Later = I == Order;
                const int64 Id = Launch(nullptr, Origin + FVector(Later ? 160 : 0, 0, 0), FVector(1000, 0, 0), 25.f);
                Bullets.Last().BirthTime = Later ? .17 : 0.0;
                if (Later) LaterId = Id;
            }
            const int32 HitsBefore = HitCount;
            Advance(.25f, FPlatformTime::Seconds());
            Check(Order == 0 ? TEXT("absolute_contacts_original_order") : TEXT("absolute_contacts_reverse_order"),
                HitCount == HitsBefore + 2 && LastHitShotId == LaterId && FMath::IsNearlyEqual(LastContactTime, .21, 1.e-5));
            Advance(.25f, FPlatformTime::Seconds());
            Check(Order == 0 ? TEXT("thin_hits_once_a") : TEXT("thin_hits_once_b"), HitCount == HitsBefore + 2);
        }
        Thin->Destroy();
        auto* Front = Target(FVector(100, 0, 0));
        auto* Rear = Target(FVector(150, 0, 0));
        Front->MaxHealth = 25;
        for (int32 Resolution = 0; Resolution < 2; ++Resolution)
        for (int32 Order = 0; Order < 2; ++Order)
        {
            ClearProjectiles();
            Front->ResetTarget();
            Rear->ResetTarget();
            const int32 HitsBefore = HitCount;
            Launch(nullptr, Origin + FVector(Order == 0 ? 84 : 85, 0, 0), FVector(1000, 0, 0), 25.f);
            Launch(nullptr, Origin + FVector(Order == 0 ? 85 : 84, 0, 0), FVector(1000, 0, 0), 25.f);
            for (int32 Step = 0; Step < (Resolution == 0 ? 1 : 50); ++Step)
                AdvanceFrame(Resolution == 0 ? .25 : .005, FPlatformTime::Seconds(), nullptr);
            const TCHAR* Key = Resolution == 0 ?
                (Order == 0 ? TEXT("shield_original_order") : TEXT("shield_reverse_order")) :
                (Order == 0 ? TEXT("fine_shield_original_order") : TEXT("fine_shield_reverse_order"));
            Check(Key,
                Bullets.IsEmpty() && Front->Hits == 1 && Rear->Hits == 0 && HitCount == HitsBefore + 2);
        }
        ClearProjectiles();
        Front->MaxHealth = 100;
        Front->ResetTarget();
        FiringClock = 0;
        Rifle->NextShotTime = Rifle->NextAllowedShotTime = 0;
        Rifle->FirePressed();
        const int32 BeforeResetShots = Rifle->ShotCount;
        const int32 BeforeResetAmmo = Rifle->Magazine;
        ProbeSpawnPosition = Origin + FVector(0, 500, 0);
        ProbeResetCallbacks = 0;
        bProbeResetPending = true;
        OnBulletHit.AddDynamic(this, &ACombatProjectileWorld::ProbeHitReset);
        AdvanceFrame(.25, FPlatformTime::Seconds(), Rifle);
        OnBulletHit.RemoveDynamic(this, &ACombatProjectileWorld::ProbeHitReset);
        bProbeResetPending = false;
        Check(TEXT("callback_reset_cancels_later_scheduled_births"), ProbeResetCallbacks == 1 &&
            Rifle->ShotCount == BeforeResetShots + 1 && Rifle->Magazine == BeforeResetAmmo - 1 && !Rifle->bFireHeld);
        Check(TEXT("callback_bullets_deferred_entire_frame"), Bullets.Num() == 2 &&
            Bullets[0].Age == 0 && Bullets[1].Age == 0 && Bullets[0].Position == ProbeSpawnPosition && Bullets[1].Position == ProbeSpawnPosition);
        AdvanceFrame(.1, FPlatformTime::Seconds(), Rifle);
        Check(TEXT("reset_has_no_later_backlog"), Rifle->ShotCount == BeforeResetShots + 1 &&
            Bullets.Num() == 2 && FMath::IsNearlyEqual(Bullets[0].Age, .1f, 1.e-6f));
        ClearProjectiles();
        Rifle->FireReleased();
        bHaveBlockerSample = false;
        AdvanceFrame(.01, FPlatformTime::Seconds(), Rifle);
        Rifle->FirePressed();
        Front->SetActorLocation(Front->GetActorLocation() + FVector(0, 50, 0));
        const int32 BeforeBarrierShots = Rifle->ShotCount;
        AdvanceFrame(.25, FPlatformTime::Seconds(), Rifle);
        Check(TEXT("moving_unrecorded_geometry_fails_closed"), GeometryBarriers == 1 &&
            Rifle->ShotCount == BeforeBarrierShots && !Rifle->bFireHeld && Bullets.IsEmpty());
        Report->SetNumberField(TEXT("max_steps"), PeakFrameSteps);
    }
    else Report->SetStringField(TEXT("error"), TEXT("Unknown timing probe kind"));
    Rifle->CancelReload();
    ClearProjectiles();
    Rifle->CancelFiringSession();
    for (AActor* Fixture : Fixtures) Fixture->Destroy();
    Player->SetActorTransform(OriginalTransform, false, nullptr, ETeleportType::TeleportPhysics);
    RecordCapsules();
    Rifle->ShotInterval = OriginalInterval;
    Rifle->BulletSpeed = OriginalSpeed;
    Rifle->Magazine = OriginalMagazine;
    Rifle->Reserve = OriginalReserve;
    Rifle->bAutomatic = OriginalAuto;
    Rifle->bTimingProbe = false;
    Rifle->bHaveViewSample = false;
    Rifle->bTimingBarrier = false;
    Rifle->bAllowedAtFrameStart = false;
    Rifle->SyncPresentation();
    FiringClock = OriginalClock;
    Rifle->NextAllowedShotTime = Rifle->NextShotTime = FiringClock;
    MaxProjectiles = OriginalCapacity;
    SetProjectileTimeScale(OriginalScale);
    Report->SetBoolField(TEXT("cleanup"), Bullets.IsEmpty() && !Rifle->bFireHeld && !Rifle->bReloading);
#else
    Report->SetStringField(TEXT("error"), TEXT("PIE-only development probe"));
#endif
    FString Result;
    FJsonSerializer::Serialize(Report, TJsonWriterFactory<>::Create(&Result));
    return Result;
}
