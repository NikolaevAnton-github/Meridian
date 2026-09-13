#include "OpeningLobbyGameMode.h"
#include "OpeningLobbyCharacter.h"

AOpeningLobbyGameMode::AOpeningLobbyGameMode()
{
    DefaultPawnClass = AOpeningLobbyCharacter::StaticClass();
}
