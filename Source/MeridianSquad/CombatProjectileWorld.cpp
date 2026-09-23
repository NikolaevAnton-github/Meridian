#include "CombatProjectileWorld.h"
#include "GASPEnemyFixture.h"
#include "EnemyCombatComponent.h"
#include "OpeningLobbyCharacter.h"
#include "CombatTarget.h"
#include "CombatRifleComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "DrawDebugHelpers.h"
#include "Engine/World.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInterface.h"
#include "Serialization/JsonSerializer.h"

namespace
{
constexpr float BulletRadius = .5f;

TSharedPtr<FJsonValue> JsonVector(const FVector& V)
{
    return MakeShared<FJsonValueArray>(TArray<TSharedPtr<FJsonValue>>{
        MakeShared<FJsonValueNumber>(V.X), MakeShared<FJsonValueNumber>(V.Y), MakeShared<FJsonValueNumber>(V.Z)});
}
double CapsuleDistanceSquared(const FVector& Point, double SegmentHalf)
{
    const FVector Nearest(0, 0, FMath::Clamp(Point.Z, -SegmentHalf, SegmentHalf));
    return FVector::DistSquared(Point, Nearest);
}
// Continuous relative sweep against an upright character capsule. This remains
// a segment when the bullet is stopped and the character moves across it.
bool CapsuleContact(const FVector& Start, const FVector& End, double Radius, double HalfHeight, double& Time)
{
    const double SegmentHalf = FMath::Max(0.0, HalfHeight - Radius);
    if (CapsuleDistanceSquared(Start, SegmentHalf) <= Radius * Radius)
    {
        Time = 0.0;
        return true;
    }
    const FVector Direction = End - Start;
    double First = 2.0;
    auto Roots = [&](double A, double B, double C, auto Accept)
    {
        const double Discriminant = B * B - 4.0 * A * C;
        if (A < 1.e-12 || Discriminant < 0.0) return;
        const double Root = FMath::Sqrt(Discriminant);
        for (double T : {(-B - Root) / (2.0 * A), (-B + Root) / (2.0 * A)})
            if (T >= 0.0 && T <= 1.0 && T < First && Accept(T)) First = T;
    };
    Roots(Direction.X * Direction.X + Direction.Y * Direction.Y,
        2.0 * (Start.X * Direction.X + Start.Y * Direction.Y),
        Start.X * Start.X + Start.Y * Start.Y - Radius * Radius,
        [&](double T) { return FMath::Abs(Start.Z + Direction.Z * T) <= SegmentHalf; });
    for (double Z : {-SegmentHalf, SegmentHalf})
    {
        const FVector Offset = Start - FVector(0, 0, Z);
        Roots(Direction.SizeSquared(), 2.0 * FVector::DotProduct(Offset, Direction),
            Offset.SizeSquared() - Radius * Radius, [](double) { return true; });
    }
    Time = First;
    return First <= 1.0;
}
}

