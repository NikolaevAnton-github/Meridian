# PhysicsControlAdaptiveSteps01: disturbance-driven recovery steps

Multica issue: **MSQ-92**.
Stage 2 of [PhysicsControlRefinement01](PhysicsControlRefinement01Plan.md).
Predecessor: [PhysicsControlLegPose01](PhysicsControlLegPose01.md).
Planning only; follow the parent authorization, preservation and verification rules.

## Scope

Replace the single fixed recovery-step size/timing with bounded adaptation to
actual body displacement, lean and momentum. Use hit impulse as an input, while
choosing support and direction from the current body state. Small recoverable
disturbances should receive a small correction; larger recoverable disturbances
may need a longer/faster step or the retained second step. Excessive disturbance
must still cause a physical fall.

Choose length, lift and phase timing together with reachable leg geometry, valid
placement and a clear swing path. Bound/filter changes so a new impulse does not
produce abrupt retargeting, toe scraping or perpetual replanning. Keep at most
two steps per episode. Record the numeric tuning and the transition thresholds
as implementation choices, not owner-approved constants. Static flat support
remains this stage's terrain envelope.

## Acceptance

- Compare two meaningfully different recoverable disturbances on one mannequin.
  Record inputs and resulting displacement, lift and duration, and show visible
  scaling with convincing weight transfer and the corrected final stance.
- Verify one mid-step disturbance/replan and one excessive or blocked case.
  The step budget is finite, the swing clears the floor and unsafe targets lead
  to a safe fallback rather than forced placement or hidden support.
- Preserve planted-foot contact and the new anatomical alignment. Check the changed
  timing under relative slowdown and clear adaptive episode state on reset.
  Reuse unaffected damage, death and get-up evidence.

Deliver `Docs/PhysicsControlAdaptiveSteps01.md` and focused evidence under
`Saved/CombatSlice01/PhysicsControlAdaptiveSteps01/`. No navigation, pursuit,
arbitrary multi-step walking or new ability implementation.
