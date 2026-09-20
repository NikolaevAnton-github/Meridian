# PhysicsControlUnevenGround01: recovery on static uneven support

Multica issue: **MSQ-95**.
Stage 5 of [PhysicsControlRefinement01](PhysicsControlRefinement01Plan.md).
Predecessor: [PhysicsControlObstacleRecovery01](PhysicsControlObstacleRecovery01.md).
Planning only; follow the parent authorization, preservation and verification rules.

## Scope

Extend the flat-floor recovery envelope to static slopes, different foot heights
and rough fixed support using removable fixtures. Resolve each foot against the
actual local surface and supported footprint, not a shared horizontal ground plane.
Coordinate sole orientation, pelvis height and leg reach while retaining corrected
knee bend and bounded foot/ankle rotation. Validate both destination support and
the swing path; clear a small obstruction only within the declared reach envelope.

Declare supported slope, height difference, footprint/edge margin, step height and
clearance limits from measured behavior. Rough terrain does not imply that every
point contact or near-vertical face is usable. Reject insufficient, unreachable or
obstructed support and retain a physical fallback. This stage supplies ground
contact for later movement; its recovery steps do not establish rubble traversal.

## Acceptance

- Demonstrate one slope and one unequal-height/fixed-rubble recovery on a
  representative mannequin, including visible swing clearance and settling at the
  displaced stance. Record surface geometry and the measured operating envelope.
- Measure stable sole contact against each local surface, retaining the existing
  grounding tolerance where applicable and documenting any justified change.
  Support feet stay planted and knees/ankles remain plausible within leg reach.
- Reject one edge/insufficient footprint and one obstructed or excessive-height
  destination. Verify the affected support-loss/fall/get-up transition on uneven
  ground; no suspension, clipping or standing on a rejected point.
- Check reset/recreation clears surface state. Reuse unchanged timing and flat-floor
  checks; record any specific regression that requires repeating them.

Deliver `Docs/PhysicsControlUnevenGround01.md` and focused evidence under
`Saved/CombatSlice01/PhysicsControlUnevenGround01/`. No dynamic debris, level
redesign, stair locomotion system or whole-scene terrain matrix.
