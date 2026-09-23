#include "EnemyCombatComponent.h"
#include "GASPEnemyFixture.h"
#include "Components/PrimitiveComponent.h"
#include "Engine/World.h"
#include "Misc/ScopeExit.h"

namespace
{
constexpr float TacticalAcceptance = 45.f;
constexpr float MaxCandidateTravel = 900.f;
}

FVector UEnemyCombatComponent::TacticalDirection(int32 Sector) const
{ return SearchForward.RotateAngleAxis(45.f * Sector, FVector::UpVector); }

void UEnemyCombatComponent::ResetTactics(bool bClearHistory)
{
    Assignment.Cancel(EncounterGeneration); ScanRequest = {};
    TacticalCandidates.Reset(); bTacticalScan = bHeldPosition = bSelectedPosition = false;
    TacticalPhase = CombatAI::TacticalPhase::None;
    HeldPosition = {}; SelectedPosition = {};
    SurfaceIndex = CandidateIndex = TacticalRejected = 0; Transfers = {};
    TacticalQueryCount = TacticalPeakQueries = 0; RejectionCounts = {};
    NextTacticalWork = NextTacticalScan = NextHoldValidation = NextLookAt = 0;
    HoldStartedAt = ScanStartedAt = TacticalMoveStartedAt = 0;
    LookSector = -1; ViewedSectors = 0; TacticalReason.Reset();
    if (bClearHistory) { RejectedPositions = {}; VisitedPositions = {}; }
}

bool UEnemyCombatComponent::TacticalTrace(FVector From, FVector To, FHitResult& Hit, ECollisionChannel Response)
{
    ++TacticalQueryCount;
    FCollisionQueryParams Query(SCENE_QUERY_STAT(EnemyTacticalGeometry), false);
    // Filter both channel response and object type inside the query. A foreground
    // ignore/overlap must not hide a farther blocker; concealed pawns stay excluded.
    FCollisionResponseParams StaticOnly(ECR_Ignore);
    StaticOnly.CollisionResponse.SetResponse(ECC_WorldStatic, ECR_Block);
    return GetWorld()->LineTraceSingleByChannel(Hit, From, To, Response, Query, StaticOnly);
}

bool UEnemyCombatComponent::TacticalGround(FVector Reference, FVector& Ground, CombatAI::PositionRejection& Failure)
{
    Failure = CombatAI::PositionRejection::Support;
    if (Reference.ContainsNaN() || FVector::Dist2D(Reference, Home) > FMath::Clamp(Tuning.NavigationRadius, 400.f, 4000.f)) return false;
    const float Step = FMath::Clamp(Tuning.MaxStepHeight, 0.f, 35.f);
    FHitResult Floor;
    const float Slope = FMath::Cos(FMath::DegreesToRadians(FMath::Clamp(Tuning.MaxSlopeDegrees, 0.f, 45.f)));
    if (!TacticalTrace(Reference + FVector(0,0,Step+15), Reference - FVector(0,0,Step+20), Floor, ECC_Pawn) ||
        Floor.ImpactNormal.Z < Slope || FMath::Abs(Floor.ImpactPoint.Z - Home.Z) > 160) return false;
    Ground = Floor.ImpactPoint;
    float Radius, HalfHeight; CapsuleSize(Radius, HalfHeight);
    // A single center ray is not proof of capsule support on a ledge.
    for (int32 I = 0; I < 4; ++I)
    {
        const FVector Offset = FVector::ForwardVector.RotateAngleAxis(90.f * I, FVector::UpVector) * (Radius * .7f);
        if (!TacticalTrace(Ground + Offset + FVector(0,0,Step+15), Ground + Offset - FVector(0,0,Step+20), Floor, ECC_Pawn) ||
            Floor.ImpactNormal.Z < Slope || FMath::Abs(Floor.ImpactPoint.Z - Ground.Z) > Step + 2) return false;
    }
    FCollisionQueryParams Query(SCENE_QUERY_STAT(EnemyTacticalCapsule), false);
    ++TacticalQueryCount;
    if (GetWorld()->OverlapAnyTestByObjectType(Ground + FVector(0,0,HalfHeight+4), FQuat::Identity,
        FCollisionObjectQueryParams(ECC_WorldStatic), FCollisionShape::MakeCapsule(Radius+3, HalfHeight), Query))
    { Failure = CombatAI::PositionRejection::Capsule; return false; }
    Failure = CombatAI::PositionRejection::None;
    return true;
}

