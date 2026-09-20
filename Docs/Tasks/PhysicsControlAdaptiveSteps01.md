# PhysicsControlAdaptiveSteps01: disturbance-driven recovery steps

Multica issue: **MSQ-92**.
Stage 3 of [PhysicsControlRefinement01](PhysicsControlRefinement01Plan.md).
Predecessor: [PhysicsControlRecoverability01 / MSQ-97](PhysicsControlRecoverability01.md).
Planning only; follow the parent authorization, preservation and verification rules.

## Scope

Refine the prerequisite's necessary recovery-step geometry/timing with bounded adaptation to
actual body displacement, lean and momentum. Use hit impulse as an input, while
choosing support and direction from the current body state. Small recoverable
disturbances should receive a small correction; larger recoverable disturbances
may need a longer/faster step or further feasible recovery steps. Excessive disturbance
must still cause a physical fall.

Choose length, lift and phase timing together with reachable leg geometry, valid
placement and a clear swing path. Bound/filter changes so a new impulse does not
produce abrupt retargeting, toe scraping or perpetual replanning. The former
two-step episode cap is superseded by the [MSQ-97 next-task decision](../Approvals/PhysicsControlRecoverability01-NextTask01.json).
Retain its support, reach, actuator-effort and progress bounds for successive
reactive steps. Reuse applicable predecessor evidence instead of implementing or
testing the recoverability controller again. Record numeric tuning and thresholds
as implementation choices, not owner-approved constants. Static flat support
remains this stage's terrain envelope.

## Acceptance

- Compare two meaningfully different recoverable disturbances on one mannequin.
  Record inputs and resulting displacement, lift and duration, and show visible
  scaling with convincing weight transfer and the corrected final stance.
- Verify one mid-step disturbance/replan and one excessive or blocked case.
  Per-step and recovery-progress bounds remain enforced, the swing clears the floor and unsafe targets lead
  to a safe fallback rather than forced placement or hidden support.
- Preserve planted-foot contact and the new anatomical alignment. Check the changed
  timing under relative slowdown and clear adaptive episode state on reset.
  Reuse unaffected damage, death and get-up evidence.

Deliver `Docs/PhysicsControlAdaptiveSteps01.md` and focused evidence under
`Saved/CombatSlice01/PhysicsControlAdaptiveSteps01/`. No navigation, pursuit,
general walking or new ability implementation. Successive reactive hit-recovery
steps remain the MSQ-97 prerequisite behavior.
