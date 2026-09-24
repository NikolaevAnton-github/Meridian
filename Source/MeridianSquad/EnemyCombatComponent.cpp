#include "EnemyCombatComponent.h"
#include "GASPEnemyFixture.h"
#include "GASPALSRifleAnimInstance.h"
#include "CombatProjectileWorld.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/PlayerController.h"
#include "HAL/IConsoleManager.h"
#include "Kismet/GameplayStatics.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraSystem.h"
#include "Serialization/JsonSerializer.h"
#include "Sound/SoundBase.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"

DEFINE_LOG_CATEGORY_STATIC(LogEnemyCombat, Log, All);

UEnemyCombatComponent::UEnemyCombatComponent()
{
    // The fixture advances decisions before its foundation produces Mover input.
    // No timer manager, second pawn/controller, or independent movement tick.
    PrimaryComponentTick.bCanEverTick = false;
    DecisionTrace = MakeUnique<CombatAI::TraceRing>();
}
AGASPEnemyFixture* UEnemyCombatComponent::Enemy() const { return Cast<AGASPEnemyFixture>(GetOwner()); }

CombatAI::ActionToken UEnemyCombatComponent::EnsureAction(CombatAI::ActionKind Kind, double Now)
{
    if (Action.Kind == Kind && Action.Accepts(Action.Token))
    { Action.Update(Action.Token, Now); return Action.Token; }
    FinishAction(Action.Token, CombatAI::ActionStatus::Canceled, CombatAI::ActionFailure::Replaced);
    Action.Start(EncounterGeneration, Kind, Now);
    RecordTrace(CombatAI::Event::Action, TEXT("action started"));
    return Action.Token;
}
bool UEnemyCombatComponent::FinishAction(CombatAI::ActionToken Request, CombatAI::ActionStatus Outcome, CombatAI::ActionFailure Why)
{
    if (!Action.Finish(Request, Outcome, Why, GetWorld()->GetTimeSeconds())) return false;
    RecordTrace(CombatAI::Event::Action, TEXT("action terminal outcome"));
    return true;
}
void UEnemyCombatComponent::ClearIntent(CombatAI::ActionFailure Why)
{
    FinishAction(Action.Token, CombatAI::ActionStatus::Canceled, Why);
    Gates.ReloadUntil = 0;
    PathRequest = {}; ReloadRequest = {};
    if ((bPlanning || !Path.IsEmpty()) && LastPathOutcome != CombatAI::PathOutcome::Arrived && LastPathOutcome != CombatAI::PathOutcome::Failed)
        RecordPath(CombatAI::PathOutcome::Canceled, TEXT("intent cleared"));
    Path.Reset(); Nodes.Reset(); OpenNodes.Reset(); CellNodes.Reset();
    PathIndex = 0; bPlanning = bPlanFailed = false;
    BurstRemaining = 0;
    if (auto* E = Enemy())
    {
        E->StopMovementCommand();
        E->SetRifleFollowPlayer(false);
        E->SetRifleStance(EGASPALSRifleStance::Ready);
        E->SetCrouchCommand(false);
    }
}
void UEnemyCombatComponent::ChangeState(EEnemyCombatState NewState, const TCHAR* Why)
{
    Reason = Why;
    if (State == NewState) return;
    State = NewState;
    StateStarted = GetWorld()->GetTimeSeconds();
    RecordTrace(CombatAI::Event::State, Why);
}
void UEnemyCombatComponent::SetEnabled(bool bEnable)
{
    bEnabled = bEnable;
    ClearIntent(CombatAI::ActionFailure::Reset);
    Action.Reset(EncounterGeneration);
    PathRequest = {}; ReloadRequest = {};
    Target.Reset(); Memory.Reset(); bTargetVisible = false;
    Knowledge.Reset(EncounterGeneration); IntentEvidenceId=0; bEvidencePending=false; NextEvidenceResponse=0;
    SearchGoal = SearchAnchor = SearchLook = PathGoal = FVector::ZeroVector;
    bRequestedWalk = true;
    ResetTactics(); Context={}; TargetHealthEvidence={}; AllyRoster={}; NextAllyRefresh=0; NextAdvanceAt=0;
    MoveBackoff = {}; WeaponBackoff = {};
    Gates = {}; Contact = CombatAI::ContactKind::None; ContactAt = ContactDecisionAt = 0;
    NextShot = GetWorld()->GetTimeSeconds();
    NextSight = NextRepath = 0; FailedAttempts = 0;
    ObstructionAttempts = 0; ObstructedSince = -1; ObstructionValidUntil = 0;
    ChangeState(bEnabled ? EEnemyCombatState::Idle : EEnemyCombatState::Disabled, bEnabled ? TEXT("combat enabled") : TEXT("manual fixture"));
}
void UEnemyCombatComponent::ResetCombat(FVector HomeGround, FRotator HomeRotation)
{
    Home = HomeGround; HomeFacing = HomeRotation;
    Magazine = FMath::Clamp(Tuning.MagazineCapacity, 1, 60);
    Shots = Reloads = Acquisitions = PathFailures = PathPlans = LastPathExpanded = 0;
    LastShotId = 0; FlashUntil = 0;
    if (const auto* Manager = ACombatProjectileWorld::Find(GetWorld()))
    {
        EncounterGeneration = Manager->GetEncounterGeneration();
        EncounterSeed = static_cast<uint32>(Manager->EncounterSeed);
    }
    Seed = CombatAI::AgentSeed(EncounterSeed, StableSpawnIndex);
    Spread.Initialize(static_cast<int32>(Seed));
    SightEventId = 0; CaptureDeltaSeconds = 0;
    LastKnownGround = LastKnownAim = FVector::ZeroVector;
    LastPathOutcome = CombatAI::PathOutcome::None;
    // Clear old intent before opening the new ring; no old-generation cancellation survives.
    SetEnabled(bEnabled);
    LastPathOutcome = CombatAI::PathOutcome::None;
    DecisionTrace->Reset(EncounterGeneration);
    RecordTrace(CombatAI::Event::Reset, TEXT("encounter reset; seed retained; player ammo unchanged"));
}
void UEnemyCombatComponent::StopCombat()
{
    ClearIntent(CombatAI::ActionFailure::Stopped);
    ResetTactics(); Gates = {};
    Target.Reset(); bTargetVisible = false; Memory.Reset();
    Knowledge.Reset(EncounterGeneration); bEvidencePending=false; IntentEvidenceId=0;
    NextShot = TNumericLimits<double>::Max();
    ChangeState(EEnemyCombatState::Disabled, TEXT("combat stopped"));
    RecordTrace(CombatAI::Event::Stop, TEXT("combat stopped"));
}
void UEnemyCombatComponent::SuspendForPhysics(bool bDead)
{
    if (!bEnabled) return;
    ClearIntent(bDead ? CombatAI::ActionFailure::Death : CombatAI::ActionFailure::Authority); bTargetVisible = false;
    ResetTactics();
    ObstructionAttempts=0; ObstructedSince=-1; ObstructionValidUntil=0;
    if (bDead) { Target.Reset(); Memory.Reset(); Knowledge.Reset(EncounterGeneration); bEvidencePending=false; }
    ChangeState(bDead ? EEnemyCombatState::Dead : EEnemyCombatState::Recovery,
        bDead ? TEXT("death cancels combat") : TEXT("physical authority owns movement"));
    RecordTrace(CombatAI::Event::Authority, TEXT("physical authority handover"));
}

