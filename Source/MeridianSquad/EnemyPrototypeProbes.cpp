#include "CombatProjectileWorld.h"
#include "CombatRifleComponent.h"
#include "OpeningLobbyCharacter.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/DamageEvents.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Serialization/JsonSerializer.h"

FString ACombatProjectileWorld::ProbeEnemy(bool bCoverOnly, bool bAimOnly)
{
    auto Report = MakeShared<FJsonObject>();
    if (bAimOnly)
    {
#if WITH_EDITOR
        if (GetWorld()->WorldType != EWorldType::PIE || bProcessingFrame || bAdvancing || !Bullets.IsEmpty())
            return TEXT("{\"error\":\"Enemy aim probe requires quiet PIE\"}");
        TGuardValue<float> ScaleGuard(ProjectileTimeScale, 1.f);
        TGuardValue<double> ClockGuard(FiringClock, FiringClock);
        FActorSpawnParameters AimParams;
        AimParams.ObjectFlags |= RF_Transient;
        AimParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
        auto* AimTarget = GetWorld()->SpawnActor<AEnemyPrototypeCharacter>(FVector(30000, 30000, 1000), FRotator::ZeroRotator, AimParams);
        AimTarget->MaxHealth = 25.f;
        AimTarget->ResetEnemy();
        AimTarget->GetCharacterMovement()->DisableMovement();
        AimTarget->GetMesh()->TickAnimation(0, false);
        AimTarget->GetMesh()->RefreshBoneTransforms();
        const FVector View = AimTarget->SampleHitSpheres()[0].Center - FVector(200, 0, 0);
        const FVector End = View + FVector(30000, 0, 0);
        auto* Rear = GetWorld()->SpawnActor<AStaticMeshActor>(View + FVector(2000, 0, 0), FRotator::ZeroRotator, AimParams);
        Rear->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
        Rear->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
        Rear->SetActorScale3D(FVector(.02, 2, 2));
        Rear->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));

        // Isolate input/ammunition from the player's rifle while exercising the
        // production scheduler, EmitScheduledShot, aim and finite-flight paths.
        auto* Rifle = NewObject<UCombatRifleComponent>(this, NAME_None, RF_Transient);
        Rifle->Simulation = this;
        Rifle->bTimingProbe = true;
        Rifle->bAllowedAtFrameStart = true;
        Rifle->bAutomatic = true;
        Rifle->ProbeView = View;
        Rifle->ProbeRotation = FQuat::Identity;
        const double StartTime = FiringClock;
        RecordCapsules();
        bHaveBlockerSample = false;
        FHitResult LiveAim, RearAim;
        const bool bLiveAim = TraceEnemyAim(View, End, StartTime, LiveAim) && LiveAim.GetActor() == AimTarget;
        FCollisionQueryParams Query(SCENE_QUERY_STAT(EnemyAimProbe), true);
        BuildQuery(Query);
        const bool bRearAim = GetWorld()->LineTraceSingleByChannel(RearAim, View, End, ECC_Visibility, Query) && RearAim.GetActor() == Rear;
        Report->SetBoolField(TEXT("live_aim_before_lethal_hit"), bLiveAim && AimTarget->Health == 25.f);
        Report->SetBoolField(TEXT("rear_world_fixture_behind_live_enemy"), bLiveAim && bRearAim && RearAim.Time > LiveAim.Time);
        Rifle->FirePressed();
        AdvanceFrame(.1, FPlatformTime::Seconds(), Rifle);
        Report->SetBoolField(TEXT("two_85ms_births_in_one_100ms_interval"), Rifle->RecentShots.Num() == 2 && LastFrameBirths == 2 &&
            FMath::IsNearlyEqual(LastFrameDelta, .1, 1.e-8) && FMath::IsNearlyEqual(double(Rifle->ShotInterval), .085, 1.e-7));
        Report->SetBoolField(TEXT("first_hit_kills_and_disables_queries"), AimTarget->Health == 0.f && AimTarget->Hits == 1 && AimTarget->Deaths == 1 &&
            !AimTarget->GetCapsuleComponent()->IsQueryCollisionEnabled());
        const auto Cached = CapsulesAt(StartTime + .085);
        const auto* CachedTarget = Cached.Find(AimTarget);
        Report->SetBoolField(TEXT("dead_enemy_spheres_remain_in_frame_history"), CachedTarget && CachedTarget->Regions.Num() == 28);
        {
            // Replay the second birth's cached query after the production frame;
            // the actual second launch direction below proves its in-frame use.
            TGuardValue<bool> CachedQueryGuard(bProcessingFrame, true);
            FHitResult DeadAim;
            Report->SetBoolField(TEXT("cached_dead_enemy_excluded_from_aim"), !TraceEnemyAim(View, End, StartTime + .085, DeadAim));
        }
        auto Measurements = MakeShared<FJsonObject>();
        Measurements->SetNumberField(TEXT("frame_start"), StartTime);
        Measurements->SetNumberField(TEXT("frame_end"), FrameEnd);
        Measurements->SetNumberField(TEXT("last_contact_time"), LastContactTime);
        Measurements->SetNumberField(TEXT("health"), AimTarget->Health);
        Measurements->SetNumberField(TEXT("hits"), AimTarget->Hits);
        Measurements->SetNumberField(TEXT("deaths"), AimTarget->Deaths);
        Measurements->SetNumberField(TEXT("steps"), LastFrameSteps);
        Measurements->SetNumberField(TEXT("cached_spheres"), CachedTarget ? CachedTarget->Regions.Num() : 0);
        auto VectorJson = [](const FVector& Value) -> TSharedPtr<FJsonValue>
        {
            return MakeShared<FJsonValueArray>(TArray<TSharedPtr<FJsonValue>>{
                MakeShared<FJsonValueNumber>(Value.X), MakeShared<FJsonValueNumber>(Value.Y), MakeShared<FJsonValueNumber>(Value.Z)});
        };
        Measurements->SetField(TEXT("live_aim_point"), VectorJson(LiveAim.ImpactPoint));
        Measurements->SetField(TEXT("rear_world_aim_point"), VectorJson(RearAim.ImpactPoint));
        TArray<TSharedPtr<FJsonValue>> Shots;
        for (const auto& Shot : Rifle->RecentShots)
        {
            auto Row = MakeShared<FJsonObject>();
            Row->SetNumberField(TEXT("id"), Shot.Id);
            Row->SetNumberField(TEXT("birth_time"), Shot.Time);
            Row->SetField(TEXT("position"), VectorJson(Shot.Position));
            Row->SetField(TEXT("velocity"), VectorJson(Shot.Velocity));
            Shots.Add(MakeShared<FJsonValueObject>(Row));
        }
        Measurements->SetArrayField(TEXT("shots"), Shots);
        if (Rifle->RecentShots.Num() == 2)
        {
            const auto& First = Rifle->RecentShots[0];
            const auto& Second = Rifle->RecentShots[1];
            const double FirstError = FVector::Distance(First.Velocity.GetSafeNormal(), (LiveAim.ImpactPoint - First.Position).GetSafeNormal());
            const double RearError = FVector::Distance(Second.Velocity.GetSafeNormal(), (RearAim.ImpactPoint - Second.Position).GetSafeNormal());
            const double DeadError = FVector::Distance(Second.Velocity.GetSafeNormal(), (LiveAim.ImpactPoint - Second.Position).GetSafeNormal());
            Measurements->SetNumberField(TEXT("first_live_direction_error"), FirstError);
            Measurements->SetNumberField(TEXT("second_rear_direction_error"), RearError);
            Measurements->SetNumberField(TEXT("second_dead_direction_error"), DeadError);
            Report->SetBoolField(TEXT("birth_times_preserve_85ms_schedule"), FMath::IsNearlyEqual(First.Time, StartTime, 1.e-8) &&
                FMath::IsNearlyEqual(Second.Time - First.Time, .085, 1.e-7));
            Report->SetBoolField(TEXT("first_shot_converges_on_live_enemy"), bLiveAim && FirstError < 1.e-6);
            Report->SetBoolField(TEXT("lethal_contact_precedes_second_birth"), LastHitShotId == First.Id && LastContactTime >= First.Time && LastContactTime < Second.Time);
            Report->SetBoolField(TEXT("second_shot_converges_on_rear_world"), bRearAim && RearError < 1.e-6 && DeadError > 1.e-3);
            const double Residual = FrameEnd - Second.Time;
            Report->SetBoolField(TEXT("second_birth_and_residual_flight_preserved"), Bullets.Num() == 1 &&
                Bullets[0].Id == Second.Id && FMath::IsNearlyEqual(Bullets[0].BirthTime, Second.Time, 1.e-8) &&
                FMath::IsNearlyEqual(double(Bullets[0].Age), Residual, 1.e-6) &&
                Bullets[0].Position.Equals(Second.Position + Second.Velocity * Residual, .001));
            if (Bullets.Num() == 1)
            {
                Measurements->SetNumberField(TEXT("surviving_birth_time"), Bullets[0].BirthTime);
                Measurements->SetNumberField(TEXT("surviving_age"), Bullets[0].Age);
                Measurements->SetField(TEXT("surviving_position"), VectorJson(Bullets[0].Position));
            }
        }
        Report->SetObjectField(TEXT("measurements"), Measurements);
        Rifle->CancelFiringSession();
        Rifle->DestroyComponent();
        AimTarget->Destroy();
        Rear->Destroy();
        ClearProjectiles();
        RecordCapsules();
        PreviousBlockers = SampleBlockers();
        bHaveBlockerSample = true;
        Report->SetBoolField(TEXT("cleanup"), Bullets.IsEmpty() && AimTarget->IsActorBeingDestroyed() && Rear->IsActorBeingDestroyed());
