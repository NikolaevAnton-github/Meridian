#include "EnemyCombatComponent.h"
#include "GASPEnemyFixture.h"
#include "Engine/World.h"

void UEnemyCombatComponent::BeginSearch(const TCHAR* Why, bool bRestart)
{
    ClearIntent(); NextRepath = 0; FailedAttempts = 0; bReposition = false;
    bSearchGoal = false; ObserveUntil = 0;
    if (bRestart)
    {
        SearchCycle.Restart();
        SearchAnchor = LastKnownGround;
        SearchLook = LastKnownAim;
        SearchForward = (LastKnownGround - Feet()).GetSafeNormal2D();
        if (SearchForward.IsNearlyZero()) SearchForward = HomeFacing.Vector().GetSafeNormal2D();
    }
    ChangeState(Memory.Alert ? EEnemyCombatState::Search : EEnemyCombatState::Idle, Why);
}

void UEnemyCombatComponent::FailTactic(const TCHAR* Why, CombatAI::ActionFailure Failure, bool bWeapon)
{
    FinishAction(Action.Token, CombatAI::ActionStatus::Failed, Failure);
    auto& Backoff = bWeapon ? WeaponBackoff : MoveBackoff;
    Backoff.Set(LastKnownGround.X, LastKnownGround.Y,
        GetWorld()->GetTimeSeconds() + FMath::Clamp(Tuning.RetryCooldown, 1.f, 30.f));
    BeginSearch(Why);
    // Avoid immediately retrying the same failed last-seen destination.
    SearchCycle.Index = 1;
}

void UEnemyCombatComponent::AdvanceSearch(double Now)
{
    auto* E = Enemy();
    if (!Memory.Alert || !Memory.HasObservation) return;
    E->SetCrouchCommand(false);
    E->SetRifleStance(EGASPALSRifleStance::Ready);
    // Look at permitted evidence or an inspection sector. Never follow the hidden pawn.
    E->SetRifleAimTarget(SearchLook);
    if (Now < SearchCycle.RetryAt || Now < ObserveUntil)
    {
        E->StopMovementCommand(); EnsureAction(CombatAI::ActionKind::Observe, Now); return;
    }
    if (Action.Kind == CombatAI::ActionKind::Observe)
        FinishAction(Action.Token, CombatAI::ActionStatus::Succeeded, CombatAI::ActionFailure::None);
    if (!bSearchGoal)
    {
        const int32 Index = SearchCycle.Index;
        // Fixed bounded proposals, validated by the same collision-based navigator.
        // Nearby fallback points originate at actual feet, including after displacement.
        const FVector Center = Index >= 5 ? Feet() : SearchAnchor;
        const float Radius = Index >= 5 ? 240.f : FMath::Clamp(Tuning.SearchRadius, 200.f, 650.f);
        const int32 Quarter = (Index - 1) % 4;
        SearchGoal = Index == 0 ? SearchAnchor : Center + SearchForward.RotateAngleAxis(90.f * Quarter, FVector::UpVector) * Radius;
        SearchLook = Index == 0 ? LastKnownAim : SearchGoal + FVector(0,0,140);
        bSearchGoal = true; FailedAttempts = 0; NextRepath = 0;
    }
    const bool Arrived = FVector::Dist2D(Feet(), SearchGoal) <= 85.f && FMath::Abs(Feet().Z - SearchGoal.Z) <= 40.f;
    const bool Suppressed = MoveBackoff.Blocks(SearchGoal.X, SearchGoal.Y, Now) || SearchBackoff.Blocks(SearchGoal.X, SearchGoal.Y, Now);
    if (Arrived || Suppressed || !FollowPath(SearchGoal, 85.f, Now, CombatAI::MovePurpose::Search))
    {
        if (Arrived)
        {
            FinishAction(Action.Token, CombatAI::ActionStatus::Succeeded, CombatAI::ActionFailure::None);
            RecordPath(CombatAI::PathOutcome::Arrived, TEXT("search inspection point reached"));
            // Inspect outward from the reached point, rather than aim vertically at our feet.
            const float SectorAngle = SearchCycle.Index == 0 ? 0.f : 90.f * ((SearchCycle.Index - 1) % 4);
            SearchLook = Feet() + SearchForward.RotateAngleAxis(SectorAngle, FVector::UpVector) * 400.f + FVector(0,0,140);
        }
        else if (!Suppressed) SearchBackoff.Set(SearchGoal.X, SearchGoal.Y, Now + FMath::Clamp(Tuning.RetryCooldown, 1.f, 30.f));
        ClearIntent();
        // Retain this sector during the dwell, then select the next bounded proposal.
        E->SetRifleAimTarget(SearchLook);
        ObserveUntil = Now + (Arrived ? FMath::Clamp(Tuning.SearchSeconds, .5f, 5.f) : .8f);
        SearchCycle.Advance(Now, .8, FMath::Clamp(Tuning.RetryCooldown, 1.f, 30.f));
        bSearchGoal = false;
        EnsureAction(CombatAI::ActionKind::Observe, Now);
    }
}

