#include "PhysicsControlDummy.h"
#include "PhysicsControlRecoveryLibrary.h"
#include "DummyRecoveryAnimInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/SkeletalBodySetup.h"
#include "PhysicsEngine/BodyInstance.h"
#include "Physics/PhysicsInterfaceCore.h"
#include "Chaos/ChaosEngineInterface.h"
#include "EngineUtils.h"

float APhysicsControlDummy::GetRecoveryAnimationTime() const
{
    // Both complete Mixamo clips begin with a nearly static down-pose lead-in
    // (measured in the retained 30 Hz motion audit). Traverse that range during
    // the snapshot's initial 0.15 s, then play the actual get-up at source speed.
    // No source frames/ranges are removed and the mapping stays continuous.
    const float LeadIn = ActiveGetUp == GetUpBack ? 2.3f : 1.2f;
    constexpr float TransitionLeadIn = .15f;
    return StateSeconds < TransitionLeadIn ? StateSeconds * LeadIn / TransitionLeadIn :
        LeadIn + StateSeconds - TransitionLeadIn;
}

void APhysicsControlDummy::CalibrateSoles()
{
    const auto Vertices = UPhysicsControlRecoveryLibrary::FootVertices(Body);
    for (bool bLeft : {true, false})
    {
        const FString Suffix = bLeft ? TEXT("_l") : TEXT("_r");
        double Bottom = TNumericLimits<double>::Max();
        for (const auto& V : Vertices)
            if (V.Bone.ToString().EndsWith(Suffix)) Bottom = FMath::Min(Bottom, V.World.Z);
        for (const auto& V : Vertices)
            if (V.Bone.ToString().EndsWith(Suffix) && V.World.Z <= Bottom + .3)
                SolePoints.Add({V.Bone, V.Local});
    }
}

float APhysicsControlDummy::SoleBottom(const USkeletalMeshComponent* Mesh, bool bLeft) const
{
    double Bottom = TNumericLimits<double>::Max();
    for (const auto& Point : SolePoints)
        if (Point.Bone.ToString().EndsWith(bLeft ? TEXT("_l") : TEXT("_r")))
            Bottom = FMath::Min(Bottom, Mesh->GetSocketTransform(Point.Bone).TransformPosition(Point.Local).Z);
    return static_cast<float>(Bottom);
}

float APhysicsControlDummy::ShapeBottom(FName Bone, const FTransform& Transform) const
{
    const auto* Asset = Body->GetPhysicsAsset();
    const int32 Index = Asset->FindBodyIndex(Bone);
    if (Index == INDEX_NONE) return Transform.GetLocation().Z;
    double Bottom = TNumericLimits<double>::Max();
    const auto& Shapes = Asset->SkeletalBodySetups[Index]->AggGeom;
    for (const auto& Box : Shapes.BoxElems)
    {
        const FTransform T = Box.GetTransform() * Transform;
        const double Height = FMath::Abs(T.GetUnitAxis(EAxis::X).Z) * Box.X / 2 +
            FMath::Abs(T.GetUnitAxis(EAxis::Y).Z) * Box.Y / 2 + FMath::Abs(T.GetUnitAxis(EAxis::Z).Z) * Box.Z / 2;
        Bottom = FMath::Min(Bottom, T.GetLocation().Z - Height);
    }
    for (const auto& Capsule : Shapes.SphylElems)
    {
        const FTransform T = Capsule.GetTransform() * Transform;
        Bottom = FMath::Min(Bottom, T.GetLocation().Z - FMath::Abs(T.GetUnitAxis(EAxis::Z).Z) * Capsule.Length / 2 - Capsule.Radius);
    }
    for (const auto& Sphere : Shapes.SphereElems)
        Bottom = FMath::Min(Bottom, (Sphere.GetTransform() * Transform).GetLocation().Z - Sphere.Radius);
    return static_cast<float>(Bottom);
}

float APhysicsControlDummy::PoseBottom(const TMap<FName,FTransform>& Pose) const
{
    float Bottom = TNumericLimits<float>::Max();
    for (const auto& Entry : Pose) Bottom = FMath::Min(Bottom, ShapeBottom(Entry.Key, Entry.Value));
    return Bottom;
}