#else
        Report->SetStringField(TEXT("error"), TEXT("Enemy aim probe is PIE-only"));
#endif
        FString Result;
        FJsonSerializer::Serialize(Report, TJsonWriterFactory<>::Create(&Result));
        return Result;
    }
    ClearProjectiles();
    const float SavedScale = ProjectileTimeScale;
    ProjectileTimeScale = 1.f;
    FActorSpawnParameters Params;
    Params.ObjectFlags |= RF_Transient;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    auto* Target = GetWorld()->SpawnActor<AEnemyPrototypeCharacter>(FVector(30000, 30000, 1000), FRotator::ZeroRotator, Params);
    auto Prepare = [&]()
    {
        ClearProjectiles();
        Target->ResetEnemy();
        Target->GetCharacterMovement()->DisableMovement();
        Target->GetMesh()->TickAnimation(0, false);
        Target->GetMesh()->RefreshBoneTransforms();
        RecordCapsules();
    };
    const double Now = FPlatformTime::Seconds();
    if (!bCoverOnly)
    {
    TArray<TSharedPtr<FJsonValue>> Regions;
    for (FName Region : {FName(TEXT("head")), FName(TEXT("torso")), FName(TEXT("pelvis")), FName(TEXT("arm_l")),
        FName(TEXT("arm_r")), FName(TEXT("leg_l")), FName(TEXT("leg_r"))})
    {
        Prepare();
        FVector Origin, Destination;
        bool Found = false;
        for (const auto& Sphere : Target->SampleHitSpheres())
        {
            if (AEnemyPrototypeCharacter::RegionForBone(Sphere.Bone) != Region) continue;
            for (const FVector Direction : {FVector::ForwardVector, -FVector::ForwardVector, FVector::RightVector, -FVector::RightVector, FVector::UpVector})
            {
                FHitResult Hit;
                Origin = Sphere.Center + Direction * 100.f;
                Destination = Sphere.Center - Direction * 5.f;
                if (TraceEnemyAim(Origin, Destination, FiringClock, Hit) && Hit.GetActor() == Target &&
                    AEnemyPrototypeCharacter::RegionForBone(Hit.BoneName) == Region) { Found = true; break; }
            }
            if (Found) break;
        }
        const float Before = Target->Health;
        if (Found)
        {
            Launch(nullptr, Origin, (Destination - Origin).GetSafeNormal() * 30000.f, 25.f);
            Advance(.01f, Now);
        }
        auto Row = MakeShared<FJsonObject>();
        Row->SetStringField(TEXT("region"), Region.ToString());
        Row->SetBoolField(TEXT("aim_query"), Found);
        Row->SetBoolField(TEXT("finite_flight_damage"), Target->Health == Before - 25.f && Target->Hits == 1);
        Row->SetBoolField(TEXT("region_matches"), Target->LastRegion == Region);
        Regions.Add(MakeShared<FJsonValueObject>(Row));
    }
    Report->SetArrayField(TEXT("regions"), Regions);
    Prepare();
    const auto Head = Target->SampleHitSpheres()[0];
    // A hit-volume gap stays a miss; the movement capsule is never a damage proxy.
    Launch(nullptr, Head.Center + FVector(-100, 30, 0), FVector(30000, 0, 0), 25);
    Advance(.006f, Now);
    Report->SetBoolField(TEXT("outside_head_sphere_misses"), Target->Health == 100.f);
    }
    Prepare();
    const FVector HeadCenter = Target->SampleHitSpheres()[0].Center;
    auto* Cover = GetWorld()->SpawnActor<AStaticMeshActor>(HeadCenter + FVector(-50, 0, 0), FRotator::ZeroRotator, Params);
    Cover->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
    Cover->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
    Cover->SetActorScale3D(FVector(.02, .6, .6));
    Cover->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
    Launch(nullptr, HeadCenter + FVector(-100, 0, 0), FVector(30000, 0, 0), 25);
    Advance(.01f, Now);
    Report->SetBoolField(TEXT("thin_world_cover_precedes_enemy_region"), Target->Health == 100.f && Bullets.IsEmpty());
    Cover->Destroy();
    if (!bCoverOnly)
    {
    Prepare();
    const FVector Suspended = Target->SampleHitSpheres()[0].Center + FVector(0, 75, 0);
    ProjectileTimeScale = 0;
    Launch(nullptr, Suspended, FVector(30000, 0, 0), 25);
    Target->AddActorWorldOffset(FVector(0, 150, 0), false, nullptr, ETeleportType::TeleportPhysics);
    Target->GetMesh()->RefreshBoneTransforms();
    Advance(.1f, Now);
    Report->SetBoolField(TEXT("moving_head_crosses_suspended_bullet"), Target->Health == 75.f && Target->LastRegion == TEXT("head"));
    Prepare();
    const FVector Past = Target->SampleHitSpheres()[0].Center + FVector(0, 75, 0);
    Target->AddActorWorldOffset(FVector(0, 150, 0), false, nullptr, ETeleportType::TeleportPhysics);
    Target->GetMesh()->RefreshBoneTransforms();
    Launch(nullptr, Past, FVector(30000, 0, 0), 25);
    Advance(.1f, Now);
    Report->SetBoolField(TEXT("birth_does_not_hit_prior_enemy_motion"), Target->Health == 100.f);
    ProjectileTimeScale = 1;
    Prepare();
    const auto DeathHead = Target->SampleHitSpheres()[0];
    for (int32 Count = 0; Count < 6; ++Count)
        Launch(nullptr, DeathHead.Center + FVector(-100, 0, 0), FVector(30000, 0, 0), 25);
    Advance(.01f, Now);
    Report->SetBoolField(TEXT("six_queued_hits_one_death"), Target->Health == 0 && Target->Hits == 4 && Target->Deaths == 1);
    FDamageEvent Invalid;
    const float Repeated = Target->TakeDamage(100, Invalid, nullptr, nullptr);
    Report->SetBoolField(TEXT("dead_repeated_damage_ignored"), Repeated == 0 && Target->Hits == 4 && Target->Deaths == 1 && Target->SampleHitSpheres().IsEmpty());
    Prepare();
    Report->SetBoolField(TEXT("reset_restores_animation_and_queries"), Target->Health == 100 && Target->Hits == 0 && Target->Deaths == 0 &&
        !Target->SampleHitSpheres().IsEmpty() && Target->GetCapsuleComponent()->IsQueryCollisionEnabled() && !Target->GetMesh()->IsAnySimulatingPhysics());
    }
    Target->Destroy();
    ClearProjectiles();
    ProjectileTimeScale = SavedScale;
    FString Result;
    FJsonSerializer::Serialize(Report, TJsonWriterFactory<>::Create(&Result));
    return Result;
}
