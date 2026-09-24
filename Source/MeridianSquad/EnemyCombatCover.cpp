#include "EnemyCombatComponent.h"
#include "GASPEnemyFixture.h"
#include "CombatProjectileWorld.h"
#include "Components/CapsuleComponent.h"
#include "Components/PrimitiveComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "DefaultMovementSet/CharacterMoverComponent.h"
#include "DefaultMovementSet/Settings/StanceSettings.h"
#include "MoveLibrary/MovementUtils.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"

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
    if (const auto* Character = Cast<ACharacter>(E->Foundation))
    {
        const auto* Movement = Character->GetCharacterMovement();
        const auto* Current = Character->GetCapsuleComponent();
        const auto* Defaults = Character->GetClass()->GetDefaultObject<ACharacter>();
        const auto* Standing = Defaults ? Defaults->GetCapsuleComponent() : nullptr;
        if (!Movement || !Current || !Standing) return false;
        const FVector Scale = Current->GetComponentScale();
        const float UnscaledRadius = bCrouched ? Current->GetUnscaledCapsuleRadius() : Standing->GetUnscaledCapsuleRadius();
        const float RequestedHeight = bCrouched ? Movement->GetCrouchedHalfHeight() : Standing->GetUnscaledCapsuleHalfHeight();
        if (Scale.ContainsNaN() || Scale.X <= 0 || Scale.Y <= 0 || Scale.Z <= 0 ||
            !FMath::IsFinite(UnscaledRadius) || UnscaledRadius <= 0 || !FMath::IsFinite(RequestedHeight)) return false;
        // CMC Crouch clamps height to the current radius. UnCrouch restores the
        // class-default size, even when the achieved capsule is still crouched.
        // UE 5.8 capsule getters scale radius by min(X,Y), half-height by Z.
        Radius = UnscaledRadius * FMath::Min(Scale.X, Scale.Y);
        HalfHeight = FMath::Max3(0.f, UnscaledRadius, RequestedHeight) * Scale.Z;
        return FMath::IsFinite(Radius) && FMath::IsFinite(HalfHeight) && Radius > 0 && HalfHeight >= Radius;
    }
    const auto* Mover = E->Foundation->FindComponentByClass<UCharacterMoverComponent>();
    const auto* Original = UMovementUtils::GetOriginalComponentType<UCapsuleComponent>(E->Foundation);
    const auto* Current = E->Foundation->FindComponentByClass<UCapsuleComponent>();
    const auto* Settings = Mover ? Mover->FindSharedSettings<UStanceSettings>() : nullptr;
    if (!Original || !Current || !Settings) return false;
    Radius = Current->GetScaledCapsuleRadius();
    // Match Mover's actual stance expansion contract, including its original capsule.
    HalfHeight = bCrouched ? Settings->CrouchHalfHeight : Original->GetScaledCapsuleHalfHeight();
    return FMath::IsFinite(Radius) && FMath::IsFinite(HalfHeight) && Radius > 0 && HalfHeight >= Radius;
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
    TArray<FVector> Points; FVector Pivot;
    if (!CoverAnatomyAt(Ground,true,Points,Pivot)) return false;
    TArray<FVector> Probes={Ground+FVector(0,0,60),Ground+FVector(0,0,85),Ground+FVector(0,0,100)};
    if (!Points.IsEmpty()) Probes={Pivot,Points[1],Points[0]};
    // A stance estimate may propose travel, but protection at achieved crouched
    // feet is checked against the actual ready/aim transition, including the head.
    const auto* E=Enemy();
    if (!Points.IsEmpty() && E && E->Body && E->IsMovementCrouched() && FVector::Dist2D(Feet(),Ground)<2 && FMath::Abs(Feet().Z-Ground.Z)<2)
        Probes={E->Body->GetSocketLocation(TEXT("spine_01")),E->Body->GetSocketLocation(TEXT("spine_05")),E->Body->GetSocketLocation(TEXT("head"))};
    int32 Blocked = 0;
    for (const FVector& Probe:Probes)
    {
        FHitResult Hit;
        if (TacticalTrace(Probe, CoverThreatAim, Hit) && Hit.Distance < 180 &&
            Hit.GetComponent() && Hit.GetComponent()->GetCollisionResponseToChannel(ECC_Pawn) == ECR_Block &&
            FMath::Abs(Hit.ImpactNormal.Z) < .4) ++Blocked;
    }
    return Blocked == 3;
}
bool UEnemyCombatComponent::CoverLane(FVector Ground)
{
    TArray<FVector> Points; FVector Pivot;
    if (!CoverAnatomyAt(Ground,false,Points,Pivot)) return false;
    FHitResult Hit;
    if (TacticalTrace(Points.IsEmpty() ? Ground+FVector(0,0,150) : Points[0], CoverThreatAim, Hit)) return false;
    FCollisionQueryParams Query(SCENE_QUERY_STAT(EnemyCoverLane), false);
    FCollisionResponseParams StaticOnly(ECR_Ignore);
    StaticOnly.CollisionResponse.SetResponse(ECC_WorldStatic, ECR_Block);
    const FVector Root = Points.IsEmpty() ? Ground+FVector(0,0,125) : Points[2];
    const FVector Direction = (CoverThreatAim-Root).GetSafeNormal();
    ++TacticalQueryCount;
    if (GetWorld()->SweepSingleByChannel(Hit, Root, Root+Direction*120, FQuat::Identity, ECC_Visibility,
        FCollisionShape::MakeSphere(10), Query, StaticOnly)) return false;
    ++TacticalQueryCount;
    return !GetWorld()->SweepSingleByChannel(Hit, Root, CoverThreatAim, FQuat::Identity, ECC_Visibility,
        FCollisionShape::MakeSphere(1), Query, StaticOnly);
}
bool UEnemyCombatComponent::CoverAnatomyAt(FVector Ground, bool bCrouched, TArray<FVector>& Points, FVector& Pivot) const
{
    Points.Reset(); Pivot=FVector::ZeroVector;
    const auto* E=Enemy();
    if (!E) return false;
    const auto Anatomy=E->GetCoverAnatomy(bCrouched);
    if (!Anatomy.IsValid()) return !Anatomy.bRequired;
    const FRotator Heading(0,(CoverThreatAim-Ground).Rotation().Yaw,0);
    for (const FVector& P:Anatomy.Points) Points.Add(Ground+Heading.RotateVector(P));
    Pivot=Ground+Heading.RotateVector(Anatomy.Pivot);
    return true;
}
UEnemyCombatComponent::FCoverOption UEnemyCombatComponent::AssessCoverOption(FVector Anchor, FVector Pose, CombatAI::CoverSide Side)
{
    FCoverOption O; O.Anchor=Anchor; O.Pose=Pose;
    auto& F=O.Features; F.Side=Side;
    F.Travel=FVector::Dist2D(Feet(),Anchor); F.ExposureTravel=FVector::Dist2D(Anchor,Pose);
    if (Side==CombatAI::CoverSide::Left || Side==CombatAI::CoverSide::Right)
    {
        O.Pose=Anchor; F.ExposureTravel=0;
        F.Protected=LeanProtected(Anchor); F.Protection=F.Protected ? 1 : 0;
        F.AnchorClear=F.PoseClear=CoverCapsule(Anchor,false);
        F.InRange=FVector::Dist2D(Anchor,CoverThreatGround)<=Context.Weapon.EffectiveRange;
        if (F.Protected && F.AnchorClear && F.InRange)
        {
            F.Lane=LeanProposal(Anchor,(Side==CombatAI::CoverSide::Left ? -1.f : 1.f)*FMath::Clamp(Tuning.CoverLeanDegrees,20.f,35.f));
            F.Outbound=F.Return=F.Lane; // Same grounded feet; only the upper body exposes.
        }
        O.Score=CombatAI::CoverScore(F,Context); return O;
    }
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
    // Find the local static shadow edge independently in each direction. At most
    // one bounded bracket and eight refinements per side, never live target reads.
    for (int32 Side=0; Side<3; ++Side)
    {
        if (CoverFailures[Side].Contains(P.Ground.X,P.Ground.Y,Now)) continue;
        const auto Kind=Side==0 ? CombatAI::CoverSide::Left : Side==1 ? CombatAI::CoverSide::Right : CombatAI::CoverSide::Up;
        if (Side==2) { P.CoverOptions[Side]=AssessCoverOption(P.Ground,P.Ground,Kind); continue; }
        const FVector Out=Right*(Side==0 ? -1.f : 1.f);
        // Leave room for the upright rifle before exposure. The lean rotates the
        // held weapon too; a muzzle already inside the wall cannot begin its arc.
        const FVector Base=P.Ground-Forward*40;
        auto Hidden=[&](float Distance)
        {
            const FVector Location=Base+Out*Distance;
            TArray<FVector> Points; FVector Pivot;
            if (!CoverAnatomyAt(Location,false,Points,Pivot)) return false;
            FHitResult Hit;
            return TacticalTrace(Points.IsEmpty() ? Location+FVector(0,0,165) : Points[0],CoverThreatAim,Hit) && Hit.Distance<180;
        };
        if (!Hidden(0) || Hidden(600)) continue;
        float Low=0, High=600;
        for (int32 I=0; I<8; ++I)
        { const float Mid=(Low+High)*.5f; if (Hidden(Mid)) Low=Mid; else High=Mid; }
        FVector Ground; CombatAI::PositionRejection Why;
        if (!TacticalGround(Base+Out*FMath::Max(0.f,Low-2.f),Ground,Why,0)) continue;
        P.CoverOptions[Side]=AssessCoverOption(Ground,Ground,Kind);
    }
}

