#include "EnemyCombatComponent.h"
#include "GASPEnemyFixture.h"
#include "CombatProjectileWorld.h"
#include "Algo/Reverse.h"
#include "Components/CapsuleComponent.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"

// Bounded navigation support for the retained lobby's single walkable layer.
// It reads current collision, never changes geometry and never teleports Mover.
void UEnemyCombatComponent::CapsuleSize(float& Radius, float& HalfHeight) const
{
    Radius = 34; HalfHeight = 86;
    const auto* E = Enemy();
    if (const auto* Capsule = E && E->Foundation ? E->Foundation->FindComponentByClass<UCapsuleComponent>() : nullptr)
    { Radius = Capsule->GetScaledCapsuleRadius(); HalfHeight = Capsule->GetScaledCapsuleHalfHeight(); }
}
FVector UEnemyCombatComponent::Feet() const
{
    const auto* E = Enemy();
    float Radius, HalfHeight; CapsuleSize(Radius, HalfHeight);
    return E && E->Foundation ? E->Foundation->GetActorLocation() - FVector(0, 0, HalfHeight) : Home;
}
void UEnemyCombatComponent::NavigationQuery(FCollisionQueryParams& Query) const
{
    Query.bTraceComplex = false;
    if (const auto* Manager = ACombatProjectileWorld::Find(GetWorld())) Manager->BuildQuery(Query, GetOwner());
    if (const auto* E = Enemy()) Query.AddIgnoredActor(E->Foundation);
}
bool UEnemyCombatComponent::GroundPoint(FVector Reference, FVector& Ground, const FCollisionQueryParams& Query) const
{
    const float Step = FMath::Clamp(Tuning.MaxStepHeight, 0.f, 35.f);
    FHitResult Floor;
    if (!GetWorld()->LineTraceSingleByChannel(Floor, Reference + FVector(0,0,Step + 15.f),
        Reference - FVector(0,0,Step + 20.f), ECC_Pawn, Query) ||
        Floor.ImpactNormal.Z < FMath::Cos(FMath::DegreesToRadians(FMath::Clamp(Tuning.MaxSlopeDegrees, 0.f, 45.f)))) return false;
    Ground = Floor.ImpactPoint;
    // No multi-floor, jump or moving-platform promises in this lobby adapter.
    if (FMath::Abs(Ground.Z - Home.Z) > 160.f) return false;
    float Radius, HalfHeight; CapsuleSize(Radius, HalfHeight);
    return !GetWorld()->OverlapBlockingTestByChannel(Ground + FVector(0,0,HalfHeight + 4.f), FQuat::Identity,
        ECC_Pawn, FCollisionShape::MakeCapsule(Radius + 3.f, HalfHeight), Query);
}
bool UEnemyCombatComponent::WalkSegment(FVector Start, FVector End, const FCollisionQueryParams& Query) const
{
    float Radius, HalfHeight; CapsuleSize(Radius, HalfHeight);
    const float Step = FMath::Clamp(Tuning.MaxStepHeight, 0.f, 35.f);
    const int32 Samples = FMath::Clamp(FMath::CeilToInt(FVector::Dist2D(Start, End) / 35.f), 1, 6);
    FVector Previous = Start;
    for (int32 I = 1; I <= Samples; ++I)
    {
        const FVector Desired = FMath::Lerp(Start, End, float(I) / Samples);
        FVector Ground;
        if (!GroundPoint(Desired, Ground, Query) || FMath::Abs(Ground.Z - Previous.Z) > Step + 2.f) return false;
        // Lift the horizontal sweep to the higher floor so a supported small
        // riser can be taken by Mover. Ceiling clearance is checked at both ends.
        const float Height = FMath::Max(Previous.Z, Ground.Z) + HalfHeight + 4.f;
        FVector A(Previous.X, Previous.Y, Height), B(Ground.X, Ground.Y, Height);
        FHitResult Hit;
        if (GetWorld()->SweepSingleByChannel(Hit, A, B, FQuat::Identity, ECC_Pawn,
            FCollisionShape::MakeCapsule(Radius + 3.f, HalfHeight), Query)) return false;
        Previous = Ground;
    }
    return true;
}

