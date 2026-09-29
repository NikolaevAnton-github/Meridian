#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "PrototypeGrenadeComponent.generated.h"

class AOpeningLobbyCharacter;
class UAnimMontage;
class UEnhancedInputComponent;
class UStaticMeshComponent;

/** Connects the existing throw animation to the purchased NGD sphere grenade. */
UCLASS(ClassGroup=(Combat), meta=(BlueprintSpawnableComponent))
class MERIDIANSQUAD_API UPrototypeGrenadeComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UPrototypeGrenadeComponent();
    void Initialize();
    void BindInput(UEnhancedInputComponent* Input);
    void StartThrow();
    bool SpawnFixed(FVector Position);
    void Reset();
    static void ResetWorld(UWorld* World);
    virtual void TickComponent(float Delta, ELevelTick TickType, FActorComponentTickFunction* TickFunction) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    UFUNCTION(BlueprintPure, Category="Combat|Grenade") FString GetState() const;

    UPROPERTY(EditAnywhere, Category="Combat|Grenade", meta=(ClampMin="0.05")) float ReleaseTime = .65f;
    UPROPERTY(EditAnywhere, Category="Combat|Grenade", meta=(ClampMin="100", ClampMax="3000")) float ThrowSpeed = 1200.f;
    UPROPERTY(EditAnywhere, Category="Combat|Grenade", meta=(ClampMin="50", ClampMax="1000")) float BlastRadius = 400.f;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Combat|Grenade") int32 Throws = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Combat|Grenade") int32 Explosions = 0;
private:
    UPROPERTY(Transient) TObjectPtr<AOpeningLobbyCharacter> Character;
    UPROPERTY(Transient) TObjectPtr<UAnimMontage> ThrowMontage;
    UPROPERTY(Transient) TObjectPtr<UStaticMeshComponent> HeldSphere;
    UPROPERTY(Transient) TSubclassOf<AActor> GrenadeClass;
    TArray<TWeakObjectPtr<AActor>> Grenades;
    TArray<TWeakObjectPtr<AActor>> Fields;
    TArray<FName> FieldNames;
    FDelegateHandle SpawnHandle;
    int32 ThrowInstance = INDEX_NONE;
    bool bReleased = false;
    void Release();
    void OnActorSpawned(AActor* Actor);
};
