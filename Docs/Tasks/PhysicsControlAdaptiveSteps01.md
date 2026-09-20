# PhysicsControlAdaptiveSteps01: disturbance-driven recovery steps

Multica issue: **MSQ-92**.
Stage 3 of [PhysicsControlRefinement01](PhysicsControlRefinement01Plan.md).
Predecessor: [PhysicsControlRecoverability01 / MSQ-97](PhysicsControlRecoverability01.md).
The owner [authorizes execution and approximately 25 percent faster recovery](../Approvals/PhysicsControlAdaptiveSteps01-OwnerStart01.json).
Use MSQ-97 Candidate07 (closure commit `5cd5b67`) as the implementation baseline.
Follow the parent preservation and focused verification rules.

Candidate06 is delivered with a passing Development Editor build and 208 focused
self-check assertions. One primary independent reviewer passes all six scoped
criteria with no blocking findings. See the [implementation](../PhysicsControlAdaptiveSteps01.md)
and [controller handoff](../PhysicsControlAdaptiveSteps01Handoff.md). Final owner
motion/play judgement remains separate; this delivery does not start MSQ-93.

## Execution and review

One existing Multica Unreal executor implements and self-checks at verified native
Astra/max/standard. One primary independent technical reviewer owns the scoped
acceptance rows below, including actual motion evidence; previous task waivers do
not extend here. The controller accepts scope, evidence applicability, finding
closure and preservation. Final motion/play judgement remains with the owner.
MSQ-93 and successors remain undispatched.

Start with ordinary recovery response and stepping about 25 percent faster than
MSQ-97's default. The controller's initial interpretation is `RecoverySpeed=1.25`,
with comparable reaction/phase durations divided by 1.25 (20 percent shorter).
Keep that setting adjustable and distinguish it from disturbance-driven geometry
and timing. Preserve impulse strength, world/player slowdown and physical fallback.
Record actual configured/effective timings and show the faster baseline in the
focused motion evidence; final tuning remains open to owner play feedback.

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
