#include "PhysicsControlDummy.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"

void APhysicsControlDummy::ClearBalanceProbeFixtures()
{
    if (IsValid(ProbeFloor)) ProbeFloor->Destroy();
    if (IsValid(ProbeCeiling)) ProbeCeiling->Destroy();
    ProbeFloor=nullptr; ProbeCeiling=nullptr;
}

bool APhysicsControlDummy::ProbeBalanceEnvironment(const FString& Operation)
{
#if WITH_EDITOR
    if (GetWorld()->WorldType != EWorldType::PIE) return false;
    if (Operation == TEXT("remove_floor"))
    {
        if (!IsValid(ProbeFloor)) return false;
        ProbeFloor->Destroy(); ProbeFloor=nullptr; return true;
    }
    if (Operation == TEXT("clear_ceiling"))
    {
        if (!IsValid(ProbeCeiling)) return false;
        ProbeCeiling->Destroy(); ProbeCeiling=nullptr; return true;
    }
    auto SpawnBox = [&](FVector Center, FVector Scale) -> AStaticMeshActor*
    {
        FActorSpawnParameters Params;
        Params.ObjectFlags |= RF_Transient;
        Params.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
        auto* Actor=GetWorld()->SpawnActor<AStaticMeshActor>(Center,FRotator::ZeroRotator,Params);
        if (!Actor) return nullptr;
        Actor->Tags.Add(TEXT("MSQ87_TransientProbe"));
        auto* Mesh=Actor->GetStaticMeshComponent();
        Mesh->SetMobility(EComponentMobility::Movable);
        Mesh->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));
        Mesh->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
        Mesh->SetCollisionObjectType(ECC_WorldStatic);
        Mesh->SetCollisionResponseToAllChannels(ECR_Block);
        Actor->SetActorScale3D(Scale);
        return Actor;
    };
    if (Operation == TEXT("platform"))
    {
        auto* Floor=SpawnBox(FVector(30000,33000,990),FVector(8,8,.2));
        if (!Floor) return false;
        const FTransform OriginalHome=Home;
        Home=FTransform(Home.GetRotation(),FVector(30000,33000,1000));
        ResetDummy();
        Home=OriginalHome;
        ProbeFloor=Floor;
        return IsValid(ProbeFloor);
    }
    if (Operation == TEXT("turn90"))
    {
        const FTransform OriginalHome = Home;
        Home.SetRotation(FRotator(0, Home.Rotator().Yaw + 90, 0).Quaternion());
        ResetDummy();
        Home = OriginalHome;
        return true;
    }
    if (Operation == TEXT("step_wall"))
    {
        if (IsValid(ProbeCeiling)) return false;
        FVector P = GetPhysicalBodyLocation(TEXT("pelvis")) - StandingForward * 40;
        P.Z = GroundHeight + 45;
        ProbeCeiling = SpawnBox(P, FVector(.1, 1.1, .9));
        if (ProbeCeiling) ProbeCeiling->SetActorRotation(StandingForward.Rotation());
        return IsValid(ProbeCeiling);
    }
    if (Operation == TEXT("ceiling"))
    {
        if (IsValid(ProbeCeiling)) return false;
        FVector P=GetPhysicalBodyLocation(TEXT("pelvis"));
        P.Z=GroundHeight+90;
        ProbeCeiling=SpawnBox(P,FVector(3,3,.2));
        return IsValid(ProbeCeiling);
    }
#endif
    return false;
}
