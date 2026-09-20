#include "DummyRecoveryAnimInstance.h"
#include "Animation/AnimInstanceProxy.h"
#include "AnimNodes/AnimNode_PoseSnapshot.h"
#include "AnimNodes/AnimNode_SequenceEvaluator.h"
#include "AnimNodes/AnimNode_TwoWayBlend.h"

struct FGroundedSequence : FAnimNode_SequenceEvaluator_Standalone
{
    float OffsetZ = 0;
    virtual void Evaluate_AnyThread(FPoseContext& Output) override
    {
        FAnimNode_SequenceEvaluator_Standalone::Evaluate_AnyThread(Output);
        Output.Pose[FCompactPoseBoneIndex(0)].AddToTranslation(FVector(0,0,OffsetZ));
    }
};

struct FDummyRecoveryAnimProxy : FAnimInstanceProxy
{
    FAnimNode_PoseSnapshot Fallen;
    FGroundedSequence Motion;
    FAnimNode_TwoWayBlend StartBlend;
    FAnimNode_PoseSnapshot Idle;
    FAnimNode_TwoWayBlend EndBlend;

    explicit FDummyRecoveryAnimProxy(UAnimInstance* Instance) : FAnimInstanceProxy(Instance)
    {
        Fallen.Mode = Idle.Mode = ESnapshotSourceMode::SnapshotPin;
        StartBlend.A.SetLinkNode(&Fallen);
        StartBlend.B.SetLinkNode(&Motion);
        EndBlend.A.SetLinkNode(&StartBlend);
        EndBlend.B.SetLinkNode(&Idle);
        // Explicit time is clamped by the caller; teleport evaluation does not loop.
        Motion.SetTeleportToExplicitTime(true);
    }
    virtual FAnimNode_Base* GetCustomRootNode() override { return &EndBlend; }
    virtual void GetCustomNodes(TArray<FAnimNode_Base*>& Nodes) override
    { Nodes = {&Fallen, &Motion, &StartBlend, &Idle, &EndBlend}; }
    virtual void PreUpdate(UAnimInstance* Instance, float DeltaSeconds) override
    {
        auto* Input = CastChecked<UDummyRecoveryAnimInstance>(Instance);
        Fallen.Snapshot = Input->StartPose;
        Idle.Snapshot = Input->EndPose;
        Motion.SetSequence(Input->Sequence);
        Motion.SetExplicitTime(Input->SequenceTime);
        Motion.OffsetZ = Input->MotionOffsetZ;
        StartBlend.Alpha = Input->bSnapshotOnly ? 0.f : Input->StartAlpha;
        EndBlend.Alpha = Input->bSnapshotOnly ? 0.f : Input->EndAlpha;
        FAnimInstanceProxy::PreUpdate(Instance, DeltaSeconds);
    }
};

FAnimInstanceProxy* UDummyRecoveryAnimInstance::CreateAnimInstanceProxy()
{ return new FDummyRecoveryAnimProxy(this); }
void UDummyRecoveryAnimInstance::DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy)
{ delete Proxy; }
