# TimeSlow01: controllable world slowdown and stop

Multica issue: **MSQ-75**.
Stage 9 of [CombatSlice01](CombatSlice01Plan.md).
Predecessor: [EnvironmentDestruction01](EnvironmentDestruction01.md).

## Scope

Implement the player's requested time-slowing/stopping ability under the
[original owner policy](../Approvals/CombatFoundation01-OwnerScope01.json), amended
for slowdown by [the 2026-09-19 decision](../Approvals/PhysicsControlVariants01-OwnerScope01.json).
During slowdown, player movement and firing also slow, but less than the world;
MSQ-85 starts with adjustable world 0.25 and player 0.65 rates. All player/enemy
bullets follow world time. Full stop was not changed by that bounded request:
retain normal player movement during stop pending this task's implementation.
Own bullets can injure the player. Use the MSQ-68 finite-flight
and separate-time seam; do not replace it with immediate hitscan damage.

Document the remaining prototype choices: input, hold/toggle behavior, duration,
recovery/cost, eligibility, player action timing and clear active/recovering
feedback. These choices remain tunable. Audit occupied bindings before
choosing a key; retain the current rifle actions unless a remap is documented.

Apply slowdown coherently to enemy perception/actions, firing/reloads, body physics,
destructible objects and effects. State which UI/resource timers use real time.
Keep the world/player relationship explicit; this ability does not give the spatial
antagonist time control. No skill tree or permanent upgrade system.

## Acceptance

- Enter and leave slowdown under clear control and cost limits; inactive state
  restores the recorded normal time values exactly.
- During slowdown, measure player movement/firing at their declared intermediate
  rate and all bullets/bodies at the lower world rate; avoid double scaling or
  catch-up bursts when crossing time-mode boundaries.
- Exact stop preserves world/projectile position and simulation age while player
  movement remains normal; resumption preserves stored velocity. Moving into a
  suspended own/enemy bullet produces the declared single damage event. Verify
  newly fired bullets during stop, launch clearance and bounded accumulation.
- Compare actual shot cadence, ammo consumption and reload commit timing before,
  during and after slowdown for player and enemy under the declared time policy.
- Exercise activation/release during firing, reload and moving debris; there are
  no duplicated events, unstable physics or audio/effect state stuck in slowdown.
- Death, restart and end of PIE restore the time state and resource/UI correctly;
  repeated input cannot stack unintended multipliers or evade the chosen limits.

Follow the parent plan. Deliver `Docs/TimeSlow01.md`, the controls/tuning contract
and focused runtime/video evidence, not a full animation regression.
