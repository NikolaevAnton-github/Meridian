# PlayerCharacter01: AI3D task synchronization

Verified 2026-09-17. The owner asked Codex to start Multica and check the tasks,
and clarified that Codex may launch the existing applications needed for
authorized work without requesting permission each time. This continues the
requested integration of Tripo, Meshy and Hunyuan3D into the protagonist pipeline.

## Services

The existing Multica instance was offline. Its existing PostgreSQL, API and web
components are now running, bound to 127.0.0.1 on ports 15432, 8080 and 3000.
The task runtime remains stopped: this is administrative task maintenance.

Scripts/multica.ps1 now supports `StartServices`, which starts database/API/web
without starting the worker. Existing `Start` behavior is preserved. The launch
and API/web readiness checks succeeded. On a Windows shell with script execution
disabled, invoke the inspected project script in a dedicated process:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File Scripts/multica.ps1 -Action StartServices
```

This does not change the persistent Windows execution policy. Processes are
started with hidden windows using the existing launcher and configuration.

## Live task findings and update

Before the audit there were 43 project issues, including MSQ-50 and its ten
children MSQ-51 through MSQ-60. No new child issues are necessary to cover the
pipeline. The gap was the missing operational AI3D detail in the existing cards.

MSQ-50 is in_progress; MSQ-51 is done; MSQ-53 is in_review; MSQ-52 and MSQ-54
through MSQ-60 are backlog. These statuses and all assignments were preserved.
The parent status is a board state, not evidence that a worker is running.

| Updated card | Added operational detail |
| --- | --- |
| MSQ-50 | Complete source-to-gameplay-to-finish sequence, current subscription scope and owner-only concept gate. |
| MSQ-52 | Actual skeleton/fingers/twist/IK, units/axes/poses, dimensions and rifle contact contract. |
| MSQ-53 | Exact owner selection, authoritative reference details and preservation of all concept variants; no independent concept reviewer. |
| MSQ-54 | Eight ordered steps: coherent references, existing-export inspection, proportional master, bounded source trial, provider-specific operations, fitted components, joint topology/weights, identified original prototype handoff. |
| MSQ-55 | Early original-body import, first-person seams/camera and complete world/shadow checks with provisional materials. |
| MSQ-56 | Movement, planted turns, crouch/jump and armor-clearance tests on the original prototype; geometry failures return to MSQ-54. |
| MSQ-57 | Fingers/grip/magazine/reload and synchronized rifle/gameplay probes before finish. |
| MSQ-58 | Stable UVs, controlled bakes, native Painter finish, weights/physics/LODs after successful MSQ-54/55/56/57 probes. |
| MSQ-59 | Final AI/input/export/native-source provenance and integrated gameplay/performance evidence. |
| MSQ-60 | Independent final geometry/deformation/gameplay/provenance review and correction rechecks. |

The delivered MSQ-51 was not edited or reopened. Existing original-character,
weapon, lobby-preservation and 250 GB requirements remain. No final character
design was selected by this operation.

The implementation uses the existing canonical editable source root
`Assets/Source/PlayerCharacter01/`, with selected AI input/export sources under
its `AI3D/<provider>/<candidate>/` subtree. The earlier pipeline's alternative
proposed source tree was corrected before production created any assets there.

Provider alternatives and armor groups remain checklist items inside MSQ-54.
Its handoff requires source-pose tests; integrated PIE presentation/gameplay
belongs to successors MSQ-55/56/57. This avoids a circular dependency while
preserving all four prerequisites of MSQ-58.

## Verification and preserved evidence

All updates used `issue update --description-file ... --no-start`.
Before/after issue readbacks verified:

- The same 43 issues remain; zero new issues were created.
- Ten descriptions changed: MSQ-50 and MSQ-52 through MSQ-60.
- All 33 non-target issue records, including MSQ-51, remain identical.
- Target titles, statuses, assignments, parents, dependencies, stages,
  metadata and other non-description fields are preserved, apart from ordinary
  revision/activity timestamps.
- Run histories for all eleven player issues remain identical; zero new runs.

The Windows CLI normalizes LF to CRLF and trims the final LF when applying a
description file. Initial MSQ-50 readback detected this formatting difference;
content matched after newline normalization. The continuation verified that
already-applied card without writing it again. The verification records both
uploaded and stored description hashes, rather than claiming byte identity.

A bounded independent checklist review found no remaining required coverage
defect after reviewing MSQ-50/53/54/58. This was task/workflow review, not concept
art evaluation or production acceptance. No model assets, DCC/editor state,
profiles, native arguments, purchases or generation credits changed.

Exact before/after records, description files, CLI responses, run histories,
one-time update script and verification are under:
`Saved/PlayerCharacter01/AI3DTaskAudit01/`.

Use [the task index](PlayerCharacter01Tasks.md) and
[the production pipeline](../PlayerCharacter01AI3DPipeline.md) for current scope.
Multica remains the source of truth for subsequent task state and execution.