bool UEnemyCombatComponent::TacticalWalk(FVector From, FVector To)
{
    const float Distance = FVector::Dist2D(From, To);
    if (Distance > MaxCandidateTravel || FMath::Abs(From.Z-To.Z) > 160) return false;
    const int32 Steps = FMath::Clamp(FMath::CeilToInt(Distance / 35.f), 1, 26);
    const float StepHeight = FMath::Clamp(Tuning.MaxStepHeight, 0.f, 35.f);
    float Radius, HalfHeight; CapsuleSize(Radius, HalfHeight);
    FCollisionQueryParams Query(SCENE_QUERY_STAT(EnemyTacticalRoute), false);
    FVector Previous = From;
    for (int32 I = 1; I <= Steps; ++I)
    {
        FVector Ground; CombatAI::PositionRejection Failure;
        if (!TacticalGround(FMath::Lerp(From, To, float(I)/Steps), Ground, Failure) || FMath::Abs(Ground.Z-Previous.Z) > StepHeight+2) return false;
        const double Height = FMath::Max(Previous.Z, Ground.Z) + HalfHeight + 4;
        FHitResult Hit; ++TacticalQueryCount;
        if (GetWorld()->SweepSingleByObjectType(Hit, FVector(Previous.X,Previous.Y,Height), FVector(Ground.X,Ground.Y,Height),
            FQuat::Identity, FCollisionObjectQueryParams(ECC_WorldStatic), FCollisionShape::MakeCapsule(Radius+3,HalfHeight), Query)) return false;
        Previous = Ground;
    }
    return FMath::Abs(Previous.Z-To.Z) <= StepHeight+2;
}

UEnemyCombatComponent::FTacticalPosition UEnemyCombatComponent::AssessTacticalPosition(FVector Reference, FVector From, bool bCheckRoute)
{
    const int32 QueriesBefore = TacticalQueryCount;
    ON_SCOPE_EXIT { TacticalPeakQueries = FMath::Max(TacticalPeakQueries, TacticalQueryCount - QueriesBefore); };
    FTacticalPosition P; P.Ground = Reference;
    auto& F = P.Features;
    CombatAI::PositionRejection Failure;
    if (!TacticalGround(Reference, P.Ground, Failure))
    { P.Rating.Rejection = Failure; return P; }
    F.Supported = F.CapsuleClear = true;
    F.Travel = FVector::Dist2D(From, P.Ground);
    F.RouteClear = !bCheckRoute || (F.Travel <= MaxCandidateTravel && TacticalWalk(From, P.Ground));
    if (!F.RouteClear) { P.Rating.Rejection = CombatAI::PositionRejection::Route; return P; }
    FCollisionQueryParams Query(SCENE_QUERY_STAT(EnemyTacticalWeapon), false);
    for (int32 I = 0; I < CombatAI::TacticalSectors; ++I)
    {
        const FVector Direction = TacticalDirection(I);
        FHitResult Low, High;
        const FVector Chest = P.Ground + FVector(0,0,95), Eye = P.Ground + FVector(0,0,150);
        const bool bLow = TacticalTrace(Chest, Chest + Direction*600, Low);
        const bool bHigh = TacticalTrace(Eye, Eye + Direction*600, High);
        const double LowDistance = bLow ? Low.Distance : 600;
        const double HighDistance = bHigh ? High.Distance : 600;
        F.OpenDistance[I] = FMath::Min(LowDistance, HighDistance);
        if (bLow && bHigh && LowDistance <= 160 && HighDistance <= 160 &&
            Low.GetComponent()->GetCollisionResponseToChannel(ECC_Pawn) == ECR_Block &&
            High.GetComponent()->GetCollisionResponseToChannel(ECC_Pawn) == ECR_Block &&
            FMath::Abs(Low.ImpactNormal.Z) < .35 && FMath::Abs(High.ImpactNormal.Z) < .35)
            F.ProtectionMask |= 1u << I;
        if (F.OpenDistance[I] >= 220)
        {
            FHitResult Weapon; ++TacticalQueryCount;
            const FVector WeaponRoot = P.Ground + FVector(0,0,125);
            if (!GetWorld()->SweepSingleByObjectType(Weapon, WeaponRoot, WeaponRoot + Direction*120, FQuat::Identity,
                FCollisionObjectQueryParams(ECC_WorldStatic), FCollisionShape::MakeSphere(10), Query)) F.WeaponMask |= 1u << I;
        }
        // Four independently supported local exits, not just an empty sight ray.
        if (I % 2 == 0 && TacticalWalk(P.Ground, P.Ground + Direction*105)) F.EscapeMask |= 1u << I;
    }
    const float Age = FMath::Max(0.0, GetWorld()->GetTimeSeconds() - Memory.LastSeen);
    const float Uncertainty = FMath::Clamp(180.f + Age*35.f, 180.f, 500.f);
    const FVector Lateral = FVector::CrossProduct(FVector::UpVector, SearchForward);
    for (int32 I = 0; I < 3; ++I)
    {
        FHitResult Hit;
        const FVector Region = SearchAnchor + Lateral*((I-1)*Uncertainty) + FVector(0,0,130);
        if (!TacticalTrace(P.Ground + FVector(0,0,130), Region, Hit)) F.RegionVisibleMask |= 1u << I;
    }
    F.Exposure = CombatAI::BitCount(F.RegionVisibleMask) / 3.0;
    P.Rating = CombatAI::RatePosition(F);
    return P;
}

