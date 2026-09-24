# CAI-08: Behavior variety and observed-habit adaptation

## Superseded architecture and pending scope: 2026-09-24

This unfinished task is **cancelled as superseded**, not completed. Successors: **MSQ-130**.
Follow [UtilityGOAP01](../UtilityGOAP01.md) and the
[owner replacement decision](../../Approvals/UtilityGOAP01-TaskCreation01.json).
Do not dispatch this old task or use it as a new completion dependency.

The remaining content records the earlier scope and is historical where it
conflicts with the replacement decision. Original reviews/candidate evidence remain unchanged.

Multica issue: **MSQ-110**.
Parent: [MSQ-101 / CombatAI01](../CombatAI01.md), under MSQ-67.
Prepared 2026-09-23; no implementation started.

Authority: [task preparation](../../Approvals/CombatAI01-TaskCreation01.json).
Read the [implementation plan](../CombatAI01Plan.md) and [design](../../Design/CombatAI01.md).

Hard prerequisites: MSQ-109.

## Package work and acceptance
**Purpose:** increase replay interest after the core encounter works.
Size/risk: medium. Depends on C; no new art dependency.

Work:

1. Add two initial behavioral profiles, such as mobile/impulsive and patient/cooperative,
   as data over the same capabilities. Keep sight honesty and physical vulnerability.
2. Separate behavior style, difficulty/pressure profile and physical response profile.
   Do not bundle perfect aim, more health and better information into a generic elite.
3. Introduce recent-route/action history and seeded selection among valid near-equal
   options. Distinct seeds should avoid synchronized movement and identical spread.
4. Add one observed-habit response first: repeated visible use of the same firing edge
   can increase a temporary hold-angle/reposition score. Record evidence count and expiry.
5. Enforce a confidence threshold, short memory and bounded counter frequency. Changing
   tactic or presenting contradictory evidence weakens the learned preference.
6. Record an action-distribution trace for one representative applicable setup; use it
   to find repetition/invalid randomness, not to impose arbitrary diversity quotas.

Acceptance: S12/S18 and one representative shared-functionality instance. The same seed
and observations reproduce pre-gate proposals; different hidden player inputs cannot
change beliefs, routes or aim. Separately captured fairness inputs may only restrict
execution timing. Owner compares style/feel; do not execute a full per-style visual matrix.

Optional future expansions need separate capability briefs: melee, grenades, vaults,
breaching, reinforcement and deliberate prop manipulation. They cannot delay D.

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
