#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "GeometryCollection/GeometryCollectionComponent.h"
#include "DestructionIsolation.generated.h"

class FJsonObject;

/** Transient DP-02 relay; normal gameplay never creates this component. */
UCLASS()
class MERIDIANSQUAD_API UDestructionIsolationBridge : public UActorComponent
{
    GENERATED_BODY()
public:
    UDestructionIsolationBridge();
    bool Initialize(UGeometryCollectionComponent* Component, bool bBatch);
    void Flush();
    void Restore();
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    UFUNCTION() void OnBreak(const FChaosBreakEvent& Event);
private:
    UPROPERTY(Transient) TObjectPtr<UGeometryCollectionComponent> Collection;
    UPROPERTY(Transient) FOnChaosBreakEvent OriginalBreakDelegates;
    UPROPERTY(Transient) TArray<FChaosBreakEvent> Pending;
    FScriptDelegate OriginalBinding;
    bool bBatchEvents = false;
    bool bInstalled = false;
    void Forward(const FChaosBreakEvent& Event);
};

namespace DestructionIsolation
{
    bool Start(UWorld* World, const FString& Mode);
    void ConfigureProp(UGeometryCollectionComponent* Component);
    // PostUpdateWork: preapply profiles, then replay vendor break callbacks.
    void Flush();
    // Call BEFORE replacing props. Flushes/restores bridges and clears counters.
    void Reset();
    void Stop();
    TSharedRef<FJsonObject> Snapshot();
}
