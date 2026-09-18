#include "PurchasedArmsAnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimNode_AssetPlayerBase.h"
#include "Animation/AnimBlueprintGeneratedClass.h"
#include "UObject/UnrealType.h"

void UPurchasedArmsAnimInstance::NativePostEvaluateAnimation()
{
    Super::NativePostEvaluateAnimation();
    ++Evaluations;
    EvaluatedWorldTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.f;
}

FString UPurchasedArmsAnimInstance::GetEvaluationState() const
{
    const UAnimMontage* Montage = GetCurrentActiveMontage();
    FString Players;
    if (const IAnimClassInterface* AnimClass = IAnimClassInterface::GetFromClass(GetClass()))
    {
        for (const FStructProperty* Property : AnimClass->GetAnimNodeProperties())
        {
            if (!Property->Struct->IsChildOf(FAnimNode_AssetPlayerBase::StaticStruct())) continue;
            const auto* Player = Property->ContainerPtrToValuePtr<FAnimNode_AssetPlayerBase>(this);
            if (!Players.IsEmpty()) Players += TEXT(",");
            Players += FString::Printf(TEXT("{\"node\":\"%s\",\"phase\":%.6f,\"weight\":%.6f}"),
                *Property->GetName(), Player->GetAccumulatedTime(), Player->GetCachedBlendWeight());
        }
    }
    return FString::Printf(TEXT("{\"evaluations\":%llu,\"world_time\":%.6f,\"montage\":\"%s\",\"action_time\":%.6f,\"hip_weight\":%.6f,\"aim_weight\":%.6f,\"players\":[%s]}"),
        Evaluations, EvaluatedWorldTime, Montage ? *Montage->GetName() : TEXT(""),
        Montage ? Montage_GetPosition(Montage) : 0.f, GetSlotMontageGlobalWeight(TEXT("DefaultSlot")),
        GetSlotMontageGlobalWeight(TEXT("Aiming")), *Players);
}