#pragma once

#include "CoreMinimal.h"

// Identity is independent of actors, physics handles and swap-removed render indices.
struct FDestructionFragmentId
{
    uint64 Owner = 0;
    uint32 Generation = 0;
    int32 Local = INDEX_NONE;
    bool operator==(const FDestructionFragmentId& Other) const
    { return Owner == Other.Owner && Generation == Other.Generation && Local == Other.Local; }
    friend uint32 GetTypeHash(const FDestructionFragmentId& Id)
    { return HashCombineFast(HashCombineFast(GetTypeHash(Id.Owner), Id.Generation), GetTypeHash(Id.Local)); }
    bool IsValid() const { return Owner != 0 && Local != INDEX_NONE; }
};

enum class EDestructionFragmentState : uint8 { Attached, Awake, Asleep, Held };
enum class EDestructionFragmentResult : uint8 { Applied, Stale, Unsupported, Unavailable };

struct FDestructionCommandGuard
{
    TAtomic<bool> Valid{true};
    TAtomic<uint64> Revision{1};
    TAtomic<uint64> LastAppliedRevision{0};
};

struct FDestructionLeafCommand
{
    int32 Bone = INDEX_NONE;
    uint8 Operation = 0;
    FVector Velocity = FVector::ZeroVector;
    FVector AngularVelocity = FVector::ZeroVector;
    FTransform Pose;
    TSharedPtr<FDestructionCommandGuard, ESPMode::ThreadSafe> Guard;
    uint64 Revision = 0;
};

struct FDestructionFragmentStamp
{
    FDestructionFragmentId Id;
    uint64 StateRevision = 0;
    uint64 PoseRevision = 0;
    bool operator==(const FDestructionFragmentStamp& Other) const
    { return Id == Other.Id && StateRevision == Other.StateRevision && PoseRevision == Other.PoseRevision; }
};

// All worker input owns its data. No UObjects, component array views or Chaos pointers.
struct FDestructionPoseInput
{
    FDestructionFragmentStamp Stamp;
    FTransform Relative, Carrier, Component, Previous;
    float DeltaTime = 0.f;
};
struct FDestructionPoseOutput
{
    FDestructionFragmentStamp Stamp;
    FTransform Local, World;
    FVector Velocity;
};

struct FDestructionHullInput
{
    FDestructionFragmentStamp Stamp;
    FTransform Pose;
    TSharedPtr<const TArray<FVector>, ESPMode::ThreadSafe> Hull;
};
struct FDestructionHullOutput
{
    FDestructionFragmentStamp Stamp;
    FVector Bottom;
};

namespace DestructionFragmentMath
{
    inline FDestructionPoseOutput Pose(const FDestructionPoseInput& In)
    {
        FDestructionPoseOutput Out;
        Out.Stamp = In.Stamp;
        Out.Local = In.Relative * In.Carrier;
        Out.World = Out.Local * In.Component;
        Out.Velocity = ((Out.World.GetLocation() - In.Previous.GetLocation()) /
            FMath::Max(In.DeltaTime, .001f)).GetClampedToMaxSize(1500.f);
        return Out;
    }
    inline FVector LowestPoint(const TArray<FVector>& Hull, const FTransform& Pose)
    {
        FVector Bottom(0., 0., DBL_MAX);
        for (const FVector& Vertex : Hull)
        {
            const FVector Point = Pose.TransformPosition(Vertex);
            if (Point.Z < Bottom.Z) Bottom = Point;
        }
        return Bottom;
    }
}
