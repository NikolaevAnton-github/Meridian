#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Chaos/ChaosNotifyHandlerInterface.h"
#include "DestructionCollisionPolicy.generated.h"

class FJsonObject;
class FStructProperty;
class UGeometryCollectionComponent;

/** Opt-in, source-verified native equivalent of the vendor collision event. */
UCLASS()
class MERIDIANSQUAD_API UDestructionCollisionPolicy : public UActorComponent
{
    GENERATED_BODY()
public:
    UDestructionCollisionPolicy();
    bool Initialize(UGeometryCollectionComponent* InCollection);
    // Retirement only: callers also retire the owner and its original latent work.
    void Restore();
    TSharedRef<FJsonObject> Snapshot() const;
    UFUNCTION() void ReceiveCollision(const FChaosPhysicsCollisionInfo& CollisionInfo);
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;

private:
    UPROPERTY(Transient) TObjectPtr<UGeometryCollectionComponent> Collection;
    UPROPERTY(Transient) TObjectPtr<UClass> BoundClass;
    UPROPERTY(Transient) FOnChaosPhysicsCollision OriginalDelegates;
    FScriptDelegate OriginalBinding;
    FStructProperty* CollisionInfoProperty = nullptr;
    FString Mode = TEXT("native");
    FString ValidationReason = TEXT("not initialized");
    bool bInitialized = false;
    bool bInstalled = false;
    bool bValidated = false;
    int64 RawCallbacks = 0;
    int64 ForwardedCallbacks = 0;
    int64 NativeCallbacks = 0;
    int64 FallbackCallbacks = 0;
    int64 ProfileRequested = 0;
    int64 ProfileApplied = 0;
    int64 ProfileSkippedIdentical = 0;
    int64 ProfileSkippedSetter = 0;
    int64 ProfileUnapplied = 0;
    int64 ProfileNativeCalls = 0;
    int64 SleepRetriggers = 0;
    int64 ResetInvalidations = 0;
};
