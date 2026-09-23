# CAI-11: Representative slice and owner acceptance

Multica issue: **MSQ-117**.
Parent: [MSQ-101 / CombatAI01](../CombatAI01.md), under MSQ-67.
Prepared 2026-09-23; no implementation started.

Authority: [task preparation](../../Approvals/CombatAI01-TaskCreation01.json).
Read the [implementation plan](../CombatAI01Plan.md) and [design](../../Design/CombatAI01.md).

Hard prerequisites: MSQ-116, MSQ-71, MSQ-72.

## Package work and acceptance
**Purpose:** close the selected program scope with an identified enjoyable encounter.
Depends on the deliveries chosen for that slice, MSQ-71/72 lifecycle and applicable
MSQ-78 integration. E features unavailable at this point remain explicit future rows.

Work:

1. Consolidate the owner controls, configuration and test route into one handoff.
   Separate runtime debug controls from player-facing encounter presentation.
2. Select one short encounter using retained geometry with clear start/end/reset and
   enough genuine routes for the claimed behaviors. Record placements and limitations.
3. Reuse prior source/build/runtime evidence with candidate applicability. Perform
   only newly coupled checks and required finding closure on the final candidate.
4. Supply actual clips/event traces for supported surprise moments when authorized.
   Have one primary reviewer own integrated technical findings without a duplicate
   controller technical pass. Owner alone decides final combat feel.
5. Capture owner feedback using the rubric below; fix the most consequential observed
   weakness in a bounded correction and recheck only affected criteria.
6. Record current supported action set, population, mechanics, hardware/performance,
   known limitations and deferred expansions. Commit verified changes before handoff.

Completion: no open crash/reset/knowledge-leak/physical-authority/shot-obstruction
blockers; supported encounter criteria have applicable evidence; owner play verdict is
explicitly recorded. A technically complete owner-test candidate may be handed off
with play verdict pending, but it is not called the best AI or final gameplay acceptance.

## Selected-slice acceptance boundary

The initial selectable scope is core delivery A-D with MSQ-71/72 lifecycle and CAI-10
evidence. Declare the selected candidate scope before execution. Absent CAI-09
features remain explicit future criteria, not failed or silently passed requirements.
For an integrated scope that includes powers/destruction, consume the corresponding
completed CAI-09 packages and applicable MSQ-78 evidence. Do not make the initial
core slice wait for all optional mechanics, and never claim full-program acceptance
from a core-only candidate. MSQ-78 retains its existing integrated mechanics scope.

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
