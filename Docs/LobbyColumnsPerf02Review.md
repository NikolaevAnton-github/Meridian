# MSQ-159: LobbyColumnsPerf02 independent review

**Verdict: PASS for the scoped technical change and visual equivalence in the supplied views. No blocking findings.** Reviewed MSQ-158-Candidate01 / Build05 against `83181e1bd0e6913825d26cd3dcf3066f0bebab5e` on 2026-09-28. Owner play/design acceptance remains separate. This review grants no new production scope or guaranteed frame rate.

The reviewer inspected the six-file implementation diff, exact identities, raw timing data and all eight comparison images, then ran focused PIE checks. No implementation, asset, configuration file or existing evidence was edited; no commit was made. Reviewer additions are this report and `Saved/LobbyColumnsPerf02/Review/`.

**Candidate and evidence identity**

All six current source hashes match `compile05.json` and the tested Build03 source hashes. The loaded module in the independent session (PID 30460) was the current `Binaries/Win64/UnrealEditor-MeridianSquad.dll`, SHA-256 `f103868fa227fcc761e3b5490aee7a190e95d321124fdb6b9db048d4efd23f43`. All 62 entries in `evidence-manifest05-aligned.json` match their bytes and hashes. `Review/identity-and-timing.json` contains the exact per-file identities; `Review/loaded-module.json` binds the independently loaded DLL.

The four baseline source files were reconstructed in memory from `83181e1` with only the documented CSV timers. Their hashes match both `baseline-source.json` and `compile04-baseline.json`. The unused pool class compiled into the baseline creates no renderer: the baseline runtime records zero shared components and 2,368 visible original components. Build05 records 888 visible shared components carrying the same 12,288 instances, with all 2,368 original query components retained.

The reviewer used a separate MSQ-159 native session. The live native process requested Astra, max reasoning and default service tier with fast mode disabled; native turn context confirms Astra/max. Profile and sanitized process evidence are in `Review/reviewer-profile.json` and `Review/native-process-settings.json`. Backend service-tier telemetry is not separately emitted in the native turn context.

**Technical assessment**

| Criterion | Assessment and evidence |
| --- | --- |
| Shared handles and removal | `LobbyFacingPool.cpp` uses monotonic handles and weak owner identity. Swap removal repairs the displaced handle's instance index; migration updates the existing handle after allocating the destination group. Empty groups remove their lookup entry before reuse. `DemoColumnCladding::EndPlay` removes the owner's entries; world deinitialization clears the pool. Independent deletion of a middle column reduced instances exactly from 12,288 to 11,520, with zero surviving render/query mapping errors. A new PIE world restored all 16 columns and 12,288 instances. See `Review/owner-lifetime.json` and `Review/world-restart.json`. |
| Hit ownership and F6 | Visible pool components have no collision; original column components and item maps still route NGD hits. The saved neighbour probe hits actor 47, actor 48, then actor 47 after removal, with query items 1, 1, 0. Applicable Build03 probes and all 14 projectile contract checks pass. All 31 NGD props retain identity, become ready and advance reset generation in `reset-all03.json`; the independently exercised F6 restores all 16 lobby columns. |
| Blocker identity and history | Both samples remain at the original `AdvanceFrame` boundaries (`CombatProjectileWorld.cpp:538` and `:605`). Sequential snapshots compare component identity, transform and extent; reordered identities use the full lookup fallback, while same-count replacement invalidates history. Live owned-component reads preserve addition/removal, collision response, NGD filtering and the original treatment of temporarily unregistered components. The independent 13-check registry probe passes. |
| Actor and level lifecycle | Initial registration includes existing actors; spawn/post-registration handlers add owners and destruction/removal handlers remove them. Weak invalid owners are pruned, and EndPlay unbinds handlers. Active-level, association/disassociation, level-collection and nonpersistent WorldSettings filters match the installed UE 5.8 `EngineUtils.h` iterator rules. Actor destruction and world recreation were exercised live. Arbitrary streamed-level/travel combinations were assessed in source, not exhaustively exercised in PIE. |
| Carrier updates and support | Changed, newly assigned and previously moving carriers update in original tile order; the extra stationary update clears velocity. The external-fracture sentinel remains active. Released leaves are sorted into the original ascending order; support scans, retention rules and wake calls remain in place. The independent damaged-column sequence covers movement within/across cells, return, external fracture and F6: seven snapshots, 1,348 ticks, zero mapping/support/registry mismatches and zero stationary attached-tile speed. Registry audits reach 5,754 with zero mismatches. See `Review/independent-damaged-transitions.json`. |
| Ordinary Play defaults | A fresh editor and ordinary PIE start use SharedFacing=2, ActiveFacing=1 and BlockerRegistry=1. Audit count is zero before the reviewer enables diagnostic mode. All final candidate timing samples also have audit count zero. See `Review/ordinary-play-defaults.json`. |

