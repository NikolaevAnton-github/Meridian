# PhysicsControlLegPose01: anatomical leg alignment after recovery steps

Multica issue: **MSQ-91**.
Stage 1 of [PhysicsControlRefinement01](PhysicsControlRefinement01Plan.md).
Predecessor: [PhysicsControlStepping01 / MSQ-89](PhysicsControlStepping01.md).
Planning only; follow the parent authorization, preservation and verification rules.

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
