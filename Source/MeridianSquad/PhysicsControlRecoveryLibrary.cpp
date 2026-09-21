#include "PhysicsControlRecoveryLibrary.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/SkeletalBodySetup.h"
#include "PhysicsEngine/PhysicsConstraintTemplate.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "Serialization/JsonSerializer.h"

namespace
{
TSharedPtr<FJsonValue> VectorJson(const FVector& V)
{
    return MakeShared<FJsonValueArray>(TArray<TSharedPtr<FJsonValue>>{
        MakeShared<FJsonValueNumber>(V.X), MakeShared<FJsonValueNumber>(V.Y), MakeShared<FJsonValueNumber>(V.Z)});
}
FString JsonText(TSharedPtr<FJsonObject> Root)
{
    FString Result;
    FJsonSerializer::Serialize(Root.ToSharedRef(), TJsonWriterFactory<>::Create(&Result));
    return Result;
}
}

FString UPhysicsControlRecoveryLibrary::AuditAsset(UPhysicsAsset* Asset)
{
    auto Root = MakeShared<FJsonObject>();
    if (!Asset) return JsonText(Root);
    Root->SetStringField(TEXT("asset"), Asset->GetPathName());
    TArray<TSharedPtr<FJsonValue>> Bodies, Exclusions, Joints;
    for (const auto& Setup : Asset->SkeletalBodySetups)
    {
        auto Row = MakeShared<FJsonObject>();
        Row->SetStringField(TEXT("bone"), Setup->BoneName.ToString());
        Row->SetNumberField(TEXT("collision_enabled"), static_cast<int32>(Setup->DefaultInstance.GetCollisionEnabled()));
        TArray<TSharedPtr<FJsonValue>> Shapes;
        auto ShapeRow = [&](const FKShapeElem& Shape, const FTransform& Transform, FVector Dimensions)
        {
            auto S = MakeShared<FJsonObject>();
            S->SetNumberField(TEXT("type"), static_cast<int32>(Shape.GetShapeType()));
            S->SetField(TEXT("center"), VectorJson(Transform.GetLocation()));
            S->SetField(TEXT("rotation"), VectorJson(Transform.Rotator().Euler()));
            S->SetField(TEXT("dimensions"), VectorJson(Dimensions));
            Shapes.Add(MakeShared<FJsonValueObject>(S));
        };
        for (const auto& S : Setup->AggGeom.SphylElems) ShapeRow(S, S.GetTransform(), FVector(S.Radius, S.Length, 0));
        for (const auto& S : Setup->AggGeom.SphereElems) ShapeRow(S, S.GetTransform(), FVector(S.Radius, 0, 0));
        for (const auto& S : Setup->AggGeom.BoxElems) ShapeRow(S, S.GetTransform(), FVector(S.X, S.Y, S.Z));
        Row->SetArrayField(TEXT("shapes"), Shapes);
        Bodies.Add(MakeShared<FJsonValueObject>(Row));
    }
    for (const auto& Pair : Asset->CollisionDisableTable)
    {
        auto Row = MakeShared<FJsonObject>();
        Row->SetStringField(TEXT("a"), Asset->SkeletalBodySetups[Pair.Key.Indices[0]]->BoneName.ToString());
        Row->SetStringField(TEXT("b"), Asset->SkeletalBodySetups[Pair.Key.Indices[1]]->BoneName.ToString());
        Exclusions.Add(MakeShared<FJsonValueObject>(Row));
    }
    for (const auto& Template : Asset->ConstraintSetup)
    {
        const auto& Joint = Template->DefaultInstance;
        auto Row = MakeShared<FJsonObject>();
        Row->SetStringField(TEXT("child"), Joint.ConstraintBone1.ToString());
        Row->SetStringField(TEXT("parent"), Joint.ConstraintBone2.ToString());
        Row->SetBoolField(TEXT("disable_collision"), Joint.ProfileInstance.bDisableCollision);
        Row->SetField(TEXT("angular_limits"), VectorJson(FVector(Joint.GetAngularSwing1Limit(), Joint.GetAngularSwing2Limit(), Joint.GetAngularTwistLimit())));
        Joints.Add(MakeShared<FJsonValueObject>(Row));
    }
    Root->SetArrayField(TEXT("bodies"), Bodies);
    Root->SetArrayField(TEXT("excluded_pairs"), Exclusions);
    Root->SetArrayField(TEXT("joints"), Joints);
    return JsonText(Root);
}

