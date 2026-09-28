#include "NGDColumnAuthoring.h"
#include "DemoColumnCladding.h"
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
#include "GeometryCollection/GeometryCollectionAlgo.h"
#include "Chaos/Convex.h"
#include "Chaos/ImplicitObject.h"
#include "GeometryCollection/Facades/CollectionAnchoringFacade.h"
#include "GeometryCollection/Facades/CollectionConnectionGraphFacade.h"
#include "GeometryCollection/GeometryCollectionProximityUtility.h"
#include "Materials/MaterialInterface.h"
#include "MeshDescription.h"
#include "StaticMeshAttributes.h"
#include "StaticMeshOperations.h"
#include "StaticMeshResources.h"
#include "Misc/PackageName.h"
#include "PhysicsEngine/BodySetup.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "NiagaraSystem.h"
#include "NiagaraEmitter.h"
#include "NiagaraEmitterHandle.h"
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
    const TArray<TSharedPtr<FJsonValue>>* SourceNormals = nullptr;
    const TArray<TSharedPtr<FJsonValue>>* SourceUVs = nullptr;
    Source->TryGetArrayField(TEXT("normals"), SourceNormals);
    Source->TryGetArrayField(TEXT("uvs"), SourceUVs);
    for (const auto& V : Source->GetArrayField(TEXT("triangles")))
    {
        const auto& T = V->AsArray();
        int32 Ids[3] = {int32(T[0]->AsNumber()), int32(T[1]->AsNumber()), int32(T[2]->AsNumber())};
        const FVector3f Edge1 = Points[Ids[1]] - Points[Ids[0]], Edge2 = Points[Ids[2]] - Points[Ids[0]];
        const FVector3f N = FVector3f::CrossProduct(Edge1, Edge2).GetSafeNormal(1.e-20f);
        FVector3f Tangent = FVector3f::CrossProduct(FMath::Abs(N.Z) > .9f ? FVector3f(0, 1, 0) : FVector3f(0, 0, 1), N).GetSafeNormal(1.e-20f);
        FVector3f Bitangent = FVector3f::CrossProduct(N, Tangent);
        if (SourceUVs)
        {
            const auto ReadUV = [&](int32 Id)
            {
                const auto& UV = (*SourceUVs)[Id]->AsArray();
                return FVector2f(UV[0]->AsNumber(), UV[1]->AsNumber());
            };
            const FVector2f UV1 = ReadUV(Ids[1]) - ReadUV(Ids[0]), UV2 = ReadUV(Ids[2]) - ReadUV(Ids[0]);
            const float Determinant = UV1.X * UV2.Y - UV1.Y * UV2.X;
            if (FMath::Abs(Determinant) > 1.e-14f)
            {
                Tangent = ((Edge1 * UV2.Y - Edge2 * UV1.Y) / Determinant).GetSafeNormal(1.e-20f);
                Bitangent = ((Edge2 * UV1.X - Edge1 * UV2.X) / Determinant).GetSafeNormal(1.e-20f);
            }
        }
        TArray<FVertexInstanceID> Corners;
        for (int32 Id : Ids)
        {
            const FVertexInstanceID VI = Mesh.CreateVertexInstance(Vertices[Id]);
            FVector3f VertexNormal = N;
            if (SourceNormals && SourceNormals->IsValidIndex(Id))
            {
                const auto& SN = (*SourceNormals)[Id]->AsArray();
                VertexNormal = FVector3f(SN[0]->AsNumber(), SN[1]->AsNumber(), SN[2]->AsNumber()).GetSafeNormal();
            }
            A.GetVertexInstanceNormals()[VI] = VertexNormal;
            FVector3f VertexTangent = (Tangent - VertexNormal * FVector3f::DotProduct(Tangent, VertexNormal)).GetSafeNormal(1.e-20f);
            if (VertexTangent.IsNearlyZero())
                VertexTangent = FVector3f::CrossProduct(FMath::Abs(VertexNormal.Z) > .9f ? FVector3f(0, 1, 0) : FVector3f(0, 0, 1), VertexNormal).GetSafeNormal();
            A.GetVertexInstanceTangents()[VI] = VertexTangent;
            A.GetVertexInstanceBinormalSigns()[VI] = FVector3f::DotProduct(FVector3f::CrossProduct(VertexNormal, VertexTangent), Bitangent) < 0.f ? -1.f : 1.f;
            A.GetVertexInstanceColors()[VI] = FVector4f(1, 1, 1, 1);
            const FVector3f P = Points[Id];
            const FVector2f UV = FMath::Abs(N.Z) > .7f ? FVector2f(P.X, P.Y) :
                (FMath::Abs(N.X) > FMath::Abs(N.Y) ? FVector2f(P.Y, P.Z) : FVector2f(P.X, P.Z));
            FVector2f VertexUV = UV / 100.f;
            if (SourceUVs && SourceUVs->IsValidIndex(Id))
            {
                const auto& SU = (*SourceUVs)[Id]->AsArray();
                VertexUV = FVector2f(SU[0]->AsNumber(), SU[1]->AsNumber());
            }
            A.GetVertexInstanceUVs().Set(VI, 0, VertexUV);
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
    // Existing preview meshes are not referenced by the lobby. Fully load their
    // packages before replacing source models, or a later load/save can restore
    // stale disk source over the newly authored object.
    if (!Asset && FPackageName::DoesPackageExist(PackageName))
        Asset = LoadObject<UStaticMesh>(nullptr, *(PackageName + TEXT(".") + Name));
    const bool bNew = !Asset;
    if (!Asset) Asset = NewObject<UStaticMesh>(Package, Name, RF_Public | RF_Standalone);
    Asset->Modify();
    Asset->GetStaticMaterials().Reset();
    for (int32 I = 0; I < Materials.Num(); ++I)
    {
        const FName Slot(*FString::Printf(TEXT("Slot%d"), I));
        Asset->GetStaticMaterials().Add(FStaticMaterial(Materials[I], Slot, Slot));
    }
    // Preserve the imported smooth fracture normals; recomputing across the
    // coincident interfaces of an intact preview can cancel opposing normals.
    Asset->SetNumSourceModels(1);
    // These dense fracture surfaces must use the same virtualized rendering
    // path as the vendor meshes, including the intact core and reinforcement.
    Asset->GetNaniteSettings().bEnabled = true;
    // Complex-as-simple collision is cooked from the fallback LOD. Preserve its
    // full source surface while Nanite independently reduces rendering cost.
    Asset->GetNaniteSettings().FallbackTarget = ENaniteFallbackTarget::PercentTriangles;
    Asset->GetNaniteSettings().FallbackPercentTriangles = 1.0f;
    Asset->GetNaniteSettings().FallbackRelativeError = 0.0f;
    auto& Settings = Asset->GetSourceModel(0).BuildSettings;
    Settings.bRecomputeNormals = false;
    Settings.bRecomputeTangents = false;
    Settings.bUseFullPrecisionUVs = true;
    Settings.bUseHighPrecisionTangentBasis = true;
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

FString UNGDColumnAuthoring::BuildDemoColumnTileFractures08()
{
#if WITH_EDITOR
    FString Raw;
    TSharedPtr<FJsonObject> Source;
    if (!FFileHelper::LoadFileToString(Raw,*(FPaths::ProjectSavedDir()/TEXT("DemoColumnExperiment08/ceramic.json"))) ||
        !FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Raw),Source)) return TEXT("{\"error\":\"Missing ceramic source\"}");
    auto* Data = LoadObject<UDemoColumnCladdingData>(nullptr,TEXT("/Game/Experiments/DemoTiledColumn01/Correction08/DA_Cladding08.DA_Cladding08"));
    if (!Data) return TEXT("{\"error\":\"Missing facing data\"}");
    int32 MeshCount = 0, TileCount = 0, GroupIndex = 0;
    for (const auto& GroupValue : Source->GetArrayField(TEXT("groups")))
    {
        const auto Group = GroupValue->AsObject();
        const FString Path = Group->GetStringField(TEXT("source"));
        auto* Original = LoadObject<UStaticMesh>(nullptr,*(Path+TEXT(".")+FPackageName::GetShortName(Path)));
        if (!Original) return TEXT("{\"error\":\"Missing original ceramic mesh\"}");
        TArray<FDemoColumnTileShard> Shards;
        for (const auto& PieceValue : Group->GetArrayField(TEXT("pieces")))
        {
            const auto Piece = PieceValue->AsObject();
            const auto Geometry = Piece->GetObjectField(TEXT("mesh"));
            const FString Name = FString::Printf(TEXT("SM_Shards08_%03d_%d"),GroupIndex,Shards.Num());
            const FString PackageName = TEXT("/Game/Experiments/DemoTiledColumn01/Correction08/Shards/")+Name;
            if (FPackageName::DoesPackageExist(PackageName)) return TEXT("{\"error\":\"Shard already exists\"}");
            auto* Mesh = NewObject<UStaticMesh>(CreatePackage(*PackageName),*Name,RF_Public|RF_Standalone);
            Mesh->GetStaticMaterials() = Original->GetStaticMaterials();
            Mesh->SetNumSourceModels(1);
            auto& Settings = Mesh->GetSourceModel(0).BuildSettings;
            Settings.bRecomputeNormals = Settings.bRecomputeTangents = false;
            Settings.bUseFullPrecisionUVs = true;
            FMeshDescription Description = ReadMesh(Geometry);
            UStaticMesh::FBuildMeshDescriptionsParams Params;
            Params.bBuildSimpleCollision = false; Params.bFastBuild = false; Params.bCommitMeshDescription = true;
            Mesh->BuildFromMeshDescriptions({&Description},Params);
            Mesh->CreateBodySetup();
            auto* Body = Mesh->GetBodySetup();
            Body->CollisionTraceFlag = CTF_UseSimpleAndComplex;
            FKConvexElem Convex;
            for (const auto& Value : Geometry->GetArrayField(TEXT("vertices")))
            {
                const auto& V = Value->AsArray();
                Convex.VertexData.Add(FVector(V[0]->AsNumber(),V[1]->AsNumber(),V[2]->AsNumber()));
            }
            Convex.UpdateElemBox(); Body->AggGeom.ConvexElems.Add(MoveTemp(Convex));
            Body->InvalidatePhysicsData(); Body->CreatePhysicsMeshes();
            FAssetRegistryModule::AssetCreated(Mesh); Mesh->MarkPackageDirty();
            FDemoColumnTileShard Shard;
            Shard.Mesh = Mesh; Shard.AreaCm2 = Geometry->GetNumberField(TEXT("area_cm2"));
            const auto& Offset = Piece->GetArrayField(TEXT("offset"));
            Shard.RelativeToTile = FTransform(FVector(Offset[0]->AsNumber(),Offset[1]->AsNumber(),Offset[2]->AsNumber()));
            Shards.Add(Shard); ++MeshCount;
        }
        for (auto& Tile : Data->Tiles)
            if (Tile.Mesh == Original) { Tile.Shards = Shards; ++TileCount; }
        ++GroupIndex;
    }
    Data->MarkPackageDirty();
    return FString::Printf(TEXT("{\"shard_meshes\":%d,\"fracturable_tiles\":%d}"),MeshCount,TileCount);
#else
    return TEXT("{\"error\":\"Editor required\"}");
#endif
}

