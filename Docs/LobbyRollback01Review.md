# MSQ-172: Independent technical review of MSQ-171

2026-09-29. **PASS for the authorized library-only rollback. No blocking technical
findings.** This verdict covers MSQ-171-Candidate01 on working-tree base
`51536caeb65cc5e00341dc1975d33aad4fe7f030`, restored to `fd84f4a` / MSQ-152.
Owner scene/play acceptance is separately recorded in
`Docs/Approvals/LobbyRollback01-OwnerAcceptance01.json`; this review grants no new
design acceptance and performs no additional editor or PIE tests.

## Candidate identity and retained behavior

- All 66 active module files match `fd84f4a` after Git line-ending normalization;
  the source inventory has no additional files. All 66 current source hashes and
  the current DLL match `Saved/LobbyRollback01/Build01.json`. The full Development
  Editor build succeeded in 103.5 seconds; `Build01.log` records the successful link.
- DLL SHA-256: `4d2092c5948192c7d6d9bd8768c0628d4553aa4a57f32d8268c9bbab1adb6831`.
- Map SHA-256: `94dbedbe2e516fc8cdde2d394f2b4c8c0a4d9573288e94772a6ebefafd54bc57`.
  Current map, archived baseline and Git LFS identities at both `fd84f4a` and
  `9e6646b` agree. The historical Build02 hashes cover six relevant source files;
  all six still match. The rebuilt DLL is identified by Build01, not the older DLL.
- Direct inspection confirms the retained NGD collection-bounds exception and
  rifle hit delivery in `Source/MeridianSquad/CombatProjectileWorld.cpp:285` and
  `:615`, F6 binding in `CombatRifleComponent.cpp:123`, and reset/material-override
  preservation in `NGDPropComponent.cpp:226` and `:293`.

## Scene, removal and preservation

`editor-reopened.json` matches the correctly loaded baseline's 143 actor inventory
and all 14 specimen configurations, transforms and material overrides. The
reused `scene-property-audit-canonical.json` compares complete T3D actor properties:
133 unchanged records, with the remaining differences confined to the custom
demo, 16 replaced columns and three custom floor sections. The floor changes are
the column-seat meshes/material slots; the four tall-column changes replace the
original `SM_FB01_TallColumn` with custom upper geometry. The only extra
non-column actor is `MassDebugVisualizer`, whose recorded engine header hash and
`Transient` declaration were verified. `Saved/LobbyColumns01/before.json` was not
used as the restoration baseline.

I inspected the actual `lobby-restored.png`: the original static tall-column
architecture is visible. That single view is supporting geometry evidence;
the complete saved-map identity and inventories establish scene coverage.

- Four integration/build files restored; 14 custom source files and 801 custom
  packages absent from active Source/Content. The pre-removal referencer audit
  covers exactly those 801 packages, with the retained map as their only external
  referencer. Current source/config/project and baseline/reopened T3D scans find
  no removed custom implementation or package references.
- All 907 before-snapshot files, totaling 3,593,480,203 bytes, have matching archived
  sizes and SHA-256 hashes. All 481 vendor files and the owner project/plugin
  descriptor retain their before-snapshot bytes. The config delta is precisely
  the appended custom debris collision-profile removal.
- Of 86 snapshot files outside the rollback mutation manifest, 82 remain byte
  identical. The four differences are administrative documentation:
  `AGENTS.md` changes only the auto-managed task-brief pointer; `Docs/ProjectState.md`
  and the two rollback task briefs record owner acceptance/review scope. Their
  exact diff is retained in `Review01/document-only-differences.diff`.

## Evidence qualifications and findings

**Informational — runtime coverage remains limited.** The new initial PIE capture
has 14 ready props. `rifle-concrete.json` records one press/release but **zero
shots, delivered hits and break events**, including its 15 samples. It does not
pass a concrete-damage or sustained-fire test. No new glass/F6 completion is
claimed. The applicable MSQ-152 evidence reports 42 passing focused checks,
including firing continuity, glass damage and material-preserving F6 reset;
combined with the restored source/map and owner's explicit acceptance, this
supports the bounded verdict. It is not a fresh Build01 gameplay test result.

**Low severity, resolved documentation precision — raw Git byte identity.**
`EnemyCombatPolicy.cpp`, `MeridianSquad.cpp` and `MeridianSquad.h` retain their
pre-existing CRLF checkout bytes; their Git blobs use LF. No content differs and
the before-snapshot and Build01 hashes agree. The current handoff correctly says
Git-equivalent content with preserved line endings, and explicitly records the
zero-shot runtime limitation. No production correction is required.

The existing scope/scene verifier was reused without its runtime runner: 11 of
12 checks pass; the remaining strict byte-preservation check is explained by the
four documentation updates above. Nine additional read-only checks cover the
current inventory, Git/map identities, archive recovery and referencer scope;
the sole raw-byte exception is the three CRLF files. Raw results remain intact
under `Saved/LobbyRollback01/Review01/`, with interpretation in
`resolved-qualifications.json`; no historical evidence was rewritten.

## Review execution

Fresh native session `01a0ecff-5c12-73d1-9bf0-e2774bfdee16` records actual
`gpt-6-astra` / `max`. Task config and native arguments specify `default` service
tier; launch arguments disable fast mode. Actual turn metadata omits service
tier, so it is not independently observable there. Evidence:
`Saved/LobbyRollback01/Review01/native-settings.json`.

Review writes are confined to this report and `Saved/LobbyRollback01/Review01/`.
No production/editor mutations, staging or commits were performed by the reviewer.
Controller retains editor reopening, acceptance administration and the local
closure commit. Final fingerprint comparison is recorded in
`Review01/final-integrity.json`.
