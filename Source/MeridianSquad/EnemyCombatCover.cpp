#include "EnemyCombatComponent.h"
#include "GASPEnemyFixture.h"
#include "CombatProjectileWorld.h"
#include "Components/CapsuleComponent.h"
#include "Components/PrimitiveComponent.h"
#include "DefaultMovementSet/CharacterMoverComponent.h"
#include "DefaultMovementSet/Settings/StanceSettings.h"
#include "MoveLibrary/MovementUtils.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"

CombatAI::WeaponProfile UEnemyCombatComponent::WeaponProfile() const
{
    CombatAI::WeaponProfile P;
    P.EffectiveRange = FMath::Clamp(Tuning.AttackRange, 150.f, 7000.f);
    P.PreferredRange = FMath::Clamp<double>(Tuning.PreferredRange, 100, P.EffectiveRange);
    P.AdvanceStep = FMath::Clamp(Tuning.AdvanceStep, 100.f, 600.f);
    P.Reaction = FMath::Clamp(Tuning.AcquireSeconds, 0.f, 5.f);
    P.Aim = FMath::Clamp(Tuning.AimSeconds, 0.f, 5.f);
    P.Interval = FMath::Clamp(Tuning.ShotInterval, .08f, 5.f);
    P.Rest = FMath::Clamp(Tuning.BurstPause, .1f, 10.f);
    P.Burst = FMath::Clamp(Tuning.BurstSize, 1, 8);
    return P;
}
void UEnemyCombatComponent::ReceiveTargetHealth(const CombatAI::HealthKnowledge& Evidence)
{
    if (Evidence.Usable(EncounterGeneration, 1, GetWorld()->GetTimeSeconds())) TargetHealthEvidence = Evidence;
}
void UEnemyCombatComponent::RefreshTacticalContext(double Now)
{
    const auto* E = Enemy();
    Context = {}; Context.Weapon = WeaponProfile();
    Context.WeaponUsable = E && E->IsRifleHeld() && E->bRightHandOccupied;
    Context.SelfHealthKnown = E && FMath::IsFinite(E->Health) && FMath::IsFinite(E->MaxHealth) && E->MaxHealth > 0;
    if (Context.SelfHealthKnown) Context.SelfHealth = FMath::Clamp(double(E->Health/E->MaxHealth), 0.0, 1.0);
    if (TargetHealthEvidence.Usable(EncounterGeneration, 1, Now)) Context.TargetHealth = TargetHealthEvidence;
    if (Now >= NextAllyRefresh)
    {
        AllyRoster = {}; NextAllyRefresh = Now + 1;
        // This encounter's friendly roster is fixtures, never their adopted pawns.
        // No positions, enemy health or privileged target information is sampled.
        if (ACombatProjectileWorld::Find(GetWorld()))
        {
            AllyRoster.Known = true; int32 Inspected = 0;
            for (TActorIterator<AGASPEnemyFixture> It(GetWorld()); It; ++It)
            {
                if (++Inspected > 16) { AllyRoster = {}; break; }
                const auto* Ally = *It;
                if (Ally == E || Ally->IsDead() || !Ally->Combat || !Ally->Combat->bEnabled ||
                    Ally->Combat->State == EEnemyCombatState::Disabled ||
                    !Ally->IsReady() || Ally->Authority != EGASPEnemyAuthority::Locomotion) continue;
                ++AllyRoster.Available;
                const auto P = Ally->Combat->WeaponProfile();
                if (P.Valid() && Ally->IsRifleHeld() && Ally->bRightHandOccupied)
                    for (int32 I = 0; I < 3; ++I) if (P.Capabilities & (1u << I)) ++AllyRoster.Capable[I];
            }
        }
    }
    Context.Allies = AllyRoster;
}

