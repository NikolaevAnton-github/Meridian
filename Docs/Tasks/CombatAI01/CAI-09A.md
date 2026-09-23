# CAI-09A: Destroyed-cover and navigation invalidation

Multica issue: **MSQ-111**.
Parent: [MSQ-101 / CombatAI01](../CombatAI01.md), under MSQ-67.
Prepared 2026-09-23; no implementation started.

Authority: [task preparation](../../Approvals/CombatAI01-TaskCreation01.json).
Read the [implementation plan](../CombatAI01Plan.md) and [design](../../Design/CombatAI01.md).

Hard prerequisites: MSQ-109, MSQ-74.

## Package work and acceptance
Dependencies: C, MSQ-74, applicable MSQ-95/96 for support, MSQ-78 for real traversal.
Invalidate damaged/destroyed cover, stance samples, reservations and affected route
segments using geometry revisions. Prevent new use immediately; schedule rebuilds.
Use current collision/support checks while navigation catches up. Search must choose
a reachable alternative when rubble blocks a route. Real traversal of moving rubble
is accepted only in the existing integrated scope, with actual representative debris.
Acceptance: S19, plus S06/S08/S10 for the directly changed transitions.

## Integration boundary

MSQ-74 and CAI-07 are hard prerequisites for destroyed-cover decisions. This task
accepts invalidation, safe routing around unsupported debris and new tactical choices.
Actual crossing of representative static/moving rubble stays in MSQ-78 and consumes
MSQ-95/96; it is not required to close this cover-invalidation scope. Record those
conditional evidence dependencies explicitly. Never create a reverse completion edge
from MSQ-78 to this task that would block its own prerequisites.

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
