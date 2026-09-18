#include "CombatPrototypeHUD.h"
#include "CombatRifleComponent.h"
#include "CombatProjectileWorld.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "GameFramework/PlayerController.h"

void ACombatPrototypeHUD::DrawHUD()
{
    Super::DrawHUD();
    const APawn* Pawn = PlayerOwner ? PlayerOwner->GetPawn() : nullptr;
    const auto* Rifle = Pawn ? Pawn->FindComponentByClass<UCombatRifleComponent>() : nullptr;
    if (!Canvas || !Rifle) return;
    const float Scale = FMath::Clamp(Canvas->SizeY / 900.f, .8f, 1.4f);
    const float X = 24.f * Scale;
    const float Y = Canvas->SizeY - 130.f * Scale;
    DrawRect(FLinearColor(0.012f, .018f, .025f, .8f), X - 10 * Scale, Y - 8 * Scale, 410 * Scale, 114 * Scale);
    DrawText(TEXT("COMBAT PROTOTYPE"), FLinearColor(.55f,.65f,.7f), X, Y, GEngine->GetSmallFont(), Scale);
    DrawText(FString::Printf(TEXT("%02d / %02d   |   RESERVE %03d   |   %s"), Rifle->Magazine,
        Rifle->MagazineCapacity, Rifle->Reserve, Rifle->bAutomatic ? TEXT("AUTO") : TEXT("SEMI")),
        Rifle->Magazine > 0 ? FLinearColor::White : FLinearColor(1,.4f,.2f), X, Y + 21 * Scale, GEngine->GetMediumFont(), Scale);
    DrawText(Rifle->StatusText.IsEmpty() ? TEXT("LMB fire   RMB aim   V mode   R reload / hold check") : Rifle->StatusText,
        FLinearColor(.75f,.83f,.85f), X, Y + 54 * Scale, GEngine->GetSmallFont(), Scale);
    DrawText(TEXT("Q quick reload   E reload   F6 reset targets"), FLinearColor(.65f,.73f,.76f),
        X, Y + 77 * Scale, GEngine->GetSmallFont(), Scale);
    const float CX = Canvas->SizeX * .5f, CY = Canvas->SizeY * .5f;
    DrawRect(FLinearColor(1,1,1,.65f), CX - 1, CY - 1, 2, 2);
    if (const auto* World = ACombatProjectileWorld::Find(GetWorld()))
    {
        if (FPlatformTime::Seconds() - World->LastHitRealTime < 1.2f)
            DrawText(World->LastHitText, FLinearColor(1,.75f,.35f), CX - 150 * Scale, CY + 42 * Scale, GEngine->GetSmallFont(), Scale);
        if (World->GetProjectileTimeScale() < 1.f)
            DrawText(FString::Printf(TEXT("DEVELOPMENT PROBE: BULLET TIME %.2f"), World->GetProjectileTimeScale()),
                FLinearColor(1,.65f,.2f), X, Y - 30 * Scale, GEngine->GetSmallFont(), Scale);
    }
}
