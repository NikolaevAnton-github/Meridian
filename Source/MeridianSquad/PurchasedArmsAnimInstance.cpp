#include "PurchasedArmsAnimInstance.h"
#include "OpeningLobbyCharacter.h"
#include "Animation/AnimInstanceProxy.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimationPoseData.h"
#include "AnimationRuntime.h"
#include "Components/SkeletalMeshComponent.h"

namespace
{
void Sample(FPoseContext& Out, UAnimSequence* Clip, float Time, UAnimSequence* Base = nullptr)
{
    Out.ResetToRefPose();
    if (!Clip) return;
    FAnimationPoseData Pose(Out);
    const FAnimExtractContext Context(static_cast<double>(Time), false);
    if (Clip->IsValidAdditive())
    {
        // Explicit runtime base references survive cooking, unlike preview-only animation state.
        if (Base) Base->GetAnimationPose(Pose, FAnimExtractContext(0.0, false));
        FPoseContext Delta(Out);
        FAnimationPoseData DeltaPose(Delta);
        Clip->GetAnimationPose(DeltaPose, Context);
        FAnimationRuntime::AccumulateAdditivePose(Pose, DeltaPose, 1.f, Clip->AdditiveAnimType);
        Out.Pose.NormalizeRotations();
    }
    else Clip->GetAnimationPose(Pose, Context);
}

void Blend(FPoseContext& Out, FPoseContext& A, FPoseContext& B, float Alpha)
{
    FAnimationPoseData Result(Out);
    FAnimationRuntime::BlendTwoPosesTogether(FAnimationPoseData(A), FAnimationPoseData(B), 1.f - Alpha, Result);
}
}

struct FPurchasedArmsAnimProxy : FAnimInstanceProxy
{
    explicit FPurchasedArmsAnimProxy(UAnimInstance* Instance) : FAnimInstanceProxy(Instance) {}
    TArray<TObjectPtr<UAnimSequence>> Locomotion, Reloads, Bases;
    FVector2D Movement = FVector2D::ZeroVector;
    float Time = 0.f, ActionTime = 0.f, ActionDuration = 0.f, Aim = 0.f, ReloadWeight = 0.f;
    float EvaluatedTime = 0.f, EvaluatedActionTime = 0.f;
    int32 Evaluations = 0;
    bool bRifle = false;

    virtual void PreUpdate(UAnimInstance* Instance, float DeltaSeconds) override
    {
        FAnimInstanceProxy::PreUpdate(Instance, DeltaSeconds);
        if (const AOpeningLobbyCharacter* Pawn = Cast<AOpeningLobbyCharacter>(Instance->GetOwningActor()))
        {
            // Copy on the game thread; evaluation never reads mutable actor state.
            bRifle = Instance->GetSkelMeshComponent() == Pawn->Rifle;
            Locomotion = Pawn->LocomotionClips;
            Reloads = bRifle ? Pawn->RifleReloadClips : Pawn->ReloadClips;
            Bases = Pawn->BasePoses;
            Movement = Pawn->MoveBlend;
            Time = Pawn->AnimationTime;
            ActionTime = Pawn->ReloadTime;
            ActionDuration = Pawn->ReloadDuration;
            Aim = Pawn->bReloading ? Pawn->ReloadAimAlpha : Pawn->AimAlpha;
            ReloadWeight = Pawn->bReloading ? FMath::Min(FMath::Clamp(ActionTime / .12f, 0.f, 1.f),
                FMath::Clamp((Pawn->ReloadDuration - ActionTime) / .15f, 0.f, 1.f)) : 0.f;
        }
    }

