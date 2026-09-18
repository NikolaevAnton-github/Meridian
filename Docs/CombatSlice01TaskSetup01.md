# CombatSlice01 task preparation verification

Recorded 2026-09-18. The owner requested preparation of sequential tasks; the
[exact record](Approvals/CombatSlice01-TaskCreation01.json) and
[ordered plan](Tasks/CombatSlice01Plan.md) define the scope.

The existing MeridianSquad Multica project now contains parent **MSQ-67** and
14 children **MSQ-68 through MSQ-81**, in native stages 1-14. Each description
contains the bounded scope, acceptance and predecessor. Shared preservation,
execution, evidence and closure rules are in the parent plan. An independent
read-only planning review informed the asset, action-compatibility and story
knowledge requirements; this is not review or acceptance of future gameplay.

CLI readback verified all 15 issues have the existing project ID, backlog status
and status category, no assignee, correct parent/stage, and an empty execution
history. Descriptions match the tracked task files after line-ending normalization.
The first child records MSQ-66 as its baseline dependency; each subsequent child
records its predecessor in the existing `metadata.depends_on` convention.

The installed Multica stages/metadata do not enforce successor scheduling. The
controller must check prerequisite evidence and explicitly dispatch each intended
run within authorized scope. The parent is coordination only. Administrative
description updates used `--no-start`; creation used backlog with no assignment.
The existing `StartServices` launcher was used for administrative access only.
No production run was created and no runtime start or editor operation was issued.
No worker profile was changed; profile/native/actual max settings must be verified
when production is later dispatched.

Evidence: `Saved/CombatSlice01/TaskSetup01/verification.json`, per-issue readbacks
and empty run histories, the child-stage response and the pre-change issue list.
Generated evidence and the one-off administrative CLI adapter remain outside Git.
The retained owner edit in `Config/DefaultEngine.ini` is excluded from this change.

The first prepared task is **MSQ-68 / CombatFoundation01**. Preparing this family
does not complete the combat parent, approve a new asset/story design or resume
paused protagonist and environment production.
