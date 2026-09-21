# GASP enemy migration and secondary reaction task setup

Prepared 2026-09-21 under the
[owner's exact task-creation request](Approvals/GASPEnemyFoundation01-TaskCreation01.json).

| Issue | Task | Priority | Prerequisites |
| --- | --- | --- | --- |
| MSQ-98 | [GASPEnemyFoundation01](Tasks/GASPEnemyFoundation01.md) | High; first pending | MSQ-92 plus current corrections |
| MSQ-99 | [EnemyDisarm01](Tasks/EnemyDisarm01.md) | Low; secondary | MSQ-98, MSQ-70 |
| MSQ-100 | [EnemyWoundReaction01](Tasks/EnemyWoundReaction01.md) | Low; secondary | MSQ-98, MSQ-70 |

All three are unstaged children of MSQ-67 in the existing MeridianSquad project.
They are backlog, unassigned, with zero execution runs. MSQ-98 is first in the
backlog column; the two secondary issues are at its bottom. No implementation or
technical reviewer was dispatched. Only administrative database/API/web services
were started; the task runtime was not started by this preparation.

MSQ-93 now depends on MSQ-98. MSQ-70 retains MSQ-69 and additionally depends on
MSQ-98. Existing MSQ-90 stage numbers, MSQ-93 -> 94 -> 95 -> 96, and the original
CombatSlice stages remain intact. The new low-priority tasks do not gate MSQ-71
or other base-combat stages and do not depend on each other. No MSQ-74/MSQ-78 or
parent-completion dependency was introduced before enemy movement.

Migration covers a configured GASP physical character, retained balance/combat
integration, a focused pilot and rollout to the three active fixtures. MSQ-70 keeps
autonomous AI combat and weapon setup; the remaining physical tasks retain their
distinct criteria. Hand-to-wound means the enemy reaches for its own injured region.

## Verification

Readback evidence is under
`Saved/CombatSlice01/GASPEnemyFoundation01/Planning/verification.json`, alongside
before/after issue snapshots and per-issue run records. Verification checks:

- Exactly three new issues, expected priorities/parents/dependencies and zero runs.
- Multica descriptions match the eight affected task/plan files; newly added local
  links resolve. Pre-existing unrelated broken links are recorded separately.
- Relevant dependency paths have no cycles; existing stages/statuses/assignments and
  unrelated issue content remain unchanged.
- `Config/DefaultEngine.ini` and `MeridianSquad.uproject` retain their pre-operation
  owner-edit fingerprints. Gameplay code, assets and editor sessions were not modified.

The preparation uses the existing Multica CLI with `--no-start` for issue updates.
Metadata changes use its dedicated metadata operation. No additional dispatcher or
task database was introduced. Future execution follows the standing max/standard,
one-primary-reviewer, focused-verification and controller-commit rules. Prior review
waivers remain task-scoped and owner motion/play judgement remains separate.
