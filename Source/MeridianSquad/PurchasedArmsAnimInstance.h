#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "PurchasedArmsAnimInstance.generated.h"

/** Runtime evaluation of the supplied poses, including local-space additive reloads. */
UCLASS(Transient)
class MERIDIANSQUAD_API UPurchasedArmsAnimInstance : public UAnimInstance
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintPure, Category="Lobby|Verification")
    FString GetEvaluationState() const;
protected:
    virtual FAnimInstanceProxy* CreateAnimInstanceProxy() override;
    virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* InProxy) override;
};