ACombatProjectileWorld::ACombatProjectileWorld()
{
    PrimaryActorTick.bCanEverTick = true;
    // Camera updates follow PostPhysics. Sample it and character movement once
    // at the same end boundary, then reconstruct this local combat interval.
    PrimaryActorTick.TickGroup = TG_PostUpdateWork;
    SetActorEnableCollision(false);
}
void ACombatProjectileWorld::BeginPlay()
{
    Super::BeginPlay();
    Bullets.Reserve(256);
    Impacts.Reserve(48);
    RecordCapsules();
    // Replace the old transient comparison (including its obstructing test boxes).
    // No fixtures are saved into the retained map; test-box source/probes survive.
    // Legacy enemy implementation/assets remain available for historical probes.
    // MSQ-70 defaults to one combat opponent; the three passive fixture profiles
    // remain available through msq.EnemyCombat fixtures.
    SetPhysicsDummyEnabled(bEnablePhysicsDummy);
}
ACombatProjectileWorld* ACombatProjectileWorld::Find(const UWorld* World)
{
    for (TActorIterator<ACombatProjectileWorld> It(World); It; ++It) return *It;
    return nullptr;
}
void ACombatProjectileWorld::SetProjectileTimeScale(float Scale)
{
    if (FMath::IsFinite(Scale)) ProjectileTimeScale = FMath::Clamp(Scale, 0.f, 1.f);
}
void ACombatProjectileWorld::BuildQuery(FCollisionQueryParams& Query, const AActor* Ignore) const
{
    Query.bFindInitialOverlaps = true;
    Query.bReturnPhysicalMaterial = true;
    if (Ignore) Query.AddIgnoredActor(Ignore);
    // Characters are handled by continuous relative sweeps. FP physics props
    // are presentation only, and never become invisible gameplay cover.
    for (TActorIterator<AActor> It(GetWorld()); It; ++It)
        if (It->IsA<ACharacter>() || It->IsA<APhysicsControlDummy>() || AGASPEnemyFixture::FromFoundation(*It) || It->GetClass()->GetName().StartsWith(TEXT("BP_TFA_Physics")))
            Query.AddIgnoredActor(*It);
}
bool ACombatProjectileWorld::TraceEnemyAim(const FVector& Start, const FVector& End, double BirthTime, FHitResult& Hit) const
{
    bool Found = false;
    double Nearest = 1.0;
    const auto Samples = bProcessingFrame ? CapsulesAt(BirthTime) : SampleCapsules();
    for (const auto& Entry : Samples)
    {
        ACharacter* Character = Entry.Key.Get();
        // A prior birth can kill an enemy after this frame's spheres were cached.
        // Match the damage query's live collision gate before considering them.
        if (!IsValid(Character) || !Character->GetCapsuleComponent()->IsQueryCollisionEnabled()) continue;
        for (const auto& Sphere : Entry.Value.Regions)
        {
            double Time;
            if (CapsuleContact(Start - Sphere.Center, End - Sphere.Center, Sphere.Radius, Sphere.Radius, Time) && Time < Nearest)
            {
                Nearest = Time;
                const FVector Point = FMath::Lerp(Start, End, Time);
                Hit = FHitResult(Character, Character->GetMesh(), Point, (Point - Sphere.Center).GetSafeNormal());
                Hit.BoneName = Sphere.Bone;
                Hit.bBlockingHit = true;
                Hit.Time = Time;
                Hit.Distance = FVector::Distance(Start, Point);
                Found = true;
            }
        }
    }
    // Physical contact eligibility is independent of health and movement capsules.
    const auto Physical = bProcessingFrame ? DummiesAt(BirthTime) : SampleDummies();
    for (const auto& Entry : Physical)
        if (const auto* Dummy = Entry.Key.Get())
        {
            FHitResult BodyHit;
            if (Dummy->TracePhysicalPose(Entry.Value, Entry.Value, Start, End, 0, BodyHit) && BodyHit.Time < Nearest)
            { Hit = BodyHit; Nearest = BodyHit.Time; Found = true; }
        }
    return Found;
}
int64 ACombatProjectileWorld::Launch(AActor* Shooter, const FVector& Position, const FVector& Velocity, float Damage)
{
    // Listener-created rounds start at the next frame boundary. They may not
    // inherit a substep whose collision queries have already completed.
    return LaunchTimed(Shooter, Position, Velocity, Damage, bProcessingFrame ? FrameEnd : FiringClock);
}
int64 ACombatProjectileWorld::LaunchTimed(AActor* Shooter, const FVector& Position, const FVector& Velocity, float Damage, double Time)
{
    if (Bullets.Num() >= FMath::Clamp(MaxProjectiles, 1, 256) || Position.ContainsNaN() ||
        Velocity.ContainsNaN() || Velocity.IsNearlyZero() || !FMath::IsFinite(Damage) || Damage <= 0.f)
    {
        ++RejectedCount;
        return 0;
    }
    FBullet Bullet;
    Bullet.Id = NextShotId++;
    Bullet.Shooter = Shooter;
    Bullet.ShooterIdentity = Shooter ? FName(*Shooter->GetPathName()) : NAME_None;
    if (const APawn* Pawn = Cast<APawn>(Shooter)) Bullet.Instigator = Pawn->GetController();
    if (const auto* Fixture = Cast<AGASPEnemyFixture>(Shooter); Fixture && Fixture->Foundation)
        Bullet.Instigator = Fixture->Foundation->GetController();
    Bullet.Position = Position;
    Bullet.Velocity = Velocity;
    Bullet.Damage = Damage;
    if (const auto* Rifle = Shooter ? Shooter->FindComponentByClass<UCombatRifleComponent>() : nullptr)
    {
        Bullet.FallImpulseMultiplier = Rifle->FallImpulseMultiplier;
        Bullet.DeathImpulseMultiplier = Rifle->DeathImpulseMultiplier;
    }
    Bullet.Born = FPlatformTime::Seconds();
    Bullet.BirthTime = Time;
    Bullet.EligibleFrame = FrameSerial + (bAdvancing || !bProcessingFrame ? 1 : 0);
    // New rounds cannot contact capsule motion that happened before their birth.
    // Keep per-round samples so firing never truncates older suspended rounds' history.
    Bullet.BirthCapsules = bProcessingFrame ? CapsulesAt(Time) : SampleCapsules();
    Bullet.BirthDummies = bProcessingFrame ? DummiesAt(Time) : SampleDummies();
    Bullet.bLaunchClear = true;
    if (const ACharacter* Character = Cast<ACharacter>(Shooter))
    {
        if (const auto* Capsule = Bullet.BirthCapsules.Find(const_cast<ACharacter*>(Character)))
            Bullet.bLaunchClear = CapsuleDistanceSquared(Position - Capsule->Center,
                Capsule->HalfHeight - Capsule->Radius) > FMath::Square(Capsule->Radius + BulletRadius + 2.f);
    }
    const auto* PhysicalShooter = Cast<APhysicsControlDummy>(Shooter);
    if (!PhysicalShooter) PhysicalShooter = AGASPEnemyFixture::FromFoundation(Shooter);
    if (PhysicalShooter)
        if (const auto* Pose = Bullet.BirthDummies.Find(const_cast<APhysicsControlDummy*>(PhysicalShooter)))
        {
            FHitResult Clearance;
            Bullet.bLaunchClear = !PhysicalShooter->TracePhysicalPose(*Pose, *Pose, Position, Position,
                BulletRadius + 2.f, Clearance);
        }
    Bullets.Add(Bullet);
    ++LaunchedCount;
    return Bullet.Id;
}
void ACombatProjectileWorld::RecordCapsules()
{
    PreviousCapsules = SampleCapsules();
    PreviousDummies = SampleDummies();
}
TMap<TWeakObjectPtr<ACharacter>, ACombatProjectileWorld::FCapsuleSample> ACombatProjectileWorld::SampleCapsules() const
{
    TMap<TWeakObjectPtr<ACharacter>, FCapsuleSample> Samples;
    for (TActorIterator<ACharacter> It(GetWorld()); It; ++It)
    {
        const auto* Capsule = It->GetCapsuleComponent();
        if (Capsule->IsQueryCollisionEnabled())
        {
            FCapsuleSample Sample{Capsule->GetComponentLocation(), Capsule->GetScaledCapsuleRadius(), Capsule->GetScaledCapsuleHalfHeight(), {}};
            if (const auto* Target = Cast<AEnemyPrototypeCharacter>(*It)) Sample.Regions = Target->SampleHitSpheres();
            Samples.Add(*It, MoveTemp(Sample));
        }
    }
    return Samples;
}
TMap<TWeakObjectPtr<ACharacter>, ACombatProjectileWorld::FCapsuleSample> ACombatProjectileWorld::CapsulesAt(double Time) const
{
    auto Samples = FrameEndCapsules;
    const double Alpha = FrameEnd > FrameStart ? FMath::Clamp((Time - FrameStart) / (FrameEnd - FrameStart), 0.0, 1.0) : 1.0;
    for (auto& Entry : Samples)
        if (const auto* Old = FrameStartCapsules.Find(Entry.Key))
        {
            Entry.Value.Center = FMath::Lerp(Old->Center, Entry.Value.Center, Alpha);
            // Crouch-size transitions use a conservative envelope throughout.
            Entry.Value.Radius = FMath::Max(Old->Radius, Entry.Value.Radius);
            Entry.Value.HalfHeight = FMath::Max(Old->HalfHeight, Entry.Value.HalfHeight);
            if (Old->Regions.Num() == Entry.Value.Regions.Num())
                for (int32 Index = 0; Index < Entry.Value.Regions.Num(); ++Index)
                    Entry.Value.Regions[Index].Center = FMath::Lerp(Old->Regions[Index].Center, Entry.Value.Regions[Index].Center, Alpha);
        }
    return Samples;
}
TMap<TWeakObjectPtr<UPrimitiveComponent>, ACombatProjectileWorld::FBlockerSample> ACombatProjectileWorld::SampleBlockers() const
{
    TMap<TWeakObjectPtr<UPrimitiveComponent>, FBlockerSample> Samples;
    for (TActorIterator<AActor> It(GetWorld()); It; ++It)
    {
        if (It->IsA<ACharacter>() || It->IsA<APhysicsControlDummy>() || AGASPEnemyFixture::FromFoundation(*It) || It->GetClass()->GetName().StartsWith(TEXT("BP_TFA_Physics"))) continue;
        TInlineComponentArray<UPrimitiveComponent*> Parts(*It);
        for (UPrimitiveComponent* Part : Parts)
            if (Part->IsQueryCollisionEnabled() && Part->GetCollisionResponseToChannel(ECC_Visibility) == ECR_Block)
                Samples.Add(Part, {Part->GetComponentTransform(), Part->Bounds.BoxExtent});
    }
    return Samples;
}
bool ACombatProjectileWorld::BlockersMatch(const TMap<TWeakObjectPtr<UPrimitiveComponent>, FBlockerSample>& Samples) const
{
    if (!bHaveBlockerSample) return true;
    if (Samples.Num() != PreviousBlockers.Num()) return false;
    for (const auto& Entry : Samples)
    {
        const auto* Old = PreviousBlockers.Find(Entry.Key);
        if (!Old || !Old->Transform.Equals(Entry.Value.Transform, 1.e-6) || !Old->Extent.Equals(Entry.Value.Extent, 1.e-4)) return false;
    }
    return true;
}
void ACombatProjectileWorld::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    const double Now = FPlatformTime::Seconds();
    ACharacter* Player = UGameplayStatics::GetPlayerCharacter(GetWorld(), 0);
    AdvanceFrame(DeltaSeconds, Now, Player ? Player->FindComponentByClass<UCombatRifleComponent>() : nullptr);
    Impacts.RemoveAll([&](const FImpact& Impact) { return Now - Impact.Born > .3; });
    for (const FImpact& Impact : Impacts)
    {
        const float Age = float(Now - Impact.Born);
        const float Size = .4f + Age * 12.f;
        const FColor Color = Impact.bMetal ? FColor(255, 195, 70) : FColor(170, 165, 150);
        const FVector Center = Impact.Position + Impact.Normal * 1.f;
        FVector U, V;
        Impact.Normal.FindBestAxisVectors(U, V);
        for (int32 I = 0; I < 5; ++I)
        {
            const float Angle = I * 2.399963f + float(FMath::Fmod(Impact.Position.X, 6.0));
            const FVector Direction = U * FMath::Cos(Angle) + V * FMath::Sin(Angle) + Impact.Normal * .7f;
            const FVector Point = Center + Direction * Size * (.3f + I * .14f);
            if (Impact.bMetal)
                DrawDebugLine(GetWorld(), Point, Point + Direction * Size * .45f, Color, false, 0.f, 0, 0.f);
            else
                DrawDebugPoint(GetWorld(), Point, 3.5f - Age * 6.f, Color, false, 0.f);
        }
    }
    // A tiny visible point makes the exact-stop development seam inspectable.
    if (ProjectileTimeScale < 1.f)
        for (const FBullet& Bullet : Bullets)
            DrawDebugPoint(GetWorld(), Bullet.Position, 5.f, FColor(255, 210, 120), false, 0.f);
    ApplyPreviewTime();
    SyncPreviewPresentation();
}
void ACombatProjectileWorld::Advance(float WorldDelta, double RealNow)
{
    // Retained low-level probe seam: one explicitly requested collision step.
    if (bAdvancing || bProcessingFrame) return;
    ++FrameSerial;
    FrameStart = FiringClock;
    FrameEnd = FrameStart + FMath::Max(0.f, WorldDelta);
    FrameStartCapsules = PreviousCapsules;
    FrameEndCapsules = SampleCapsules();
    FrameStartDummies = PreviousDummies;
    FrameEndDummies = SampleDummies();
    AdvanceSegment(FrameStart, FrameEnd, RealNow);
    FiringClock = FrameEnd;
    PlayerActionClock += FMath::Max(0.f, WorldDelta) * PlayerActionRate;
    RecordCapsules();
}
void ACombatProjectileWorld::AdvanceFrame(double WorldDelta, double RealNow, UCombatRifleComponent* Rifle)
{
    if (bProcessingFrame || bAdvancing || !FMath::IsFinite(WorldDelta) || WorldDelta < 0.0) return;
    TGuardValue<bool> FrameGuard(bProcessingFrame, true);
    ++FrameSerial;
    FrameStart = FiringClock;
    FrameEnd = FrameStart + WorldDelta;
    const double ActionStart = PlayerActionClock;
    const double ActionEnd = ActionStart + WorldDelta * PlayerActionRate;
    LastFrameDelta = WorldDelta;
    LastFrameSteps = LastFrameBirths = 0;
    FrameStartCapsules = PreviousCapsules;
    FrameEndCapsules = SampleCapsules();
    FrameStartDummies = PreviousDummies;
    FrameEndDummies = SampleDummies();
    FVector View = FVector::ZeroVector, StartView = FVector::ZeroVector;
    FQuat Rotation = FQuat::Identity, StartRotation = FQuat::Identity;
    if (Rifle)
    {
        Rifle->SampleView(View, Rotation);
        StartView = Rifle->bHaveViewSample ? Rifle->PreviousView : View;
        StartRotation = Rifle->bHaveViewSample ? Rifle->PreviousViewRotation : Rotation;
        Rifle->PrepareTimingFrame(ActionStart, ActionEnd);
    }
    const auto Blockers = SampleBlockers();
    bool bHistoryValid = BlockersMatch(Blockers);
    for (const auto& Entry : FrameEndCapsules)
        if (const auto* Old = FrameStartCapsules.Find(Entry.Key))
            bHistoryValid &= FVector::DistSquared(Old->Center, Entry.Value.Center) <= FMath::Square(250.0);
    const bool bOverload = WorldDelta > MaxFrameTime + 1.e-8;
    bool bCanceled = bOverload || !bHistoryValid;
    if (bCanceled)
    {
        // There is no trustworthy transform history for skipped time or moving
        // arbitrary geometry. Fail closed instead of tracing a past world using
        // today's blockers. No delayed ammunition debit or trigger debt survives.
        if (bOverload) ++OverloadFrames; else ++GeometryBarriers;
        DroppedTime += WorldDelta;
        ClearProjectiles();
        if (Rifle) Rifle->CancelFiringSession();
    }
    const uint64 Generation = ResetGeneration;
    double Cursor = FrameStart;
    auto DueOnManagerClock = [&]()
    {
        if (!Rifle || Rifle->GetDueTime() == TNumericLimits<double>::Max()) return TNumericLimits<double>::Max();
        return FrameStart + (Rifle->GetDueTime() - ActionStart) / PlayerActionRate;
    };
    while (!bCanceled && Cursor < FrameEnd - 1.e-8)
    {
        FiringClock = Cursor;
        PlayerActionClock = ActionStart + (Cursor - FrameStart) * PlayerActionRate;
        if (Rifle && DueOnManagerClock() <= Cursor + 1.e-8)
        {
            if (LastFrameBirths >= MaxFrameBirths) { bCanceled = true; break; }
            const double Birth = FMath::Max(FrameStart, DueOnManagerClock());
            const double Alpha = FMath::Clamp((Birth - FrameStart) / WorldDelta, 0.0, 1.0);
            Rifle->EmitScheduledShot(ActionStart + (Birth - FrameStart) * PlayerActionRate,
                FMath::Lerp(StartView, View, Alpha), FQuat::Slerp(StartRotation, Rotation, Alpha), Birth);
            ++LastFrameBirths;
        }
        const double GridEnd = FrameStart + (FMath::FloorToDouble((Cursor - FrameStart) / MaxStepTime + 1.e-7) + 1.0) * MaxStepTime;
        double Next = FMath::Min(FrameEnd, GridEnd);
        if (Rifle) Next = FMath::Min(Next, DueOnManagerClock());
        if (LastFrameSteps >= MaxFrameSteps || Next <= Cursor) { bCanceled = true; break; }
        AdvanceSegment(Cursor, Next, RealNow);
        ++LastFrameSteps;
        Cursor = Next;
        // Reset cancels births later in this interval as well as pending hits.
        bCanceled = Generation != ResetGeneration || IsActorBeingDestroyed();
    }
    if (bCanceled && Generation == ResetGeneration && Cursor < FrameEnd && !bOverload && bHistoryValid)
    {
        ++OverloadFrames;
        DroppedTime += FrameEnd - Cursor;
        ClearProjectiles();
        if (Rifle) Rifle->CancelFiringSession();
    }
    FiringClock = FrameEnd;
    PlayerActionClock = ActionEnd;
    PeakFrameSteps = FMath::Max(PeakFrameSteps, LastFrameSteps);
    if (Rifle)
    {
        if (bCanceled && Generation != ResetGeneration) Rifle->CancelFiringSession();
        Rifle->PreviousView = View;
        Rifle->PreviousViewRotation = Rotation;
        Rifle->bHaveViewSample = true;
        Rifle->FinishTimingFrame(bCanceled);
    }
    RecordCapsules();
    PreviousBlockers = SampleBlockers();
    bHaveBlockerSample = true;
}
void ACombatProjectileWorld::AdvanceSegment(double StartTime, double EndTime, double RealNow)
{
    if (bAdvancing) return;
    TGuardValue<bool> AdvancingGuard(bAdvancing, true);
    if (Bullets.IsEmpty()) return;
    struct FPendingHit { FBullet Bullet; FHitResult Hit; double Time; };
    TArray<FPendingHit> PendingHits;
    FCollisionQueryParams Query(SCENE_QUERY_STAT(CombatBullet), true);
    BuildQuery(Query);
    // Query the whole step before any damage or user callback can remove cover.
    // This conservative snapshot consumes all rounds blocked at step start,
    // even when an earlier hit destroys the shared obstruction.
    for (int32 Index = Bullets.Num() - 1; Index >= 0; --Index)
    {
        FBullet& Bullet = Bullets[Index];
        if (Bullet.EligibleFrame > FrameSerial) continue;
        if (RealNow - Bullet.Born >= FMath::Max(1.f, MaxRealAge))
        {
            Bullets.RemoveAtSwap(Index);
            ++RetiredCount;
            continue;
        }
        const float RemainingTime = FMath::Max(0.f, MaxSimulationAge - Bullet.Age);
        const float RemainingTravel = FMath::Max(0.f, MaxTravel - Bullet.Travel);
        const double Speed = Bullet.Velocity.Size();
        const double FlightStart = FMath::Max(StartTime, Bullet.BirthTime);
        if (FlightStart > EndTime + 1.e-8) continue;
        const double Duration = FMath::Max(0.0, EndTime - FlightStart);
        const float SimDelta = Duration * ProjectileTimeScale;
        const float Step = FMath::Min3(SimDelta, RemainingTime, float(RemainingTravel / Speed));
        const double FlightDuration = ProjectileTimeScale > 0.f ? FMath::Min(Duration, double(Step) / ProjectileTimeScale) : Duration;
        const auto StartCapsules = CapsulesAt(FlightStart);
        const auto EndCapsules = CapsulesAt(FlightStart + FlightDuration);
        const auto StartDummies = DummiesAt(FlightStart);
        const auto EndDummies = DummiesAt(FlightStart + FlightDuration);
        const FVector Start = Bullet.Position;
        const FVector End = Start + Bullet.Velocity * Step;
        FHitResult Hit;
        bool bHit = GetWorld()->SweepSingleByChannel(Hit, Start, End, FQuat::Identity, ECC_Visibility,
            FCollisionShape::MakeSphere(BulletRadius), Query);
        double Earliest = bHit ? Hit.Time : 2.0;
        for (const auto& Entry : EndCapsules)
        {
            ACharacter* Character = Entry.Key.Get();
            if (!IsValid(Character)) continue;
            auto* Capsule = Character->GetCapsuleComponent();
            if (!Capsule->IsQueryCollisionEnabled()) continue;
            const FCapsuleSample& Current = Entry.Value;
            const FVector Center = Current.Center;
            const FCapsuleSample* Old = Bullet.bFirstAdvance ? Bullet.BirthCapsules.Find(Character) : StartCapsules.Find(Character);
            if (!Old) Old = &Current;
            if (Character == Bullet.Shooter.Get() && !Bullet.bLaunchClear)
            {
                // Immunity lasts only while still inside the launch capsule. A
                // 200 cm flight without clearance retires this invalid launch.
                Bullet.bLaunchClear = CapsuleDistanceSquared(End - Center, Current.HalfHeight - Current.Radius) >
                    FMath::Square(Current.Radius + BulletRadius + 2.f);
                continue;
            }
            double ContactTime = 0.0;
            if (Character->IsA<AEnemyPrototypeCharacter>())
            {
                // Linear per-bone sphere history keeps moving limbs and stopped
                // bullets on the same birth/substep timeline as player capsules.
                for (int32 Region = 0; Region < Current.Regions.Num(); ++Region)
                {
                    const auto& New = Current.Regions[Region];
                    const FVector Before = Old->Regions.IsValidIndex(Region) ? Old->Regions[Region].Center : New.Center;
                    if (CapsuleContact(Start - Before, End - New.Center, New.Radius + BulletRadius,
                        New.Radius + BulletRadius, ContactTime) && ContactTime < Earliest)
                    {
                        Earliest = ContactTime;
                        const FVector Point = FMath::Lerp(Start, End, ContactTime);
                        Hit = FHitResult(Character, Character->GetMesh(), Point,
                            (Point - FMath::Lerp(Before, New.Center, ContactTime)).GetSafeNormal());
                        Hit.BoneName = New.Bone;
                        Hit.bBlockingHit = true;
                        Hit.Time = ContactTime;
                        Hit.ImpactPoint = Point;
                        bHit = true;
                    }
                }
                continue;
            }
            if (CapsuleContact(Start - Old->Center, End - Center,
                FMath::Max(Old->Radius, Current.Radius) + BulletRadius,
                FMath::Max(Old->HalfHeight, Current.HalfHeight) + BulletRadius, ContactTime) && ContactTime < Earliest)
            {
                Earliest = ContactTime;
                const FVector Point = FMath::Lerp(Start, End, ContactTime);
                Hit = FHitResult(Character, Capsule, Point, (Point - FMath::Lerp(Old->Center, Center, ContactTime)).GetSafeNormal());
                Hit.bBlockingHit = true;
                Hit.Time = ContactTime;
                Hit.ImpactPoint = Point;
                bHit = true;
            }
        }
        for (const auto& Entry : EndDummies)
            if (const auto* Dummy = Entry.Key.Get())
            {
                const bool bShooterBody = Dummy == Bullet.Shooter.Get() || Dummy == AGASPEnemyFixture::FromFoundation(Bullet.Shooter.Get());
                if (bShooterBody && !Bullet.bLaunchClear)
                {
                    FHitResult Clearance;
                    Bullet.bLaunchClear = !Dummy->TracePhysicalPose(Entry.Value, Entry.Value, End, End,
                        BulletRadius + 2.f, Clearance);
                    continue;
                }
                const auto* Old = Bullet.bFirstAdvance ? Bullet.BirthDummies.Find(Entry.Key) : StartDummies.Find(Entry.Key);
                FHitResult BodyHit;
                if (Dummy->TracePhysicalPose(Old ? *Old : Entry.Value, Entry.Value, Start, End, BulletRadius, BodyHit) && BodyHit.Time < Earliest)
                { Hit = BodyHit; Earliest = BodyHit.Time; bHit = true; }
            }
        if (bHit)
        {
            PendingHits.Add({Bullet, Hit, FlightStart + FlightDuration * Hit.Time});
            Bullets.RemoveAtSwap(Index);
            continue;
        }
        Bullet.bFirstAdvance = false;
        Bullet.BirthCapsules.Reset();
        Bullet.BirthDummies.Reset();
        Bullet.Position = End;
        Bullet.Age += Step;
        Bullet.Travel += Speed * Step;
        if (Bullet.Age >= MaxSimulationAge || Bullet.Travel >= MaxTravel || (!Bullet.bLaunchClear && Bullet.Travel >= 200.f))
        {
            Bullets.RemoveAtSwap(Index);
            ++RetiredCount;
        }
    }
    PendingHits.Sort([](const FPendingHit& A, const FPendingHit& B)
    {
        return A.Time == B.Time ? A.Bullet.Id < B.Bullet.Id : A.Time < B.Time;
    });
    const uint64 Generation = ResetGeneration;
    for (int32 Index = 0; Index < PendingHits.Num(); ++Index)
    {
        if (Generation != ResetGeneration || IsActorBeingDestroyed())
        {
            RetiredCount += PendingHits.Num() - Index;
            break;
        }
        LastContactTime = PendingHits[Index].Time;
        FiringClock = PendingHits[Index].Time;
        ResolveHit(PendingHits[Index].Bullet, PendingHits[Index].Hit, RealNow);
    }
}
void ACombatProjectileWorld::ResolveHit(const FBullet& Bullet, const FHitResult& Hit, double Now)
{
    AActor* Victim = Hit.GetActor();
    const bool bSelf = Victim && Victim == Bullet.Shooter.Get();
    ++HitCount;
    if (bSelf) ++SelfHitCount;
    LastHitShotId = Bullet.Id;
    LastHitShooterIdentity = Bullet.ShooterIdentity;
    LastHitRealTime = Now;
    const uint64 Generation = ResetGeneration;
    auto* PhysicalTarget = Cast<APhysicsControlDummy>(Victim);
    const float Applied = IsValid(PhysicalTarget) ? PhysicalTarget->ReceiveBullet(Bullet.Id, Bullet.Damage,
        Bullet.Velocity.GetSafeNormal(), Hit, LastContactTime, Bullet.BirthTime, FrameSerial,
        Bullet.FallImpulseMultiplier, Bullet.DeathImpulseMultiplier) :
        IsValid(Victim) ? UGameplayStatics::ApplyPointDamage(Victim, Bullet.Damage, Bullet.Velocity.GetSafeNormal(),
            Hit, Bullet.Instigator.Get(), Bullet.Shooter.Get(), nullptr) : 0.f;
    if (Generation != ResetGeneration || IsActorBeingDestroyed()) return;
    Victim = Hit.GetActor();
    const auto* Target = Cast<ACombatTarget>(Victim);
    const auto* EnemyTarget = Cast<AEnemyPrototypeCharacter>(Victim);
    LastHitText = bSelf ? TEXT("SELF HIT") : Target ?
        FString::Printf(TEXT("HIT %.0f  |  TARGET %.0f / %.0f"), Applied, Target->Health, Target->MaxHealth) : EnemyTarget ?
        FString::Printf(TEXT("HIT %.0f  |  %s  |  ENEMY %.0f"), Applied, *EnemyTarget->LastRegion.ToString(), EnemyTarget->Health) : TEXT("SURFACE IMPACT");
    if (IsValid(PhysicalTarget)) LastHitText = FString::Printf(TEXT("PHYSICS %s  |  %s  |  %.0f HP"),
        PhysicalTarget->IsDead() ? TEXT("CORPSE") : TEXT("HIT"), *Hit.BoneName.ToString(), PhysicalTarget->Health);
    if (const auto* Player = Cast<AOpeningLobbyCharacter>(Victim))
        LastHitText = FString::Printf(TEXT("PLAYER HIT %.0f  |  RECEIVED %d  |  TOTAL %.0f"),
            Applied, Player->ReceivedCombatHits, Player->ReceivedCombatDamage);
    bool bMetal = Victim && Victim->ActorHasTag(TEXT("CombatMetal"));
    LastHitMaterial.Empty();
    if (const auto* Part = Hit.GetComponent())
        for (int32 Slot = 0; Slot < Part->GetNumMaterials(); ++Slot)
            if (const auto* Material = Part->GetMaterial(Slot))
            {
                const FString Name = Material->GetPathName();
                if (Slot == 0) LastHitMaterial = Name;
                bMetal |= Name.Contains(TEXT("metal"), ESearchCase::IgnoreCase) || Name.Contains(TEXT("steel"), ESearchCase::IgnoreCase);
            }
    if (Impacts.Num() >= 48) Impacts.RemoveAt(0);
    Impacts.Add({Hit.ImpactPoint, Hit.ImpactNormal.GetSafeNormal(UE_DOUBLE_SMALL_NUMBER, FVector::UpVector), Now, bMetal});
    LastHitSurface = bMetal ? TEXT("metal") : TEXT("stone_or_other");
    OnBulletHit.Broadcast(Bullet.Id, Bullet.ShooterIdentity, Bullet.Shooter.Get(), Victim, Bullet.Damage, Hit.ImpactPoint, bSelf);
}
void ACombatProjectileWorld::ClearProjectiles()
{
    ++ResetGeneration;
    RetiredCount += Bullets.Num();
    Bullets.Reset();
    Impacts.Reset();
    RecordCapsules();
    bHaveBlockerSample = false;
}
void ACombatProjectileWorld::ResetTargets()
{
    ClearProjectiles();
    for (ACombatTarget* Target : Targets) if (IsValid(Target)) Target->ResetTarget();
    for (APhysicsControlDummy* Dummy : PhysicsDummies) if (IsValid(Dummy))
    {
        if (auto* Fixture = Cast<AGASPEnemyFixture>(Dummy)) Fixture->Combat->bEnabled = bEnemyCombatMode;
        Dummy->ResetDummy();
    }
    SetPhysicsPreviewScale(1);
    PreviousDummies.Reset(); FrameStartDummies.Reset(); FrameEndDummies.Reset();
    RecordCapsules();
    for (TActorIterator<ACharacter> It(GetWorld()); It; ++It)
    {
        if (auto* Rifle = It->FindComponentByClass<UCombatRifleComponent>()) Rifle->ClearTransientFeedback();
        if (auto* Player = Cast<AOpeningLobbyCharacter>(*It)) Player->ResetCombatReceiver();
    }
    LastHitText = TEXT("TARGETS RESET  |  AMMO UNCHANGED");
    LastHitRealTime = FPlatformTime::Seconds();
}
void ACombatProjectileWorld::EndPlay(const EEndPlayReason::Type Reason)
{
    RestorePreviewTime();
    ClearProjectiles();
    PreviousCapsules.Reset();
    PreviousDummies.Reset(); FrameStartDummies.Reset(); FrameEndDummies.Reset();
    OnBulletHit.Clear();
    Super::EndPlay(Reason);
}
FString ACombatProjectileWorld::GetCombatState() const
{
    auto Root = MakeShared<FJsonObject>();
    Root->SetNumberField(TEXT("scale"), ProjectileTimeScale);
    Root->SetNumberField(TEXT("physics_preview_scale"), ActivePreviewScale);
    Root->SetBoolField(TEXT("physics_dummy_enabled"), !PhysicsDummies.IsEmpty());
    Root->SetNumberField(TEXT("physics_dummy_count"), PhysicsDummies.Num());
    Root->SetBoolField(TEXT("enemy_combat_mode"), bEnemyCombatMode);
    Root->SetBoolField(TEXT("immortal_dummies"), bImmortalDummies);
    Root->SetBoolField(TEXT("recovery_assistance"), bRecoveryAssistance);
    Root->SetNumberField(TEXT("player_action_clock"), PlayerActionClock);
    Root->SetNumberField(TEXT("player_action_rate"), PlayerActionRate);
    Root->SetNumberField(TEXT("physical_history_actors"), PreviousDummies.Num());
    Root->SetNumberField(TEXT("firing_clock"), FiringClock);
    Root->SetNumberField(TEXT("frame_delta"), LastFrameDelta);
    Root->SetNumberField(TEXT("frame_steps"), LastFrameSteps);
    Root->SetNumberField(TEXT("frame_birth_attempts"), LastFrameBirths);
    Root->SetNumberField(TEXT("peak_steps"), PeakFrameSteps);
    Root->SetNumberField(TEXT("overload_frames"), OverloadFrames);
    Root->SetNumberField(TEXT("geometry_barriers"), GeometryBarriers);
    Root->SetNumberField(TEXT("dropped_time"), DroppedTime);
    Root->SetNumberField(TEXT("last_contact_time"), LastContactTime);
    Root->SetNumberField(TEXT("active"), Bullets.Num());
    Root->SetNumberField(TEXT("launched"), LaunchedCount);
    Root->SetNumberField(TEXT("hits"), HitCount);
    Root->SetNumberField(TEXT("self_hits"), SelfHitCount);
    Root->SetNumberField(TEXT("retired"), RetiredCount);
    Root->SetNumberField(TEXT("rejected"), RejectedCount);
    Root->SetNumberField(TEXT("impacts"), Impacts.Num());
    Root->SetNumberField(TEXT("last_hit_shot"), LastHitShotId);
    Root->SetStringField(TEXT("last_hit"), LastHitText);
    Root->SetStringField(TEXT("last_hit_shooter"), LastHitShooterIdentity.ToString());
    Root->SetStringField(TEXT("last_surface"), LastHitSurface);
    Root->SetStringField(TEXT("last_material"), LastHitMaterial);
    TArray<TSharedPtr<FJsonValue>> Values;
    for (const FBullet& B : Bullets)
    {
        auto Row = MakeShared<FJsonObject>();
        Row->SetNumberField(TEXT("id"), B.Id);
        Row->SetNumberField(TEXT("birth_time"), B.BirthTime);
        Row->SetStringField(TEXT("shooter"), B.ShooterIdentity.ToString());
        Row->SetField(TEXT("position"), JsonVector(B.Position));
        Row->SetField(TEXT("velocity"), JsonVector(B.Velocity));
        Row->SetNumberField(TEXT("age"), B.Age);
        Row->SetNumberField(TEXT("travel"), B.Travel);
        Row->SetBoolField(TEXT("launch_clear"), B.bLaunchClear);
        Values.Add(MakeShared<FJsonValueObject>(Row));
    }
    Root->SetArrayField(TEXT("bullets"), Values);
    Values.Reset();
    for (const ACombatTarget* Target : Targets)
        if (IsValid(Target))
        {
            auto Row = MakeShared<FJsonObject>();
            Row->SetStringField(TEXT("name"), Target->GetName());
            Row->SetNumberField(TEXT("health"), Target->Health);
            Row->SetNumberField(TEXT("hits"), Target->Hits);
            Values.Add(MakeShared<FJsonValueObject>(Row));
        }
    Root->SetArrayField(TEXT("targets"), Values);
    FString Result;
    FJsonSerializer::Serialize(Root, TJsonWriterFactory<>::Create(&Result));
    return Result;
}

