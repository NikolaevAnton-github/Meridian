#include "EnemyCombatComponent.h"
#include "GASPEnemyFixture.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"

void UEnemyCombatComponent::AdvanceMobile(double Now, double Distance)
{
    auto* E=Enemy();
    const auto Motion=E->GetFireMotion();
    auto Rest=[&](const TCHAR* Why)
    {
        ClearMovement(); MobilePhase=CombatAI::MobilePhase::Cooldown;
        NextMobileAt=Now+FMath::Clamp(Tuning.CombatMoveRest,.1f,1.f);
        TacticalReason=Why; RecordTrace(CombatAI::Event::Tactical,Why);
    };
    const bool Active=MobilePhase==CombatAI::MobilePhase::Strafe || MobilePhase==CombatAI::MobilePhase::Approach;
    if (Active)
    {
        if (!bTargetVisible || CoverPhase!=CombatAI::CoverPhase::None ||
            !Motion.Authority || !Motion.Grounded || Now-MobileStarted>4 || Distance<150)
        { Rest(TEXT("mobile movement canceled: contact, authority, motion, range or deadline")); return; }
        // Hand off before destination braking. A successful leg has no dwell,
        // and neither the weapon action nor a magazine change owns this route.
        if (FVector::Dist2D(Feet(),MobileGoal)>FMath::Max(35.0,Motion.Speed*.2))
        {
            if (!FollowPath(MobileGoal,18,Now,CombatAI::MovePurpose::Cautious) ||
                LastPathOutcome==CombatAI::PathOutcome::Failed)
                Rest(TEXT("mobile route failed; stop at actual feet and reassess"));
            return;
        }
        FinishMoveAction(CombatAI::ActionStatus::Succeeded,CombatAI::ActionFailure::None);
        MobilePhase=CombatAI::MobilePhase::None;
    }
    if (Now<NextMobileAt || CoverPhase!=CombatAI::CoverPhase::None || !bTargetVisible ||
        MoveBackoff.Blocks(LastKnownGround.X,LastKnownGround.Y,Now) ||
        !Motion.Authority || !Motion.Grounded || E->IsMovementCrouched() ||
        !(Context.Weapon.Capabilities & CombatAI::CautiousMove)) return;
    const auto Pose=E->GetRiflePose();
    if (Pose.bValid && FMath::Abs(Pose.Lean)>.5f) return;
    const bool Approach=RangeIntent==CombatAI::RangeIntent::CautiousAdvance;
    if (!Approach && Distance>Context.Weapon.EffectiveRange) return;
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
        MobileSerial+=I; Found=true; break;
    }
    if (!Found) { ++MobileSerial; Rest(TEXT("no supported mobile corridor at weapon range; bounded retry")); return; }
    ClearMovement(); MobileGoal=Goal; MobileStarted=Now;
    MobilePhase=Approach ? CombatAI::MobilePhase::Approach : CombatAI::MobilePhase::Strafe;
    Path={Goal}; PathGoal=Goal; PathIndex=0; PathRequest=EnsureMoveAction(Now);
    FailedAttempts=0; ProgressPosition=Feet(); LastProgress=Now;
    TacticalReason=Approach ? TEXT("bounded cautious approach; weapon action independent") : TEXT("continuous supported lateral movement; independent fire and reload");
    RecordTrace(CombatAI::Event::Tactical,*TacticalReason);
    if (!FollowPath(Goal,18,Now,CombatAI::MovePurpose::Cautious)) Rest(TEXT("mobile start refused"));
}
