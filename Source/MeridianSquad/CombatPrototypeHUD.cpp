#include "CombatPrototypeHUD.h"
#include "CombatRifleComponent.h"
#include "CombatProjectileWorld.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "GameFramework/PlayerController.h"
#include "PhysicsControlDummy.h"
#include "GASPEnemyFixture.h"
#include "EnemyCombatComponent.h"
#include "OpeningLobbyCharacter.h"
#include "EngineUtils.h"

void ACombatPrototypeHUD::DrawHUD()
{
    Super::DrawHUD();
    const APawn* Pawn = PlayerOwner ? PlayerOwner->GetPawn() : nullptr;
    const auto* Rifle = Pawn ? Pawn->FindComponentByClass<UCombatRifleComponent>() : nullptr;
    if (!Canvas || !Rifle) return;
    const float Scale = FMath::Clamp(Canvas->SizeY / 900.f, .8f, 1.4f);
    const float X = 24.f * Scale;
    const float Y = Canvas->SizeY - 173.f * Scale;
    DrawRect(FLinearColor(0.012f, .018f, .025f, .8f), X - 10 * Scale, Y - 8 * Scale, 440 * Scale, 157 * Scale);
    DrawText(TEXT("COMBAT PROTOTYPE"), FLinearColor(.55f,.65f,.7f), X, Y, GEngine->GetSmallFont(), Scale);
    const FString ReserveText = Rifle->bInfiniteReserve ? TEXT("INF") : FString::Printf(TEXT("%03d"), Rifle->Reserve);
    DrawText(FString::Printf(TEXT("%02d / %02d   |   RESERVE %s   |   %s"), Rifle->Magazine,
        Rifle->MagazineCapacity, *ReserveText, Rifle->bAutomatic ? TEXT("AUTO") : TEXT("SEMI")),
        Rifle->Magazine > 0 ? FLinearColor::White : FLinearColor(1,.4f,.2f), X, Y + 21 * Scale, GEngine->GetMediumFont(), Scale);
    DrawText(Rifle->StatusText.IsEmpty() ? TEXT("LMB fire   RMB aim   V mode   R reload / hold check") : Rifle->StatusText,
        FLinearColor(.75f,.83f,.85f), X, Y + 54 * Scale, GEngine->GetSmallFont(), Scale);
    DrawText(TEXT("F6 reset   Y slow preview   F10 mannequins"), FLinearColor(.65f,.73f,.76f),
        X, Y + 77 * Scale, GEngine->GetSmallFont(), Scale);
    const auto* CombatWorld = ACombatProjectileWorld::Find(GetWorld());
    DrawText(FString::Printf(TEXT("Ctrl+F7 immortal: %s   Ctrl+F8 reserve: %s"),
        CombatWorld && CombatWorld->bImmortalDummies ? TEXT("ON") : TEXT("OFF"),
        Rifle->bInfiniteReserve ? TEXT("ON") : TEXT("OFF")), FLinearColor(.65f,.83f,.76f),
        X, Y + 100 * Scale, GEngine->GetSmallFont(), Scale);
    DrawText(FString::Printf(TEXT("Ctrl+F9 bounded recovery assist: %s"),
        CombatWorld && CombatWorld->bRecoveryAssistance ? TEXT("ON") : TEXT("OFF")), FLinearColor(.65f,.83f,.76f),
        X, Y + 123 * Scale, GEngine->GetSmallFont(), Scale);
    const float CX = Canvas->SizeX * .5f, CY = Canvas->SizeY * .5f;
    DrawRect(FLinearColor(1,1,1,.65f), CX - 1, CY - 1, 2, 2);
    if (const auto* Player = Cast<AOpeningLobbyCharacter>(Pawn))
    {
        DrawText(FString::Printf(TEXT("PLAYER HITS %d   DAMAGE %.0f   |   F6 restart"),
            Player->ReceivedCombatHits, Player->ReceivedCombatDamage), FLinearColor(1.f,.65f,.5f),
            X, Y - 55 * Scale, GEngine->GetSmallFont(), Scale);
        const float HitFade = FMath::Clamp(float(1.0 - (FPlatformTime::Seconds() - Player->LastCombatHitRealTime) / .65), 0.f, 1.f);
        if (HitFade > 0)
        {
            DrawRect(FLinearColor(.8f,.05f,.02f, .18f * HitFade), 0, 0, Canvas->SizeX, 12 * Scale);
            DrawText(FString::Printf(TEXT("HIT -%.0f"), Player->LastCombatDamage), FLinearColor(1,.2f,.08f,HitFade),
                CX - 32 * Scale, CY - 70 * Scale, GEngine->GetMediumFont(), Scale);
        }
    }
    for (TActorIterator<APhysicsControlDummy> It(GetWorld()); It; ++It)
    {
        const FVector Point = It->GetPhysicalBodyLocation(TEXT("head")) + FVector(0, 0, 28);
        FVector2D Screen;
        if (!PlayerOwner->ProjectWorldLocationToScreen(Point, Screen, true) || Screen.X < 0 || Screen.X > Canvas->SizeX ||
            Screen.Y < 0 || Screen.Y > Canvas->SizeY) continue;
        FCollisionQueryParams Query(SCENE_QUERY_STAT(FixtureLabel), true);
        if (const auto* Manager = ACombatProjectileWorld::Find(GetWorld())) Manager->BuildQuery(Query, Pawn);
        FVector Eye; FRotator View; PlayerOwner->GetPlayerViewPoint(Eye, View);
        FHitResult Obstruction;
        if (GetWorld()->LineTraceSingleByChannel(Obstruction, Eye, Point, ECC_Visibility, Query)) continue;
        if (const auto* Manager = ACombatProjectileWorld::Find(GetWorld()))
            if (Manager->TraceEnemyAim(Eye, Point, Manager->GetFiringClock(), Obstruction) && Obstruction.GetActor() != *It) continue;
        const auto* GASP = Cast<AGASPEnemyFixture>(*It);
        const bool bCombat = GASP && GASP->Combat && GASP->Combat->bEnabled;
        DrawRect(FLinearColor(.01f,.02f,.025f,.85f), Screen.X - 88 * Scale, Screen.Y - 4 * Scale, 176 * Scale, (bCombat ? 48 : 26) * Scale);
        DrawText(FString::Printf(TEXT("%d  |  %.0f HP%s"), It->ReactionProfile, It->Health, It->IsDead() ? TEXT("  CORPSE") : TEXT("")),
            FLinearColor(.4f,.9f,1.f), Screen.X - 56 * Scale, Screen.Y, GEngine->GetMediumFont(), Scale);
        if (bCombat)
            DrawText(GASP->Combat->GetLabel(), FLinearColor(1.f,.75f,.35f), Screen.X - 80 * Scale,
                Screen.Y + 23 * Scale, GEngine->GetSmallFont(), Scale);
    }
    if (const auto* World = ACombatProjectileWorld::Find(GetWorld()))
    {
        if (FPlatformTime::Seconds() - World->LastHitRealTime < 1.2f)
            DrawText(World->LastHitText, FLinearColor(1,.75f,.35f), CX - 150 * Scale, CY + 42 * Scale, GEngine->GetSmallFont(), Scale);
        if (World->GetProjectileTimeScale() < 1.f)
            DrawText(FString::Printf(TEXT("DEVELOPMENT PROBE: BULLET TIME %.2f"), World->GetProjectileTimeScale()),
                FLinearColor(1,.65f,.2f), X, Y - 30 * Scale, GEngine->GetSmallFont(), Scale);
    }
}
