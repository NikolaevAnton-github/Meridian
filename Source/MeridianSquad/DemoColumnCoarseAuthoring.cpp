#include "NGDColumnAuthoring.h"
#include "DemoColumnCladding.h"

#if WITH_EDITOR
#include "AssetRegistry/AssetRegistryModule.h"
#include "Engine/StaticMesh.h"
#include "MeshDescription.h"
#include "StaticMeshAttributes.h"
#include "GeometryCollection/GeometryCollectionObject.h"
#include "GeometryCollection/GeometryCollection.h"
#include "GeometryCollection/GeometryCollectionAlgo.h"
#include "GeometryCollection/GeometryCollectionClusteringUtility.h"
#include "GeometryCollection/GeometryCollectionConvexUtility.h"
#include "GeometryCollection/GeometryCollectionProximityUtility.h"
#include "GeometryCollection/Facades/CollectionAnchoringFacade.h"
#include "Misc/PackageName.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "UObject/Package.h"
#include "PlanarCut.h"
#include "Voronoi/Voronoi.h"
#include "PhysicalMaterials/PhysicalMaterial.h"
#include "Serialization/JsonSerializer.h"

namespace
{
struct FColumnSurfaceTriangle
{
    FVector P[3];
    FVector Normal;
    FBox Bounds;
};
struct FColumnTileTriangle { FVector2D P[3]; FBox2D Bounds; };

int32 ProtectCoarseCore(FGeometryCollection& C, UDemoColumnCladdingData& Data)
{
    TArray<FTransform> Global;
    GeometryCollectionAlgo::GlobalMatrices(C.Transform, C.Parent, Global);
    TArray<FBox> Bounds;
    Bounds.Init(FBox(ForceInit), Global.Num());
    for (int32 V = 0; V < C.Vertex.Num(); ++V)
    {
        const int32 B = C.BoneMap[V];
        Bounds[B] += Global[B].TransformPosition(FVector(C.Vertex[V]));
    }
    // A tiny exterior patch does not turn a full-depth structural block into
    // facing. Preserve every original fragment entering the central 70 cm square.
    Data.SurfaceBones.RemoveAll([&](int32 B)
    {
        const FBox& Box = Bounds[B];
        return Box.Min.X < 35. && Box.Max.X > -35. && Box.Min.Y < 35. && Box.Max.Y > -35.;
    });
    Chaos::Facades::FCollectionAnchoringFacade Anchoring(C);
    Anchoring.AddAnchoredAttribute();
    int32 Core = 0;
    for (int32 B = 0; B < C.Transform.Num(); ++B)
    {
        const bool bCore = C.SimulationType[B] == FGeometryCollection::FST_Rigid && !Data.SurfaceBones.Contains(B);
        Anchoring.SetAnchored(B, bCore);
        if (C.SimulationType[B] == FGeometryCollection::FST_Rigid)
            C.InitialDynamicState[B] = int32(bCore ? Chaos::EObjectStateType::Kinematic : Chaos::EObjectStateType::Dynamic);
        Core += bCore;
    }
    return Core;
}

bool Overlap(const FVector2D* A, const FVector2D* B)
{
    for (int32 S = 0; S < 2; ++S)
        for (int32 E = 0; E < 3; ++E)
        {
            const auto* T = S ? B : A;
            const FVector2D Edge = T[(E + 1) % 3] - T[E];
            const FVector2D Axis(-Edge.Y, Edge.X);
            double MinA = DBL_MAX, MaxA = -DBL_MAX, MinB = DBL_MAX, MaxB = -DBL_MAX;
            for (int32 V = 0; V < 3; ++V)
            {
                const double X = FVector2D::DotProduct(A[V], Axis), Y = FVector2D::DotProduct(B[V], Axis);
                MinA = FMath::Min(MinA, X); MaxA = FMath::Max(MaxA, X);
                MinB = FMath::Min(MinB, Y); MaxB = FMath::Max(MaxB, Y);
            }
            // Exclude an edge-only contact, but retain thin genuine overlap.
            const double Tolerance = .001 * Axis.Size();
            if (MaxA <= MinB + Tolerance || MaxB <= MinA + Tolerance) return false;
        }
    return true;
}
}
#endif

