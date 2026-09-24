#include "CombatProjectileWorld.h"
#include "EnemyCombatComponent.h"
#include "GASPEnemyFixture.h"
#include "OpeningLobbyCharacter.h"
#include "Components/CapsuleComponent.h"
#include "DefaultMovementSet/CharacterMoverComponent.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "Sound/SoundAttenuation.h"

namespace
{
CombatAI::Position Point(FVector P) { return {P.X,P.Y,P.Z}; }
FVector Vector(CombatAI::Position P) { return {P.X,P.Y,P.Z}; }
}

void ACombatProjectileWorld::QueueSound(AActor* Attribution, CombatAI::SourceTeam Category,
    CombatAI::Sense Kind, FVector Position, double Range, uint64 Shot, double SimulationTime,
    AActor* DirectVictim, FVector Incoming)
{
    if (Position.ContainsNaN() || Incoming.ContainsNaN() || !FMath::IsFinite(Range) || Range <= 0) return;
    // A resolved bullet has one impact and at most one direct victim. Coalesce
    // duplicate producer callbacks before bounded fan-out, without reordering hits.
    for (const auto& Q : Stimuli)
        if (Shot && Q.Record.Get().Shot == Shot && Q.Record.Get().Kind == Kind &&
            Q.Record.Get().ProjectileGeneration == ResetGeneration) return;
    if (Stimuli.Num() >= 64) { ++DroppedStimuli; return; }
    CombatAI::StimulusData S;
    S.Id = NextStimulusId++; S.Generation = EncounterGeneration; S.ProjectileGeneration = ResetGeneration;
    S.Shot = Shot; S.Kind = Kind; S.Category = Category;
    S.Region = Point(Position); S.Bearing = Point(-Incoming.GetSafeNormal());
    S.OccurredWorld = GetWorld()->GetTimeSeconds(); S.SimulationTime = SimulationTime;
    S.Strength = Range;
    Stimuli.Add({CombatAI::Stimulus(S), Attribution, DirectVictim, Range});
    if (Category==CombatAI::SourceTeam::Enemy && Kind==CombatAI::Sense::Step) ++EnemyStepStimuli;
}

