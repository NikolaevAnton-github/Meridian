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

On 2026-09-21 the owner selected [physical recoverability / MSQ-97](PhysicsControlRecoverability01.md)
as the next task, between MSQ-91 and MSQ-92; see the [later decision](../Approvals/PhysicsControlRecoverability01-NextTask01.json).
It adds displaced-leg replanting, contact/momentum-based recovery limits and
successive steps under sustained hits. The active baseline is MSQ-91 Candidate07
plus CombatTestToggles02 commit `37af4b8`; earlier evidence stays immutable.
The owner subsequently [authorized MSQ-97 execution without an independent reviewer](../Approvals/PhysicsControlRecoverability01-OwnerStart01.json).
Its executor supplies focused self-checks; controller scope/evidence acceptance
and owner motion/play judgement remain separate. MSQ-92 through MSQ-96 remain
undispatched; neither task-specific waiver extends to them.
MSQ-97 Candidate07 now supplies the physical recovery foundation with a passing
build and 183 focused self-checks; see the [controller handoff](../PhysicsControlRecoverability01Handoff.md).

## GASP foundation inserted before remaining refinements

The later [2026-09-21 owner request](../Approvals/GASPEnemyFoundation01-TaskCreation01.json)
places [GASPEnemyFoundation01 / MSQ-98](GASPEnemyFoundation01.md) first in the pending
work. It is an unstaged child of MSQ-67, consuming delivered MSQ-92 plus applicable
follow-ups, and becomes MSQ-93's immediate prerequisite. Current order is
**MSQ-91 -> MSQ-97 -> MSQ-92 -> MSQ-98 -> MSQ-93 -> MSQ-94 -> MSQ-95 -> MSQ-96**.
Keep this family's existing native stages 1-7; MSQ-98 is an external prerequisite,
not another child stage. MSQ-70 also consumes MSQ-98, while retaining MSQ-69.
Migration is planning-only and does not dispatch any remaining task.

MSQ-98 adapts existing recovery to the configured GASP character and proves the
flat-floor movement/physics handover. The remaining tasks retain their distinct
counterbalance, obstacle and terrain criteria on that adopted foundation. Earlier
Mover/locomotion exclusions do not forbid the newly scoped enemy migration; player
movement remains unchanged. The original baseline/evidence above stays historical.

## Ordered implementation tasks

The later [MSQ-92 start and tempo request](../Approvals/PhysicsControlAdaptiveSteps01-OwnerStart01.json)
authorizes stage 3 on MSQ-97 Candidate07, with approximately 25 percent faster
recovery response/stepping as initial tuning. One primary independent technical
reviewer applies to MSQ-92; earlier scoped waivers remain historical. MSQ-93
through MSQ-96 remain undispatched. This supersedes the earlier MSQ-92 planning-only
status above without changing predecessor evidence or owner motion acceptance.
MSQ-92 Candidate06 is now delivered with a passing build, 208 focused assertions
and six passing independent review rows; see the
[controller handoff](../PhysicsControlAdaptiveSteps01Handoff.md). Owner motion/play
judgement remains separate, and no later stage is started.

| Stage | Multica | Task | Required result |
| --- | --- | --- | --- |
| 1 | MSQ-91 | [PhysicsControlLegPose01](PhysicsControlLegPose01.md) | Anatomical knee/foot alignment and a credible settled stance after steps. |
| 2 | MSQ-97 | [PhysicsControlRecoverability01](PhysicsControlRecoverability01.md) | Displaced-leg replanting and successive recovery steps within physical support and effort limits; fall when recovery is infeasible. |
| 3 | MSQ-92 | [PhysicsControlAdaptiveSteps01](PhysicsControlAdaptiveSteps01.md) | Refine step length, lift and timing on the recoverability foundation. |
| External | MSQ-98 | [GASPEnemyFoundation01](GASPEnemyFoundation01.md) | Migrate the configured GASP enemy foundation and retain our balance/combat behavior before stage 4. |
| 4 | MSQ-93 | [PhysicsControlCounterbalance01](PhysicsControlCounterbalance01.md) | Torso and arms help balance, then settle without perpetual sway. |
| 5 | MSQ-94 | [PhysicsControlObstacleRecovery01](PhysicsControlObstacleRecovery01.md) | Obstacle-aware living get-up, finite retries and safe blocked behavior. |
| 6 | MSQ-95 | [PhysicsControlUnevenGround01](PhysicsControlUnevenGround01.md) | Ground contact and recovery steps on slopes, unequal heights and fixed rough support. |
| 7 | MSQ-96 | [PhysicsControlDebrisSupport01](PhysicsControlDebrisSupport01.md) | Contact with translating, rotating or disappearing debris, including loss of support. |

The first child depends on MSQ-89; each subsequent child consumes the verified
preceding handoff, including the inserted MSQ-98 prerequisite before MSQ-93.
Use the latest applicable candidate, preserving older manifests.
Stage 5 addresses the retained wall/get-up retry limitation; terrain work follows
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

Stage 7 may close its support capability against removable dynamic fixtures before
MSQ-74 exists. That closure does not close real rubble traversal: MSQ-78 retains the
explicit open integration gate until the movement and destruction prerequisites
are available. Do not make MSQ-70 depend on MSQ-74/MSQ-78 or reorder the original
CombatSlice stages; the later owner request adds only MSQ-98 as a new prerequisite
to MSQ-70. Creating these links does not dispatch any of those tasks.

## Shared acceptance and preservation

Each child defines its affected behaviors, records numeric operating limits and
provides an identified candidate, concise changes, measurements and ordinary-speed
continuous footage. Owner motion/play acceptance remains separate. Verify only
changed behavior and related transitions; reuse applicable passing evidence. For
the current three-mannequin experiment, inspect the set rendering and check shared behavior
on one representative mannequin unless a distinct profile defect needs a check.
Do not run a full animation, variant or combat matrix by default.

The former one/two-step episode cap is superseded for reactive hit recovery by
MSQ-97. Successive steps are permitted while support, reach, actuator limits and
progress remain valid. Navigation, pursuit and general walking remain excluded.
Retain hit response, true physical collapse when
recovery fails, living get-up, terminal death, damage state, self-collision and
calibrated sole contact. Preserve F6 reset without ammunition refill, F10, optional
Ctrl+F7/Ctrl+F8 controls and the 0.25 world / 0.65 player slowdown. MSQ-97 replaces
Ctrl+F9's unlimited fall veto with bounded recovery assistance. Recheck slowdown
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