bool UEnemyCombatComponent::ObservePlayer()
{
    const CombatAI::EncounterMemory Prior = Memory;
    const bool WasVisible = bTargetVisible;
    const FVector PriorDirection = (LastKnownGround - Feet()).GetSafeNormal2D();
    bTargetVisible = TryObservePlayer();
    if (bTargetVisible)
    {
        const double Now = GetWorld()->GetTimeSeconds();
        const FVector Direction = (LastKnownGround - Feet()).GetSafeNormal2D();
        const double Dot = PriorDirection.IsNearlyZero() || Direction.IsNearlyZero() ? 1 : FVector::DotProduct(PriorDirection, Direction);
        const auto Kind = CombatAI::ClassifyContact(Prior.Alert, Prior.HasObservation, WasVisible, Now-Prior.LastSeen, Dot);
        Gates.Sight(Kind, Now, WeaponProfile().Reaction);
        if (Kind != CombatAI::ContactKind::Continuous) { Contact = Kind; ContactAt = Now; }
    }
    RecordTrace(bTargetVisible ? CombatAI::Event::Sight : CombatAI::Event::SightLost,
        bTargetVisible ? TEXT("direct sight sample") : TEXT("sight query failed; retained last observation only"));
    return bTargetVisible;
}
bool UEnemyCombatComponent::TryObservePlayer()
{
    auto* E = Enemy();
    auto* PC = GetWorld()->GetFirstPlayerController();
    APawn* Player = PC ? PC->GetPawn() : nullptr;
    if (!E || !E->Foundation || !E->Body || !IsValid(Player)) return false;
    FVector Eye; FRotator View;
    PC->GetPlayerViewPoint(Eye, View);
    const FVector Origin = E->Body->GetSocketLocation(TEXT("head"));
    const auto* Capsule = Player->FindComponentByClass<UCapsuleComponent>();
    const FVector Center = Player->GetActorLocation();
    const float HalfHeight = Capsule ? Capsule->GetScaledCapsuleHalfHeight() : 88;
    const FVector Ground = Center - FVector(0,0,HalfHeight);
    const double Now = GetWorld()->GetTimeSeconds();
    const float Angle = FMath::Clamp(Tuning.SightHalfAngle + (Knowledge.RetainsContact(Now) ? 20.f : 0.f), 5.f, 179.f);
    FCollisionQueryParams Query(SCENE_QUERY_STAT(EnemySight), true);
    if (auto* World = ACombatProjectileWorld::Find(GetWorld())) World->BuildQuery(Query, E);
    Query.AddIgnoredActor(Player); Query.AddIgnoredActor(E->Foundation);
    // Camera, upper torso and lower torso have independent geometry tests. Reading
    // candidate points is confined to this sensor; no failed sample enters memory.
    const FVector Samples[] = {Eye, Ground+FVector(0,0,HalfHeight*1.45), Ground+FVector(0,0,HalfHeight*.8)};
    const int32 VisibleSample = CombatAI::FirstVisibleSample(3, [&](int32 Index)
    {
        const FVector& Sample=Samples[Index];
        const FVector Delta = Sample-Origin;
        if (Delta.SizeSquared() > FMath::Square(FMath::Clamp(Tuning.SightRange, 200.f, 10000.f)) ||
            FVector::DotProduct(Delta.GetSafeNormal2D(), E->Foundation->GetActorForwardVector().GetSafeNormal2D()) <
                FMath::Cos(FMath::DegreesToRadians(Angle))) return false;
        FHitResult Hit;
        return !GetWorld()->LineTraceSingleByChannel(Hit, Origin, Sample, ECC_Visibility, Query);
    });
    if (VisibleSample < 0) return false;
    // Only successful visibility may refresh these positions. Search never reads
    // the hidden player's transform, velocity or follow-player rifle seam.
    Target = Player;
    LastKnownAim = Samples[VisibleSample];
    LastKnownGround = Ground;
    CombatAI::StimulusData S;
    S.Id = (uint64(1)<<63) | (uint64(StableSpawnIndex)<<48) | ++SightEventId;
    S.Generation=EncounterGeneration; S.Observer=StableSpawnIndex; S.KnownIdentity=1;
    S.Kind=CombatAI::Sense::Sight; S.Category=CombatAI::SourceTeam::Player;
    S.Region={Ground.X,Ground.Y,Ground.Z}; S.Confidence=1;
    S.OccurredWorld=S.ReceivedWorld=Now;
    Knowledge.Accept(CombatAI::Stimulus(S), Now);
    Memory.Observe(Now); IntentEvidenceId=S.Id;
    return true;
}

