#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "NGDColumnAuthoring.generated.h"

class UGeometryCollection;
class UStaticMesh;

/** Editor-only import of the bounded MSQ-154 column source; no runtime damage system. */
UCLASS()
class MERIDIANSQUAD_API UNGDColumnAuthoring : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="Destruction|Authoring")
    static FString BuildColumn(const FString& SourceFile);
    UFUNCTION(BlueprintCallable, Category="Destruction|Authoring")
    static FString InspectCollection(UGeometryCollection* Collection);
    UFUNCTION(BlueprintCallable, Category="Destruction|Authoring")
    static FString InspectMesh(UStaticMesh* Mesh);
};
