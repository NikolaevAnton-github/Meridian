#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PhysicsControlDummy.generated.h"

class UPhysicsControlComponent;
class USkeletalMeshComponent;
class UTextRenderComponent;
class UAnimSequence;
class FJsonValue;
class FJsonObject;

/** Primitive geometry from PA_Mannequin, transformed by the actual Chaos body. */
struct FDummyShape
{
    FName Bone;
    FTransform Transform;
    FVector Extent = FVector::ZeroVector;
    float Radius = 0;
    float HalfHeight = 0;
    bool bBox = false;
};

struct FDummyPose
{
    TArray<FDummyShape> Shapes;
    uint64 Epoch = 0;
};

/** A removable fixture with explicit world-space pose springs. No balance or AI. */
UCLASS()
class MERIDIANSQUAD_API APhysicsControlDummy : public AActor
{
    GENERATED_BODY()
public:
    APhysicsControlDummy();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Physics Dummy")
    TObjectPtr<USkeletalMeshComponent> Body;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Physics Dummy")
    TObjectPtr<UPhysicsControlComponent> PhysicsControl;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float MaxHealth = 100.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float LimbAngularStrength = 8.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float PoseLinearStrength = 4.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float TrunkAngularStrength = 8.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float SupportStrength = 20.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float DriveDampingRatio = 1.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float HitRecoverySeconds = .3f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float BulletImpulse = 900.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Physics Dummy|Tuning")
    float MaxImpulseVelocity = 180.f;
    UPROPERTY(BlueprintReadOnly, Category="Physics Dummy")
    float Health = 100.f;
    UPROPERTY(BlueprintReadOnly, Category="Physics Dummy")
    int32 Deaths = 0;
    UPROPERTY(BlueprintReadOnly, Category="Physics Dummy")
    int32 PhysicalHits = 0;

    UFUNCTION(BlueprintCallable, Category="Physics Dummy")
    void ResetDummy();
    UFUNCTION(BlueprintPure, Category="Physics Dummy|Verification")
    FString GetDummyState(bool IncludeContacts = true) const;
    UFUNCTION(BlueprintPure, Category="Physics Dummy|Verification")
    FVector GetPhysicalBodyLocation(FName Bone) const;

    FDummyPose SamplePhysicalPose() const;
    bool TracePhysicalPose(const FDummyPose& Before, const FDummyPose& After,
        const FVector& Start, const FVector& End, float Radius, FHitResult& Hit) const;
    float ReceiveBullet(int64 ShotId, float Damage, const FVector& Direction, const FHitResult& Hit,
        double ContactTime, double BirthTime, uint64 CombatFrame);
    bool IsDead() const { return Deaths != 0; }
    bool IsReady() const { return bReady; }
    uint64 DeathFrame = 0;
    double DeathTime = -1;

private:
    UPROPERTY() TObjectPtr<USceneComponent> FixtureRoot;
    UPROPERTY() TObjectPtr<UTextRenderComponent> Label;
    UPROPERTY() TObjectPtr<UAnimSequence> Idle;
    FTransform Home;
    FTransform SupportTarget;
    TMap<FName, FTransform> ReferencePose;
    TArray<FName> Controls;
    TMap<FName, FName> BodyControls;
    TMap<FName, float> RecoveringControls;
    uint64 PoseEpoch = 0;
    bool bReady = false;
    int32 UnsupportedShapes = 0;
    int32 WidenedJoints = 0;
    TArray<TSharedPtr<FJsonValue>> Contacts;
    void UpdateLabel();
    TSharedPtr<FJsonObject> BodyState() const;
};
