#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "NGDColumnAuthoring.generated.h"

class UGeometryCollection;
class UStaticMesh;
class UNiagaraSystem;

/** Editor-only import of the bounded MSQ-154 column source; no runtime damage system. */
UCLASS()
class MERIDIANSQUAD_API UNGDColumnAuthoring : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="Destruction|Authoring")
    static FString BuildColumn(const FString& SourceFile);
    UFUNCTION(BlueprintCallable, Category="Destruction|Experiments")
    static FString AddDemoColumnTiles(UGeometryCollection* Collection, const FString& SourceFile);
    UFUNCTION(BlueprintCallable, Category="Destruction|Experiments")
    static FString BuildDemoColumnCladding(const FString& SourceFile);
    UFUNCTION(BlueprintCallable, Category="Destruction|Experiments")
    static FString BakeDemoColumnScale();
    UFUNCTION(BlueprintCallable, Category="Destruction|Authoring")
    static FString InspectCollection(UGeometryCollection* Collection);
    UFUNCTION(BlueprintCallable, Category="Destruction|Authoring")
    static FString InspectMesh(UStaticMesh* Mesh);
    UFUNCTION(BlueprintCallable, Category="Destruction|Authoring")
    static FString ConfigureConcreteCrumbs(UNiagaraSystem* System);
    UFUNCTION(BlueprintCallable, Category="Destruction|Authoring")
    static FString ExportColumnCollision(UGeometryCollection* Collection);
    UFUNCTION(BlueprintCallable, Category="Destruction|Authoring")
    static FString ApplyMergedCollision(UGeometryCollection* Collection, const FString& CollisionSource, const FString& MergeDesign);
};