FString UNGDColumnAuthoring::InspectMesh(UStaticMesh* Mesh)
{
#if WITH_EDITOR
    if (!Mesh || !Mesh->GetMeshDescription(0)) return TEXT("{}");
    TSharedRef<FJsonObject> Out = MakeShared<FJsonObject>();
    const FMeshDescription& Description = *Mesh->GetMeshDescription(0);
    FStaticMeshConstAttributes Attributes(Description);
    int32 InvalidNormals = 0, InvalidTangents = 0;
    for (const auto Id : Description.VertexInstances().GetElementIDs())
    {
        InvalidNormals += Attributes.GetVertexInstanceNormals()[Id].IsNearlyZero() ? 1 : 0;
        InvalidTangents += Attributes.GetVertexInstanceTangents()[Id].IsNearlyZero() ? 1 : 0;
    }
    Out->SetNumberField(TEXT("source_triangles"), Description.Triangles().Num());
    Out->SetNumberField(TEXT("source_vertices"), Description.Vertices().Num());
    Out->SetNumberField(TEXT("invalid_normals"), InvalidNormals);
    Out->SetNumberField(TEXT("invalid_tangents"), InvalidTangents);
    if (Mesh->GetRenderData() && Mesh->GetRenderData()->LODResources.Num())
        Out->SetNumberField(TEXT("render_triangles"), Mesh->GetRenderData()->LODResources[0].GetNumTriangles());
    return ToJson(Out);
#else
    return TEXT("{}");
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
    TArray<TSharedPtr<FJsonValue>> Geometry;
    for (int32 G = 0; G < C.BoundingBox.Num(); ++G)
    {
        TSharedRef<FJsonObject> Row = MakeShared<FJsonObject>();
        const int32 Transform = C.TransformIndex[G];
        Row->SetNumberField(TEXT("index"), G);
        Row->SetNumberField(TEXT("transform"), Transform);
        Row->SetNumberField(TEXT("faces"), C.FaceCount[G]);
        Row->SetStringField(TEXT("bounds"), C.BoundingBox[G].ToString());
        Row->SetStringField(TEXT("local_transform"), C.Transform[Transform].ToString());
        TMap<int32, double> Areas, UVAreas;
        int32 SmoothCorners = 0;
        double MinEdge = TNumericLimits<double>::Max(), MaxEdge = 0.;
        for (int32 F = C.FaceStart[G]; F < C.FaceStart[G] + C.FaceCount[G]; ++F)
        {
            const FIntVector T = C.Indices[F];
            const FVector3f Cross = FVector3f::CrossProduct(C.Vertex[T.Y] - C.Vertex[T.X], C.Vertex[T.Z] - C.Vertex[T.X]);
            const double Area = .5 * Cross.Length();
            Areas.FindOrAdd(C.MaterialID[F]) += Area;
            if (C.NumUVLayers() > 0)
            {
                const FVector2f A = C.GetUV(T.Y, 0) - C.GetUV(T.X, 0);
                const FVector2f B = C.GetUV(T.Z, 0) - C.GetUV(T.X, 0);
                UVAreas.FindOrAdd(C.MaterialID[F]) += .5 * FMath::Abs(A.X * B.Y - A.Y * B.X);
            }
            for (int32 K = 0; K < 3; ++K)
            {
                const double Edge = (C.Vertex[T[K]] - C.Vertex[T[(K + 1) % 3]]).Length();
                MinEdge = FMath::Min(MinEdge, Edge);
                MaxEdge = FMath::Max(MaxEdge, Edge);
                SmoothCorners += FMath::Abs(FVector3f::DotProduct(Cross.GetSafeNormal(), C.Normal[T[K]])) < .999f ? 1 : 0;
            }
        }
        TSharedRef<FJsonObject> Surface = MakeShared<FJsonObject>();
        for (const auto& Area : Areas)
        {
            TSharedRef<FJsonObject> Stats = MakeShared<FJsonObject>();
            Stats->SetNumberField(TEXT("area_cm2"), Area.Value);
            Stats->SetNumberField(TEXT("uv_area"), UVAreas.FindRef(Area.Key));
            Surface->SetObjectField(FString::FromInt(Area.Key), Stats);
        }
        Row->SetObjectField(TEXT("surface_by_material"), Surface);
        Row->SetNumberField(TEXT("min_edge_cm"), MinEdge);
        Row->SetNumberField(TEXT("max_edge_cm"), MaxEdge);
        Row->SetNumberField(TEXT("smooth_corners"), SmoothCorners);
        Geometry.Add(MakeShared<FJsonValueObject>(Row));
    }
    Out->SetArrayField(TEXT("geometry"), Geometry);
    const auto HullData = FGeometryCollectionConvexUtility::GetConvexHullDataIfPresent(Collection->GetGeometryCollection().Get());
    if (HullData.IsSet())
    {
        Out->SetNumberField(TEXT("convex_hulls"), HullData->ConvexHull.Num());
        int32 TotalVertices = 0, MaxVertices = 0;
        for (const auto& Hull : HullData->ConvexHull) if (Hull)
        {
            TotalVertices += Hull->NumVertices();
            MaxVertices = FMath::Max(MaxVertices, Hull->NumVertices());
        }
        Out->SetNumberField(TEXT("convex_vertices"), TotalVertices);
        Out->SetNumberField(TEXT("max_convex_vertices"), MaxVertices);
        TArray<TSharedPtr<FJsonValue>> Missing;
        for (int32 I = 0; I < C.Transform.Num(); ++I)
            if (C.TransformToGeometryIndex[I] != INDEX_NONE && C.Children[I].Num() == 0 && HullData->TransformToConvexIndices[I].Num() == 0)
                Missing.Add(MakeShared<FJsonValueNumber>(I));
        Out->SetArrayField(TEXT("leaves_without_convex"), Missing);
    }
#endif
    return ToJson(Out);
}

