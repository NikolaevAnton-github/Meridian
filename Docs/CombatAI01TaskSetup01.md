# CombatAI01 task setup

Prepared 2026-09-23 under the [owner task request](Approvals/CombatAI01-TaskCreation01.json).
The detailed design/plan was already independently reviewed; this preparation maps
that scope to the existing Multica project without starting implementation.

## Prepared family

**MSQ-101** is an unstaged coordination child of MSQ-67. Its 16 implementation
children are **MSQ-102 through MSQ-117**; see the complete
[task index and dependency table](Tasks/CombatAI01.md).

- MSQ-102 through MSQ-105 deliver the first persistent hunter.
- MSQ-106 develops individual tactics; MSQ-107 through MSQ-109 deliver the small squad.
- MSQ-110 adds replay variety and restrained observed-habit adaptation.
- MSQ-111 through MSQ-115 are separate prerequisite-driven integrations: destroyed
  cover, time behavior, push/telekinesis, disarming and wound-action ownership.
- MSQ-116 profiles the supported core population; MSQ-117 accepts the selected slice.

All 17 new issues are **backlog, unassigned, with zero runs** at this setup snapshot.
Core children have native stages 1-11. Integration children are unstaged, so unavailable
future mechanics do not become intermediate stage barriers before core profiling.
MSQ-114 and MSQ-115 are independent and consume MSQ-99 and MSQ-100 respectively.

Hard prerequisites and conditional evidence are distinguished in descriptions and
metadata. MSQ-111 can complete cover invalidation without claiming real rubble
traversal; MSQ-95/96 and MSQ-78 retain that applicable support/integration acceptance.
MSQ-116 depends on the core MSQ-110 result, with later integrations owning affected
cost rechecks. MSQ-117 declares its selected scope; missing optional features cannot
be silently marked passed or block an explicitly core-only candidate.

MSQ-70 remains in its historical Multica backlog state although its direct candidate
was delivered and documented. MSQ-102 explicitly consumes that candidate/source
identity and owner feedback; preparation does not rerun MSQ-70, change its status or
invent owner acceptance. Existing task dependencies, stages, assignments and content
remain preserved. The proposed implementation order remains subject to explicit
execution authorization and prerequisite evidence, not automatic bulk dispatch.

## Administrative verification

Evidence: `Saved/CombatAI01/TaskSetup01/`, including before/after issue snapshots,
per-issue creation/update records, run readbacks and `verification.json`.

The focused readback verifies the exact new issue set, project/parent/stage/priority,
backlog/unassigned/zero-run state, file/description equality after newline normalization,
dependency existence and
acyclicity, independent integration branches, preservation of existing issue content
and unchanged owner config/project fingerprints. Local introduced document links and
the task-creation JSON are checked. A read-only mapping advisor checked conditional
dependency traps; no duplicate technical review of the design or implementation ran.

The existing launcher was invoked with `StartServices` for administrative access;
API/web were already running and task runtime remained stopped. Creation used the
existing CLI with unassigned backlog defaults; description updates used `--no-start`
and dependencies used dedicated metadata operations. No editor, build, gameplay,
asset mutation, production assignment or task execution was performed.

The controller owns this administrative acceptance and its local task-scoped commit.
Live Multica may change after this snapshot; this document is evidence of preparation,
not a second live task database.
