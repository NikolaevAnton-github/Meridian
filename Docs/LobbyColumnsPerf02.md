# MSQ-158: LobbyColumnsPerf02

Candidate **MSQ-158-Candidate01 / Build05**, ready for independent review. Base: `83181e1`. No worker commit. Authority and scope remain `Docs/Tasks/LobbyColumnsPerf02.md` and `Docs/Approvals/LobbyColumnsPerf02-OwnerScope01.json`.

## Implementation

- `LobbyFacingPool.h/.cpp`: transient game-world rendering in six spatial cells, using the original 148 meshes, materials and shadows. Attached facing keeps 12,288 instances while visible components fall from 2,368 to 888 (62.5%). Per-column query ISMs and NGD hit/item ownership remain unchanged. Monotonic handles plus weak owner identity repair render swap-removal, cell migration, EndPlay and F6. Material overrides outside the audited defaults retain their original renderer.
- `DemoColumnCladding.h/.cpp`: update tile poses by changed carrier, including a stationary update that clears velocity. Preserve the per-tick external-fracture sentinel and existing support/retention polls. Poll released concrete in the original ascending order. Carried facing, loose tiles, shards and retention limits keep their existing routes.
- `CombatProjectileWorld.h/.cpp`: register actor lifetimes and read their owned components live at both original sample boundaries. Contiguous blocker snapshots avoid per-frame hash-table construction and normal-frame hash lookups; a fallback preserves order-independent comparison. Diagnostic mode compares both membership and history decisions against the original world scan.

No assets, owner configuration, fragment limits, geometry detail or scene layout were changed. All facing meshes have one LOD. Material graphs contain texture samples/constants, with no actor-position, bounds or per-instance-random dependency. Non-default runtime renderer overrides are outside this fixed-material lane.

## Measurement

Pilot: three neighbours, 444 to 148 visible components; median RT 10.059 to 9.721 ms in the same initial view. Movement, cross-cell movement, external fracture, firing and reset passed before the hall rollout. Controller attribution is reused; disabling shadows was never a production change.

Final paired captures use original `83181e1` production paths plus CSV timers (`compile04-baseline`) and Build05. The pool class remains compiled but creates no render actor in the baseline. Both runs use 1984x1313, identical scalability (all quality groups 3), VSync off, `t.MaxFPS=0`, smoothing/fixed step off, the same views and an 18-shot sequence across three columns. Unreal's editor clamp applies even with smoothing disabled: its upper bound was raised transiently from 120 to 1000 for both runs, then restored. Every state contains at least 1731 valid frames. Five boundary frames at each end are excluded; no outlier trimming.

Median milliseconds, **baseline / Build05**:

| State | Frame | GT | RT | GPU |
| --- | --- | --- | --- | --- |
| intact | 11.235 / 7.501 | 11.296 / 7.141 | 8.999 / 7.146 | 4.993 / 4.865 |
| firing | 12.029 / 8.386 | 12.063 / 8.358 | 9.306 / 7.273 | 4.672 / 4.648 |
| settled | 12.473 / 7.950 | 12.490 / 7.730 | 10.101 / 7.695 | 5.046 / 4.933 |
| reset | 9.680 / 7.446 | 8.652 / 6.860 | 9.675 / 7.426 | 5.011 / 4.868 |
| reverse | 9.691 / 7.839 | 8.586 / 7.315 | 9.671 / 7.797 | 5.148 / 4.996 |

Build05 frame distribution, milliseconds:

| State | Mean | Median | p95 | p99 |
| --- | --- | --- | --- | --- |
| intact | 7.668 | 7.501 | 9.730 | 10.743 |
| firing | 8.572 | 8.386 | 11.400 | 13.083 |
| settled | 8.166 | 7.950 | 10.426 | 11.612 |
| reset | 7.652 | 7.446 | 9.773 | 10.919 |
| reverse | 8.017 | 7.839 | 10.108 | 11.070 |

`Saved/LobbyColumnsPerf02/performance05-aligned.csv` contains mean/median/p95/p99 for **all four metrics and both runs**. Exact settings and summaries use the `long-baseline04` / `long-candidate05` prefixes; raw captures are `Saved/Profiling/CSV/LobbyColumnsPerf02-long-*.csv`. The opposite hall view also improves. GPU medians stay close to baseline; larger spatial bounds do not erase the CPU/render benefit in either measured view.

