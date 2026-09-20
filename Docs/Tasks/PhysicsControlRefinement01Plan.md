# PhysicsControlRefinement01: stance, balance and terrain support

Multica issue: **MSQ-90**.
Unstaged planning family under [CombatSlice01 / MSQ-67](CombatSlice01Plan.md).
Baseline: [PhysicsControlStepping01 / MSQ-89](PhysicsControlStepping01.md),
Candidate05, closure commit `71d7d36`.

## Owner direction and authorization

The owner broadly likes the result but reports unnatural leg-joint positions
after recovery steps. The owner then agrees that uneven surfaces are necessary
because future destruction will leave debris that actors must move over, and
asks to split the discussed improvements into tasks. See the
[exact request](../Approvals/PhysicsControlRefinement01-TaskCreation01.json) and
[original stance screenshot](../Approvals/PhysicsControlRefinement01-LegPose01.png).
This feedback is not acceptance of the defective pose or unrestricted locomotion.

The original request authorized task creation and dependency planning only: the
parent and six children were created in backlog, unassigned, with zero runs.
The owner subsequently [authorized MSQ-91 execution without independent review](../Approvals/PhysicsControlLegPose01-OwnerStart01.json).
That authorization is scoped to stage 1; MSQ-92 through MSQ-96 remain undispatched.
Multica owns live status. Stage order and dependency metadata guide later dispatch;
they are not execution permission.

## Ordered implementation tasks

| Stage | Multica | Task | Required result |
| --- | --- | --- | --- |
| 1 | MSQ-91 | [PhysicsControlLegPose01](PhysicsControlLegPose01.md) | Anatomical knee/foot alignment and a credible settled stance after steps. |
| 2 | MSQ-92 | [PhysicsControlAdaptiveSteps01](PhysicsControlAdaptiveSteps01.md) | Step length, lift and timing respond to actual disturbance and safe reachable placement. |
| 3 | MSQ-93 | [PhysicsControlCounterbalance01](PhysicsControlCounterbalance01.md) | Torso and arms help balance, then settle without perpetual sway. |
| 4 | MSQ-94 | [PhysicsControlObstacleRecovery01](PhysicsControlObstacleRecovery01.md) | Obstacle-aware living get-up, finite retries and safe blocked behavior. |
| 5 | MSQ-95 | [PhysicsControlUnevenGround01](PhysicsControlUnevenGround01.md) | Ground contact and recovery steps on slopes, unequal heights and fixed rough support. |
| 6 | MSQ-96 | [PhysicsControlDebrisSupport01](PhysicsControlDebrisSupport01.md) | Contact with translating, rotating or disappearing debris, including loss of support. |

The first child depends on MSQ-89; each subsequent child consumes the verified
preceding handoff. Use the latest applicable candidate, preserving older manifests.
Stage 4 addresses the retained wall/get-up retry limitation; terrain work follows
so that blocked recovery already has a safe outcome. These are bounded increments,
not a mandatory solver, animation-system or movement-framework replacement.

## Real traversal integration

Reactive recovery at a displaced stance does not establish walking across rubble.
The owner's traversal requirement remains mandatory and is assigned explicitly to
[CombatIntegration01 / MSQ-78](CombatIntegration01.md), consuming this family plus:

- [EnemyCombat01 / MSQ-70](EnemyCombat01.md): actual enemy movement and a defined
  handover between locomotion, hit recovery and standing. Preserve usable support
  data and the terrain-contact contract; fixtures alone do not prove locomotion.
- [EnvironmentDestruction01 / MSQ-74](EnvironmentDestruction01.md): representative
  destruction debris with bounded physics, collision/navigation updates and cleanup.

MSQ-78 must demonstrate both the player and the adopted enemy entering, crossing
and leaving a representative traversable debris patch through ordinary movement.
For the enemy, include credible foot contact/clearance and the affected hit-recovery
handover. At least one supported piece must actually move or lose support. Define
which rubble is traversable and which is too high/unstable and must be rejected or
routed around; routing around the entire test pile cannot satisfy crossing it.
Teleportation, collision disabling, cosmetic rubble and permanently frozen chunks
do not satisfy this row. Reuse focused earlier evidence and check only the newly
coupled behavior and cleanup. This is not unrestricted traversal over every fragment.

Stage 6 may close its support capability against removable dynamic fixtures before
MSQ-74 exists. That closure does not close real rubble traversal: MSQ-78 retains the
explicit open integration gate until the movement and destruction prerequisites
are available. Do not make MSQ-70 depend on MSQ-74/MSQ-78 or reorder the original
CombatSlice stages. Creating these links does not dispatch any of those tasks.

## Shared acceptance and preservation

Each child defines its affected behaviors, records numeric operating limits and
provides an identified candidate, concise changes, measurements and ordinary-speed
continuous footage. Owner motion/play acceptance remains separate. Verify only
changed behavior and related transitions; reuse applicable passing evidence. For
the six-mannequin experiment, inspect the set rendering and check shared behavior
on one representative mannequin unless a distinct profile defect needs a check.
Do not run a full animation, variant or combat matrix by default.

Retain hit response, one/two-step recovery limit, true physical collapse when
recovery fails, living get-up, terminal death, damage state, self-collision and
calibrated sole contact. Preserve F6 reset without ammunition refill, F10, optional
Ctrl+F7/Ctrl+F8 controls and the 0.25 world / 0.65 player slowdown. Recheck slowdown
only where changed timing/support behavior couples to it. Reset/recreation must
clear any new episode or support references. No hidden suspension or forced
placement through geometry may make a failed recovery appear successful.

Use the existing Multica project, one production writer and one heavy workload
at a time at verified native Astra/max/standard. Confirm actual editor project,
map, PIE and dirty state through official Epic MCP before future editor mutations;
preserve owner sessions and unrelated edits. Use existing focused probes and
recording facilities. Follow applicable review responsibilities and later scoped
owner instructions; the MSQ-89 review waiver stays attached to MSQ-89. No reviewer
is requested or dispatched by this planning work.

Preserve historical candidates/evidence, original Mixamo sources, Manny assets,
purchased arms and lobby geometry. Shared asset changes need scoped derivatives
and appropriate registry inventory, not overwritten accepted fingerprints. Keep
task evidence under `Saved/CombatSlice01/<TaskName>/`; use LFS for binary sources.
The controller owns scope/evidence acceptance and local task-scoped closure commits.

No new art, paid services, environment redesign, whole-building destruction,
general locomotion overhaul, Mover migration, AI expansion or automatic successor
start is authorized here. Full stop remains later scope. The character continues
to be a technical mannequin; these tasks do not accept final character art.