bool UEnemyCombatComponent::CanShoot(FVector& Muzzle, FVector& Direction, bool& bObstructed) const
{
    bObstructed = false;
    const auto* E = Enemy();
    if (!E || !E->IsReady() || E->IsDead() || E->Authority != EGASPEnemyAuthority::Locomotion ||
        !E->IsRifleHeld() || !E->bRightHandOccupied || !E->Rifle || !Target.IsValid() || !bTargetVisible) return false;
    if (E->bCrouchCommand != E->IsMovementCrouched()) return false;
    const auto* Anim = Cast<UGASPALSRifleAnimInstance>(E->Body->GetAnimInstance());
    if (!Anim || Anim->RifleAlpha < .9f || Anim->RifleAimAlpha < .9f || E->GetRifleMovementAlpha() > .15f) return false;
    // The retained M4's measured barrel axis is local +Y. Prefer an authored
    // socket if a later weapon supplies one; this prototype ends at Y=61.96 cm.
    Muzzle = E->Rifle->DoesSocketExist(TEXT("Muzzle")) ? E->Rifle->GetSocketLocation(TEXT("Muzzle")) :
        E->Rifle->GetComponentTransform().TransformPosition(FVector(0, 62.f, 9.f));
    Direction = (LastKnownAim - Muzzle).GetSafeNormal();
    const float Alignment = FVector::DotProduct(E->Rifle->GetRightVector(), Direction);
    if (Alignment < FMath::Cos(FMath::DegreesToRadians(FMath::Clamp(Tuning.AimToleranceDegrees, .5f, 12.f)))) return false;
    bObstructed = MuzzleCorridorBlocked(Muzzle);
    return !bObstructed;
}
bool UEnemyCombatComponent::MuzzleCorridorBlocked(const FVector& Muzzle) const
{
    const auto* E = Enemy();
    FCollisionQueryParams Query(SCENE_QUERY_STAT(EnemyMuzzle), true);
    if (auto* World = ACombatProjectileWorld::Find(GetWorld())) World->BuildQuery(Query, E);
    FHitResult Hit;
    // A barrel clipped through thin cover is not a valid launch. Validate the
    // origin corridor as well as the full muzzle-to-observed-target corridor.
    return GetWorld()->SweepSingleByChannel(Hit, E->Body->GetSocketLocation(TEXT("spine_05")),
        Muzzle, FQuat::Identity, ECC_Visibility, FCollisionShape::MakeSphere(1.f), Query) ||
        GetWorld()->SweepSingleByChannel(Hit, Muzzle, LastKnownAim, FQuat::Identity,
            ECC_Visibility, FCollisionShape::MakeSphere(1.f), Query);
}
void UEnemyCombatComponent::RefreshObstruction(double Now, double Distance)
{
    const bool HadObstruction = ObstructedSince >= 0;
    if (Now >= ObstructionValidUntil) ObstructedSince = -1;
    const auto* E = Enemy();
    if (!bTargetVisible || !Target.IsValid() || !E || !E->Body || !E->Rifle ||
        (!HadObstruction && Distance <= Context.Weapon.EffectiveRange)) return;
    // Range movement needs current geometry, even while aim/stance is settling.
    // Use the same actual barrel corridors as launch, with permitted sight only;
    // this does not grant firing readiness or read a hidden target transform.
    const FVector Muzzle = E->Rifle->DoesSocketExist(TEXT("Muzzle")) ? E->Rifle->GetSocketLocation(TEXT("Muzzle")) :
        E->Rifle->GetComponentTransform().TransformPosition(FVector(0, 62.f, 9.f));
    if (MuzzleCorridorBlocked(Muzzle))
    {
        if (ObstructedSince < 0) ObstructedSince = Now;
        ObstructionValidUntil = Now + .5;
    }
    else { ObstructedSince = -1; ObstructionValidUntil = 0; }
}
bool UEnemyCombatComponent::Fire(double Now, CombatAI::ActionToken Request)
{
    if (!Action.Accepts(Request) || Action.Kind != CombatAI::ActionKind::Burst ||
        Request.Generation != EncounterGeneration) return false;
    if (Now < Gates.ReadyAt(NextShot) || BurstRemaining <= 0) return false;
    if (CoverPhase != CombatAI::CoverPhase::None &&
        (CoverPhase != CombatAI::CoverPhase::Firing || !Assignment.Accepts(CoverOwner))) return false;
    // Recheck visibility at the actual birth; cached perception cannot authorize
    // an extra round through newly entered cover or a replaced player pawn.
    bTargetVisible = ObservePlayer();
    if (CoverPhase != CombatAI::CoverPhase::None &&
        (!RefreshCoverThreat(Now) ||
         FVector::Dist2D(Feet(),CoverPlan.Pose) > 20 || !CoverCapsule(Feet(),false) ||
         !CoverWalk(Feet(),CoverPlan.Anchor) || !CoverProtected(CoverPlan.Anchor))) return false;
    FVector Muzzle, Direction; bool bObstructed;
    if (!bTargetVisible || Magazine <= 0 || Now < Gates.ReadyAt(NextShot) ||
        FVector::Dist2D(Feet(),LastKnownGround) > WeaponProfile().EffectiveRange ||
        !CanShoot(Muzzle, Direction, bObstructed)) return false;
    auto* World = ACombatProjectileWorld::Find(GetWorld());
    if (!World) return false;
    const FVector ShotDirection = Spread.VRandCone(Direction,
        FMath::DegreesToRadians(FMath::Clamp(Tuning.SpreadDegrees, 0.f, 5.f)));
    const int64 Shot = World->Launch(Enemy(), Muzzle, ShotDirection * FMath::Clamp(Tuning.BulletSpeed, 100.f, 100000.f),
        FMath::Clamp(Tuning.BulletDamage, .1f, 1000.f));
    if (!Shot) return false;
    LastShotId = Shot; ++Shots; --Magazine; --BurstRemaining;
    ObstructionAttempts = 0; ObstructedSince = -1; ObstructionValidUntil = 0;
    // Never repay missed-frame debt as an unbounded burst. Enemy cadence, reload
    // and thought deadlines share genuine world time (including 0.25 slowdown).
    NextShot = Now + WeaponProfile().Interval;
    LastMuzzle = Muzzle; LastBarrel = Direction; FlashUntil = Now + .06;
    if (!ShotSound) ShotSound = LoadObject<USoundBase>(nullptr,
        TEXT("/Game/InfimaGames/TacticalFPSAnimations/Weapons/AssaultRifle/Audio/Firing/A_TFA_AR_Fire_Single_Cue.A_TFA_AR_Fire_Single_Cue"));
    if (!MuzzleEffect) MuzzleEffect = LoadObject<UNiagaraSystem>(nullptr,
        TEXT("/Game/InfimaGames/TacticalFPSAnimations/Common/VFX/Systems/NS_TFA_MuzzleFlash.NS_TFA_MuzzleFlash"));
    if (ShotSound) UGameplayStatics::PlaySoundAtLocation(this, ShotSound, Muzzle, .45f,
        FMath::Clamp(UGameplayStatics::GetGlobalTimeDilation(this), .25f, 1.f));
    if (MuzzleEffect) UNiagaraFunctionLibrary::SpawnSystemAtLocation(GetWorld(), MuzzleEffect, Muzzle,
        Direction.Rotation(), FVector(.4f), true, true, ENCPoolMethod::AutoRelease);
    RecordTrace(CombatAI::Event::Shot, TEXT("finite projectile launched"));
    return true;
}

