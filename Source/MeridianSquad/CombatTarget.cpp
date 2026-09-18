#include "CombatTarget.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/Material.h"
#include "UObject/ConstructorHelpers.h"

ACombatTarget::ACombatTarget()
{
    PrimaryActorTick.bCanEverTick = true;
    TargetMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Target"));
    SetRootComponent(TargetMesh);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    TargetMesh->SetStaticMesh(Cube.Object);
    TargetMesh->SetRelativeScale3D(FVector(.18, .75, 1.0));
    TargetMesh->SetCollisionProfileName(TEXT("BlockAllDynamic"));
    TargetMesh->SetCastShadow(false);
    Label = CreateDefaultSubobject<UTextRenderComponent>(TEXT("Status"));
    Label->SetupAttachment(TargetMesh);
    Label->SetAbsolute(false, false, true);
    Label->SetRelativeLocation(FVector(-65, 0, 75));
    Label->SetRelativeRotation(FRotator(0, 180, 0));
    Label->SetHorizontalAlignment(EHTA_Center);
    Label->SetWorldSize(15.f);
    Label->SetCastShadow(false);
}

void ACombatTarget::BeginPlay()
{
    Super::BeginPlay();
    ColorMaterial = TargetMesh->CreateDynamicMaterialInstance(0);
    ResetTarget();
}
void ACombatTarget::ResetTarget()
{
    Health = FMath::Max(1.f, MaxHealth);
    Hits = 0;
    FlashUntil = 0.0;
    TargetMesh->SetVisibility(true);
    TargetMesh->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    UpdatePresentation();
}
float ACombatTarget::TakeDamage(float Amount, const FDamageEvent& Event, AController* EventInstigator, AActor* Causer)
{
    if (Health <= 0 || !FMath::IsFinite(Amount) || Amount <= 0) return 0.f;
    const float Applied = FMath::Min(Health, Amount);
    Health -= Applied;
    ++Hits;
    FlashUntil = FPlatformTime::Seconds() + .18;
    if (Health <= 0)
    {
        TargetMesh->SetVisibility(false);
        TargetMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    }
    UpdatePresentation();
    return Applied;
}
void ACombatTarget::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (FlashUntil > 0 && FPlatformTime::Seconds() >= FlashUntil)
    {
        FlashUntil = 0;
        UpdatePresentation();
    }
}
void ACombatTarget::UpdatePresentation()
{
    const bool Alive = Health > 0;
    Label->SetText(FText::FromString(Alive ? FString::Printf(TEXT("TARGET  %.0f / %.0f"), Health, MaxHealth) : TEXT("DESTROYED\nF6: RESET")));
    Label->SetTextRenderColor(Alive ? (FlashUntil > 0 ? FColor(255, 210, 90) : FColor(180, 240, 215)) : FColor(255, 150, 85));
    if (ColorMaterial)
        ColorMaterial->SetVectorParameterValue(TEXT("Color"), FlashUntil > 0 ? FLinearColor(1,.2f,.04f) : FLinearColor(.16f,.55f,.4f));
}
