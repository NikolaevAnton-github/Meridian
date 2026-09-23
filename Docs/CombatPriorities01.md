# Combat priorities: AI, shooting and destruction

Recorded 2026-09-23 under the [owner decision](Approvals/CombatPriorities01-OwnerScope01.json).
Administrative update to MSQ-67/MSQ-101 and existing children; no new issue or run.

## Applied change

- MSQ-73 remains backlog and unassigned, now low priority at native stage 16.
  Its technical prerequisite remains MSQ-72. It is a deferred expansion after
  priority combat work, rather than a gate before destruction or slice acceptance.
- MSQ-74 remains backlog and unassigned, now high priority and dependent on MSQ-72
  directly. Stage 8 is retained; stage 7 is vacant, preserving other stage numbers.
- MSQ-78/MSQ-81 retain ordinary regional damage, physical reactions and death.
  Advanced wounds and separation are excluded from initial acceptance and remain
  open in MSQ-73, which later owns its affected integration checks.
- MSQ-67/MSQ-101 descriptions and current project/design navigation reflect the
  priority. MSQ-102 remains the recommended next implementation task. Detailed
  interleaving of destruction with AI packages remains a recommendation.
- MSQ-111 retains MSQ-109/MSQ-74 dependencies; support and actual rubble traversal
  remain scoped to MSQ-95/96 and MSQ-78. No gameplay test permission is changed.

## Administrative verification

The controller used the existing CLI with `--no-start` for descriptions, stage and
priority, and its dedicated metadata operation for MSQ-74's dependency. Existing
API/web services were available; the task runtime stayed stopped.

Focused readback passes description/file equality, the exact stage/priority and
dependency delta, an acyclic dependency graph, absence of MSQ-73 from the priority
tasks' prerequisite ancestry, unchanged status/assignment/run history, preservation
of unrelated issue content, local document links and owner configuration hashes.
Evidence and the bounded adapter using the existing setup-validator conventions
are in `Saved/CombatPriorities01/`, including `verification.json`.

Review route: controller self-checks and acceptance for a small administrative
change, with read-only dependency advice. No gameplay implementation, build,
editor operation, production assignment or technical-review execution occurred.
Historical approvals and task-setup evidence remain unchanged. The deferred task
is not completed or cancelled, and initial slice acceptance cannot close it.