void UEnemyCombatComponent::AddTacticalCandidate(FVector Ground)
{
    if (TacticalCandidates.Num() >= CombatAI::MaxTacticalCandidates || Ground.ContainsNaN()) return;
    for (const auto& P : TacticalCandidates) if (FVector::Dist2D(P.Ground, Ground) < 65) return;
    FTacticalPosition P; P.Ground = Ground; TacticalCandidates.Add(P);
}

void UEnemyCombatComponent::BeginTacticalScan(double Now)
{
    Transfers.Refresh(Now);
    ScanRequest = Assignment.Token; ScanOrigin = Feet(); ScanStartedAt = Now;
    SurfaceIndex = CandidateIndex = TacticalRejected = 0; RejectionCounts = {};
    TacticalCandidates.Reset(CombatAI::MaxTacticalCandidates); AddTacticalCandidate(ScanOrigin);
    bTacticalScan = true; NextTacticalWork = Now;
    if (!bHeldPosition) TacticalPhase = CombatAI::TacticalPhase::Scanning;
    TacticalReason = TEXT("bounded local collision scan; current position included");
    RecordTrace(CombatAI::Event::Tactical, *TacticalReason);
}

void UEnemyCombatComponent::AdvanceTacticalScan(double Now)
{
    if (!bTacticalScan || Now < NextTacticalWork) return;
    if (!Assignment.Accepts(ScanRequest)) { bTacticalScan = false; return; }
    // One surface ray OR one candidate assessment per tick, at most 40/world second.
    // No A-star query per candidate; only proven direct supported strips qualify.
    NextTacticalWork = Now + .025;
    const int32 QueriesBefore = TacticalQueryCount;
    if (SurfaceIndex < 8)
    {
        const FVector Direction = TacticalDirection(SurfaceIndex++);
        const FVector Origin = ScanOrigin + FVector(0,0,100);
        FHitResult Hit;
        if (TacticalTrace(Origin, Origin + Direction * FMath::Clamp(Tuning.TacticalRadius, 250.f, 750.f), Hit, ECC_Pawn) &&
            FMath::Abs(Hit.ImpactNormal.Z) < .35)
        {
            float Radius, HalfHeight; CapsuleSize(Radius, HalfHeight);
            const FVector Normal = Hit.ImpactNormal.GetSafeNormal2D();
            const FVector Tangent = FVector::CrossProduct(FVector::UpVector, Normal);
            FVector Surface = Hit.ImpactPoint + Normal * (Radius + 26.f);
            Surface.Z = ScanOrigin.Z;
            AddTacticalCandidate(Surface);
            AddTacticalCandidate(Surface + Tangent*140);
            AddTacticalCandidate(Surface - Tangent*140);
        }
        if (SurfaceIndex == 8)
            for (int32 I = 0; I < 4; ++I)
                AddTacticalCandidate(ScanOrigin + TacticalDirection(I*2) * FMath::Clamp(Tuning.SearchRadius, 200.f, 400.f));
    }
    else if (TacticalCandidates.IsValidIndex(CandidateIndex))
    {
        auto& P = TacticalCandidates[CandidateIndex++];
        if (FVector::Dist2D(P.Ground, ScanOrigin) > 60 && RejectedPositions.Contains(P.Ground.X, P.Ground.Y, Now))
            P.Rating.Rejection = CombatAI::PositionRejection::RecentFailure;
        else P = AssessTacticalPosition(P.Ground, ScanOrigin, true);
        if (!P.Rating.Valid)
        { ++TacticalRejected; ++RejectionCounts[static_cast<size_t>(P.Rating.Rejection)]; }
    }
    TacticalPeakQueries = FMath::Max(TacticalPeakQueries, TacticalQueryCount - QueriesBefore);
    if ((SurfaceIndex >= 8 && CandidateIndex >= TacticalCandidates.Num()) || Now - ScanStartedAt >= 4)
    {
        bTacticalScan = false;
        ChooseTacticalPosition(Now);
    }
}

