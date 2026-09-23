#pragma once

#include "CombatAIAction.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>

// Production value contracts. These types have no actor or world-position getter.
namespace CombatAI
{
struct Position
{
    double X = 0, Y = 0, Z = 0;
    bool operator==(const Position&) const = default;
};
inline double Distance2D(Position A, Position B) { return std::hypot(A.X-B.X, A.Y-B.Y); }
inline bool Finite(Position P) { return std::isfinite(P.X) && std::isfinite(P.Y) && std::isfinite(P.Z); }
enum class Sense : std::uint8_t { Sight, Step, Landing, Shot, Impact, Damage };
enum class SourceTeam : std::uint8_t { Unknown, Player, Enemy, Environment };

struct StimulusData
{
    std::uint64_t Id = 0, Generation = 0, ProjectileGeneration = 0, Shot = 0;
    std::uint32_t Observer = 0, KnownIdentity = 0;
    Sense Kind = Sense::Step;
    SourceTeam Category = SourceTeam::Unknown;
    // World occurrence is the world frame where the producer ran. No conversion
    // from the separate finite-projectile timeline or real presentation clock.
    double OccurredWorld = 0, ReceivedWorld = 0, SimulationTime = -1;
    Position Region, Bearing;
    double Confidence = 0, Uncertainty = 0, Strength = 0;
    bool operator==(const StimulusData&) const = default;
};

// Immutable to consumers; attribution/lifecycle handles live only in the adapter.
class Stimulus
{
    StimulusData Data;
public:
    Stimulus() = default;
    explicit Stimulus(StimulusData In) : Data(In) {}
    const StimulusData& Get() const { return Data; }
};

inline double MaxDeliveryAge(Sense Kind) { return Kind == Sense::Step ? 1.2 : 3.0; }
inline bool Fresh(const StimulusData& S, std::uint64_t Generation, double Now)
{
    return S.Id != 0 && S.Generation == Generation && Finite(S.Region) && Finite(S.Bearing) &&
        std::isfinite(Now) && std::isfinite(S.OccurredWorld) && std::isfinite(S.ReceivedWorld) &&
        S.OccurredWorld <= S.ReceivedWorld && S.ReceivedWorld <= Now &&
        Now - S.OccurredWorld <= MaxDeliveryAge(S.Kind) &&
        std::isfinite(S.Confidence) && S.Confidence > 0 && S.Confidence <= 1 &&
        std::isfinite(S.Uncertainty) && S.Uncertainty >= 0 &&
        std::isfinite(S.Strength) && S.Strength >= 0 &&
        (S.Kind == Sense::Sight || (S.KnownIdentity == 0 && S.Uncertainty >= 100));
}
inline bool EligibleSound(SourceTeam Team, Sense Kind, bool DirectVictim)
{
    if (Team == SourceTeam::Enemy) return false;
    return Kind != Sense::Sight && (Kind != Sense::Damage || DirectVictim);
}

struct AcousticResult { bool Audible = false; Position Region; double Radius = 0, Confidence = 0; };
inline AcousticResult LocalizeSound(Position Emission, double Distance, double Range, bool Blocked)
{
    AcousticResult R;
    if (!Finite(Emission) || !std::isfinite(Distance) || !std::isfinite(Range) || Distance < 0 || Range <= 0) return R;
    const double EffectiveRange = Range * (Blocked ? .55 : 1.0);
    if (Distance > EffectiveRange) return R;
    R.Radius = std::clamp(140 + Distance*.12 + (Blocked ? 220 : 0), 140.0, 650.0);
    // Stable quantization cannot be averaged into an exact hidden trajectory by
    // repeated step events. Radius describes localization, not reachable topology.
    const double Cell = R.Radius;
    R.Region = {std::round(Emission.X/Cell)*Cell, std::round(Emission.Y/Cell)*Cell, Emission.Z};
    R.Confidence = std::clamp((1-Distance/EffectiveRange)*.55 + .25 - (Blocked ? .1 : 0), .15, .8);
    R.Audible = true;
    return R;
}

struct Hypothesis
{
    bool Valid = false;
    Stimulus Evidence;
    double ConfidenceAt(double Now) const
    {
        const auto& E = Evidence.Get();
        return Valid ? E.Confidence / (1 + std::max(0.0, Now-E.OccurredWorld)/8) : 0;
    }
};
class Knowledge
{
    struct Receipt
    {
        std::uint64_t Id=0, Shot=0, ProjectileGeneration=0;
        Sense Kind=Sense::Sight;
    };
    std::array<Receipt, 64> Seen{};
    std::size_t NextSeen = 0;
public:
    std::uint64_t Generation = 0, Revision = 0;
    std::array<Hypothesis, 4> Hypotheses{};
    bool Alert = false;
    double LastSight = -1000, LastLoud = -1000;
    void Reset(std::uint64_t InGeneration) { *this = {}; Generation = InGeneration; }
    bool Accept(const Stimulus& Record, double Now)
    {
        const auto& E = Record.Get();
        if (!Fresh(E, Generation, Now)) return false;
        for (const auto& Prior : Seen)
            if (Prior.Id==E.Id || (E.Shot && Prior.Shot==E.Shot &&
                Prior.ProjectileGeneration==E.ProjectileGeneration && Prior.Kind==E.Kind)) return false;
        Seen[NextSeen] = {E.Id,E.Shot,E.ProjectileGeneration,E.Kind}; NextSeen = (NextSeen+1) % Seen.size();
        if (E.Kind == Sense::Step && E.OccurredWorld < LastLoud + .35) return false;
        if (E.Kind == Sense::Shot || E.Kind == Sense::Damage) LastLoud = E.OccurredWorld;
        // Out-of-order weaker events cannot drag intent behind fresher evidence.
        auto* Slot = &Hypotheses[0];
        for (auto& H : Hypotheses)
        {
            if (H.Valid && H.Evidence.Get().Kind == E.Kind &&
                Distance2D(H.Evidence.Get().Region, E.Region) <= std::max(160.0, E.Uncertainty))
            { if (H.Evidence.Get().OccurredWorld > E.OccurredWorld) return false; Slot = &H; break; }
            if (!H.Valid || (Slot->Valid && H.ConfidenceAt(Now) < Slot->ConfidenceAt(Now))) Slot = &H;
        }
        *Slot = {true, Record}; Alert = true; ++Revision;
        if (E.Kind == Sense::Sight) LastSight = E.OccurredWorld;
        return true;
    }
    const Hypothesis* Dominant(double Now, bool CurrentSight) const
    {
        const Hypothesis* Best = nullptr;
        for (const auto& H : Hypotheses) if (H.Valid)
        {
            const auto& E = H.Evidence.Get();
            const double Age = std::max(0.0, Now-E.OccurredWorld);
            // Silence never invents a new position. Old hypotheses remain regions
            // with declining confidence, rather than an extrapolated live target.
            if (CurrentSight && E.Kind==Sense::Sight && Age<.5) return &H;
            if (!Best || E.OccurredWorld>Best->Evidence.Get().OccurredWorld ||
                (E.OccurredWorld==Best->Evidence.Get().OccurredWorld && E.Confidence>Best->Evidence.Get().Confidence)) Best=&H;
        }
        return Best;
    }
    bool RetainsContact(double Now) const { return Now >= LastSight && Now-LastSight <= .5; }
};

template<class Visible>
int FirstVisibleSample(int Count, Visible Test)
{
    for (int I=0; I<std::min(Count,3); ++I) if (Test(I)) return I;
    return -1;
}

enum class MotionEvent : std::uint8_t { None, Step, Landing };
struct MotionSample
{
    Position Feet;
    double WorldTime = 0;
    std::uint64_t Generation = 0;
    bool Grounded = false, Crouched = false, Running = false, Enabled = true;
};
struct MotionEmission
{
    MotionEvent Kind = MotionEvent::None;
    double Range = 0, Volume = 0;
};
class GroundTravel
{
    MotionSample Previous;
    bool Initialized = false;
    double Distance = 0, AirStarted = 0, AirHeight = 0, LastEmit = -1000;
    bool HadFlight = false;
public:
    void Reset() { *this = {}; }
    MotionEmission Advance(const MotionSample& S)
    {
        MotionEmission E;
        if (!Finite(S.Feet) || !std::isfinite(S.WorldTime)) { Reset(); return E; }
        const double Dt = S.WorldTime-Previous.WorldTime;
        const double Travel = Distance2D(S.Feet, Previous.Feet);
        if (!Initialized || S.Generation != Previous.Generation || !S.Enabled || !Previous.Enabled ||
            Dt < 0 || Dt > .5 || Travel > std::max(120.0, Dt*2200) || std::abs(S.Feet.Z-Previous.Feet.Z) > 200)
        {
            Previous=S; Initialized=true; Distance=0; HadFlight=false;
            AirStarted=S.WorldTime; AirHeight=S.Feet.Z; return E;
        }
        if (Dt == 0) return E;
        if (!S.Grounded)
        {
            if (Previous.Grounded) { AirStarted=Previous.WorldTime; AirHeight=Previous.Feet.Z; }
            HadFlight |= S.WorldTime-AirStarted >= .12 && std::abs(S.Feet.Z-AirHeight) >= 12;
            Distance=0;
        }
        else if (!Previous.Grounded)
        {
            if (HadFlight) E = {MotionEvent::Landing, S.Crouched ? 750.0 : 1500.0, S.Crouched ? .22 : .7};
            HadFlight=false; Distance=0;
        }
        else
        {
            // Use displacement, never requested velocity/input. Stop and blocked
            // locomotion cannot repeatedly pay a stride; no accumulated air travel.
            if (Travel/Dt < 2) Distance=0;
            else Distance += Travel;
            const double Stride = S.Crouched ? 115 : S.Running ? 175 : 150;
            if (Distance >= Stride && S.WorldTime-LastEmit >= .08)
            {
                E = {MotionEvent::Step, S.Crouched ? 180.0 : S.Running ? 2000.0 : 900.0,
                    S.Crouched ? .06 : S.Running ? .85 : .45};
                Distance = std::fmod(Distance, Stride); // At most one event; no hitch catch-up burst.
            }
        }
        if (E.Kind != MotionEvent::None) LastEmit=S.WorldTime;
        Previous=S;
        return E;
    }
};
}
