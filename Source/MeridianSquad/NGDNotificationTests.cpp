#include "NGDPropComponent.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Engine/World.h"
#include "GeometryCollection/GeometryCollectionComponent.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FNGDNotificationContractTest, "Meridian.Destruction.NotificationContract",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::EngineFilter)

bool FNGDNotificationContractTest::RunTest(const FString& Parameters)
{
    // No actor ticks, vendor assets, solver, or global frame mutation are needed for this contract.
    UWorld* World = NewObject<UWorld>();
    auto* Subsystem = NewObject<UNGDWorldSubsystem>(World);
    Subsystem->bBatchNotifications = true;
    auto MakeSource = [&](const TCHAR* Path, int64 Lifetime)
    {
        auto* Source = NewObject<UNGDPropComponent>(World);
        Source->Collection = NewObject<UGeometryCollectionComponent>(World);
        Source->ObjectId = TEXT("CopiedObjectId");
        Source->ActorPath = FName(Path);
        Source->AdapterPath = FName(*(FString(Path) + TEXT(".Adapter")));
        Source->CollectionPath = FName(*(FString(Path) + TEXT(".Collection")));
        Source->AdapterLifetimeId = Lifetime;
        Source->bReady = true;
        return Source;
    };
    auto Change = [](UNGDPropComponent* Source, int32 Revision, double Min, double Max, FName Reason = TEXT("break"))
    {
        FNGDCollisionChange Value;
        Value.ObjectId = Source->ObjectId;
        Value.ActorPath = Source->ActorPath;
        Value.AdapterPath = Source->AdapterPath;
        Value.CollectionPath = Source->CollectionPath;
        Value.AdapterLifetimeId = Source->AdapterLifetimeId;
        Value.FirstCollisionRevision = Revision;
        Value.CollisionRevision = Revision;
        Value.ResetGeneration = Source->ResetGeneration;
        Value.ChangedBounds = FBox(FVector(Min), FVector(Max));
        Value.Reason = Reason;
        Source->CollisionRevision = Revision;
        return Value;
    };

    auto* A = MakeSource(TEXT("World.ActorA"), 1);
    auto* B = MakeSource(TEXT("World.ActorB"), 2);
    TArray<FNGDCollisionChange> Published;
    Subsystem->OnCollisionChangesBatchedNative.AddLambda([&](const FNGDCollisionChange& Value) { Published.Add(Value); });
    Subsystem->Publish(A, Change(A, 1, -100, 1));
    Subsystem->Publish(B, Change(B, 1, 40, 50));
    Subsystem->Publish(A, Change(A, 2, -1, 300));
    Subsystem->Publish(A, Change(A, 3, 0, 1));
    TestEqual(TEXT("Legacy last state is synchronous before frame flush"),
        Subsystem->LatestChanges[A->ObjectId].CollisionRevision, 3);
    TestEqual(TEXT("No explicit batch before flush"), Published.Num(), 0);
    Subsystem->FlushPending();
    TestEqual(TEXT("Copied IDs retain two actor batches"), Published.Num(), 2);
    if (Published.Num() != 2) return false;
    TestEqual(TEXT("First-change actor order"), Published[0].ActorPath, A->ActorPath);
    TestEqual(TEXT("Second actor order"), Published[1].ActorPath, B->ActorPath);
    TestEqual(TEXT("All changes retained in count"), Published[0].ChangeCount, 3);
    TestEqual(TEXT("First revision retained"), Published[0].FirstCollisionRevision, 1);
    TestEqual(TEXT("Final revision retained"), Published[0].CollisionRevision, 3);
    TestEqual(TEXT("Intermediate negative envelope retained"), Published[0].ChangedBounds.Min.X, -100.0);
    TestEqual(TEXT("Intermediate positive envelope retained"), Published[0].ChangedBounds.Max.X, 300.0);
    TestEqual(TEXT("Actor cache separates copied IDs"), Subsystem->LatestActorChanges.Num(), 2);
    TestFalse(TEXT("First pending state drained"), A->bPendingNotification);

    // A reset consumes an old pending envelope and changes identity without a stale break flush.
    Published.Reset();
    Subsystem->Publish(A, Change(A, 4, -500, 600));
    const FBox ResetBounds = Subsystem->CancelPending(A);
    A->bRetiring = true;
    auto* Replacement = MakeSource(TEXT("World.ActorAReplacement"), 3);
    Replacement->ResetGeneration = 1;
    auto Reset = Change(Replacement, 5, 0, 1, TEXT("reset"));
    Reset.ChangedBounds += ResetBounds;
    Subsystem->Publish(Replacement, Reset);
    Subsystem->FlushPending();
    TestEqual(TEXT("Only replacement reset is published"), Published.Num(), 1);
    TestEqual(TEXT("Reset revision advances past pending break"), Published[0].CollisionRevision, 5);
    TestEqual(TEXT("Reset uses new lifetime"), Published[0].AdapterLifetimeId, int64(3));
    TestEqual(TEXT("Reset generation retained"), Published[0].ResetGeneration, 1);
    TestEqual(TEXT("Reset carries complete pending envelope"), Published[0].ChangedBounds.Max.X, 600.0);
    TestEqual(TEXT("Canceled break counted"), A->InvalidatedNotificationChanges, int64(1));
    TestFalse(TEXT("Retired actor removed from actor cache"), Subsystem->LatestActorChanges.Contains(A->ActorPath));
    Subsystem->Publish(Replacement, Change(Replacement, 6, 1, 5));
    Subsystem->FlushPending();
    TestEqual(TEXT("Damage after reset still publishes"), Published.Num(), 2);

    // Reentrant same-actor damage is queued after the detached batch and cannot publish twice/frame.
    auto* Reentrant = MakeSource(TEXT("World.Reentrant"), 4);
    bool bAddedReentrantChange = false;
    const FDelegateHandle ReentrantHandle = Subsystem->OnCollisionChangesBatchedNative.AddLambda(
        [&](const FNGDCollisionChange& Value)
        {
            if (Value.AdapterLifetimeId != 4 || bAddedReentrantChange) return;
            bAddedReentrantChange = true;
            Subsystem->Publish(Reentrant, Change(Reentrant, 2, -20, 20));
            Subsystem->FlushPending();
        });
    const int32 BeforeReentrant = Published.Num();
    Subsystem->Publish(Reentrant, Change(Reentrant, 1, -1, 1));
    Subsystem->FlushPending();
    Subsystem->FlushPending();
    TestEqual(TEXT("Reentrant flush publishes only once this frame"), Published.Num(), BeforeReentrant + 1);
    TestTrue(TEXT("Reentrant change remains pending"), Reentrant->bPendingNotification);
    Reentrant->LastNotificationFrame = MAX_uint64; // Simulate a later frame without changing engine state.
    Subsystem->FlushPending();
    TestEqual(TEXT("Reentrant change is eventually published"), Published.Num(), BeforeReentrant + 2);
    Subsystem->OnCollisionChangesBatchedNative.Remove(ReentrantHandle);

    // A listener that resets a later actor during flush invalidates the detached old entry too.
    auto* First = MakeSource(TEXT("World.Resetter"), 5);
    auto* Later = MakeSource(TEXT("World.ResetVictim"), 6);
    const FDelegateHandle ResetHandle = Subsystem->OnCollisionChangesBatchedNative.AddLambda(
        [&](const FNGDCollisionChange& Value)
        {
            if (Value.AdapterLifetimeId != 5) return;
            Subsystem->CancelPending(Later);
            Later->bRetiring = true;
        });
    const int32 BeforeReset = Published.Num();
    Subsystem->Publish(First, Change(First, 1, 0, 1));
    Subsystem->Publish(Later, Change(Later, 1, 0, 1));
    Subsystem->FlushPending();
    TestEqual(TEXT("No stale later actor after reset within batch callback"), Published.Num(), BeforeReset + 1);
    TestFalse(TEXT("Later actor pending cleared"), Later->bPendingNotification);
    Subsystem->OnCollisionChangesBatchedNative.Remove(ResetHandle);

    // Particle lifetime can change even though actor, adapter and collection addresses are equal.
    auto* Recreated = MakeSource(TEXT("World.Recreated"), 8);
    Subsystem->NextLifetimeId = 100;
    Subsystem->SourcesByCollection.Add(Recreated->Collection.Get(), Recreated);
    Subsystem->Publish(Recreated, Change(Recreated, 1, -700, 900));
    const int32 BeforeRecreation = Published.Num();
    Subsystem->PhysicsDestroyed(Recreated->Collection.Get());
    TestTrue(TEXT("Destroyed physics blocks old-lifetime callbacks"), Recreated->bPhysicsRecreating);
    TestFalse(TEXT("Destroyed physics invalidates pending batch"), Recreated->bPendingNotification);
    Subsystem->FlushPending();
    TestEqual(TEXT("Destroyed physics cannot flush stale change"), Published.Num(), BeforeRecreation);
    Subsystem->PhysicsCreated(Recreated->Collection.Get());
    TestEqual(TEXT("Physics recreation publishes immediate reset"), Published.Num(), BeforeRecreation + 1);
    TestEqual(TEXT("Physics recreation creates distinct lifetime"), Recreated->AdapterLifetimeId, int64(101));
    TestEqual(TEXT("Physics recreation advances revision"), Recreated->CollisionRevision, 2);
    TestEqual(TEXT("Physics recreation advances reset generation"), Recreated->ResetGeneration, 1);
    TestEqual(TEXT("Physics recreation retains canceled envelope"), Published.Last().ChangedBounds.Max.X, 900.0);
    TestEqual(TEXT("Physics recreation counts invalidated events"), Recreated->LifetimeInvalidatedNotificationChanges, int64(1));
    Subsystem->Publish(Recreated, Change(Recreated, 3, 1, 2));
    Subsystem->FlushPending();
    TestEqual(TEXT("Damage after physics recreation publishes"), Published.Num(), BeforeRecreation + 2);

    auto* Control = MakeSource(TEXT("World.Immediate"), 7);
    Subsystem->bBatchNotifications = false;
    const int32 BeforeControl = Published.Num();
    Subsystem->Publish(Control, Change(Control, 1, 0, 1));
    Subsystem->Publish(Control, Change(Control, 2, 1, 2));
    TestEqual(TEXT("Immediate control publishes every change"), Published.Num(), BeforeControl + 2);
    TestEqual(TEXT("Immediate control queues no changes"), Control->QueuedNotificationChanges, int64(0));
    TestFalse(TEXT("Immediate control leaves no pending state"), Control->bPendingNotification);
    Subsystem->OnCollisionChangesBatchedNative.Clear();
    return true;
}
#endif