FString UNGDColumnAuthoring::ExportColumnCollision(UGeometryCollection* Collection)
{
#if WITH_EDITOR
    if (!Collection) return TEXT("{\"error\":\"Missing collection\"}");
    const auto C = Collection->GetGeometryCollection();
    const auto Hulls = FGeometryCollectionConvexUtility::GetConvexHullDataIfPresent(C.Get());
    if (!Hulls.IsSet()) return TEXT("{\"error\":\"Missing convex data\"}");
    TArray<FTransform> Global;
    GeometryCollectionAlgo::GlobalMatrices(C->Transform, C->Parent, Global);
    TArray<TSharedPtr<FJsonValue>> Leaves;
    for (int32 I = 0; I < C->Transform.Num(); ++I)
    {
        if (C->TransformToGeometryIndex[I] == INDEX_NONE || C->Children[I].Num()) continue;
        if (Hulls->TransformToConvexIndices[I].Num() != 1)
            return TEXT("{\"error\":\"Expected one convex per source leaf\"}");
        const auto& Hull = Hulls->ConvexHull[*Hulls->TransformToConvexIndices[I].CreateConstIterator()];
        TArray<TSharedPtr<FJsonValue>> Points;
        for (int32 V = 0; V < Hull->NumVertices(); ++V)
        {
            const FVector P = Global[I].TransformPosition(FVector(Hull->GetVertex(V)));
            Points.Add(MakeShared<FJsonValueArray>(TArray<TSharedPtr<FJsonValue>>{
                MakeShared<FJsonValueNumber>(P.X), MakeShared<FJsonValueNumber>(P.Y), MakeShared<FJsonValueNumber>(P.Z)}));
        }
        Leaves.Add(MakeShared<FJsonValueArray>(Points));
    }
    TSharedRef<FJsonObject> Out = MakeShared<FJsonObject>();
    Out->SetArrayField(TEXT("leaves"), Leaves);
    Out->SetStringField(TEXT("space"), TEXT("collection"));
    return ToJson(Out);
#else
    return TEXT("{\"error\":\"Editor only\"}");
#endif
}