FString UNGDColumnAuthoring::BuildDemoColumnCoarse()
{
#if WITH_EDITOR
    const FString Destination(TEXT("/Game/Experiments/DemoTiledColumn01/Correction06/"));
    if (FPackageName::DoesPackageExist(Destination + TEXT("GC_DemoColumn06"))) return TEXT("{\"error\":\"Candidate already exists\"}");
    auto* Source = LoadObject<UGeometryCollection>(nullptr, TEXT("/Game/Experiments/DemoTiledColumn01/Correction03/GC_DemoColumn03.GC_DemoColumn03"));
    auto* Facing = LoadObject<UDemoColumnCladdingData>(nullptr, TEXT("/Game/Experiments/DemoTiledColumn01/Correction04/DA_Cladding04.DA_Cladding04"));
    if (!Source || !Facing) return TEXT("{\"error\":\"Missing checkpoint assets\"}");
    auto* Asset = DuplicateObject<UGeometryCollection>(Source, CreatePackage(*(Destination + TEXT("GC_DemoColumn06"))), TEXT("GC_DemoColumn06"));
    auto C = Asset->GetGeometryCollection();
    TArray<int32> Leaves;
    int32 OriginalFaces = 0;
    for (int32 B = 0; B < C->Transform.Num(); ++B)
        if (C->SimulationType[B] == FGeometryCollection::FST_Rigid && C->Children[B].IsEmpty())
        {
            Leaves.Add(B);
            OriginalFaces += C->FaceCount[C->TransformToGeometryIndex[B]];
        }
    const int32 OriginalLeaves = Leaves.Num();
    // Preserve all previous fragment meshes and sizes. Only remove the extra
    // hierarchy levels that used to consume hits before a visible piece released.
    FGeometryCollectionClusteringUtility::UpdateHierarchyLevelOfChildren(C.Get(), -1);
    FGeometryCollectionClusteringUtility::ClusterBonesUnderExistingRoot(C.Get(), Leaves);
    FGeometryCollectionClusteringUtility::RemoveDanglingClusters(C.Get());
    FGeometryCollectionClusteringUtility::UpdateHierarchyLevelOfChildren(C.Get(), -1);
    TArray<int32> HiddenGeometry;
    for (int32 G = 0; G < C->TransformIndex.Num(); ++G)
        if (C->SimulationType[C->TransformIndex[G]] != FGeometryCollection::FST_Rigid) HiddenGeometry.Add(G);
    if (HiddenGeometry.Num()) C->RemoveElements(FGeometryCollection::GeometryGroup, HiddenGeometry);
    if (C->TransformIndex.Num() != OriginalLeaves || C->Indices.Num() != OriginalFaces)
        return TEXT("{\"error\":\"Original fragment topology changed\"}");

    TArray<FTransform> Global;
    GeometryCollectionAlgo::GlobalMatrices(C->Transform, C->Parent, Global);
    TMap<int32, TArray<FColumnSurfaceTriangle>> Surfaces;
    TMap<int32, FBox> SurfaceBounds;
    for (int32 F = 0; F < C->Indices.Num(); ++F)
    {
        if (!C->Visible[F] || C->MaterialID[F] != 0) continue;
        const auto T = C->Indices[F];
        const int32 B = C->BoneMap[T.X];
        FColumnSurfaceTriangle Triangle;
        Triangle.P[0] = Global[B].TransformPosition(FVector(C->Vertex[T.X]));
        Triangle.P[1] = Global[B].TransformPosition(FVector(C->Vertex[T.Y]));
        Triangle.P[2] = Global[B].TransformPosition(FVector(C->Vertex[T.Z]));
        Triangle.Normal = -FVector::CrossProduct(Triangle.P[1] - Triangle.P[0], Triangle.P[2] - Triangle.P[0]).GetSafeNormal();
        if (Triangle.Normal.IsNearlyZero() || FMath::Abs(Triangle.Normal.Z) > .3) continue;
        Triangle.Bounds = FBox(Triangle.P, 3);
        Surfaces.FindOrAdd(B).Add(Triangle);
        auto* Bounds = SurfaceBounds.Find(B);
        if (Bounds) *Bounds += Triangle.Bounds; else SurfaceBounds.Add(B, Triangle.Bounds);
    }
    auto* Data = DuplicateObject<UDemoColumnCladdingData>(Facing, CreatePackage(*(Destination + TEXT("DA_Cladding06"))), TEXT("DA_Cladding06"));
    Surfaces.GetKeys(Data->SurfaceBones);
    Data->SurfaceBones.Sort();
    const int32 Core = ProtectCoarseCore(*C, *Data);
    int32 Links = 0, MaxSupports = 0, EdgeSupports = 0;
    for (auto& Tile : Data->Tiles)
    {
        Tile.SupportBones.Reset();
        const FVector Point = Tile.RestTransform.GetLocation();
        const FVector Normal = Tile.RestTransform.GetUnitAxis(EAxis::X);
        const FVector U = Tile.RestTransform.GetUnitAxis(EAxis::Y), V = Tile.RestTransform.GetUnitAxis(EAxis::Z);
        auto Project = [&](const FVector& P) { const FVector D = P - Point; return FVector2D(FVector::DotProduct(D, U), FVector::DotProduct(D, V)); };
        const FMeshDescription* Mesh = Tile.Mesh ? Tile.Mesh->GetMeshDescription(0) : nullptr;
        if (!Mesh) return TEXT("{\"error\":\"Missing tile source mesh\"}");
        const auto Positions = FStaticMeshConstAttributes(*Mesh).GetVertexPositions();
        TArray<FColumnTileTriangle> Footprint;
        FBox TileBounds(ForceInit);
        for (const FTriangleID ID : Mesh->Triangles().GetElementIDs())
        {
            const auto Vertices = Mesh->GetTriangleVertices(ID);
            FVector P[3];
            for (int32 J = 0; J < 3; ++J) P[J] = Tile.RestTransform.TransformPosition(FVector(Positions[Vertices[J]]));
            const FVector N = FVector::CrossProduct(P[1] - P[0], P[2] - P[0]).GetSafeNormal();
            if (FMath::Abs(FVector::DotProduct(N, Normal)) < .8) continue;
            FColumnTileTriangle T;
            for (int32 J = 0; J < 3; ++J) { T.P[J] = Project(P[J]); TileBounds += P[J]; }
            T.Bounds = FBox2D(T.P, 3);
            Footprint.Add(T);
        }
        if (Footprint.IsEmpty()) return TEXT("{\"error\":\"Missing tile footprint\"}");
        TileBounds = TileBounds.ExpandBy(4.);
        double Best = DBL_MAX;
        int32 Primary = INDEX_NONE;
        for (const auto& Pair : Surfaces)
        {
            if (!SurfaceBounds[Pair.Key].Intersect(TileBounds)) continue;
            bool bOverlap = false;
            for (const auto& T : Pair.Value)
            {
                if (FVector::DotProduct(T.Normal, Normal) < .8 || !T.Bounds.Intersect(TileBounds)) continue;
                const double Distance = FVector::DistSquared(Point, FMath::ClosestPointOnTriangleToPoint(Point, T.P[0], T.P[1], T.P[2]));
                if (Distance < Best) { Best = Distance; Primary = Pair.Key; }
                if (bOverlap) continue;
                FVector2D Projected[3] = {Project(T.P[0]), Project(T.P[1]), Project(T.P[2])};
                const FBox2D Bounds(Projected, 3);
                for (const auto& F : Footprint)
                    if (Bounds.Intersect(F.Bounds) && Overlap(Projected, F.P)) { bOverlap = true; break; }
            }
            if (bOverlap) Tile.SupportBones.Add(Pair.Key);
        }
        if (Primary == INDEX_NONE || (Tile.SupportBones.IsEmpty() && Best > 64.))
            return FString::Printf(TEXT("{\"error\":\"Tile has no concrete support\",\"tile\":%d,\"nearest_distance_sq\":%.9f}"), int32(&Tile - Data->Tiles.GetData()), Best);
        // The preserved facing wraps beyond the concrete's side/bottom bevel.
        // Tiny rim slivers need the nearest surface within 8 cm rather than a
        // positive-area intersection. Never accept a distant/unbacked tile.
        if (Tile.SupportBones.IsEmpty())
        {
            ++EdgeSupports;
            UE_LOG(LogTemp, Display, TEXT("DemoColumn06 edge tile=%d point=%s distance=%.3f area=%.3f"),
                int32(&Tile - Data->Tiles.GetData()), *Point.ToCompactString(), FMath::Sqrt(Best), Tile.AreaCm2);
        }
        Tile.SupportBones.AddUnique(Primary);
        Tile.SupportBones.Sort();
        Tile.Bone = Primary;
        Tile.RelativeToBone = Tile.RestTransform.GetRelativeTransform(Global[Primary]);
        Links += Tile.SupportBones.Num();
        MaxSupports = FMath::Max(MaxSupports, Tile.SupportBones.Num());
    }
    C->RemoveAttribute(FGeometryCollection::ExternalCollisionsAttribute, FGeometryCollection::TransformGroup);
    Asset->bImportCollisionFromSource = false;
    FGeometryCollectionConvexUtility::CreateNonOverlappingConvexHullData(C.Get(), .3, 1., .5);
    FGeometryCollectionConvexUtility::SetVolumeAttributes(C.Get());
    FGeometryCollectionProximityUtility(C.Get()).UpdateProximity();
    FGeometryCollectionProximityUtility(C.Get()).CopyProximityToConnectionGraph();
    Asset->DamagePropagationData.bEnabled = false;
    Asset->bRemoveOnMaxSleep = false;
    Asset->InvalidateCollection();
    Asset->CreateSimulationData();
    Asset->RebuildRenderData();
    FAssetRegistryModule::AssetCreated(Asset);
    FAssetRegistryModule::AssetCreated(Data);
    Asset->MarkPackageDirty(); Data->MarkPackageDirty();
    const FString Report = FString::Printf(TEXT("{\"original_leaves\":%d,\"geometries\":%d,\"faces\":%d,\"surface_bones\":%d,\"protected_core_bones\":%d,\"tiles\":%d,\"support_links\":%d,\"max_supports_per_tile\":%d,\"edge_slivers\":%d}"),
        OriginalLeaves, C->TransformIndex.Num(), C->Indices.Num(), Data->SurfaceBones.Num(), Core, Data->Tiles.Num(), Links, MaxSupports, EdgeSupports);
    FFileHelper::SaveStringToFile(Report, *(FPaths::ProjectSavedDir() / TEXT("DemoColumnExperiment06/authoring.json")));
    return Report;
#else
    return TEXT("{\"error\":\"Editor required\"}");
#endif
}

