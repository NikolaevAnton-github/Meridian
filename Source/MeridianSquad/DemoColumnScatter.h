#pragma once

#include "CoreMinimal.h"

class UGeometryCollectionComponent;
struct FHitResult;

// Call on the game thread immediately after applying local external strain.
MERIDIANSQUAD_API void ApplyDemoColumnScatter(UGeometryCollectionComponent* Concrete, const FHitResult& Hit, uint32 Seed);

MERIDIANSQUAD_API void ReleaseDemoColumnLeaf(UGeometryCollectionComponent* Concrete, int32 Bone, const FHitResult& Hit, uint32 Seed);
MERIDIANSQUAD_API void FreezeDemoColumnLeaf(UGeometryCollectionComponent* Concrete, int32 Bone, TFunction<void(bool)> Completion);
MERIDIANSQUAD_API void KeepDemoColumnLeafAwake(UGeometryCollectionComponent* Concrete, int32 Bone);
