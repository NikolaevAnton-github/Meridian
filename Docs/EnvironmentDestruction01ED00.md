# MSQ-140 / ED-00: copied lobby and baseline

Delivered 2026-09-24 for controller review. Candidate **MSQ-140-Candidate01**;
source revision `157d285173aed0dc2c6f9c548828751165e7ee5b`.
Authority: `Docs/Tasks/EnvironmentDestruction01/ED-00.md` and
`Docs/Approvals/EnvironmentDestruction01-LobbyLab01.json`.

## Result and preservation

`/Game/Maps/L_OpeningLobby_DestructionLab01` is saved, loaded and ready to inspect.
It contains the retained lobby, with **no destructible specimens added**.
The editor is outside PIE with no dirty map/content packages. The controller owns
commit, registry administration, issue status and acceptance; the executor made
no commit or successor dispatch.

The copy represents the saved source state: both dirty-package lists were empty
before copying. Native `EditorLoadingAndSavingUtils.save_map` invokes
`FEditorFileUtils::SaveWorld`, which duplicates an existing on-disk world through
`ObjectTools::DuplicateSingleObject`, including world/object identity remapping.
Epic MCP loaded the resulting map. No filesystem map copy or Save All was used.

| Package/file | Final SHA-256 |
| --- | --- |
| `Content/Maps/L_OpeningLobby_PainterStone01.umap` | `b28fa0f6e8bb80dcc71b4789df9c3e2375a3cf8b1da67021225584e4560fd92f` |
| `Content/Maps/L_OpeningLobby_DestructionLab01.umap` | `127a74eca42a0942cd5aed2a6035f54d19378d8415242f996090364bba397b44` |
| `Config/DefaultEngine.ini` | `a47c56f4e860ce8085347f057503a3211b16a62a559cbedcdc95412d7c31e3af` |
| `MeridianSquad.uproject` | `189ba61a9584348db935ca2c958b8362ed14f7d0ac2d3ead23c2a83211962202` |

The lab map is 261,014 bytes and matches the existing Git LFS filter. There is one
persistent level, no World Partition, no external actors, and no separate map
build-data package. No external actor/object directories were required or created.
All 129 listed actors and all 150 actor components belong to the lab package.
The source world is absent from its dependency references. Actor transforms and
the 108 recorded StaticMeshComponents' transforms, mesh/material assignments and
collision settings match after normalizing the copied world name. The dependency
graph also matches. Ownership of all 150 components was checked separately.

All **118 preflight files** (115 map/dependency packages plus task-injected AGENTS,
engine config and project descriptor) retained their SHA-256 values during worker
verification. No project package was missing from the recorded dependency closure.
Initial owner edits were `Config/DefaultEngine.ini` and `MeridianSquad.uproject`.
The AGENTS addition and generated `.multica/` context were Multica task injection,
not owner edits. The daemon restores AGENTS to its committed form after execution;
that expected lifecycle change is not a source-package preservation failure.
Owner files and source/shared packages were preserved. These observations do not replace historical
acceptance manifests. Shared meshes, materials, textures and classes remain
read-only dependencies; ED-01 must duplicate any asset it intends to modify.

## Measured baseline

Hardware: Ryzen 7 9800X3D, RTX 5090, driver 617.14; Windows 11 25H2.
Engine: **5.8.3-58210709+++UE5+Release-5.8**, Development editor, D3D12/SM6.
Native worker configuration and process flags specify **gpt-6-astra, max,
default service tier**; the native turn record independently reports Astra/max.
The turn record does not separately repeat the tier. The controller confirmed it
was not operating the editor; one UnrealEditor process (PID 2748) was observed.

The baseline is a fixed-camera **floating PIE** session, with the inherited
OpeningLobby game mode, player, weapon, HUD and existing GASP enemy/AI work.
“Before specimens” does not mean an environment-only or zero-physics workload.
No shots, break events, debris or density fixtures were introduced.

- All ten recorded scalability groups were 3 (Epic). TSR, Lumen GI/reflections,
  virtual shadow maps, Nanite and ray tracing retained their existing settings.