bool UEnemyCombatComponent::PlanPath(FVector Goal, float Acceptance)
{
    Path.Reset(); PathIndex = 0; Nodes.Reset(); OpenNodes.Reset(); CellNodes.Reset();
    bPlanning = bPlanFailed = false; LastPathExpanded = 0;
    PathGoal = Goal; PathAcceptance = FMath::Max(Acceptance, 45.f);
    PathCell = FMath::Clamp(Tuning.NavigationCell, 60.f, 120.f);
    const float Radius = FMath::Clamp(Tuning.NavigationRadius, 400.f, 4000.f);
    const FVector Start = Feet();
    // Refuse destinations beyond the explicit home region, instead of snapping
    // them to a misleading reachable point and endlessly restarting pursuit.
    if (FVector::Dist2D(Start, Home) > Radius || FVector::Dist2D(Goal, Home) > Radius ||
        FMath::Abs(Goal.Z - Home.Z) > 160.f) return false;
    FCollisionQueryParams Query(SCENE_QUERY_STAT(EnemyPathStart), false);
    NavigationQuery(Query);
    FVector Ground;
    if (!GroundPoint(Start, Ground, Query)) return false;
    FPathNode Node;
    Node.Cell = FIntPoint(FMath::RoundToInt((Start.X - Home.X) / PathCell), FMath::RoundToInt((Start.Y - Home.Y) / PathCell));
    Node.Ground = Ground; Node.Cost = 0; Node.bWalkable = true;
    Nodes.Add(Node); CellNodes.Add(Node.Cell, 0); OpenNodes.Add(0);
    bPlanning = true; PlanStarted = GetWorld()->GetTimeSeconds(); ++PathPlans;
    return true;
}

void UEnemyCombatComponent::ContinuePath()
{
    if (!bPlanning) return;
    const double BudgetStart = FPlatformTime::Seconds();
    const int32 ExpansionLimit = FMath::Clamp(Tuning.MaxPathExpansions, 64, 2000);
    const float Radius = FMath::Clamp(Tuning.NavigationRadius, 400.f, 4000.f);
    FCollisionQueryParams Query(SCENE_QUERY_STAT(EnemyPathExpand), false); NavigationQuery(Query);
    // At most 16 nodes per frame, plus a 1.5 ms boundary between expansions.
    // One expansion has at most eight fixed-length edges. Work is resumed next
    // frame, not repeated from scratch. Pending searches time out in five seconds.
    for (int32 Work = 0; Work < 16 && bPlanning; ++Work)
    {
        if (OpenNodes.IsEmpty() || LastPathExpanded >= ExpansionLimit ||
            GetWorld()->GetTimeSeconds() - PlanStarted > 5.f)
        { bPlanning = false; bPlanFailed = true; break; }
        if (Work > 0 && FPlatformTime::Seconds() - BudgetStart > .0015) break;
        int32 BestOpen = 0; float BestScore = TNumericLimits<float>::Max();
        for (int32 I = 0; I < OpenNodes.Num(); ++I)
        {
            const auto& Candidate = Nodes[OpenNodes[I]];
            const float Score = Candidate.Cost + FVector::Dist2D(Candidate.Ground, PathGoal);
            if (Score < BestScore) { BestScore = Score; BestOpen = I; }
        }
        const int32 CurrentIndex = OpenNodes[BestOpen]; OpenNodes.RemoveAtSwap(BestOpen);
        Nodes[CurrentIndex].bClosed = true;
        const FPathNode Current = Nodes[CurrentIndex];
        ++LastPathExpanded;
        if (FVector::Dist2D(Current.Ground, PathGoal) <= PathAcceptance && FMath::Abs(Current.Ground.Z - PathGoal.Z) <= 40.f)
        {
            for (int32 Index = CurrentIndex; Index != 0 && Index != INDEX_NONE; Index = Nodes[Index].Parent)
                Path.Add(Nodes[Index].Ground);
            Algo::Reverse(Path);
            bPlanning = false; bPlanFailed = false;
            ProgressPosition = Feet(); LastProgress = GetWorld()->GetTimeSeconds();
            return;
        }
        for (int32 X = -1; X <= 1; ++X)
            for (int32 Y = -1; Y <= 1; ++Y)
            {
                if (X == 0 && Y == 0) continue;
                const FIntPoint Cell = Current.Cell + FIntPoint(X,Y);
                const FVector Reference(Home.X + Cell.X * PathCell, Home.Y + Cell.Y * PathCell, Current.Ground.Z);
                if (FVector::Dist2D(Reference, Home) > Radius) continue;
                int32 Index;
                if (const int32* Existing = CellNodes.Find(Cell)) Index = *Existing;
                else
                {
                    FPathNode Node; Node.Cell = Cell;
                    Node.bWalkable = GroundPoint(Reference, Node.Ground, Query);
                    Index = Nodes.Add(Node); CellNodes.Add(Cell, Index);
                }
                const auto& Next = Nodes[Index];
                if (!Next.bWalkable || Next.bClosed) continue;
                const float Cost = Current.Cost + FVector::Dist2D(Current.Ground, Next.Ground);
                if (Cost >= Next.Cost || !WalkSegment(Current.Ground, Next.Ground, Query)) continue;
                Nodes[Index].Cost = Cost; Nodes[Index].Parent = CurrentIndex;
                OpenNodes.AddUnique(Index);
            }
    }
}

