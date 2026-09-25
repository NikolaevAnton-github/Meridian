#include "NGDColumnAuthoring.h"
#include "GeometryCollection/GeometryCollectionObject.h"
#include "GeometryCollection/GeometryCollection.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

#if WITH_EDITOR
#include "AssetRegistry/AssetRegistryModule.h"
#include "Engine/StaticMesh.h"
#include "GeometryCollection/GeometryCollectionEngineConversion.h"
#include "GeometryCollection/GeometryCollectionClusteringUtility.h"
#include "GeometryCollection/GeometryCollectionConvexUtility.h"
#include "GeometryCollection/Facades/CollectionAnchoringFacade.h"
#include "GeometryCollection/GeometryCollectionProximityUtility.h"
#include "Materials/MaterialInterface.h"
#include "MeshDescription.h"
#include "StaticMeshAttributes.h"
#include "PhysicsEngine/BodySetup.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "UObject/Package.h"
#endif

namespace
{
FString ToJson(const TSharedRef<FJsonObject>& Value)
{
    FString Result;
    FJsonSerializer::Serialize(Value, TJsonWriterFactory<>::Create(&Result));
    return Result;
}

#if WITH_EDITOR
// Source triangles carry material ids. UVs use centimetres and a 100 cm repeat;
// the retained slab material uses its original world-space origin and extents.
FMeshDescription ReadMesh(const TSharedPtr<FJsonObject>& Source)
{
    FMeshDescription Mesh;
    FStaticMeshAttributes A(Mesh);
    A.Register();
    A.GetVertexInstanceUVs().SetNumChannels(1);
    TArray<FPolygonGroupID> Groups;
    for (int32 I = 0; I < 4; ++I)
    {
        const FPolygonGroupID G = Mesh.CreatePolygonGroup();
        A.GetPolygonGroupMaterialSlotNames()[G] = FName(*FString::Printf(TEXT("Slot%d"), I));
        Groups.Add(G);
    }
    TArray<FVector3f> Points;
    TArray<FVertexID> Vertices;
    for (const auto& V : Source->GetArrayField(TEXT("vertices")))
    {
        const auto& P = V->AsArray();
        const FVector3f Point(P[0]->AsNumber(), P[1]->AsNumber(), P[2]->AsNumber());
        const FVertexID Id = Mesh.CreateVertex();
        A.GetVertexPositions()[Id] = Point;
        Points.Add(Point);
        Vertices.Add(Id);
    }
    for (const auto& V : Source->GetArrayField(TEXT("triangles")))
    {
        const auto& T = V->AsArray();
        int32 Ids[3] = {int32(T[0]->AsNumber()), int32(T[1]->AsNumber()), int32(T[2]->AsNumber())};
        const FVector3f N = FVector3f::CrossProduct(Points[Ids[1]] - Points[Ids[0]], Points[Ids[2]] - Points[Ids[0]]).GetSafeNormal();
        const FVector3f Tangent = FVector3f::CrossProduct(FMath::Abs(N.Z) > .9f ? FVector3f(0, 1, 0) : FVector3f(0, 0, 1), N).GetSafeNormal();
        TArray<FVertexInstanceID> Corners;
        for (int32 Id : Ids)
        {
            const FVertexInstanceID VI = Mesh.CreateVertexInstance(Vertices[Id]);
            A.GetVertexInstanceNormals()[VI] = N;
            A.GetVertexInstanceTangents()[VI] = Tangent;
            A.GetVertexInstanceBinormalSigns()[VI] = 1;
            A.GetVertexInstanceColors()[VI] = FVector4f(1, 1, 1, 1);
            const FVector3f P = Points[Id];
            const FVector2f UV = FMath::Abs(N.Z) > .7f ? FVector2f(P.X, P.Y) :
                (FMath::Abs(N.X) > FMath::Abs(N.Y) ? FVector2f(P.Y, P.Z) : FVector2f(P.X, P.Z));
            A.GetVertexInstanceUVs().Set(VI, 0, UV / 100.f);
            Corners.Add(VI);
        }
        // Editable source uses outward right-handed winding; UE mesh faces are clockwise.
        Swap(Corners[1], Corners[2]);
        Mesh.CreatePolygon(Groups[int32(T[3]->AsNumber())], Corners);
    }
    return Mesh;
}

UStaticMesh* MakeStatic(const TCHAR* Name, FMeshDescription& Mesh, const TArray<UMaterialInterface*>& Materials)
{
    const FString PackageName = FString(TEXT("/Game/ReinforcedColumn01/")) + Name;
    UPackage* Package = CreatePackage(*PackageName);
    // Re-authoring is explicit and task-scoped; never replaces a vendor/source mesh.
    UStaticMesh* Asset = FindObject<UStaticMesh>(Package, Name);
    const bool bNew = !Asset;
    if (!Asset) Asset = NewObject<UStaticMesh>(Package, Name, RF_Public | RF_Standalone);
    Asset->Modify();
    Asset->GetStaticMaterials().Reset();
    for (int32 I = 0; I < Materials.Num(); ++I)
    {
        const FName Slot(*FString::Printf(TEXT("Slot%d"), I));
        Asset->GetStaticMaterials().Add(FStaticMaterial(Materials[I], Slot, Slot));
    }
    UStaticMesh::FBuildMeshDescriptionsParams Params;
    Params.bBuildSimpleCollision = false;
    Params.bFastBuild = false;
    Params.bCommitMeshDescription = true;
    Asset->BuildFromMeshDescriptions({&Mesh}, Params);
    Asset->CreateBodySetup();
    Asset->GetBodySetup()->CollisionTraceFlag = CTF_UseComplexAsSimple;
    Asset->GetBodySetup()->InvalidatePhysicsData();
    Asset->GetBodySetup()->CreatePhysicsMeshes();
    if (bNew) FAssetRegistryModule::AssetCreated(Asset);
    Asset->MarkPackageDirty();
    return Asset;
}
#endif
}