Median game-thread scope costs per frame, **baseline / Build05**, milliseconds:

| State | Blocker collection | Blocker comparison | Cladding tick |
| --- | --- | --- | --- |
| intact | 3.056 / 0.829 | 1.020 / 0.013 | 0.006 / 0.006 |
| firing | 3.054 / 0.907 | 1.015 / 0.014 | 0.478 / 0.304 |
| settled | 3.429 / 0.933 | 1.083 / 0.014 | 0.592 / 0.367 |
| reset | 1.556 / 0.769 | 0.247 / 0.014 | 0.007 / 0.006 |
| reverse | 1.563 / 0.836 | 0.247 / 0.015 | 0.007 / 0.007 |

The corrected parser excludes headers/footer structurally, verifies header compatibility, then trims a common physical frame window before converting metrics. Earlier summaries could retain one extra frame for a metric when numeric footer metadata survived conversion. Final `*-aligned.json` summaries supersede those statistics; original summaries and raw files remain preserved. All final frame/GT/RT/GPU samples are finite, with zero near-zero RT or critical-path samples. Anomalous samples in earlier captures remain included and explicitly flagged with source-line ranges. `csv-alignment-verification05.json` matches the controller's independent frame counts and all-row statistics for the earlier captures.

These are bounded PIE results, not a guaranteed FPS or simultaneous destruction of all 16 columns. The firing windows include the scripted view changes, state samples and the normal enemy fixture; Chaos trajectories/stray enemy damage vary between runs. Reset timing is the stable post-F6 state, not the reset hitch itself. Earlier capped measurements and captures with screenshot-associated RT anomalies remain preserved in `capture-notes.json`; the exact engine cause was not established. Final timing runs contain no screenshots.

## Verification and evidence

All paths below are under `Saved/LobbyColumnsPerf02/` unless stated otherwise.

- `registry-lifecycle03.json`: 13 checks covering spawn, component addition/removal, same-count replacement, collision changes, movement, unregistration/reregistration and reorder semantics. `projectile-contracts03.json`: 14 existing timing/contact/reset checks pass. `candidate03-damaged-transitions.json` ends with 33,924 legacy-equivalence audits and zero mismatches.
- `candidate03-first-hits.json`, `candidate03-transitions.json` and `candidate03-damaged-transitions.json`: neighbouring first hits, swap maps, intact/damaged movement across cells, zero stale attached velocity, external fracture and F6. Render/query mappings and support invariants pass. Long runtime captures and `visual03.json` also pass `Scripts/LobbyColumnsPerf02/verify.py`.
- `reset-all03.json`: all 31 NGD props, including the central specimen and 14 other demo specimens, retain their IDs, become ready and advance reset generation. Non-lobby facing stays unpooled and preserves attached counts.
- `material-graph-audit.json`, `material-equivalence03.json`, `facing-lods03.json`: exact materials, shadows enabled, render-only collision disabled, 148 single-LOD meshes. `baseline02-*.png` and `visual03-*.png` provide separate same-view visual evidence. Independent visual and owner play/design acceptance remain pending.
- `compile05.json` binds all six source files and the loaded DLL. Build05 source hashes equal the fully tested Build03 source hashes; reuse of its semantic/visual evidence is intentional. `loaded-module05.json` verifies the loaded binary. DLL SHA-256: `f103868fa227fcc761e3b5490aee7a190e95d321124fdb6b9db048d4efd23f43`.
- `cleanup-final05.json`: PIE stopped, no dirty map/content packages or editor pool actors, original camera/throttle and editor FPS bound restored. `footprint03.json` measured 79.4 GiB of project-owned files, excluding junction traversal, before the final long captures; the task remains well below the 250 GB cap. Astra/max/default tier and fast-mode-off were verified in native settings and confirmed by the controller.

Controller owns issue status, independent technical/visual review, finding closure and the final task-scoped local commit. Unrelated owner edits and preparation documents remain untouched. Reproduction helpers are in `Scripts/LobbyColumnsPerf02/`; `evidence-manifest05-aligned.json` hashes the corrected handoff and primary evidence. The earlier manifest/report remain preserved as pre-correction evidence.