FString ACombatProjectileWorld::ProbeBallistics()
{
    auto Report = MakeShared<FJsonObject>();
#if WITH_EDITOR
    if (GetWorld()->WorldType != EWorldType::PIE || !Bullets.IsEmpty()) return TEXT("{\"error\":\"Probe requires quiet PIE\"}");
    const float OriginalScale = ProjectileTimeScale;
    const int32 OriginalCapacity = MaxProjectiles;
    const FVector Origin(0, 0, 12000);
    auto Check = [&](const TCHAR* Name, bool Passed) { Report->SetBoolField(Name, Passed); };
    auto Step = [&](float Delta) { Advance(Delta, FPlatformTime::Seconds()); };
    FActorSpawnParameters Params;
    Params.ObjectFlags |= RF_Transient;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    auto* Target = GetWorld()->SpawnActor<ACombatTarget>(Origin + FVector(1000, 0, 0), FRotator::ZeroRotator, Params);
    SetProjectileTimeScale(1.f);
    const int32 BeforeFinite = HitCount;
    Launch(nullptr, Origin, FVector(1000, 0, 0), 25.f);
    Step(.4f);
    Check(TEXT("finite_before_contact"), Bullets.Num() == 1 && HitCount == BeforeFinite && Target->Health == 100.f);
    Step(.7f);
    Check(TEXT("collision_damage_once"), Bullets.IsEmpty() && HitCount == BeforeFinite + 1 && Target->Health == 75.f && Target->Hits == 1);
    Step(.7f);
    Check(TEXT("no_repeat_damage"), Target->Health == 75.f && Target->Hits == 1);

    auto* Wall = GetWorld()->SpawnActor<AStaticMeshActor>(Origin + FVector(500, 0, 0), FRotator::ZeroRotator, Params);
    Wall->SetMobility(EComponentMobility::Movable);
    Wall->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
    Wall->SetActorScale3D(FVector(.002, 2, 2));
    Wall->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
    Target->ResetTarget();
    const int32 BeforeWall = HitCount;
    Launch(nullptr, Origin, FVector(200000, 0, 0), 25.f);
    Step(.02f);
    Check(TEXT("two_mm_wall_at_2000_mps"), HitCount == BeforeWall + 1 && Bullets.IsEmpty() && Target->Hits == 0);
    Wall->Destroy();
    for (int32 I = 0; I < 4; ++I)
    {
        Launch(nullptr, Origin, FVector(20000, 0, 0), 25.f);
        Step(.08f);
    }
    Check(TEXT("target_death"), Target->Health == 0.f && Target->Hits == 4 && !Target->TargetMesh->IsVisible() &&
        Target->TargetMesh->GetCollisionEnabled() == ECollisionEnabled::NoCollision);
    Target->ResetTarget();
    Check(TEXT("target_reset"), Target->Health == 100.f && Target->Hits == 0 && Target->TargetMesh->IsVisible());
    Target->Destroy();

    Launch(nullptr, Origin, FVector(1000, 0, 0), 25.f);
    Step(.4f);
    Check(TEXT("normal_clock"), Bullets.Num() == 1 && Bullets[0].Position.Equals(Origin + FVector(400, 0, 0), .01) &&
        FMath::IsNearlyEqual(Bullets[0].Age, .4f));
    ClearProjectiles();
    SetProjectileTimeScale(.25f);
    Launch(nullptr, Origin, FVector(1000, 0, 0), 25.f);
    Step(.4f);
    Check(TEXT("quarter_clock"), Bullets.Num() == 1 && Bullets[0].Position.Equals(Origin + FVector(100, 0, 0), .01) &&
        FMath::IsNearlyEqual(Bullets[0].Age, .1f));
    const FBullet Frozen = Bullets[0];
    SetProjectileTimeScale(0.f);
    Step(2.f);
    Check(TEXT("exact_stop_position_velocity_age"), Bullets.Num() == 1 && Bullets[0].Position == Frozen.Position &&
        Bullets[0].Velocity == Frozen.Velocity && Bullets[0].Age == Frozen.Age && Bullets[0].Travel == Frozen.Travel);
    SetProjectileTimeScale(1.f);
    Step(.4f);
    Check(TEXT("clean_resumption"), Bullets.Num() == 1 && Bullets[0].Position.Equals(Origin + FVector(500, 0, 0), .01) &&
        FMath::IsNearlyEqual(Bullets[0].Age, .5f));
    ClearProjectiles();

    const int32 BeforeMiss = HitCount;
    Launch(nullptr, Origin, FVector(1000, 0, 0), 25.f);
    Step(4.f);
    Check(TEXT("miss_simulation_lifetime"), Bullets.IsEmpty() && HitCount == BeforeMiss);
    SetProjectileTimeScale(0.f);
    Launch(nullptr, Origin, FVector(1000, 0, 0), 25.f);
    const double Expiry = Bullets[0].Born + MaxRealAge + .01;
    Advance(1.f, Expiry);
    Check(TEXT("stop_real_safety_retirement"), Bullets.IsEmpty() && HitCount == BeforeMiss);
    MaxProjectiles = 2;
    const int64 A = Launch(nullptr, Origin, FVector(1000, 0, 0), 25.f);
    const int64 B = Launch(nullptr, Origin, FVector(1000, 0, 0), 25.f);
    const int64 C = Launch(nullptr, Origin, FVector(1000, 0, 0), 25.f);
    Check(TEXT("capacity_rejects_without_phantom"), A != 0 && B != 0 && C == 0 && Bullets.Num() == 2);
    ClearProjectiles();
    MaxProjectiles = OriginalCapacity;

    ACharacter* Player = UGameplayStatics::GetPlayerCharacter(GetWorld(), 0);
    if (Player)
    {
        const FVector Center = Player->GetCapsuleComponent()->GetComponentLocation();
        const int32 SelfBefore = SelfHitCount;
        SetProjectileTimeScale(1.f);
        Launch(Player, Center, FVector(1000, 0, 0), 25.f);
        Step(.01f);
        Check(TEXT("no_initial_spawn_self_hit"), Bullets.Num() == 1 && !Bullets[0].bLaunchClear && SelfHitCount == SelfBefore);
        Step(.1f);
        Check(TEXT("bounded_geometric_clearance"), Bullets.Num() == 1 && Bullets[0].bLaunchClear && SelfHitCount == SelfBefore);
        ClearProjectiles();
        const int64 OwnId = Launch(Player, Center + FVector(100, 0, 0), FVector(-1000, 0, 0), 25.f);
        Step(.2f);
        Check(TEXT("own_shot_point_damage_contract"), Bullets.IsEmpty() && SelfHitCount == SelfBefore + 1 && LastHitShotId == OwnId);
        Check(TEXT("retained_shooter_identity"), LastHitShooterIdentity == FName(*Player->GetPathName()));
        Step(.2f);
        Check(TEXT("self_event_at_most_once"), SelfHitCount == SelfBefore + 1);
    }
    double Contact = 0.0;
    Check(TEXT("continuous_moving_capsule_crossing"), CapsuleContact(FVector(-100,0,0), FVector(100,0,0), 34.5, 88.5, Contact)
        && FMath::IsNearlyEqual(Contact, .3275, 1.e-6));
    Check(TEXT("capsule_miss"), !CapsuleContact(FVector(-100,40,0), FVector(100,40,0), 34.5, 88.5, Contact));
    ClearProjectiles();
    SetProjectileTimeScale(OriginalScale);
    Report->SetNumberField(TEXT("temporary_actors_remaining"), (IsValid(Target) && !Target->IsActorBeingDestroyed() ? 1 : 0) +
        (IsValid(Wall) && !Wall->IsActorBeingDestroyed() ? 1 : 0));
#else
    Report->SetStringField(TEXT("error"), TEXT("PIE-only development probe"));
#endif
    FString Result;
    FJsonSerializer::Serialize(Report, TJsonWriterFactory<>::Create(&Result));
    return Result;
}

