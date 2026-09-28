#pragma once

#include "CoreMinimal.h"
#include "DestructionFragmentState.h"

class UGeometryCollectionComponent;
struct FHitResult;

// Call on the game thread immediately after applying local external strain.
MERIDIANSQUAD_API void ApplyDemoColumnScatter(UGeometryCollectionComponent* Concrete, const FHitResult& Hit, uint32 Seed);

MERIDIANSQUAD_API void ReleaseDemoColumnLeaf(UGeometryCollectionComponent* Concrete, int32 Bone, const FHitResult& Hit, uint32 Seed);
MERIDIANSQUAD_API void FreezeDemoColumnLeaf(UGeometryCollectionComponent* Concrete, int32 Bone, TFunction<void(bool)> Completion);
MERIDIANSQUAD_API void KeepDemoColumnLeafAwake(UGeometryCollectionComponent* Concrete, int32 Bone);
MERIDIANSQUAD_API void ConfigureDemoColumnDebrisCollision(UGeometryCollectionComponent* Concrete, int32 Bone);
MERIDIANSQUAD_API bool CommandDemoColumnLeaf(UGeometryCollectionComponent* Concrete, int32 Bone,
    uint8 Operation, FVector Velocity, FVector AngularVelocity, FTransform Pose,
    TSharedPtr<FDestructionCommandGuard, ESPMode::ThreadSafe> Guard, uint64 Revision);
MERIDIANSQUAD_API bool CommandDemoColumnLeaves(UGeometryCollectionComponent* Concrete, TArray<FDestructionLeafCommand> Commands);
