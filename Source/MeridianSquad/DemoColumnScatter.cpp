#include "DemoColumnScatter.h"
#include "Chaos/PBDRigidClustering.h"
#include "Chaos/PBDRigidsEvolution.h"
#include "Engine/HitResult.h"
#include "GeometryCollection/GeometryCollectionComponent.h"
#include "Math/RandomStream.h"
#include "PhysicsProxy/GeometryCollectionPhysicsProxy.h"
#include "PhysicsSolver.h"
#include "Async/Async.h"
#include "GameFramework/Actor.h"
#include "Physics/PhysicsFiltering.h"

void ApplyDemoColumnScatter(UGeometryCollectionComponent* Concrete, const FHitResult& Hit, uint32 Seed)
{
    check(IsInGameThread());
    if (!Concrete || Hit.Item == INDEX_NONE) return;
    auto* Proxy = Concrete->GetPhysicsProxy();
    if (!Proxy) return;
    auto* Solver = Proxy->GetSolver<Chaos::FPhysicsSolver>();
    if (!Solver) return;

    const FVector Origin = Hit.ImpactPoint;
    const FVector Normal = Hit.ImpactNormal.GetSafeNormal();
    if (Origin.ContainsNaN() || Normal.ContainsNaN() || Normal.IsNearlyZero()) return;
    const auto Item = FGeometryCollectionItemIndex::CreateFromExistingItemIndex(Hit.Item);
    TArray<int32> InternalChildren;
    if (Item.IsInternalCluster())
    {
        const auto* Children = Proxy->FindInternalClusterChildrenTransformIndices_External(Item);
        if (!Children || Children->IsEmpty()) return;
        InternalChildren = *Children;
    }

    // Match the native breaking-velocity API's one-shot solver enqueue lifetime.
    // Copy GT indices; particle handles are resolved only on the physics thread.
    Solver->EnqueueCommandImmediate([Proxy, Solver, Item, Origin, Normal, Seed, InternalChildren = MoveTemp(InternalChildren)]()
    {
        using FCluster = Chaos::FPBDRigidClusteredParticleHandle;
        FCluster* Body = nullptr;
        if (!Item.IsInternalCluster())
        {
            // This accessor accepts a transform index and maps it to the particle.
            if (auto* Particle = Proxy->GetParticleByIndex_Internal(Item.GetTransformIndex()))
                Body = Particle->CastToClustered();
        }
        else
        {
            for (const int32 TransformIndex : InternalChildren)
            {
                auto* Particle = Proxy->GetParticleByIndex_Internal(TransformIndex);
                auto* Child = Particle ? Particle->CastToClustered() : nullptr;
                auto* Parent = Child ? Child->Parent() : nullptr;
                if (Parent && Parent->InternalCluster() && Parent->PhysicsProxy() == Proxy &&
                    Parent->UniqueIdx().Idx == Item.GetInternalClusterIndex())
                {
                    Body = Parent;
                    break;
                }
            }
        }
        if (!Body || Body->Disabled() || Body->PhysicsProxy() != Proxy) return;
        auto* Evolution = Solver->GetEvolution();
        if (!Evolution) return;

        auto Scatter = [&](FCluster* Child)
        {
            if (!Child || !Child->IsDynamic()) return;
            FVector Position = Child->GetX();
            if (Child->Disabled())
            {
                if (Child->Parent() != Body) return;
                Position = (Child->ChildToParent() * Chaos::FRigidTransform3(Body->GetX(), Body->GetR())).GetTranslation();
            }
            FVector Radial = (Position - Origin).GetSafeNormal();
            if (Radial.IsNearlyZero()) Radial = Normal;
            const FVector DeltaV = Radial * 200.f + Normal * 250.f + FVector(0, 0, 70);
            const uint32 BodySeed = Seed ^ (static_cast<uint32>(Child->UniqueIdx().Idx) * 0x9e3779b9u);
            FRandomStream Random(static_cast<int32>(BodySeed));
            const FVector SpinAxis = Random.VRand();
            const FVector DeltaW = SpinAxis * Random.FRandRange(3.f, 7.f);
            Child->SetV(Child->GetV() + DeltaV);
            Child->SetW(Child->GetW() + DeltaW);
            if (!Child->Disabled()) Evolution->WakeParticle(Child);
            UE_LOG(LogTemp, Display, TEXT("DemoColumnScatter item=%d body=%d position=%s deltaV=%s"),
                Item.GetItemIndex(), Child->UniqueIdx().Idx, *Position.ToCompactString(), *DeltaV.ToCompactString());
        };

        if (Body->ClusterIds().NumChildren > 0)
        {
            const auto* Children = Evolution->GetRigidClustering().GetChildrenMap().Find(Body);
            if (!Children) return;
            for (auto* Particle : *Children)
            {
                auto* Child = Particle ? Particle->CastToClustered() : nullptr;
                if (Child && Child->GetExternalStrain() >= Child->GetInternalStrains()) Scatter(Child);
            }
        }
        else
        {
            // An already released, active leaf can receive another direct hit.
            Scatter(Body);
        }
    });
}

