#pragma once

#include <cstdint>

// Engine-independent contracts used by the live executor and its focused tests.
namespace CombatAI
{
struct EncounterMemory
{
    bool Alert = false;
    bool HasObservation = false;
    double LastSeen = -1000;
    void Observe(double Now) { Alert = HasObservation = true; LastSeen = Now; }
    void Reset() { *this = {}; }
};

enum class ActionKind : std::uint8_t { None, Move, Aim, Burst, Reload, Observe };
enum class ActionStatus : std::uint8_t { None, Running, Succeeded, Canceled, Failed };
enum class ActionFailure : std::uint8_t { None, Replaced, Authority, Death, Reset, Stopped, Route, Timeout, Weapon, Sight, Obstruction };
enum class MovePurpose : std::uint8_t { Pursuit, Search, Return, Cautious, Cover };

struct ActionToken
{
    std::uint64_t Generation = 0, Id = 0;
    bool operator==(const ActionToken&) const = default;
};

struct ActionRuntime
{
    ActionToken Token;
    ActionKind Kind = ActionKind::None;
    ActionStatus Status = ActionStatus::None;
    ActionFailure Failure = ActionFailure::None;
    double Started = 0, Updated = 0;

    bool Accepts(ActionToken Request) const
    { return Status == ActionStatus::Running && Request == Token; }
    void Reset(std::uint64_t Generation)
    {
        Token = {Generation, Token.Id + 1}; Kind = ActionKind::None;
        Status = ActionStatus::None; Failure = ActionFailure::None; Started = Updated = 0;
    }
    ActionToken Start(std::uint64_t Generation, ActionKind NewKind, double Now)
    {
        // IDs never repeat on an individual executor, even for a same-generation reset.
        Token = {Generation, Token.Id + 1}; Kind = NewKind;
        Status = ActionStatus::Running; Failure = ActionFailure::None;
        Started = Updated = Now;
        return Token;
    }
    bool Update(ActionToken Request, double Now)
    {
        if (!Accepts(Request)) return false;
        Updated = Now; return true;
    }
    bool Finish(ActionToken Request, ActionStatus Outcome, ActionFailure Why, double Now)
    {
        if (!Accepts(Request) || Outcome == ActionStatus::Running || Outcome == ActionStatus::None) return false;
        Status = Outcome; Failure = Why; Updated = Now; return true;
    }
};

struct DestinationBackoff
{
    double X = 0, Y = 0, Until = 0;
    void Set(double GoalX, double GoalY, double Deadline) { X = GoalX; Y = GoalY; Until = Deadline; }
    bool Blocks(double GoalX, double GoalY, double Now) const
    { const double DX = X - GoalX, DY = Y - GoalY; return Now < Until && DX * DX + DY * DY < 160.0 * 160.0; }
};

struct LocalSearchCycle
{
    static constexpr int CandidateCount = 9; // Last sight, four area points, four local points.
    int Index = 0;
    double RetryAt = 0;
    void Restart() { Index = 0; RetryAt = 0; }
    void Advance(double Now, double ShortPause, double CyclePause)
    {
        Index = (Index + 1) % CandidateCount;
        RetryAt = Now + (Index == 0 ? CyclePause : ShortPause);
    }
};

inline bool WantsWalk(MovePurpose Purpose, double Remaining, double TurnDot)
{ return Purpose == MovePurpose::Return || Purpose == MovePurpose::Cautious || Purpose == MovePurpose::Cover || Remaining < 250.0 || TurnDot < 0.8; }
}
