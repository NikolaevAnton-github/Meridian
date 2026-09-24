# UtilityGOAP01 planning and task preparation

Date: 2026-09-24. Parent: **MSQ-122** under MSQ-67.
Authority: [owner architecture and replacement request](Approvals/UtilityGOAP01-TaskCreation01.json).
Deliverables: [design](Design/UtilityGOAP01.md), [source inventory](Design/UtilityGOAP01SourceInventory.md),
[detailed plan](Tasks/UtilityGOAP01Plan.md), [task index](Tasks/UtilityGOAP01.md).

## Prepared scope

Created one coordination parent and fifteen bounded children, **MSQ-123..137**.
Ten core tasks have native stages 1..10; five mechanic integrations are unstaged.
All new issues are backlog and unassigned. Description updates use `--no-start`;
the administrative services were already available. No production runtime was started.

The first implementation task removes obsolete active AI and extracts individually
justified primitives. It explicitly leaves a passive/manual intermediate. The next
task restores a minimal Utility+GOAP combat enemy. Historical code stays in Git;
no legacy brain/navigation fallback is kept in the intended production architecture.

The thirteen unassigned zero-run MSQ-105..117 issues are cancelled as superseded,
with exact successor links and metadata. MSQ-101 retains its historical identity,
delivered children and a supersession notice. Their previous descriptions and live
state are saved under `Saved/UtilityGOAP01/TaskSetup01/issues-before.json`.
Earlier task/design documents receive current supersession notices; original
approval records, technical reviews and candidate manifests are unchanged.

External mechanic tasks keep their status and scope. MSQ-72 gains MSQ-126 as a
dependency and a one-enemy-first dispatch note; its original cover/lifecycle
acceptance and cap of three remain. MSQ-127 later enables two/three enemies.
Destruction integration MSQ-131 has high priority after MSQ-125, MSQ-71, MSQ-126,
one-enemy MSQ-72 and a real MSQ-74 specimen, before extensive tuning/group work.
Other external fields remain unchanged. Core profiling/handoff remains independent
of future mechanics. The new plan preserves current GASPALS/CMC and the later
world/bullet/rifle 0.25 versus hero movement 0.65 slowdown decision.

## Independent technical planning review

Primary reviewer: `/root/utility_goap_plan_review`, independent of authorship.
The read-only architecture advisor `/root/ai_classification` supplied the source
inventory and is not the acceptance reviewer. Native session turn metadata verifies
`gpt-6-astra` with `max` reasoning for both delegated agents. Standard speed was
requested with no fast override; native records do not expose an explicit response
tier, so an independently measured service-tier assertion is not made.

Final verdict: **PASS**, with zero open technical findings. The initial review
raised one P2 finding, UGP-R1: the early MSQ-72 encounter lane required cover and
could enable several enemies before the replacement capabilities existed.

Correction: MSQ-71 -> MSQ-126 initial cover -> one-enemy MSQ-72 -> MSQ-74/MSQ-131,
with MSQ-127 enabling two/three enemies afterward. MSQ-72 gains the explicit cover
dependency without losing its original acceptance criteria. MSQ-131 depends on
actual individual cover and destruction; MSQ-74 does not depend back on MSQ-131.
The same reviewer performed only the affected boundary recheck and closed UGP-R1.
Passing architecture/source-contract criteria were carried forward.

The full initial finding, closure and document identity evidence are preserved in
`Saved/UtilityGOAP01/PlanningReview01/report.md` and `verdict.json`. The controller
accepts the owner scope, applicable planning evidence and finding closure; no
second full technical review or production/runtime acceptance is implied.

## Administrative verification

The adapted existing setup validator passes. Live readback establishes:

- Exactly sixteen new issues: one parent and fifteen children, all backlog,
  unassigned and with zero runs; the task runtime remains stopped.
- Exact description-file synchronization, parentage, core stages, independently
  unstaged integrations and an acyclic dependency graph. No live dependent is left
  behind a newly cancelled predecessor.
- Thirteen old tasks cancelled with exact successor metadata and original
  description bodies preserved. Multica automatically moved their board positions
  when status changed; that bounded server effect is recorded in verification.
- MSQ-101 changes only its historical index notice/metadata. MSQ-72 changes only its
  dependency/dispatch notice. Other pre-existing issues, including delivered tasks
  and external mechanics, retain their checked status, assignment, description,
  stage, priority, parentage and metadata.
- All earlier local task/design bodies retain their content behind a clearly
  identified supersession notice. Original approval/review/candidate evidence is
  unchanged. The two existing owner edits, `Config/DefaultEngine.ini` and
  `MeridianSquad.uproject`, retain their exact pre-task SHA-256 values.
- The documentation link scan checks 610 local references without newly broken
  links; pre-existing unrelated broken references are listed separately. No source
  or asset change is present, and scoped whitespace checks pass.

Evidence: `Saved/UtilityGOAP01/TaskSetup01/verification.json`, issue snapshots,
description updates, run readbacks, service state and `native-execution-settings.json`.
The helper adapts the existing CombatAI01 administrative setup checks; it is not a
new dispatcher, task database or gameplay benchmark.

## Delivery boundary

This is a planning and backlog change. No production source/assets, native build,
editor state or gameplay were changed or tested. The current source remains Build07
at `7ba267f` until implementation starts. Future runtime evidence and owner judgement
are separate gates; this report does not claim the new AI is implemented or better
in play. The controller makes a verified task-scoped local commit before handoff.
