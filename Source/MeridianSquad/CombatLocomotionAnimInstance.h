#pragma once
#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "CombatLocomotionAnimInstance.generated.h"

/** Distance-based movement audio owns steps during a combat world. */
UCLASS(Transient, Blueprintable)
class MERIDIANSQUAD_API UCombatLocomotionAnimInstance : public UAnimInstance
{
    GENERATED_BODY()
public:
    virtual bool HandleNotify(const FAnimNotifyEvent& Event) override;
};