void UEnemyCombatComponent::ChooseTacticalPosition(double Now)
{
    if (!Assignment.Accepts(ScanRequest)) return;
    // Actual feet can drift while braking. A displaced scan cannot authorize travel.
    if (FVector::Dist2D(Feet(), ScanOrigin) > 60)
    { NextTacticalScan = Now + .5; TacticalReason = TEXT("scan origin displaced; rebuild at actual feet"); return; }
    FTacticalPosition Current = AssessTacticalPosition(Feet(), Feet(), false);
    const bool bWasHolding = TacticalPhase == CombatAI::TacticalPhase::Holding && bHeldPosition && Current.Rating.Valid;
    if (!bWasHolding) HoldStartedAt = Now;
    int32 Best = INDEX_NONE;
    double Score = Current.Rating.Valid ? Current.Rating.Score : CombatAI::InvalidPositionScore;
    // First seek protection without an artificial hold commitment. Subsequent
    // scans compare against freshly validated feet, never the old goal's score.
    const double HoldAge = bWasHolding ? Now - HoldStartedAt : TNumericLimits<double>::Max();
    for (int32 I = 0; I < CandidateIndex; ++I)
    {
        const auto& P = TacticalCandidates[I];
        const double Travel = FVector::Dist2D(Feet(), P.Ground);
        if (!Transfers.CanStart() || Travel < 100 ||
            RejectedPositions.Contains(P.Ground.X, P.Ground.Y, Now) ||
            MoveBackoff.Blocks(P.Ground.X, P.Ground.Y, Now)) continue;
        if (!CombatAI::WorthSwitching(Current.Rating, P.Rating, HoldAge, Travel,
            VisitedPositions.Contains(P.Ground.X, P.Ground.Y, Now), FMath::Clamp(Tuning.TacticalCommitSeconds, 1.f, 10.f),
            FMath::Clamp(Tuning.TacticalSwitchMargin, 3.f, 30.f), FMath::Clamp(Tuning.TacticalProbeSeconds, 3.f, 20.f))) continue;
        const double Utility = P.Rating.Score + (HoldAge >= Tuning.TacticalProbeSeconds ?
            FMath::Min(CombatAI::BitCount(P.Rating.OpenMask & ~Current.Rating.OpenMask), 2)*12 : 0);
        if (Utility > Score) { Best = I; Score = Utility; }
    }
    NextTacticalScan = Now + FMath::Clamp(Tuning.TacticalReassessSeconds, 1.5f, 8.f);
    if (Best != INDEX_NONE)
    {
        // The incremental scan is a proposal cache, not permanent geometry truth.
        // Refresh the single winner before committing movement as well as at arrival.
        const auto Winner = AssessTacticalPosition(TacticalCandidates[Best].Ground, Feet(), true);
        if (!CombatAI::WorthSwitching(Current.Rating, Winner.Rating, HoldAge, Winner.Features.Travel,
            VisitedPositions.Contains(Winner.Ground.X, Winner.Ground.Y, Now), FMath::Clamp(Tuning.TacticalCommitSeconds, 1.f, 10.f),
            FMath::Clamp(Tuning.TacticalSwitchMargin, 3.f, 30.f), FMath::Clamp(Tuning.TacticalProbeSeconds, 3.f, 20.f)))
        { RejectTacticalPosition(Winner.Ground, Winner.Rating.Valid ? CombatAI::PositionRejection::Arrival : Winner.Rating.Rejection, Now); return; }
        ClearIntent(); SelectedPosition = Winner; bSelectedPosition = true;
        bHeldPosition = false; SearchGoal = SelectedPosition.Ground; Transfers.Start();
        TacticalMoveStartedAt = Now; NextRepath = 0; FailedAttempts = 0;
        TacticalPhase = CombatAI::TacticalPhase::Moving;
        TacticalReason = TEXT("better validated protection or informative adjacent observation");
    }
    else
    {
        HeldPosition = Current; bHeldPosition = Current.Rating.Valid;
        bSelectedPosition = false; SearchGoal = Feet();
        TacticalPhase = bHeldPosition ? CombatAI::TacticalPhase::Holding : CombatAI::TacticalPhase::Fallback;
        TacticalReason = !bHeldPosition ? TEXT("no supported position with useful weapon-facing space; alert fallback") :
            Current.Rating.Protection < .1 ? TEXT("no better reachable protection; observe useful open approaches") :
            TEXT("retain validated protection; no worthwhile unvisited alternative");
        NextHoldValidation = Now + 1;
        if (LookSector < 0) NextLookAt = 0;
    }
    RecordTrace(CombatAI::Event::Tactical, *TacticalReason);
}