TArray<FDummySoleVertex> UPhysicsControlRecoveryLibrary::FootVertices(USkeletalMeshComponent* Mesh)
{
    TArray<FDummySoleVertex> Result;
    if (!Mesh || !Mesh->GetSkeletalMeshAsset()) return Result;
    const auto* Data = Mesh->GetSkeletalMeshRenderData();
    const auto& LOD = Data->LODRenderData[0];
    const auto* Weights = Mesh->GetSkinWeightBuffer(0);
    TArray<FMatrix44f> Matrices;
    Mesh->GetCurrentRefToLocalMatrices(Matrices, 0);
    TArray<FVector3f> Positions;
    USkinnedMeshComponent::ComputeSkinnedPositions(Mesh, Positions, Matrices, LOD, *Weights);
    const auto& Ref = Mesh->GetSkeletalMeshAsset()->GetRefSkeleton();
    for (const auto& Section : LOD.RenderSections)
        for (uint32 V = Section.BaseVertexIndex; V < Section.BaseVertexIndex + Section.NumVertices; ++V)
        {
            int32 MaxWeight = -1, Bone = 0;
            for (uint32 I = 0; I < Weights->GetMaxBoneInfluences(); ++I)
                if (int32(Weights->GetBoneWeight(V, I)) > MaxWeight)
                { MaxWeight = Weights->GetBoneWeight(V, I); Bone = Section.BoneMap[Weights->GetBoneIndex(V, I)]; }
            const FString Name = Ref.GetBoneName(Bone).ToString();
            if (!(Name.StartsWith(TEXT("foot")) || Name.StartsWith(TEXT("ball")))) continue;
            const FVector World = Mesh->GetComponentTransform().TransformPosition(FVector(Positions[V]));
            Result.Add({V, Ref.GetBoneName(Bone), World, Mesh->GetBoneTransform(Bone).InverseTransformPosition(World)});
        }
    return Result;
}

FString UPhysicsControlRecoveryLibrary::AuditSkin(USkeletalMeshComponent* Mesh)
{
    auto Root = MakeShared<FJsonObject>();
    if (!Mesh || !Mesh->GetSkeletalMeshAsset()) return JsonText(Root);
    TArray<TSharedPtr<FJsonValue>> Rows;
    for (const auto& Vertex : FootVertices(Mesh))
    {
        auto Row = MakeShared<FJsonObject>();
        Row->SetNumberField(TEXT("vertex"), Vertex.Index);
        Row->SetStringField(TEXT("bone"), Vertex.Bone.ToString());
        Row->SetField(TEXT("world"), VectorJson(Vertex.World));
        Row->SetField(TEXT("bone_local"), VectorJson(Vertex.Local));
        Rows.Add(MakeShared<FJsonValueObject>(Row));
    }
    Root->SetArrayField(TEXT("foot_vertices"), Rows);
    Root->SetNumberField(TEXT("skeleton_bones"), Mesh->GetSkeletalMeshAsset()->GetRefSkeleton().GetNum());
    Root->SetNumberField(TEXT("render_vertices"), Mesh->GetSkeletalMeshRenderData()->LODRenderData[0].GetNumVertices());
    return JsonText(Root);
}

