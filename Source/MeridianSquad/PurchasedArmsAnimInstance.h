#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "PurchasedArmsAnimInstance.generated.h"

/** Source animation graph host with evaluated-frame telemetry for recovery checks. */
UCLASS(Transient)
class MERIDIANSQUAD_API UPurchasedArmsAnimInstance : public UAnimInstance
{
    GENERATED_BODY()
public:
    virtual void NativeUpdateAnimation(float DeltaSeconds) override;
    virtual void NativePostEvaluateAnimation() override;
    UPROPERTY(Transient, BlueprintReadOnly, Category="Lobby|Presentation")
    bool bUseOrdinaryJumpBase = false;
    UFUNCTION(BlueprintPure, Category="Lobby|Verification")
    FString GetEvaluationState() const;
private:
    uint64 Evaluations = 0;
    float EvaluatedWorldTime = 0.f;
};