void ACombatProjectileWorld::SampleMovementSounds()
{
    const double Now = GetWorld()->GetTimeSeconds();
    auto Emit = [&](AActor* Actor, FVector Feet, const CombatAI::MotionEmission& Emission, CombatAI::SourceTeam Team)
    {
        if (Emission.Kind == CombatAI::MotionEvent::None) return;
        // GASP already owns its landing foley; only player landing uses this fallback.
        if (Team == CombatAI::SourceTeam::Enemy && Emission.Kind == CombatAI::MotionEvent::Landing) return;
        QueueSound(Actor, Team, Emission.Kind == CombatAI::MotionEvent::Landing ? CombatAI::Sense::Landing : CombatAI::Sense::Step,
            Feet, Emission.Range);
        // Source CMC animation notifies own its audible foley. Hearing remains
        // driven by paid displacement, independent of audio and virtualization.
        if (const auto* Enemy = Cast<AGASPEnemyFixture>(Actor))
            if (Enemy->Foundation && Enemy->Foundation->FindComponentByClass<UCharacterMovementComponent>()) return;
        if (!StepSound) StepSound = LoadObject<USoundBase>(nullptr,
            TEXT("/Game/InfimaGames/TacticalFPSAnimations/Common/Audio/Foley/A_TFA_Foley_Footsteps_Cue.A_TFA_Foley_Footsteps_Cue"));
        // Audio is a second consumer. Muting/virtualization cannot cancel hearing.
        if (StepSound)
        {
            const int32 Index = Emission.Range <= 180 ? 0 : Emission.Range <= 750 ? 1 : Emission.Range <= 900 ? 2 : Emission.Range <= 1500 ? 3 : 4;
            StepAttenuation.SetNum(5);
            if (!StepAttenuation[Index])
            {
                StepAttenuation[Index] = NewObject<USoundAttenuation>(this);
                auto& Settings = StepAttenuation[Index]->Attenuation;
                Settings.bAttenuate = true; Settings.bSpatialize = true;
                Settings.AttenuationShapeExtents = FVector(60,0,0);
                Settings.FalloffDistance = static_cast<float>(Emission.Range);
            }
            UGameplayStatics::PlaySoundAtLocation(this, StepSound, Feet, FRotator::ZeroRotator,
                static_cast<float>(Emission.Volume), FMath::Clamp(UGameplayStatics::GetGlobalTimeDilation(this), .25f, 1.f),
                0, StepAttenuation[Index], nullptr, Actor);
        }
    };
    auto* Player = Cast<AOpeningLobbyCharacter>(UGameplayStatics::GetPlayerCharacter(this, 0));
    if (Player != TravelPlayer.Get()) { PlayerTravel.Reset(); TravelPlayer = Player; }
    if (Player)
    {
        const FVector Feet = Player->GetActorLocation() - FVector(0,0,Player->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
        const auto* Move = Player->GetCharacterMovement();
        // Speed is used only to classify a paid displacement stride. Character
        // custom dilation affects travel, not world-clock cognition or deadlines.
        const auto Emission = PlayerTravel.Advance({Point(Feet), Now, EncounterGeneration,
            Move->IsMovingOnGround(), Player->bIsCrouched != 0, Move->Velocity.Size2D() > 430, true});
        Emit(Player, Feet, Emission, CombatAI::SourceTeam::Player);
    }
    int32 Count = 0;
    for (APhysicsControlDummy* Dummy : PhysicsDummies)
    {
        auto* E = Cast<AGASPEnemyFixture>(Dummy);
        if (!E || !IsValid(E->Foundation) || ++Count > 8) continue;
        auto* Capsule = E->Foundation->FindComponentByClass<UCapsuleComponent>();
        auto* Mover = E->Foundation->FindComponentByClass<UCharacterMoverComponent>();
        auto* CMC = E->Foundation->FindComponentByClass<UCharacterMovementComponent>();
        if (!Capsule || (!Mover && !CMC)) continue;
        FVector Feet = E->Foundation->GetActorLocation() - FVector(0,0,Capsule->GetScaledCapsuleHalfHeight());
        auto& Travel = EnemyTravel.FindOrAdd(E);
        const auto Emission = Travel.Advance({Point(Feet), Now, EncounterGeneration,
            CMC ? CMC->IsMovingOnGround() : Mover->IsOnGround(), E->IsMovementCrouched(), !E->bWalkCommand,
            E->IsReady() && !E->IsDead() && E->Authority == EGASPEnemyAuthority::Locomotion});
        Emit(E, Feet, Emission, CombatAI::SourceTeam::Enemy);
    }
    for (auto It = EnemyTravel.CreateIterator(); It; ++It) if (!It.Key().IsValid()) It.RemoveCurrent();
}

void ACombatProjectileWorld::DeliverStimuli()
{
    check(!bAdvancing && !bProcessingFrame);
    // Drain a snapshot only after the full sorted collision frame. Consumers never
    // touch projectile storage or inherit a partial contact iteration.
    const auto Batch = MoveTemp(Stimuli); Stimuli.Reset();
    const double Now = GetWorld()->GetTimeSeconds();
    const uint64 ProjectileGeneration = ResetGeneration;
    int32 Listeners = 0;
    for (APhysicsControlDummy* Dummy : PhysicsDummies)
    {
        auto* E = Cast<AGASPEnemyFixture>(Dummy);
        if (!E || !E->Combat || !E->Combat->bEnabled || E->IsDead() || !IsValid(E->Foundation)) continue;
        if (++Listeners > 8) break;
        const FVector Ear = E->Foundation->GetActorLocation() + FVector(0,0,55);
        for (const auto& Q : Batch)
        {
            if (ResetGeneration != ProjectileGeneration || IsActorBeingDestroyed()) return;
            auto S = Q.Record.Get();
            const bool Victim = Q.DirectVictim.Get() == E;
            if (S.Generation != EncounterGeneration || S.ProjectileGeneration != ResetGeneration ||
                Q.Attribution.Get() == E || !CombatAI::EligibleSound(S.Category,S.Kind,Victim) ||
                Now-S.OccurredWorld > CombatAI::MaxDeliveryAge(S.Kind)) continue;
            S.ReceivedWorld = Now;
            if (S.Kind == CombatAI::Sense::Damage)
            {
                // Bearing has no source range. The 5 m point is an investigation
                // proposal inside a broad region, not an inferred shooter position.
                const FVector Bearing = Vector(S.Bearing).GetSafeNormal2D();
                const FVector Origin = Vector(S.Region);
                S.Region = Point(Origin + Bearing*500); S.Uncertainty=650; S.Confidence=.85;
            }
            else
            {
                const FVector Emission = Vector(S.Region);
                const double Distance = FVector::Dist(Ear, Emission);
                if (Distance > Q.Range) continue;
                FHitResult Hit;
                FCollisionQueryParams Query(SCENE_QUERY_STAT(CombatHearing), false);
                FCollisionResponseParams StaticOnly(ECR_Ignore);
                StaticOnly.CollisionResponse.SetResponse(ECC_WorldStatic, ECR_Block);
                const bool Blocked = GetWorld()->LineTraceSingleByChannel(Hit, Ear,
                    Emission + FVector(0,0,35), ECC_Visibility, Query, StaticOnly);
                const auto Heard = CombatAI::LocalizeSound(S.Region, Distance, Q.Range, Blocked);
                if (!Heard.Audible) continue;
                S.Region=Heard.Region; S.Uncertainty=Heard.Radius; S.Confidence=Heard.Confidence;
            }
            E->Combat->ReceiveStimulus(CombatAI::Stimulus(S)); ++DeliveredStimuli;
        }
    }
}
