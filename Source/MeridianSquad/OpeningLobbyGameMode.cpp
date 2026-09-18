#include "OpeningLobbyGameMode.h"
#include "OpeningLobbyCharacter.h"
#include "UObject/ConstructorHelpers.h"

AOpeningLobbyGameMode::AOpeningLobbyGameMode()
{
    static ConstructorHelpers::FClassFinder<APawn> PurchasedPawn(TEXT("/Game/InfimaGames/TacticalFPSAnimations/Common/Core/Characters/BP_TFA_BaseCharacter"));
    DefaultPawnClass = PurchasedPawn.Class ? PurchasedPawn.Class.Get() : AOpeningLobbyCharacter::StaticClass();
}
