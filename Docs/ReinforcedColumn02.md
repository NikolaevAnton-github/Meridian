# ReinforcedColumn02 — MSQ-156 Candidate01, rim correction

2026-09-25. Source revision 04 addresses the controller's finding in thread
`01a0da05-77f0-7cc8-a4a9-56baa7adac6b`: long straight fracture rims and large
planar cavity walls remained visible behind the reinforcement. The current
handoff includes a physical geometry correction and comparable editor previews.
The owner [waived independent review](Approvals/ReinforcedColumn02-ReviewWaiver01.json)
for this delivery. MSQ-157 was cancelled without a verdict; owner visual/play
acceptance remains pending.

## Physical correction

The supplied `Saved/ReinforcedColumn01/OwnerVideoReview01/frame-03.png` was
compared with the actual `authoring-detail-final08.png` and final deep view.
The finding also applied to those later images: the previous deformation faded
to zero across the stone layer and only displaced the concrete by up to 1.105 cm
per axis. This retained straight polygon rims and recognisable planar pockets.

`Scripts/ReinforcedColumn01/generate_progressive.py` now uses a composition of
monotone coordinate deformations at several spatial scales. Tangential motion
continues through the stone boundary, so the physical rim and the concrete
immediately beneath it are both irregular. The outer planes and the 1.8 cm
stone layer remain exact. Maximum per-axis displacement is bounded by 8.15 cm.
Shared interface boundaries are sampled consistently; interior refinement
limits the pre-deformation triangle edges to 4.5 cm instead of retaining a
coarse uniform fan. Adjacent solids use the same displaced interface.

The correction retains the seed positions, removable piece identities, cluster
membership, anchor geometry, reinforcement, preview omissions, materials,
material UV scale, damage settings, camera and inspection light. It does not
use a texture or lighting change to stand in for geometry correction.

`physical-relief04.json` measures the actual authored source faces against the
preserved previous generator, using the same pre-deformation sample positions:

| Measurement | Previous deformation | Revision 04 |
| --- | ---: | ---: |
| Median best-plane residual on 2,378 concrete faces of at least 150 cm2 | 0.349 cm RMS | 1.354 cm RMS |
| Median bend of 735 stone/concrete boundary segments longer than 15 cm, relative to their endpoint chord | effectively 0 cm | 2.744 cm |
| Maximum measured boundary bend | — | 10.443 cm |

These measurements establish a physical change. They are not a visual
acceptance score. Under the matched capture setup, the rim is irregular and
the large cavity walls have broken-up relief. The overall cavity still follows
the underlying Voronoi lobes; some coarse convex forms and short straight
sections remain visible. Exact vendor appearance is not claimed, and the
controller/owner visual finding is not independently closed by this worker.

## Current column

The same `RC01_ReinforcedColumn` at **(-1260, -240, 0) cm** remains in
`/Game/Maps/L_OpeningLobby_PainterStone01`, with static core actor
`StaticMeshActor_35` / `FB01_newNcolumnNN12p6NN2p4` at (-1260, -240, 900) cm.
The 240 x 240 x 1800 cm envelope, stone, placement and upper architecture are
preserved. Only the lower 0–280 cm perimeter is removable.

- 644 closed dynamic fragments, including 16 shallow stone chips; seed depths
  remain 4.5, 18 and 34 cm. There are 1,571,928 fragment triangles and 171,447
  core triangles. The denser physical surface increases the former triangle
  count from 809,856; performance has not been tested.
- 120 supported local clusters and 120 anchored leaves; 885 transforms total,
  with hierarchy counts 1/120/764. Initial states remain 644 dynamic and 241
  kinematic transforms. All 764 leaves have convex collision, with 766 hulls.
  The connection mode remains Chaos Minimal Spanning Subset Delaunay
  Triangulation, and damage thresholds remain 500000/50000/5000.
- 60 rays across four faces meet **2–6 distinct removable fragments** before
  the first static mass, at **38.62–63.55 cm** depth. Curved fragments can
  intersect a ray more than once, producing 2–10 intervals; the checker now
  retains those real intervals instead of treating every piece as convex.
  These are source measurements, not shot-count claims.
