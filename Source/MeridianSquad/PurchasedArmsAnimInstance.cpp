#include "PurchasedArmsAnimInstance.h"
#include "OpeningLobbyCharacter.h"
#include "CombatRifleComponent.h"
#include "Components/SceneComponent.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimNode_AssetPlayerBase.h"
#include "Animation/AnimBlueprintGeneratedClass.h"
#include "UObject/UnrealType.h"

void UPurchasedArmsAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);
    const auto* Character = Cast<AOpeningLobbyCharacter>(TryGetPawnOwner());
    // Game-thread snapshot consumed by the source animation transition rules.
    bUseOrdinaryJumpBase = Character && Character->NeedsOrdinaryJumpBase();
}

void UPurchasedArmsAnimInstance::NativePostEvaluateAnimation()
{
    Super::NativePostEvaluateAnimation();
    ++Evaluations;
    EvaluatedWorldTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.f;
}

int32 UPurchasedArmsAnimInstance::GetCombatMagazineRounds() const
{
    const AActor* MagazineActor = GetOwningActor();
    const AActor* OwnerActor = MagazineActor;
    for (int32 Depth = 0; OwnerActor && Depth < 4; ++Depth, OwnerActor = OwnerActor->GetAttachParentActor())
        if (const auto* Rifle = OwnerActor->FindComponentByClass<UCombatRifleComponent>())
        {
            const auto* Root = MagazineActor->GetRootComponent();
            const bool Spare = Root && Root->GetAttachSocketName().ToString().Contains(TEXT("Reserve"));
            if (!Spare) return Rifle->Magazine;
            return Rifle->bInfiniteReserve ? Rifle->MagazineCapacity :
                FMath::Min(Rifle->MagazineCapacity, Rifle->Magazine + Rifle->Reserve);
        }
    return 0;
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
            const auto* Asset = Player->GetAnimAsset();
            Players += FString::Printf(TEXT("{\"node\":\"%s\",\"asset\":\"%s\",\"phase\":%.6f,\"weight\":%.6f}"),
                *Property->GetName(), Asset ? *Asset->GetPathName() : TEXT(""),
                Player->GetAccumulatedTime(), Player->GetCachedBlendWeight());
        }
    }
    return FString::Printf(TEXT("{\"evaluations\":%llu,\"world_time\":%.6f,\"montage\":\"%s\",\"action_time\":%.6f,\"hip_weight\":%.6f,\"aim_weight\":%.6f,\"players\":[%s]}"),
        Evaluations, EvaluatedWorldTime, Montage ? *Montage->GetName() : TEXT(""),
        Montage ? Montage_GetPosition(Montage) : 0.f, GetSlotMontageGlobalWeight(TEXT("DefaultSlot")),
        GetSlotMontageGlobalWeight(TEXT("Aiming")), *Players);
}