FString UNGDColumnAuthoring::ApplyMergedCollision(UGeometryCollection* Collection, const FString& CollisionSource, const FString& MergeDesign)
{
#if WITH_EDITOR
    if (!Collection || Collection->GetPathName() != TEXT("/Game/ReinforcedColumn01/GC_RC01_BondedConcrete.GC_RC01_BondedConcrete"))
        return TEXT("{\"error\":\"Expected column collection\"}");
    auto ReadSource = [](const FString& Path, TSharedPtr<FJsonObject>& Out)
    {
        FString Full = FPaths::ConvertRelativePathToFull(Path);
        FPaths::NormalizeFilename(Full);
        FPaths::CollapseRelativeDirectories(Full);
        const FString Allowed = FPaths::ConvertRelativePathToFull(FPaths::ProjectDir() / TEXT("Assets/Source/ReinforcedColumn01/"));
        FString Raw;
        return Full.StartsWith(Allowed) && FFileHelper::LoadFileToString(Raw, *Full) && FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Raw), Out);
    };
    TSharedPtr<FJsonObject> Source, Design;
    if (!ReadSource(CollisionSource, Source) || !ReadSource(MergeDesign, Design))
        return TEXT("{\"error\":\"Invalid collision source or merge design\"}");
    const auto& Leaves = Source->GetArrayField(TEXT("leaves"));
    const auto& Groups = Design->GetArrayField(TEXT("merge_groups"));
    const int32 OriginalCount = int32(Design->GetNumberField(TEXT("original_dynamic_bodies")));
    const auto C = Collection->GetGeometryCollection();
    auto Hulls = FGeometryCollectionConvexUtility::GetConvexHullDataIfPresent(C.Get());
    const int32 LeafCount = Groups.Num() + Leaves.Num() - OriginalCount;
    if (!Hulls.IsSet() || OriginalCount != 644 || Groups.Num() != 480 || LeafCount != C->NumElements(FGeometryCollection::GeometryGroup))
        return TEXT("{\"error\":\"Collision/source topology mismatch\"}");
    TArray<FTransform> Global;
    GeometryCollectionAlgo::GlobalMatrices(C->Transform, C->Parent, Global);
    TArray<Chaos::FConvexPtr> NewHulls;
    for (int32 I = 0; I < LeafCount; ++I)
    {
        if (Hulls->TransformToConvexIndices[I].Num() != 1)
            return TEXT("{\"error\":\"Expected one convex per target leaf\"}");
        TArray<int32> OldIndices;
        if (I < Groups.Num())
            for (const auto& Index : Groups[I]->AsArray()) OldIndices.Add(int32(Index->AsNumber()));
        else OldIndices.Add(OriginalCount + I - Groups.Num());
        TArray<Chaos::FConvex::FVec3Type> Points;
        for (const int32 Old : OldIndices)
        {
            if (!Leaves.IsValidIndex(Old)) return TEXT("{\"error\":\"Invalid source leaf index\"}");
            for (const auto& Value : Leaves[Old]->AsArray())
            {
                const auto& P = Value->AsArray();
                const FVector Local = Global[I].InverseTransformPosition(FVector(P[0]->AsNumber(), P[1]->AsNumber(), P[2]->AsNumber()));
                Points.Add(Chaos::FConvex::FVec3Type(Local));
            }
        }
        // Reuse the known economical source hull vertices. Only merged pieces
        // need the convex envelope of two or three prior collision shapes.
        Chaos::FConvexPtr Hull = new Chaos::FConvex(Points, 0.f);
        if (Hull->NumVertices() < 4) return TEXT("{\"error\":\"Degenerate merged convex\"}");
        NewHulls.Add(MoveTemp(Hull));
    }
    Collection->Modify();
    for (int32 I = 0; I < LeafCount; ++I)
        Hulls->ConvexHull[*Hulls->TransformToConvexIndices[I].CreateConstIterator()] = MoveTemp(NewHulls[I]);
    Collection->InvalidateCollection();
    Collection->CreateSimulationData();
    Collection->RebuildRenderData();
    Collection->MarkPackageDirty();
    return InspectCollection(Collection);
#else
    return TEXT("{\"error\":\"Editor only\"}");
#endif
}

FString UNGDColumnAuthoring::ConfigureConcreteCrumbs(UNiagaraSystem* System)
{
#if WITH_EDITOR
    if (!System || System->GetPathName() != TEXT("/Game/ReinforcedColumn01/NS_RC03_ConcreteCrumbs.NS_RC03_ConcreteCrumbs"))
        return TEXT("{\"error\":\"Expected column-local effect copy\"}");
    bool bHasSmallPieces = false;
    TSet<FGuid> Remove;
    for (const auto& Handle : System->GetEmitterHandles())
    {
        bHasSmallPieces |= Handle.GetName() == TEXT("ConcretePiecesSmall");
        if (Handle.GetName() == TEXT("ConcretePiecesLarge")) Remove.Add(Handle.GetId());
    }
    if (!bHasSmallPieces || Remove.Num() != 1)
        return TEXT("{\"error\":\"Unexpected source emitter layout\"}");
    System->Modify();
    // Keep the existing fine mesh particles and dust presentation. Large flying
    // chunks are supplied by Chaos; do not duplicate them in the visual effect.
    System->RemoveEmitterHandlesById(Remove);
    System->RequestCompile(true);
    System->WaitForCompilationComplete(true);
    if (!System->IsValid()) return TEXT("{\"error\":\"Niagara compilation failed\"}");
    System->MarkPackageDirty();
    TArray<TSharedPtr<FJsonValue>> Emitters;
    for (const auto& Handle : System->GetEmitterHandles())
    {
        TSharedRef<FJsonObject> Row = MakeShared<FJsonObject>();
        Row->SetStringField(TEXT("name"), Handle.GetName().ToString());
        Row->SetBoolField(TEXT("enabled"), Handle.GetIsEnabled());
        if (const auto* Data = Handle.GetEmitterData())
            Row->SetStringField(TEXT("simulation"), Data->SimTarget == ENiagaraSimTarget::GPUComputeSim ? TEXT("GPU") : TEXT("CPU"));
        Emitters.Add(MakeShared<FJsonValueObject>(Row));
    }
    TSharedRef<FJsonObject> Out = MakeShared<FJsonObject>();
    Out->SetArrayField(TEXT("emitters"), Emitters);
    Out->SetBoolField(TEXT("valid"), true);
    return ToJson(Out);
#else
    return TEXT("{\"error\":\"Editor only\"}");
#endif
}

