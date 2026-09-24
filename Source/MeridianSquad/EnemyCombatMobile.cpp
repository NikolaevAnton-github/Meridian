#include "EnemyCombatComponent.h"
#include "GASPEnemyFixture.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"

void UEnemyCombatComponent::AdvanceMobile(double Now, double Distance)
{
    auto* E=Enemy();
    auto Rest=[&](const TCHAR* Why)
    {
        ClearMovement(); MobilePhase=CombatAI::MobilePhase::Cooldown;
        NextMobileAt=Now+FMath::Clamp(Tuning.CombatMoveRest,2.f,8.f);
        TacticalReason=Why; RecordTrace(CombatAI::Event::Tactical,Why);
    };
    const bool Active=MobilePhase==CombatAI::MobilePhase::Strafe || MobilePhase==CombatAI::MobilePhase::Approach;
    if (Active)
    {
        if (!bTargetVisible || CoverPhase!=CombatAI::CoverPhase::None ||
            E->GetFireMotion().Gate()!=CombatAI::MotionGate::Ready || Now-MobileStarted>4 ||
            Distance<FMath::Min(Context.Weapon.PreferredRange*.65,600.0))
        { Rest(TEXT("mobile movement canceled: contact, authority, motion, range or deadline")); return; }
        if (!FollowPath(MobileGoal,18,Now,CombatAI::MovePurpose::Cautious) ||
            LastPathOutcome==CombatAI::PathOutcome::Failed)
        { Rest(TEXT("mobile route failed; stop at actual feet and reassess")); return; }
        if (FVector::Dist2D(Feet(),MobileGoal)<=18)
            Rest(TEXT("bounded mobile step complete; weapon action continues"));
        return;
    }
    if (Now<NextMobileAt || bCoverScan || CoverPhase!=CombatAI::CoverPhase::None || !bTargetVisible ||
        MoveBackoff.Blocks(LastKnownGround.X,LastKnownGround.Y,Now) ||
        E->GetFireMotion().Gate()!=CombatAI::MotionGate::Ready || E->IsMovementCrouched() ||
        !(Context.Weapon.Capabilities & CombatAI::CautiousMove)) return;
    const auto Pose=E->GetRiflePose();
    if (!Pose.bValid || FMath::Abs(Pose.Lean)>.5f) return;
    const bool Approach=RangeIntent==CombatAI::RangeIntent::CautiousAdvance;
    if (!Approach && (Distance>Context.Weapon.EffectiveRange || Shots==0 || ObstructedSince>=0)) return;
    const FVector Start=Feet(), Forward=(LastKnownGround-Start).GetSafeNormal2D();
    const FVector Right=FVector::CrossProduct(FVector::UpVector,Forward);
    FVector Goal=FVector::ZeroVector; bool Found=false;
    // Two deterministic side options per attempt. No random per-frame weaving,
    // target pursuit during a side step, or stationary restart on a weapon event.
    for (int32 I=0; I<(Approach ? 1 : 2); ++I)
    {
        const float Side=((MobileSerial+int32(StableSpawnIndex)+I)%2)==0 ? -1.f : 1.f;
        const FVector Proposed=Start+(Approach ? Forward*CombatAI::CautiousStep(Context,Distance) :
            Right*Side*FMath::Clamp(Tuning.CombatStrafeDistance,100.f,240.f));
        CombatAI::PositionRejection Failure;
        if (!TacticalGround(Proposed,Goal,Failure,0) || !TacticalWalk(Start,Goal,0)) continue;
        const double EndRange=FVector::Dist2D(Goal,LastKnownGround);
        if (EndRange<FMath::Min(Distance,Context.Weapon.PreferredRange) ||
            (!Approach && EndRange>Context.Weapon.EffectiveRange)) continue;
        if (!Approach)
        {
            FHitResult Hit;
            if (TacticalTrace(Goal+FVector(0,0,150),LastKnownAim,Hit) ||
                TacticalTrace((Start+Goal)*.5+FVector(0,0,150),LastKnownAim,Hit)) continue;
        }
        Found=true; break;
    }
    ++MobileSerial;
    if (!Found) { Rest(TEXT("no supported mobile corridor at weapon range; bounded retry")); return; }
    ClearMovement(); MobileGoal=Goal; MobileStarted=Now;
    MobilePhase=Approach ? CombatAI::MobilePhase::Approach : CombatAI::MobilePhase::Strafe;
    Path={Goal}; PathGoal=Goal; PathIndex=0; PathRequest=EnsureMoveAction(Now);
    FailedAttempts=0; ProgressPosition=Feet(); LastProgress=Now;
    NextCoverScan=Now+1; bTacticalScan=bCoverScan=bCoverScanReady=false;
    TacticalReason=Approach ? TEXT("bounded cautious approach; fire on entering valid range") : TEXT("short lateral firing step; independent aim and finite burst");
    RecordTrace(CombatAI::Event::Tactical,*TacticalReason);
    if (!FollowPath(Goal,18,Now,CombatAI::MovePurpose::Cautious)) Rest(TEXT("mobile start refused"));
}
