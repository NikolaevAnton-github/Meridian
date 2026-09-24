#pragma once

#include "CoreMinimal.h"
#include "CombatLocomotionAnimInstance.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "GASPALSRifleAnimInstance.generated.h"

/** Mover/physical-authority adapter for the imported GASPALS rifle poses. */
UCLASS(Transient, Blueprintable)
class MERIDIANSQUAD_API UGASPALSRifleAnimInstance : public UCombatLocomotionAnimInstance
{
    GENERATED_BODY()
public:
    virtual void NativeUpdateAnimation(float DeltaSeconds) override;
    UPROPERTY(BlueprintReadOnly, Category="Enemy|Rifle") float RifleAlpha = 0;
    UPROPERTY(BlueprintReadOnly, Category="Enemy|Rifle") float RifleReadyAlpha = 1;
    UPROPERTY(BlueprintReadOnly, Category="Enemy|Rifle") float RifleAimAlpha = 0;
    UPROPERTY(BlueprintReadOnly, Category="Enemy|Rifle") float RifleMoveAlpha = 0;
    UPROPERTY(BlueprintReadOnly, Category="Enemy|Rifle") float RifleCrouchAlpha = 0;
    UPROPERTY(BlueprintReadOnly, Category="Enemy|Rifle") float RiflePitchTime = .5f;
    UPROPERTY(BlueprintReadOnly, Category="Enemy|Rifle") float RifleLeanDegrees = 0;
    UFUNCTION(BlueprintPure, Category="Enemy|Rifle", meta=(BlueprintThreadSafe))
    FRotator GetRifleAimCorrection(FVector2D RootRelativeAim) const;
};

/** Bounded editor seam: the original and accepted skeletons are never mutated. */
UCLASS()
class MERIDIANSQUAD_API UGASPALSAnimationLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="Enemy|Rifle|Authoring")
    static bool AssignSkeleton(UAnimSequence* Sequence, USkeleton* Skeleton);
    UFUNCTION(BlueprintCallable, Category="Enemy|Rifle|Authoring")
    static FString CompareSkeletons(USkeleton* Source, USkeleton* Target);
    UFUNCTION(BlueprintCallable, Category="Enemy|Rifle|Authoring")
    static bool RemapImportedReferences(const TArray<UObject*>& Sources, const TArray<UObject*>& Derivatives);
};
