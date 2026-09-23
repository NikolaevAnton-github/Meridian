# CAI-00: Baseline, contracts and observability

Multica issue: **MSQ-102**.
Parent: [MSQ-101 / CombatAI01](../CombatAI01.md), under MSQ-67.
Prepared 2026-09-23; no implementation started.

Authority: [task preparation](../../Approvals/CombatAI01-TaskCreation01.json).
Read the [implementation plan](../CombatAI01Plan.md) and [design](../../Design/CombatAI01.md).

Hard prerequisites: MSQ-70.

MSQ-70 was delivered directly outside Multica; its historical backlog status
does not authorize rerunning it. Inspect the documented current candidate and
owner feedback before accepting the prerequisite evidence.

## Package work and acceptance
**Purpose:** make every later decision diagnosable and establish what the current
one-enemy implementation actually does. Size/risk: small scope, low code risk.
Prerequisite: current MSQ-70 source/build identity and authorized execution route.

Work:

1. Record repository state, owner edits, current DLL/candidate, engine version, map,
   active test mode and permitted test scope. Check live editor state before mutations.
2. Inventory the exact movement, rifle, damage, projectile and reset interfaces.
   Document the single input writer and current physical authority precedence.
3. Extend existing status output with encounter generation, alert/evidence, current
   intent, physical authority, path outcome and a bounded decision/event ring.
4. Record current build-only limitations: no demonstrated run gait, hearing, persistent
   search, group lanes or multi-enemy performance. Mark facts separately from hypotheses.
5. Define the input/event snapshot used by later pure decision tests; keep privileged
   fairness inputs in a separate trace channel. Introduce stable
   per-agent seeds derived from encounter seed and stable spawn index, not identical
   `Spread.Initialize(70)` for every enemy.
6. Inventory reusable player-facing audio cues. Debug text is sufficient for diagnosis
   but cannot close the final audibility/readability criterion.

Outputs: short baseline report, proposed data contracts, bounded status trace, declared
test configuration and recorded seeds. No scene redesign or AI framework migration.

Acceptance: same seed/event stream reproduces decision-level input capture; F6 clears
the ring/generation without changing unrelated player-ammo behavior; no credentials or
unbounded per-frame logs; source/build checks identify the actual candidate. If runtime
is authorized, collect one representative baseline cost sample, not a benchmark suite.

Owner route: run current one-enemy mode, break sight, receive/inflict a hit and restart.
Use existing feedback to identify the observed failure path; do not ask the owner to
prove every source assertion manually.

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
