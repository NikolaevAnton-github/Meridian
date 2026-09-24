#include "EnemyCombatComponent.h"
#include "GASPEnemyFixture.h"
#include "Engine/World.h"

void UEnemyCombatComponent::BeginSearch(const TCHAR* Why, bool bRestart)
{
    ClearIntent(); NextRepath=0; FailedAttempts=0;
    ResetTactics(false);
    if (bRestart)
    {
        SearchAnchor=LastKnownGround;
        SearchForward=(LastKnownGround-Feet()).GetSafeNormal2D();
        if (SearchForward.IsNearlyZero()) SearchForward=HomeFacing.Vector().GetSafeNormal2D();
        SearchLook=Feet()+SearchForward*400+FVector(0,0,140);
    }
    const double Now=GetWorld()->GetTimeSeconds();
    Assignment.Assign(EncounterGeneration,CombatAI::SelectObjective({Memory.Alert,Memory.HasObservation,false,true}),IntentEvidenceId,Now);
    HoldStartedAt=Now;
    ChangeState(Memory.Alert ? EEnemyCombatState::Search : EEnemyCombatState::Idle,Why);
}
void UEnemyCombatComponent::FailTactic(const TCHAR* Why, CombatAI::ActionFailure Failure, bool bWeapon)
{
    FinishAction(Action.Token,CombatAI::ActionStatus::Failed,Failure);
    auto& Backoff=bWeapon ? WeaponBackoff : MoveBackoff;
    Backoff.Set(LastKnownGround.X,LastKnownGround.Y,GetWorld()->GetTimeSeconds()+FMath::Clamp(Tuning.RetryCooldown,1.f,30.f));
    BeginSearch(Why);
}

bool UEnemyCombatComponent::AdvanceWeapon(double Now, bool bFromCover)
{
    auto* E=Enemy();
    if (bFromCover) E->StopMovementCommand();
    E->SetRifleStance(EGASPALSRifleStance::Aim); E->SetRifleAimTarget(LastKnownAim);
    if (E->GetFireMotion().Gate()!=CombatAI::MotionGate::Ready)
    {
        LastFireGate=CombatAI::FireGate::Motion;
        FinishAction(Action.Token,CombatAI::ActionStatus::Canceled,CombatAI::ActionFailure::Authority);
        BurstRemaining=0; E->SetRifleStance(EGASPALSRifleStance::Ready);
        ChangeState(EEnemyCombatState::Aim,TEXT("unsupported achieved motion; cancel pending burst and lower rifle"));
        Gates.AimUntil=FMath::Max(Gates.AimUntil,Now+Context.Weapon.Aim);
        return false;
    }
    if (Magazine<=0)
    {
        if (bFromCover) { ReturnToCover(Now,TEXT("empty magazine; reload after protected return"),false,false); return false; }
        ClearIntent(); ReloadRequest=EnsureAction(CombatAI::ActionKind::Reload,Now);
        Gates.ReloadUntil=Now+FMath::Clamp(Tuning.ReloadSeconds,.3f,15.f);
        ChangeState(EEnemyCombatState::Reload,TEXT("empty magazine; guarded reload")); return false;
    }
    if (State!=EEnemyCombatState::Burst) EnsureAction(CombatAI::ActionKind::Aim,Now);
    if (Now<Gates.ReadyAt(NextShot)) return false;
    FVector Muzzle,Direction; bool Obstructed=false;
    if (!CanShoot(Muzzle,Direction,Obstructed))
    {
        if (Obstructed)
        {
            RangeIntent=CombatAI::SelectRangeIntent(Context,FVector::Dist2D(Feet(),LastKnownGround),true);
            if (bFromCover) ReturnToCover(Now,TEXT("actual muzzle blocked at exposure; reject this side"),true,true);
            else
            {
                if (ObstructedSince<0) ObstructedSince=Now;
                ObstructionValidUntil=Now+.5;
                // Keep this position and let the bounded geometry scan find a lane.
                // Never pursue the remembered target position to fix a blocked muzzle.
                if (State==EEnemyCombatState::Burst)
                { FinishAction(Action.Token,CombatAI::ActionStatus::Canceled,CombatAI::ActionFailure::Obstruction); BurstRemaining=0; }
                ChangeState(EEnemyCombatState::Aim,TEXT("muzzle blocked; seek protected firing side while holding range"));
                TacticalReason=TEXT("muzzle blocked; bounded alternate cover scan, no charge");
                if (Now-ObstructedSince>4.5 && !bCoverScan)
                { WeaponBackoff.Set(LastKnownGround.X,LastKnownGround.Y,Now+1); ObstructedSince=Now; }
            }
        }
        else if (Now-StateStarted>3 && !bFromCover)
        { WeaponBackoff.Set(LastKnownGround.X,LastKnownGround.Y,Now+.5); ChangeState(EEnemyCombatState::Aim,TEXT("physical aim pending; hold actual feet")); }
        return false;
    }
    if (State!=EEnemyCombatState::Burst)
    {
        FinishAction(Action.Token,CombatAI::ActionStatus::Succeeded,CombatAI::ActionFailure::None);
        BurstRemaining=Context.Weapon.Burst;
        if (bFromCover) SetCoverPhase(CombatAI::CoverPhase::Firing,Now,TEXT("fresh visible contact at achieved exposure"));
        EnsureAction(CombatAI::ActionKind::Burst,Now);
        ChangeState(EEnemyCombatState::Burst,TEXT("settled rifle and current clear target"));
    }
    if (!Fire(Now,Action.Token))
    {
        if (bFromCover) ReturnToCover(Now,TEXT("launch veto; cancel burst and return"),true,bTargetVisible);
        else if (!bTargetVisible) BeginSearch(TEXT("launch sight lost; cancel burst"));
        else if (Now<Gates.ReadyAt(NextShot))
        {
            FinishAction(Action.Token,CombatAI::ActionStatus::Canceled,CombatAI::ActionFailure::Sight); BurstRemaining=0;
            ChangeState(EEnemyCombatState::Aim,TEXT("fresh launch observation requires short response gate"));
        }
        else FailTactic(TEXT("launch request failed"),CombatAI::ActionFailure::Weapon,true);
        return false;
    }
    if (BurstRemaining<=0)
    {
        FinishAction(Action.Token,CombatAI::ActionStatus::Succeeded,CombatAI::ActionFailure::None);
        Gates.PauseUntil=Now+Context.Weapon.Rest;
        if (bFromCover) { ++CoverBursts; ReturnToCover(Now,TEXT("finite burst complete; return to protection"),false,false); }
        else ChangeState(EEnemyCombatState::Aim,TEXT("finite burst pause"));
    }
    return true;
}