    virtual bool Evaluate(FPoseContext& Out) override
    {
        ++Evaluations;
        EvaluatedTime = Time;
        EvaluatedActionTime = ActionTime;
        Out.ResetToRefPose();
        if (Locomotion.Num() != 10 || Reloads.Num() != 2 || Bases.Num() != 2) return true;
        if (!bRifle)
        {
            const float Amount = FMath::Clamp(Movement.Size(), 0.f, 1.f);
            const float Sum = FMath::Max(FMath::Abs(Movement.X) + FMath::Abs(Movement.Y), SMALL_NUMBER);
            const float Weights[] = {1.f - Amount,
                Amount * FMath::Max(Movement.X, 0.f) / Sum,
                Amount * FMath::Max(-Movement.X, 0.f) / Sum,
                Amount * FMath::Max(-Movement.Y, 0.f) / Sum,
                Amount * FMath::Max(Movement.Y, 0.f) / Sum};
            float Accumulated = 0.f;
            for (int32 Index = 0; Index < 10; ++Index)
            {
                const float Weight = Weights[Index % 5] * (Index < 5 ? 1.f - Aim : Aim);
                if (Weight <= SMALL_NUMBER || !Locomotion[Index]) continue;
                FPoseContext Next(Out);
                Sample(Next, Locomotion[Index], FMath::Fmod(Time, Locomotion[Index]->GetPlayLength()));
                if (Accumulated <= SMALL_NUMBER) Out = Next;
                else
                {
                    FPoseContext Previous(Out);
                    Previous = Out;
                    Blend(Out, Previous, Next, Weight / (Accumulated + Weight));
                }
                Accumulated += Weight;
            }
            // Aimed locomotion clips reduce sway but still use the hip holding pose.
            // Apply the source aim-pose offset before layering the separately authored reload.
            if (Aim > SMALL_NUMBER)
            {
                FPoseContext HipBase(Out), AimOffset(Out);
                Sample(HipBase, Bases[0], 0.f);
                Sample(AimOffset, Bases[1], 0.f);
                FAnimationPoseData AimData(AimOffset), Result(Out);
                FAnimationRuntime::ConvertPoseToAdditive(AimOffset.Pose, HipBase.Pose);
                AimOffset.Curve.ConvertToAdditive(HipBase.Curve);
                FAnimationRuntime::AccumulateAdditivePose(Result, AimData, Aim, AAT_LocalSpaceBase);
            }
        }
        if (ReloadWeight > SMALL_NUMBER)
        {
            FPoseContext Hip(Out), ADS(Out), ReloadPose(Out), Previous(Out);
            Previous = Out;
            Sample(Hip, Reloads[0], ActionTime, bRifle ? nullptr : Bases[0].Get());
            Sample(ADS, Reloads[1], ActionTime, bRifle ? nullptr : Bases[1].Get());
            Blend(ReloadPose, Hip, ADS, Aim);
            Blend(Out, Previous, ReloadPose, ReloadWeight);
            if (bRifle && ActionTime >= ActionDuration - .15f)
            {
                // The visible replacement is seated in the authored reserve pose. Its reference
                // pose is storage below the rifle, so preserve this channel through the fade.
                // At completion the equally seated reference main becomes the visible magazine.
                const FBoneContainer& Bones = Out.Pose.GetBoneContainer();
                const int32 MeshIndex = Bones.GetPoseBoneIndexForBoneName(TEXT("Magazine_Reserve"));
                if (MeshIndex != INDEX_NONE)
                {
                    const FCompactPoseBoneIndex Index = Bones.MakeCompactPoseIndex(FMeshPoseBoneIndex(MeshIndex));
                    if (Index != INDEX_NONE) Out.Pose[Index] = ReloadPose.Pose[Index];
                }
            }
        }
        Out.Pose.NormalizeRotations();
        return true;
    }
};

FAnimInstanceProxy* UPurchasedArmsAnimInstance::CreateAnimInstanceProxy()
{
    return new FPurchasedArmsAnimProxy(this);
}

void UPurchasedArmsAnimInstance::DestroyAnimInstanceProxy(FAnimInstanceProxy* InProxy)
{
    delete InProxy;
}

FString UPurchasedArmsAnimInstance::GetEvaluationState() const
{
    const FPurchasedArmsAnimProxy& Proxy = GetProxyOnGameThread<FPurchasedArmsAnimProxy>();
    return FString::Printf(TEXT("{\"evaluations\":%d,\"time\":%.6f,\"action_time\":%.6f,\"aim\":%.6f,\"reload_weight\":%.6f,\"rifle\":%s}"),
        Proxy.Evaluations, Proxy.EvaluatedTime, Proxy.EvaluatedActionTime, Proxy.Aim, Proxy.ReloadWeight,
        Proxy.bRifle ? TEXT("true") : TEXT("false"));
}
