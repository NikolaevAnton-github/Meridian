#include "CombatProjectileWorld.h"
#include "CombatRifleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "PhysicsEngine/BodyInstance.h"
#include "Serialization/JsonSerializer.h"
#include "GameFramework/WorldSettings.h"
#include "Kismet/GameplayStatics.h"

FString ACombatProjectileWorld::ProbePhysicsPreviewOverrides()
{
    auto Report = MakeShared<FJsonObject>();
#if WITH_EDITOR
    auto* Player = UGameplayStatics::GetPlayerCharacter(GetWorld(), 0);
    if (GetWorld()->WorldType != EWorldType::PIE || !Player || bProcessingFrame || bOwnsPreviewTime || !Bullets.IsEmpty())
        return TEXT("{\"error\":\"Requires quiet normal PIE\"}");
    const float WorldBefore = GetWorld()->GetWorldSettings()->TimeDilation;
    const float PlayerBefore = Player->CustomTimeDilation, ManagerBefore = CustomTimeDilation, BulletBefore = ProjectileTimeScale;
    auto* Rifle = Player->FindComponentByClass<UCombatRifleComponent>();
    const int32 Ammo = Rifle->Magazine, Reserve = Rifle->Reserve;
    TArray<AActor*> Attached;
    Player->GetAttachedActors(Attached, true, true);
    TMap<TWeakObjectPtr<AActor>, float> ActorBefore;
    TMap<TWeakObjectPtr<USkeletalMeshComponent>, float> AnimationBefore;
    for (AActor* Actor : Attached)
    {
        ActorBefore.Add(Actor, Actor->CustomTimeDilation);
        Actor->CustomTimeDilation = .85f;
        TInlineComponentArray<USkeletalMeshComponent*> Meshes(Actor);
        for (auto* Mesh : Meshes) { AnimationBefore.Add(Mesh, Mesh->GlobalAnimRateScale); Mesh->GlobalAnimRateScale = .9f; }
    }
    UGameplayStatics::SetGlobalTimeDilation(GetWorld(), .8f);
    Player->CustomTimeDilation = .9f; CustomTimeDilation = 1.1f; ProjectileTimeScale = .7f;
    auto Restored = [&]()
    {
        bool Good = FMath::IsNearlyEqual(GetWorld()->GetWorldSettings()->TimeDilation, .8f) &&
            FMath::IsNearlyEqual(Player->CustomTimeDilation, .9f) && FMath::IsNearlyEqual(CustomTimeDilation, 1.1f) &&
            FMath::IsNearlyEqual(ProjectileTimeScale, .7f) && PlayerActionRate == 1.f;
        for (const auto& E : ActorBefore) Good &= E.Key.IsValid() && FMath::IsNearlyEqual(E.Key->CustomTimeDilation, .85f);
        for (const auto& E : AnimationBefore) Good &= E.Key.IsValid() && FMath::IsNearlyEqual(E.Key->GlobalAnimRateScale, .9f);
        return Good;
    };
    for (int32 I = 0; I < 3; ++I)
    {
        SetPhysicsPreviewScale(.25f); ApplyPreviewTime();
        Report->SetBoolField(FString::Printf(TEXT("enter_%d_no_compounding"), I),
            FMath::IsNearlyEqual(GetWorld()->GetWorldSettings()->TimeDilation, .2f) &&
            FMath::IsNearlyEqual(Player->CustomTimeDilation, .9f * .65f / .25f) &&
            FMath::IsNearlyEqual(ProjectileTimeScale, .7f * .25f));
        if (I == 0) SetPhysicsPreviewScale(1);
        if (I == 1) ResetTargets();
        if (I == 2) SetPhysicsDummyEnabled(false);
        ApplyPreviewTime();
        Report->SetBoolField(I == 0 ? TEXT("y_restores_saved_overrides") : I == 1 ? TEXT("f6_restores_saved_overrides") : TEXT("disable_restores_saved_overrides"), Restored());
    }
    SetPhysicsDummyEnabled(true);
    Report->SetBoolField(TEXT("six_recreated_and_ammo_unchanged"), PhysicsDummies.Num() == 6 && Rifle->Magazine == Ammo && Rifle->Reserve == Reserve);
    UGameplayStatics::SetGlobalTimeDilation(GetWorld(), WorldBefore);
    Player->CustomTimeDilation = PlayerBefore; CustomTimeDilation = ManagerBefore; ProjectileTimeScale = BulletBefore;
    for (const auto& E : ActorBefore) if (E.Key.IsValid()) E.Key->CustomTimeDilation = E.Value;
    for (const auto& E : AnimationBefore) if (E.Key.IsValid()) E.Key->GlobalAnimRateScale = E.Value;
#endif
    FString Result; FJsonSerializer::Serialize(Report, TJsonWriterFactory<>::Create(&Result)); return Result;
}

