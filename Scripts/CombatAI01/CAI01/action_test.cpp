// Pure production contracts only; no engine world or gameplay simulation.
#include "../../../Source/MeridianSquad/CombatAIObservation.h"
#include <cassert>
#include <iostream>

using namespace CombatAI;

int main()
{
    EncounterMemory Memory;
    Memory.Observe(10);
    LocalSearchCycle Search;
    DestinationBackoff Route, Weapon;
    ActionRuntime A;
    // S01/S07: repeated failed actions and observation dwells beyond 60 seconds
    // cannot clear confirmed contact; retries stay bounded to nine proposals.
    for (int I = 0; I < 10000; ++I)
    {
        const double Now = 11.0 + I;
        const auto Request = A.Start(7, ActionKind::Move, Now);
        assert(A.Update(Request, Now + .25));
        assert(A.Finish(Request, ActionStatus::Failed, ActionFailure::Route, Now + .5));
        assert(!A.Finish(Request, ActionStatus::Succeeded, ActionFailure::None, Now + .6));
        Search.Advance(Now, .8, 5);
        assert(Search.Index >= 0 && Search.Index < LocalSearchCycle::CandidateCount);
        assert(Search.RetryAt > Now && Search.RetryAt <= Now + 5);
        assert(Memory.Alert && Memory.HasObservation && Memory.LastSeen == 10);
    }
    Route.Set(100, 200, 90);
    assert(Route.Blocks(100, 200, 89));
    assert(!Route.Blocks(100, 200, 90));
    assert(!Route.Blocks(500, 200, 89)); // New destination is eligible during backoff.
    assert(!Weapon.Blocks(100, 200, 89)); // Route failure cannot suppress a weapon action.
    Memory.Observe(89); // A tactical deadline is not a perception deadline.
    assert(Memory.LastSeen == 89 && Memory.Alert);
    // S06/S10: each command type rejects old update and completion after physical
    // interruption, same-generation replacement, reset and death.
    for (auto Kind : {ActionKind::Move, ActionKind::Aim, ActionKind::Burst, ActionKind::Reload, ActionKind::Observe})
    {
        auto Old = A.Start(7, Kind, 100);
        assert(A.Finish(Old, ActionStatus::Canceled, ActionFailure::Authority, 101));
        assert(!A.Update(Old, 102));
        assert(!A.Finish(Old, ActionStatus::Succeeded, ActionFailure::None, 102));
        assert(Memory.Alert && Memory.LastSeen == 89);
        const auto Recovered = A.Start(7, Kind, 103);
        assert(Recovered.Id != Old.Id && !A.Accepts(Old));
        assert(!A.Finish(Old, ActionStatus::Succeeded, ActionFailure::None, 104));
        const auto Reset = A.Start(8, Kind, 105);
        assert(!A.Accepts(Recovered) && A.Accepts(Reset));
        auto Forged = Reset; Forged.Generation = 7;
        assert(!A.Update(Forged, 106));
        assert(A.Finish(Reset, ActionStatus::Canceled, ActionFailure::Death, 107));
        assert(!A.Accepts(Reset));
    }
    // Reload commits once, and only against its original still-active request.
    int Ammo = 0;
    const auto Reload = A.Start(8, ActionKind::Reload, 110);
    if (A.Finish(Reload, ActionStatus::Succeeded, ActionFailure::None, 113)) ++Ammo;
    if (A.Finish(Reload, ActionStatus::Succeeded, ActionFailure::None, 114)) ++Ammo;
    assert(Ammo == 1);
    const auto BeforeReset = A.Start(8, ActionKind::Move, 115);
    A.Reset(8);
    assert(!A.Accepts(BeforeReset) && A.Kind == ActionKind::None && A.Token.Id != BeforeReset.Id);
    A.Reset(9);
    assert(A.Token.Generation == 9 && !A.Finish(BeforeReset, ActionStatus::Succeeded, ActionFailure::None, 116));
    Memory.Reset(); Search.Restart();
    assert(!Memory.Alert && !Memory.HasObservation && Memory.LastSeen == -1000);
    assert(Search.Index == 0 && Search.RetryAt == 0);
    assert(!WantsWalk(MovePurpose::Pursuit, 900, 1));
    assert(!WantsWalk(MovePurpose::Search, 700, 1));
    assert(WantsWalk(MovePurpose::Search, 100, 1));
    assert(WantsWalk(MovePurpose::Pursuit, 900, .7));
    assert(WantsWalk(MovePurpose::Return, 900, 1));
    TraceRing Ring; Ring.Reset(8);
    InputSnapshot Snapshot; Snapshot.Generation = 8; Snapshot.Alert = true;
    Snapshot.ActionId = A.Token; Snapshot.ActionState = A.Status;
    assert(Ring.Push(Event::Reset, Snapshot, "reset invalidates action"));
    assert(Ring.At(0).Input.ActionState == ActionStatus::None);
    Snapshot.Generation = 7;
    assert(!Ring.Push(Event::Action, Snapshot, "stale world"));
    std::cout << "PASS: 10000 bounded search/failure transitions; persistent contact; destination-scoped retry; fresh observation during retry; all five action kinds reject stale authority/replacement/reset/death requests; reload commits once; gait purposes; schema-2 trace. Runtime S01/S06/S07/S10 remain PENDING OWNER.\n";
}