FString UNGDColumnAuthoring::AnchorDemoColumnCore()
{
#if WITH_EDITOR
    auto* Asset = LoadObject<UGeometryCollection>(nullptr, TEXT("/Game/Experiments/DemoTiledColumn01/Correction06/GC_DemoColumn06.GC_DemoColumn06"));
    auto* Data = LoadObject<UDemoColumnCladdingData>(nullptr, TEXT("/Game/Experiments/DemoTiledColumn01/Correction06/DA_Cladding06.DA_Cladding06"));
    if (!Asset || !Data || Data->SurfaceBones.Num() < 500) return TEXT("{\"error\":\"Unexpected candidate\"}");
    auto C = Asset->GetGeometryCollection();
    if (C->TransformIndex.Num() != 730) return TEXT("{\"error\":\"Unexpected topology\"}");
    ProtectCoarseCore(*C, *Data);
    Asset->InvalidateCollection();
    Asset->CreateSimulationData();
    Asset->RebuildRenderData();
    Asset->MarkPackageDirty();
    Data->MarkPackageDirty();
    return InspectCollection(Asset);
#else
    return TEXT("{\"error\":\"Editor required\"}");
#endif
}

FString UNGDColumnAuthoring::BuildDemoColumnRefinement()
{
#if WITH_EDITOR
    const FString Destination(TEXT("/Game/Experiments/DemoTiledColumn01/Correction07/"));
    if (FPackageName::DoesPackageExist(Destination + TEXT("GC_DemoColumn07"))) return TEXT("{\"error\":\"Candidate already exists\"}");
    auto* Source = LoadObject<UGeometryCollection>(nullptr, TEXT("/Game/Experiments/DemoTiledColumn01/Correction06/GC_DemoColumn06.GC_DemoColumn06"));
    auto* Facing = LoadObject<UDemoColumnCladdingData>(nullptr, TEXT("/Game/Experiments/DemoTiledColumn01/Correction06/DA_Cladding06.DA_Cladding06"));
    if (!Source || !Facing) return TEXT("{\"error\":\"Missing checkpoint assets\"}");
    auto* Asset = DuplicateObject<UGeometryCollection>(Source, CreatePackage(*(Destination + TEXT("GC_DemoColumn07"))), TEXT("GC_DemoColumn07"));
    auto C = Asset->GetGeometryCollection();
    TArray<FTransform> BeforeGlobal;
    GeometryCollectionAlgo::GlobalMatrices(C->Transform, C->Parent, BeforeGlobal);
    auto& SourceBone = C->AddAttribute<int32>(TEXT("DemoSourceBone"), FGeometryCollection::TransformGroup);
    for (int32 B = 0; B < C->Transform.Num(); ++B) SourceBone[B] = B;
    TMap<int32, double> Areas;
    for (int32 F = 0; F < C->Indices.Num(); ++F)
    {
        if (!C->Visible[F] || C->MaterialID[F] != 0) continue;
        const auto T = C->Indices[F]; const int32 B = C->BoneMap[T.X];
        const FVector A = BeforeGlobal[B].TransformPosition(FVector(C->Vertex[T.X]));
        const FVector D = BeforeGlobal[B].TransformPosition(FVector(C->Vertex[T.Y]));
        const FVector E = BeforeGlobal[B].TransformPosition(FVector(C->Vertex[T.Z]));
        const FVector Cross = FVector::CrossProduct(D-A,E-A);
        if (FMath::Abs(Cross.GetSafeNormal().Z) < .3) Areas.FindOrAdd(B) += Cross.Size() * .5;
    }
    TArray<int32> CutSources;
    for (const int32 B : Facing->SurfaceBones)
    {
        if (Areas.FindRef(B) < 4000.) continue;
        const int32 G = C->TransformToGeometryIndex[B];
        const FBox Box = C->BoundingBox[G].TransformBy(BeforeGlobal[B]);
        const FVector Size = Box.GetSize();
        const int32 Axis = Size.Z >= Size.X && Size.Z >= Size.Y ? 2 : Size.X >= Size.Y ? 0 : 1;
        struct FSample { double Position, Area; };
        TArray<FSample> Samples;
        for (int32 F = C->FaceStart[G]; F < C->FaceStart[G] + C->FaceCount[G]; ++F)
        {
            if (C->MaterialID[F] != 0) continue;
            const auto T = C->Indices[F];
            const FVector A = BeforeGlobal[B].TransformPosition(FVector(C->Vertex[T.X]));
            const FVector D = BeforeGlobal[B].TransformPosition(FVector(C->Vertex[T.Y]));
            const FVector E = BeforeGlobal[B].TransformPosition(FVector(C->Vertex[T.Z]));
            const FVector Cross = FVector::CrossProduct(D-A,E-A);
            if (FMath::Abs(Cross.GetSafeNormal().Z) < .3) Samples.Add({(A[Axis]+D[Axis]+E[Axis])/3., Cross.Size()*.5});
        }
        Samples.Sort([](const FSample& A, const FSample& B) { return A.Position < B.Position; });
        double Accumulated = 0., Split = Box.GetCenter()[Axis];
        for (const auto& Sample : Samples)
        {
            Accumulated += Sample.Area;
            if (Accumulated >= Areas[B] * .5) { Split = Sample.Position; break; }
        }
        FVector P = Box.GetCenter(); P[Axis] = Split;
        FVector Offset = FVector::ZeroVector; Offset[Axis] = Size[Axis] * .25;
        TArray<FVector> Sites{P-Offset, P+Offset};
        FVoronoiDiagram Diagram(Sites, Box, 1.);
        FPlanarCells Cells(Sites, Diagram);
        Cells.InternalSurfaceMaterials.GlobalMaterialID = 1;
        Cells.InternalSurfaceMaterials.GlobalUVScale = .01f;
        const int32 OldCount = C->Transform.Num();
        CutWithPlanarCells(Cells, *C, B, 0., 0., 280907+B, {}, true, false,
            nullptr, FVector::ZeroVector, FIslandSplitSettings(false));
        if (C->Transform.Num() != OldCount + 2) return TEXT("{\"error\":\"Large fragment did not split into two pieces\"}");
        for (int32 New = OldCount; New < C->Transform.Num(); ++New) SourceBone[New] = B;
        CutSources.Add(B);
    }
    const int32 OriginalLeaves = 730;
    TArray<int32> Leaves;
    for (int32 B = 0; B < C->Transform.Num(); ++B)
        if (C->SimulationType[B] == FGeometryCollection::FST_Rigid && C->Children[B].IsEmpty())
        {
            Leaves.Add(B);
        }

    // Retain the unsplit fragments and flatten the new two-piece cuts. Remove
    // hierarchy levels that used to consume hits before a visible piece released.
    FGeometryCollectionClusteringUtility::UpdateHierarchyLevelOfChildren(C.Get(), -1);
    FGeometryCollectionClusteringUtility::ClusterBonesUnderExistingRoot(C.Get(), Leaves);
    FGeometryCollectionClusteringUtility::RemoveDanglingClusters(C.Get());
    FGeometryCollectionClusteringUtility::UpdateHierarchyLevelOfChildren(C.Get(), -1);
    TArray<int32> HiddenGeometry;
    for (int32 G = 0; G < C->TransformIndex.Num(); ++G)
        if (C->SimulationType[C->TransformIndex[G]] != FGeometryCollection::FST_Rigid) HiddenGeometry.Add(G);
    if (HiddenGeometry.Num()) C->RemoveElements(FGeometryCollection::GeometryGroup, HiddenGeometry);
    if (C->TransformIndex.Num() != OriginalLeaves + CutSources.Num())
        return TEXT("{\"error\":\"Unexpected refined topology\"}");

    TArray<FTransform> Global;
    GeometryCollectionAlgo::GlobalMatrices(C->Transform, C->Parent, Global);
    TMap<int32, TArray<FColumnSurfaceTriangle>> Surfaces;
    TMap<int32, FBox> SurfaceBounds;
    for (int32 F = 0; F < C->Indices.Num(); ++F)
    {
        if (!C->Visible[F] || C->MaterialID[F] != 0) continue;
        const auto T = C->Indices[F];
        const int32 B = C->BoneMap[T.X];
        FColumnSurfaceTriangle Triangle;
        Triangle.P[0] = Global[B].TransformPosition(FVector(C->Vertex[T.X]));
        Triangle.P[1] = Global[B].TransformPosition(FVector(C->Vertex[T.Y]));
        Triangle.P[2] = Global[B].TransformPosition(FVector(C->Vertex[T.Z]));
        Triangle.Normal = -FVector::CrossProduct(Triangle.P[1] - Triangle.P[0], Triangle.P[2] - Triangle.P[0]).GetSafeNormal();
        if (Triangle.Normal.IsNearlyZero() || FMath::Abs(Triangle.Normal.Z) > .3) continue;
        Triangle.Bounds = FBox(Triangle.P, 3);
        Surfaces.FindOrAdd(B).Add(Triangle);
        auto* Bounds = SurfaceBounds.Find(B);
        if (Bounds) *Bounds += Triangle.Bounds; else SurfaceBounds.Add(B, Triangle.Bounds);
    }
    auto* Data = DuplicateObject<UDemoColumnCladdingData>(Facing, CreatePackage(*(Destination + TEXT("DA_Cladding07"))), TEXT("DA_Cladding07"));
    Surfaces.GetKeys(Data->SurfaceBones);
    Data->SurfaceBones.Sort();
    const int32 Core = ProtectCoarseCore(*C, *Data);
    int32 Links = 0, MaxSupports = 0, EdgeSupports = 0;
    for (auto& Tile : Data->Tiles)
    {
        Tile.SupportBones.Reset();
        const FVector Point = Tile.RestTransform.GetLocation();
        const FVector Normal = Tile.RestTransform.GetUnitAxis(EAxis::X);
        const FVector U = Tile.RestTransform.GetUnitAxis(EAxis::Y), V = Tile.RestTransform.GetUnitAxis(EAxis::Z);
        auto Project = [&](const FVector& P) { const FVector D = P - Point; return FVector2D(FVector::DotProduct(D, U), FVector::DotProduct(D, V)); };
        const FMeshDescription* Mesh = Tile.Mesh ? Tile.Mesh->GetMeshDescription(0) : nullptr;
        if (!Mesh) return TEXT("{\"error\":\"Missing tile source mesh\"}");
        const auto Positions = FStaticMeshConstAttributes(*Mesh).GetVertexPositions();
        TArray<FColumnTileTriangle> Footprint;
        FBox TileBounds(ForceInit);
        for (const FTriangleID ID : Mesh->Triangles().GetElementIDs())
        {
            const auto Vertices = Mesh->GetTriangleVertices(ID);
            FVector P[3];
            for (int32 J = 0; J < 3; ++J) P[J] = Tile.RestTransform.TransformPosition(FVector(Positions[Vertices[J]]));
            const FVector N = FVector::CrossProduct(P[1] - P[0], P[2] - P[0]).GetSafeNormal();
            if (FMath::Abs(FVector::DotProduct(N, Normal)) < .8) continue;
            FColumnTileTriangle T;
            for (int32 J = 0; J < 3; ++J) { T.P[J] = Project(P[J]); TileBounds += P[J]; }
            T.Bounds = FBox2D(T.P, 3);
            Footprint.Add(T);
        }
        if (Footprint.IsEmpty()) return TEXT("{\"error\":\"Missing tile footprint\"}");
        TileBounds = TileBounds.ExpandBy(4.);
        double Best = DBL_MAX;
        int32 Primary = INDEX_NONE;
        for (const auto& Pair : Surfaces)
        {
            if (!SurfaceBounds[Pair.Key].Intersect(TileBounds)) continue;
            bool bOverlap = false;
            for (const auto& T : Pair.Value)
            {
                if (FVector::DotProduct(T.Normal, Normal) < .8 || !T.Bounds.Intersect(TileBounds)) continue;
                const double Distance = FVector::DistSquared(Point, FMath::ClosestPointOnTriangleToPoint(Point, T.P[0], T.P[1], T.P[2]));
                if (Distance < Best) { Best = Distance; Primary = Pair.Key; }
                if (bOverlap) continue;
                FVector2D Projected[3] = {Project(T.P[0]), Project(T.P[1]), Project(T.P[2])};
                const FBox2D Bounds(Projected, 3);
                for (const auto& F : Footprint)
                    if (Bounds.Intersect(F.Bounds) && Overlap(Projected, F.P)) { bOverlap = true; break; }
            }
            if (bOverlap) Tile.SupportBones.Add(Pair.Key);
        }
        if (Primary == INDEX_NONE || (Tile.SupportBones.IsEmpty() && Best > 64.))
            return FString::Printf(TEXT("{\"error\":\"Tile has no concrete support\",\"tile\":%d,\"nearest_distance_sq\":%.9f}"), int32(&Tile - Data->Tiles.GetData()), Best);
        // The preserved facing wraps beyond the concrete's side/bottom bevel.
        // Tiny rim slivers need the nearest surface within 8 cm rather than a
        // positive-area intersection. Never accept a distant/unbacked tile.
        if (Tile.SupportBones.IsEmpty())
        {
            ++EdgeSupports;
            UE_LOG(LogTemp, Display, TEXT("DemoColumn07 edge tile=%d point=%s distance=%.3f area=%.3f"),
                int32(&Tile - Data->Tiles.GetData()), *Point.ToCompactString(), FMath::Sqrt(Best), Tile.AreaCm2);
        }
        Tile.SupportBones.AddUnique(Primary);
        Tile.SupportBones.Sort();
        Tile.Bone = Primary;
        Tile.RelativeToBone = Tile.RestTransform.GetRelativeTransform(Global[Primary]);
        Links += Tile.SupportBones.Num();
        MaxSupports = FMath::Max(MaxSupports, Tile.SupportBones.Num());
    }
    C->RemoveAttribute(FGeometryCollection::ExternalCollisionsAttribute, FGeometryCollection::TransformGroup);
    Asset->bImportCollisionFromSource = false;
    FGeometryCollectionConvexUtility::CreateNonOverlappingConvexHullData(C.Get(), .3, 1., .5);
    FGeometryCollectionConvexUtility::SetVolumeAttributes(C.Get());
    FGeometryCollectionProximityUtility(C.Get()).UpdateProximity();
    FGeometryCollectionProximityUtility(C.Get()).CopyProximityToConnectionGraph();
    auto* Heavy = NewObject<UPhysicalMaterial>(CreatePackage(*(Destination + TEXT("PM_HeavyConcrete07"))),
        TEXT("PM_HeavyConcrete07"), RF_Public | RF_Standalone);
    Heavy->Friction = .85f; Heavy->StaticFriction = .95f; Heavy->Restitution = .025f;
    Heavy->Density = 2.4f;
    Heavy->bOverrideFrictionCombineMode = true; Heavy->FrictionCombineMode = EFrictionCombineMode::Max;
    Heavy->bOverrideRestitutionCombineMode = true; Heavy->RestitutionCombineMode = EFrictionCombineMode::Min;
    Asset->PhysicsMaterial = Heavy;
    FAssetRegistryModule::AssetCreated(Heavy); Heavy->MarkPackageDirty();
    Asset->DamagePropagationData.bEnabled = false;
    Asset->bRemoveOnMaxSleep = false;
    Asset->InvalidateCollection();
    Asset->CreateSimulationData();
    Asset->RebuildRenderData();
    FAssetRegistryModule::AssetCreated(Asset);
    FAssetRegistryModule::AssetCreated(Data);
    Asset->MarkPackageDirty(); Data->MarkPackageDirty();
    TArray<double> Ratios;
    const auto Sizing = MakeShared<FJsonObject>();
    TArray<TSharedPtr<FJsonValue>> SourceRows;
    for (const int32 Original : CutSources)
    {
        const auto Row = MakeShared<FJsonObject>();
        Row->SetNumberField(TEXT("source_bone"), Original);
        Row->SetNumberField(TEXT("source_area_cm2"), Areas[Original]);
        TArray<TSharedPtr<FJsonValue>> Children;
        for (const auto& Pair : Surfaces)
        {
            if (SourceBone[Pair.Key] != Original) continue;
            double Area = 0.;
            for (const auto& T : Pair.Value) Area += FVector::CrossProduct(T.P[1]-T.P[0],T.P[2]-T.P[0]).Size()*.5;
            const double Ratio = FMath::Sqrt(Area / Areas[Original]); Ratios.Add(Ratio);
            const auto Child = MakeShared<FJsonObject>();
            Child->SetNumberField(TEXT("bone"), Pair.Key); Child->SetNumberField(TEXT("area_cm2"),Area);
            Child->SetNumberField(TEXT("linear_ratio"),Ratio); Children.Add(MakeShared<FJsonValueObject>(Child));
        }
        Row->SetArrayField(TEXT("children"), Children); SourceRows.Add(MakeShared<FJsonValueObject>(Row));
    }
    if (Ratios.IsEmpty()) return TEXT("{\"error\":\"No large pieces refined\"}");
    Ratios.Sort();
    Sizing->SetArrayField(TEXT("sources"),SourceRows);
    Sizing->SetNumberField(TEXT("cut_sources"),CutSources.Num());
    Sizing->SetNumberField(TEXT("median_linear_ratio"), Ratios[Ratios.Num()/2]);
    FString SizeJson; FJsonSerializer::Serialize(Sizing,TJsonWriterFactory<>::Create(&SizeJson));
    FFileHelper::SaveStringToFile(SizeJson, *(FPaths::ProjectSavedDir()/TEXT("DemoColumnExperiment07/sizing.json")));
    const FString Report = FString::Printf(TEXT("{\"original_leaves\":%d,\"geometries\":%d,\"faces\":%d,\"surface_bones\":%d,\"protected_core_bones\":%d,\"tiles\":%d,\"support_links\":%d,\"max_supports_per_tile\":%d,\"edge_slivers\":%d}"),
        OriginalLeaves, C->TransformIndex.Num(), C->Indices.Num(), Data->SurfaceBones.Num(), Core, Data->Tiles.Num(), Links, MaxSupports, EdgeSupports);
    FFileHelper::SaveStringToFile(Report, *(FPaths::ProjectSavedDir() / TEXT("DemoColumnExperiment07/authoring.json")));
    return Report;
#else
    return TEXT("{\"error\":\"Editor required\"}");
#endif
}

