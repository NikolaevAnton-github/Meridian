#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "PhysicsControlRecoveryLibrary.generated.h"

class UPhysicsAsset;
class USkeletalMeshComponent;

struct FDummySoleVertex
{
    uint32 Index;
    FName Bone;
    FVector World;
    FVector Local;
};

/** Bounded editor audit/derivation and geometry shared by placement diagnostics. */
UCLASS()
class MERIDIANSQUAD_API UPhysicsControlRecoveryLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="Physics Dummy|Verification")
    static FString AuditAsset(UPhysicsAsset* Asset);
    UFUNCTION(BlueprintCallable, Category="Physics Dummy|Verification")
    static FString AuditSkin(USkeletalMeshComponent* Mesh);
    UFUNCTION(BlueprintCallable, Category="Physics Dummy|Verification")
    static bool ConfigureAsset(UPhysicsAsset* Asset);
    /** Task-scoped sole boxes measured from the adopted mesh in a neutral pose. */
    UFUNCTION(BlueprintCallable, Category="Physics Dummy|Verification")
    static bool ConfigureGASPAsset(UPhysicsAsset* Asset, USkeletalMeshComponent* Mesh);
    static TArray<FDummySoleVertex> FootVertices(USkeletalMeshComponent* Mesh);
};