void UEnemyCombatComponent::RejectTacticalPosition(const FVector& Ground, CombatAI::PositionRejection Why, double Now)
{
    RejectedPositions.Remember(Ground.X, Ground.Y, Now + 12);
    ++TacticalRejected; ++RejectionCounts[static_cast<size_t>(Why)];
    ClearIntent(CombatAI::ActionFailure::Route);
    bSelectedPosition = bHeldPosition = bTacticalScan = false; LookSector = -1;
    TacticalPhase = CombatAI::TacticalPhase::Fallback;
    NextHoldValidation = 0; NextTacticalScan = !Transfers.CanStart() ? FMath::Max(Now+4, Transfers.ResetAt) : Now+.5;
    TacticalReason = Why == CombatAI::PositionRejection::Arrival ? TEXT("actual arrival failed protection/facing; reject destination") :
        TEXT("tactical route or held geometry failed; bounded observation fallback");
    RecordTrace(CombatAI::Event::Tactical, *TacticalReason);
}

void UEnemyCombatComponent::SetObservationFacing(double Now)
{
    if (Now < NextLookAt) return;
    if (bHeldPosition)
    {
        if ((ViewedSectors & HeldPosition.Rating.OpenMask) == HeldPosition.Rating.OpenMask) ViewedSectors = 0;
        LookSector = CombatAI::ObservationSector(HeldPosition.Features, ViewedSectors);
        if (LookSector >= 0)
        {
            ViewedSectors |= 1u << LookSector;
            SearchLook = Feet() + TacticalDirection(LookSector) * FMath::Clamp(HeldPosition.Features.OpenDistance[LookSector]*.75, 220.0, 450.0) + FVector(0,0,140);
        }
    }
    else
    {
        // No valid standing/weapon space: inspect only a freshly clear horizontal
        // sector. If every sector is blocked, do not assert a valid facing.
        LookSector = -1;
        for (int32 I = 0; I < 8; ++I)
        {
            const int32 Sector = (CandidateIndex + I) % 8;
            FHitResult Hit; const FVector Origin = Feet() + FVector(0,0,140);
            if (!TacticalTrace(Origin, Origin + TacticalDirection(Sector)*250, Hit))
            { LookSector = Sector; SearchLook = Origin + TacticalDirection(Sector)*250; break; }
        }
    }
    NextLookAt = Now + FMath::Clamp(Tuning.SearchSeconds, .5f, 3.f);
}