void ACombatProjectileWorld::ProbeHitReset(int64 ShotId, FName ShooterIdentity, AActor* Shooter,
    AActor* Victim, float Damage, FVector Position, bool bSelfHit)
{
#if WITH_EDITOR
    if (!bProbeResetPending || GetWorld()->WorldType != EWorldType::PIE) return;
    bProbeResetPending = false;
    ++ProbeResetCallbacks;
    ResetTargets();
    Launch(nullptr, ProbeSpawnPosition, FVector(1000, 0, 0), 25.f);
    Launch(nullptr, ProbeSpawnPosition, FVector(1000, 0, 0), 25.f);
#endif
}

FString ACombatProjectileWorld::ProbeCorrections()
{
    auto Report = MakeShared<FJsonObject>();
#if WITH_EDITOR
    if (GetWorld()->WorldType != EWorldType::PIE || bAdvancing || !Bullets.IsEmpty())
        return TEXT("{\"error\":\"Probe requires quiet PIE\"}");
    const float OriginalScale = ProjectileTimeScale;
    const FVector Origin(0, 4000, 12000);
    auto Check = [&](const TCHAR* Name, bool Passed) { Report->SetBoolField(Name, Passed); };
    auto Step = [&](float Delta) { Advance(Delta, FPlatformTime::Seconds()); };
    FActorSpawnParameters Params;
    Params.ObjectFlags |= RF_Transient;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

    auto* Character = GetWorld()->SpawnActor<ACharacter>(Origin, FRotator::ZeroRotator, Params);
    Character->GetCapsuleComponent()->SetCapsuleSize(34.f, 88.f);
    RecordCapsules();
    Character->SetActorLocation(Origin + FVector(-10, 0, 0), false, nullptr, ETeleportType::TeleportPhysics);
    SetProjectileTimeScale(0.f);
    const int32 BeforeBirth = SelfHitCount;
    const int64 NewShot = Launch(Character, Origin + FVector(28, 0, 0), FVector(1000, 0, 0), 25.f);
    Step(.016f);
    Check(TEXT("backward_launch_has_no_prebirth_self_hit"), Bullets.Num() == 1 &&
        Bullets[0].Id == NewShot && Bullets[0].bLaunchClear && SelfHitCount == BeforeBirth);
    Character->SetActorLocation(Origin + FVector(100, 0, 0), false, nullptr, ETeleportType::TeleportPhysics);
    Step(.016f);
    Check(TEXT("later_genuine_reentry_hits_once"), Bullets.IsEmpty() && SelfHitCount == BeforeBirth + 1 && LastHitShotId == NewShot);
    Step(.016f);
    Check(TEXT("reentry_does_not_repeat"), SelfHitCount == BeforeBirth + 1);
    ClearProjectiles();

    Character->SetActorLocation(Origin, false, nullptr, ETeleportType::TeleportPhysics);
    RecordCapsules();
    const int64 OldShot = Launch(Character, Origin + FVector(50, 0, 0), FVector(1000, 0, 0), 25.f);
    Step(0.f);
    Character->SetActorLocation(Origin + FVector(100, 0, 0), false, nullptr, ETeleportType::TeleportPhysics);
    const int64 LaterShot = Launch(Character, Origin + FVector(140, 0, 0), FVector(1000, 0, 0), 25.f);
    Step(.016f);
    Check(TEXT("new_launch_preserves_old_suspended_contact_history"), Bullets.Num() == 1 &&
        Bullets[0].Id == LaterShot && LastHitShotId == OldShot && SelfHitCount == BeforeBirth + 2);
    Character->SetActorLocation(Origin + FVector(200, 0, 0), false, nullptr, ETeleportType::TeleportPhysics);
    Step(.016f);
    Check(TEXT("second_generation_round_has_normal_later_contact"), Bullets.IsEmpty() &&
        LastHitShotId == LaterShot && SelfHitCount == BeforeBirth + 3);
    Character->Destroy();
    ClearProjectiles();

    SetProjectileTimeScale(1.f);
    auto* Front = GetWorld()->SpawnActor<ACombatTarget>(Origin + FVector(100, 0, 0), FRotator::ZeroRotator, Params);
    auto* Rear = GetWorld()->SpawnActor<ACombatTarget>(Origin + FVector(150, 0, 0), FRotator::ZeroRotator, Params);
    Front->MaxHealth = 25.f;
    for (int32 Order = 0; Order < 2; ++Order)
    {
        Front->ResetTarget();
        Rear->ResetTarget();
        const int32 BeforeHits = HitCount;
        Launch(nullptr, Origin + FVector(Order == 0 ? 90 : 0, 0, 0), FVector(1000, 0, 0), 25.f);
        Launch(nullptr, Origin + FVector(Order == 0 ? 0 : 90, 0, 0), FVector(1000, 0, 0), 25.f);
        Step(.1f);
        Check(Order == 0 ? TEXT("snapshot_blocks_rear_original_order") : TEXT("snapshot_blocks_rear_reversed_order"),
            Bullets.IsEmpty() && Front->Health == 0.f && Front->Hits == 1 && Rear->Health == 100.f &&
            Rear->Hits == 0 && HitCount == BeforeHits + 2);
    }

    Front->MaxHealth = 100.f;
    Front->ResetTarget();
    const int32 BeforeCallbackHits = HitCount;
    const int32 BeforeCallbackRetired = RetiredCount;
    const int32 BeforeCallbackLaunches = LaunchedCount;
    ProbeSpawnPosition = Origin;
    ProbeResetCallbacks = 0;
    bProbeResetPending = true;
    OnBulletHit.AddDynamic(this, &ACombatProjectileWorld::ProbeHitReset);
    Launch(nullptr, Origin, FVector(1000, 0, 0), 25.f);
    Launch(nullptr, Origin, FVector(1000, 0, 0), 25.f);
    Launch(nullptr, Origin + FVector(0, 300, 0), FVector(1000, 0, 0), 25.f);
    Step(.2f);
    OnBulletHit.RemoveDynamic(this, &ACombatProjectileWorld::ProbeHitReset);
    bProbeResetPending = false;
    Check(TEXT("hit_listener_reset_runs_once"), ProbeResetCallbacks == 1 && HitCount == BeforeCallbackHits + 1);
    Check(TEXT("reset_cancels_remaining_pending_hit_and_live_round"), RetiredCount == BeforeCallbackRetired + 2 && Front->Hits == 1);
    Check(TEXT("callback_launches_wait_for_next_step"), Bullets.Num() == 2 &&
        Bullets[0].Position == Origin && Bullets[1].Position == Origin &&
        Bullets[0].Age == 0.f && Bullets[1].Age == 0.f && Bullets[0].Travel == 0.f && Bullets[1].Travel == 0.f);
    Step(.2f);
    Check(TEXT("callback_rounds_process_normally_next_step"), Bullets.IsEmpty() &&
        HitCount == BeforeCallbackHits + 3 && Front->Hits == 3 && Front->Health == 25.f);
    Check(TEXT("callback_round_accounting_conserved"), LaunchedCount - BeforeCallbackLaunches ==
        HitCount - BeforeCallbackHits + RetiredCount - BeforeCallbackRetired + Bullets.Num());
    Report->SetNumberField(TEXT("callback_launches"), LaunchedCount - BeforeCallbackLaunches);
    Report->SetNumberField(TEXT("callback_hits"), HitCount - BeforeCallbackHits);
    Report->SetNumberField(TEXT("callback_retirements"), RetiredCount - BeforeCallbackRetired);
    Front->Destroy();
    Rear->Destroy();
    ClearProjectiles();
    SetProjectileTimeScale(OriginalScale);
    Check(TEXT("probe_cleanup"), Bullets.IsEmpty() && Impacts.IsEmpty() &&
        Character->IsActorBeingDestroyed() && Front->IsActorBeingDestroyed() && Rear->IsActorBeingDestroyed());
#else
    Report->SetStringField(TEXT("error"), TEXT("PIE-only development probe"));
#endif
    FString Result;
    FJsonSerializer::Serialize(Report, TJsonWriterFactory<>::Create(&Result));
    return Result;
}

