# MSQ-141 / ED-01 — MSQ-141-Candidate01

Implemented and self-checked on 2026-09-24 under
`Docs/Approvals/EnvironmentDestruction01-ColumnCladding01.json`. One existing
column in `/Game/Maps/L_OpeningLobby_DestructionLab01` now loses local cladding
under real rifle impacts. The exposed structural backing remains solid.
Independent review is waived for this task by the owner's scoped decision in
`Docs/Approvals/EnvironmentDestruction01-ED01ReviewWaiver01.json`; queued MSQ-148
was cancelled. Executor self-checks are complete. Bounded controller acceptance
and owner visual/play acceptance remain pending.
Commit, issue status, registry and acceptance remain with the controller.

## Candidate identity and preservation

Base Git revision: `76f88649dce7b908f051d3db5077673e712cd82e`; no worker commit.
Before this task the lab LFS SHA-256 was
`127a74eca42a0942cd5aed2a6035f54d19378d8415242f996090364bba397b44`.
The final file identities are in `candidate-manifest02.json` under the evidence
directory below, including the map, native DLL, source, editable recipe and assets.
The original `candidate-manifest.json` remains immutable. Manifest 02 adds the
readability evidence and updated handoff/tooling; production map, assets, C++ and
DLL bytes are unchanged from manifest 01.

Source actor: `StaticMeshActor_35`, label `FB01_newNcolumnNN12p6NN2p4`, originally
`/Game/OpeningLobby/FunctionalBuild01/Meshes/SM_FB01_TallColumn` with
`/Game/OpeningLobby/MaterialsComplete01/SlabLayout01/MI_Slabs_035`.
Live inspection confirmed its centre `(-1260,-240,900)` cm, unit scale, zero
rotation, and approximately `240 x 240 x 1800` cm bounds. The source is an
eight-vertex cuboid. Original packages and Blender source remain unchanged.

The lab actor now references
`/Game/Development/EnvironmentDestruction01/MSQ141Candidate01/SM_ED01_ColumnBacking04`.
The added actor is `DestructibleCladding_0`, label
`ED01_Column035_LowerNorthCladding`, at `(-1260,-240,0)` cm. Its 32 meshes are
`SM_ED01_Cell03_00` through `SM_ED01_Cell03_31` in the same asset directory.
Their face material remains the shared, unchanged `MI_Slabs_035`.
New backing and non-front fragment surfaces use `M_ED01_Backing`, a plain rough
technical material (linear RGB 0.18/0.17/0.15, roughness 0.92). These surfaces,
including exposed end returns, await the owner's visual gate.

The final native scene audit finds exactly one changed existing actor (35) and
one added actor. All other actor/component inventory entries match ED-00.
All **120 protected file hashes** match the start, including the original lobby,
shared dependencies, editable source, and pre-existing `AGENTS.md`,
`Config/DefaultEngine.ini` and `MeridianSquad.uproject` edits. Those edits and
`.multica/` are unrelated controller/owner state and must be excluded from this
worker's file set. The review-waiver approval is also controller-owned. Binary
Unreal assets use the existing LFS rules; generated DLLs
and logs remain outside Git.

## Construction and behavior

The selected face points toward +Y/the aisle. Its lower course occupies world
X `[-1380,-1140]`, Y `[-124,-120]`, Z `[0,240]` cm. Physical thickness is **4 cm**;
the old 0.075 cm shader recess is not used as thickness. The original envelope,
120 x 240 cm slab pattern and front appearance are retained. Backing is at
Y = -124 cm; the untouched column above Z = 240 cm still ends at Y = -120 cm.

GeometryCollection classes and Geometry Script are available locally; the
inspected GeometryCollection Python library exposes no fracture-authoring entry.
This bounded alternative uses native Geometry Script assets and Chaos rigid-body
simulation on pre-cut convex StaticMesh components. It does not claim a clustered
GeometryCollection, propagation model or arbitrary runtime fracture.

| Parameter | Candidate value |
| --- | --- |
| Granularity | 32 deterministic clipped Voronoi cells; 16 per existing slab; seed 14101 |
| Support | Each cell is independently bonded to the intact backing |
| Damage | One contacted cell releases at point damage >= 10; actual rifle damage is 25 |
| Mass | Volume at 2600 kg/m3; tested cells 9/22 are 17.41/19.30 kg |
| Release | 4.5 cm outward clearance, then 80 cm/s outward impulse velocity |
| Rotation / damping | Initial angular velocity (25,0,+/-15) degrees/s; linear 0.5, angular 1.5 |
| Bounds | One cell per impact; fixed 32 components/bodies maximum for this specimen; authoring hard limit 64 |
| Retirement | No lifetime deletion; sleeping fragments remain until reset |

The clearance prevents flush convex seams from friction-locking a released panel.
Visual geometry and collision move together. Released fragments collide physically
with the static scene but **ignore weapon Visibility, Pawn and other PhysicsBody
objects**: they are debris, not cover or traversal obstacles. This is a deliberate
ED-01 limitation. Keeping moving fragments as generic Visibility blockers caused
the existing finite-projectile history guard to cancel firing while they moved.
The final implementation follows the existing physical weapon-prop convention;
it does not weaken that guard. Bonded cells and backing continue blocking shots.

`ADestructibleCladding::TakeDamage` consumes the existing `ApplyPointDamage` route
from `CombatProjectileWorld`. No rifle, projectile, timing, movement or AI source
was changed. The impacting bullet stops normally. Collision revision, piece ID,
affected bounds and reset generation are broadcast before changes. There is no
idle actor tick, accumulating component spawn, damage accumulation, dust or new audio.

