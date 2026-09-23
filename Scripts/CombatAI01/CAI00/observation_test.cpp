// Pure production-header checks: no engine world, actor, rendering or gameplay.
#include "../../../Source/MeridianSquad/CombatAIObservation.h"
#include <cassert>
#include <cstring>
#include <iostream>
#include <type_traits>
#include <set>

using namespace CombatAI;

int main()
{
    static_assert(std::is_trivially_copyable_v<InputSnapshot>);
    static_assert(std::is_standard_layout_v<InputSnapshot>);
    static_assert(!std::is_convertible_v<PrivilegedFairnessTrace, InputSnapshot>);
    std::set<std::uint32_t> Seeds;
    for (std::uint32_t I = 0; I < 1024; ++I)
    {
        auto S = AgentSeed(102, I);
        assert(S == AgentSeed(102, I));
        assert(S != AgentSeed(103, I));
        assert(S <= 0x7fffffffu);
        assert(Seeds.insert(S).second);
    }
    TraceRing A, B;
    A.Reset(7); B.Reset(7);
    InputSnapshot Input;
    Input.Generation = 7; Input.Seed = AgentSeed(102, 0);
    Input.HasMemory = true; Input.TargetEvidence = Evidence::LastSight;
    Input.KnownGround = {12, 34, 56}; Input.KnownAim = {12, 34, 180};
    for (int I = 0; I < 1000; ++I)
    {
        Input.WorldTime = I * .12; Input.SightEventId = I + 1;
        assert(A.Push(Event::DecisionInput, Input, "identical permitted evidence"));
        assert(B.Push(Event::DecisionInput, Input, "identical permitted evidence"));
    }
    assert(A.Size() == TraceCapacity && A.Total() == 1000);
    assert(A.At(0).Sequence == 937 && A.At(63).Sequence == 1000);
    for (std::size_t I = 0; I < A.Size(); ++I)
    {
        const auto& X = A.At(I); const auto& Y = B.At(I);
        assert(X.Input == Y.Input);
        assert(X.Sequence == Y.Sequence && X.Kind == Y.Kind && X.Reason == Y.Reason);
        assert(X.Input.WorldTime == Y.Input.WorldTime && X.Input.Seed == Y.Input.Seed);
        assert(X.Input.SightEventId == Y.Input.SightEventId);
        assert(X.Input.KnownGround.X == Y.Input.KnownGround.X);
        assert(X.Input.KnownAim.Z == Y.Input.KnownAim.Z);
    }
    // Records own their values. Caller mutation cannot rewrite the captured observation.
    Input.KnownGround.X = 9999;
    assert(A.At(63).Input.KnownGround.X == 12);
    PrivilegedFairnessTrace HiddenA, HiddenB;
    HiddenA.ActualPlayerPosition = {1,2,3}; HiddenB.ActualPlayerPosition = {900,800,700};
    assert(A.At(63).Input == B.At(63).Input); // Separate diagnostic values cannot enter this API.
    A.Reset(8);
    assert(A.Size() == 0 && A.Total() == 0);
    assert(!A.Push(Event::Sight, Input, "stale generation"));
    assert(A.Size() == 0 && A.Total() == 0);
    Input.Generation = 8;
    char LongReason[300]; std::memset(LongReason, 'x', sizeof(LongReason)); LongReason[299] = 0;
    assert(A.Push(Event::Reset, Input, LongReason));
    assert(A.At(0).Sequence == 1 && A.At(0).Input.Generation == 8);
    assert(std::strlen(A.At(0).Reason.data()) == 95);
    assert(A.At(0).Input.Seed == AgentSeed(102, 0));
    std::cout << "PASS: seed stability/distinct slots, 1000-event bounded replay, ordered eviction, owned values, reset, stale-generation rejection, bounded reasons\n";
    std::cout << "default seed=102 slots=0,1,2 agent_seeds=" << AgentSeed(102,0) << "," << AgentSeed(102,1) << "," << AgentSeed(102,2) << " ring_bytes=" << sizeof(TraceRing) << "\n";
}
