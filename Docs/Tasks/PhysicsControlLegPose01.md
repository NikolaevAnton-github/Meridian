# PhysicsControlLegPose01: anatomical leg alignment after recovery steps

Multica issue: **MSQ-91**.
Stage 1 of [PhysicsControlRefinement01](PhysicsControlRefinement01Plan.md).
Predecessor: [PhysicsControlStepping01 / MSQ-89](PhysicsControlStepping01.md).
The owner [authorized execution without independent review](../Approvals/PhysicsControlLegPose01-OwnerStart01.json)
on 2026-09-20. Follow the parent's preservation and focused verification rules.
The executor owns implementation and focused self-checks; the controller accepts
scope, candidate identity, evidence applicability and preservation. No independent
reviewer is dispatched. Final visual and motion/play judgement remains with the owner.
Use one existing Multica Unreal executor at verified native Astra/max/standard.

## Scope

Correct the unnatural knee/ankle/foot relationship and residual crouched or twisted
stance shown in the [owner screenshot](../Approvals/PhysicsControlRefinement01-LegPose01.png).
Reproduce the observed post-step defect before tuning. A screenshot identifies the
symptom, not a proven unique cause. Inspect the existing bend-plane selection,
preserved foot rotation, pelvis reach, accumulated stance targets and effective
joint limits only as needed to establish the cause.

Use stable anatomical bend directions and feasible thigh/calf twist. Coordinate
pelvis height/orientation, stance width and foot yaw with reachable leg geometry.
Finish each episode in a credible standing pose at the new location; do not retain
a distorted solved pose as the next neutral baseline. If the stance cannot settle
without moving a planted foot, use the remaining corrective step within the retained
two-step limit, or fail safely. Do not slide planted feet or widen physical limits
indiscriminately to conceal an impossible target. Solver choice stays an
implementation decision; a framework rewrite is not a requirement.

## Acceptance

- Show before/after rear and side views of the reported defect and continuous
  footage through landing and settling. Knees bend consistently with the stance;
  feet do not remain excessively turned relative to the knees or pelvis.
- Complete representative left/right recovery and repeated episodes without
  accumulating twist, knee flips, hyperextension or a progressively crouched rest
  pose. Record effective joint/stance bounds and observed values; do not invent
  anatomical precision from a single screenshot.
- Preserve meaningful support-foot planting, leg reach and calibrated sole contact.
  Check one infeasible stance fallback and the changed step-to-stand transition;
  a failed recovery must retain physical collapse/get-up rather than suspension.
- Reuse unaffected stepping evidence. Check reset clears any new neutral-pose or
  bend state; final visual/motion judgement belongs to the owner.

Deliver `Docs/PhysicsControlLegPose01.md` and a focused identified candidate under
`Saved/CombatSlice01/PhysicsControlLegPose01/`. No adaptive gait, terrain support,
new get-up clips or autonomous locomotion is added in this correction.

## Execution handoff, 2026-09-20

The existing Multica Unreal executor owns implementation and the sole editor
writer lease for this run. Read the owner authorization above and the MSQ-89
implementation/handoff. Confirm live project, map, PIE and dirty packages through
official Epic MCP before mutations; preserve an active owner-controlled session.
Keep unrelated owner edits in `Config/DefaultEngine.ini` and
`MeridianSquad.uproject`; controller fingerprints are under
`Saved/CombatSlice01/PhysicsControlLegPose01/Controller/`.

First reproduce and document the defect on the retained baseline before changing
runtime code. Use the existing focused probes and recorder, extending only the
needed leg/stance observations. Keep full evidence, concise progress and immutable
candidate manifests under `Saved/CombatSlice01/PhysicsControlLegPose01/Worker/`.
Show measured effective joint/stance bounds, before/after comparable rear and side
views and ordinary-speed continuous landing/settling footage. Focus self-checks
on the acceptance rows above; use one representative mannequin and reuse unaffected
MSQ-89 evidence. No independent reviewer or variant comparison is requested.

Deliver the implementation report, changed-file list, passing focused results and
honest remaining limits. No commit, profile/status administration, asset registration
or successor dispatch by the worker; the controller owns those steps. Keep internal
progress and reports in English. Release the editor writer lease at handoff, leaving
the retained lobby ready for owner Play unless an owner-controlled session appears;
preserve and report any such session. Do not claim owner motion/play acceptance.

## Implementation handoff, 2026-09-20

Candidate07 supplies corrected neutral-frame leg solving and settled stance,
bounded corrective steps and retained infeasible-target physical fall/get-up.
The final build and 183 focused self-check assertions pass. See the
[implementation report](../PhysicsControlLegPose01.md) and
[controller handoff](../PhysicsControlLegPose01Handoff.md) for candidate identity,
applicable reused evidence, recordings and limits. Independent review remains
waived for MSQ-91; final owner motion/play acceptance is pending. No successor
is authorized by this handoff.