- Window settings and CSV system resolution: 1920 x 1080. The live player HUD
  viewport API returned **1920 x 1082**; the native still is 1920 x 1080. Preserve
  this discrepancy when comparing future measurements.
- `r.ScreenPercentage=0`, `sg.ResolutionQuality=0`, desktop automatic mode 1,
  and PIE editor-screen-percentage override 1 were retained. Effective internal
  render resolution was not independently measured; this is not a native-100%
  rendering claim. No DLSS cvars were present.
- `r.VSync=0`, `t.MaxFPS=0`; CSV metadata nevertheless reports target frame rate
  120 and the observed cadence is near 8.33 ms. This is not an uncapped capacity
  benchmark. Background-editor throttling remained enabled; Unreal foreground
  ownership was observed, but not continuously sampled throughout the capture.
- Only GPU CSV instrumentation changed temporarily:
  `r.GPUCsvStatsEnabled: 0 -> 1 -> 0`. Rendering/quality cvars were not changed.
  Profiling and editor overhead remain included.

Native CSV recorded **3274 frames**, approximately **27.39 seconds** of frame
time (CSV metadata capture duration 27.34361 seconds). The stationary pawn had
settled before capture; start/stop timestamps and world age are preserved.
Statistics below use all numeric frames; P95 is nearest rank.

| Native CSV field | Mean ms | P95 ms | Maximum ms |
| --- | ---: | ---: | ---: |
| FrameTime | 8.3651 | 8.3415 | 51.2905 |
| GameThreadTime | 5.3126 | 6.8530 | 40.9166 |
| GPUTime | 3.9080 | 4.2841 | 5.0178 |
| Exclusive/GameThread/Physics | 0.0306 | 0.0401 | 0.4921 |
| Exclusive/AllWorkers/Physics | 0.1036 | 0.1535 | 0.7148 |

The 51.2905 ms maximum is the first captured frame; it is retained in the table.
After that frame the maximum is 11.4201 ms. No causal attribution is established.
The native `RenderThreadTime` signal is almost zero (mean 0.0031 ms, P95 0.0010 ms,
maximum 3.9101 ms); treat it as an unsuitable independent render-thread budget.
The raw CSV also retains exclusive render-thread scopes for later investigation.
Physics worker scopes represent accumulated CPU work, not total solver wall time;
do not add them to Game/GPU timings. Destruction budgets, density limits and
break-event P95 remain unmeasured.

## Views, route and reset

Coordinates are Unreal centimetres, rotation is pitch/yaw/roll, HFOV is 90 degrees.

| View | Camera XYZ | Rotation |
| --- | --- | --- |
| Entry | `-500, 0, 172.15` | `-10, 180, 0` |
| Hall / measured stationary view | `1900, 0, 172.15` | `0, 180, 0` |

Comparable native editor captures exist for both maps at both views, at
1961 x 1283. They preserve the same geometry/material composition. Editor light
icons and a PlayerStart outline remain visible despite UI/game-view capture
requests, and temporal shading differs slightly; these are not pixel-identical
acceptance images. `runtime-stationary.png` is the separate native PIE still.
No image retouching, new lighting, material adjustment or architecture work was done.

A short centre-aisle route was actually traversed with CharacterMovement input:
pawn centre `(1900, 0, 90.15)` toward negative X, ending at
`(-1501.875, 0, 90.15)` after **9.57 seconds / 34.02 metres**. All 47 recorded samples
were walking. The starting placement was transient; no teleport occurred during
the observed segment. Move/look input was ignored for the bounded automated
observation, with forced movement input supplied to the existing pawn. Stopping
PIE removed this transient state. This route had no simultaneous timing capture;
it does not validate combat, rubble traversal or subjective motion quality.

To inspect/reset: stop PIE, open `/Game/Maps/L_OpeningLobby_DestructionLab01`, then
start floating PIE. Its unchanged PlayerStart is `(-2850, -105, 100)`.
For the stationary comparison use the Hall pose above and the recorded settings;
for traversal begin at the recorded pawn centre and walk along negative X to -1500.
Stop PIE to discard runtime actors and reopen the saved lab if necessary.
Never save unrelated dirty packages. Future authorized captures need a new
evidence identity; the ED-00 helpers refuse existing artifacts.