FString UNGDColumnAuthoring::BuildDemoColumnCladding(const FString& SourceFile)
{
#if WITH_EDITOR
    FString Full = FPaths::ConvertRelativePathToFull(SourceFile);
    FPaths::NormalizeFilename(Full);
    FPaths::CollapseRelativeDirectories(Full);
    FString Allowed = FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir() / TEXT("DemoTiledColumn01/Correction02/"));
    FPaths::NormalizeFilename(Allowed);
    FString VariedSource = FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir() / TEXT("DemoTiledColumn01/Correction04/"));
    FPaths::NormalizeFilename(VariedSource);
    const bool bVaried = Full.StartsWith(VariedSource);
    if (!Full.StartsWith(Allowed) && !bVaried) return TEXT("{\"error\":\"Correction source directory required\"}");
    FString Raw;
    TSharedPtr<FJsonObject> Source;
    if (!FFileHelper::LoadFileToString(Raw, *Full) || !FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Raw), Source))
        return TEXT("{\"error\":\"Invalid cladding source\"}");
    auto* Vendor = LoadObject<UGeometryCollection>(nullptr, bVaried
        ? TEXT("/Game/Experiments/DemoTiledColumn01/Correction03/GC_DemoColumn03.GC_DemoColumn03")
        : TEXT("/Game/NextGenDestruction/GeometryCollections/Concrete/GC_ConcretePillar_Square_5m.GC_ConcretePillar_Square_5m"));
    if (!Vendor) return TEXT("{\"error\":\"Missing source collection\"}");
    const auto C = Vendor->GetGeometryCollection();
    TArray<FTransform> Global;
    GeometryCollectionAlgo::GlobalMatrices(C->Transform, C->Parent, Global);
    const FVector ActorScale = bVaried ? FVector::OneVector : FVector(2.364, 2.364, 3.6);
    struct FSurface { FVector A, B, D; };
    struct FExterior { int32 Bone; FBox Bounds = FBox(ForceInit); TArray<FSurface> Surfaces; };
    TArray<FExterior> Exterior;
    TMap<int32, int32> ExteriorByBone;
    for (int32 F = 0; F < C->Indices.Num(); ++F)
    {
        if (!C->Visible[F] || C->MaterialID[F] != 0) continue;
        const FIntVector T = C->Indices[F];
        const int32 Bone = C->BoneMap[T.X];
        if (C->SimulationType[Bone] != FGeometryCollection::FST_Rigid || !C->Children[Bone].IsEmpty()) continue;
        int32* Existing = ExteriorByBone.Find(Bone);
        const int32 Index = Existing ? *Existing : Exterior.AddDefaulted();
        if (!Existing) { ExteriorByBone.Add(Bone, Index); Exterior[Index].Bone = Bone; }
        auto& E = Exterior[Index];
        const FSurface Surface{Global[Bone].TransformPosition(FVector(C->Vertex[T.X])) * ActorScale,
            Global[Bone].TransformPosition(FVector(C->Vertex[T.Y])) * ActorScale,
            Global[Bone].TransformPosition(FVector(C->Vertex[T.Z])) * ActorScale};
        E.Surfaces.Add(Surface);
        E.Bounds += Surface.A; E.Bounds += Surface.B; E.Bounds += Surface.D;
    }
    if (Exterior.IsEmpty()) return TEXT("{\"error\":\"Missing source exterior\"}");
    TArray<UMaterialInterface*> Materials;
    for (const auto& Value : Source->GetArrayField(TEXT("materials")))
    {
        auto* Material = LoadObject<UMaterialInterface>(nullptr, *Value->AsString());
        if (!Material) return TEXT("{\"error\":\"Missing cladding material\"}");
        Materials.Add(Material);
    }
    const FString Destination = bVaried ? TEXT("/Game/Experiments/DemoTiledColumn01/Correction04/") : TEXT("/Game/Experiments/DemoTiledColumn01/Correction02/");
    TArray<UStaticMesh*> Meshes;
    for (const auto& Value : Source->GetArrayField(TEXT("meshes")))
    {
        const FString Name = FString::Printf(TEXT("SM_Tile%02d_%03d"), bVaried ? 4 : 2, Meshes.Num());
        const FString PackageName = Destination + Name;
        if (FPackageName::DoesPackageExist(PackageName)) return TEXT("{\"error\":\"Cladding mesh already exists\"}");
        UPackage* Package = CreatePackage(*PackageName);
        UStaticMesh* MeshAsset = NewObject<UStaticMesh>(Package, *Name, RF_Public | RF_Standalone);
        for (int32 I = 0; I < Materials.Num(); ++I)
        {
            const FName Slot(*FString::Printf(TEXT("Slot%d"), I));
            MeshAsset->GetStaticMaterials().Add(FStaticMaterial(Materials[I], Slot, Slot));
        }
        MeshAsset->SetNumSourceModels(1);
        auto& Settings = MeshAsset->GetSourceModel(0).BuildSettings;
        Settings.bRecomputeNormals = false;
        Settings.bRecomputeTangents = false;
        Settings.bUseFullPrecisionUVs = true;
        FMeshDescription Mesh = ReadMesh(Value->AsObject());
        UStaticMesh::FBuildMeshDescriptionsParams Params;
        Params.bBuildSimpleCollision = false;
        Params.bFastBuild = false;
        Params.bCommitMeshDescription = true;
        MeshAsset->BuildFromMeshDescriptions({&Mesh}, Params);
        MeshAsset->CreateBodySetup();
        auto* Body = MeshAsset->GetBodySetup();
        Body->CollisionTraceFlag = CTF_UseSimpleAndComplex;
        FKConvexElem Convex;
        for (const auto& Vertex : Value->AsObject()->GetArrayField(TEXT("vertices")))
        {
            const auto& V = Vertex->AsArray();
            Convex.VertexData.Add(FVector(V[0]->AsNumber(), V[1]->AsNumber(), V[2]->AsNumber()));
        }
        Convex.UpdateElemBox();
        Body->AggGeom.ConvexElems.Add(MoveTemp(Convex));
        Body->InvalidatePhysicsData();
        Body->CreatePhysicsMeshes();
        FAssetRegistryModule::AssetCreated(MeshAsset);
        MeshAsset->MarkPackageDirty();
        Meshes.Add(MeshAsset);
    }
    const FString DataName = bVaried ? TEXT("DA_Cladding04") : TEXT("DA_Cladding02");
    if (FPackageName::DoesPackageExist(Destination + DataName)) return TEXT("{\"error\":\"Cladding data already exists\"}");
    auto* Data = NewObject<UDemoColumnCladdingData>(CreatePackage(*(Destination + DataName)), *DataName, RF_Public | RF_Standalone);
    int32 Bonded = 0;
    for (const auto& Value : Source->GetArrayField(TEXT("tiles")))
    {
        const auto Tile = Value->AsObject();
        const auto& S = Tile->GetArrayField(TEXT("sample"));
        const FVector Sample(S[0]->AsNumber(), S[1]->AsNumber(), S[2]->AsNumber());
        double Best = TNumericLimits<double>::Max();
        int32 Host = INDEX_NONE;
        const FVector WorldSample = Sample * ActorScale;
        TArray<int32> Candidates;
        for (int32 I = 0; I < Exterior.Num(); ++I) Candidates.Add(I);
        Candidates.Sort([&](int32 L, int32 R) { return Exterior[L].Bounds.ComputeSquaredDistanceToPoint(WorldSample) < Exterior[R].Bounds.ComputeSquaredDistanceToPoint(WorldSample); });
        for (const int32 Index : Candidates)
        {
            const auto& E = Exterior[Index];
            if (E.Bounds.ComputeSquaredDistanceToPoint(WorldSample) > Best) break;
            for (const auto& Surface : E.Surfaces)
            {
                const FVector Closest = FMath::ClosestPointOnTriangleToPoint(WorldSample, Surface.A, Surface.B, Surface.D);
                const double Distance = FVector::DistSquared(Closest, WorldSample);
                if (Distance < Best) { Best = Distance; Host = E.Bone; }
            }
        }
        const auto& P = Tile->GetArrayField(TEXT("position"));
        FDemoColumnTile Record;
        Record.Mesh = Meshes[int32(Tile->GetNumberField(TEXT("mesh")))];
        Record.Bone = Host;
        Record.RestTransform = FTransform(FRotator(0, Tile->GetNumberField(TEXT("yaw")), 0), FVector(P[0]->AsNumber(), P[1]->AsNumber(), P[2]->AsNumber()));
        Record.RelativeToBone = Record.RestTransform.GetRelativeTransform(Global[Host]);
        Record.bBonded = Tile->GetBoolField(TEXT("bonded")) && C->InitialDynamicState[Host] != int32(Chaos::EObjectStateType::Kinematic);
        double Area = 0.;
        Tile->TryGetNumberField(TEXT("area_cm2"), Area);
        Record.AreaCm2 = Area;
        Bonded += Record.bBonded ? 1 : 0;
        Data->Tiles.Add(Record);
    }
    FAssetRegistryModule::AssetCreated(Data);
    Data->MarkPackageDirty();
    const auto Out = MakeShared<FJsonObject>();
    Out->SetNumberField(TEXT("tiles"), Data->Tiles.Num());
    Out->SetNumberField(TEXT("bonded"), Bonded);
    Out->SetNumberField(TEXT("clean_release"), Data->Tiles.Num() - Bonded);
    Out->SetNumberField(TEXT("mesh_variants"), Meshes.Num());
    Out->SetStringField(TEXT("concrete"), Vendor->GetPathName());
    return ToJson(Out);
