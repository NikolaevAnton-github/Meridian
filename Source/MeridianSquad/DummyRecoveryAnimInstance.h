#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "Animation/PoseSnapshot.h"
#include "DummyRecoveryAnimInstance.generated.h"

/** Native AnimGraph: fallen snapshot -> advancing sequence -> grounded idle.
 * The same evaluated full skeleton supplies the visible mesh and physics targets.
 */
UCLASS(Transient)
class MERIDIANSQUAD_API UDummyRecoveryAnimInstance : public UAnimInstance
{
    GENERATED_BODY()
public:
    UPROPERTY() FPoseSnapshot StartPose;
    UPROPERTY() FPoseSnapshot EndPose;
    UPROPERTY() TObjectPtr<UAnimSequence> Sequence;
    float SequenceTime = 0;
    float StartAlpha = 1;
    float EndAlpha = 0;
    float MotionOffsetZ = 0;
    bool bSnapshotOnly = false;
protected:
    virtual FAnimInstanceProxy* CreateAnimInstanceProxy() override;
    virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy) override;
};
