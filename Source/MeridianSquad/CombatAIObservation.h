#pragma once
#include "CombatAIMobile.h"

#include <array>
#include <cstdint>
#include <cstddef>
#include "CombatAIAction.h"
#include "CombatAITactics.h"
#include "CombatAISenses.h"

// Value-only decision capture. No UObject, target getter or fairness input.
namespace CombatAI
{
constexpr std::uint32_t SchemaVersion = 5;
constexpr std::size_t TraceCapacity = 64;
constexpr std::uint32_t DefaultEncounterSeed = 102;

// Versioned integer-only mixing, independent of actor names, addresses and reset count.
constexpr std::uint32_t AgentSeed(std::uint32_t EncounterSeed, std::uint32_t SpawnIndex)
{
    std::uint32_t X = EncounterSeed ^ (0x9e3779b9u * (SpawnIndex + 1u));
    X ^= X >> 16; X *= 0x85ebca6bu;
    X ^= X >> 13; X *= 0xc2b2ae35u;
    return (X ^ (X >> 16)) & 0x7fffffffu;
}

enum class Evidence : std::uint8_t { None, Sight, LastSight, Sound, Bearing };
enum class PathOutcome : std::uint8_t { None, Planning, Ready, Following, Arrived, Failed, Canceled };
enum class Event : std::uint8_t { Reset, DecisionInput, Sight, SightLost, State, Path, Shot, Stop, Authority, Action, Tactical, Stimulus };

struct InputSnapshot
{
    std::uint64_t Generation = 0;
    std::uint32_t EncounterSeed = DefaultEncounterSeed, SpawnIndex = 0, Seed = 0;
    double WorldTime = 0, DeltaSeconds = 0;
    Position SelfFeet, Home, KnownGround, KnownAim;
    Position ActionGoal, SearchAnchor, SearchLook;
    double LastSeenWorldTime = -1000, StateStarted = 0;
    double ReadyAt = 0, NextShot = 0, MoveRetryAt = 0, WeaponRetryAt = 0, SearchRetryAt = 0;
    ActionToken ActionId;
    ActionKind Action = ActionKind::None;
    ActionStatus ActionState = ActionStatus::None;
    ActionFailure Failure = ActionFailure::None;
    double ActionStarted = 0, ActionUpdated = 0;
    TacticalObjective Objective = TacticalObjective::None;
    TacticalPhase PositionPhase = TacticalPhase::None;
    ContactKind Contact = ContactKind::None;
    DecisionGate Gate = DecisionGate::None;
    ActionToken AssignmentId;
    Position SelectedPosition, SelectedFacing;
    double ContactAt = 0, ContactDecisionAt = 0, ObjectiveDecidedAt = 0, ScanStartedAt = 0;
    double ContactUntil = 0, AimUntil = 0, PauseUntil = 0, ReloadUntil = 0;
    double HoldStartedAt = 0, MoveStartedAt = 0, NextReassess = 0, NextSector = 0, EvidenceAge = -1;
    double PositionScore = InvalidPositionScore, Protection = 0, Exposure = 1;
    TacticalContext Context;
    RangeIntent Range = RangeIntent::NoWeapon;
    CoverPhase Cover = CoverPhase::None;
    CoverSide Side = CoverSide::None;
    CoverGate CoverWait = CoverGate::None;
    ActionToken CoverOwner;
    Position CoverAnchor, CoverPose, CoverThreat;
    double CoverStarted = 0, CoverPhaseAt = 0, NextCoverScan = 0;
    int CoverBursts = 0;
    bool CoverScanning = false;
    ActionToken MovementId;
    ActionStatus MovementState = ActionStatus::None;
    ActionFailure MovementFailure = ActionFailure::None;
    MobilePhase Mobile = MobilePhase::None;
    Position MobileGoal;
    double MobileStarted = 0, NextMobileAt = 0, MovingSpread = 0;
    FireMotion Motion;
    FireGate LaunchGate = FireGate::Contact;
    double LeanRequested = 0, LeanAnimated = 0;
    bool LeanCaptured = false;
    int CandidateCount = 0, EvaluatedCount = 0, RejectedCount = 0, TransferAttempts = 0, LookSector = -1;
    int GeometryQueries = 0, PeakAssessmentQueries = 0;
    bool Scanning = false, HasPosition = false;
    std::array<int, static_cast<std::size_t>(PositionRejection::Count)> Rejections{};
    std::array<char, 96> TacticalReason{};
    int SearchIndex = 0;
    bool Alert = false, RequestedWalk = true;
    bool RequestedCrouch = false, ActualCrouch = false, RetainedContact = false;
    StimulusData DominantEvidence;
    std::uint64_t KnowledgeRevision = 0;
    MovePurpose Purpose = MovePurpose::Pursuit;
    std::uint64_t SightEventId = 0;
    // Native EEnemyCombatState / EGASPEnemyAuthority numeric values in schema v1.
    std::uint8_t Intent = 0, Authority = 0;
    Evidence TargetEvidence = Evidence::None;
    PathOutcome Path = PathOutcome::None;
    bool Enabled = false, Ready = false, HasMemory = false, Visible = false;
    bool Dead = false, RifleHeld = false, RightHandOccupied = false;
    int Magazine = 0, Shots = 0, SpreadState = 0, PathRemaining = 0, PathFailures = 0;
    bool operator==(const InputSnapshot&) const = default;
};

struct TraceEntry
{
    std::uint64_t Sequence = 0;
    Event Kind = Event::Reset;
    InputSnapshot Input;
    // UTF-8/ASCII diagnostic text, bounded and never an actor reference.
    std::array<char, 96> Reason{};
};

class TraceRing
{
public:
    void Reset(std::uint64_t NewGeneration)
    {
        Generation = NewGeneration; Count = Head = 0; NextSequence = 1;
        Entries = {}; // Invalidate even overwritten storage, not only visible count.
    }
    bool Push(Event Kind, const InputSnapshot& Input, const char* Reason)
    {
        if (Input.Generation != Generation) return false;
        TraceEntry Entry{};
        Entry.Sequence = NextSequence++; Entry.Kind = Kind; Entry.Input = Input;
        if (Reason)
            for (std::size_t I = 0; I + 1 < Entry.Reason.size() && Reason[I]; ++I) Entry.Reason[I] = Reason[I];
        Entries[Head] = Entry; Head = (Head + 1) % TraceCapacity;
        if (Count < TraceCapacity) ++Count;
        return true;
    }
    const TraceEntry& At(std::size_t Index) const { return Entries[(Head + TraceCapacity - Count + Index) % TraceCapacity]; }
    std::size_t Size() const { return Count; }
    std::uint64_t Total() const { return NextSequence - 1; }
private:
    std::array<TraceEntry, TraceCapacity> Entries{};
    std::size_t Count = 0, Head = 0;
    std::uint64_t Generation = 0, NextSequence = 1;
};

// Proposed future pressure-gate diagnostic channel only. Never embedded in InputSnapshot
// or TraceEntry and never consumed by the CAI-00 legacy policy. No live actor handles.
struct PrivilegedFairnessTrace
{
    std::uint64_t Generation = 0, ProposalId = 0;
    double WorldTime = 0, ReconsiderAt = 0;
    Position ActualPlayerPosition, CameraPosition, CameraForward;
    bool Granted = false;
    std::array<char, 96> DebugOnlyReason{};
};
}