void UEnemyCombatComponent::AdvanceCombat(float DeltaSeconds)
{
    CaptureDeltaSeconds=DeltaSeconds;
    auto* E=Enemy();
    if (!bEnabled || !E || State==EEnemyCombatState::Disabled) return;
    if (E->IsDead()) { if (State!=EEnemyCombatState::Dead) SuspendForPhysics(true); return; }
    if (E->Authority!=EGASPEnemyAuthority::Locomotion || !E->IsReady() || !IsValid(E->Foundation))
    { if (State!=EEnemyCombatState::Recovery) SuspendForPhysics(false); return; }
    const double Now=GetWorld()->GetTimeSeconds();
    RefreshTacticalContext(Now);
    if (!Context.WeaponUsable || !Context.Weapon.Valid())
    {
        ClearIntent(CombatAI::ActionFailure::Weapon); ResetTactics(false);
        ObstructedSince=-1; ObstructionValidUntil=0; RangeIntent=CombatAI::RangeIntent::NoWeapon;
        ChangeState(EEnemyCombatState::Blocked,TEXT("weapon unavailable; action ownership and pose requests cleared"));
        return;
    }
    if (State==EEnemyCombatState::Recovery)
    {
        MoveBackoff={}; WeaponBackoff={};
        BeginSearch(TEXT("locomotion returned; replan from actual feet")); NextSight=0;
        Gates.AimUntil=Now+Context.Weapon.Aim;
    }
    if (Now>=NextSight)
    {
        ObservePlayer(); NextSight=Now+FMath::Clamp(Tuning.SightInterval,.05f,1.f);
        RecordTrace(CombatAI::Event::DecisionInput,TEXT("post-perception weapon and tactical context"));
    }
    Action.Update(Action.Token,Now);
    if (bTargetVisible && ContactAt>ContactDecisionAt) ContactDecisionAt=Now;
    // Own ducking must not pass through search/reacquire cancellation. Sounds are
    // retained in Knowledge; the active cover action consumes its frozen evidence.
    if (AdvanceCover(Now)) return;
    ApplyEvidenceIntent(Now);
    const double Distance=FVector::Dist2D(Feet(),LastKnownGround);
    RefreshObstruction(Now,Distance);
    RangeIntent=CombatAI::SelectRangeIntent(Context,Distance,ObstructedSince>=0);
    const bool WeaponSuppressed=WeaponBackoff.Blocks(LastKnownGround.X,LastKnownGround.Y,Now);
    if (bTargetVisible && (State==EEnemyCombatState::Idle || State==EEnemyCombatState::Search || State==EEnemyCombatState::Blocked))
    {
        ClearIntent(); ResetTactics(false); FailedAttempts=0; NextRepath=0;
        Assignment.Assign(EncounterGeneration,CombatAI::TacticalObjective::Engage,IntentEvidenceId,Now);
        ++Acquisitions; ContactDecisionAt=Now;
        // Response and aim overlap; raise the rifle while the short reaction is paid.
        Gates.AimUntil=Now+Context.Weapon.Aim;
        ChangeState(EEnemyCombatState::Acquire,TEXT("current contact; concurrent reaction and aim"));
    }
    if (State==EEnemyCombatState::Idle) { E->StopMovementCommand(); return; }
    if (State==EEnemyCombatState::Reload)
    {
        E->StopMovementCommand(); E->SetRifleStance(EGASPALSRifleStance::Ready);
        if (Now<Gates.ReloadUntil) return;
        if (!FinishAction(ReloadRequest,CombatAI::ActionStatus::Succeeded,CombatAI::ActionFailure::None))
        { BeginSearch(TEXT("stale reload discarded")); return; }
        Magazine=FMath::Clamp(Tuning.MagazineCapacity,1,60); ++Reloads;
        Gates.ReloadUntil=0; ReloadRequest={};
        if (!bTargetVisible) { BeginSearch(TEXT("reload complete; continue evidence-based observation")); return; }
        ChangeState(EEnemyCombatState::Aim,TEXT("timed reload complete")); Gates.AimUntil=Now+Context.Weapon.Aim;
    }
    // Scans coexist with stationary engagement. They cannot replace a running
    // burst, reset weapon deadlines, or consume a live concealed target transform.
    if (!bTargetVisible && State==EEnemyCombatState::Burst)
    {
        FinishAction(Action.Token,CombatAI::ActionStatus::Canceled,CombatAI::ActionFailure::Sight);
        BurstRemaining=0; Gates.PauseUntil=FMath::Max(Gates.PauseUntil,Now+Context.Weapon.Rest);
        ChangeState(EEnemyCombatState::Aim,TEXT("direct burst lost useful sight; preserve scan and rest"));
    }
    if (MobilePhase!=CombatAI::MobilePhase::Strafe && MobilePhase!=CombatAI::MobilePhase::Approach) AdvanceCoverScan(Now);
    if (CoverPhase!=CombatAI::CoverPhase::None) { AdvanceCover(Now); return; }
    if (!bTargetVisible)
    {
        if (MobilePhase==CombatAI::MobilePhase::Strafe || MobilePhase==CombatAI::MobilePhase::Approach)
            ClearMovement(CombatAI::ActionFailure::Sight);
        else E->StopMovementCommand();
        if (bCoverScan)
        { E->SetRifleAimTarget(CoverThreatAim); E->SetRifleStance(EGASPALSRifleStance::Aim); return; }
        if (Knowledge.RetainsContact(Now) && Assignment.Objective==CombatAI::TacticalObjective::Engage)
        { E->SetRifleAimTarget(LastKnownAim); E->SetRifleStance(EGASPALSRifleStance::Aim); return; }
        if (State!=EEnemyCombatState::Search) BeginSearch(TEXT("no current sight; protected observation"));
        AdvanceSearch(Now); return;
    }
    E->SetCrouchCommand(false); E->SetRifleAimTarget(LastKnownAim); E->SetRifleStance(EGASPALSRifleStance::Aim);
    if (State==EEnemyCombatState::Acquire)
    {
        E->StopMovementCommand(); EnsureAction(CombatAI::ActionKind::Aim,Now);
        if (Now<Gates.ContactUntil) return;
        ChangeState(EEnemyCombatState::Aim,TEXT("short response paid; useful existing range"));
    }
    AdvanceMobile(Now,Distance);
    if (WeaponSuppressed) { TacticalReason=TEXT("bounded weapon retry; cover scan remains available"); return; }
    if (Distance>Context.Weapon.EffectiveRange) return;
    AdvanceWeapon(Now,false);
}