void ReleaseDemoColumnLeaf(UGeometryCollectionComponent* Concrete, int32 Bone, const FHitResult& Hit, uint32 Seed)
{
    check(IsInGameThread());
    auto* Proxy = Concrete ? Concrete->GetPhysicsProxy() : nullptr;
    auto* Solver = Proxy ? Proxy->GetSolver<Chaos::FPhysicsSolver>() : nullptr;
    if (!Solver || Bone == INDEX_NONE) return;
    FVector Normal = Hit.ImpactNormal.GetSafeNormal();
    const bool bStacking = Concrete->GetOwner()->ActorHasTag(TEXT("DemoColumnStacking08"));
    const bool bHeavy = Concrete->GetOwner()->ActorHasTag(TEXT("DemoColumnRefined07"));
    if (bStacking)
    {
        const FVector Local = Concrete->GetComponentTransform().InverseTransformPosition(Hit.ImpactPoint);
        const FVector Side = FMath::Abs(Local.X) >= FMath::Abs(Local.Y)
            ? FVector(FMath::Sign(Local.X),0,0) : FVector(0,FMath::Sign(Local.Y),0);
        Normal = Concrete->GetComponentTransform().TransformVectorNoScale(Side).GetSafeNormal();
        ConfigureDemoColumnDebrisCollision(Concrete, Bone);
    }
    Solver->EnqueueCommandImmediate([Proxy, Solver, Bone, Normal, Seed, bHeavy, bStacking]()
    {
        auto* Particle = Proxy->GetParticleByIndex_Internal(Bone);
        auto* Leaf = Particle ? Particle->CastToClustered() : nullptr;
        if (!Leaf || Leaf->PhysicsProxy() != Proxy || Leaf->ClusterIds().NumChildren != 0) return;
        auto* Evolution = Solver->GetEvolution();
        if (!Evolution) return;
        bool Released = false;
        if (Leaf->Disabled() && Leaf->Parent() && !Leaf->Parent()->Parent())
        {
            Evolution->GetRigidClustering().ReleaseClusterParticles(TArray<Chaos::FPBDRigidParticleHandle*>{Leaf}, true);
            Released = !Leaf->Disabled() && !Leaf->Parent();
        }
        // An exposed original support leaf must also respond to its direct hit.
        // Only this released leaf changes state; untouched support stays fixed.
        if (!Leaf->Disabled() && !Leaf->Parent() && !Leaf->IsDynamic() && !Leaf->IsSleeping())
        {
            Leaf->SetIsAnchored(false);
            Evolution->SetParticleObjectState(Leaf, Chaos::EObjectStateType::Dynamic);
        }
        if (!Leaf->Disabled() && Leaf->IsDynamic())
        {
            // Material sleep can stop detached GC leaves before ground contact.
            // The bounded debris controller freezes only supported, settled pieces.
            Evolution->SetParticleSleepType(Leaf, Chaos::ESleepType::NeverSleep);
            FRandomStream Random(Seed * 733u + uint32(Bone));
            if (bStacking)
            {
                const double Speed = FMath::Clamp(16000. / FMath::Max(double(Leaf->M()), 30.), 135., 190.);
                // The side's outward normal remains valid inside a shot cavity;
                // fracture-face normals can point into the protected core.
                const FVector Sideways = FVector::CrossProduct(Normal, FVector::UpVector);
                Leaf->SetV(Normal*Speed + Sideways*Random.FRandRange(-10.f,10.f) + FVector(0,0,12));
                Leaf->SetW(Random.VRand()*Random.FRandRange(.2f,.45f));
            }
            else if (bHeavy)
            {
                const double Speed = FMath::Clamp(9000. / FMath::Max(double(Leaf->M()), 30.), 55., 115.);
                Leaf->SetV(Leaf->GetV() + Normal * Speed + Random.VRand() * 12. + FVector(0, 0, 8));
                Leaf->SetW(Leaf->GetW() + Random.VRand() * Random.FRandRange(.35f, .8f));
            }
            else
            {
                Leaf->SetV(Leaf->GetV() + Normal * 300. + Random.VRand() * 120. + FVector(0, 0, 70));
                Leaf->SetW(Leaf->GetW() + Random.VRand() * Random.FRandRange(3.f, 7.f));
            }
            Evolution->WakeParticle(Leaf);
        }
        UE_LOG(LogTemp, Display, TEXT("DemoColumn05 hit=%u bone=%d released=%d disabled=%d parent=%d"),
            Seed, Bone, Released, Leaf->Disabled(), Leaf->Parent() != nullptr);
    });
}