FString UEnemyCombatComponent::GetLabel() const
{
    return FString::Printf(TEXT("%s  %d/%d"), *StaticEnum<EEnemyCombatState>()->GetNameStringByValue(int64(State)),
        Magazine, FMath::Clamp(Tuning.MagazineCapacity, 1, 60));
}
FString UEnemyCombatComponent::GetCombatState() const
{
    auto Root = MakeShared<FJsonObject>();
    AppendObservationStatus(Root);
    AppendSensesStatus(Root);
    Root->SetBoolField(TEXT("enabled"), bEnabled);
    Root->SetStringField(TEXT("state"), StaticEnum<EEnemyCombatState>()->GetNameStringByValue(int64(State)));
    Root->SetStringField(TEXT("reason"), Reason);
    Root->SetNumberField(TEXT("world_time"), GetWorld()->GetTimeSeconds());
    Root->SetNumberField(TEXT("state_started"), StateStarted);
    Root->SetNumberField(TEXT("next_shot_world_time"), NextShot);
    Root->SetBoolField(TEXT("visible"), bTargetVisible);
    Root->SetNumberField(TEXT("last_seen_world_time"), Memory.LastSeen);
    Root->SetStringField(TEXT("last_known_ground"), LastKnownGround.ToString());
    Root->SetStringField(TEXT("target"), Target.IsValid() ? Target->GetPathName() : TEXT(""));
    Root->SetNumberField(TEXT("magazine"), Magazine);
    Root->SetStringField(TEXT("reserve_policy"), TEXT("unlimited; timed reload; interrupted reload restarts"));
    Root->SetNumberField(TEXT("shots"), Shots); Root->SetNumberField(TEXT("reloads"), Reloads);
    Root->SetNumberField(TEXT("last_shot_id"), LastShotId); Root->SetNumberField(TEXT("acquisitions"), Acquisitions);
    Root->SetNumberField(TEXT("path_failures"), PathFailures); Root->SetNumberField(TEXT("path_plans"), PathPlans);
    Root->SetNumberField(TEXT("path_expanded"), LastPathExpanded); Root->SetBoolField(TEXT("planning"), bPlanning);
    Root->SetNumberField(TEXT("obstruction_attempts"), ObstructionAttempts);
    Root->SetNumberField(TEXT("path_remaining"), Path.Num() - PathIndex);
    Root->SetStringField(TEXT("home_ground"), Home.ToString()); Root->SetStringField(TEXT("feet"), Feet().ToString());
    FString Result; FJsonSerializer::Serialize(Root, TJsonWriterFactory<>::Create(&Result)); return Result;
}

