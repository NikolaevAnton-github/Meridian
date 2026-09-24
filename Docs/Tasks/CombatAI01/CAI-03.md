# CAI-03: Encounter navigation and persistent spatial search

## Superseded architecture and pending scope: 2026-09-24

This unfinished task is **cancelled as superseded**, not completed. Successors: **MSQ-125**.
Follow [UtilityGOAP01](../UtilityGOAP01.md) and the
[owner replacement decision](../../Approvals/UtilityGOAP01-TaskCreation01.json).
Do not dispatch this old task or use it as a new completion dependency.

The remaining content records the earlier scope and is historical where it
conflicts with the replacement decision. Original reviews/candidate evidence remain unchanged.

Multica issue: **MSQ-105**.
Parent: [MSQ-101 / CombatAI01](../CombatAI01.md), under MSQ-67.
Prepared 2026-09-23; no implementation started.

Authority: [task preparation](../../Approvals/CombatAI01-TaskCreation01.json).
Read the [implementation plan](../CombatAI01Plan.md) and [design](../../Design/CombatAI01.md).

Hard prerequisites: MSQ-104.

## Package work and acceptance
**Purpose:** give search real spatial alternatives and remove the home-grid limitation.
Size/risk: large integration risk; keep its scope to routes/search. Depends on CAI-02.

Work:

1. Add a navigation adapter with Pending/Complete/Partial/Invalid/Unreachable outcomes,
   request generation, geometry revision and explicit cancel/replacement behavior.
2. Use Recast queries with actual agent capsule properties, bounded ground projection,
   supported slope/step envelope and removable nav setup. Keep GASP as movement owner.
3. Prove a direct path and a route around existing retained geometry. Smooth/look ahead
   within verified traversability; never shortcut through a wall or unsupported edge.
4. Retain local collision/support validation while following a cached route. A partial
   path is useful to a boundary but is not successful arrival at the requested target.
5. Derive a small connected set of search sectors and plausible exits from current
   navigation and occlusion. Add removable annotations only where geometry is ambiguous.
6. Track checked visible areas, rejected/unreachable destinations and observation age.
   Prioritize information gain and avoid repeatedly clearing the same empty location.
7. Allow a new clue to redirect the search with a controlled replan. Replace hard pursuit
   expiry with action failure/backoff and a useful new search/observation decision.
8. Establish global nav work quotas, outstanding-request limits and stale-result checks.
   Verify bounded behavior with an unreachable goal and a moved/invalidated obstacle.

Acceptance: S01-S03, S07, S08 and affected S06/S10. Persistent search lasts at least
60 world seconds in the scoped scenario without returning unaware or growing queues.
The test is a bounded sample of an invariant, not proof of literally infinite execution.

Fallback: preserve the previous navigator behind an explicit debug switch until the
new adapter passes. Do not silently change to unlimited per-enemy searches. If Recast
cannot support a required route, diagnose projection/collision/support before trying
NavMover/standard path following; never run both followers simultaneously.

Delivery A closure: running, hearing, incoming-fire awareness and persistent search
have a named candidate and honest evidence status. The owner can evaluate one hunter.

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