FString UNGDColumnAuthoring::BuildDemoColumnRefinement08()
{
#if WITH_EDITOR
    const FString Destination(TEXT("/Game/Experiments/DemoTiledColumn01/Correction08/"));
    if (FPackageName::DoesPackageExist(Destination + TEXT("GC_DemoColumn08"))) return TEXT("{\"error\":\"Candidate already exists\"}");
    auto* Source = LoadObject<UGeometryCollection>(nullptr, TEXT("/Game/Experiments/DemoTiledColumn01/Correction07/GC_DemoColumn07.GC_DemoColumn07"));
    auto* Facing = LoadObject<UDemoColumnCladdingData>(nullptr, TEXT("/Game/Experiments/DemoTiledColumn01/Correction07/DA_Cladding07.DA_Cladding07"));
    if (!Source || !Facing) return TEXT("{\"error\":\"Missing checkpoint assets\"}");
    auto* Asset = DuplicateObject<UGeometryCollection>(Source, CreatePackage(*(Destination + TEXT("GC_DemoColumn08"))), TEXT("GC_DemoColumn08"));
    auto C = Asset->GetGeometryCollection();
    TArray<FTransform> BeforeGlobal;
    GeometryCollectionAlgo::GlobalMatrices(C->Transform, C->Parent, BeforeGlobal);
    auto& SourceBone = C->AddAttribute<int32>(TEXT("DemoSourceBone"), FGeometryCollection::TransformGroup);
    for (int32 B = 0; B < C->Transform.Num(); ++B) SourceBone[B] = B;
    TMap<int32, double> Areas;
    for (int32 F = 0; F < C->Indices.Num(); ++F)
    {
        if (!C->Visible[F] || C->MaterialID[F] != 0) continue;
        const auto T = C->Indices[F]; const int32 B = C->BoneMap[T.X];
        const FVector A = BeforeGlobal[B].TransformPosition(FVector(C->Vertex[T.X]));
        const FVector D = BeforeGlobal[B].TransformPosition(FVector(C->Vertex[T.Y]));
        const FVector E = BeforeGlobal[B].TransformPosition(FVector(C->Vertex[T.Z]));
        const FVector Cross = FVector::CrossProduct(D-A,E-A);
        if (FMath::Abs(Cross.GetSafeNormal().Z) < .3) Areas.FindOrAdd(B) += Cross.Size() * .5;
    }
    TArray<int32> CutSources;
    for (const int32 B : Facing->SurfaceBones)
    {
        if (Areas.FindRef(B) < 3000.) continue;
        const int32 G = C->TransformToGeometryIndex[B];
        const FBox Box = C->BoundingBox[G].TransformBy(BeforeGlobal[B]);
        const FVector Size = Box.GetSize();
        struct FSample { FVector Position; double Area; };
        TArray<FSample> Samples;
        for (int32 F = C->FaceStart[G]; F < C->FaceStart[G] + C->FaceCount[G]; ++F)
        {
            if (C->MaterialID[F] != 0) continue;
            const auto T = C->Indices[F];
            const FVector A = BeforeGlobal[B].TransformPosition(FVector(C->Vertex[T.X]));
            const FVector D = BeforeGlobal[B].TransformPosition(FVector(C->Vertex[T.Y]));
            const FVector E = BeforeGlobal[B].TransformPosition(FVector(C->Vertex[T.Z]));
            const FVector Cross = FVector::CrossProduct(D-A,E-A);
            if (FMath::Abs(Cross.GetSafeNormal().Z) < .3) Samples.Add({(A+D+E)/3., Cross.Size()*.5});
        }
        // Choose an axis along the visible surface, not through its thickness.
        FVector Mean = FVector::ZeroVector, Variance = FVector::ZeroVector;
        for (const auto& Sample : Samples) Mean += Sample.Position * Sample.Area;
        Mean /= Areas[B];
        for (const auto& Sample : Samples)
        {
            const FVector Delta = Sample.Position - Mean;
            Variance += Delta * Delta * Sample.Area;
        }
        TArray<int32> Axes{0,1,2};
        Axes.Sort([&](int32 A, int32 D) { return Variance[A] > Variance[D]; });
        int32 Axis = INDEX_NONE;
        double Split = 0.;
        for (const int32 Candidate : Axes)
        {
            Samples.Sort([Candidate](const FSample& A, const FSample& D) { return A.Position[Candidate] < D.Position[Candidate]; });
            double Accumulated = 0.;
            for (const auto& Sample : Samples)
            {
                Accumulated += Sample.Area;
                if (Accumulated >= Areas[B]*.64) { Split = Sample.Position[Candidate]; break; }
            }
            // A corner's broad flat face can put the area quantile on a boundary.
            // Try the next surface axis rather than cut off a zero-width sliver.
            if (Split > Box.Min[Candidate]+Size[Candidate]*.02 && Split < Box.Max[Candidate]-Size[Candidate]*.02)
            { Axis = Candidate; break; }
        }
        if (Axis == INDEX_NONE) return FString::Printf(TEXT("{\"error\":\"Cut has no interior surface span\",\"bone\":%d}"),B);
        FVector P = Box.GetCenter(); P[Axis] = Split;
        FVector Offset = FVector::ZeroVector; Offset[Axis] = .45 * FMath::Min(Split-Box.Min[Axis],Box.Max[Axis]-Split);
        TArray<FVector> Sites{P-Offset, P+Offset};
        FVoronoiDiagram Diagram(Sites, Box, 1.);
        FPlanarCells Cells(Sites, Diagram);
        Cells.InternalSurfaceMaterials.GlobalMaterialID = 1;
        Cells.InternalSurfaceMaterials.GlobalUVScale = .01f;
        const int32 OldCount = C->Transform.Num();
        CutWithPlanarCells(Cells, *C, B, 0., 0., 280908+B, {}, true, false,
            nullptr, FVector::ZeroVector, FIslandSplitSettings(false));
        if (C->Transform.Num() != OldCount + 2) return TEXT("{\"error\":\"Large fragment did not split into two pieces\"}");
        for (int32 New = OldCount; New < C->Transform.Num(); ++New) SourceBone[New] = B;
        CutSources.Add(B);
    }
    const int32 OriginalLeaves = 874;
    TArray<int32> Leaves;
    for (int32 B = 0; B < C->Transform.Num(); ++B)
        if (C->SimulationType[B] == FGeometryCollection::FST_Rigid && C->Children[B].IsEmpty())
        {
            Leaves.Add(B);
        }

    // Retain the unsplit fragments and flatten the new two-piece cuts. Remove
    // hierarchy levels that used to consume hits before a visible piece released.
    FGeometryCollectionClusteringUtility::UpdateHierarchyLevelOfChildren(C.Get(), -1);
    FGeometryCollectionClusteringUtility::ClusterBonesUnderExistingRoot(C.Get(), Leaves);
    FGeometryCollectionClusteringUtility::RemoveDanglingClusters(C.Get());
    FGeometryCollectionClusteringUtility::UpdateHierarchyLevelOfChildren(C.Get(), -1);
    TArray<int32> HiddenGeometry;
    for (int32 G = 0; G < C->TransformIndex.Num(); ++G)
        if (C->SimulationType[C->TransformIndex[G]] != FGeometryCollection::FST_Rigid) HiddenGeometry.Add(G);
    if (HiddenGeometry.Num()) C->RemoveElements(FGeometryCollection::GeometryGroup, HiddenGeometry);
    if (C->TransformIndex.Num() != OriginalLeaves + CutSources.Num())
        return TEXT("{\"error\":\"Unexpected refined topology\"}");

    TArray<FTransform> Global;
    GeometryCollectionAlgo::GlobalMatrices(C->Transform, C->Parent, Global);
    TMap<int32, TArray<FColumnSurfaceTriangle>> Surfaces;
    TMap<int32, FBox> SurfaceBounds;
    for (int32 F = 0; F < C->Indices.Num(); ++F)
    {
        if (!C->Visible[F] || C->MaterialID[F] != 0) continue;
        const auto T = C->Indices[F];
        const int32 B = C->BoneMap[T.X];
        FColumnSurfaceTriangle Triangle;
        Triangle.P[0] = Global[B].TransformPosition(FVector(C->Vertex[T.X]));
        Triangle.P[1] = Global[B].TransformPosition(FVector(C->Vertex[T.Y]));
        Triangle.P[2] = Global[B].TransformPosition(FVector(C->Vertex[T.Z]));
        Triangle.Normal = -FVector::CrossProduct(Triangle.P[1] - Triangle.P[0], Triangle.P[2] - Triangle.P[0]).GetSafeNormal();
        if (Triangle.Normal.IsNearlyZero() || FMath::Abs(Triangle.Normal.Z) > .3) continue;
        Triangle.Bounds = FBox(Triangle.P, 3);
        Surfaces.FindOrAdd(B).Add(Triangle);
        auto* Bounds = SurfaceBounds.Find(B);
        if (Bounds) *Bounds += Triangle.Bounds; else SurfaceBounds.Add(B, Triangle.Bounds);
    }
    auto* Data = DuplicateObject<UDemoColumnCladdingData>(Facing, CreatePackage(*(Destination + TEXT("DA_Cladding08"))), TEXT("DA_Cladding08"));
    Surfaces.GetKeys(Data->SurfaceBones);
    Data->SurfaceBones.Sort();
    const int32 Core = ProtectCoarseCore(*C, *Data);
    int32 Links = 0, MaxSupports = 0, EdgeSupports = 0;
    for (auto& Tile : Data->Tiles)
    {
        Tile.SupportBones.Reset();
        const FVector Point = Tile.RestTransform.GetLocation();
        const FVector Normal = Tile.RestTransform.GetUnitAxis(EAxis::X);
        const FVector U = Tile.RestTransform.GetUnitAxis(EAxis::Y), V = Tile.RestTransform.GetUnitAxis(EAxis::Z);
        auto Project = [&](const FVector& P) { const FVector D = P - Point; return FVector2D(FVector::DotProduct(D, U), FVector::DotProduct(D, V)); };
        const FMeshDescription* Mesh = Tile.Mesh ? Tile.Mesh->GetMeshDescription(0) : nullptr;
        if (!Mesh) return TEXT("{\"error\":\"Missing tile source mesh\"}");
        const auto Positions = FStaticMeshConstAttributes(*Mesh).GetVertexPositions();
        TArray<FColumnTileTriangle> Footprint;
        FBox TileBounds(ForceInit);
        for (const FTriangleID ID : Mesh->Triangles().GetElementIDs())
        {
            const auto Vertices = Mesh->GetTriangleVertices(ID);
            FVector P[3];
            for (int32 J = 0; J < 3; ++J) P[J] = Tile.RestTransform.TransformPosition(FVector(Positions[Vertices[J]]));
            const FVector N = FVector::CrossProduct(P[1] - P[0], P[2] - P[0]).GetSafeNormal();
            if (FMath::Abs(FVector::DotProduct(N, Normal)) < .8) continue;
            FColumnTileTriangle T;
            for (int32 J = 0; J < 3; ++J) { T.P[J] = Project(P[J]); TileBounds += P[J]; }
            T.Bounds = FBox2D(T.P, 3);
            Footprint.Add(T);
        }
        if (Footprint.IsEmpty()) return TEXT("{\"error\":\"Missing tile footprint\"}");
        TileBounds = TileBounds.ExpandBy(4.);
        double Best = DBL_MAX;
        int32 Primary = INDEX_NONE;
        for (const auto& Pair : Surfaces)
        {
            if (!SurfaceBounds[Pair.Key].Intersect(TileBounds)) continue;
            bool bOverlap = false;
            for (const auto& T : Pair.Value)
            {
                if (FVector::DotProduct(T.Normal, Normal) < .8 || !T.Bounds.Intersect(TileBounds)) continue;
                const double Distance = FVector::DistSquared(Point, FMath::ClosestPointOnTriangleToPoint(Point, T.P[0], T.P[1], T.P[2]));
                if (Distance < Best) { Best = Distance; Primary = Pair.Key; }
                if (bOverlap) continue;
                FVector2D Projected[3] = {Project(T.P[0]), Project(T.P[1]), Project(T.P[2])};
                const FBox2D Bounds(Projected, 3);
                for (const auto& F : Footprint)
                    if (Bounds.Intersect(F.Bounds) && Overlap(Projected, F.P)) { bOverlap = true; break; }
            }
            if (bOverlap) Tile.SupportBones.Add(Pair.Key);
        }
        if (Primary == INDEX_NONE || (Tile.SupportBones.IsEmpty() && Best > 64.))
            return FString::Printf(TEXT("{\"error\":\"Tile has no concrete support\",\"tile\":%d,\"nearest_distance_sq\":%.9f}"), int32(&Tile - Data->Tiles.GetData()), Best);
        // The preserved facing wraps beyond the concrete's side/bottom bevel.
        // Tiny rim slivers need the nearest surface within 8 cm rather than a
        // positive-area intersection. Never accept a distant/unbacked tile.
        if (Tile.SupportBones.IsEmpty())
        {
            ++EdgeSupports;
            UE_LOG(LogTemp, Display, TEXT("DemoColumn08 edge tile=%d point=%s distance=%.3f area=%.3f"),
                int32(&Tile - Data->Tiles.GetData()), *Point.ToCompactString(), FMath::Sqrt(Best), Tile.AreaCm2);
        }
        Tile.SupportBones.AddUnique(Primary);
        Tile.SupportBones.Sort();
        Tile.Bone = Primary;
        Tile.RelativeToBone = Tile.RestTransform.GetRelativeTransform(Global[Primary]);
        Links += Tile.SupportBones.Num();
        MaxSupports = FMath::Max(MaxSupports, Tile.SupportBones.Num());
    }
    C->RemoveAttribute(FGeometryCollection::ExternalCollisionsAttribute, FGeometryCollection::TransformGroup);
    Asset->bImportCollisionFromSource = false;
    FGeometryCollectionConvexUtility::CreateNonOverlappingConvexHullData(C.Get(), .3, 1., .5);
    FGeometryCollectionConvexUtility::SetVolumeAttributes(C.Get());
    FGeometryCollectionProximityUtility(C.Get()).UpdateProximity();
    FGeometryCollectionProximityUtility(C.Get()).CopyProximityToConnectionGraph();
    auto* Heavy = NewObject<UPhysicalMaterial>(CreatePackage(*(Destination + TEXT("PM_HeavyConcrete08"))),
        TEXT("PM_HeavyConcrete08"), RF_Public | RF_Standalone);
    Heavy->Friction = .85f; Heavy->StaticFriction = .95f; Heavy->Restitution = .025f;
    Heavy->Density = 2.4f;
    Heavy->bOverrideFrictionCombineMode = true; Heavy->FrictionCombineMode = EFrictionCombineMode::Max;
    Heavy->bOverrideRestitutionCombineMode = true; Heavy->RestitutionCombineMode = EFrictionCombineMode::Min;
    Asset->PhysicsMaterial = Heavy;
    FAssetRegistryModule::AssetCreated(Heavy); Heavy->MarkPackageDirty();
    Asset->DamagePropagationData.bEnabled = false;
    Asset->bRemoveOnMaxSleep = false;
    Asset->InvalidateCollection();
    Asset->CreateSimulationData();
    Asset->RebuildRenderData();
    FAssetRegistryModule::AssetCreated(Asset);
    FAssetRegistryModule::AssetCreated(Data);
    Asset->MarkPackageDirty(); Data->MarkPackageDirty();
    TArray<double> Ratios, LargestRatios;
    const auto Sizing = MakeShared<FJsonObject>();
    TArray<TSharedPtr<FJsonValue>> SourceRows;
    for (const int32 Original : CutSources)
    {
        const auto Row = MakeShared<FJsonObject>();
        Row->SetNumberField(TEXT("source_bone"), Original);
        Row->SetNumberField(TEXT("source_area_cm2"), Areas[Original]);
        TArray<TSharedPtr<FJsonValue>> Children;
        double Largest = 0.;
        for (const auto& Pair : Surfaces)
        {
            if (SourceBone[Pair.Key] != Original) continue;
            double Area = 0.;
            for (const auto& T : Pair.Value) Area += FVector::CrossProduct(T.P[1]-T.P[0],T.P[2]-T.P[0]).Size()*.5;
            const double Ratio = FMath::Sqrt(Area / Areas[Original]); Ratios.Add(Ratio); Largest = FMath::Max(Largest,Ratio);
            const auto Child = MakeShared<FJsonObject>();
            Child->SetNumberField(TEXT("bone"), Pair.Key); Child->SetNumberField(TEXT("area_cm2"),Area);
            Child->SetNumberField(TEXT("linear_ratio"),Ratio); Children.Add(MakeShared<FJsonValueObject>(Child));
        }
        LargestRatios.Add(Largest);
        Row->SetArrayField(TEXT("children"), Children); SourceRows.Add(MakeShared<FJsonValueObject>(Row));
    }
    if (Ratios.IsEmpty()) return TEXT("{\"error\":\"No large pieces refined\"}");
    Ratios.Sort(); LargestRatios.Sort();
    Sizing->SetNumberField(TEXT("median_largest_ratio"),LargestRatios[LargestRatios.Num()/2]);
    Sizing->SetArrayField(TEXT("sources"),SourceRows);
    Sizing->SetNumberField(TEXT("cut_sources"),CutSources.Num());
    Sizing->SetNumberField(TEXT("median_linear_ratio"), Ratios[Ratios.Num()/2]);
    FString SizeJson; FJsonSerializer::Serialize(Sizing,TJsonWriterFactory<>::Create(&SizeJson));
    FFileHelper::SaveStringToFile(SizeJson, *(FPaths::ProjectSavedDir()/TEXT("DemoColumnExperiment08/sizing.json")));
    const FString Report = FString::Printf(TEXT("{\"original_leaves\":%d,\"geometries\":%d,\"faces\":%d,\"surface_bones\":%d,\"protected_core_bones\":%d,\"tiles\":%d,\"support_links\":%d,\"max_supports_per_tile\":%d,\"edge_slivers\":%d}"),
        OriginalLeaves, C->TransformIndex.Num(), C->Indices.Num(), Data->SurfaceBones.Num(), Core, Data->Tiles.Num(), Links, MaxSupports, EdgeSupports);
    FFileHelper::SaveStringToFile(Report, *(FPaths::ProjectSavedDir() / TEXT("DemoColumnExperiment08/authoring.json")));
    return Report;
#else
    return TEXT("{\"error\":\"Editor required\"}");
#endif
}
