# CAI-07: Cooperative maneuvers and interruption

Multica issue: **MSQ-109**.
Parent: [MSQ-101 / CombatAI01](../CombatAI01.md), under MSQ-67.
Prepared 2026-09-23; no implementation started.

Authority: [task preparation](../../Approvals/CombatAI01-TaskCreation01.json).
Read the [implementation plan](../CombatAI01Plan.md) and [design](../../Design/CombatAI01.md).

Hard prerequisites: MSQ-108.

## Package work and acceptance
**Purpose:** deliver the first representative surprising squad.
Size/risk: large coordination scope. Depends on CAI-06.

Work:

1. Assign temporary pressure/maneuver/search roles using ammo, location, capability and
   useful route options. Add leases and hysteresis; do not switch roles every update.
2. Implement four bounded contracts: cover-and-cross, alternate-angle approach, split
   search and staggered reload. Each has preparation, acknowledgement, commitment,
   outcome, failure, participant loss and cleanup. Cover-and-cross requires the accepted
   CAI-04 `SuppressRegion` seam and S23 evidence; it cannot relax direct-fire visibility.
3. Require physically different reachable routes/angles for a flank. Use the enemy's
   evidence region as target context; no shortcut from director true-position data.
4. Transfer responsibilities after visible/communicated ally interruption with a short
   ordinary reaction/aim transition. Avoid instantaneous replacement salvos.
5. Add role-appropriate real callout sequences where assets exist. Canceled contracts
   cancel misleading follow-up lines; independent search reports preserve uncertainty.
6. Give the last active enemy a useful individual fallback, with no requirement for a
   missing partner and no unimplemented reinforcement call.

Acceptance: S13-S17. A candidate demonstrates actual space/timing cooperation and a
successful player interruption of it. A disabled participant releases its role, route,
cover and fire leases. At least two supported encounter situations produce a distinct
cooperative response; this is an applicability check, not a per-variant matrix.

Owner route: let one enemy establish pressure, observe another crossing; interrupt
either participant; break contact and hear/see split searching. Repeat one relevant
setup with a different player decision and judge whether the response changes usefully.

Delivery C should already produce memorable stories on existing mechanics. If it
does not, refine these four contracts before adding more actions or enemy types.

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
