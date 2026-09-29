#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DestructionPerfFixture.generated.h"

class UStaticMeshComponent;
class UTextRenderComponent;

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
    };
    UPROPERTY() TObjectPtr<UStaticMeshComponent> Marker;
    UPROPERTY() TObjectPtr<UTextRenderComponent> Label;
    TArray<FSample> History;
    TArray<FSample> Capture;
    int32 HistoryHead = 0;
    int32 HistoryCount = 0;
    int32 AutoRemaining = 1;
    int32 AutoIndex = 0;
    double ResetAt = 0;
    double LastTick = 0, ArmedAt = 0, DetonatedAt = 0, AutoAt = 0, QuitAt = 0;
    bool bSpent = false;
    FString AutoName, LastOutput;
    TSharedPtr<FJsonObject> Metadata;
    void SaveCapture(const FString& Outcome);
};
