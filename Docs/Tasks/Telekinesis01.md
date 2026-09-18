# Telekinesis01: acquire, hold and throw objects

Multica issue: **MSQ-77**.
Stage 11 of [CombatSlice01](CombatSlice01Plan.md).
Predecessor: [ForcePush01](ForcePush01.md).

## Scope

Implement one-target acquisition, stable holding, release and throwing for a
bounded whitelist of existing movable objects. State prototype controls, range,
mass limits, line of sight, hold position, cost/recovery and cancel behavior. Living
enemy levitation, large structural objects and multi-object control are excluded
from this first slice unless separately scoped.

Define whether rifle fire/reload is allowed during acquisition/holding/throwing
and how action ownership returns on release. Rejected requests consume no resources
and cannot strand rifle locks or create a partial reload/hold state.

Prevent held objects from clipping through walls, obstructing the camera indefinitely
or launching the player. Define behavior when the held object breaks or loses its
valid target state. Thrown impact damage uses the established damage path with a
bounded velocity/energy rule and protections against repeated resting-contact hits.

## Acceptance

- Acquire only eligible visible targets and hold one object predictably while
  moving/aiming near walls. A second acquire cannot leak the first constraint.
- Release/throw restores the correct simulation/collision; impacts damage eligible
  enemies/objects once per defined impact, not once per tick forever.
- Verify force push and slowdown while holding/throwing, target destruction,
  range loss, cancellation and exhausted resources under explicit policies.
- Player death, encounter restart and PIE exit release targets and constraints;
  no object remains frozen or carries a stale owner reference.
- Check accepted/rejected activation while firing/reloading, and fire/reload input
  while holding, according to the documented compatibility policy.

Follow the parent plan. Deliver `Docs/Telekinesis01.md`, controls/eligibility/tuning
and focused gameplay/physics evidence. No inventory or new asset-production scope.
