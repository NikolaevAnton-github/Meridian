#include "DestructionCollisionPolicy.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "NGDPropComponent.h"
#include "Dom/JsonObject.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GeometryCollection/GeometryCollectionComponent.h"
#include "Misc/AutomationTest.h"
#include "Serialization/JsonSerializer.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDP03CollisionContractTest, "Meridian.Destruction.CollisionRuntimeContract",
    EAutomationTestFlags::ClientContext | EAutomationTestFlags::EngineFilter)

bool FDP03CollisionContractTest::RunTest(const FString& Parameters)
{
    UWorld* World = nullptr;
    for (const auto& Context : GEngine->GetWorldContexts())
        if (Context.World() && Context.World()->WorldType == EWorldType::Game) World = Context.World();
    if (!TestNotNull(TEXT("Standalone game world required"), World)) return false;
    TArray<UNGDPropComponent*> Props;
    for (TActorIterator<AActor> It(World); It; ++It)
        if (auto* Prop = It->FindComponentByClass<UNGDPropComponent>(); Prop && Prop->bReady) Props.Add(Prop);
    if (!TestTrue(TEXT("Retained fixture has multiple managed props"), Props.Num() >= 2)) return false;
    auto* A = Props[0];
    auto* B = Props[1];
    auto* Policy = A->GetOwner()->FindComponentByClass<UDestructionCollisionPolicy>();
    auto* OtherPolicy = B->GetOwner()->FindComponentByClass<UDestructionCollisionPolicy>();
    if (!TestNotNull(TEXT("First policy"), Policy) || !TestNotNull(TEXT("Second policy"), OtherPolicy)) return false;
    if (!TestTrue(TEXT("Native source-verified policy is installed"), Policy->Snapshot()->GetBoolField(TEXT("installed"))) ||
        !TestEqual(TEXT("Native mode selected"), Policy->Snapshot()->GetStringField(TEXT("mode")), FString(TEXT("native")))) return false;
    auto* GC = A->GetOwner()->FindComponentByClass<UGeometryCollectionComponent>();
    auto* OtherGC = B->GetOwner()->FindComponentByClass<UGeometryCollectionComponent>();
    auto Count = [](UDestructionCollisionPolicy* P, const TCHAR* Key) { return int64(P->Snapshot()->GetNumberField(Key)); };
    const TArray<int32> Index{0};
    GC->SetPerParticleCollisionProfileName(Index, TEXT("BlockAll"));
    OtherGC->SetPerParticleCollisionProfileName(Index, TEXT("BlockAll"));
    FChaosPhysicsCollisionInfo Event;
    Event.Component = GC;
    Event.OtherComponent = OtherGC;
    Event.Location = A->GetOwner()->GetActorLocation();
    auto Send = [&](double Speed) { Event.Velocity = FVector(Speed, 0, 0); Policy->ReceiveCollision(Event); };
    const int64 Requested = Count(Policy, TEXT("profile_requested"));
    const int64 Applied = Count(Policy, TEXT("profile_applied"));
    const int64 Skipped = Count(Policy, TEXT("profile_skipped_identical"));
    const int64 Forwarded = Count(Policy, TEXT("forwarded_callbacks"));
    Send(.5);
    TestEqual(TEXT("Exact lower threshold does not request a profile"), Count(Policy, TEXT("profile_requested")), Requested);
    Send(.51);
    TestEqual(TEXT("Actual nonidentical override is applied"), Count(Policy, TEXT("profile_applied")), Applied + 1);
    TestEqual(TEXT("Authoritative override is current"), Policy->Snapshot()->GetStringField(TEXT("authoritative_profile0")), FString(TEXT("IgnoreCharChaos")));
    Send(.51);
    TestEqual(TEXT("Repeated identical override is skipped"), Count(Policy, TEXT("profile_skipped_identical")), Skipped + 1);
    Send(200.);
    TestEqual(TEXT("Exact upper threshold retains fast path"), Count(Policy, TEXT("forwarded_callbacks")), Forwarded);
    Send(200.001);
    TestEqual(TEXT("High-speed callback uses original vendor sleep/audio path"), Count(Policy, TEXT("forwarded_callbacks")), Forwarded + 1);
    GC->SetPerParticleCollisionProfileName(Index, TEXT("BlockAll"));
    Send(1.);
    TestEqual(TEXT("External write invalidates equality without a cached last request"), Count(Policy, TEXT("profile_applied")), Applied + 2);
    const FName OriginalBId = B->ObjectId;
    B->ObjectId = A->ObjectId;
    TestEqual(TEXT("Copied ObjectId cannot affect other collection"), OtherPolicy->Snapshot()->GetStringField(TEXT("authoritative_profile0")), FString(TEXT("BlockAll")));
    Event.Component = OtherGC;
    Event.OtherComponent = GC;
    Event.Velocity = FVector(1, 0, 0);
    OtherPolicy->ReceiveCollision(Event);
    TestEqual(TEXT("Copied-ID peer applies its own override"), OtherPolicy->Snapshot()->GetStringField(TEXT("authoritative_profile0")), FString(TEXT("IgnoreCharChaos")));
    B->ObjectId = OriginalBId;
    // Recreate the same component, then change its desired state. A path/ID cache
    // alone would survive this particle-lifetime boundary and skip the new write.
    GC->RecreatePhysicsState();
    GC->SetPerParticleCollisionProfileName(Index, TEXT("BlockAll"));
    Event.Component = GC;
    Event.OtherComponent = OtherGC;
    Send(1.);
    TestEqual(TEXT("Recreated component still uses authoritative state"), Count(Policy, TEXT("profile_applied")), Applied + 3);
    const FName Id = A->ObjectId;
    const FVector Location = A->GetOwner()->GetActorLocation();
    const int32 Generation = A->ResetGeneration;
    UNGDPropComponent::ResetAll(World);
    TestFalse(TEXT("Retired policy no longer receives events"), Policy->Snapshot()->GetBoolField(TEXT("installed")));
    UNGDPropComponent* Replacement = nullptr;
    for (TActorIterator<AActor> It(World); It; ++It)
        if (auto* Prop = It->FindComponentByClass<UNGDPropComponent>(); Prop && Prop->bReady && Prop->ObjectId == Id &&
            It->GetActorLocation().Equals(Location, 1.)) Replacement = Prop;
    if (!TestNotNull(TEXT("Reset recreates the prop"), Replacement)) return false;
    TestEqual(TEXT("Reset advances generation"), Replacement->ResetGeneration, Generation + 1);
    TestEqual(TEXT("Reset starts with no break notifications"), Replacement->BreakEvents, 0);
    auto* NewGC = Replacement->GetOwner()->FindComponentByClass<UGeometryCollectionComponent>();
    auto* NewPolicy = Replacement->GetOwner()->FindComponentByClass<UDestructionCollisionPolicy>();
    TestTrue(TEXT("Replacement policy is installed"), NewPolicy && NewPolicy->Snapshot()->GetBoolField(TEXT("installed")));
    // Exercise the real adapter's vendor damage entrypoint twice with one shot ID.
    // Physics outcome is separately covered by repeated F7 captures, not this synchronous test.
    FHitResult Hit(Replacement->GetOwner(), NewGC, Location + FVector(0, 0, 100), FVector(1, 0, 0));
    Hit.Item = 0;
    Replacement->ReceiveBullet(903001, Hit);
    Replacement->ReceiveBullet(903001, Hit);
    TestEqual(TEXT("Subsequent damage delivered once after reset"), Replacement->DeliveredHits, 1);
    UNGDPropComponent::ResetAll(World);
    return true;
}
#endif
