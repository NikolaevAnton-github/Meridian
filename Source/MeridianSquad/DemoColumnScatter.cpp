#include "DemoColumnScatter.h"
#include "Chaos/PBDRigidClustering.h"
#include "Chaos/PBDRigidsEvolution.h"
#include "Engine/HitResult.h"
#include "GeometryCollection/GeometryCollectionComponent.h"
#include "Math/RandomStream.h"
#include "PhysicsProxy/GeometryCollectionPhysicsProxy.h"
#include "PhysicsSolver.h"

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