## Local specimen candidates

Both are existing industrial crate variants, approximately **120 x 80 x 90 cm**,
with Body and Metal material slots. Their current source/Unreal bytes match the
existing BenchA/BenchB acceptance manifests (22 checked artifacts total).
Historical accepted evidence describes eight closed box components and 864
triangles per crate; topology was not rebuilt or re-reviewed in ED-00.

| Candidate | Unreal mesh | Editable sources | Possible role / limitation |
| --- | --- | --- | --- |
| BenchA crate | `/Game/Development/Benchmark/BenchA/SM_BenchA_Crate` | `Assets/Source/SmokeTest/OrchestrationAB/BenchA/Crate.blend` and `Crate.spp` in that folder | Candidate for low cover and local panel breaks; Body and Metal need an explicit physical material/damage decision. |
| BenchB crate | `/Game/Development/Benchmark/BenchB/SM_BenchB_Crate` | `Assets/Source/SmokeTest/OrchestrationAB/BenchB/Crate.blend` and `Crate.spp` in that folder | Alternative of the same object family; trim could support cosmetic debris. It is not evidence of a second distinct destruction material. |

The bounded search found no additional suitable editable nonstructural family to
establish a wood/masonry/other second specimen. Existing architectural assets were
excluded. Connected/intersecting box parts require an explicit derived fracture,
interior, collision and support plan; the render mesh is not already an approved
destruction asset. **Specimen/art selection remains pending before ED-01.**
No source was opened for editing, imported, placed, fractured or registered anew.

## Evidence and remaining limits

Evidence root: `Saved/EnvironmentDestruction01/ED-00/MSQ-140-Candidate01/`.

- Preservation/identity: `source-before.json`, `source-levels.json`,
  `copy-operation.json`, `lab-loaded.json`, `ownership-preservation02.json`,
  `final-editor-state.json`, `handoff-editor-state.json`, `worker-identity.json`,
  `native-processes.json`.
- Views: `source-entry-gameview.png`, `lab-entry-gameview.png`,
  `source-hall-gameview.png`, `lab-hall-gameview.png`, `runtime-stationary.png`,
  matching camera JSONs and `image-dimensions.json`. Earlier Epic stills are retained.
- Measurements: `baseline-stationary.csv`, `baseline-summary.json`, start/stop
  JSONs, `runtime-fixed-pose.json`, `runtime-measured-pose.json`,
  `render-settings-before.json`, `profile-cvars-discovery.json`,
  `settings-restored.json`, `route-observation.json` and its one-shot source.
- Inventory: `specimen-inventory-native.json`, `inventory-source-preservation.json`.
- Diagnostics: `diagnostic-excerpts.log`, `capture-limitations.json`, `footprint.json`.

The initial comparison report `ownership-preservation.json` incorrectly normalized
only package paths, leaving duplicated world object names unequal. Correcting the
comparer produced `ownership-preservation02.json`; the separate raw comparison
contains zero differences. No map change was made to obtain that pass.

A handled `FAppTime IsInGameThread` ensure occurred during early still-capture work
at 18:42 UTC. It was not repaired as part of this task. A deferred editor
`HighResShot` request later produced `source-entry-console.png` during lab PIE;
that misleadingly named file is preserved but **excluded as source-map evidence**.
The first PIE session ended before profiling, without an executor StopPIE command;
only the second, completed stationary capture supplies timing evidence. The early
session also logged a PoseSearch asynchronous-index warning. These observations
do not establish a new engine or gameplay defect caused by the map copy.

Recorded rendering, window and game-view settings were restored. The canonical
project-tree census is 59.965 GB including local history/services, excluding
reparse-point aliases and external engine/DCC installations. ED-00 evidence was
about 34 MB before packaging; no duplicate project, build or bake was created.

Review route: executor preservation/load checks and one primary independent
technical reviewer (`destruction_performance`), followed by controller evidence
and finding closure. The reviewer verified the copied contents, ownership,
settings restoration and bounded baseline; the remaining report precision
findings were corrected by the controller. Owner visual/play judgement and later
destruction implementation remain separate and pending.
