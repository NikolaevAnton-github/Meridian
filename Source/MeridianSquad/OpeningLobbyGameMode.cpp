#include "OpeningLobbyGameMode.h"
#include "OpeningLobbyCharacter.h"
#include "CombatProjectileWorld.h"
#include "CombatPrototypeHUD.h"
#include "Engine/World.h"
#include "UObject/ConstructorHelpers.h"

AOpeningLobbyGameMode::AOpeningLobbyGameMode()
{
    static ConstructorHelpers::FClassFinder<APawn> PurchasedPawn(TEXT("/Game/InfimaGames/TacticalFPSAnimations/Common/Core/Characters/BP_TFA_BaseCharacter"));
    DefaultPawnClass = PurchasedPawn.Class ? PurchasedPawn.Class.Get() : AOpeningLobbyCharacter::StaticClass();
    HUDClass = ACombatPrototypeHUD::StaticClass();
}

void AOpeningLobbyGameMode::BeginPlay()
{
    Super::BeginPlay();
    FActorSpawnParameters Params;
    Params.ObjectFlags |= RF_Transient;
    GetWorld()->SpawnActor<ACombatProjectileWorld>(FVector::ZeroVector, FRotator::ZeroRotator, Params);
}