Editable sources are
`Assets/Source/EnvironmentDestruction01/MSQ-141-Candidate01/cladding-recipe.json`
and `Scripts/EnvironmentDestruction01/ed01_geometry.py` / `ed01_author.py`.
Earlier mesh iterations remain preserved but are not referenced by the final map.

## Controls and reproducible checks

Open the lab and start floating PIE. Move from the unchanged PlayerStart toward
the chosen column. The recorded firing pose is pawn centre `(-1260,290,90.15)` cm,
camera about `(-1260,290,172.15)`, yaw -90, pitch -6. **LMB** fires the existing
rifle; **F7** resets only the specimen, preserving ammunition. **Y** uses the
existing slow preview with the default enabled mannequin. Stopping PIE also resets.

Aim A is `(-1335,-120,165)` and aim B is `(-1185,-120,105)` cm, separated by
approximately 162 cm. Verification injects the existing player's key input,
uses normal finite projectile launches, and records `OnBulletHit`; it never
substitutes debug damage. The existing enemy combat component is disabled only
inside the test PIE world. Stopping PIE discards that test state.

Evidence root: `Saved/EnvironmentDestruction01/ED-01/MSQ-141-Candidate01/`.

- `build-06.log/json`: successful Development Editor native build; final DLL.
- `normal05-complete.json`: five real rifle hits; A and B release pieces 9 and 22;
  the second round hits `StaticMeshActor_35` at Y = -124 cm. Three reset/rebreak
  cycles restore all 32 actual component identities and zero simulating bodies.
- `slow04-complete.json`: three real rifle hits repeat A, exposed backing and B;
  one reset restores the specimen. World/projectiles/rifle action rate are 0.25;
  hero custom dilation is 2.6, giving net hero rate 0.65.
- In both runs an untouched region remains blocking at Y = -120 cm. Removed
  regions expose backing at -124 cm; debris moves and sleeps. Moving fragments
  add no geometry-history barriers. Reset retains the existing single-frame
  history invalidation instead of bypassing it.
- `verification-summary.json`: all normal/slow acceptance assertions pass.
  Native `normal05-*` and `slow04-*` PNGs provide intact, removed and reset views.
- `readable03-*` PNGs and `readable-verification.json`: supplemental comparable
  intact, one-region, two-region and reset views address the controller's dark-face
  evidence note. The same frontal camera uses a transient PIE camera exposure-bias
  override of 1.0 with blend weight 1. Scene lighting and rendering quality are
  unchanged. This is diagnostic exposure, not a final lighting acceptance claim.
  Three actual rifle impacts again verify shell/core/shell behavior.
- `scene-final-audit.json` and `preservation-after-final.json`: scene scope and
  protected-byte checks. PIE is stopped, all packages are clean, Python remote
  execution is off, GPU CSV instrumentation is restored to 0, and background CPU
  throttling is restored to its original enabled state.
- `editor-state-after-readable.json` and `preservation-after-delivery.json` confirm
  the same clean/restored editor state and 120 unchanged protected hashes after
  the supplemental captures. `runtime-readable-editor.log` retains their log.

Earlier failed geometry, release, history-barrier and background-throttle runs
are retained as diagnostics. They are not passing evidence for the final candidate.
The obstructed `readable01` and overexposed `readable02` capture attempts are also
retained; use `readable03` for the supplemental comparison.

## Bounded local cost observation

`cost01.csv` records **2277 frames / 19.0107 seconds**, with one actual rifle
break and reset and no screenshot captures. Hardware: Ryzen 7 9800X3D, RTX 5090,
approximately 32 GiB installed RAM; UE 5.8.3-58210709, Development Editor PIE,
reported viewport **1920 x 1082**. Captured scalability groups are 3; TSR is selected.
Screen percentage and resolution quality remain automatic (both cvars 0);
internal render resolution was not independently measured. VSync and t.MaxFPS
remain 0, but the observed cadence is near 120 Hz, not an uncapped capacity claim.

| Native CSV signal | Mean ms | P95 ms | Maximum ms |
| --- | ---: | ---: | ---: |
| FrameTime | 8.3490 | 8.3352 | 28.9040 |
| GameThreadTime | 5.1823 | 6.3048 | 26.9503 |
| GPUTime | 3.8359 | 4.4467 | 5.1527 |
| Exclusive/GameThread/Physics | 0.0262 | 0.0336 | 0.3682 |
| Exclusive/AllWorkers/Physics | 0.1128 | 0.1840 | 0.6378 |

The nearly-zero RenderThreadTime counter is unsuitable for an independent render
budget. Worker physics is accumulated CPU work, not solver wall time. Do not sum
these overlapping timings. Samples include editor, profiling, setup/reset and
verification overhead. This is a local observation, not a density/FPS guarantee or
a representative break-event P95 budget. Screenshot-bearing functional runs are
retained separately and include capture hitches.

For slow04, cost01 and the supplemental readable runs, background CPU throttling was temporarily disabled
in memory because losing focus otherwise reduced PIE to about 3 FPS and invoked
the existing overload guard. It was restored on completion. Rendering quality was
not reduced. Workspace footprint was observed at 101.39 GB, below the 250 GB cap.

Configured/native execution used `gpt-6-astra`, **max** reasoning, default service
tier and fast mode disabled. `worker-settings.json` records config, native command
flags and turn-context evidence. The native turn reports max but omits the tier
field; standard speed is established by the default-tier/disabled-fast launch flags.

Not covered: all 32 fragments active together, sustained automatic fire, airborne
debris as bullet cover, pawn/rubble traversal, accumulated damage/support graphs,
density growth, final fracture art/effects, or owner motion/play judgment.
Independent technical review was waived only for ED-01. No successor task was
dispatched.
