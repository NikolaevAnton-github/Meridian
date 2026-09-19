#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "EnemyPrototypeCharacter.generated.h"

class UAnimSequence;
class UTextRenderComponent;

/** A sampled, bone-bound query volume. Rendering and rigid-body collision are separate. */
struct FEnemyHitSphere
{
    FName Bone;
    FVector Center;
    float Radius;
};

/** Removable asset-readiness fixture. Preview motion is scripted, not enemy AI. */
UCLASS()
class MERIDIANSQUAD_API AEnemyPrototypeCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    AEnemyPrototypeCharacter();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual float TakeDamage(float Amount, const FDamageEvent& Event, AController* EventInstigator, AActor* Causer) override;
    UFUNCTION(BlueprintCallable, Category="Combat|Prototype")
    void ResetEnemy();
    UFUNCTION(BlueprintCallable, Category="Combat|Prototype")
    void SetPreviewMoving(bool Moving);
    bool IsPreviewMoving() const { return bPreviewMoving; }
    UFUNCTION(BlueprintCallable, Category="Combat|Prototype")
    void PreviewFire();
    UFUNCTION(BlueprintPure, Category="Combat|Verification")
    FString GetEnemyState() const;
    TArray<FEnemyHitSphere> SampleHitSpheres() const;
    static FName RegionForBone(FName Bone);
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Combat", meta=(ClampMin="1"))
    float MaxHealth = 100.f;
    UPROPERTY(BlueprintReadOnly, Category="Combat")
    float Health = 100.f;
    UPROPERTY(BlueprintReadOnly, Category="Combat")
    int32 Hits = 0;
    UPROPERTY(BlueprintReadOnly, Category="Combat")
    int32 Deaths = 0;
    UPROPERTY(BlueprintReadOnly, Category="Combat")
    FName LastRegion;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Combat")
    TObjectPtr<USkeletalMeshComponent> PreviewRifle;
private:
    UPROPERTY() TObjectPtr<UTextRenderComponent> Label;
    UPROPERTY() TObjectPtr<UAnimSequence> IdleAnimation;
    UPROPERTY() TObjectPtr<UAnimSequence> LeftAnimation;
    UPROPERTY() TObjectPtr<UAnimSequence> RightAnimation;
    UPROPERTY() TObjectPtr<UAnimSequence> HitAnimation;
    UPROPERTY() TObjectPtr<UAnimSequence> FireAnimation;
    UPROPERTY() TObjectPtr<UAnimSequence> CurrentAnimation;
    FTransform Home;
    bool bPreviewMoving = false;
    bool bDead = false;
    float PreviewDirection = 1.f;
    float ResponseRemaining = 0.f;
    float DeathAge = 0.f;
    void Play(UAnimSequence* Animation, bool Loop);
    void UpdateLabel();
};
