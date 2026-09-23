#include "EnemyCombatComponent.h"
#include "GASPEnemyFixture.h"
#include "Engine/World.h"

void UEnemyCombatComponent::BeginSearch(const TCHAR* Why, bool bRestart)
{
    ClearIntent(); NextRepath = 0; FailedAttempts = 0; bReposition = false;
    ResetTactics(false);
    if (bRestart)
    {
        SearchAnchor = LastKnownGround;
        SearchForward = (LastKnownGround - Feet()).GetSafeNormal2D();
        if (SearchForward.IsNearlyZero()) SearchForward = HomeFacing.Vector().GetSafeNormal2D();
        SearchLook = Feet() + SearchForward*400 + FVector(0,0,140);
    }
    const double Now = GetWorld()->GetTimeSeconds();
    Assignment.Assign(EncounterGeneration, CombatAI::SelectObjective({Memory.Alert, Memory.HasObservation, false, true}), SightEventId, Now);
    HoldStartedAt = Now;
    ChangeState(Memory.Alert ? EEnemyCombatState::Search : EEnemyCombatState::Idle, Why);
}

void UEnemyCombatComponent::FailTactic(const TCHAR* Why, CombatAI::ActionFailure Failure, bool bWeapon)
{
    FinishAction(Action.Token, CombatAI::ActionStatus::Failed, Failure);
    auto& Backoff = bWeapon ? WeaponBackoff : MoveBackoff;
    Backoff.Set(LastKnownGround.X, LastKnownGround.Y,
        GetWorld()->GetTimeSeconds() + FMath::Clamp(Tuning.RetryCooldown, 1.f, 30.f));
    BeginSearch(Why);
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
    if (!E->IsReady() || !IsValid(E->Foundation))
    { if (State != EEnemyCombatState::Recovery) SuspendForPhysics(false); return; }
    const double Now = GetWorld()->GetTimeSeconds();
    if (State == EEnemyCombatState::Recovery)
    {
        MoveBackoff = {}; WeaponBackoff = {};
        BeginSearch(TEXT("locomotion returned; replan from actual feet"));
        NextSight = 0;
        Gates.AimUntil = Now + FMath::Clamp(Tuning.AimSeconds, .1f, 5.f);
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
    if (bTargetVisible && ContactAt > ContactDecisionAt) ContactDecisionAt = Now;
    if (bTargetVisible && (State == EEnemyCombatState::Idle || State == EEnemyCombatState::Search || State == EEnemyCombatState::Blocked))
    {
        // Fresh known contact cancels scanning, ordinary holds and old routes on
        // this decision tick, even when a weapon/route backoff still blocks attack.
        if (CanReacquire || Assignment.Objective != CombatAI::TacticalObjective::Engage)
        {
            ClearIntent(); ResetTactics(false); FailedAttempts = 0; NextRepath = 0; bReposition = false;
            Assignment.Assign(EncounterGeneration, CombatAI::SelectObjective({Memory.Alert, Memory.HasObservation, true, true}), SightEventId, Now);
            ContactDecisionAt = Now;
            ObstructionAttempts = 0; ObstructedSince = -1; ++Acquisitions;
            if (CanReacquire)
                ChangeState(EEnemyCombatState::Acquire, Contact == CombatAI::ContactKind::Initial ?
                    TEXT("initial contact response") : TEXT("known contact interrupts observation"));
        }
    }
    if (State == EEnemyCombatState::Idle)
    { E->StopMovementCommand(); E->SetRifleStance(EGASPALSRifleStance::Ready); return; }
    if (State == EEnemyCombatState::Reload)
    {
        E->StopMovementCommand(); E->SetRifleStance(EGASPALSRifleStance::Ready);
        E->SetRifleAimTarget(LastKnownAim);
        if (!E->IsRifleHeld() || !E->bRightHandOccupied)
        { FailTactic(TEXT("reload lost weapon capability"), CombatAI::ActionFailure::Weapon, true); return; }
        if (Now < Gates.ReloadUntil) return;
        // No ammo commit from an interrupted or replaced request, even in the same generation.
        if (!FinishAction(ReloadRequest, CombatAI::ActionStatus::Succeeded, CombatAI::ActionFailure::None))
        { BeginSearch(TEXT("stale reload discarded")); return; }
        Magazine = FMath::Clamp(Tuning.MagazineCapacity, 1, 60); ++Reloads;
        Gates.ReloadUntil = 0; ReloadRequest = {};
        if (!bTargetVisible) { BeginSearch(TEXT("reload complete; continue search")); return; }
        ChangeState(EEnemyCombatState::Aim, TEXT("timed reload complete; unlimited reserve"));
        Gates.AimUntil = Now + FMath::Clamp(Tuning.AimSeconds, .1f, 5.f);
    }
    if (!bTargetVisible)
    {
        if (State != EEnemyCombatState::Search || Assignment.Objective != CombatAI::TacticalObjective::ProtectedObservation)
            BeginSearch(TEXT("lost sight; protected observation from permitted evidence"));
        AdvanceSearch(Now); return;
    }
    if (State == EEnemyCombatState::Search && !CanReacquire)
    {
        E->StopMovementCommand(); E->SetRifleStance(EGASPALSRifleStance::Aim);
        E->SetRifleAimTarget(LastKnownAim); EnsureAction(CombatAI::ActionKind::Observe, Now);
        TacticalReason = WeaponSuppressed ? TEXT("known visible contact; weapon backoff") : TEXT("known visible contact; route backoff");
        return;
    }
    E->SetRifleAimTarget(LastKnownAim); E->SetCrouchCommand(false);
    if (!E->IsRifleHeld() || !E->bRightHandOccupied)
    { FailTactic(TEXT("no held usable weapon"), CombatAI::ActionFailure::Weapon, true); return; }
    if (State == EEnemyCombatState::Acquire)
    {
        E->StopMovementCommand(); E->SetRifleStance(EGASPALSRifleStance::Ready);
        EnsureAction(CombatAI::ActionKind::Observe, Now);
        if (Now < Gates.ContactUntil) return;
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
        Gates.AimUntil = Now + FMath::Clamp(Tuning.AimSeconds, .1f, 5.f);
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
        Gates.ReloadUntil = Now + FMath::Clamp(Tuning.ReloadSeconds, .3f, 15.f); return;
    }
    if (State != EEnemyCombatState::Burst) EnsureAction(CombatAI::ActionKind::Aim, Now);
    if (Now < Gates.ReadyAt(NextShot)) return;
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
        Gates.PauseUntil = Now + FMath::Clamp(Tuning.BurstPause, .1f, 10.f);
    }
}
