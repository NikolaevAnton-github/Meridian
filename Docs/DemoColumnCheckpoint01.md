# DemoColumnCheckpoint01 — current column checkpoint

2026-09-28. Direct owner request: commit the existing center-hall demo column,
inspect the recording, and propose per-shot destruction and settled-debris
retention options. Outside the task pool and Multica; no independent reviewer.
This checkpoint implements no destruction or retention changes.

## Saved identity

- Map: `/Game/Maps/L_OpeningLobby_PainterStone01`.
- Actor label: `EXP_DemoTiledColumn01`, actor `BP_BreakableObject_C_16`, origin
  `(0, 0, 0)`, scale `(1, 1, 1)`.
- Data: `/Game/Experiments/DemoTiledColumn01/Correction04/DA_DemoTiledColumn04`.
- Concrete: `/Game/Experiments/DemoTiledColumn01/Correction03/GC_DemoColumn03`.
- Current authoring reports 1,560 facing fragments, 156 mesh variants,
  1,092 clean-release and 468 bonded pieces. Intended envelope: 240 x 240 x 1800 cm.

The commit includes current runtime/authoring code, the saved lobby, and all 240
packages in this experiment directory, preserving predecessors and current
dependencies. Unreal binaries use LFS (approximately 880 MB total before LFS
deduplication). Eleven exact authoring source/script copies are archived under
`Assets/Source/DemoTiledColumn01/`. Original Saved evidence remains in place.
Unrelated local config, project-plugin edits, and the historical ED-02 draft
are excluded. No existing map, asset, or runtime source bytes were changed here.

Live read-only checks confirmed the named editor project/map, no PIE, and no
dirty map/content packages. The successful Correction04 compile02 fingerprint
record matches the current DLL and every source it records. Its preceding
compile01 log includes DemoColumnCladding and DemoColumnScatter compilation.
This reuses existing build evidence; it is not a new performance or gameplay pass.

## Recording and source observations

Owner recording: `D:/devgames/Запись 2026-09-28 144441.mp4`, duration 23.5333 s.
SHA-256: `443c58d996152215590c44e90915713bbe66785f77c2e4a0be1b2d9dbb5b9a78`.
Sampled frames show repeated impacts with little apparent local geometry change
around 3–7 s, followed by a larger release around 8–10 s. Additional shots near
14–17 s show a similar delay before a larger visible change. This establishes
the visible symptom, not the exact runtime branch responsible for every shot.

Facing and concrete use different paths. Clean facing detaches directly; bonded
facing first damages the substrate and detaches directly after another hit.
Concrete receives 2,000,000 external strain with radius 0 and propagation depth 0.
The installed UE 5.8 implementation selects the closest immediate cluster child;
it does not guarantee selection of the visible surface leaf. Large leaf geometry,
multi-level clusters, collision approximation, or a hit on reinforcement remain
possible contributors. Merely raising strain cannot make a prefractured leaf
split into smaller geometry. Exact per-shot attribution needs a focused runtime
probe if a correction is subsequently requested.

Facing debris currently has a fixed 12 s actor lifespan and no retention policy.
Live concrete asset settings: remove-on-max-sleep false, slow-moving-as-sleeping
false; maximum sleep 1–2 s and removal duration 2–3 s are stored but do not enable
sleep removal. Component removal permissions are true. This says nothing about
uninspected per-piece removal-on-break data. The older MSQ-156 performance and
removal figures describe another column and do not measure this demo.

Evidence: `Saved/DemoColumnCheckpoint01/` contains recording identity, sampled
frames/contact sheets, live-state readback, before fingerprints and copy checks.
Gameplay changes and retained-debris performance remain proposals, not delivery.
