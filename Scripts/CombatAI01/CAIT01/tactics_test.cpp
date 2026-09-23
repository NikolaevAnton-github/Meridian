#include "../../../Source/MeridianSquad/CombatAITactics.h"
#include "../../../Source/MeridianSquad/CombatAIObservation.h"
#include <cstdlib>
#include <iostream>

using namespace CombatAI;
static int Checks = 0;
void Check(bool Pass, const char* Name)
{
    ++Checks;
    if (!Pass) { std::cerr << "FAIL " << Name << '\n'; std::exit(1); }
    std::cout << "PASS " << Name << '\n';
}
PositionFeatures Open()
{
    PositionFeatures F;
    F.Supported = F.CapsuleClear = F.RouteClear = true;
    F.OpenDistance.fill(600); F.WeaponMask = 255; F.EscapeMask = 85;
    return F;
}
PositionFeatures Protected()
{
    auto F = Open(); F.ProtectionMask = 0x7c; F.WeaponMask = 0x83;
    for (int I = 2; I <= 6; ++I) F.OpenDistance[I] = 70;
    F.EscapeMask = 5; F.Exposure = 1.0/3; F.Travel = 400;
    return F;
}
int main()
{
    const auto Exposed = RatePosition(Open()), Safe = RatePosition(Protected());
    Check(Safe.Valid && Safe.Score > Exposed.Score + 30 && Safe.Protection > .9, "T01 collision protection outranks exposed shorter position");
    for (int Mask = 0; Mask < 7; ++Mask)
    {
        auto F = Protected(); F.Supported = (Mask&1)!=0; F.CapsuleClear = (Mask&2)!=0; F.RouteClear = (Mask&4)!=0;
        const auto R = RatePosition(F);
        if (R.Valid || R.Score != InvalidPositionScore) return 2;
    }
    Check(true, "T01 every invalid support/capsule/route combination rejected");
    auto F = Protected(); F.OpenDistance.fill(100);
    Check(!RatePosition(F).Valid, "T01 enclosed position cannot claim useful facing");
    F = Open(); F.WeaponMask = 0;
    Check(!RatePosition(F).Valid, "T01 no usable weapon space rejected");
    F = Open(); F.OpenDistance[0] = 219; F.WeaponMask = 1;
    Check(!RatePosition(F).Valid, "T01 short look into wall rejected at boundary");
    F.OpenDistance[0] = 220;
    Check(RatePosition(F).Valid, "T01 useful look boundary accepted");
    for (double V : {-1.0, 1.01, std::numeric_limits<double>::infinity(), std::numeric_limits<double>::quiet_NaN()})
    { F = Open(); F.Exposure = V; if (RatePosition(F).Valid) return 3; }
    for (double V : {-1.0, std::numeric_limits<double>::infinity(), std::numeric_limits<double>::quiet_NaN()})
    {
        F = Open(); F.Travel = V; if (RatePosition(F).Valid) return 4;
        F = Open(); F.OpenDistance[3] = V; if (RatePosition(F).Valid) return 5;
    }
    Check(true, "T01 invalid numeric geometry/cost inputs rejected");
    F = Protected(); F.Travel += 100;
    Check(RatePosition(F).Score < Safe.Score, "T01 additional travel penalized");
    F = Protected(); F.Exposure = 1;
    Check(RatePosition(F).Score < Safe.Score, "T01 larger threat-region exposure penalized");
    F = Protected(); F.EscapeMask = 0;
    Check(RatePosition(F).Score < Safe.Score, "T01 fewer validated escapes penalized");
    Check(Safe.Facing == 0 && (Safe.OpenMask & (1u<<Safe.Facing)), "T02 protected wall behind useful approach-facing");
    unsigned Viewed = 0;
    for (int I = 0; I < BitCount(Safe.OpenMask); ++I)
    {
        const int SectorIndex = ObservationSector(Protected(), Viewed);
        if (SectorIndex < 0 || !(Safe.OpenMask & (1u<<SectorIndex)) || (Viewed & (1u<<SectorIndex))) return 6;
        Viewed |= 1u<<SectorIndex;
    }
    Check(Viewed == Safe.OpenMask, "T02 active hold visits all useful sectors without wall/feet facing");
    F = Open(); F.WeaponMask = 0;
    Check(ObservationSector(F, 0) == -1, "T02 no fabricated valid facing in fully blocked weapon space");
    // The production seam accepts only geometry/evidence. Privileged snapshots
    // vary separately and cannot be supplied to this selector's type signature.
    PrivilegedFairnessTrace Hidden;
    for (int I = 0; I < 10000; ++I)
    {
        Hidden.ActualPlayerPosition = {double(I*19), double(-I*31), double(I%200)};
        const auto R = RatePosition(Protected());
        if (R.Score != Safe.Score || R.Facing != Safe.Facing || R.OpenMask != Safe.OpenMask) return 7;
    }
    Check(Hidden.ActualPlayerPosition.X != 0, "T02 identical permitted inputs invariant under 10000 isolated privileged positions");
    Check(ClassifyContact(false, false, false, 1000, 1) == ContactKind::Initial, "T03 initial contact classified before memory refresh");
    Check(ClassifyContact(true, true, false, .12, 1) == ContactKind::Brief, "T03 brief known reacquisition classified");
    Check(ClassifyContact(true, true, false, 20, 1) == ContactKind::Known, "T03 long absent encounter remains known");
    Check(ClassifyContact(true, true, false, .12, .49) == ContactKind::NewDirection, "T03 substantially new direction distinguished");
    Check(ClassifyContact(true, true, true, .12, .9) == ContactKind::Continuous, "T03 continuous sight does not restart reaction");
    ResponseGates G; G.Sight(ContactKind::Initial, 10, .65);
    G.Sight(ContactKind::Brief, 10.12, .65);
    Check(G.ContactUntil == 10.65, "T03 brief hide cannot bypass unpaid initial delay");
    const double Initial = G.ContactUntil;
    for (int I = 0; I < 10000; ++I) G.Sight(ContactKind::Continuous, 10+I*.12, .65);
    Check(G.ContactUntil == Initial, "T03 repeated sight does not extend deadline");
    G = {}; G.Sight(ContactKind::Brief, 20, .65);
    Check(G.ContactUntil == 20, "T03 known threat adds no redundant acquire dwell");
    G = {}; G.Sight(ContactKind::NewDirection, 20, .65);
    Check(G.ContactUntil == 20.2, "T03 new direction adds bounded 200ms response gate");
    G = {}; G.AimUntil = 21; G.PauseUntil = 22; G.ReloadUntil = 23;
    for (auto Kind : {ContactKind::Initial, ContactKind::Brief, ContactKind::Known, ContactKind::NewDirection, ContactKind::Continuous})
    {
        G.Sight(Kind, 20, .65);
        if (G.AimUntil != 21 || G.PauseUntil != 22 || G.ReloadUntil != 23 || G.ReadyAt(24) != 24) return 8;
    }
    Check(true, "T03 all contact classes preserve aim/reload/burst-pause/cadence gates");
    G.ReloadUntil = 0;
    Check(G.ReadyAt(20) == 22, "T03 completed reload does not erase existing burst pause");
    Check(!WorthSwitching(Exposed, Safe, 3.99, 400, false, 4, 10, 6), "T04 commitment prevents early ordinary replacement");
    Check(WorthSwitching(Exposed, Safe, 4, 400, false, 4, 10, 6), "T04 materially better protection replaces completed commitment");
    for (int I = 0; I < 10000; ++I)
        if (WorthSwitching(Safe, Safe, I*.1, 200, false, 4, 10, 6)) return 9;
    Check(true, "T04 identical holds do not thrash over 10000 reassessments");
    auto Narrow = Safe, Probe = Safe; Narrow.OpenMask = 1; Probe.OpenMask = 3;
    Probe.Score = Narrow.Score - 1;
    Check(!WorthSwitching(Narrow, Probe, 5.99, 200, false, 4, 10, 6) &&
        WorthSwitching(Narrow, Probe, 6, 200, false, 4, 10, 6), "T04 stale hold yields to informative safe adjacent probe");
    Probe.Exposure = Narrow.Exposure + .06;
    Check(!WorthSwitching(Narrow, Probe, 10, 200, false, 4, 10, 6), "T04 information does not license additional exposure");
    Probe = Safe; Probe.Score = Narrow.Score - 1; Probe.OpenMask = 3;
    Check(!WorthSwitching(Narrow, Probe, 10, 451, false, 4, 10, 6), "T04 exploratory move limited to neighborhood");
    Check(!WorthSwitching(Exposed, Safe, 10, 200, true, 4, 10, 6), "T04 recently visited better point cannot create ping-pong");
    Check(WorthSwitching({}, Safe, 0, 200, true, 4, 10, 6), "T04 invalid hold releases commitment and visit preference");
    PositionHistory History;
    for (int I = 0; I < 10000; ++I)
    {
        History.Remember(I*200.0, 0, I+12.0);
        if (!History.Contains(I*200.0+119, 0, I+11.9) || History.Contains(I*200.0, 0, I+12.0) || History.Next >= 8) return 10;
    }
    Check(History.Entries.size() == 8, "T04 10000 failures retain constant storage and bounded expiry");
    History = {}; History.Remember(100, 100, 20); History.Remember(120, 100, 25);
    Check(History.Next == 1 && History.Contains(120, 100, 24), "T04 neighboring failures coalesce rather than flush history");
    TransferBudget Budget;
    int Starts = 0;
    for (int I = 0; I < 12000; ++I)
    { const double Now = I*.001; Budget.Refresh(Now); if (Budget.Start()) ++Starts; }
    Check(Starts == 2 && Budget.Attempts == 2, "T04 repeated scans cannot exceed two transfers per window");
    Budget.Refresh(12);
    Check(Budget.Start() && Budget.Attempts == 1 && Budget.ResetAt == 24, "T04 bounded retry opens at world-clock boundary");
    Check(!AcceptTacticalArrival(Safe, Exposed) && !AcceptTacticalArrival(Safe, {}) && AcceptTacticalArrival(Safe, Safe),
        "T01 actual arrival loses protection or validity and is rejected");
    TacticalAssignment Assignment;
    Assignment.Assign(7, SelectObjective({true,true,false,true}), 11, 1);
    const auto OldScan = Assignment.Token;
    Check(Assignment.Objective == TacticalObjective::ProtectedObservation && Assignment.Accepts(OldScan), "T05 one-member coordinator consumes permitted report");
    Assignment.Assign(7, SelectObjective({true,true,true,true}), 12, 2);
    Check(Assignment.Objective == TacticalObjective::Engage && !Assignment.Accepts(OldScan), "T05 fresh contact invalidates obsolete scan assignment");
    const auto BeforePhysics = Assignment.Token; Assignment.Cancel(7);
    Check(!Assignment.Accepts(BeforePhysics), "T05 living physics invalidates assignment in same generation");
    Assignment.Assign(8, SelectObjective({true,true,false,true}), 12, 3);
    Check(!Assignment.Accepts(OldScan) && Assignment.Objective == TacticalObjective::ProtectedObservation, "T05 recovery can reassign retained personal evidence with new token");
    Check(SelectObjective({true,true,false,false}) == TacticalObjective::None &&
        SelectObjective({false,false,false,true}) == TacticalObjective::None, "T05 dead/disabled/unaware member gets no tactical objective");
    ActionRuntime A;
    const auto Reload = A.Start(7,ActionKind::Reload,1);
    A.Finish(Reload,ActionStatus::Canceled,ActionFailure::Authority,2);
    A.Start(7,ActionKind::Observe,3);
    Check(!A.Finish(Reload,ActionStatus::Succeeded,ActionFailure::None,4), "T05 canceled reload cannot commit ammo via stale action");
    TraceRing Ring; Ring.Reset(8); InputSnapshot Input; Input.Generation=8;
    Input.Objective=Assignment.Objective; Input.AssignmentId=Assignment.Token; Input.ContactUntil=10.65; Input.PauseUntil=22;
    Input.Rejections[static_cast<std::size_t>(PositionRejection::Arrival)]=1;
    Ring.Push(Event::Tactical,Input,"actual feet");
    Check(Ring.At(0).Input == Input && Ring.At(0).Kind == Event::Tactical, "T06 bounded trace preserves tactical fields/gates/rejections");
    std::cout << "PASS " << Checks << " focused production-contract groups; no Unreal gameplay executed\n";
}
