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
#include "GeometryCollection/GeometryCollectionAlgo.h"
#include "Chaos/Convex.h"
#include "GeometryCollection/Facades/CollectionAnchoringFacade.h"
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
