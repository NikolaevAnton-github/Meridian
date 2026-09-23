# CAI-04: Individual tactics, cover and firing rhythm

Multica issue: **MSQ-106**.
Parent: [MSQ-101 / CombatAI01](../CombatAI01.md), under MSQ-67.
Prepared 2026-09-23; no implementation started.

Authority: [task preparation](../../Approvals/CombatAI01-TaskCreation01.json).
Read the [implementation plan](../CombatAI01Plan.md) and [design](../../Design/CombatAI01.md).

Hard prerequisites: MSQ-105, MSQ-71.

## Package work and acceptance
**Purpose:** turn movement competence into interesting combat choices.
Size/risk: large behavior/feel scope. Depends on A; MSQ-71 for survival balance acceptance.

Work:

1. Add the action eligibility/utility selector and inspectable score terms, commitment,
   switching margin, recent-action penalty and deterministic bounded tie variation.
2. Define the initial action set from the design document. Use stable action outcomes
   rather than adding another switch branch for every combination of conditions.
3. Add a small set of removable tactical anchors on existing geometry. Validate stance,
   capsule clearance, cover direction, muzzle corridor, exposure and approach/exit.
4. Implement repositioning to a genuinely different useful angle and withdrawing to
   another active position when the current one is compromised.
5. Improve aim reacquisition/turn limits, burst decisions and magazine-aware action
   choice. Split `DirectFire` and `SuppressRegion` aim-source/authorization contracts:
   direct shots retain fresh sight; suppression uses an evidence-backed bounded region,
   original age, finite round budget and expiry without a live target-position read.
   Both retain common weapon/authority/geometry safety and the finite-flight launch path.
6. Add a bounded suppression action with independent eligibility/commitment; loss of
   sight does not silently convert an unfinished direct burst. Add near-miss evidence
   only where needed, sampling actual traveled segments up to earliest impact with
   deduplication and no repeated frozen-bullet stimuli.
7. Model reload as a vulnerable real action; use cover when available. Keep gameplay
   ammo transfer separate from animation completion and retain interruption policy.
8. Make failure recovery specific: blocked muzzle -> reposition candidate; stale target
   -> search; no cover -> use a valid exposed action with a documented risk score.

Acceptance: S04/S05, S08/S09, S12 and S23. At least two materially different valid responses
are possible when the scenario actually offers two useful positions. No utility
oscillation, indefinite aim wait, precision fire during unsupported movement or
continuous suppression that follows the unseen player.

Owner route: fight one enemy from two different positions, repeat a visible peek, break
contact and attack while it changes position/reloads. Judge whether those choices
create readable opportunities rather than forcing prolonged passive play.

Delivery B closes on competent decisions and owner feedback; initial tuning is not
locked for the whole game. Do not multiply health/damage to disguise weak choices.

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
