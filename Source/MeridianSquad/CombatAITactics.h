#pragma once

#include "CombatAIAction.h"
#include <array>
#include <algorithm>
#include <cmath>
#include <limits>

// Value-only coordinator/selection contracts. Geometry comes from the local adapter;
// neither an actor reference nor privileged player data is an input here.
namespace CombatAI
{
enum class TacticalObjective : std::uint8_t { None, Engage, ProtectedObservation };
enum class ContactKind : std::uint8_t { None, Initial, Continuous, Brief, Known, NewDirection };
enum class TacticalPhase : std::uint8_t { None, Scanning, Moving, Holding, Fallback };
enum class DecisionGate : std::uint8_t { None, Disabled, Physics, Readiness, Reload, Contact, Aim, BurstPause, Cadence, Path, Travel, Scan, Observation, WeaponBackoff, RouteBackoff, LaunchSafety };
enum class PositionRejection : std::uint8_t { None, Support, Capsule, Route, Facing, RecentFailure, Arrival, Count };

struct CoordinatorInput
{
    bool Alert = false, HasEvidence = false, Visible = false, CanAct = false;
};
inline TacticalObjective SelectObjective(const CoordinatorInput& Input)
{
    if (!Input.CanAct || !Input.Alert || !Input.HasEvidence) return TacticalObjective::None;
    return Input.Visible ? TacticalObjective::Engage : TacticalObjective::ProtectedObservation;
}

// One member owns one assignment now. Later group policy can supply the same
// assignment; it must not write personal memory or execute movement directly.
struct TacticalAssignment
{
    ActionToken Token;
    TacticalObjective Objective = TacticalObjective::None;
    std::uint64_t EvidenceId = 0;
    double DecidedAt = 0;
    void Assign(std::uint64_t Generation, TacticalObjective NewObjective, std::uint64_t Evidence, double Now)
    { Token = {Generation, Token.Id + 1}; Objective = NewObjective; EvidenceId = Evidence; DecidedAt = Now; }
    void Cancel(std::uint64_t Generation)
    { Assign(Generation, TacticalObjective::None, 0, 0); }
    bool Accepts(ActionToken Request) const
    { return Objective != TacticalObjective::None && Request == Token; }
};

inline ContactKind ClassifyContact(bool WasAlert, bool HadEvidence, bool WasVisible, double Age, double DirectionDot)
{
    if (!WasAlert || !HadEvidence) return ContactKind::Initial;
    if (DirectionDot < .5) return ContactKind::NewDirection; // More than 60 degrees.
    if (WasVisible) return ContactKind::Continuous;
    return Age <= 1.5 ? ContactKind::Brief : ContactKind::Known;
}

struct ResponseGates
{
    double ContactUntil = 0, AimUntil = 0, PauseUntil = 0, ReloadUntil = 0;
    void Sight(ContactKind Kind, double Now, double InitialDelay)
    {
        if (Kind == ContactKind::Continuous || Kind == ContactKind::None) return;
        const double Delay = Kind == ContactKind::Initial ? InitialDelay : Kind == ContactKind::NewDirection ? .2 : 0;
        // Brief hiding cannot cancel an unpaid first-contact deadline.
        ContactUntil = std::max(ContactUntil, Now + Delay);
    }
    double ReadyAt(double NextShot) const
    { return std::max({ContactUntil, AimUntil, PauseUntil, ReloadUntil, NextShot}); }
};

struct TransferBudget
{
    int Attempts = 0;
    double ResetAt = 0;
    void Refresh(double Now)
    { if (Now >= ResetAt) { Attempts = 0; ResetAt = Now + 12; } }
    bool CanStart() const { return Attempts < 2; }
    bool Start() { if (!CanStart()) return false; ++Attempts; return true; }
};

constexpr int TacticalSectors = 8;
constexpr int MaxTacticalCandidates = 29; // Current + 8 surfaces * 3 + 4 nearby probes.
constexpr int MaxTacticalTransfers = 2;
constexpr double InvalidPositionScore = -1e9;
inline int Sector(int Index) { return (Index + TacticalSectors * 2) % TacticalSectors; }
inline int BitCount(unsigned Mask)
{
    int Count = 0;
    for (int I = 0; I < TacticalSectors; ++I) Count += (Mask >> I) & 1u;
    return Count;
}

struct PositionFeatures
{
    bool Supported = false, CapsuleClear = false, RouteClear = false;
    std::array<double, TacticalSectors> OpenDistance{};
    unsigned ProtectionMask = 0, WeaponMask = 0, EscapeMask = 0, RegionVisibleMask = 0;
    double Exposure = 1, Travel = 0;
};
struct PositionRating
{
    bool Valid = false;
    int Facing = -1;
    unsigned OpenMask = 0;
    double Protection = 0, Exposure = 1, Score = InvalidPositionScore;
    PositionRejection Rejection = PositionRejection::None;
};
inline double SectorUtility(const PositionFeatures& F, int I)
{
    if ((F.WeaponMask & (1u << I)) == 0 || F.OpenDistance[I] < 220) return InvalidPositionScore;
    const auto Protected = [&](int Offset) { return double((F.ProtectionMask >> Sector(I + Offset)) & 1u); };
    const double Rear = (Protected(3) + Protected(4) + Protected(5)) / 3;
    const double Side = (Protected(2) + Protected(6)) / 2;
    // Sector 0 faces the remembered region. Free approaches take precedence over
    // staring at that point through a wall. No target height enters held facing.
    const double ThreatAlignment = std::cos(I * 3.141592653589793 / 4);
    return Rear * 24 + Side * 16 + std::min(F.OpenDistance[I], 600.0) / 30 + ThreatAlignment * 6;
}
inline PositionRating RatePosition(const PositionFeatures& F)
{
    PositionRating R;
    if (!F.Supported) { R.Rejection = PositionRejection::Support; return R; }
    if (!F.CapsuleClear) { R.Rejection = PositionRejection::Capsule; return R; }
    if (!F.RouteClear) { R.Rejection = PositionRejection::Route; return R; }
    if (!std::isfinite(F.Exposure) || F.Exposure < 0 || F.Exposure > 1 || !std::isfinite(F.Travel) || F.Travel < 0)
    { R.Rejection = PositionRejection::Route; return R; }
    double Best = InvalidPositionScore;
    for (int I = 0; I < TacticalSectors; ++I)
    {
        if (!std::isfinite(F.OpenDistance[I]) || F.OpenDistance[I] < 0) { R.Rejection = PositionRejection::Facing; return R; }
        const double Utility = SectorUtility(F, I);
        if (Utility > InvalidPositionScore) R.OpenMask |= 1u << I;
        if (Utility > Best) { Best = Utility; R.Facing = I; }
    }
    if (R.Facing < 0) { R.Rejection = PositionRejection::Facing; return R; }
    const auto Protected = [&](int Offset) { return double((F.ProtectionMask >> Sector(R.Facing + Offset)) & 1u); };
    const double Rear = (Protected(3) + Protected(4) + Protected(5)) / 3;
    const double Side = (Protected(2) + Protected(6)) / 2;
    R.Protection = Rear * .6 + Side * .4;
    R.Exposure = std::clamp(F.Exposure, 0.0, 1.0);
    R.Score = R.Protection * 60 + (1 - R.Exposure) * 30 + Best * .35 +
        std::min(BitCount(R.OpenMask), 5) * 2 + std::min(BitCount(F.EscapeMask), 3) * 6 - F.Travel * .025;
    R.Valid = true;
    return R;
}

inline bool WorthSwitching(const PositionRating& Held, const PositionRating& Proposed,
    double HoldAge, double Travel, bool RecentlyVisited, double Commitment, double Margin, double ProbeAfter)
{
    if (!Proposed.Valid) return false;
    if (!Held.Valid) return true;
    if (RecentlyVisited) return false;
    if (HoldAge < Commitment || Travel < 100) return false;
    if (Proposed.Score > Held.Score + Margin) return true;
    const int NovelSectors = BitCount(Proposed.OpenMask & ~Held.OpenMask);
    // A stale hold can yield to a safer informative neighboring look. A timer
    // alone never licenses an exposed walk or a move between equivalent points.
    return HoldAge >= ProbeAfter && Travel <= 450 && NovelSectors > 0 &&
        Proposed.Protection >= Held.Protection - .1 && Proposed.Exposure <= Held.Exposure + .05 &&
        Proposed.Score + std::min(NovelSectors, 2) * 12 > Held.Score + Margin;
}

inline bool AcceptTacticalArrival(const PositionRating& Selected, const PositionRating& Actual)
{
    return Selected.Valid && Actual.Valid && Actual.Protection + .15 >= Selected.Protection &&
        Actual.Exposure <= Selected.Exposure + .34;
}

inline int ObservationSector(const PositionFeatures& F, unsigned ViewedMask)
{
    int Best = -1;
    double Score = InvalidPositionScore;
    for (int I = 0; I < TacticalSectors; ++I)
    {
        const double Value = SectorUtility(F, I);
        if (Value <= InvalidPositionScore) continue;
        const double Weighted = Value - ((ViewedMask & (1u << I)) ? 80 : 0);
        if (Weighted > Score) { Score = Weighted; Best = I; }
    }
    return Best;
}

// Constant storage, spatially coalesced failures/visits, world-clock expiry.
struct PositionHistory
{
    struct Entry { double X = 0, Y = 0, Until = 0; };
    std::array<Entry, 8> Entries{};
    std::size_t Next = 0;
    bool Contains(double X, double Y, double Now) const
    {
        for (const auto& E : Entries)
            if (Now < E.Until && (X-E.X)*(X-E.X) + (Y-E.Y)*(Y-E.Y) < 120*120) return true;
        return false;
    }
    void Remember(double X, double Y, double Until)
    {
        for (auto& E : Entries)
            if ((X-E.X)*(X-E.X) + (Y-E.Y)*(Y-E.Y) < 120*120 && E.Until > 0)
            { E = {X,Y,Until}; return; }
        Entries[Next] = {X,Y,Until}; Next = (Next + 1) % Entries.size();
    }
};
}