bool UPhysicsControlRecoveryLibrary::ConfigureAsset(UPhysicsAsset* Asset)
{
#if WITH_EDITOR
    // Never author the shared mannequin asset, including through this audit seam.
    if (!Asset || !Asset->GetPathName().StartsWith(TEXT("/Game/Development/PhysicsControlRecovery01/"))) return false;
    Asset->Modify();
    // Retain all existing non-adjacent collisions and adjacent exclusions.
    // The shoulder capsules overlap the chest at their attachment, so the upper
    // arm/chest pair remains excluded. Forearms/hands block every trunk segment.
    for (const TCHAR* Arm : {TEXT("lowerarm_l"),TEXT("lowerarm_r"),TEXT("hand_l"),TEXT("hand_r")})
        for (const TCHAR* Trunk : {TEXT("pelvis"),TEXT("spine_02"),TEXT("spine_03"),TEXT("spine_04"),TEXT("spine_05")})
            Asset->EnableCollision(Asset->FindBodyIndex(Arm), Asset->FindBodyIndex(Trunk));
    for (const auto& Setup : Asset->SkeletalBodySetups)
    {
        if (Setup->BoneName == TEXT("foot_l") || Setup->BoneName == TEXT("foot_r"))
        {
            Setup->Modify();
            // Manny's local foot X is vertical: measured sole extent is 7.78 cm
            // from the ankle; a 7.0 cm box at +/-4.4 places its face at 7.9 cm.
            for (auto& Box : Setup->AggGeom.BoxElems) Box.X = 7.f;
            Setup->InvalidatePhysicsData();
            Setup->CreatePhysicsMeshes();
        }
    }
    Asset->MarkPackageDirty();
    return true;
#else
    return false;
#endif
}

bool UPhysicsControlRecoveryLibrary::ConfigureGASPAsset(UPhysicsAsset* Asset, USkeletalMeshComponent* Mesh)
{
#if WITH_EDITOR
    if (!Asset || !Mesh || !Asset->GetPathName().StartsWith(TEXT("/GASPEnemyFoundation01/"))) return false;
    const auto Vertices = FootVertices(Mesh);
    if (Vertices.IsEmpty()) return false;
    Asset->Modify();
    for (FName Foot : {FName("foot_l"), FName("foot_r")})
    {
        const int32 Index = Asset->FindBodyIndex(Foot);
        if (Index == INDEX_NONE) return false;
        const FString Side = Foot == TEXT("foot_l") ? TEXT("_l") : TEXT("_r");
        FBox Bounds(ForceInit);
        for (const auto& Vertex : Vertices)
            if (Vertex.Bone.ToString().EndsWith(Side))
                Bounds += Mesh->GetComponentTransform().InverseTransformPosition(Vertex.World);
        if (!Bounds.IsValid) return false;
        auto* Setup = Asset->SkeletalBodySetups[Index].Get();
        Setup->Modify();
        Setup->AggGeom.EmptyElements();
        // In mesh space the measured lower skin surface sets the contact plane.
        // A 6 cm sole remains inside the visible foot; shrink its footprint 10%.
        FVector Size = Bounds.GetSize();
        Size.X *= .9; Size.Y *= .9; Size.Z = FMath::Min(6.0, Size.Z);
        FVector Center = Bounds.GetCenter();
        Center.Z = Bounds.Min.Z + Size.Z * .5;
        FTransform BoxWorld(Mesh->GetComponentQuat(), Mesh->GetComponentTransform().TransformPosition(Center));
        const FTransform BoxLocal = BoxWorld.GetRelativeTransform(Mesh->GetSocketTransform(Foot));
        FKBoxElem Box;
        Box.X = Size.X; Box.Y = Size.Y; Box.Z = Size.Z;
        Box.SetTransform(BoxLocal);
        Setup->AggGeom.BoxElems.Add(Box);
        Setup->InvalidatePhysicsData();
        Setup->CreatePhysicsMeshes();
    }
    for (const TCHAR* Arm : {TEXT("lowerarm_l"), TEXT("lowerarm_r"), TEXT("hand_l"), TEXT("hand_r")})
        for (const TCHAR* Trunk : {TEXT("pelvis"), TEXT("spine_02"), TEXT("spine_03"), TEXT("spine_04"), TEXT("spine_05")})
        {
            const int32 A = Asset->FindBodyIndex(Arm), B = Asset->FindBodyIndex(Trunk);
            if (A != INDEX_NONE && B != INDEX_NONE) Asset->EnableCollision(A, B);
        }
    Asset->MarkPackageDirty();
    return true;
#else
    return false;
#endif
}