- A conservative continuous central square prism is at least **76.51 cm**
  wide. All 1,680 sampled anchor surface positions remain inside the core;
  minimum sampled clearance along the test axis is **8.46 cm**.
- The original 28-bar reinforcement geometry is unchanged, including ties,
  cover and embedded ends. Existing materials and the 50 cm concrete texture
  repeat are retained. NGD radius remains 0.14 m; impact/F6/runtime code is
  unchanged.

## Evidence and verification

Current evidence root: `Saved/ReinforcedColumn02/Candidate01/RimCorrection01/`.
Current source: `Assets/Source/ReinforcedColumn01/ReinforcedColumn02-Candidate01/column04.json`.
SHA-256: `f43ad5f18612f022442e7cb5029d423dd87490eb9e7b3e6403244343480cc6ee`.
`design04.json` records the unchanged seeds/grouping and current mesh counts.
Generator command: `generate_progressive.py --revision 04`; existing source
revisions are never overwritten.

- `source-check04.json`: all fragments and anchors are closed with positive
  volume; coordinates are finite. Total solid volume is 103,679,999.9897 cm3
  against the 103,680,000 cm3 envelope.
- `core-seams04.json`: 245 tessellation junction edges resolve to 241 paired,
  oppositely directed subsegments at 0.0005 cm tolerance. No open core boundary
  or internal orientation failure remains.
- `progression04.json` and `anchor-progression04.json`: depth, support and
  normal/UV checks pass. 2,000 sampled deformation Jacobians are positive;
  the minimum is 0.819. Source steel and material references match exactly.
- `asset-build04.json`, `asset-verification04.json`, `cold-reload04.json`:
  saved assets retain the hierarchy, anchors and collision after a complete
  editor restart. Source/render triangle counts agree: core 171,447, steel
  139,520, shallow preview 1,534,336 and deep preview 1,450,904. No invalid
  imported normal or tangent frames were found. Static collision remains
  complex-as-simple; normal/tangent recomputation stays disabled.
- All 144 original scene actors match their pre-edit snapshot; 813 protected
  vendor, lobby, owner and prior-evidence files are unchanged. No temporary
  preview actors or dirty packages remain, and normal visibility/shadows are
  restored. Temporary loopback Python remote execution is disabled again.
- The existing successful native `../Build05.json` / `../Build05.log` is reused:
  C++ source and the exact compiled DLL are unchanged in this correction.
  `native-settings.json` verifies configured and actual Astra/max/default,
  with fast mode disabled. No agent profile settings were changed.
- `final-checks.json` records syntax/diff/LFS checks, unchanged authoring inputs,
  upper geometry and matched capture settings. `final-manifest.json` hashes the
  exact current deliverables and selected evidence.

`Before/` preserves all 24 files from the preceding handoff against its original
manifest, including the prior assets, source, generator and report. The parent
evidence directory, source revision 03 and all older MSQ-154 records remain
unchanged. The previous full footprint measurement was 107.90 GB against the
250 GB cap; this correction's bounded source/assets/evidence sizes are recorded
in `final-checks.json`.

## Comparable captures and remaining gates

The four native captures are `authoring-intact-rim04.png`,
`authoring-shallow-rim04.png`, `authoring-deep-rim04.png` and
`authoring-detail-rim04.png`. They were inspected directly. Their camera, FOV,
light and deliberately omitted piece sets match the corresponding parent
`final08` captures. Materials and UV density are unchanged. No image processing
was applied. Matching metadata and mesh readbacks are included.

These are **editor authoring previews, not firing evidence**. A single temporary
inspection light reveals the surface. All preview actors/lights were removed
before saving; the normal intact column is loaded in the clean lobby editor.
No PIE, firing, F6, slowdown or performance session was started. The owner owns
all gameplay testing and final visual acceptance. The controller closed the
specific rim finding against the matched authoring capture and stopped the
independent review on the owner's instruction. Controller delivery checks cover
scope, evidence identity and preservation, followed by the task-scoped local
commit. The worker did not commit or dispatch another agent.

The immutable worker handoff is retained as `report04.md` in the current evidence
root and in `Saved/ReinforcedColumn02/Controller/BeforeClosure/Docs/`. Its manifest
still identifies those exact worker bytes; only this report's delivery status
was updated for the owner's subsequent review waiver.