bool UEnemyCombatComponent::PoseCapsuleSize(bool bCrouched, float& Radius, float& HalfHeight) const
{
    const auto* E = Enemy();
    if (!E || !E->Foundation) return false;
    const auto* Mover = E->Foundation->FindComponentByClass<UCharacterMoverComponent>();
    const auto* Original = UMovementUtils::GetOriginalComponentType<UCapsuleComponent>(E->Foundation);
    const auto* Current = E->Foundation->FindComponentByClass<UCapsuleComponent>();
    const auto* Settings = Mover ? Mover->FindSharedSettings<UStanceSettings>() : nullptr;
    if (!Original || !Current || !Settings) return false;
    Radius = Current->GetScaledCapsuleRadius();
    // Match Mover's actual stance expansion contract, including its original capsule.
    HalfHeight = bCrouched ? Settings->CrouchHalfHeight : Original->GetScaledCapsuleHalfHeight();
    return FMath::IsFinite(HalfHeight) && Radius > 0 && HalfHeight >= Radius;
}
bool UEnemyCombatComponent::CoverCapsule(FVector Ground, bool bCrouched)
{
    FVector Supported; CombatAI::PositionRejection Why;
    return TacticalGround(Ground, Supported, Why, bCrouched ? 1 : 0) && FMath::Abs(Supported.Z-Ground.Z) <= 8;
}
bool UEnemyCombatComponent::CoverWalk(FVector From, FVector To)
{ return TacticalWalk(From, To, 1); }
bool UEnemyCombatComponent::RefreshCoverThreat(double Now)
{
    const bool Valid=CombatAI::CoverEvidenceValid(Now,Memory.LastSeen,CoverStarted,
        FVector::Dist2D(CoverThreatGround,LastKnownGround));
    // Only successful direct sight can refine an active plan's threat geometry.
    // Small observed changes force revalidation; a large change abandons commitment.
    if (Valid && bTargetVisible)
    {
        if (!CoverThreatGround.Equals(LastKnownGround,1) || !CoverThreatAim.Equals(LastKnownAim,1)) CoverValidateAt=0;
        CoverThreatGround=LastKnownGround; CoverThreatAim=LastKnownAim;
    }
    return Valid;
}
bool UEnemyCombatComponent::CoverProtected(FVector Ground)
{
    int32 Blocked = 0;
    for (float Height : {60.f, 85.f, 100.f})
    {
        FHitResult Hit;
        if (TacticalTrace(Ground+FVector(0,0,Height), CoverThreatAim, Hit) && Hit.Distance < 180 &&
            Hit.GetComponent() && Hit.GetComponent()->GetCollisionResponseToChannel(ECC_Pawn) == ECR_Block &&
            FMath::Abs(Hit.ImpactNormal.Z) < .4) ++Blocked;
    }
    return Blocked == 3;
}
bool UEnemyCombatComponent::CoverLane(FVector Ground)
{
    FHitResult Hit;
    if (TacticalTrace(Ground+FVector(0,0,150), CoverThreatAim, Hit)) return false;
    FCollisionQueryParams Query(SCENE_QUERY_STAT(EnemyCoverLane), false);
    FCollisionResponseParams StaticOnly(ECR_Ignore);
    StaticOnly.CollisionResponse.SetResponse(ECC_WorldStatic, ECR_Block);
    const FVector Root = Ground+FVector(0,0,125);
    const FVector Direction = (CoverThreatAim-Root).GetSafeNormal();
    ++TacticalQueryCount;
    if (GetWorld()->SweepSingleByChannel(Hit, Root, Root+Direction*120, FQuat::Identity, ECC_Visibility,
        FCollisionShape::MakeSphere(10), Query, StaticOnly)) return false;
    ++TacticalQueryCount;
    return !GetWorld()->SweepSingleByChannel(Hit, Root, CoverThreatAim, FQuat::Identity, ECC_Visibility,
        FCollisionShape::MakeSphere(1), Query, StaticOnly);
}
UEnemyCombatComponent::FCoverOption UEnemyCombatComponent::AssessCoverOption(FVector Anchor, FVector Pose, CombatAI::CoverSide Side)
{
    FCoverOption O; O.Anchor=Anchor; O.Pose=Pose;
    auto& F=O.Features; F.Side=Side;
    F.Travel=FVector::Dist2D(ScanOrigin,Anchor); F.ExposureTravel=FVector::Dist2D(Anchor,Pose);
    F.Protected=CoverProtected(Anchor); F.Protection=F.Protected ? 1 : 0;
    F.AnchorClear=CoverCapsule(Anchor,true);
    F.PoseClear=CoverCapsule(Pose,false);
    F.InRange=FVector::Dist2D(Pose,CoverThreatGround) <= Context.Weapon.EffectiveRange;
    // All geometry is only a proposal. The actual actor's head and barrel gate launch.
    if (F.Protected && F.AnchorClear && F.PoseClear && F.InRange)
    {
        F.Lane=CoverLane(Pose);
        if (F.Lane)
        {
            F.Outbound=CoverWalk(Anchor,Pose);
            F.Return=CoverWalk(Pose,Anchor);
        }
    }
    O.Score=CombatAI::CoverScore(F,Context); return O;
}
void UEnemyCombatComponent::AssessCoverOptions(FTacticalPosition& P)
{
    P.CoverOptions={};
    const double Now=GetWorld()->GetTimeSeconds();
    if (!CoverProtected(P.Ground)) return;
    const FVector Forward=(CoverThreatGround-P.Ground).GetSafeNormal2D();
    if (Forward.IsNearlyZero()) return;
    const FVector Right=FVector::CrossProduct(FVector::UpVector,Forward);
    // Side distance is measured from actual collision bounds when available.
    // Wide walls still get independent bounded step-outs; an unreachable edge fails.
    for (int32 Side=0; Side<3; ++Side)
    {
        if (CoverFailures[Side].Contains(P.Ground.X,P.Ground.Y,Now)) continue;
        const auto Kind=Side==0 ? CombatAI::CoverSide::Left : Side==1 ? CombatAI::CoverSide::Right : CombatAI::CoverSide::Up;
        if (Side==2) { P.CoverOptions[Side]=AssessCoverOption(P.Ground,P.Ground,Kind); continue; }
        for (float Distance : {80.f,160.f,240.f,360.f,480.f,600.f})
        {
            FVector Pose=P.Ground+Right*(Side==0 ? -Distance : Distance);
            FVector Ground; CombatAI::PositionRejection Why;
            if (!TacticalGround(Pose,Ground,Why,1)) continue;
            auto O=AssessCoverOption(P.Ground,Ground,Kind);
            if (O.Score>CombatAI::InvalidPositionScore) { P.CoverOptions[Side]=O; break; }
        }
    }
}