void UEnemyCombatComponent::HoldTacticalPosition(double Now)
{
    auto* E = Enemy(); E->StopMovementCommand();
    if (Now >= NextHoldValidation)
    {
        const auto Before = HeldPosition.Rating;
        const int32 QueriesBefore = TacticalQueryCount;
        HeldPosition = AssessTacticalPosition(Feet(), Feet(), false);
        TacticalPeakQueries = FMath::Max(TacticalPeakQueries, TacticalQueryCount - QueriesBefore);
        bHeldPosition = HeldPosition.Rating.Valid;
        NextHoldValidation = Now + 1;
        if (!bHeldPosition || (Before.Valid && HeldPosition.Rating.Protection + .15 < Before.Protection))
        {
            // Lost prerequisites override commitment and invalidate cached work.
            if (Before.Valid)
            {
                bTacticalScan = false;
                Assignment.Assign(EncounterGeneration, Assignment.Objective, Assignment.EvidenceId, Now);
            }
            TacticalPhase = CombatAI::TacticalPhase::Fallback;
            NextTacticalScan = FMath::Min(NextTacticalScan, Now);
            TacticalReason = TEXT("held geometry changed; reassess actual feet");
        }
        if (LookSector < 0 || (HeldPosition.Rating.OpenMask & (1u << LookSector)) == 0) NextLookAt = 0;
    }
    SetObservationFacing(Now);
    // Aim/strafe inputs turn the adopted foundation, with no follow-player seam.
    E->SetRifleStance(LookSector >= 0 ? EGASPALSRifleStance::Aim : EGASPALSRifleStance::Ready);
    if (LookSector >= 0) E->SetRifleAimTarget(SearchLook);
    else E->SetRifleFollowPlayer(false);
    EnsureAction(CombatAI::ActionKind::Observe, Now);
}

void UEnemyCombatComponent::AdvanceSearch(double Now)
{
    if (!Memory.Alert || !Memory.HasObservation) return;
    auto* E = Enemy(); E->SetCrouchCommand(false);
    if (bSelectedPosition)
    {
        E->SetRifleStance(EGASPALSRifleStance::Ready);
        E->SetRifleFollowPlayer(false); // Locomotion faces travel until arrival.
        if (FVector::Dist2D(Feet(), SearchGoal) <= TacticalAcceptance && FMath::Abs(Feet().Z - SearchGoal.Z) <= 40)
        {
            const auto Arrived = AssessTacticalPosition(Feet(), Feet(), false);
            // A path's tolerance is not evidence of protection at actual feet.
            if (!CombatAI::AcceptTacticalArrival(SelectedPosition.Rating, Arrived.Rating))
            { RejectTacticalPosition(SearchGoal, CombatAI::PositionRejection::Arrival, Now); }
            else
            {
                FinishAction(Action.Token, CombatAI::ActionStatus::Succeeded, CombatAI::ActionFailure::None);
                RecordPath(CombatAI::PathOutcome::Arrived, TEXT("actual tactical feet and useful facing validated"));
                ClearIntent(); HeldPosition = Arrived; bHeldPosition = true; bSelectedPosition = false;
                HoldStartedAt = Now; NextHoldValidation = Now+1; NextLookAt = 0; ViewedSectors = 0;
                LookSector = -1; TacticalPhase = CombatAI::TacticalPhase::Holding;
                VisitedPositions.Remember(Feet().X, Feet().Y, Now+20);
                NextTacticalScan = Now + FMath::Clamp(Tuning.TacticalReassessSeconds, 1.5f, 8.f);
                TacticalReason = Arrived.Rating.Protection >= .1 ? TEXT("protected observation at validated actual feet") : TEXT("informative observation at validated actual feet; no local protection");
                RecordTrace(CombatAI::Event::Tactical, *TacticalReason);
            }
        }
        else if (Now - TacticalMoveStartedAt > 10 || !FollowPath(SearchGoal, TacticalAcceptance, Now, CombatAI::MovePurpose::Search))
            RejectTacticalPosition(SearchGoal, CombatAI::PositionRejection::Route, Now);
        return;
    }
    HoldTacticalPosition(Now);
    if (!bTacticalScan && Now >= NextTacticalScan)
    {
        // At most two travel requests per 12-world-second window. Fixed history
        // survives scans and prevents retrying the same failed neighborhood.
        BeginTacticalScan(Now);
    }
    AdvanceTacticalScan(Now);
}
