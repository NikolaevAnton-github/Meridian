#pragma once
#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "CombatPrototypeHUD.generated.h"

/** Deliberately small prototype readout; authoritative ammunition and collision feedback. */
UCLASS()
class MERIDIANSQUAD_API ACombatPrototypeHUD : public AHUD
{
    GENERATED_BODY()
public:
    virtual void DrawHUD() override;
};
