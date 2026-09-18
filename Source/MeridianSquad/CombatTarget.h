#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CombatTarget.generated.h"

class UStaticMeshComponent;
class UTextRenderComponent;
class UMaterialInstanceDynamic;

/** Resettable runtime-only target. A simple prototype primitive, not enemy art. */
UCLASS()
class MERIDIANSQUAD_API ACombatTarget : public AActor
{
    GENERATED_BODY()
public:
    ACombatTarget();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual float TakeDamage(float Amount, const FDamageEvent& Event, AController* EventInstigator, AActor* Causer) override;
    UFUNCTION(BlueprintCallable, Category="Combat")
    void ResetTarget();
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Combat", meta=(ClampMin="1"))
    float MaxHealth = 100.f;
    UPROPERTY(BlueprintReadOnly, Category="Combat")
    float Health = 100.f;
    UPROPERTY(BlueprintReadOnly, Category="Combat")
    int32 Hits = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Combat")
    TObjectPtr<UStaticMeshComponent> TargetMesh;
private:
    UPROPERTY()
    TObjectPtr<UTextRenderComponent> Label;
    UPROPERTY(Transient)
    TObjectPtr<UMaterialInstanceDynamic> ColorMaterial;
    double FlashUntil = 0.0;
    void UpdatePresentation();
};