bool APhysicsControlDummy::FootSupported(FName Bone) const
{
    const auto* BI = Body->GetBodyInstance(Bone);
    if (!BI) return false;
    const FTransform Actual = BI->GetUnrealWorldTransform();
    const float Bottom = ShapeBottom(Bone, Actual);
    FVector Point = Actual.GetLocation();
    Point.Z = Bottom;
    FHitResult Floor;
    if (!FindFloor(Point, FMath::Clamp(SupportReach, .5f, 3.f), Floor)) return false;
    const float Gap = Bottom - Floor.ImpactPoint.Z;
    return Gap >= -2.f && Gap <= FMath::Clamp(SupportReach, .5f, 3.f);
}

void APhysicsControlDummy::IsolateSelfCollision()
{
    // Shape filtering must block PhysicsBody for self contact. Explicit Chaos
    // pairs preserve isolation between fixtures without affecting their rifle trace.
    TMap<FPhysicsActorHandle, TArray<FPhysicsActorHandle>> Exclusions;
    const auto* Asset = Body->GetPhysicsAsset();
    for (int32 I = 0; I < Body->Bodies.Num(); ++I)
    {
        auto* BI = Body->Bodies[I];
        if (!BI || !BI->IsValidBodyInstance()) continue;
        auto& Ignored = Exclusions.FindOrAdd(BI->GetPhysicsActor());
        // Include own asset exclusions in the same command: pending Chaos maps
        // replace earlier maps for a source body in the same solver timestamp.
        for (const auto& Pair : Asset->CollisionDisableTable)
        {
            const int32 A = Pair.Key.Indices[0], B = Pair.Key.Indices[1];
            const int32 Other = A == I ? B : B == I ? A : INDEX_NONE;
            if (Body->Bodies.IsValidIndex(Other) && Body->Bodies[Other])
                Ignored.AddUnique(Body->Bodies[Other]->GetPhysicsActor());
        }
        for (TActorIterator<APhysicsControlDummy> It(GetWorld()); It; ++It)
            if (*It != this)
                for (auto* Other : It->Body->Bodies)
                    if (Other && Other->IsValidBodyInstance()) Ignored.AddUnique(Other->GetPhysicsActor());
        BI->SetUseCCD(true);
    }
    FPhysicsCommand::ExecuteWrite(Body, [&]() { FChaosEngineInterface::AddDisabledCollisionsFor_AssumesLocked(Exclusions); });
}

void APhysicsControlDummy::SetVisibleAnimationPose()
{
    FPoseSnapshot Output;
    PoseSource->SnapshotPose(Output);
    Output.LocalTransforms[0] = (Output.LocalTransforms[0] * PoseSource->GetComponentTransform()).GetRelativeTransform(Body->GetComponentTransform());
    auto* Anim = CastChecked<UDummyRecoveryAnimInstance>(Body->GetAnimInstance());
    Anim->StartPose = MoveTemp(Output);
    Anim->bSnapshotOnly = true;
    Body->bPauseAnims = false;
    // Physics remains at weight 1. The graph drives non-physical bones and the
    // same pose's body targets, so animation and independent drives cannot disagree.
}

void APhysicsControlDummy::EvaluateRecoveryPose(float Time, float Blend, float EndBlend, TMap<FName,FTransform>& Pose)
{
    // Retargeting preserves the full motion but its support envelope varies in Z.
    // Calibrate the moving animation branch before the snapshot blend, keeping
    // the actual fallen snapshot fixed at alpha zero and the floor underneath it.
    TMap<FName,FTransform> Raw;
    SampleAnimation(ActiveGetUp, Time, RecoveryRoot, Raw);
    const float MotionOffset = GroundHeight + .15f - PoseBottom(Raw);
    auto* Anim = CastChecked<UDummyRecoveryAnimInstance>(PoseSource->GetAnimInstance());
    Anim->Sequence = ActiveGetUp;
    Anim->SequenceTime = Time;
    Anim->StartPose = FallenSnapshot;
    Anim->EndPose = IdleSnapshot;
    Anim->StartAlpha = Blend;
    Anim->EndAlpha = EndBlend;
    Anim->MotionOffsetZ = MotionOffset;
    PoseSource->TickAnimation(0, false);
    PoseSource->RefreshBoneTransforms();
    Pose.Reset();
    for (const auto& Entry : StandingPose) Pose.Add(Entry.Key, PoseSource->GetSocketTransform(Entry.Key));
    SetVisibleAnimationPose();
}
