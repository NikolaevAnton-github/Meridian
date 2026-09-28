#pragma once

#include "CoreMinimal.h"

class UGeometryCollectionComponent;
struct FHitResult;

// Call on the game thread immediately after applying local external strain.
MERIDIANSQUAD_API void ApplyDemoColumnScatter(UGeometryCollectionComponent* Concrete, const FHitResult& Hit, uint32 Seed);
