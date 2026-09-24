#include "EnemyCombatComponent.h"
#include "GASPEnemyFixture.h"
#include "CombatProjectileWorld.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/PrimitiveComponent.h"
#include "Engine/World.h"

float UEnemyCombatComponent::LeanSign() const
{
    if (CoverPhase==CombatAI::CoverPhase::None) return 0;
    return CoverPlan.Features.Side==CombatAI::CoverSide::Left ? -1.f :
        CoverPlan.Features.Side==CombatAI::CoverSide::Right ? 1.f : 0.f;
}
bool UEnemyCombatComponent::LeanProtected(FVector Ground)
{
    // Standing chest/head must be concealed at the same feet that will lean.
    for (float Height : {125.f,150.f,165.f})
    {
        FHitResult Hit;
        if (!TacticalTrace(Ground+FVector(0,0,Height),CoverThreatAim,Hit) || Hit.Distance>180 ||
            !Hit.GetComponent() || Hit.GetComponent()->GetCollisionResponseToChannel(ECC_Pawn)!=ECR_Block ||
            FMath::Abs(Hit.ImpactNormal.Z)>.4) return false;
    }
    return true;
}
TArray<FVector> UEnemyCombatComponent::LeanPoints() const
{
    const auto* E=Enemy();
    if (!E || !E->Body || !E->Rifle) return {};
    return {E->Body->GetSocketLocation(TEXT("head")),E->Body->GetSocketLocation(TEXT("spine_05")),
        E->Body->GetSocketLocation(TEXT("hand_r")),
        E->Rifle->DoesSocketExist(TEXT("Muzzle")) ? E->Rifle->GetSocketLocation(TEXT("Muzzle")) :
            E->Rifle->GetComponentTransform().TransformPosition(FVector(0,62,9))};
}
bool UEnemyCombatComponent::LeanSweep(const TArray<FVector>& From, const TArray<FVector>& To) const
{
    if (From.Num()!=4 || To.Num()!=4) return false;
    const float Radius[]={8,11,5,3};
    FCollisionQueryParams Query(SCENE_QUERY_STAT(EnemyLeanClearance),true);
    if (auto* World=ACombatProjectileWorld::Find(GetWorld())) World->BuildQuery(Query,Enemy());
    else return false;
    for (int32 I=0; I<4; ++I)
    {
        FHitResult Hit;
        if (From[I].ContainsNaN() || To[I].ContainsNaN() || GetWorld()->SweepSingleByChannel(Hit,From[I],To[I],
            FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(Radius[I]),Query)) return false;
    }
    // Include the held rifle length, rather than testing its muzzle alone.
    FHitResult Hit;
    return !GetWorld()->SweepSingleByChannel(Hit,To[2],To[3],FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(3),Query) &&
        !GetWorld()->SweepSingleByChannel(Hit,To[1],To[0],FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(7),Query) &&
        !GetWorld()->SweepSingleByChannel(Hit,To[1],To[2],FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(5),Query);
}
bool UEnemyCombatComponent::LeanProposal(FVector Ground, float Degrees)
{
    const FVector Forward=(CoverThreatAim-(Ground+FVector(0,0,145))).GetSafeNormal();
    const FVector Right=FVector::CrossProduct(FVector::UpVector,Forward).GetSafeNormal();
    const FVector Pivot=Ground+FVector(0,0,95);
    const TArray<FVector> Neutral={Ground+FVector(0,0,170),Ground+FVector(0,0,140),
        Ground+FVector(0,0,145)+Right*12+Forward*15,Ground+FVector(0,0,145)+Right*12+Forward*75};
    TArray<FVector> Prior=Neutral, Proposed;
    for (int32 Step=1; Step<=4; ++Step)
    {
        const FQuat Rotation(Forward,FMath::DegreesToRadians(-Degrees*Step/4));
        Proposed.Reset(); for (const FVector& P:Neutral) Proposed.Add(Pivot+Rotation.RotateVector(P-Pivot));
        if (!LeanSweep(Prior,Proposed)) return false;
        Prior=Proposed;
    }
    FHitResult Hit;
    return !TacticalTrace(Proposed[0],CoverThreatAim,Hit) && !TacticalTrace(Proposed[3],CoverThreatAim,Hit);
}
bool UEnemyCombatComponent::CaptureLeanPose()
{
    const auto* E=Enemy();
    const auto Pose=E ? E->GetRiflePose() : FEnemyRiflePose{};
    if (!Pose.bValid || Pose.Layer<.99f || Pose.Aim<.99f || FMath::Abs(Pose.Lean)>.25f) return false;
    LeanNeutral=LeanPoints();
    if (LeanNeutral.Num()!=4) return false;
    LeanPivot=E->Body->GetSocketLocation(TEXT("spine_01"));
    LeanAxis=E->Rifle->GetRightVector().GetSafeNormal();
    const FVector ToThreat=(CoverThreatAim-LeanNeutral[3]).GetSafeNormal();
    if (FVector::DotProduct(LeanAxis,ToThreat)<FMath::Cos(FMath::DegreesToRadians(6.f))) return false;
    // The achieved upright head must be concealed. A foot step that already
    // exposes the head is not accepted as a successful lean.
    FHitResult Hit;
    if (!TacticalTrace(LeanNeutral[0],CoverThreatAim,Hit) || Hit.Distance>180) return false;
    TArray<FVector> Prior=LeanNeutral, Proposed;
    for (int32 Step=1; Step<=4; ++Step)
    {
        const FQuat Rotation(LeanAxis,FMath::DegreesToRadians(-LeanSign()*FMath::Clamp(Tuning.CoverLeanDegrees,20.f,35.f)*Step/4));
        Proposed.Reset(); for (const FVector& P:LeanNeutral) Proposed.Add(LeanPivot+Rotation.RotateVector(P-LeanPivot));
        if (!LeanSweep(Prior,Proposed)) return false;
        Prior=Proposed;
    }
    if (TacticalTrace(Proposed[0],CoverThreatAim,Hit) || TacticalTrace(Proposed[3],CoverThreatAim,Hit)) return false;
    bLeanPoseCaptured=true; return true;
}
bool UEnemyCombatComponent::AchievedLeanClear() const
{
    const auto* E=Enemy();
    const auto Pose=E ? E->GetRiflePose() : FEnemyRiflePose{};
    if (!bLeanPoseCaptured || LeanNeutral.Num()!=4 || !Pose.bValid || LeanSign()==0 ||
        FMath::Abs(Pose.Lean-LeanSign()*FMath::Clamp(Tuning.CoverLeanDegrees,20.f,35.f))>1 ||
        E->GetFireMotion().Gate()!=CombatAI::MotionGate::Ready || E->GetFireMotion().Speed>15 ||
        FVector::Dist2D(Feet(),CoverPlan.Anchor)>12 || E->IsMovementCrouched()) return false;
    const auto Actual=LeanPoints();
    const FVector Right=FVector::CrossProduct(FVector::UpVector,LeanAxis).GetSafeNormal();
    const FVector Pivot=E->Body->GetSocketLocation(TEXT("spine_01"));
    // Actual socket displacement, relative to the actual pivot, is required.
    // A requested float, refused graph pose or translated capsule cannot pass.
    if (Actual.Num()!=4 || FVector::DotProduct((Actual[0]-Pivot)-(LeanNeutral[0]-LeanPivot),Right)*LeanSign()<10 ||
        FVector::DotProduct((Actual[1]-Pivot)-(LeanNeutral[1]-LeanPivot),Right)*LeanSign()<5) return false;
    return LeanSweep(Actual,Actual);
}
bool UEnemyCombatComponent::LeanReturned() const
{
    if (!bLeanPoseCaptured) return true;
    const auto* E=Enemy();
    const auto Actual=LeanPoints();
    if (!E || !E->Body || Actual.Num()!=4 || LeanNeutral.Num()!=4) return false;
    const FVector Pivot=E->Body->GetSocketLocation(TEXT("spine_01"));
    const FVector Right=FVector::CrossProduct(FVector::UpVector,LeanAxis).GetSafeNormal();
    return FMath::Abs(FVector::DotProduct((Actual[0]-Pivot)-(LeanNeutral[0]-LeanPivot),Right))<=4 &&
        FMath::Abs(FVector::DotProduct((Actual[1]-Pivot)-(LeanNeutral[1]-LeanPivot),Right))<=4;
}
bool UEnemyCombatComponent::AdvanceLeanCover(double Now)
{
    using Phase=CombatAI::CoverPhase; using Gate=CombatAI::CoverGate;
    auto* E=Enemy();
    const auto Pose=E->GetRiflePose();
    const float Actual=Pose.Lean;
    const bool AtAnchor=FVector::Dist2D(Feet(),CoverPlan.Anchor)<=12 && FMath::Abs(Feet().Z-CoverPlan.Anchor.Z)<=12;
    const bool Settled=E->GetFireMotion().Gate()==CombatAI::MotionGate::Ready && E->GetFireMotion().Speed<=15;
    E->SetCrouchCommand(false);
    if (CoverPhase==Phase::ToAnchor)
    {
        E->SetRifleLean(0); E->SetRifleStance(EGASPALSRifleStance::Ready);
        if (Now-CoverPhaseAt>8 || E->IsMovementCrouched())
        {
            E->StopMovementCommand();
            if (Now-CoverPhaseAt>8) ReturnToCover(Now,TEXT("lean anchor travel or stand deadline"),true,true);
            return true;
        }
        if (!AtAnchor)
        {
            CoverGate=Gate::Travel;
            if (!FollowPath(CoverPlan.Anchor,12,Now,CombatAI::MovePurpose::Cover))
                ReturnToCover(Now,TEXT("lean anchor unreachable"),true,true);
            return true;
        }
        E->StopMovementCommand(); if (!Settled) return true;
        ClearIntent(); SetCoverPhase(Phase::Protected,Now,TEXT("standing protected edge achieved; prepare upper-body exposure"));
    }
    if (CoverPhase==Phase::Returning)
    {
        E->StopMovementCommand(); E->SetRifleLean(0); E->SetRifleStance(EGASPALSRifleStance::Aim);
        CoverGate=Gate::Stand;
        // Blend fully upright before permitting any new travel or crouch owner.
        if (FMath::Abs(Actual)>.5f || !LeanReturned())
        {
            if (Now-CoverPhaseAt>1.2) { E->SetRifleLean(0,true); FailCoverReturn(Now,TEXT("lean return pose refused; offsets cleared")); }
            return true;
        }
        if (!AtAnchor || bEndCoverAfterReturn || !LeanProtected(Feet()) || CoverBursts>=3 || !RefreshCoverThreat(Now))
        {
            ClearIntent(); ResetCover(); NextCoverScan=Now+1; NextMobileAt=Now+1;
            BeginSearch(TEXT("lean returned; replan from current feet and permitted evidence")); return true;
        }
        bLeanPoseCaptured=false; LeanNeutral.Reset();
        SetCoverPhase(Phase::Protected,Now,TEXT("upper body returned to protected edge"));
    }
    if (CoverPhase==Phase::Protected)
    {
        E->StopMovementCommand(); E->SetRifleLean(0); E->SetRifleStance(EGASPALSRifleStance::Aim);
        if (!AtAnchor || !Settled || E->IsMovementCrouched() || !LeanProtected(Feet()))
        { ReturnToCover(Now,TEXT("lean support, standing protection or position invalidated"),true,true); return true; }
        if (Magazine<=0 || State==EEnemyCombatState::Reload)
        {
            CoverGate=Gate::Reload; E->SetRifleStance(EGASPALSRifleStance::Ready);
            if (State!=EEnemyCombatState::Reload)
            {
                ClearIntent(); ReloadRequest=EnsureAction(CombatAI::ActionKind::Reload,Now);
                Gates.ReloadUntil=Now+FMath::Clamp(Tuning.ReloadSeconds,.3f,15.f);
                ChangeState(EEnemyCombatState::Reload,TEXT("reload behind upright cover edge"));
            }
            if (Now<Gates.ReloadUntil) return true;
            if (!FinishAction(ReloadRequest,CombatAI::ActionStatus::Succeeded,CombatAI::ActionFailure::None))
            { ReturnToCover(Now,TEXT("stale lean reload canceled"),true,false); return true; }
            Magazine=FMath::Clamp(Tuning.MagazineCapacity,1,60); ++Reloads; ReloadRequest={}; Gates.ReloadUntil=0;
            SetCoverPhase(Phase::Protected,Now,TEXT("protected lean reload complete")); return true;
        }
        if (Now<Gates.ReadyAt(NextShot) || Now-CoverPhaseAt<.15) { CoverGate=Gate::Rest; return true; }
        if (!CoverCapsule(Feet(),false) || !CaptureLeanPose())
        {
            CoverGate=Gate::Geometry;
            if (Now-CoverPhaseAt>1.8) ReturnToCover(Now,TEXT("actual neutral pose has no safe lean arc or lane"),true,true);
            return true;
        }
        SetCoverPhase(Phase::Exposing,Now,TEXT("safe actual head/chest/rifle arc; blend torso out"));
    }
    if (CoverPhase==Phase::Exposing || CoverPhase==Phase::Aiming || CoverPhase==Phase::Firing)
    {
        E->StopMovementCommand(); E->SetRifleStance(EGASPALSRifleStance::Aim);
        E->SetRifleLean(LeanSign()*FMath::Clamp(Tuning.CoverLeanDegrees,20.f,35.f));
        if (!AtAnchor || !Settled || E->IsMovementCrouched() || Now-CoverPhaseAt>2)
        { ReturnToCover(Now,TEXT("lean interrupted or exposure deadline"),true,true); return true; }
        const auto Points=LeanPoints();
        if (!LeanSweep(Points,Points))
        { ReturnToCover(Now,TEXT("actual lean body/rifle space blocked"),true,true); return true; }
        if (!AchievedLeanClear()) { CoverGate=Gate::Stand; return true; }
        if (CoverPhase==Phase::Exposing)
        {
            SetCoverPhase(Phase::Aiming,Now,TEXT("signed physical socket displacement achieved; sample current sight"));
            ObservePlayer(); NextSight=Now+FMath::Clamp(Tuning.SightInterval,.05f,1.f);
        }
        if (!bTargetVisible)
        {
            CoverGate=Gate::Contact;
            if (CoverPhase==Phase::Firing || Now-CoverPhaseAt>.45)
                ReturnToCover(Now,TEXT("lean has no current contact; bounded return"),true,false);
            return true;
        }
        CoverGate=Gate::WeaponSafety; AdvanceWeapon(Now,true);
    }
    return true;
}
