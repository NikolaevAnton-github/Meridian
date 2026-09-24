# CAI-10: Measured performance and bounded failure handling

## Superseded architecture and pending scope: 2026-09-24

This unfinished task is **cancelled as superseded**, not completed. Successors: **MSQ-136**.
Follow [UtilityGOAP01](../UtilityGOAP01.md) and the
[owner replacement decision](../../Approvals/UtilityGOAP01-TaskCreation01.json).
Do not dispatch this old task or use it as a new completion dependency.

The remaining content records the earlier scope and is historical where it
conflicts with the replacement decision. Original reviews/candidate evidence remain unchanged.

Multica issue: **MSQ-116**.
Parent: [MSQ-101 / CombatAI01](../CombatAI01.md), under MSQ-67.
Prepared 2026-09-23; no implementation started.

Authority: [task preparation](../../Approvals/CombatAI01-TaskCreation01.json).
Read the [implementation plan](../CombatAI01Plan.md) and [design](../../Design/CombatAI01.md).

Hard prerequisites: MSQ-110.

## Package work and acceptance
**Purpose:** establish a sustainable target population and eliminate growing work.
Size/risk: driven by measurements. Run after C/D and revisit only affected CAI-09 costs.

Work:

1. Profile one and three active enemies at the same declared map/settings/frame target,
   including decision, perception, nav, projectile, animation and Physics Control cost.
2. State the measured baseline and proposed 1.5 ms p95 AI game-thread target separately.
   Include worker/nav-build cost and total frame distribution; do not hide shifted work.
3. Add global scheduling/quota improvements only for observed bottlenecks: staggered
   sensing, bounded candidate queries, cached geometry, registered spatial listeners.
4. Inspect repeated whole-world query construction and forced bone updates before
   assuming the utility selector is the dominant cost. Preserve hit/pose correctness.
5. Validate bounded persistent-search queues, evidence rings and reservation tables.
   Run one targeted long-search sample and a small repeated-reset sample.
6. Exercise one stale async result, one unreachable region and participant removal
   during an active contract. Compare only affected behavior against prior evidence.
7. Explore six enemies only if three has measured headroom. Otherwise retain the
   three-enemy supported target and document the actual bottleneck.

Acceptance: S07/S10/S22, declared target hardware/settings, bounded work/storage and
no skipped shot/physical safety. Scaling acceptance is explicit per supported count.
Do not run a full enemy/profile/animation cross-product or lower visual settings
without documenting the change in comparison conditions.

## Conditional follow-up boundary

CAI-08 is the core completion prerequisite. CAI-09 integrations and future abilities
do not block the initial one/three-enemy cost acceptance. Each later integration
records its own affected performance/lifecycle checks and reuses this baseline;
only a measured new coupled cost justifies an additional bounded profiling pass.

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
