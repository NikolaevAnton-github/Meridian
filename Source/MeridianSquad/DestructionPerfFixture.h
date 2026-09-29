#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DestructionPerfFixture.generated.h"

class UStaticMeshComponent;
class UTextRenderComponent;
class UNGDPropComponent;

/** Lobby-only repeatable blast and bounded, real-time frame recorder. No asset edits. */
UCLASS()
class MERIDIANSQUAD_API ADestructionPerfFixture : public AActor
{
    GENERATED_BODY()
public:
    ADestructionPerfFixture();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    void Arm();
    void ResetFixture();
    void MarkDetonation();
    UFUNCTION(BlueprintPure, Category="Destruction|Performance") FString GetState() const;
private:
    struct FSample
    {
        double Time = 0, Frame = 0, Game = 0, Render = 0, RHI = 0, GPU = 0;
        double Simulation = 0;
        uint64 EngineFrame = 0;
        int32 BreakEvents = 0;
        bool bDiagnosticSample = false;
        int32 ActiveTransforms = -1, SleepingTransforms = -1, DynamicTransforms = -1, NiagaraComponents = -1;
        uint64 PhysicalBytes = 0, VirtualBytes = 0, PeakPhysicalBytes = 0;
        int32 ObservedActivations = -1, AudioSources = -1;
    };
    struct FAudioObservation { TAtomic<int32> Sources{-1}; };
    UPROPERTY() TObjectPtr<UStaticMeshComponent> Marker;
    UPROPERTY() TObjectPtr<UTextRenderComponent> Label;
    TArray<FSample> History;
    TArray<FSample> Capture;
    TArray<TWeakObjectPtr<UNGDPropComponent>> Props;
    FSample Diagnostics;
    TMap<FString, TBitArray<>> PreviousActive;
    TMap<FString, int32> ObservedActivations;
    TSharedPtr<FAudioObservation, ESPMode::ThreadSafe> AudioObservation;
    int32 HistoryHead = 0;
    int32 HistoryCount = 0;
    int32 AutoRemaining = 1;
    int32 AutoIndex = 0;
    double ResetAt = 0;
    double LastTick = 0, ArmedAt = 0, DetonatedAt = 0, AutoAt = 0, QuitAt = 0;
    bool bSpent = false;
    bool bDiagnostics = false;
    bool bRefreshProps = false;
    double NextDiagnosticAt = 0, ArmedSimulation = 0, DetonatedSimulation = 0;
    int32 Phase = -1;
    FString AutoName, LastOutput;
    TSharedPtr<FJsonObject> Metadata;
    void SaveCapture(const FString& Outcome);
    void RefreshProps();
    void SetPhase(int32 NewPhase);
    void SampleDiagnostics();
};
