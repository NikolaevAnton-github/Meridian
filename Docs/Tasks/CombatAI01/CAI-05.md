# CAI-05: Safe multi-enemy foundation and shared information

## Superseded architecture and pending scope: 2026-09-24

This unfinished task is **cancelled as superseded**, not completed. Successors: **MSQ-127**.
Follow [UtilityGOAP01](../UtilityGOAP01.md) and the
[owner replacement decision](../../Approvals/UtilityGOAP01-TaskCreation01.json).
Do not dispatch this old task or use it as a new completion dependency.

The remaining content records the earlier scope and is historical where it
conflicts with the replacement decision. Original reviews/candidate evidence remain unchanged.

Multica issue: **MSQ-107**.
Parent: [MSQ-101 / CombatAI01](../CombatAI01.md), under MSQ-67.
Prepared 2026-09-23; no implementation started.

Authority: [task preparation](../../Approvals/CombatAI01-TaskCreation01.json).
Read the [implementation plan](../CombatAI01Plan.md) and [design](../../Design/CombatAI01.md).

Hard prerequisites: MSQ-106, MSQ-72.

## Package work and acceptance
**Purpose:** introduce two/three combatants with correct space, knowledge and lifecycle.
Size/risk: high concurrency and collision risk. Depends on B and MSQ-72 lifecycle.

Work:

1. Generalize explicit one/two/three-enemy encounter configuration with stable IDs and
   per-agent seeds. Retain passive fixtures as a separate test mode.
2. Add encounter/squad coordinator records, membership and idempotent register/remove.
   Death, reset and mode changes must release all memberships/reservations.
3. Add target reports carrying original uncertainty, observation time and delayed
   delivery. Share friendly status without sharing a hidden target transform.
4. Introduce tactical position, narrow-passage and firing-lane reservations with leases,
   expiry and generation checks. Useful local yielding replaces collision disabling.
5. Add friendly physical/proxy occupancy checks independent of projectile `BuildQuery`.
   Recheck friendly risk at launch; an unsafe lane defers fire or changes position.
6. Introduce the minimum pressure permission seam now: conservative new-shooter and
   maneuver limits. Group competence must not precede all pressure safeguards.
7. Cover membership change during recovery, death, late report delivery and F6. Record
   current friendly-fire policy explicitly and preserve the shared damage path.

Acceptance: S10, S13, S14 and initial S15. Two enemies do not share a reserved pose,
lock one another indefinitely or shoot solely because static geometry is clear.
Reports cannot become fresher or more precise through relay. A removed actor cannot
retain an attack permit or receive a stale callback into a new encounter.

Owner route: encounter two, then three enemies in the existing bounded placement;
move across their lines, knock one down and reset. This stage establishes safe group
operation, not the final cooperation/readability verdict.

## Execution and verification contract

Prepared only: backlog, unassigned, no run. Dispatch requires a later execution
instruction under the standing project workflow. Read `Docs/ProjectState.md` first,
then this task, the linked plan/design and only relevant prerequisite decisions.

- One production writer and one Unreal writer; max reasoning at standard speed,
  verified in configured and native execution.
- Executor implements and self-checks; one primary independent reviewer owns
  substantive technical review. Controller owns scoped acceptance and local commit.
- State the applicable verification mode at dispatch. The continuing MSQ-70
  owner-test reservation is not silently revoked. Under owner-only gameplay testing,
  provide build/source evidence and the owner route; leave runtime rows pending.
- Run only affected scenarios and related transitions; reuse applicable evidence.
  Owner retains motion, readability, surprise and combat-feel acceptance.
- Preserve GASP/Mover physical authority, finite bullets and current time policy:
  world/bullets/rifle cadence 0.25, hero movement 0.65 during slowdown.
- Preserve owner edits, current map, asset sources and historical evidence. No new
  paid services, duplicate project or unapproved art/architecture production.

## Required handoff

Provide scope, candidate identity, changed files/assets, tuning, build result,
applicable focused evidence, review findings/closure, owner controls/route and known
limits. Keep generated evidence in `Saved/CombatAI01/<package>/<candidate>/`.
Commit verified task-scoped changes locally with the real MSQ task ID before handoff.
