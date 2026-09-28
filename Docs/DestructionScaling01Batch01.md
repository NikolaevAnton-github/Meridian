# MSQ-162–167: direct destruction optimization batch

Status: implemented, built and self-verified. Owner visual/play/performance verdict remains pending.
Authority: [DirectBatch01](Approvals/DestructionScaling01-DirectBatch01.json). One direct executor, self-review, no Multica launch/dispatch or independent agent. MSQ-168 remains separate.

## Implementation

- Stable owner/reset-generation/local fragment IDs and state/pose revisions. Resolve pending projectile targets before instance swap-removal or fracture; pool reuse and world recreation cannot alias selected handles.
- Shared post-physics world lifecycle: native Chaos contact-island sleep, selected wake/impulse, temporary hold, move and release with explicit velocity. Persistent lobby/stacking fragments replace the former 12-second expiry, 32-shard eviction and permanent kinematic retention.
- Compatible static-mesh actor/body pools, bounded prewarm followed by growth, two-frame contact-callback quarantine, complete return/reuse reset, strong immutable resource caches and explicit allocation failure counters.
- Shared spatial bounds and cross-owner resting-contact dependencies. Exact engine hull sweeps validate physical supports; changed/moved/deleted supports wake dependents. Structural attachment remains separate from resting contact. Collision-driven concrete fracture stays disabled.
- Immutable hull snapshots use coarse UE Tasks batches, overlapping spatial publication and dependency invalidation. Small workloads run serially. Apply validates owner/generation/state/pose and recomputes invalidated results. Exact queries, UObjects and solver writes stay in safe phases.
- Compact intact facing: 768 original tiles become 36 render-only sections per column, preserving all 11,576 source triangles, material assignments and UV channels. A hit expands only its affected section; original query geometry remains authoritative. Shared material-compatible debris render groups batch updates and migrate by world position. Geometry Collection concrete retains its native Nanite renderer and exact rigid bodies.

## Important integration finding

Making detached bodies shootable initially made their movement trigger the arbitrary-static-blocker history barrier. Debugger evidence at `CombatProjectileWorld.cpp` showed `bHistoryValid=false` at a 34.62 ms frame, below the 250 ms overload threshold. The interim workload emitted only 3 of 18 presses and is **not** valid performance evidence.

Managed fragment bodies now use the same live-piece collision contract as managed Geometry Collections. Both history boundaries still sample component presence/query response, owner transform and stable occupant identity. Arbitrary unregistered moving geometry keeps the existing fail-closed policy. The focused follow-up emitted all 18 presses. Projectile sorting, deduplication and the step-start consumption rule remain unchanged.

The first support fixture exposed the limitation of a single lowest-vertex ray: a real planar contact could be missed after tiny lateral movement. Support validation now uses exact convex moving-shape sweeps. Triangle render geometry is excluded from the moving query shape because UE 5.8's `CastHelper` does not support it; original simple simulation shapes remain intact.

The first complete capture exposed premature per-body forced sleep fighting active contact neighbours (thousands of state revisions and repeated support queries). Final code lets Chaos settle entire contact islands naturally. Support invalidation still wakes sleeping bodies immediately when their known support changes.

A selected concrete move exposed another integration defect: assigning the leaf's kinematic-target field alone did not register it in Chaos' moving-kinematic list. Paused native evidence (`gc-kinematic-debug.json`) showed the valid selected leaf kinematic with a position target but its original pose. The final implementation calls `FPBDRigidsEvolutionGBF::SetParticleKinematicTarget`, which also updates that list.

## Evidence and delivery

Full builds, source/DLL hashes, debugger evidence, failure captures, focused checks and CSVs are retained under `Saved/DestructionScaling01/` and `Saved/Profiling/CSV/`. The stopped MSQ-161 fixture was not resumed. Derived assets are below `/Game/OpeningLobby/DestructionScaling01/Candidate01`; the candidate manifest and exact source provenance are checked in. Registration is inventory, not owner acceptance.