#else
    return TEXT("{\"error\":\"Editor required\"}");
#endif
}

FString UNGDColumnAuthoring::BakeDemoColumnScale()
{
#if WITH_EDITOR
    const FString Destination(TEXT("/Game/Experiments/DemoTiledColumn01/Correction03/"));
    if (FPackageName::DoesPackageExist(Destination + TEXT("GC_DemoColumn03")))
        return TEXT("{\"error\":\"Scaled source already exists\"}");
    auto* Vendor = LoadObject<UGeometryCollection>(nullptr, TEXT("/Game/NextGenDestruction/GeometryCollections/Concrete/GC_ConcretePillar_Square_5m.GC_ConcretePillar_Square_5m"));
    auto* Previous = LoadObject<UDemoColumnCladdingData>(nullptr, TEXT("/Game/Experiments/DemoTiledColumn01/Correction02/DA_Cladding02.DA_Cladding02"));
    if (!Vendor || !Previous) return TEXT("{\"error\":\"Missing source\"}");
    const FVector Scale(2.364, 2.364, 3.6);
    auto* Asset = DuplicateObject<UGeometryCollection>(Vendor, CreatePackage(*(Destination + TEXT("GC_DemoColumn03"))), TEXT("GC_DemoColumn03"));
    const auto C = Asset->GetGeometryCollection();
    TArray<FTransform> Global;
    GeometryCollectionAlgo::GlobalMatrices(C->Transform, C->Parent, Global);
    const auto Out = MakeShared<FJsonObject>();
    if (auto* External = C->FindAttribute<Chaos::FImplicitObjectPtr>(FGeometryCollection::ExternalCollisionsAttribute, FGeometryCollection::TransformGroup))
        for (int32 B = 0; B < External->Num(); ++B)
            if ((*External)[B])
            {
                // This vendor stores external collision in identity rest frames.
                // Replace shared implicits; never scale a source object in place.
                if (!Global[B].Equals(FTransform::Identity)) return TEXT("{\"error\":\"Unexpected external collision frame\"}");
                (*External)[B] = (*External)[B]->DeepCopyGeometryWithScale(Chaos::FVec3(Scale));
            }
    if (const auto* Mass = C->FindAttribute<FTransform>(TEXT("MassToLocal"), FGeometryCollection::TransformGroup))
        if (Mass->Num()) Out->SetStringField(TEXT("vendor_root_mass_to_local"), (*Mass)[0].ToString());
    // Bake the enlargement into geometry, retaining every fracture, bone ID,
    // hierarchy edge and anchor. Chaos then runs at unit component scale.
    for (int32 V = 0; V < C->Vertex.Num(); ++V)
    {
        const FTransform& Frame = Global[C->BoneMap[V]];
        C->Vertex[V] = FVector3f(Frame.TransformPosition(FVector(C->Vertex[V])) * Scale);
        C->Normal[V] = FVector3f((Frame.TransformVectorNoScale(FVector(C->Normal[V]) / Frame.GetScale3D()) / Scale).GetSafeNormal());
        C->TangentU[V] = FVector3f((Frame.TransformVector(FVector(C->TangentU[V])) * Scale).GetSafeNormal());
        C->TangentV[V] = FVector3f((Frame.TransformVector(FVector(C->TangentV[V])) * Scale).GetSafeNormal());
    }
    if (auto Hulls = FGeometryCollectionConvexUtility::GetConvexHullDataIfPresent(C.Get()))
    {
        TSet<int32> Owners;
        // The vendor has one owner per hull. Refuse ambiguous shared frames.
        for (int32 B = 0; B < C->Transform.Num(); ++B)
            for (int32 H : Hulls->TransformToConvexIndices[B])
            {
                if (Owners.Contains(H)) return TEXT("{\"error\":\"Shared hull frame\"}");
                Owners.Add(H);
                const auto& Old = Hulls->ConvexHull[H];
                if (!Old) continue;
                TArray<Chaos::FConvex::FVec3Type> Points;
                for (int32 V = 0; V < Old->NumVertices(); ++V)
                    Points.Add(Chaos::FConvex::FVec3Type(Global[B].TransformPosition(FVector(Old->GetVertex(V))) * Scale));
                Hulls->ConvexHull[H] = new Chaos::FConvex(Points, 0.f);
            }
        Out->SetNumberField(TEXT("retained_collision_hulls"), Owners.Num());
    }
    for (int32 B = 0; B < C->Transform.Num(); ++B) C->Transform[B] = FTransform3f::Identity;
    for (int32 G = 0; G < C->BoundingBox.Num(); ++G)
    {
        FBox Box(ForceInit);
        for (int32 V = C->VertexStart[G]; V < C->VertexStart[G] + C->VertexCount[G]; ++V) Box += FVector(C->Vertex[V]);
        C->BoundingBox[G] = Box;
    }
    FGeometryCollectionConvexUtility::SetVolumeAttributes(C.Get());
    Asset->DamagePropagationData.bEnabled = false;
    Asset->DamagePropagationData.BreakDamagePropagationFactor = 0.f;
    Asset->DamagePropagationData.ShockDamagePropagationFactor = 0.f;
    Asset->InvalidateCollection();
    Asset->CreateSimulationData();
    Asset->RebuildRenderData();
    FAssetRegistryModule::AssetCreated(Asset);
    Asset->MarkPackageDirty();
    auto* Data = DuplicateObject<UDemoColumnCladdingData>(Previous, CreatePackage(*(Destination + TEXT("DA_Cladding03"))), TEXT("DA_Cladding03"));
    for (auto& Tile : Data->Tiles)
    {
        Tile.RestTransform = Tile.RestTransform * FTransform(FQuat::Identity, FVector::ZeroVector, Scale);
        Tile.RelativeToBone = Tile.RestTransform;
    }
    FAssetRegistryModule::AssetCreated(Data);
    Data->MarkPackageDirty();
    Out->SetNumberField(TEXT("transforms"), C->Transform.Num());
    Out->SetNumberField(TEXT("geometries"), C->BoundingBox.Num());
    Out->SetNumberField(TEXT("faces"), C->Indices.Num());
    Out->SetNumberField(TEXT("tiles"), Data->Tiles.Num());
    return ToJson(Out);
#else
    return TEXT("{\"error\":\"Editor required\"}");
#endif
}