`Review/functional-validation.json` records applicability checks against the original worker evidence. The existing runtime verifier was reused with only its output directory redirected. Its independent run passes. The prior 33,924-audit damaged-transition result remains applicable because the Build03 and Build05 source bytes are identical.

**Independent visual assessment**

Directly inspected `baseline02-{intact,settled,reset,reverse}.png` against the corresponding `visual03-*` images. In the intact, reset and reverse pairs, column silhouettes, tile layout/detail, material appearance, light patches and cast-shadow structure remain consistent. No missing facing, disabled shadows or visible simplification was found in these views. The settled pair retains damaged edges and debris appearance; exact fragment positions and unrelated enemy damage differ, so it is not a pixel-identical simulation comparison. Rifle idle pose also varies independently of this change.

The checked source preserves the original meshes and mesh-default materials, retains a renderer fallback when materials differ, and leaves carried/loose/shard paths intact. The material audit contains only textures/constants, without actor-position, bounds or instance-random dependencies. The 148-mesh audit reports one LOD per mesh. These support the image assessment, rather than substitute for it. Runtime material/renderer overrides outside the documented fixed-material lane, every possible camera angle and owner aesthetic/play acceptance are not covered by this verdict.

**Timing assessment**

PASS for the corrected final comparison. Independently recomputed all 40 Frame/GT/RT/GPU summary rows and checked the published `performance05-aligned.csv`. Every mean, median, p95 and p99 matches. The 10 final captures contain 25,180 retained physical frames, at least 1,731 per state, with no invalid required cells or near-zero RT/RT-critical-path values.

The current parser checks header-prefix compatibility, removes repeated headers and metadata before selecting the common `[5:-5]` physical-frame window, and retains anomaly diagnostics. It reproduces all 15 historical frame-alignment references, including 3,137 anomalously small RT records. Those historical RT aggregates are rejected for performance conclusions; the anomaly's engine cause remains unestablished. No scope sum or conditional trimmed mean was substituted for RT.

Final frame milliseconds, baseline → Build05:

| State | Mean | Median | p95 | p99 |
| --- | --- | --- | --- | --- |
| Intact | 11.407 → 7.668 | 11.235 → 7.501 | 13.989 → 9.730 | 15.402 → 10.743 |
| Firing | 12.197 → 8.572 | 12.029 → 8.386 | 14.935 → 11.400 | 17.136 → 13.083 |
| Settled | 12.640 → 8.166 | 12.473 → 7.950 | 15.270 → 10.426 | 16.666 → 11.612 |
| Post-F6 | 9.859 → 7.652 | 9.680 → 7.446 | 11.870 → 9.773 | 13.610 → 10.919 |
| Reverse | 9.816 → 8.017 | 9.691 → 7.839 | 11.657 → 10.108 | 12.731 → 11.070 |

`Review/timings-reviewed.csv` includes all four metrics and both runs. Matching settings specify 1984×1313, quality groups 3, VSync off, no fixed step/smoothing, t.MaxFPS=0 and the same temporary 1000 FPS editor upper bound. The capture script uses matching views, 22-second static windows and a 30-second firing window with 18 shots across three columns. Final timing captures contain no screenshots. The worker's controller attribution and pilot remain supporting evidence, not replacements for the final comparison.

Frame distributions improve in both hall views; GT and RT medians improve while GPU medians remain close. This is one bounded paired PIE comparison, with normal enemy activity, scripted view changes and state-sampling overhead. Chaos trajectories vary. Post-F6 measures the restored steady state, not the reset hitch. Firing median 8.386 ms and the reported tails exceed the 8.333 ms budget for sustained 120 FPS; no universal 120+ FPS claim is supported. Simultaneous destruction of all 16 columns was not benchmarked. Overlapping shadow wait and worker scopes must not be added together.

**Restoration and handoff**

`Review/cleanup.json` confirms PIE stopped, no dirty map/content packages, no editor pool actor, diagnostic audit disabled, controller-original camera/throttle restored and the 120 FPS editor upper bound retained. The editor was initially closed; the reviewer launched it for testing and closed that exact process gracefully after the clean-state check (`Review/editor-exit.json`). Current source/DLL, owner-file fingerprints and the 62-file evidence manifest were rechecked after testing. Git reports no Content/Assets changes.

No implementation correction is requested. Controller acceptance, issue administration and the task-scoped local commit remain with the controller. Owner play/design acceptance remains open.