Final full Development Editor build: `build-11.log` / `build-11.json`, succeeded. The latter records every project header/source and the exact DLL SHA-256 used in PIE. `delivery-verification.json` verifies those hashes, all 490 immutable source inputs, registry hashes, 18 actual shots in both accepted captures and zero render/query mapping errors. The candidate's authoring/provenance bytes are protected against checkout line-ending conversion.

- `focused-05.json`: 16 passed checks covering cross-owner support, moved support, native sleep, second impulse, selected hold/move/release, thin-body CCD, persistence beyond 12 simulation seconds, held F6 reset, stale handles, growth/reuse and exact serial/parallel comparison. Earlier `focused-03` used wall time while the editor was throttled; `focused-04/05` use simulation time.
- `transitions-02.json`: 17 passed checks for exact selected GC movement/release, deletion of a lower support, owner deletion, render-cell migration, material regrouping, custom-depth fallback and return to shared rendering.
- `history-and-world-02.json`: 13 existing blocker-registry transition checks plus two old/new-world identity checks passed. Both sampling boundaries remain active. The source audit confirms hit capture precedes swap/removal and pending hits do not redirect to the swapped-in neighbour.
- `final-world-recreated.json`: all 16 columns and 576 compact sections restored with zero query/render mapping errors and zero old fragments. The preceding deletion fixture intentionally left 15 owners until world recreation.
- `registry-final-validate.json`: no artifact/evidence changes. `footprint-final.json`: 85.81 GB / 79.92 GiB project tree including Git and generated data, below the 250 GB limit.
- Representative PIE views: `final-damaged-04.png`, `final-pile-01.png`, and `final-intact-01.png`. Original meshes, physical hulls, UV/material detail and shadows remain. These are technical visual checks, not owner acceptance.

## Approximate frame time

One short lobby workload, 16 columns, the same 18 semi-auto presses, 1280 x 722 PIE viewport, Epic quality, VSync off. Accepted runs: production `before-02` and final `after-02`; full CSVs are retained. Medians exclude five edge frames at each end of each six-second window.

| Phase | Before | After | Change |
| --- | ---: | ---: | ---: |
| Intact | 7.61 ms | 7.04 ms | -7.5% |
| Moving / settling debris | 8.20 ms | 11.36 ms | +38.6% |
| Settled scene | 7.72 ms | 8.92 ms | +15.5% |

This is **not a net destruction frame-time win in the representative scene**. The old path retained 53 ceramic entries at the damaged sample and 48 at the settled sample; the final path preserved 81 at both samples, plus individually interactive concrete. It no longer buys speed by expiry, eviction or permanent kinematic retention. Physics, body synchronization and persistent query/support state consume the saved render budget. The moving window also reflects different physical settling; this is a representative behavioral comparison, not deterministic identical-body replay or a large-battle estimate.

The intact shared renderer fell from 888 to 216 components and from 12,288 to 576 instances across 16 columns. All source triangles remain. Moving-window shadow initialization fell from 1.83 to 1.09 ms; the fragment manager cost 0.44 ms while moving and 0.16 ms settled. Native contact-island sleep reduced the previous forced-sleep implementation's moving manager cost from 2.73 ms to 0.44 ms. These CPU scopes overlap other work and must not be added as whole-frame savings.

GPU medians were approximately 4.07 -> 3.86 ms intact, 4.35 -> 4.40 ms moving, and 4.14 -> 4.24 ms settled. The near-zero `RenderThreadTime` CSV column is invalid for claims and is excluded. Small-run variance, active enemy behavior and additional persistent bodies limit extrapolation. Owner judgement remains open; MSQ-168 was not executed.

Unrelated owner changes in `Config/DefaultEngine.ini`, `MeridianSquad.uproject` and `Docs/EnvironmentDestruction01ED02.md` are excluded from this delivery.
