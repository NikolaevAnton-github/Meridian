# MSQ-171: Library-only lobby restored

The retained lobby is restored to `fd84f4a` / MSQ-152, with 14 ready-made NGD
library specimens, the original static architecture and original rifle/F6
integration. The owner checked the restored lobby and accepted it on 2026-09-29:
[acceptance](Approvals/LobbyRollback01-OwnerAcceptance01.json).

## Scope and preservation

Four integration/build source files were restored from the audited baseline;
14 later custom destruction source files and 801 custom packages were removed
from active Source/Content. Current Source/MeridianSquad content matches the
baseline in Git; pre-existing checkout line endings remain preserved. Custom
packages were confined to DemoTiledColumn01, ReinforcedColumn01,
LobbyColumns01 and DestructionScaling01. Original source archives, approvals,
scripts and historical evidence remain available. The appended custom debris
collision profile was removed; unrelated config and owner project/plugin edits
were preserved. No repository-wide reset or history deletion was performed.

Before mutation, 907 exact files, Git changes, vendor hashes and the live map
were preserved under `Saved/LobbyRollback01/Before/`. The full canonical T3D
comparison found 133 unchanged actor records; differences were the custom demo,
16 replaced columns and three floor sections. The extra Mass debug actor was
confirmed engine-transient. The custom asset referencer scan found only the
custom asset set and retained map, allowing exact historical map restoration.

## Verification and limits

- Map SHA-256: `94dbedbe2e516fc8cdde2d394f2b4c8c0a4d9573288e94772a6ebefafd54bc57`.
- `Saved/LobbyRollback01/Build01.json` and `Build01.log`: successful full
  Development Editor build, exact source/DLL hashes, 103.5 seconds.
- `editor-reopened.json`, `editor-reopened.t3d`, `lobby-restored.png`: actual saved
  map reopened in the freshly built editor, with the 14 library specimens.
- `runtime-initial.json` and `rifle-concrete.json`: incomplete runtime captures
  gathered before owner acceptance. The concrete capture records zero shots and
  hits, so it does not prove actual damage. Additional glass/F6 automated runs
  were stopped; do not represent these as completed tests. The exact MSQ-152
  source/map baseline and its existing evidence remain applicable, and the owner
  separately accepted the restored scene/play state.
- `native-settings.json`: actual Astra/max; default service tier and fast disabled
  in launch arguments. Native turn metadata does not expose actual service tier.

The production run was intentionally stopped after the owner's check, preventing
further automated gameplay interaction. Its launched editor exited with the run;
controller reopened the saved map for handoff. The independent
[MSQ-172 technical review](LobbyRollback01Review.md) passed without blocking
findings. Its limited runtime coverage and line-ending qualifications are recorded
explicitly. Controller accepted the scoped evidence and owns the local closure commit.