void UEnemyCombatComponent::AdvanceCombat(float DeltaSeconds)
{
    CaptureDeltaSeconds = DeltaSeconds;
    auto* E = Enemy();
    if (!bEnabled || !E || State == EEnemyCombatState::Disabled) return;
    // Terminal/authority safety precedes readiness and every possible side effect.
    if (E->IsDead()) { if (State != EEnemyCombatState::Dead) SuspendForPhysics(true); return; }
    if (E->Authority != EGASPEnemyAuthority::Locomotion)
    { if (State != EEnemyCombatState::Recovery) SuspendForPhysics(false); return; }
    if (!E->IsReady() || !IsValid(E->Foundation)) { ClearIntent(CombatAI::ActionFailure::Authority); return; }
    const double Now = GetWorld()->GetTimeSeconds();
    if (State == EEnemyCombatState::Recovery)
    {
        MoveBackoff = {}; WeaponBackoff = {}; SearchBackoff = {};
        BeginSearch(TEXT("locomotion returned; replan from actual feet"));
        NextSight = 0;
        NextShot = ReadyAt = Now + FMath::Clamp(Tuning.AimSeconds, .1f, 5.f);
    }
    // Perception is independent of tactical deadlines, including reload/backoff.
    if (Now >= NextSight)
    {
        ObservePlayer();
        NextSight = Now + FMath::Clamp(Tuning.SightInterval, .05f, 1.f);
        RecordTrace(CombatAI::Event::DecisionInput, TEXT("post-perception persistent policy input"));
    }
    Action.Update(Action.Token, Now);
    const bool MoveSuppressed = MoveBackoff.Blocks(LastKnownGround.X, LastKnownGround.Y, Now);
    const bool WeaponSuppressed = WeaponBackoff.Blocks(LastKnownGround.X, LastKnownGround.Y, Now);
    const float AttackRange = FMath::Clamp(Tuning.AttackRange, 150.f, 5000.f);
    const float Distance = FVector::Dist2D(Feet(), LastKnownGround);
    // A failed route cannot suppress an already viable in-range weapon action.
    const bool CanReacquire = !WeaponSuppressed && (!MoveSuppressed || Distance <= AttackRange);
    if (bTargetVisible && CanReacquire && (State == EEnemyCombatState::Idle || State == EEnemyCombatState::Search || State == EEnemyCombatState::Blocked))
    {
        ClearIntent(); FailedAttempts = 0; NextRepath = 0; bReposition = false;
        ObstructionAttempts = 0; ObstructedSince = -1; ++Acquisitions;
        ChangeState(EEnemyCombatState::Acquire, TEXT("player visibly acquired"));
        ReadyAt = Now + FMath::Clamp(Tuning.AcquireSeconds, .1f, 5.f);
    }
    if (State == EEnemyCombatState::Idle)
    { E->StopMovementCommand(); E->SetRifleStance(EGASPALSRifleStance::Ready); return; }
    if (State == EEnemyCombatState::Reload)
    {
        E->StopMovementCommand(); E->SetRifleStance(EGASPALSRifleStance::Ready);
        E->SetRifleAimTarget(LastKnownAim);
        if (!E->IsRifleHeld() || !E->bRightHandOccupied)
        { FailTactic(TEXT("reload lost weapon capability"), CombatAI::ActionFailure::Weapon, true); return; }
        if (Now < ReadyAt) return;
        // No ammo commit from an interrupted or replaced request, even in the same generation.
        if (!FinishAction(ReloadRequest, CombatAI::ActionStatus::Succeeded, CombatAI::ActionFailure::None))
        { BeginSearch(TEXT("stale reload discarded")); return; }
        Magazine = FMath::Clamp(Tuning.MagazineCapacity, 1, 60); ++Reloads;
        if (!bTargetVisible) { BeginSearch(TEXT("reload complete; continue search")); return; }
        ChangeState(EEnemyCombatState::Aim, TEXT("timed reload complete; unlimited reserve"));
        ReadyAt = NextShot = Now + FMath::Clamp(Tuning.AimSeconds, .1f, 5.f);
    }
    if (!bTargetVisible)
    {
        if (State != EEnemyCombatState::Search) BeginSearch(TEXT("lost sight; persistent local search"));
        AdvanceSearch(Now); return;
    }
    if (State == EEnemyCombatState::Search && !CanReacquire)
    { AdvanceSearch(Now); return; }
    E->SetRifleAimTarget(LastKnownAim); E->SetCrouchCommand(false);
    if (!E->IsRifleHeld() || !E->bRightHandOccupied)
    { FailTactic(TEXT("no held usable weapon"), CombatAI::ActionFailure::Weapon, true); return; }
    if (State == EEnemyCombatState::Acquire)
    {
        E->StopMovementCommand(); E->SetRifleStance(EGASPALSRifleStance::Ready);
        EnsureAction(CombatAI::ActionKind::Observe, Now);
        if (Now < ReadyAt) return;
        FinishAction(Action.Token, CombatAI::ActionStatus::Succeeded, CombatAI::ActionFailure::None);
        ChangeState(EEnemyCombatState::Pursue, TEXT("acquisition delay complete"));
    }
    if (State == EEnemyCombatState::Pursue)
    {
        if (Now - StateStarted > FMath::Clamp(Tuning.PursuitSeconds, 2.f, 60.f))
        { FailTactic(TEXT("pursuit action deadline; alert retained"), CombatAI::ActionFailure::Timeout, false); return; }
        // If closing distance failed but this observation is already in firing range,
        // brake and aim here instead of reacquiring and retrying the suppressed route.
        const float StopRange = bReposition ? 85.f : (MoveSuppressed ? AttackRange : AttackRange * .82f);
        E->SetRifleStance(EGASPALSRifleStance::Ready);
        if (Distance > StopRange)
        {
            if (MoveSuppressed || !FollowPath(LastKnownGround, StopRange, Now, CombatAI::MovePurpose::Pursuit))
                FailTactic(TEXT("pursuit route unavailable; inspect alternatives"), CombatAI::ActionFailure::Route, false);
            return;
        }
        FinishAction(Action.Token, CombatAI::ActionStatus::Succeeded, CombatAI::ActionFailure::None);
        RecordPath(CombatAI::PathOutcome::Arrived, TEXT("pursuit attack region reached"));
        ClearIntent(); E->SetRifleAimTarget(LastKnownAim); bReposition = false;
        ChangeState(EEnemyCombatState::Aim, TEXT("attack distance reached; braking into aim"));
        ReadyAt = FMath::Max(NextShot, Now + FMath::Clamp(Tuning.AimSeconds, .1f, 5.f));
    }
    if (Distance > AttackRange * 1.15f)
    {
        ClearIntent(); NextRepath = 0; FailedAttempts = 0;
        ChangeState(EEnemyCombatState::Pursue, TEXT("visible player left firing range")); return;
    }
    E->StopMovementCommand(); E->SetRifleStance(EGASPALSRifleStance::Aim);
    if (Magazine <= 0)
    {
        ClearIntent();
        ReloadRequest = EnsureAction(CombatAI::ActionKind::Reload, Now);
        ChangeState(EEnemyCombatState::Reload, TEXT("empty magazine"));
        ReadyAt = Now + FMath::Clamp(Tuning.ReloadSeconds, .3f, 15.f); return;
    }
    if (State != EEnemyCombatState::Burst) EnsureAction(CombatAI::ActionKind::Aim, Now);
    if (Now < ReadyAt || Now < NextShot) return;
    FVector Muzzle, Direction; bool bObstructed;
    if (!CanShoot(Muzzle, Direction, bObstructed))
    {
        if (bObstructed)
        {
            if (ObstructedSince < 0) ObstructedSince = Now;
            ++ObstructionAttempts;
            if (ObstructionAttempts >= 3 || Now - ObstructedSince > 6.f)
            { FailTactic(TEXT("muzzle obstruction; observe and reposition"), CombatAI::ActionFailure::Obstruction, true); return; }
            FinishAction(Action.Token, CombatAI::ActionStatus::Failed, CombatAI::ActionFailure::Obstruction);
            ClearIntent(); NextRepath = 0; FailedAttempts = 0; bReposition = true;
            ChangeState(EEnemyCombatState::Pursue, TEXT("muzzle corridor obstructed"));
        }
        else if (Now - StateStarted > 6.f)
            FailTactic(TEXT("aim did not settle; alert retained"), CombatAI::ActionFailure::Timeout, true);
        return;
    }
    if (State != EEnemyCombatState::Burst)
    {
        FinishAction(Action.Token, CombatAI::ActionStatus::Succeeded, CombatAI::ActionFailure::None);
        BurstRemaining = FMath::Clamp(Tuning.BurstSize, 1, 8);
        EnsureAction(CombatAI::ActionKind::Burst, Now);
        ChangeState(EEnemyCombatState::Burst, TEXT("settled rifle and clear observed target"));
    }
    if (!Fire(Now, Action.Token))
    {
        if (!bTargetVisible) BeginSearch(TEXT("sight lost at launch; burst canceled"));
        else FailTactic(TEXT("launch request failed"), CombatAI::ActionFailure::Weapon, true);
        return;
    }
    if (BurstRemaining <= 0)
    {
        FinishAction(Action.Token, CombatAI::ActionStatus::Succeeded, CombatAI::ActionFailure::None);
        ChangeState(EEnemyCombatState::Aim, TEXT("burst pause"));
        ReadyAt = Now + FMath::Clamp(Tuning.BurstPause, .1f, 10.f);
    }
}
