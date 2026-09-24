#pragma once
#include "CombatMovement.h"
#include <algorithm>
#include <cmath>
#include <cstdint>

namespace CombatAI
{
enum class MotionGate : std::uint8_t { Ready, Authority, Airborne, Gait, Speed, Vertical };
struct FireMotion
{
    double Speed = 0, VerticalSpeed = 0;
    bool Authority = false, Grounded = false, Walking = false;
    // Supplied by the achieved movement stack. Legacy fixtures retain their cap.
    double SpeedLimit = CombatMovement::BaseSpeed;
    MotionGate Gate() const
    {
        if (!Authority) return MotionGate::Authority;
        if (!Grounded) return MotionGate::Airborne;
        if (!Walking && Speed > 15) return MotionGate::Gait;
        if (!std::isfinite(SpeedLimit) || SpeedLimit <= 0 || !std::isfinite(Speed) || Speed < 0 || Speed > SpeedLimit + 1.0) return MotionGate::Speed;
        if (!std::isfinite(VerticalSpeed) || std::abs(VerticalSpeed) > 45) return MotionGate::Vertical;
        return MotionGate::Ready;
    }
    double SpreadCost(double Maximum) const
    { return std::clamp(Maximum, 0.0, 4.0) * std::clamp(Speed / std::max(1.0, SpeedLimit), 0.0, 1.0); }
    bool operator==(const FireMotion&) const = default;
};
enum class MobilePhase : std::uint8_t { None, Strafe, Approach, Cooldown };
enum class FireGate : std::uint8_t { Ready, Authority, Contact, Stance, Motion, Pose, Lean, Alignment, Muzzle };
}