bool ACombatProjectileWorld::PreparePhysicsDummyFreefallProbe()
{
#if WITH_EDITOR
    if (GetWorld()->WorldType != EWorldType::PIE || bProcessingFrame || bAdvancing || !Bullets.IsEmpty()) return false;
    // Isolate the physical clock from ground-contact solver sensitivity. This is
    // an explicit quiet-PIE verification placement, never a production spawn.
    SetPhysicsDummyEnabled(false);
    bEnablePhysicsDummy = true;
    FActorSpawnParameters Params;
    Params.ObjectFlags |= RF_Transient;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    auto* PhysicsDummy = GetWorld()->SpawnActor<APhysicsControlDummy>(FVector(30000, 33000, 1000), FRotator(0, 180, 0), Params);
    PhysicsDummies.Add(PhysicsDummy);
    RecordCapsules();
    return IsValid(PhysicsDummy) && PhysicsDummy->IsReady();
#else
    return false;
#endif
}

FString ACombatProjectileWorld::ProbePhysicsDummy()
{
    auto Report = MakeShared<FJsonObject>();
#if WITH_EDITOR
    if (GetWorld()->WorldType != EWorldType::PIE || bProcessingFrame || bAdvancing || !Bullets.IsEmpty())
        return TEXT("{\"error\":\"Requires quiet PIE\"}");
    TGuardValue<float> ScaleGuard(ProjectileTimeScale, 1.f);
    TGuardValue<double> ClockGuard(FiringClock, FiringClock);
    TGuardValue<double> ActionClockGuard(PlayerActionClock, FiringClock);
    TGuardValue<float> ActionRateGuard(PlayerActionRate, 1.f);
    auto Check = [&](const TCHAR* Name, bool Pass) { Report->SetBoolField(Name, Pass); };
    auto Vec = [](const FVector& V) -> TSharedPtr<FJsonValue>
    { return MakeShared<FJsonValueArray>(TArray<TSharedPtr<FJsonValue>>{MakeShared<FJsonValueNumber>(V.X), MakeShared<FJsonValueNumber>(V.Y), MakeShared<FJsonValueNumber>(V.Z)}); };
    FActorSpawnParameters Params;
    Params.ObjectFlags |= RF_Transient;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    auto* Target = GetWorld()->SpawnActor<APhysicsControlDummy>(FVector(30000, 33000, 1000), FRotator(0, 180, 0), Params);
    Target->MaxHealth = 25;
    Target->ResetDummy();
    const auto Pose = Target->SamplePhysicalPose();
    if (Pose.Shapes.IsEmpty())
    {
        Target->Destroy();
        return TEXT("{\"error\":\"No physical query geometry\"}");
    }
    FVector Center = Pose.Shapes[0].Transform.GetLocation();
    for (const auto& Shape : Pose.Shapes)
        if (Shape.Bone.ToString().Contains(TEXT("spine"))) Center = Shape.Transform.GetLocation();
    const FVector View = Center - FVector(800, 0, 0);
    const FVector End = View + FVector(30000, 0, 0);
    auto* Rifle = NewObject<UCombatRifleComponent>(this, NAME_None, RF_Transient);
    Rifle->Simulation = this;
    Rifle->bTimingProbe = true;
    Rifle->bAllowedAtFrameStart = true;
    Rifle->bAutomatic = true;
    Rifle->ProbeView = View;
    Rifle->ProbeRotation = FQuat::Identity;
    const double StartTime = FiringClock;
    RecordCapsules(); bHaveBlockerSample = false;
    FHitResult LivingAim;
    const bool Aim = TraceEnemyAim(View, End, StartTime, LivingAim) && LivingAim.GetActor() == Target;
    Check(TEXT("physical_geometry_ready"), Target->IsReady() && Pose.Shapes.Num() >= 10);
    Check(TEXT("live_physical_aim"), Aim);
    Rifle->FirePressed();
    AdvanceFrame(.1, FPlatformTime::Seconds(), Rifle);
    Check(TEXT("two_births_one_100ms_interval"), Rifle->RecentShots.Num() == 2 && LastFrameBirths == 2);
    Check(TEXT("one_lethal_contact_before_later_birth"), Target->IsDead() && Target->Deaths == 1 && Target->PhysicalHits == 1 &&
        Target->DeathTime > StartTime && Target->DeathTime < StartTime + .085);
    FHitResult CorpseAim;
    {
        TGuardValue<bool> Processing(bProcessingFrame, true);
        Check(TEXT("same_interval_corpse_aim_is_eligible"), TraceEnemyAim(View, End, StartTime + .085, CorpseAim) && CorpseAim.GetActor() == Target);
    }
    TArray<TSharedPtr<FJsonValue>> Shots;
    for (const auto& S : Rifle->RecentShots)
    {
        auto Row = MakeShared<FJsonObject>();
        Row->SetNumberField(TEXT("id"), S.Id); Row->SetNumberField(TEXT("time"), S.Time);
        Row->SetField(TEXT("position"), Vec(S.Position)); Row->SetField(TEXT("velocity"), Vec(S.Velocity));
        Shots.Add(MakeShared<FJsonValueObject>(Row));
    }
    Report->SetArrayField(TEXT("shots"), Shots);
    Report->SetNumberField(TEXT("frame_start"), StartTime);
    Report->SetNumberField(TEXT("frame_end"), FrameEnd);
    Report->SetField(TEXT("corpse_aim"), Vec(CorpseAim.ImpactPoint));
    if (Rifle->RecentShots.Num() == 2)
    {
        const auto& First = Rifle->RecentShots[0]; const auto& Second = Rifle->RecentShots[1];
        Check(TEXT("85ms_spacing"), FMath::IsNearlyEqual(Second.Time - First.Time, .085, 1.e-7));
        const double Error = FVector::Distance(Second.Velocity.GetSafeNormal(), (CorpseAim.ImpactPoint - Second.Position).GetSafeNormal());
        Report->SetNumberField(TEXT("second_direction_error"), Error);
        Check(TEXT("second_converges_on_physical_corpse"), Error < 1.e-6);
        Check(TEXT("later_birth_has_only_residual_flight"), Bullets.Num() == 1 && Bullets[0].Id == Second.Id &&
            FMath::IsNearlyEqual(double(Bullets[0].Age), FrameEnd - Second.Time, 1.e-6) &&
            Bullets[0].Position.Equals(Second.Position + Second.Velocity * (FrameEnd - Second.Time), .001));
    }
    Rifle->CancelFiringSession();
    AdvanceFrame(.04, FPlatformTime::Seconds(), nullptr);
    Check(TEXT("later_round_consumed_once_by_corpse"), Bullets.IsEmpty() && Target->PhysicalHits == 2 && Target->Health == 0 && Target->Deaths == 1);
    TSharedPtr<FJsonObject> State;
    FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Target->GetDummyState()), State);
    Report->SetObjectField(TEXT("death_and_corpse"), State);

    Target->MaxHealth = 100; Target->ResetDummy(); ClearProjectiles();
    const auto ResetPose = Target->SamplePhysicalPose();
    bool bResetVelocities = true, bResetPose = ResetPose.Shapes.Num() == Pose.Shapes.Num();
    for (int32 I = 0; I < ResetPose.Shapes.Num(); ++I)
    {
        const auto* BI = Target->Body->GetBodyInstance(ResetPose.Shapes[I].Bone);
        bResetVelocities &= BI && BI->GetUnrealWorldVelocity().IsNearlyZero(.01) && BI->GetUnrealWorldAngularVelocityInRadians().IsNearlyZero(.01);
        bResetPose &= Pose.Shapes.IsValidIndex(I) && ResetPose.Shapes[I].Transform.Equals(Pose.Shapes[I].Transform, .001);
    }
    Check(TEXT("reset_return_clears_velocities"), bResetVelocities);
    Check(TEXT("reset_return_restores_pose_and_living_state"), bResetPose && Target->IsReady() && Target->Health == 100 && Target->Deaths == 0 && Target->PhysicalHits == 0);
    auto* Wall = GetWorld()->SpawnActor<AStaticMeshActor>(View + FVector(400, 0, 0), FRotator::ZeroRotator, Params);
    Wall->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
    Wall->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
    Wall->SetActorScale3D(FVector(.002, 3, 3));
    Wall->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
    const int32 BeforeWall = HitCount;
    Launch(nullptr, View, FVector(30000, 0, 0), 25);
    AdvanceFrame(.04, FPlatformTime::Seconds(), nullptr);
    Check(TEXT("nearest_two_mm_world_cover_consumes_bullet"), HitCount == BeforeWall + 1 && Bullets.IsEmpty() && Target->PhysicalHits == 0);
    Wall->Destroy(); ClearProjectiles();

    // Multiple live/corpse shapes must retain the nearest nonpenetrating contact,
    // independent health and independent reset epochs in either query direction.
    auto* Rear = GetWorld()->SpawnActor<APhysicsControlDummy>(FVector(30300, 33000, 1000), FRotator(0, 180, 0), Params);
    Rear->ConfigureReactionProfile(6); Rear->ResetDummy();
    Target->ConfigureReactionProfile(1); Target->ResetDummy();
    RecordCapsules();
    FHitResult Nearest;
    Check(TEXT("six_profile_nearest_aim"), TraceEnemyAim(View, End, FiringClock, Nearest) && Nearest.GetActor() == Target);
    const int32 BeforeTwo = HitCount;
    Launch(nullptr, View, FVector(30000, 0, 0), 25);
    AdvanceFrame(.04, FPlatformTime::Seconds(), nullptr);
    Check(TEXT("nearest_fixture_one_damage_one_impulse"), HitCount == BeforeTwo + 1 && Bullets.IsEmpty() &&
        Target->Health == 75 && Target->PhysicalHits == 1 && Rear->Health == 100 && Rear->PhysicalHits == 0);
    Launch(nullptr, Center + FVector(800, 0, 0), FVector(-30000, 0, 0), 25);
    AdvanceFrame(.04, FPlatformTime::Seconds(), nullptr);
    Check(TEXT("reverse_query_selects_other_fixture"), Target->Health == 75 && Target->PhysicalHits == 1 &&
        Rear->Health == 75 && Rear->PhysicalHits == 1 && Bullets.IsEmpty());
    const uint64 RearEpoch = Rear->SamplePhysicalPose().Epoch;
    Target->ResetDummy();
    Check(TEXT("per_actor_health_and_history_are_independent"), Rear->Health == 75 && Rear->PhysicalHits == 1 &&
        Rear->SamplePhysicalPose().Epoch == RearEpoch && Target->Health == 100 && Target->PhysicalHits == 0);
    Rear->Destroy(); ClearProjectiles();

    Rifle->bAutomatic = false;
    Rifle->ProbeView = Center - FVector(40, 0, 0);
    Rifle->bHaveViewSample = false;
    Rifle->FirePressed();
    AdvanceFrame(.02, FPlatformTime::Seconds(), Rifle);
    Check(TEXT("near_body_launch_stays_at_view"), Rifle->RecentShots.Num() == 3 && Rifle->RecentShots.Last().Position.Equals(Rifle->ProbeView, .001));
    Check(TEXT("near_body_receives_finite_contact_once"), Target->PhysicalHits == 1 && Bullets.IsEmpty());
    Rifle->CancelFiringSession(); ClearProjectiles();

    // Controlled translation history using one actual PA primitive. The body crossed
    // the suspended bullet at +20 ms, before the late bullet's +80 ms birth.
    FDummyPose Current = Target->SamplePhysicalPose();
    Current.Shapes.SetNum(1);
    FDummyPose Old = Current;
    Old.Shapes[0].Transform.AddToTranslation(FVector(-200, 0, 0));
    const FVector Suspended = Current.Shapes[0].Transform.GetLocation() - FVector(160, 0, 0);
    ProjectileTimeScale = 0;
    auto HistoryCase = [&](double BirthOffset)
    {
        ++FrameSerial;
        FrameStart = FiringClock; FrameEnd = FrameStart + .1;
        FrameStartDummies.Reset(); FrameEndDummies.Reset();
        FrameStartDummies.Add(Target, Old); FrameEndDummies.Add(Target, Current);
        FrameStartCapsules.Reset(); FrameEndCapsules.Reset();
        TGuardValue<bool> Processing(bProcessingFrame, true);
        LaunchTimed(nullptr, Suspended, FVector(1000, 0, 0), 25, FrameStart + BirthOffset);
        AdvanceSegment(FrameStart + BirthOffset, FrameEnd, FPlatformTime::Seconds());
        FiringClock = FrameEnd;
    };
    const int32 BeforeHistory = Target->PhysicalHits;
    HistoryCase(.08);
    Check(TEXT("late_birth_does_not_contact_prebirth_body_motion"), Target->PhysicalHits == BeforeHistory && Bullets.Num() == 1);
    ClearProjectiles();
    HistoryCase(0);
    Check(TEXT("existing_suspended_bullet_contacts_crossing_body"), Target->PhysicalHits == BeforeHistory + 1 && Bullets.IsEmpty());
    ClearProjectiles();
    Rifle->DestroyComponent(); Target->Destroy();
    RecordCapsules(); PreviousBlockers = SampleBlockers(); bHaveBlockerSample = true;
    FrameStartDummies.Reset(); FrameEndDummies.Reset();
    Check(TEXT("probe_cleanup"), Bullets.IsEmpty() && Target->IsActorBeingDestroyed());
#else
    Report->SetStringField(TEXT("error"), TEXT("PIE-only probe"));
#endif
    FString Result;
    FJsonSerializer::Serialize(Report, TJsonWriterFactory<>::Create(&Result));
    return Result;
}
