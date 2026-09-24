#pragma once

#include "CombatAIAction.h"
#include <array>
#include <algorithm>
#include <cmath>

namespace CombatAI
{
enum WeaponCapability : unsigned { DirectFire = 1, CoverFire = 2, CautiousMove = 4 };
struct WeaponProfile
{
    unsigned Capabilities = DirectFire | CoverFire | CautiousMove;
    double EffectiveRange = 5500, PreferredRange = 2800, AdvanceStep = 450;
    double Reaction = .08, Aim = .10, Interval = .18, Rest = .45;
    int Burst = 3;
    bool Valid() const
    {
        return (Capabilities & DirectFire) && std::isfinite(EffectiveRange) && EffectiveRange >= 150 &&
            std::isfinite(PreferredRange) && PreferredRange >= 100 && PreferredRange <= EffectiveRange &&
            std::isfinite(AdvanceStep) && AdvanceStep > 0 && AdvanceStep <= 600 &&
            std::isfinite(Reaction) && Reaction >= 0 && std::isfinite(Aim) && Aim >= 0 &&
            std::isfinite(Interval) && Interval >= .08 && std::isfinite(Rest) && Rest >= .1 && Burst >= 1 && Burst <= 8;
    }
    bool operator==(const WeaponProfile&) const = default;
};
struct HealthKnowledge
{
    bool Known = false;
    double Fraction = 0, ObservedAt = 0, ExpiresAt = 0;
    std::uint64_t Generation = 0, EvidenceId = 0, Identity = 0;
    bool Usable(std::uint64_t G, std::uint64_t TargetIdentity, double Now) const
    {
        return Known && Generation == G && Identity == TargetIdentity && EvidenceId != 0 &&
            std::isfinite(Fraction) && Fraction >= 0 && Fraction <= 1 &&
            std::isfinite(ObservedAt) && std::isfinite(ExpiresAt) && ObservedAt <= Now &&
            ExpiresAt > Now && ExpiresAt-ObservedAt <= 5;
    }
    bool operator==(const HealthKnowledge&) const = default;
};
struct AllySummary
{
    bool Known = false;
    int Available = 0;
    // Composition by capability, not actor classes: these buckets may overlap.
    std::array<int,3> Capable{}; // direct fire, cover fire, cautious movement
    bool Valid() const
    {
        return Known && Available >= 0 && Available <= 16 &&
            std::all_of(Capable.begin(), Capable.end(), [&](int N){return N >= 0 && N <= Available;});
    }
    bool operator==(const AllySummary&) const = default;
};
struct TacticalContext
{
    WeaponProfile Weapon;
    bool WeaponUsable = false, SelfHealthKnown = false;
    double SelfHealth = 0;
    HealthKnowledge TargetHealth;
    AllySummary Allies;
    bool operator==(const TacticalContext&) const = default;
};
struct RiskPreference
{
    double Protection = 1, CautiousAttack = 0;
};
inline RiskPreference EvaluateRisk(const TacticalContext& C)
{
    const bool SelfKnown = C.SelfHealthKnown && std::isfinite(C.SelfHealth) && C.SelfHealth >= 0 && C.SelfHealth <= 1;
    const double Self = SelfKnown ? C.SelfHealth : .5;
    const bool TargetKnown = C.TargetHealth.Known && std::isfinite(C.TargetHealth.Fraction) && C.TargetHealth.Fraction >= 0 && C.TargetHealth.Fraction <= 1;
    const double Advantage = SelfKnown && TargetKnown ? std::max(0.0, Self-C.TargetHealth.Fraction) : 0;
    const double Support = C.Allies.Valid() ? std::min(1.0, C.Allies.Capable[0]*.12 + C.Allies.Capable[1]*.12 + C.Allies.Capable[2]*.04) : 0;
    return {1 + (1-Self)*2.5, std::clamp(Advantage*.8 + Support*.3 - (1-Self)*.2, 0.0, 1.0)};
}
enum class RangeIntent : std::uint8_t { NoWeapon, HoldRange, SeekLane, CautiousAdvance, FavorProtection };
inline RangeIntent SelectRangeIntent(const TacticalContext& C, double Distance, bool LaneBlocked)
{
    if (!C.WeaponUsable || !C.Weapon.Valid() || !std::isfinite(Distance) || Distance < 0) return RangeIntent::NoWeapon;
    // A blocked barrel never changes the range goal to the target's feet.
    if (LaneBlocked) return RangeIntent::SeekLane;
    if (Distance <= C.Weapon.EffectiveRange) return RangeIntent::HoldRange;
    if (!(C.Weapon.Capabilities & CautiousMove) || EvaluateRisk(C).Protection > 2.65) return RangeIntent::FavorProtection;
    return RangeIntent::CautiousAdvance;
}
inline double CautiousStep(const TacticalContext& C, double Distance)
{
    return SelectRangeIntent(C, Distance, false) == RangeIntent::CautiousAdvance ?
        std::clamp(Distance-C.Weapon.PreferredRange, 0.0, C.Weapon.AdvanceStep) : 0;
}
inline bool CoverTransferEligible(const TacticalContext& C, double Travel, bool HasUsefulContact, bool Blocked)
{
    if (!C.WeaponUsable || !C.Weapon.Valid() || !(C.Weapon.Capabilities & CoverFire) || !std::isfinite(Travel) || Travel < 0) return false;
    if (!HasUsefulContact || Blocked) return Travel <= 1200;
    const auto Risk = EvaluateRisk(C);
    // Hurt agents accept a longer protected transfer. A known advantage/support
    // favors retaining a useful firing range instead of taking distant cover.
    const double Limit = 450 + (Risk.Protection-1)*180 - Risk.CautiousAttack*150;
    return Travel <= Limit;
}
enum class CoverSide : std::uint8_t { None, Left, Right, Up };
enum class CoverPhase : std::uint8_t { None, ToAnchor, Protected, Exposing, Aiming, Firing, Returning };
enum class CoverGate : std::uint8_t { None, Geometry, Travel, Crouch, Stand, Contact, WeaponSafety, Rest, Reload, Stale, ReturnFailed, Deadline, NoOption };
struct CoverFeatures
{
    bool Protected = false, AnchorClear = false, PoseClear = false, Lane = false;
    bool Outbound = false, Return = false, InRange = false;
    double Travel = 0, ExposureTravel = 0, Protection = 0;
    CoverSide Side = CoverSide::None;
};
inline double CoverScore(const CoverFeatures& F, const TacticalContext& C)
{
    if (!C.WeaponUsable || !C.Weapon.Valid() || !(C.Weapon.Capabilities & CoverFire) ||
        F.Side == CoverSide::None || !F.Protected || !F.AnchorClear || !F.PoseClear || !F.Lane ||
        !F.Outbound || !F.Return || !F.InRange || !std::isfinite(F.Travel) || F.Travel < 0 ||
        !std::isfinite(F.ExposureTravel) || F.ExposureTravel < 0 || F.ExposureTravel > 600 ||
        !std::isfinite(F.Protection) || F.Protection < 0 || F.Protection > 1) return -1e9;
    const auto Risk = EvaluateRisk(C);
    return 100 + F.Protection * 80 * Risk.Protection - F.Travel*.08 - F.ExposureTravel*.10 +
        Risk.CautiousAttack * (40 - std::min(F.ExposureTravel,400.0)*.08);
}
inline int SelectCoverSide(const std::array<CoverFeatures,3>& Options, const TacticalContext& C)
{
    int Best = -1; double Score = -1e9;
    for (int I = 0; I < 3; ++I)
    {
        const double S = CoverScore(Options[I], C);
        if (S > Score) { Score=S; Best=I; }
    }
    return Best;
}
// Bound commitment separately from phase deadlines and the final bounded return. Sight loss caused
// by our own cover pose is not invalidation; stale evidence and relocation are.
inline bool CoverEvidenceValid(double Now, double LastSeen, double Started, double ThreatShift)
{
    return std::isfinite(Now) && std::isfinite(LastSeen) && Now >= LastSeen &&
        Now-LastSeen <= 6 && Now-Started <= 12 && ThreatShift <= 180;
}
}
