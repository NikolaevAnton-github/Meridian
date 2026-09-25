# ReinforcedColumn01: noncollapsing layered lobby column

2026-09-25. **MSQ-154**, parent MSQ-74. Multica owns live state.
Authority: [owner start](../Approvals/ReinforcedColumn01-OwnerStart01.json).

## Objective and scope

Convert one representative existing column in
`/Game/Maps/L_OpeningLobby_PainterStone01` into a playable Next Gen-based reinforced
column. Default bounded first pass: a substantial reachable lower region around
its perimeter, including corners, with unchanged remaining upper architecture.
Choose and record actual actor, dimensions, affected height/depth after live inspection.
The owner will evaluate the result. No collapse, severing, falling upper section,
ceiling damage or future collapse milestone is authorized.

Preserve the intact outer envelope, placement, existing stone/tile appearance and
all unrelated actors. The authorized internal/fracture authoring does not require
a new lobby concept: its named references are the existing column and large vendor
demo pillar. Recoverably snapshot current saved/unsaved state before editing.

## Behavior and authoring

- Inspect `DA_Pillar_Large_Concrete_Square`,
  `GC_ConcretePillar_Square_5m`, and the demo's `OptionalStaticMesh` reinforcement
  (`/Game/NextGenDestruction/Meshes/Props/SM_ConcretePillar_Square_5m_REBAR`).
  Follow its stable reinforced/noncollapsing behavior; reuse source geometry when
  it fits, otherwise author a plausible longitudinal-bar and transverse-tie cage.
  Record dimensions, concrete cover and why the adapted cage fits this column.
  Avoid arbitrary stretched rods, exposed steel before damage or floating ends.
- Tile/cladding starts bonded to concrete. Allow local tile chips/detachment,
  volumetric concrete loss and some concrete fragments retaining cladding.
  Do not require complete stripping before any concrete damage. Author irregular
  fracture and material interiors; do not substitute a smooth undamaged inner box
  for convincing exposed damaged concrete around the reinforcement.
- Keep a physically supported, indestructible core/anchors and stable reinforcement
  so sustained fire never collapses the column. Lost fragments must not retain a
  full original-column invisible collision proxy. Retained material remains solid.
- Use derived task assets, existing NGD `BP_BreakableObject`/data assets/impact field
  and `NGDPropComponent` rifle/reset route. Tune the vendor field radius to this
  geometry; the small demo pillar's nominal 40 cm radius is not a tile-scale recipe.
  Do not revive the retired custom ED framework or build a new generic system.
- Keep dynamic body count bounded; fine chips may use existing effects. Large
  remaining fragments and exposed reinforcement must read coherently. Reuse F6
  reset, preserving source geometry/materials and noncollapsing anchoring.

## Acceptance and verification

1. Exact existing column and affected dimensions are documented; normal intact
   view matches retained architecture and other lobby actors remain preserved.
2. Actual normal-speed rifle smoke test shows localized tile/concrete damage,
   visible plausible reinforcement, and surviving continuous supported column.
   Include one sustained local burst only as needed to prove no collapse.
3. No floating cladding or fragments, obvious layer gaps/intersections, uniform
   clean shell removal or invisible full-envelope blocker in removed material.
4. F6 restores intact geometry/materials and the next normal shot works.
5. Save/reload and relevant build/asset checks pass. Record paired intact/damaged
   normal gameplay views, source paths and current candidate hashes.
6. NO slowdown tests. No broad performance/AI/traversal matrix. Owner does principal
   play/design testing. Independent primary review checks changed implementation,
   preservation and actual visual evidence; controller checks evidence/finding closure.

## Allowed writes and delivery

Task assets: `Content/ReinforcedColumn01/`; editable sources:
`Assets/Source/ReinforcedColumn01/`; scripts: `Scripts/ReinforcedColumn01/`;
retained lobby map and narrowly necessary NGD adapter/editor authoring code.
Prefer asset-only changes; justify any native helper and limit its scope.
Never edit vendor originals, unrelated owner files, immutable historical manifests
or other tasks. Reuse existing editor tooling and source paths before adding tools.
One editor writer and one heavy operation at a time. Verify live project/bridge,
effective and actual native Astra/max/default settings, and capture preservation.

Evidence: `Saved/ReinforcedColumn01/Candidate01/`; handoff:
`Docs/ReinforcedColumn01.md`. Supporting vendor advisory:
`Saved/ReinforcedColumn01/Controller/vendor-research.md` when present.
Baseline references: `Docs/NextGenDestructionIntegration01NGD01.md` (impact/reset),
`Docs/LobbyPlaytestFix01.md` (current 14 specimens); read relevant sections only.
Executor ends in review with concise handoff/checkpoint, no commit; controller
owns independent review, task closure and local task-scoped commit.

## Candidate01 executor handoff — 2026-09-25

Implementation and bounded normal-speed checks are delivered in
[ReinforcedColumn01](../ReinforcedColumn01.md). One existing 240 × 240 × 1800 cm
column has a destructible 0–280 cm region, permanent rough core and authored cage.
Final identities: Build09 (read-only inspector extension), runtime Build08 /
asset-build07; exact hashes and checks are under
`Saved/ReinforcedColumn01/Candidate01/`. F6 and the following real-rifle shot pass.
MSQ-155 independent technical and visual-evidence review passed with no blocking
findings. Controller scope/evidence closure passed; local commit identity is in
`Saved/ReinforcedColumn01/Controller/acceptance.json`. Owner play/design acceptance
remains pending. No production successor was dispatched.