void UEnemyCombatComponent::ResetCover(bool bHistory)
{
    if (auto* E=Enemy()) E->SetRifleLean(0);
    bLeanPoseCaptured=false; LeanNeutral.Reset();
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
    // The scan may finish while moving. AssessCoverOption and TacticalRoute
    // below revalidate the winner from the current feet before committing it.
    if (!Assignment.Accepts(ScanRequest)) return;
    for (int32 I=0; I<CandidateIndex; ++I)
    {
        const auto& P=TacticalCandidates[I];
        if (!P.Features.RouteClear) continue;
        for (int32 S=0; S<3; ++S)
        {
            auto O=P.CoverOptions[S];
            O.Features.Travel=FVector::Dist2D(Feet(),O.Anchor);
            if (MoveBackoff.Blocks(O.Anchor.X,O.Anchor.Y,Now) || CoverFailures[S].Contains(O.Anchor.X,O.Anchor.Y,Now) ||
                !CombatAI::CoverTransferEligible(Context,O.Features.Travel,bTargetVisible,ObstructedSince>=0)) continue;
            const double Score=CombatAI::CoverScore(O.Features,Context);
            if (Score>Best) { Best=Score; BestCandidate=I; BestSide=S; }
        }
    }
    if (BestCandidate==INDEX_NONE)
    { CoverGate=CombatAI::CoverGate::NoOption; TacticalReason=TEXT("no supported protected anchor with a usable firing lane; hold range"); return; }
    auto Winner=TacticalCandidates[BestCandidate];
    const auto Proposed=Winner.CoverOptions[BestSide];
    auto Option=AssessCoverOption(Proposed.Anchor,Proposed.Pose,Proposed.Features.Side);
    double Length=0; TArray<FVector> Route;
    const bool Lean=Option.Features.Side!=CombatAI::CoverSide::Up;
    if (Option.Score<=CombatAI::InvalidPositionScore || !TacticalRoute(Feet(),Option.Anchor,Winner.Obstacle,Route,Length,Lean ? 0 : 1))
    { CoverFailures[BestSide].Remember(Option.Anchor.X,Option.Anchor.Y,Now+5); CoverGate=CombatAI::CoverGate::Geometry; return; }
    Option.Features.Travel=Length;
    Option.Score=CombatAI::CoverScore(Option.Features,Context);
    if (!CombatAI::CoverTransferEligible(Context,Length,bTargetVisible,ObstructedSince>=0))
    { CoverGate=CombatAI::CoverGate::Travel; return; }
    Transfers.Refresh(Now);
    const bool Moving=FVector::Dist2D(Feet(),Option.Anchor)>12;
    if (Moving && !Transfers.Start()) { CoverGate=CombatAI::CoverGate::Travel; return; }
    ClearIntent(); bTacticalScan=bSelectedPosition=bHeldPosition=false;
    Assignment.Assign(EncounterGeneration,CombatAI::TacticalObjective::CoverEngagement,IntentEvidenceId,Now);
    CoverOwner=Assignment.Token; CoverPlan=Option; CoverStarted=Now; CoverBursts=0; bEndCoverAfterReturn=false;
    SelectedPosition=Winner; Path=Route; PathIndex=0; PathGoal=Option.Anchor;
    PathRequest=EnsureMoveAction(Now); ProgressPosition=Feet(); LastProgress=Now; FailedAttempts=0;
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
    PathRequest=EnsureMoveAction(Now); ProgressPosition=Feet(); LastProgress=Now;
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
    Enemy()->SetCrouchCommand(LeanSign()==0);
    // Route is installed after crouch is achieved. Protected return survives clearing
    // the local movement action; an independent reload keeps its original deadline.
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
    if (LeanSign()!=0) return AdvanceLeanCover(Now);
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
        if (Gates.ReloadUntil>0)
        { CoverGate=Gate::Reload; E->SetRifleStance(EGASPALSRifleStance::Ready); return true; }
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