void ConfigureDemoColumnDebrisCollision(UGeometryCollectionComponent* Concrete, int32 Bone)
{
    auto* Proxy = Concrete ? Concrete->GetPhysicsProxy() : nullptr;
    if (!Proxy) return;
    FCollisionResponseContainer Responses(ECR_Ignore);
    Responses.SetResponse(ECC_WorldStatic, ECR_Block);
    Responses.SetResponse(ECC_PhysicsBody, ECR_Block);
    Responses.SetResponse(ECC_Visibility, ECR_Block);
    FPhysicsFilterBuilder Builder;
    Builder.SetOwnerID(Concrete->GetOwner()->GetUniqueID());
    Builder.SetComponentID(Concrete->GetUniqueID());
    Builder.SetCollisionChannelIndex(ECC_PhysicsBody);
    Builder.SetResponses(Responses);
    Builder.SetFlags(Chaos::EFilterFlags::SimpleCollision | Chaos::EFilterFlags::ComplexCollision | Chaos::EFilterFlags::CCD, true);
    FGeometryCollectionPhysicsProxy::FParticleCollisionFilterData Filter;
    Filter.ParticleIndex = Bone;
    Filter.bIsValid = Filter.bSimEnabled = Filter.bQueryEnabled = true;
    Filter.ShapeFilterData = Builder.BuildShapeFilterData();
    Filter.FilterInstanceData = Builder.BuildInstanceData();
    Proxy->UpdatePerParticleFilterData_External({Filter});
}

void KeepDemoColumnLeafAwake(UGeometryCollectionComponent* Concrete, int32 Bone)
{
    check(IsInGameThread());
    auto* Proxy = Concrete ? Concrete->GetPhysicsProxy() : nullptr;
    auto* Solver = Proxy ? Proxy->GetSolver<Chaos::FPhysicsSolver>() : nullptr;
    if (!Solver) return;
    Solver->EnqueueCommandImmediate([Proxy, Solver, Bone]()
    {
        auto* Particle = Proxy->GetParticleByIndex_Internal(Bone);
        auto* Leaf = Particle ? Particle->CastToClustered() : nullptr;
        if (!Leaf || Leaf->PhysicsProxy() != Proxy || Leaf->Disabled() || Leaf->Parent() ||
            Leaf->ClusterIds().NumChildren || !Leaf->IsDynamic()) return;
        Solver->GetEvolution()->SetParticleSleepType(Leaf, Chaos::ESleepType::NeverSleep);
        Solver->GetEvolution()->WakeParticle(Leaf);
    });
}

void FreezeDemoColumnLeaf(UGeometryCollectionComponent* Concrete, int32 Bone, TFunction<void(bool)> Completion)
{
    check(IsInGameThread());
    auto* Proxy = Concrete ? Concrete->GetPhysicsProxy() : nullptr;
    auto* Solver = Proxy ? Proxy->GetSolver<Chaos::FPhysicsSolver>() : nullptr;
    if (!Solver) { Completion(false); return; }
    // Enqueue immediately on the owning solver, matching the native one-shot
    // command lifetime. No raw proxy is stored for a later game-thread call.
    Solver->EnqueueCommandImmediate([Proxy, Solver, Bone, Completion = MoveTemp(Completion)]() mutable
    {
        bool Frozen = false;
        auto* Particle = Proxy->GetParticleByIndex_Internal(Bone);
        auto* Leaf = Particle ? Particle->CastToClustered() : nullptr;
        if (Leaf && Leaf->PhysicsProxy() == Proxy && !Leaf->Disabled() && !Leaf->Parent() &&
            Leaf->ClusterIds().NumChildren == 0 && (Leaf->IsDynamic() || Leaf->IsSleeping()) &&
            Leaf->GetV().SizeSquared() < 25. && Leaf->GetW().SizeSquared() < .04)
        {
            Leaf->SetV(Chaos::FVec3::ZeroVector);
            Leaf->SetW(Chaos::FVec3::ZeroVector);
            Leaf->SetKinematicTarget(Chaos::FKinematicTarget{});
            Solver->GetEvolution()->SetParticleObjectState(Leaf, Chaos::EObjectStateType::Kinematic);
            Solver->GetParticles().MarkTransientDirtyParticle(Leaf);
            Frozen = true;
        }
        AsyncTask(ENamedThreads::GameThread, [Completion = MoveTemp(Completion), Frozen]() mutable { Completion(Frozen); });
    });
}
