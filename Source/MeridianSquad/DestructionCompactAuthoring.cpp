#include "NGDColumnAuthoring.h"
#include "DemoColumnCladding.h"

#if WITH_EDITOR
#include "AssetRegistry/AssetRegistryModule.h"
#include "Engine/StaticMesh.h"
#include "MeshDescription.h"
#include "StaticMeshAttributes.h"
#include "StaticMeshOperations.h"
#include "Misc/PackageName.h"
#include "UObject/Package.h"
#include "Serialization/JsonSerializer.h"
#endif

FString UNGDColumnAuthoring::BuildCompactLobbyFacing(const FString& Destination)
{
#if WITH_EDITOR
    if (!Destination.StartsWith(TEXT("/Game/OpeningLobby/DestructionScaling01/")))
        return TEXT("{\"error\":\"Destination must be in the task candidate directory\"}");
    const FString DataPath=Destination/TEXT("DA_CompactFacing");
    if (FPackageName::DoesPackageExist(DataPath)) return TEXT("{\"error\":\"Candidate already exists\"}");
    auto* Source=LoadObject<UDemoColumnCladdingData>(nullptr,
        TEXT("/Game/OpeningLobby/LobbyColumns01/DA_Cladding01.DA_Cladding01"));
    if (!Source) return TEXT("{\"error\":\"Source missing\"}");
    TMap<int32,TArray<int32>> Groups;
    for (int32 I=0; I<Source->Tiles.Num(); ++I)
    {
        const auto& Tile=Source->Tiles[I];
        if (!Tile.Mesh || !Tile.Mesh->GetMeshDescription(0)) return TEXT("{\"error\":\"Source mesh description missing\"}");
        const FVector N=Tile.RestTransform.GetUnitAxis(EAxis::X);
        const int32 Face=FMath::Abs(N.X)>FMath::Abs(N.Y) ? (N.X>0 ? 0:1) : (N.Y>0 ? 2:3);
        Groups.FindOrAdd(FMath::FloorToInt(Tile.RestTransform.GetLocation().Z/100.)*4+Face).Add(I);
    }
    auto* Data=NewObject<UDemoColumnCompactData>(CreatePackage(*DataPath),TEXT("DA_CompactFacing"),RF_Public|RF_Standalone);
    Data->Source=Source;
    TArray<int32> Keys; Groups.GetKeys(Keys); Keys.Sort();
    int64 SourceTriangles=0, ResultTriangles=0;
    for (const int32 Key : Keys)
    {
        FMeshDescription Merged;
        FStaticMeshAttributes Attributes(Merged); Attributes.Register();
        TArray<UMaterialInterface*> Materials;
        TMap<UMaterialInterface*,FPolygonGroupID> MaterialGroups;
        for (const int32 TileIndex : Groups[Key])
        {
            const auto& Tile=Source->Tiles[TileIndex];
            const FMeshDescription* Mesh=Tile.Mesh->GetMeshDescription(0);
            SourceTriangles+=Mesh->Triangles().Num();
            FStaticMeshOperations::FAppendSettings Settings;
            for (bool& UV : Settings.bMergeUVChannels) UV=true;
            Settings.MeshTransform=Tile.RestTransform;
            Settings.PolygonGroupsDelegate.BindLambda([&](const FMeshDescription& Input,FMeshDescription& Output,PolygonGroupMap& Remap)
            {
                FStaticMeshConstAttributes InputAttributes(Input);
                for (const FPolygonGroupID Group : Input.PolygonGroups().GetElementIDs())
                {
                    const FName Slot=InputAttributes.GetPolygonGroupMaterialSlotNames()[Group];
                    int32 MaterialIndex=Tile.Mesh->GetMaterialIndex(Slot);
                    if (MaterialIndex==INDEX_NONE) MaterialIndex=Group.GetValue();
                    UMaterialInterface* Material=Tile.Mesh->GetMaterial(MaterialIndex);
                    FPolygonGroupID Target;
                    if (const auto* Existing=MaterialGroups.Find(Material)) Target=*Existing;
                    else
                    {
                        Target=Output.CreatePolygonGroup();
                        const int32 Index=Materials.Add(Material);
                        Attributes.GetPolygonGroupMaterialSlotNames()[Target]=FName(*FString::Printf(TEXT("Material%d"),Index));
                        MaterialGroups.Add(Material,Target);
                    }
                    Remap.Add(Group,Target);
                }
            });
            FStaticMeshOperations::AppendMeshDescription(*Mesh,Merged,Settings);
        }
        ResultTriangles+=Merged.Triangles().Num();
        const FString Name=FString::Printf(TEXT("SM_FacingSection_%03d"),Data->Sections.Num());
        auto* Mesh=NewObject<UStaticMesh>(CreatePackage(*(Destination/Name)),*Name,RF_Public|RF_Standalone);
        for (int32 I=0; I<Materials.Num(); ++I)
            Mesh->GetStaticMaterials().Add(FStaticMaterial(Materials[I],FName(*FString::Printf(TEXT("Material%d"),I)),
                FName(*FString::Printf(TEXT("Material%d"),I))));
        Mesh->AddSourceModel();
        auto& Build=Mesh->GetSourceModel(0).BuildSettings;
        Build.bRecomputeNormals=false; Build.bRecomputeTangents=false;
        Build.bGenerateLightmapUVs=false; Build.bUseFullPrecisionUVs=true;
        Mesh->GetNaniteSettings().bEnabled=true;
        Mesh->GetNaniteSettings().FallbackTarget=ENaniteFallbackTarget::PercentTriangles;
        Mesh->GetNaniteSettings().FallbackPercentTriangles=1.f;
        Mesh->GetNaniteSettings().FallbackRelativeError=0.f;
        UStaticMesh::FBuildMeshDescriptionsParams Params;
        Params.bBuildSimpleCollision=false; Params.bFastBuild=false; Params.bCommitMeshDescription=true;
        Mesh->BuildFromMeshDescriptions({&Merged},Params);
        FAssetRegistryModule::AssetCreated(Mesh); Mesh->MarkPackageDirty();
        auto& Section=Data->Sections.AddDefaulted_GetRef();
        Section.Mesh=Mesh; Section.Tiles=Groups[Key];
    }
    FAssetRegistryModule::AssetCreated(Data); Data->MarkPackageDirty();
    return FString::Printf(TEXT("{\"tiles\":%d,\"sections\":%d,\"source_triangles\":%lld,\"result_triangles\":%lld,\"data\":\"%s\"}"),
        Source->Tiles.Num(),Data->Sections.Num(),SourceTriangles,ResultTriangles,*Data->GetPathName());
#else
    return TEXT("{\"error\":\"Editor only\"}");
#endif
}
