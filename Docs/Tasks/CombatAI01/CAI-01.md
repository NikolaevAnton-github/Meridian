# CAI-01: Persistent intent and running

Multica issue: **MSQ-103**.
Parent: [MSQ-101 / CombatAI01](../CombatAI01.md), under MSQ-67.
Prepared 2026-09-23; no implementation started.

Authority: [task preparation](../../Approvals/CombatAI01-TaskCreation01.json).
Read the [implementation plan](../CombatAI01Plan.md) and [design](../../Design/CombatAI01.md).

Hard prerequisites: MSQ-102.

## Package work and acceptance
**Purpose:** deliver the earliest visible improvement while preparing safe action
execution. Size/risk: medium, movement/physical boundary. Depends on CAI-00.

Work:

1. Add separate encounter alert and last-observation fields; remove the policy coupling
   between a failed action, `StartReturn`, memory erasure and `IgnoreSightUntil`.
2. Keep fresh perception running during tactical cooldowns. Cooldowns suppress only
   the failed action/destination, never all new observations.
3. Add a minimal action lifecycle around the existing move/aim/burst/reload commands:
   start, update, success, cancel and failure reason with action/generation IDs.
4. Select walk/run explicitly by purpose. Verify the imported GASP gait mapping.
   Direction magnitude is normalized by the existing setter; it is not a speed input.
5. Validate running, braking into aim and return from physical recovery using existing
   assets. Retain the current stationary launch gate until moving fire has its own proof.
6. Implement a bounded preliminary search using last-seen area and reachable local
   alternatives. It remains alert after all existing 4/12-second disengagement limits.
   CAI-03 later replaces the limited spatial search with encounter topology.
7. Cancel requests on physics/death/reset; retain evidence through living recovery;
   reject stale callbacks and replan from actual feet when movement authority returns.

Acceptance: S01, S06, S07, S10 in the scenario catalogue. No stale movement/fire after
authority changes; a failed path leaves the enemy alert; actual running is visible
when movement is feasible. Do not claim Recast routes or multi-room search yet.

Fallback: if the gait request exposes a bridge defect, correct that bounded bridge
without replacing the locomotion system. If no alternate local route exists, the
enemy visibly observes a useful reachable sector and retries on new evidence.

Owner route: provoke pursuit over a clear distance, disappear behind retained cover,
wait beyond the old timeout, relocate, hit the enemy and observe re-entry into search.

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
