#include "NGDColumnAuthoring.h"
#include "DemoColumnCladding.h"

#if WITH_EDITOR
#include "AssetRegistry/AssetRegistryModule.h"
#include "Chaos/ImplicitObject.h"
#include "GeometryCollection/GeometryCollectionObject.h"
#include "GeometryCollection/GeometryCollection.h"
#include "GeometryCollection/GeometryCollectionAlgo.h"
#include "GeometryCollection/GeometryCollectionClusteringUtility.h"
#include "GeometryCollection/GeometryCollectionConvexUtility.h"
#include "GeometryCollection/GeometryCollectionProximityUtility.h"
#include "PlanarCut.h"
#include "Voronoi/Voronoi.h"
#include "Misc/PackageName.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/Package.h"
#endif

FString UNGDColumnAuthoring::BuildDemoColumnSurface()
{
#if WITH_EDITOR
    const FString Destination(TEXT("/Game/Experiments/DemoTiledColumn01/Correction05/"));
    if (FPackageName::DoesPackageExist(Destination + TEXT("GC_DemoColumn05")))
        return TEXT("{\"error\":\"Candidate already exists\"}");
    auto* Source = LoadObject<UGeometryCollection>(nullptr, TEXT("/Game/Experiments/DemoTiledColumn01/Correction03/GC_DemoColumn03.GC_DemoColumn03"));
    auto* Facing = LoadObject<UDemoColumnCladdingData>(nullptr, TEXT("/Game/Experiments/DemoTiledColumn01/Correction04/DA_Cladding04.DA_Cladding04"));
    if (!Source || !Facing) return TEXT("{\"error\":\"Missing checkpoint assets\"}");
    auto* Asset = DuplicateObject<UGeometryCollection>(Source, CreatePackage(*(Destination + TEXT("GC_DemoColumn05"))), TEXT("GC_DemoColumn05"));
    auto C = Asset->GetGeometryCollection();
    TArray<FTransform> Global;
    GeometryCollectionAlgo::GlobalMatrices(C->Transform, C->Parent, Global);
    struct FSurface { FVector A, B, D, Normal; };
    TMap<int32, TArray<FSurface>> Surfaces;
    TMap<int32, double> Areas;
    for (int32 F = 0; F < C->Indices.Num(); ++F)
    {
        if (!C->Visible[F] || C->MaterialID[F] != 0) continue;
        const auto T = C->Indices[F];
        const int32 Bone = C->BoneMap[T.X];
        if (C->SimulationType[Bone] != FGeometryCollection::FST_Rigid) continue;
        const FVector A = Global[Bone].TransformPosition(FVector(C->Vertex[T.X]));
        const FVector B = Global[Bone].TransformPosition(FVector(C->Vertex[T.Y]));
        const FVector D = Global[Bone].TransformPosition(FVector(C->Vertex[T.Z]));
        const FVector Cross = FVector::CrossProduct(B - A, D - A);
        // GeometryCollection faces use Unreal's clockwise exterior winding.
        const FVector Normal = -Cross.GetSafeNormal();
        if (FMath::Abs(Normal.Z) > .3f) continue;
        Surfaces.FindOrAdd(Bone).Add({A, B, D, Normal});
        Areas.FindOrAdd(Bone) += Cross.Size() * .5;
    }
    TArray<int32> Originals;
    Surfaces.GetKeys(Originals);
    Originals.Sort();
    const int32 OriginalTransforms = C->Transform.Num();
    int32 CutCount = 0;
    for (const int32 Bone : Originals)
    {
        if (Areas[Bone] < 900.) continue;
        const auto& Triangles = Surfaces[Bone];
        const int32 Geometry = C->TransformToGeometryIndex[Bone];
        if (Geometry == INDEX_NONE) continue;
        const FBox Bounds = C->BoundingBox[Geometry].TransformBy(Global[Bone]);
        FRandomStream Random(280905 + Bone * 113);
        TArray<FVector> Sites;
        // Dense sites live only near the four exterior faces. Coarse interior
        // sites retain deeper chunks; this is not uniform whole-column shattering.
        for (int32 Face = 0; Face < 4; ++Face)
        {
            const int32 Axis = Face / 2;
            const int32 Tangent = 1 - Axis;
            const double Sign = Face % 2 ? -1. : 1.;
            FVector Normal = FVector::ZeroVector;
            Normal[Axis] = Sign;
            for (double Z = FMath::FloorToDouble(Bounds.Min.Z / 30.) * 30. + 15.; Z <= Bounds.Max.Z + 15.; Z += 30.)
                for (double U = FMath::FloorToDouble(Bounds.Min[Tangent] / 30.) * 30. + 15.; U <= Bounds.Max[Tangent] + 15.; U += 30.)
                {
                    FVector Sample = FVector::ZeroVector;
                    Sample[Axis] = Sign * 118.2;
                    Sample[Tangent] = U + Random.FRandRange(-6.f, 6.f);
                    Sample.Z = Z + Random.FRandRange(-6.f, 6.f);
                    double Best = FMath::Square(16.);
                    FVector Nearest;
                    bool Found = false;
                    for (const auto& T : Triangles)
                    {
                        if (FVector::DotProduct(T.Normal, Normal) < .8) continue;
                        const FVector P = FMath::ClosestPointOnTriangleToPoint(Sample, T.A, T.B, T.D);
                        const double Distance = FVector::DistSquared(Sample, P);
                        if (Distance < Best) { Best = Distance; Nearest = P; Found = true; }
                    }
                    if (!Found) continue;
                    const FVector Site = Nearest - Normal * Random.FRandRange(6.f, 12.f);
                    if (!Sites.ContainsByPredicate([&](const FVector& P) { return FVector::DistSquared(P, Site) < 15. * 15.; }))
                        Sites.Add(Site);
                }
        }
        if (Sites.Num() < 2) continue;
        const int32 SurfaceSites = Sites.Num();
        for (int32 I = 0; I < SurfaceSites; ++I)
        {
            FVector Coarse = Sites[I];
            const int32 Axis = FMath::Abs(Coarse.X) > FMath::Abs(Coarse.Y) ? 0 : 1;
            Coarse[Axis] -= FMath::Sign(Coarse[Axis]) * 48.;
            if (!Sites.ContainsByPredicate([&](const FVector& P) { return FVector::DistSquared(P, Coarse) < 65. * 65.; })) Sites.Add(Coarse);
        }
        Sites.Add(Bounds.GetCenter());
        FVoronoiDiagram Diagram(Sites, Bounds, 1.0);
        FPlanarCells Cells(Sites, Diagram);
        Cells.InternalSurfaceMaterials.GlobalMaterialID = 1;
        Cells.InternalSurfaceMaterials.GlobalUVScale = .01f;
        const int32 OldCount = C->Transform.Num();
        CutWithPlanarCells(Cells, *C, Bone, 0., 0., 280905 + Bone, {}, true, false,
            nullptr, FVector::ZeroVector, FIslandSplitSettings(false));
        if (C->Transform.Num() > OldCount)
        {
            ++CutCount;
            for (int32 New = OldCount; New < C->Transform.Num(); ++New)
                C->InitialDynamicState[New] = C->InitialDynamicState[Bone];
        }
        if (CutCount % 25 == 0) UE_LOG(LogTemp, Display, TEXT("DemoColumn05 author cut=%d transforms=%d"), CutCount, C->Transform.Num());
    }
    TArray<int32> Leaves;
    for (int32 B = 0; B < C->Transform.Num(); ++B)
        if (C->SimulationType[B] == FGeometryCollection::FST_Rigid && C->Children[B].IsEmpty()) Leaves.Add(B);
    // A rifle impact can release a leaf directly from the live root/internal
    // remainder cluster without spending earlier shots opening hierarchy levels.
    FGeometryCollectionClusteringUtility::UpdateHierarchyLevelOfChildren(C.Get(), -1);
    FGeometryCollectionClusteringUtility::ClusterBonesUnderExistingRoot(C.Get(), Leaves);
    FGeometryCollectionClusteringUtility::RemoveDanglingClusters(C.Get());
    FGeometryCollectionClusteringUtility::UpdateHierarchyLevelOfChildren(C.Get(), -1);
    GeometryCollectionAlgo::GlobalMatrices(C->Transform, C->Parent, Global);
    TArray<int32> HiddenGeometry;
    for (int32 G = 0; G < C->TransformIndex.Num(); ++G)
        if (C->SimulationType[C->TransformIndex[G]] != FGeometryCollection::FST_Rigid) HiddenGeometry.Add(G);
    if (HiddenGeometry.Num()) C->RemoveElements(FGeometryCollection::GeometryGroup, HiddenGeometry);
    C->RemoveAttribute(FGeometryCollection::ExternalCollisionsAttribute, FGeometryCollection::TransformGroup);
    Asset->bImportCollisionFromSource = false;
    // Recompute candidate hulls from its current geometry, never the pre-cut
    // parent collision. One hull per leaf is adequate for these bounded chips.
    FGeometryCollectionConvexUtility::CreateNonOverlappingConvexHullData(C.Get(), .3, 1., .5);
    FGeometryCollectionConvexUtility::SetVolumeAttributes(C.Get());
    FGeometryCollectionProximityUtility(C.Get()).UpdateProximity();
    FGeometryCollectionProximityUtility(C.Get()).CopyProximityToConnectionGraph();
    TMap<int32, TArray<FSurface>> FinalSurfaces;
    for (int32 F = 0; F < C->Indices.Num(); ++F)
    {
        if (!C->Visible[F] || C->MaterialID[F] != 0) continue;
        const auto T = C->Indices[F];
        const int32 B = C->BoneMap[T.X];
        if (C->SimulationType[B] != FGeometryCollection::FST_Rigid) continue;
        const FVector A = Global[B].TransformPosition(FVector(C->Vertex[T.X]));
        const FVector D = Global[B].TransformPosition(FVector(C->Vertex[T.Z]));
        const FVector V = Global[B].TransformPosition(FVector(C->Vertex[T.Y]));
        const FVector N = -FVector::CrossProduct(V - A, D - A).GetSafeNormal();
        if (FMath::Abs(N.Z) > .3f) continue;
        FinalSurfaces.FindOrAdd(B).Add({A, V, D, N});
        // Surface skin remains shootable even above an originally anchored
        // vendor chunk. Original deeper support particles stay anchored.
        C->InitialDynamicState[B] = int32(Chaos::EObjectStateType::Dynamic);
    }
    auto* Data = DuplicateObject<UDemoColumnCladdingData>(Facing, CreatePackage(*(Destination + TEXT("DA_Cladding05"))), TEXT("DA_Cladding05"));
    for (auto& Tile : Data->Tiles)
    {
        const FVector Point = Tile.RestTransform.GetLocation();
        const FVector Normal = Tile.RestTransform.GetUnitAxis(EAxis::X);
        double Best = TNumericLimits<double>::Max();
        int32 BestBone = INDEX_NONE;
        for (const auto& Pair : FinalSurfaces)
            for (const auto& T : Pair.Value)
            {
                if (FVector::DotProduct(Normal, T.Normal) < .8) continue;
                const double D = FVector::DistSquared(Point, FMath::ClosestPointOnTriangleToPoint(Point, T.A, T.B, T.D));
                if (D < Best) { Best = D; BestBone = Pair.Key; }
            }
        if (BestBone == INDEX_NONE) return TEXT("{\"error\":\"Missing facing support\"}");
        Tile.Bone = BestBone;
        Tile.RelativeToBone = Tile.RestTransform.GetRelativeTransform(Global[BestBone]);
    }
    Asset->DamagePropagationData.bEnabled = false;
    Asset->bRemoveOnMaxSleep = false;
    Asset->InvalidateCollection();
    Asset->CreateSimulationData();
    Asset->RebuildRenderData();
    FAssetRegistryModule::AssetCreated(Asset);
    FAssetRegistryModule::AssetCreated(Data);
    Asset->MarkPackageDirty();
    Data->MarkPackageDirty();
    const FString Report = FString::Printf(TEXT("{\"original_transforms\":%d,\"cut_leaves\":%d,\"transforms\":%d,\"geometries\":%d,\"faces\":%d,\"tiles\":%d,\"surface_bones\":%d}"),
        OriginalTransforms, CutCount, C->Transform.Num(), C->TransformIndex.Num(), C->Indices.Num(), Data->Tiles.Num(), FinalSurfaces.Num());
    FFileHelper::SaveStringToFile(Report, *(FPaths::ProjectSavedDir() / TEXT("DemoColumnExperiment05/authoring.json")));
    return Report;
#else
    return TEXT("{\"error\":\"Editor required\"}");
#endif
}
