#include "OpeningLobbyCharacter.h"
#include "Engine/DamageEvents.h"
#include "Engine/World.h"

DEFINE_LOG_CATEGORY_STATIC(LogPlayerCombatReceiver, Log, All);

float AOpeningLobbyCharacter::TakeDamage(float Amount, const FDamageEvent& Event,
    AController* EventInstigator, AActor* Causer)
{
    if (!FMath::IsFinite(Amount) || Amount <= 0.f) return 0.f;
    // Super dispatches the standard OnTakePointDamage/OnTakeAnyDamage events.
    // These are the MSQ-71 integration seam; counters never subtract health.
    const float Applied = Super::TakeDamage(Amount, Event, EventInstigator, Causer);
    if (Applied <= 0.f) return Applied;
    ++ReceivedCombatHits; ReceivedCombatDamage += Applied; LastCombatDamage = Applied;
    LastCombatDamageCauser = Causer; LastCombatHitRealTime = FPlatformTime::Seconds();
    LastCombatHitDirection = Event.IsOfType(FPointDamageEvent::ClassID) ?
        static_cast<const FPointDamageEvent&>(Event).ShotDirection : FVector::ZeroVector;
    UE_LOG(LogPlayerCombatReceiver, Log, TEXT("player=%s hits=%d amount=%.1f total=%.1f source=%s instigator=%s world_time=%.3f"),
        *GetName(), ReceivedCombatHits, Applied, ReceivedCombatDamage,
        *GetNameSafe(Causer), *GetNameSafe(EventInstigator), GetWorld()->GetTimeSeconds());
    return Applied;
}

void AOpeningLobbyCharacter::ResetCombatReceiver()
{
    ReceivedCombatHits = 0; ReceivedCombatDamage = LastCombatDamage = 0;
    LastCombatDamageCauser = nullptr; LastCombatHitRealTime = -1000;
    LastCombatHitDirection = FVector::ZeroVector;
}
