# PhysicsControlCounterbalance01: torso and arm balance during recovery

Multica issue: **MSQ-93**.
Stage 3 of [PhysicsControlRefinement01](PhysicsControlRefinement01Plan.md).
Predecessor: [PhysicsControlAdaptiveSteps01](PhysicsControlAdaptiveSteps01.md).
Planning only; follow the parent authorization, preservation and verification rules.

## Scope

Coordinate pelvis, torso and arm counter-motion with the recovery step and actual
body disturbance. Preserve the current readable hit response while giving the
upper body a useful balancing role. Limit and damp the assistance; once stable,
return smoothly to the standing pose without perpetual sway, rigid snapping or
repeated corrective impulses. Retain shoulder/arm self-collision and plausible
joint motion. Do not create arm poses that depend on a future weapon/aim system.

## Acceptance

- Show a representative lateral and fore/aft recovery through settling, with
  bounded torso/arm motion, preserved step placement and no new body penetration.
  Record assistance bounds and observed settling behavior.
- Check a repeat hit while balancing and the affected handover into physical fall
  and living get-up. Assistance must release appropriately rather than cancel a
  fall, hold a dead actor up or fight the recovery animation.
- Check any new timed damping under relative slowdown and clear counterbalance
  state on reset. Reuse unchanged foot-placement and collision evidence unless
  the altered poses invalidate it. Owner judgement determines weight and feel.

Deliver `Docs/PhysicsControlCounterbalance01.md` and focused evidence under
`Saved/CombatSlice01/PhysicsControlCounterbalance01/`. Weapon aiming integration
belongs to MSQ-70; no new animation purchase or character-art work.