FString UNGDColumnAuthoring::AddDemoColumnTiles(UGeometryCollection* Collection, const FString& SourceFile)
{
#if WITH_EDITOR
    if (!Collection || Collection->GetPathName() != TEXT("/Game/Experiments/DemoTiledColumn01/GC_DemoTiledColumn01.GC_DemoTiledColumn01"))
        return TEXT("{\"error\":\"Experiment collection required\"}");
    FString Full = FPaths::ConvertRelativePathToFull(SourceFile);
    FPaths::NormalizeFilename(Full);
    FPaths::CollapseRelativeDirectories(Full);
    FString Allowed = FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir() / TEXT("DemoTiledColumn01/"));
    FPaths::NormalizeFilename(Allowed);
    if (!Full.StartsWith(Allowed)) return TEXT("{\"error\":\"Experiment source directory required\"}");
    FString Raw;
    TSharedPtr<FJsonObject> Source;
    if (!FFileHelper::LoadFileToString(Raw, *Full) || !FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Raw), Source))
        return TEXT("{\"error\":\"Invalid tile source\"}");
    const auto C = Collection->GetGeometryCollection();
    if (!C || C->Transform.Num() != 1086 || C->TransformIndex.Num() != 731 || Collection->Materials.Num() != 4)
        return TEXT("{\"error\":\"Fresh vendor duplicate with four materials required\"}");
    TArray<FTransform> Global;
    GeometryCollectionAlgo::GlobalMatrices(C->Transform, C->Parent, Global);
    struct FSurface { FVector A, B, D; int32 Bone; };
    TArray<FSurface> Surfaces;
    for (int32 F = 0; F < C->Indices.Num(); ++F)
    {
        if (C->MaterialID[F] != 0) continue;
        const FIntVector T = C->Indices[F];
        const int32 Bone = C->BoneMap[T.X];
        if (C->SimulationType[Bone] != FGeometryCollection::FST_Rigid || C->Parent[Bone] == INDEX_NONE) continue;
        Surfaces.Add({Global[Bone].TransformPosition(FVector(C->Vertex[T.X])),
            Global[Bone].TransformPosition(FVector(C->Vertex[T.Y])),
            Global[Bone].TransformPosition(FVector(C->Vertex[T.Z])), Bone});
    }
    if (Surfaces.IsEmpty()) return TEXT("{\"error\":\"No vendor exterior surface\"}");
    Collection->Modify();
    TArray<int32> TileBones;
    TArray<int32> TileHosts;
    TMap<int32, TArray<int32>> BondedGroups;
    int32 Counts[4] = {};
    for (const auto& Value : Source->GetArrayField(TEXT("pieces")))
    {
        const auto Piece = Value->AsObject();
        const auto& P = Piece->GetArrayField(TEXT("sample"));
        const FVector Sample(P[0]->AsNumber(), P[1]->AsNumber(), P[2]->AsNumber());
        double Best = TNumericLimits<double>::Max();
        int32 Host = INDEX_NONE;
        for (const auto& S : Surfaces)
        {
            const double Distance = FVector::DistSquared(Sample, FMath::ClosestPointOnTriangleToPoint(Sample, S.A, S.B, S.D));
            if (Distance < Best) { Best = Distance; Host = S.Bone; }
        }
        int32 Mode = int32(Piece->GetNumberField(TEXT("mode")));
        if (Mode == 3 && C->InitialDynamicState[Host] == int32(Chaos::EObjectStateType::Kinematic)) Mode = 2;
        const int32 Tile = C->Transform.Num();
        FMeshDescription Mesh = ReadMesh(Piece);
        FGeometryCollectionEngineConversion::AppendMeshDescription(&Mesh,
            FString::Printf(TEXT("Tile_%d_%03d"), Mode, TileBones.Num()), 0, FTransform::Identity, C.Get(), nullptr, false, false, false);
        C->InitialDynamicState[Tile] = int32(Chaos::EObjectStateType::Dynamic);
        GeometryCollectionAlgo::ParentTransforms(C.Get(), C->Parent[Host], {Tile});
        TileBones.Add(Tile);
        TileHosts.Add(Host);
        ++Counts[Mode];
        if (Mode == 3) BondedGroups.FindOrAdd(Host).Add(Tile);
    }
    for (auto& Group : BondedGroups)
    {
        Group.Value.Insert(Group.Key, 0);
        const int32 Cluster = FGeometryCollectionClusteringUtility::ClusterBonesUnderNewNodeWithParent(
            C.Get(), C->Parent[Group.Key], Group.Value, true, false);
        C->InitialDynamicState[Cluster] = C->InitialDynamicState[Group.Key];
        C->BoneName[Cluster] = FString::Printf(TEXT("TileConcreteBond_%d"), Group.Key);
    }
    FGeometryCollectionClusteringUtility::UpdateHierarchyLevelOfChildren(C.Get(), -1);
    C->ReindexMaterials();
    // Generate only new tile hulls; the demo's detailed concrete leaf collision is retained.
    FGeometryCollectionConvexUtility::FLeafConvexHullSettings LeafSettings;
    FGeometryCollectionConvexUtility::GenerateLeafConvexHulls(*C, true, TileBones, LeafSettings);
    FGeometryCollectionConvexUtility::FClusterConvexHullSettings ClusterSettings;
    FGeometryCollectionConvexUtility::GenerateClusterConvexHullsFromChildrenHulls(*C, ClusterSettings);
    FGeometryCollectionProximityUtility(C.Get()).UpdateProximity();
    auto& Proximity = C->ModifyAttribute<TSet<int32>>(TEXT("Proximity"), FGeometryCollection::GeometryGroup);
    for (int32 I = 0; I < TileBones.Num(); ++I)
    {
        const int32 TileGeometry = C->TransformToGeometryIndex[TileBones[I]];
        const int32 HostGeometry = C->TransformToGeometryIndex[TileHosts[I]];
        Proximity[TileGeometry].Add(HostGeometry);
        Proximity[HostGeometry].Add(TileGeometry);
    }
    FGeometryCollectionProximityUtility(C.Get()).CopyProximityToConnectionGraph();
    GeometryCollection::Facades::FCollectionConnectionGraphFacade Connections(*C);
    Connections.DefineSchema();
    for (int32 I = 0; I < TileBones.Num(); ++I)
    {
        int32 Host = TileHosts[I];
        while (C->Parent[Host] != C->Parent[TileBones[I]] && C->Parent[Host] != INDEX_NONE) Host = C->Parent[Host];
        if (C->Parent[Host] != C->Parent[TileBones[I]]) continue;
        bool bConnected = false;
        for (int32 Edge = 0; Edge < Connections.NumConnections(); ++Edge)
        {
            const auto Pair = Connections.GetConnection(Edge);
            if ((Pair.Key == TileBones[I] && Pair.Value == Host) || (Pair.Value == TileBones[I] && Pair.Key == Host))
            { bConnected = true; break; }
        }
        if (!bConnected)
        {
            if (Connections.HasContactAreas()) Connections.ConnectWithContact(TileBones[I], Host, 1.f);
            else Connections.Connect(TileBones[I], Host);
        }
    }
    // Original two active levels keep their vendor thresholds. The extra bond level
    // holds selected tiles to the original concrete fragments until a stronger hit.
    Collection->DamageThreshold = {500000.f, 50000.f, 150000.f, 150000.f};
    Collection->MaxClusterLevel = 10;
    Collection->InvalidateCollection();
    Collection->CreateSimulationData();
    Collection->RebuildRenderData();
    Collection->MarkPackageDirty();
    const auto Out = MakeShared<FJsonObject>();
    Out->SetNumberField(TEXT("vendor_geometries_retained"), 731);
    Out->SetNumberField(TEXT("tile_fragments"), TileBones.Num());
    Out->SetNumberField(TEXT("clean"), Counts[0]);
    Out->SetNumberField(TEXT("thin_backing"), Counts[1]);
    Out->SetNumberField(TEXT("thick_backing"), Counts[2]);
    Out->SetNumberField(TEXT("bonded_to_original_concrete"), Counts[3]);
    Out->SetNumberField(TEXT("bond_clusters"), BondedGroups.Num());
    return ToJson(Out);