FString UNGDColumnAuthoring::InspectCollection(UGeometryCollection* Collection)
{
    TSharedRef<FJsonObject> Out = MakeShared<FJsonObject>();
    if (!Collection || !Collection->GetGeometryCollection()) return TEXT("{}");
    const auto& C = *Collection->GetGeometryCollection();
    Out->SetNumberField(TEXT("transforms"), C.Transform.Num());
    Out->SetNumberField(TEXT("geometries"), C.BoundingBox.Num());
    Out->SetNumberField(TEXT("vertices"), C.Vertex.Num());
    Out->SetNumberField(TEXT("faces"), C.Indices.Num());
    TMap<int32, int32> States;
    for (int32 State : C.InitialDynamicState) ++States.FindOrAdd(State);
    TSharedRef<FJsonObject> StateCounts = MakeShared<FJsonObject>();
    for (const auto& S : States) StateCounts->SetNumberField(FString::FromInt(S.Key), S.Value);
    Out->SetObjectField(TEXT("initial_states"), StateCounts);
#if WITH_EDITOR
    // Read the vendor and candidate managed attributes without changing either.
    Chaos::Facades::FCollectionAnchoringFacade Anchoring(C);
    TArray<TSharedPtr<FJsonValue>> Hierarchy;
    TMap<int32, int32> Levels;
    int32 AnchoredCount = 0;
    for (int32 I = 0; I < C.Transform.Num(); ++I)
    {
        int32 Level = 0, Parent = C.Parent[I];
        while (Parent != INDEX_NONE && Level < C.Transform.Num())
        {
            ++Level;
            Parent = C.Parent[Parent];
        }
        ++Levels.FindOrAdd(Level);
        const bool bAnchored = Anchoring.HasAnchoredAttribute() && Anchoring.IsAnchored(I);
        AnchoredCount += bAnchored ? 1 : 0;
        TSharedRef<FJsonObject> Row = MakeShared<FJsonObject>();
        Row->SetNumberField(TEXT("index"), I);
        Row->SetNumberField(TEXT("parent"), C.Parent[I]);
        Row->SetNumberField(TEXT("level"), Level);
        Row->SetNumberField(TEXT("children"), C.Children[I].Num());
        Row->SetNumberField(TEXT("geometry"), C.TransformToGeometryIndex[I]);
        Row->SetNumberField(TEXT("initial_state"), C.InitialDynamicState[I]);
        Row->SetBoolField(TEXT("anchored"), bAnchored);
        Row->SetStringField(TEXT("name"), C.BoneName[I]);
        Hierarchy.Add(MakeShared<FJsonValueObject>(Row));
    }
    TSharedRef<FJsonObject> LevelCounts = MakeShared<FJsonObject>();
    for (const auto& L : Levels) LevelCounts->SetNumberField(FString::FromInt(L.Key), L.Value);
    Out->SetObjectField(TEXT("level_counts"), LevelCounts);
    Out->SetBoolField(TEXT("has_anchored_attribute"), Anchoring.HasAnchoredAttribute());
    Out->SetNumberField(TEXT("anchored_count"), AnchoredCount);
    Out->SetArrayField(TEXT("hierarchy"), Hierarchy);
#endif
    return ToJson(Out);
}