bool ACombatProjectileWorld::ProbeCover(FName Kind)
{
#if WITH_EDITOR
    if (GetWorld()->WorldType != EWorldType::PIE) return false;
    if (Kind != TEXT("near") && Kind != TEXT("offset") && Kind != TEXT("thin") && Kind != TEXT("clear") &&
        Kind != TEXT("metal") && Kind != TEXT("stone")) return false;
    for (TActorIterator<AStaticMeshActor> It(GetWorld()); It; ++It)
        if (It->ActorHasTag(TEXT("CombatProbeCover"))) It->Destroy();
    if (Kind == TEXT("clear")) return true;
    const auto* PC = UGameplayStatics::GetPlayerController(GetWorld(), 0);
    if (!PC) return false;
    FVector View;
    FRotator Rotation;
    PC->GetPlayerViewPoint(View, Rotation);
    const bool Offset = Kind == TEXT("offset");
    const bool MaterialFixture = Kind == TEXT("metal") || Kind == TEXT("stone");
    const FVector Position = View + Rotation.RotateVector(Offset ? FVector(35, 8, -5) :
        Kind == TEXT("thin") ? FVector(300, 0, 0) : MaterialFixture ? FVector(100, 0, 0) : FVector(25, 0, 0));
    FActorSpawnParameters Params;
    Params.ObjectFlags |= RF_Transient;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    auto* Wall = GetWorld()->SpawnActor<AStaticMeshActor>(Position, Rotation, Params);
    Wall->Tags.Add(TEXT("CombatProbeCover"));
    if (!MaterialFixture) Wall->Tags.Add(TEXT("CombatMetal"));
    Wall->SetMobility(EComponentMobility::Movable);
    Wall->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
    Wall->SetActorScale3D(Offset ? FVector(.01, .08, .5) : FVector(.002, 2, 2));
    Wall->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
    if (MaterialFixture)
        Wall->GetStaticMeshComponent()->SetMaterial(0, LoadObject<UMaterialInterface>(nullptr, Kind == TEXT("metal") ?
            TEXT("/Game/OpeningLobby/PainterMetal01/Materials/M_PainterMetal01.M_PainterMetal01") :
            TEXT("/Game/OpeningLobby/PainterStone01/Materials/M_PainterStone01.M_PainterStone01")));
    return true;
#else
    return false;
#endif
}
