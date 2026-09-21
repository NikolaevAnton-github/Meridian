# EnemyDisarm01: weapon loss and disarmed enemy behavior

Multica issue: **MSQ-99**.
Low-priority unstaged child of [CombatSlice01 / MSQ-67](CombatSlice01Plan.md).
Prerequisites: [GASPEnemyFoundation01 / MSQ-98](GASPEnemyFoundation01.md) and
[EnemyCombat01 / MSQ-70](EnemyCombat01.md), including an actual enemy weapon setup.
See [the owner's task-creation and priority decision](../Approvals/GASPEnemyFoundation01-TaskCreation01.json).
Planning only: backlog, unassigned, zero runs; no automatic execution.
This secondary feature does not block migration, MSQ-71 or base combat progression.

## Scope

Implement a configurable disarm rule using authoritative hit/contact and enemy
state. Document qualifying and nonqualifying conditions; hit region, weapon contact,
impulse and injury thresholds are implementation choices, not fixed owner rules.
Reuse existing contact/weapon capabilities; any new weapon hit shape must integrate
with the established finite-flight projectile path without duplicate damage.

Release all relevant hand grips and attachments once, preserving the weapon's
world transform and plausible inherited motion as independent weapon physics starts.
Enter a defined disarmed state that stops firing, aiming and reloading and clears
stale hand targets. Keep ammunition/weapon ownership consistent. Define bounded
collision, sleep and reset cleanup; do not add an inventory or autonomous retrieval.

Coordinate hand use with balance, fall protection and get-up. If
[EnemyWoundReaction01](EnemyWoundReaction01.md) has landed, reuse its hand arbitration
and check the newly coupled interaction. Neither secondary task requires the other.
Death and reset have explicit precedence and cannot duplicate or reattach a released
weapon accidentally. Preserve the existing player weapon and controls.

## Focused acceptance

- One qualifying real hit disarms the correct enemy once; one nonqualifying hit
  retains the weapon. Record inputs, trigger policy and authoritative hit evidence.
- The released weapon moves independently without a transform snap, duplicate
  ownership or continued shots/reload. Both hand targets agree with the new state.
- Check one affected fall/death transition, repeat trigger, reset cleanup and
  changed weapon motion/timing under existing slowdown. Reuse unchanged combat tests.
- Show ordinary-speed continuous footage on one representative armed enemy.

Deliver `Docs/EnemyDisarm01.md` and focused evidence under
`Saved/CombatSlice01/EnemyDisarm01/`. Use the shared preservation, one-writer,
verified max/standard execution and one-primary-reviewer rules in
[GASPEnemyFoundation01](GASPEnemyFoundation01.md). Owner motion judgement is separate.
No new paid assets, protagonist/lobby work, dismemberment or successor dispatch.
