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
