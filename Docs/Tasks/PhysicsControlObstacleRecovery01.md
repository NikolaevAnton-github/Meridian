# PhysicsControlObstacleRecovery01: obstacle-aware living get-up

Multica issue: **MSQ-94**.
Stage 5 of [PhysicsControlRefinement01](PhysicsControlRefinement01Plan.md).
Predecessor: [PhysicsControlCounterbalance01](PhysicsControlCounterbalance01.md).
Planning only; follow the parent authorization, preservation and verification rules.

## Scope

Address repeated aborted get-up attempts near walls and other obstacles. Validate
support, the occupied body volume and the relevant get-up path before committing.
Use a feasible existing back/stomach recovery route or a bounded safe orientation
choice when available; do not rotate or teleport the body through geometry.
Preserve the full pose-snapshot transition and original get-up sources.

Give blocked recovery an explicit finite retry/backoff policy. If space stays
blocked, remain physically down and retry only under a stated condition or bounded
interval. React safely when the obstacle/support changes during recovery. This
stage uses removable simple obstacles on static support and does not implement
navigation, tactical relocation or a new get-up animation library.

## Acceptance

- Demonstrate a near-wall case with enough room for a valid recovery and a case
  with no valid route. Show continuous footage from physical rest through success
  or the stated blocked state, with no clipping, forced standing or retry loop.
- Remove or move the blocking fixture and demonstrate a subsequent valid attempt;
  add one obstruction during an active attempt and verify safe interruption.
- Preserve feasible final foot placement and anatomical stance. Check a newly
  coupled hit/death interruption and reset of retry/obstacle state; reuse unaffected
  get-up evidence rather than rerunning all falls and animations.

Deliver `Docs/PhysicsControlObstacleRecovery01.md` and focused evidence under
`Saved/CombatSlice01/PhysicsControlObstacleRecovery01/`. No lobby geometry edits,
automatic navigation escape or guaranteed recovery from every tangled pose.
