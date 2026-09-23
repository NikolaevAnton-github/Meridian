# EnemyCombat01: one functioning combat opponent

Multica issue: **MSQ-70**.
Stage 4 of [CombatSlice01](CombatSlice01Plan.md).

## Current owner authorization

On 2026-09-23 the owner [authorized direct implementation outside Multica and
reserved testing for themselves](../Approvals/EnemyCombat01-OwnerStart02.json).
Use the delivered GASPALS armed foundation and current physical corrections.
This delivery uses native build and focused source checks, with one independent
source reviewer; no agent gameplay, firing, PIE automation or visual tests.
The runtime acceptance rows below remain owner test criteria, not claimed passes.
Do not start Multica execution or any successor task.

Candidate01/build03 is now delivered for owner testing. See the
[implementation and controls](../EnemyCombat01.md),
[sole independent source review](../EnemyCombat01Review.md) and
[controller acceptance](../EnemyCombat01Acceptance.md). Native build and source
checks pass; gameplay/visual criteria remain pending the owner's test. This direct
delivery does not change Multica execution state or authorize MSQ-71.

## Foundation

Predecessor: [EnemyPrototype01](EnemyPrototype01.md), with its asset contract.
The later [owner priority decision](../Approvals/GASPEnemyFoundation01-TaskCreation01.json)
adds [GASPEnemyFoundation01 / MSQ-98](GASPEnemyFoundation01.md) as a prerequisite.
Consume its adopted character, damage interfaces and demonstrated flat-floor
movement/recovery handover. This task still owns perception, pursuit/navigation,
aiming, actual enemy weapon setup and autonomous firing; the migration does not
complete those features. Retain MSQ-69 and native CombatSlice stage 4.
The later [PhysicsControlVariants01 / MSQ-85](PhysicsControlVariants01.md) adopts
Physics Control and removes the legacy enemy from active gameplay under
[the owner's decision](../Approvals/PhysicsControlVariants01-OwnerScope01.json).
Read its verified handoff before dispatch and carry the adopted response/death
behavior forward; do not silently restore the old active enemy. Its supported
stationary fixtures do not establish locomotion or autonomous balance. Integrate
the required movement within this task without claiming that those are already solved.

## Scope

Implement one enemy that detects the player, pursues through reachable space,
stops/aims and fires, responds to incoming damage and dies. Use configurable
perception/range/timing and a small readable state model. Loss of sight must have
a stated finite search/return policy; no perfect tracking through walls.

Enemy fire uses the established hit/damage path and real obstruction checks.
Supply a damage event suitable for the next player-health task; during this stage
verify it on an instrumented receiver. Player death is not claimed yet. Establish
enemy cadence and ammunition/reload policy without inventing an inventory system.
Expose held-weapon and hand-occupancy state for later
[MSQ-99 disarming](EnemyDisarm01.md) and [MSQ-100 wound gestures](EnemyWoundReaction01.md).
Those low-priority follow-ups do not block this task or MSQ-71.

Use existing lobby geometry and bounded navigation support. Do not move columns,
alter passages or add rooms to rescue pathfinding. Keep spawn and reset repeatable.
Dead actors stop AI, shots, timers and movement before death physics/presentation.

The later [PhysicsControlRefinement01 / MSQ-90](PhysicsControlRefinement01Plan.md)
plans corrected stance and uneven/moving support. Consume its applicable completed
handoffs and define how ordinary movement transfers to hit-recovery steps and back
without conflicting foot targets or stale support. Do not replace adopted physical
response with the old enemy implementation. MSQ-70 establishes autonomous combat locomotion;
real destruction-rubble traversal is an explicit integration row in MSQ-78 after
MSQ-74 produces representative debris. Preserve this task's existing predecessor
and stage, with MSQ-98 added above: these links do not authorize those later tasks or create a dependency
on MSQ-74/MSQ-78 before enemy movement can be implemented.

## Acceptance

- Demonstrate acquisition, reachable movement, obstruction/lost sight, attack,
  hit reaction and death on the identified enemy prototype.
- Enemy shots cannot pass through retained cover; verify damage events and timing
  separately from muzzle/sound presentation. No fire from dead actors or a stale
  target after reset.
- Unreachable destinations fail cleanly instead of oscillating or accumulating
  tasks. A bounded restart restores one opponent with no duplicate controllers.
- Inspect actual gameplay views for aim, movement and hit/death readability;
  technical AI checks do not accept final enemy art.
- Demonstrate the affected movement-to-hit-recovery-to-movement handover at the
  displaced position using the applicable Physics Control candidate. Document
  support/placement interfaces needed for the later rubble crossing; stationary
  recovery steps alone do not satisfy this task's reachable movement requirement.

No squad tactics, enemy variants, progression or a full behavior framework.
Follow the parent plan; deliver `Docs/EnemyCombat01.md` and focused evidence.