#else
    return TEXT("{\"error\":\"Editor required\"}");
#endif
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
    bool bPreserveStaticMeshes = false;
    Source->TryGetBoolField(TEXT("preserve_static_meshes"), bPreserveStaticMeshes);
    if (bPreserveStaticMeshes)
    {
        // A surface-preserving piece merge must also retain the optimized core
        // collider and the exact saved reinforcement rather than reimporting them.
        for (const TCHAR* Name : {TEXT("SM_RC01_SupportedColumn"), TEXT("SM_RC01_Rebar")})
            if (!LoadObject<UStaticMesh>(nullptr, *(FString(TEXT("/Game/ReinforcedColumn01/")) + Name)))
                return TEXT("{\"error\":\"Missing retained static mesh\"}");
    }
    else
    {
        FMeshDescription Core = ReadMesh(Source->GetObjectField(TEXT("core")));
        FMeshDescription Steel = ReadMesh(Source->GetObjectField(TEXT("steel")));
        MakeStatic(TEXT("SM_RC01_SupportedColumn"), Core, Materials);
        MakeStatic(TEXT("SM_RC01_Rebar"), Steel, Materials);
    }

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
    // Vendor impact fields sample active particles and their immediate children.
    // Keep the fine fragments directly below the root: an intermediate anchored
    // cluster places its centre outside a local bullet field and shields its
    // disabled children from strain. Embedded anchored leaves retain support.
    FGeometryCollectionClusteringUtility::UpdateHierarchyLevelOfChildren(C.Get(), -1);
    for (int32 I = 0; I < C->Transform.Num(); ++I)
        C->InitialDynamicState[I] = int32(I < DynamicCount ? Chaos::EObjectStateType::Dynamic : Chaos::EObjectStateType::Kinematic);
    Chaos::Facades::FCollectionAnchoringFacade Anchoring(*C);
    Anchoring.AddAnchoredAttribute();
    for (int32 I = 0; I < C->Transform.Num(); ++I)
        Anchoring.SetAnchored(I, I >= DynamicCount && I < Number);
    FGeometryCollectionConvexUtility::CreateNonOverlappingConvexHullData(C.Get());
    FGeometryCollectionProximityUtility(C.Get()).UpdateProximity();
    Asset->EnableClustering = true;
    Asset->EnableNanite = true;
    // Leaves previously inherited 50000 from their level-one local cluster.
    // Preserve that resistance after removing the otherwise shielding level.
    Asset->DamageThreshold = {50000.f};
    // A bullet should detach pieces inside its field without cascading through
    // the connection graph into the remaining supported shell.
    Asset->DamagePropagationData.bEnabled = false;
    Asset->DamagePropagationData.BreakDamagePropagationFactor = 0.f;
    Asset->DamagePropagationData.ShockDamagePropagationFactor = 0.f;
    Asset->bMassAsDensity = true;
    Asset->Mass = 2400.f;
    Asset->MinimumMassClamp = .1f;
    Asset->bRemoveOnMaxSleep = true;
    Asset->MaximumSleepTime = FVector2D(3., 5.);
    Asset->RemovalDuration = FVector2D(1., 2.);
    Asset->bSlowMovingAsSleeping = true;
    Asset->SlowMovingVelocityThreshold = 10.f;
    Asset->SizeSpecificData.SetNum(1);
    Asset->SizeSpecificData[0].CollisionShapes.SetNum(1);
    auto& Shape = Asset->SizeSpecificData[0].CollisionShapes[0];
    // Convex-to-convex contacts avoid particle/level-set collision on the dense
    // authored fracture surfaces while retaining the generated convex hulls.
    Shape.CollisionType = ECollisionTypeEnum::Chaos_Volumetric;
    Shape.ImplicitType = EImplicitTypeEnum::Chaos_Implicit_Convex;
    Asset->InvalidateCollection();
    Asset->CreateSimulationData();
    Asset->RebuildRenderData();
    if (bNew) FAssetRegistryModule::AssetCreated(Asset);
    Asset->MarkPackageDirty();
    const TArray<TSharedPtr<FJsonValue>>* Previews = nullptr;
    if (Source->TryGetArrayField(TEXT("previews"), Previews))
    {
        for (const auto& PreviewValue : *Previews)
        {
            const auto Preview = PreviewValue->AsObject();
            const FString Name = Preview->GetStringField(TEXT("name"));
            if (!Name.StartsWith(TEXT("SM_RC02_Preview_")) || Name.Contains(TEXT("/"))) continue;
            FMeshDescription Combined;
            FStaticMeshAttributes Attributes(Combined);
            Attributes.Register();
            Attributes.GetVertexInstanceUVs().SetNumChannels(1);
            for (const auto& Index : Preview->GetArrayField(TEXT("pieces")))
            {
                const FMeshDescription Part = ReadMesh(Source->GetArrayField(TEXT("pieces"))[int32(Index->AsNumber())]->AsObject());
                FStaticMeshOperations::AppendMeshDescription(Part, Combined, FStaticMeshOperations::FAppendSettings());
            }
            MakeStatic(*Name, Combined, Materials);
        }
    }
    return InspectCollection(Asset);
#else
    return TEXT("{\"error\":\"Editor only\"}");
#endif
}