void UEnemyCombatComponent::ResetCover(bool bHistory)
{
    CoverPhase=CombatAI::CoverPhase::None; CoverOwner={}; CoverPlan={};
    bCoverScan=bCoverScanReady=bEndCoverAfterReturn=false;
    CoverStarted=CoverPhaseAt=CoverValidateAt=0; CoverBursts=0;
    if (bHistory) { CoverFailures={}; NextCoverScan=0; CoverGate=CombatAI::CoverGate::None; }
}
void UEnemyCombatComponent::AdvanceCoverScan(double Now)
{
    if (CoverPhase!=CombatAI::CoverPhase::None || !Context.WeaponUsable ||
        !(Context.Weapon.Capabilities & CombatAI::CoverFire)) return;
    if (!bCoverScan && Now >= NextCoverScan && (bTargetVisible || Now-Memory.LastSeen<=6))
    {
        bCoverScan=true; CoverScanAt=Now;
        CoverThreatGround=LastKnownGround; CoverThreatAim=LastKnownAim;
        SearchAnchor=CoverThreatGround; SearchForward=(CoverThreatGround-Feet()).GetSafeNormal2D();
        if (SearchForward.IsNearlyZero()) SearchForward=HomeFacing.Vector();
        BeginTacticalScan(Now);
    }
    if (!bCoverScan) return;
    if (Now-CoverScanAt>4.5 || FVector::Dist2D(CoverThreatGround,LastKnownGround)>180 || Now-Memory.LastSeen>6)
    {
        bCoverScan=bCoverScanReady=bTacticalScan=false; NextCoverScan=Now+.5;
        CoverGate=CombatAI::CoverGate::Stale; return;
    }
    AdvanceTacticalScan(Now);
    // Do not replace an already running finite burst or reload to take cover.
    if (bCoverScanReady && State!=EEnemyCombatState::Burst && State!=EEnemyCombatState::Reload) ChooseCover(Now);
}
void UEnemyCombatComponent::ChooseCover(double Now)
{
    bCoverScan=bCoverScanReady=false; NextCoverScan=Now+2;
    int32 BestCandidate=INDEX_NONE, BestSide=INDEX_NONE; double Best=CombatAI::InvalidPositionScore;
    if (!Assignment.Accepts(ScanRequest) || FVector::Dist2D(Feet(),ScanOrigin)>60) return;
    for (int32 I=0; I<CandidateIndex; ++I)
    {
        const auto& P=TacticalCandidates[I];
        if (!P.Features.RouteClear || MoveBackoff.Blocks(P.Ground.X,P.Ground.Y,Now) ||
            !CombatAI::CoverTransferEligible(Context,P.Features.Travel,bTargetVisible,ObstructedSince>=0)) continue;
        for (int32 S=0; S<3; ++S)
        {
            const double Score=CombatAI::CoverScore(P.CoverOptions[S].Features,Context);
            if (Score>Best) { Best=Score; BestCandidate=I; BestSide=S; }
        }
    }
    if (BestCandidate==INDEX_NONE)
    { CoverGate=CombatAI::CoverGate::NoOption; TacticalReason=TEXT("no supported protected anchor with a usable firing lane; hold range"); return; }
    auto Winner=TacticalCandidates[BestCandidate];
    auto Option=AssessCoverOption(Winner.Ground,Winner.CoverOptions[BestSide].Pose,Winner.CoverOptions[BestSide].Features.Side);
    double Length=0; TArray<FVector> Route;
    if (Option.Score<=CombatAI::InvalidPositionScore || !TacticalRoute(Feet(),Winner.Ground,Winner.Obstacle,Route,Length,1))
    { CoverFailures[BestSide].Remember(Winner.Ground.X,Winner.Ground.Y,Now+5); CoverGate=CombatAI::CoverGate::Geometry; return; }
    Transfers.Refresh(Now);
    const bool Moving=FVector::Dist2D(Feet(),Winner.Ground)>25;
    if (Moving && !Transfers.Start()) { CoverGate=CombatAI::CoverGate::Travel; return; }
    ClearIntent(); bTacticalScan=bSelectedPosition=bHeldPosition=false;
    Assignment.Assign(EncounterGeneration,CombatAI::TacticalObjective::CoverEngagement,IntentEvidenceId,Now);
    CoverOwner=Assignment.Token; CoverPlan=Option; CoverStarted=Now; CoverBursts=0; bEndCoverAfterReturn=false;
    SelectedPosition=Winner; Path=Route; PathIndex=0; PathGoal=Option.Anchor;
    PathRequest=EnsureAction(CombatAI::ActionKind::Move,Now); ProgressPosition=Feet(); LastProgress=Now; FailedAttempts=0;
    SetCoverPhase(CombatAI::CoverPhase::ToAnchor,Now,TEXT("committed protected anchor and independently selected firing side"));
}
void UEnemyCombatComponent::SetCoverPhase(CombatAI::CoverPhase Phase, double Now, const TCHAR* Why)
{
    CoverPhase=Phase; CoverPhaseAt=Now; CoverValidateAt=0; TacticalReason=Why;
    CoverGate=CombatAI::CoverGate::None;
    ChangeState(EEnemyCombatState::Aim,Why);
    if (Phase==CombatAI::CoverPhase::Exposing) Gates.AimUntil=Now+Context.Weapon.Aim;
    RecordTrace(CombatAI::Event::Tactical,Why);
}
bool UEnemyCombatComponent::StartCoverMove(FVector Goal, double Now)
{
    // A failed preview never falls through to an unrelated route toward the threat.
    if (!CoverWalk(Feet(),Goal)) return false;
    ClearIntent(); Path={Goal}; PathIndex=0; PathGoal=Goal;
    Enemy()->SetCrouchCommand(true); Enemy()->SetRifleAimTarget(bTargetVisible ? LastKnownAim : CoverThreatAim);
    PathRequest=EnsureAction(CombatAI::ActionKind::Move,Now); ProgressPosition=Feet(); LastProgress=Now;
    FailedAttempts=0; NextRepath=Now; return true;
}
void UEnemyCombatComponent::ReturnToCover(double Now, const TCHAR* Why, bool bEnd, bool bFailed)
{
    bEndCoverAfterReturn |= bEnd;
    if (bFailed)
    {
        const int32 Index=int32(CoverPlan.Features.Side)-1;
        if (Index>=0 && Index<3) CoverFailures[Index].Remember(CoverPlan.Anchor.X,CoverPlan.Anchor.Y,Now+5);
    }
    ClearIntent();
    SetCoverPhase(CombatAI::CoverPhase::Returning,Now,Why);
    Enemy()->SetCrouchCommand(true);
    // Route is installed after crouch is achieved. Protected return survives clearing
    // the local weapon action; no unfinished reload is committed during this phase.
}
void UEnemyCombatComponent::FailCoverReturn(double Now, const TCHAR* Why)
{
    for (auto& History : CoverFailures) History.Remember(CoverPlan.Anchor.X,CoverPlan.Anchor.Y,Now+5);
    ClearIntent(); ResetCover(); CoverGate=CombatAI::CoverGate::ReturnFailed; NextCoverScan=Now+1;
    BeginSearch(Why);
}
bool UEnemyCombatComponent::AdvanceCover(double Now)
{
    using Phase=CombatAI::CoverPhase; using Gate=CombatAI::CoverGate;
    if (CoverPhase==Phase::None) return false;
    auto* E=Enemy();
    if (!Assignment.Accepts(CoverOwner) || CoverOwner.Generation!=EncounterGeneration || !Context.WeaponUsable)
    { ClearIntent(); ResetCover(); return false; }
    const bool EvidenceValid=RefreshCoverThreat(Now);
    if (!EvidenceValid && CoverPhase!=Phase::Returning)
    { ReturnToCover(Now,TEXT("cover evidence expired or observed threat moved; return then replan"),true,false); CoverGate=Gate::Stale; }
    E->SetRifleAimTarget(bTargetVisible ? LastKnownAim : CoverThreatAim);
    const bool AtAnchor=FVector::Dist2D(Feet(),CoverPlan.Anchor)<=25 && FMath::Abs(Feet().Z-CoverPlan.Anchor.Z)<=20;
    const bool AtPose=FVector::Dist2D(Feet(),CoverPlan.Pose)<=20 && FMath::Abs(Feet().Z-CoverPlan.Pose.Z)<=20;
    const bool Stationary=E->GetRifleMovementAlpha()<=.15f;
    if (CoverPhase==Phase::ToAnchor)
    {
        E->SetCrouchCommand(true); E->SetRifleStance(EGASPALSRifleStance::Ready);
        if (Now-CoverPhaseAt>8) { ReturnToCover(Now,TEXT("anchor travel deadline"),true,true); return true; }
        if (!E->IsMovementCrouched()) { E->StopMovementCommand(); CoverGate=Gate::Crouch; return true; }
        if (!AtAnchor)
        {
            CoverGate=Gate::Travel;
            if (!FollowPath(CoverPlan.Anchor,25,Now,CombatAI::MovePurpose::Cover))
                ReturnToCover(Now,TEXT("anchor route failed; bounded return"),true,true);
            return true;
        }
        E->StopMovementCommand();
        if (!Stationary) return true;
        if (!CoverProtected(Feet()) || !CoverCapsule(Feet(),true))
        { ReturnToCover(Now,TEXT("achieved anchor does not protect; abandon plan"),true,true); return true; }
        ClearIntent(); SetCoverPhase(Phase::Protected,Now,TEXT("actual crouched anchor achieved"));
    }
    if (CoverPhase==Phase::Returning)
    {
        E->SetCrouchCommand(true); E->SetRifleStance(EGASPALSRifleStance::Ready);
        if (Now-CoverPhaseAt>4 || !CoverCapsule(CoverPlan.Anchor,true))
        {
            FailCoverReturn(Now,TEXT("cover return invalidated; stopped at actual feet")); return true;
        }
        if (!E->IsMovementCrouched()) { E->StopMovementCommand(); CoverGate=Gate::Crouch; return true; }
        if (!AtAnchor)
        {
            CoverGate=Gate::Travel;
            if ((Path.IsEmpty() && !StartCoverMove(CoverPlan.Anchor,Now)) ||
                !FollowPath(CoverPlan.Anchor,25,Now,CombatAI::MovePurpose::Cover))
            {
                FailCoverReturn(Now,TEXT("safe return route unavailable; replan from actual feet"));
            }
            return true;
        }
        E->StopMovementCommand();
        if (!Stationary) return true;
        const bool Protected=CoverProtected(Feet());
        if (bEndCoverAfterReturn || !Protected || CoverBursts>=3 || !EvidenceValid)
        {
            ClearIntent(); ResetCover(); NextCoverScan=Now+.5;
            BeginSearch(TEXT("cover cycle ended in protection; bounded reassessment")); return true;
        }
        ClearIntent(); SetCoverPhase(Phase::Protected,Now,TEXT("burst returned to achieved crouched protection"));
    }
    if (CoverPhase==Phase::Protected)
    {
        E->StopMovementCommand(); E->SetCrouchCommand(true); E->SetRifleStance(EGASPALSRifleStance::Ready);
        if (!AtAnchor || !E->IsMovementCrouched() || !Stationary)
        {
            CoverGate=Gate::Crouch;
            if (Now-CoverPhaseAt>1.2) ReturnToCover(Now,TEXT("protected stance refused or feet displaced"),true,true);
            return true;
        }
        if (Magazine<=0 || State==EEnemyCombatState::Reload)
        {
            CoverGate=Gate::Reload;
            if (State!=EEnemyCombatState::Reload)
            {
                ClearIntent(); ReloadRequest=EnsureAction(CombatAI::ActionKind::Reload,Now);
                E->SetCrouchCommand(true);
                Gates.ReloadUntil=Now+FMath::Clamp(Tuning.ReloadSeconds,.3f,15.f);
                ChangeState(EEnemyCombatState::Reload,TEXT("reload at achieved protected anchor"));
            }
            if (Now<Gates.ReloadUntil) return true;
            if (!FinishAction(ReloadRequest,CombatAI::ActionStatus::Succeeded,CombatAI::ActionFailure::None))
            { ReturnToCover(Now,TEXT("obsolete protected reload discarded"),true,false); return true; }
            Magazine=FMath::Clamp(Tuning.MagazineCapacity,1,60); ++Reloads; ReloadRequest={}; Gates.ReloadUntil=0;
            ChangeState(EEnemyCombatState::Aim,TEXT("protected reload complete"));
        }
        if (Now<Gates.ReadyAt(NextShot) || Now-CoverPhaseAt<.15) { CoverGate=Gate::Rest; return true; }
        const auto Fresh=AssessCoverOption(Feet(),CoverPlan.Pose,CoverPlan.Features.Side);
        if (Fresh.Score<=CombatAI::InvalidPositionScore)
        { ReturnToCover(Now,TEXT("firing side or return geometry no longer valid"),true,true); return true; }
        SetCoverPhase(Phase::Exposing,Now,TEXT("expose toward permitted evidence; seek current sight"));
    }
    if (CoverPhase==Phase::Exposing)
    {
        E->SetRifleStance(EGASPALSRifleStance::Aim);
        E->SetCrouchCommand(!AtPose);
        if (Now-CoverPhaseAt>3)
        { ReturnToCover(Now,TEXT("exposure route or stand refused; deadline"),true,true); CoverGate=Gate::Deadline; return true; }
        if (!AtPose)
        {
            CoverGate=Gate::Travel;
            if (!E->IsMovementCrouched()) { E->StopMovementCommand(); return true; }
            if ((Path.IsEmpty() && !StartCoverMove(CoverPlan.Pose,Now)) ||
                !FollowPath(CoverPlan.Pose,20,Now,CombatAI::MovePurpose::Cover))
                ReturnToCover(Now,TEXT("exposure route failed"),true,true);
            return true;
        }
        E->StopMovementCommand(); CoverGate=Gate::Stand;
        if (E->IsMovementCrouched() || !Stationary) return true;
        ClearIntent(); SetCoverPhase(Phase::Aiming,Now,TEXT("actual firing pose achieved; await fresh sight and barrel safety"));
        ObservePlayer(); NextSight=Now+FMath::Clamp(Tuning.SightInterval,.05f,1.f);
        if (bTargetVisible && ContactAt>ContactDecisionAt) ContactDecisionAt=Now;
    }
    if (CoverPhase==Phase::Aiming || CoverPhase==Phase::Firing)
    {
        E->StopMovementCommand(); E->SetCrouchCommand(false); E->SetRifleStance(EGASPALSRifleStance::Aim);
        if (!AtPose || E->IsMovementCrouched() || !Stationary || Now-CoverPhaseAt>2)
        { ReturnToCover(Now,TEXT("exposed pose interrupted or timed out"),true,true); return true; }
        if (Now>=CoverValidateAt)
        {
            CoverValidateAt=Now+.35;
            if (!CoverCapsule(Feet(),false) || !CoverWalk(Feet(),CoverPlan.Anchor))
            { ReturnToCover(Now,TEXT("exposed pose or safe return invalidated"),true,true); return true; }
        }
        if (!bTargetVisible)
        {
            CoverGate=Gate::Contact;
            if (CoverPhase==Phase::Firing || Now-CoverPhaseAt>.45)
                ReturnToCover(Now,TEXT("no useful current sight at exposure; return"),true,false);
            return true;
        }
        CoverGate=Gate::WeaponSafety;
        AdvanceWeapon(Now,true);
    }
    return true;
}
