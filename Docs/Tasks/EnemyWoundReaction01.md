# EnemyWoundReaction01: hand-to-wound reaction

Multica issue: **MSQ-100**.
Low-priority unstaged child of [CombatSlice01 / MSQ-67](CombatSlice01Plan.md).
Prerequisites: [GASPEnemyFoundation01 / MSQ-98](GASPEnemyFoundation01.md) and
[EnemyCombat01 / MSQ-70](EnemyCombat01.md), including weapon and hand occupancy.
See [the owner's task-creation and priority decision](../Approvals/GASPEnemyFoundation01-TaskCreation01.json).
Planning only: backlog, unassigned, zero runs; no automatic execution.
This secondary feature does not block migration, MSQ-71 or base combat progression.

## Scope

Make the wounded enemy reach toward and hold its own injured body region. Reuse
the authoritative hit bone/contact and store the target relative to the struck
body so it follows subsequent movement. Choose a suitable existing or locally
authored gesture, then use bounded hand IK/pose targets through the adopted single
PhysicsControl authority. Audit animation coverage; GASP does not establish a ready
exact-wound gesture for every hit. No animation purchase or paid generation.

Select an available, usable hand and a reachable surface target with a palm offset.
Respect elbow/joint limits and arm/body collision. Unreachable targets or unavailable
hands use an explicit safe fallback rather than stretching or penetrating the body.
Define finite hold/release times and a bounded repeated-hit update policy.

Arbitrate weapon grip, wound contact, balance/fall protection and get-up support.
State the resulting firing/aim/reload policy; no hand may serve incompatible tasks
at once. Falling/get-up/death can interrupt the gesture and reset clears it. If
[EnemyDisarm01](EnemyDisarm01.md) has landed, consume its weapon state and check the
newly coupled interaction. Neither secondary task requires the other.

## Focused acceptance

- A reachable torso hit and one reachable limb hit produce appropriate gestures
  following the wounded region as the body moves. Show contact and natural release.
- One unavailable-hand or unreachable-target case falls back safely. Record the
  chosen coverage, reach bounds and hand/weapon priority policy.
- Verify one repeated hit and affected balance/fall/get-up/death interruptions,
  reset and new gesture timing under the existing slowdown. No competing drives,
  stale world-space wound target, arm snapping or forbidden simultaneous weapon use.
- Show ordinary-speed continuous footage on one representative enemy; reuse
  unaffected damage, locomotion and physical-recovery evidence.

Deliver `Docs/EnemyWoundReaction01.md` and focused evidence under
`Saved/CombatSlice01/EnemyWoundReaction01/`. Use the shared preservation, one-writer,
verified max/standard execution and one-primary-reviewer rules in
[GASPEnemyFoundation01](GASPEnemyFoundation01.md). Owner motion judgement is separate.
This is presentation/action arbitration, not new damage, dismemberment, healing,
player grappling, AI combat policy or automatic successor execution.
