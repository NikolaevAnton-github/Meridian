#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DestructibleCladding.generated.h"

class UStaticMesh;
class UStaticMeshComponent;

// Sent before the collision change, so future consumers can invalidate support/cover.
DECLARE_DYNAMIC_MULTICAST_DELEGATE_FiveParams(FCladdingChanged, int32, PieceId,
    FBox, AffectedWorldBounds, int32, CollisionRevision, int32, ResetGeneration, bool, bReset);

/** ED-01: individually bonded, pre-cut nonstructural shell. The backing is a separate solid actor. */
UCLASS()
class MERIDIANSQUAD_API ADestructibleCladding : public AActor
{
    GENERATED_BODY()
public:
    ADestructibleCladding();
    virtual void BeginPlay() override;
    virtual float TakeDamage(float Damage, const FDamageEvent& Event,
        AController* EventInstigator, AActor* Causer) override;

    UPROPERTY(EditAnywhere, Category="Cladding|Recipe") TArray<TObjectPtr<UStaticMesh>> PieceMeshes;
    UPROPERTY(EditAnywhere, Category="Cladding|Recipe") TArray<FTransform> PieceTransforms;
    UPROPERTY(EditAnywhere, Category="Cladding|Recipe") TArray<float> PieceMassKg;
    UPROPERTY(EditAnywhere, Category="Cladding|Tuning", meta=(ClampMin="1")) float BreakThreshold = 10.f;
    UPROPERTY(EditAnywhere, Category="Cladding|Tuning", meta=(ClampMin="0", ClampMax="150")) float ReleaseSpeedCmS = 80.f;
    UPROPERTY(EditAnywhere, Category="Cladding|Tuning", meta=(ClampMin="0", ClampMax="8")) float ReleaseClearanceCm = 4.5f;
    UPROPERTY(EditAnywhere, Category="Cladding|Tuning") FVector LocalOutwardNormal = FVector::YAxisVector;
    UPROPERTY(BlueprintAssignable, Category="Cladding") FCladdingChanged OnCladdingChanged;

    // Author once in the editor. Reset reuses the fixed component set without accumulating bodies.
    UFUNCTION(BlueprintCallable, CallInEditor, Category="Cladding") bool BuildSpecimen();
    UFUNCTION(BlueprintCallable, CallInEditor, Category="Cladding") void ResetSpecimen();
    UFUNCTION(BlueprintPure, Category="Cladding|Verification") FString GetCladdingState() const;

private:
    UPROPERTY(VisibleAnywhere, Instanced, Category="Cladding") TArray<TObjectPtr<UStaticMeshComponent>> Pieces;
    TArray<bool> Broken;
    int32 CollisionRevision = 0;
    int32 ResetGeneration = 0;
    bool bChanging = false;
    FVector LastHit = FVector::ZeroVector;
    int32 LastPiece = INDEX_NONE;
    float LastDamage = 0.f;
    double LastBreakMs = 0;
    void RestorePiece(int32 Index);
};