FString UNGDColumnAuthoring::BuildColumn(const FString& SourceFile)
{
#if WITH_EDITOR
    FString Full = FPaths::ConvertRelativePathToFull(SourceFile);
    FPaths::NormalizeFilename(Full);
    FString Allowed = FPaths::ConvertRelativePathToFull(FPaths::ProjectDir() / TEXT("Assets/Source/ReinforcedColumn01/"));
    FPaths::NormalizeFilename(Allowed);
    FPaths::CollapseRelativeDirectories(Full);
    if (!Full.StartsWith(Allowed)) return TEXT("{\"error\":\"Source outside task directory\"}");
    FString Raw;
    TSharedPtr<FJsonObject> Source;
    if (!FFileHelper::LoadFileToString(Raw, *Full) || !FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Raw), Source))
        return TEXT("{\"error\":\"Invalid source JSON\"}");
    TArray<UMaterialInterface*> Materials;
    for (const auto& M : Source->GetArrayField(TEXT("materials")))
    {
        auto* Material = LoadObject<UMaterialInterface>(nullptr, *M->AsString());
        if (!Material) return TEXT("{\"error\":\"Missing material\"}");
        Materials.Add(Material);
    }
    if (Materials.Num() != 4) return TEXT("{\"error\":\"Four source materials required\"}");
    FMeshDescription Core = ReadMesh(Source->GetObjectField(TEXT("core")));
    FMeshDescription Steel = ReadMesh(Source->GetObjectField(TEXT("steel")));
    MakeStatic(TEXT("SM_RC01_SupportedColumn"), Core, Materials);
    MakeStatic(TEXT("SM_RC01_Rebar"), Steel, Materials);

    UPackage* Package = CreatePackage(TEXT("/Game/ReinforcedColumn01/GC_RC01_BondedConcrete"));
    UGeometryCollection* Asset = FindObject<UGeometryCollection>(Package, TEXT("GC_RC01_BondedConcrete"));
    const bool bNew = !Asset;
    if (!Asset) Asset = NewObject<UGeometryCollection>(Package, TEXT("GC_RC01_BondedConcrete"), RF_Public | RF_Standalone);
    Asset->Modify();
    Asset->Reset();
    Asset->Materials.Reset();
    for (auto* M : Materials) Asset->Materials.Add(M);
    const auto C = Asset->GetGeometryCollection();
    int32 Number = 0;
    for (const auto& Chunk : Source->GetArrayField(TEXT("pieces")))
    {
        FMeshDescription Mesh = ReadMesh(Chunk->AsObject());
        FGeometryCollectionEngineConversion::AppendMeshDescription(&Mesh, FString::Printf(TEXT("Bonded_%03d"), Number++), 0,
            FTransform::Identity, C.Get(), nullptr, false, false, false);
    }
    const int32 DynamicCount = Number;
    for (const auto& Anchor : Source->GetArrayField(TEXT("anchors")))
    {
        FMeshDescription Mesh = ReadMesh(Anchor->AsObject());
        FGeometryCollectionEngineConversion::AppendMeshDescription(&Mesh, FString::Printf(TEXT("FixedBond_%03d"), Number++), 0,
            FTransform::Identity, C.Get(), nullptr, false, false, false);
    }
    // Anchors are embedded in the separately retained core. Keep their faces
    // present in the physical collection; invisible geometry can be pruned.
    C->ReindexMaterials();
    FGeometryCollectionClusteringUtility::ClusterAllBonesUnderNewRoot(C.Get());
    FGeometryCollectionClusteringUtility::UpdateHierarchyLevelOfChildren(C.Get(), -1);
    for (int32 I = 0; I < Number; ++I)
        C->InitialDynamicState[I] = int32(I < DynamicCount ? Chaos::EObjectStateType::Dynamic : Chaos::EObjectStateType::Kinematic);
    C->InitialDynamicState[Number] = int32(Chaos::EObjectStateType::Kinematic);
    Chaos::Facades::FCollectionAnchoringFacade Anchoring(*C);
    Anchoring.AddAnchoredAttribute();
    for (int32 I = 0; I <= Number; ++I)
        Anchoring.SetAnchored(I, I >= DynamicCount && I < Number);
    FGeometryCollectionConvexUtility::CreateNonOverlappingConvexHullData(C.Get());
    FGeometryCollectionProximityUtility(C.Get()).UpdateProximity();
    Asset->EnableClustering = true;
    Asset->DamageThreshold = {500000.f, 50000.f, 5000.f};
    Asset->bMassAsDensity = true;
    Asset->Mass = 2400.f;
    Asset->MinimumMassClamp = .1f;
    Asset->bRemoveOnMaxSleep = true;
    Asset->MaximumSleepTime = FVector2D(3., 5.);
    Asset->RemovalDuration = FVector2D(1., 2.);
    Asset->SizeSpecificData.SetNum(1);
    Asset->SizeSpecificData[0].CollisionShapes.SetNum(1);
    auto& Shape = Asset->SizeSpecificData[0].CollisionShapes[0];
    Shape.CollisionType = ECollisionTypeEnum::Chaos_Surface_Volumetric;
    Shape.ImplicitType = EImplicitTypeEnum::Chaos_Implicit_Convex;
    Asset->InvalidateCollection();
    Asset->CreateSimulationData();
    Asset->RebuildRenderData();
    if (bNew) FAssetRegistryModule::AssetCreated(Asset);
    Asset->MarkPackageDirty();
    return InspectCollection(Asset);
#else
    return TEXT("{\"error\":\"Editor only\"}");
#endif
}