namespace
{
void EnemyCommand(const TArray<FString>& Args, UWorld* World)
{
    if (!World || !World->IsGameWorld() || Args.IsEmpty()) return;
    auto* Manager = ACombatProjectileWorld::Find(World);
    if (!Manager) return;
    const FString Op = Args[0].ToLower();
    if (Op == TEXT("one") || Op == TEXT("fixtures"))
    { Manager->SetEnemyCombatMode(Op == TEXT("one")); return; }
    if (Op == TEXT("reset")) { Manager->ResetTargets(); return; }
    if (Op == TEXT("seed") && Args.Num() == 2 && Args[1].IsNumeric())
    {
        const int64 Value = FCString::Atoi64(*Args[1]);
        if (Value < 0 || Value > MAX_int32) return;
        Manager->EncounterSeed = static_cast<int32>(Value);
        Manager->ResetTargets(); return;
    }
    for (TActorIterator<AGASPEnemyFixture> It(World); It; ++It)
    {
        auto* Combat = It->Combat.Get();
        if (Op == TEXT("pause")) Combat->SetEnabled(false);
        else if (Op == TEXT("resume") && Manager->IsEnemyCombatMode()) Combat->SetEnabled(true);
        else if (Op == TEXT("status")) { UE_LOG(LogEnemyCombat, Display, TEXT("%s"), *Combat->GetCombatState()); }
        else if (Op == TEXT("trace"))
        {
            const FString Directory = FPaths::ProjectSavedDir() / TEXT("CombatAI01/CAI-T02/Traces");
            IFileManager::Get().MakeDirectory(*Directory, true);
            const auto Snapshot = Combat->CaptureDecisionInput();
            const FString File = Directory / FString::Printf(TEXT("G%llu_S%u_%lld.json"),
                static_cast<uint64>(Snapshot.Generation), Snapshot.SpawnIndex, FDateTime::UtcNow().GetTicks());
            const bool Saved = FFileHelper::SaveStringToFile(Combat->GetCombatState(), *File,
                FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
            UE_LOG(LogEnemyCombat, Display, TEXT("Bounded trace %s: %s"), Saved ? TEXT("saved") : TEXT("failed"), *File);
        }
        else if (Op == TEXT("tune") && Args.Num() == 3 && Args[2].IsNumeric())
        {
            const float Value = FCString::Atof(*Args[2]);
            if (!FMath::IsFinite(Value)) continue;
            const FString Name = Args[1].ToLower();
            if (Name == TEXT("range")) Combat->Tuning.AttackRange = FMath::Clamp(Value, 150.f, 7000.f);
            else if (Name == TEXT("preferred")) Combat->Tuning.PreferredRange = FMath::Clamp(Value, 100.f, 7000.f);
            else if (Name == TEXT("advance")) Combat->Tuning.AdvanceStep = FMath::Clamp(Value, 100.f, 600.f);
            else if (Name == TEXT("reaction")) Combat->Tuning.AcquireSeconds = FMath::Clamp(Value, 0.f, 5.f);
            else if (Name == TEXT("sight")) Combat->Tuning.SightRange = FMath::Clamp(Value, 200.f, 10000.f);
            else if (Name == TEXT("aim")) Combat->Tuning.AimSeconds = FMath::Clamp(Value, 0.f, 5.f);
            else if (Name == TEXT("interval")) Combat->Tuning.ShotInterval = FMath::Clamp(Value, .08f, 5.f);
            else if (Name == TEXT("pause")) Combat->Tuning.BurstPause = FMath::Clamp(Value, .1f, 10.f);
            else if (Name == TEXT("reload")) Combat->Tuning.ReloadSeconds = FMath::Clamp(Value, .3f, 15.f);
            else if (Name == TEXT("search")) Combat->Tuning.SearchSeconds = FMath::Clamp(Value, .5f, 20.f);
            else if (Name == TEXT("tacticalradius")) Combat->Tuning.TacticalRadius = FMath::Clamp(Value, 250.f, 750.f);
            else if (Name == TEXT("reassess")) Combat->Tuning.TacticalReassessSeconds = FMath::Clamp(Value, 1.5f, 8.f);
            else if (Name == TEXT("commit")) Combat->Tuning.TacticalCommitSeconds = FMath::Clamp(Value, 1.f, 10.f);
            else if (Name == TEXT("probe")) Combat->Tuning.TacticalProbeSeconds = FMath::Clamp(Value, 3.f, 20.f);
            else if (Name == TEXT("margin")) Combat->Tuning.TacticalSwitchMargin = FMath::Clamp(Value, 3.f, 30.f);
            else { UE_LOG(LogEnemyCombat, Warning, TEXT("Unknown tuning key: %s"), *Name); continue; }
            UE_LOG(LogEnemyCombat, Display, TEXT("%s = %.3f (world seconds / cm)"), *Name, Value);
        }
    }
}
FAutoConsoleCommandWithWorldAndArgs EnemyCombatConsole(TEXT("msq.EnemyCombat"),
    TEXT("one | fixtures (three passive originals) | pause | resume | reset | seed 0..2147483647 (resets) | status | trace (explicit bounded export) | tune range/sight/aim/interval/pause/reload/search/tacticalradius/reassess/commit/probe/margin value"),
    FConsoleCommandWithWorldAndArgsDelegate::CreateStatic(&EnemyCommand));
}