bool UEnemyCombatComponent::FollowPath(FVector Goal, float Acceptance, double Now)
{
    auto* E = Enemy(); if (!E) return false;
    const FVector Position = Feet();
    if (FVector::Dist2D(Position, Goal) <= Acceptance && FMath::Abs(Position.Z - Goal.Z) <= 40.f)
    { E->StopMovementCommand(); return true; }
    auto Failed = [&]()
    {
        ++PathFailures; ++FailedAttempts;
        Path.Reset(); bPlanning = bPlanFailed = false;
        NextRepath = Now + FMath::Clamp(Tuning.RepathSeconds, .3f, 5.f);
        E->StopMovementCommand();
        return FailedAttempts < 2;
    };
    if (bPlanning)
    {
        E->StopMovementCommand(); ContinuePath();
        if (bPlanFailed) return Failed();
        if (bPlanning) return true;
    }
    const bool bChangedGoal = FVector::Dist2D(Goal, PathGoal) > FMath::Clamp(Tuning.NavigationCell, 60.f,120.f) * 2.f;
    if ((!Path.IsValidIndex(PathIndex) || bChangedGoal) && Now >= NextRepath)
    {
        if (!PlanPath(Goal, Acceptance)) return Failed();
        NextRepath = Now + FMath::Clamp(Tuning.RepathSeconds, .3f, 5.f);
        E->StopMovementCommand();
        return true;
    }
    if (!Path.IsValidIndex(PathIndex)) { E->StopMovementCommand(); return true; }
    while (Path.IsValidIndex(PathIndex) && FVector::Dist2D(Position, Path[PathIndex]) < 32.f) ++PathIndex;
    if (!Path.IsValidIndex(PathIndex)) { E->StopMovementCommand(); return true; }
    FCollisionQueryParams Query(SCENE_QUERY_STAT(EnemyPathFollow), false); NavigationQuery(Query);
    if (!WalkSegment(Position, Path[PathIndex], Query)) return Failed();
    if (FVector::Dist2D(Position, ProgressPosition) > 20.f)
    { ProgressPosition = Position; LastProgress = Now; FailedAttempts = 0; }
    else if (Now - LastProgress > FMath::Clamp(Tuning.StuckSeconds, .5f, 5.f)) return Failed();
    E->SetMovementCommand(Path[PathIndex] - Position, true);
    return true;
}
