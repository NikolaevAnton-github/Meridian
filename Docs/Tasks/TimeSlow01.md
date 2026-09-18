# TimeSlow01: controllable time slowdown

Multica issue: **MSQ-75**.
Stage 8 of [CombatSlice01](CombatSlice01Plan.md).
Predecessor: [EnvironmentDestruction01](EnvironmentDestruction01.md).

## Scope

Implement the player's requested time-slowing ability with a documented prototype
contract: input, hold/toggle behavior, world/player time relationship, duration,
recovery/cost, eligibility and clear active/recovering feedback. These are working
rules because the product brief leaves them open. Audit occupied bindings before
choosing a key; retain the current rifle actions unless a remap is documented.

Apply slowdown coherently to enemy perception/actions, firing/reloads, body physics,
destructible objects and effects. State which UI/resource timers use real time.
Keep the world/player relationship explicit; this ability does not give the spatial
antagonist time control. No skill tree or permanent upgrade system.

## Acceptance

- Enter and leave slowdown under clear control and cost limits; inactive state
  restores the recorded normal time values exactly.
- Compare actual shot cadence, ammo consumption and reload commit timing before,
  during and after slowdown for player and enemy under the declared time policy.
- Exercise activation/release during firing, reload and moving debris; there are
  no duplicated events, unstable physics or audio/effect state stuck in slowdown.
- Death, restart and end of PIE restore the time state and resource/UI correctly;
  repeated input cannot stack unintended multipliers or evade the chosen limits.

Follow the parent plan. Deliver `Docs/TimeSlow01.md`, the controls/tuning contract
and focused runtime/video evidence, not a full animation regression.
