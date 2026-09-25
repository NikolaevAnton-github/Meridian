# ReinforcedColumn01 — MSQ-154 Candidate01

2026-09-25. MSQ-155 independent technical and visual-evidence review: **PASS**.
Controller scope/evidence acceptance passed for Candidate01 / Build09.
Owner play/design acceptance remains pending. Local closure identity is recorded
in `Saved/ReinforcedColumn01/Controller/acceptance.json`.

## Delivered column

The retained lobby's `StaticMeshActor_35`, label
`FB01_newNcolumnNN12p6NN2p4`, remains at `(-1260, -240, 900)` cm with its original
rotation, scale and material override. Its outer dimensions remain
`240 × 240 × 1800` cm. The lower `0–280` cm around all four faces and corners is
the affected region. The upper architecture remains continuous and fixed.

The actor now uses `SM_RC01_SupportedColumn`. One added vendor
`BP_BreakableObject`, labeled `RC01_ReinforcedColumn`, sits at
`(-1260, -240, 0)` and uses `DA_RC01_Column`. All derived assets are under
`/Game/ReinforcedColumn01/`; no vendor asset was changed.

The intact surface retains the original slab layout, textures, world-space
origin and extent. A derived copy of `M_Slabs01` and `MI_Slabs_035` provides the
Geometry Collection material usage without modifying the owner's materials.

## Construction and behavior

- 288 irregular Voronoi fragments: 22 shallow stone chips and 266 bonded
  stone/concrete fragments. Stone thickness is 1.8 cm. Deep fracture centres are
  18–29 cm below the original surface, with matching irregular concrete faces.
  The source generator preserves exact shared boundaries and original volume.
- A permanent rough concrete core fills the complementary volume and continues
  to the top. This is collision geometry matching the retained surface, using
  complex collision for the static mesh, rather than the old full-column box.
  The static core has collinear tessellation junctions at face/band boundaries;
  the source check records them. `core-seams01.json` separately splits those
  108 unmatched mesh edges at existing collinear endpoints: all 100 resulting
  segments have two opposite incidences, with no open boundary or orientation
  failure at 0.0005 cm tolerance. This establishes geometric closure beyond the
  volume check; it does not claim welded topology. Each dynamic fragment is
  closed, and combined visible solid volume matches within 0.012 cm³.
- Every fragment has a small bond anchor embedded in the permanent core.
  The collection contains 288 dynamic bodies, 288 fixed anchors and one root.
  Anchors use Chaos's persistent `Anchored` attribute as well as kinematic
  initial state. Untouched fragments remain supported after neighbouring loss.
  Per-fragment convex collision is explicitly generated; sleeping debris uses
  a 3–5 second removal delay and 1–2 second removal duration.
- The vendor large pillar's separate attached reinforcement pattern is retained.
  Its original cage is approximately 85 × 83 × 475 cm, too small for this 240 cm
  column. The authored cage has 28 ribbed Ø28 mm longitudinal bars at about
  317 mm spacing, Ø12 mm rounded perimeter ties at 200 mm spacing, and internal
  cross-links. Nominal cover to the outer tie is 48 mm behind the stone. Bars
  extend 400 mm below the base and 612 mm above the affected band, remaining
  embedded at both ends. Vendor concrete and steel materials are reused.
- `DA_RC01_Column` derives from `DA_Pillar_Large_Concrete_Square`. It retains the
  vendor concrete effects, sounds and damage thresholds; the impact radius is
  0.22 m for these approximately 30 cm fragments. Rifle hits and F6 use the
  existing `NGDPropComponent` and vendor impact field. No retired ED system,
  new damage framework or collapse behavior was introduced.

Native changes are limited to an editor mesh/collection importer
(`NGDColumnAuthoring`), its three editor-only build dependencies, and one exact
data-asset allowlist entry in `NGDTools::Spawn` so placement and F6 can reconstruct
the derived vendor actor. The importer converts source winding to Unreal's
clockwise faces and preserves imported material slot names.

## Verification

Final build: **Build09**. Final asset authoring: `asset-build07.json`.
Runtime evidence uses **Build08**. Build09 only extends the read-only managed
collection inspector requested by the controller. `inspector-only-diff.json`
verifies unchanged importer construction, mesh helpers, tested map/assets,
editable geometry and runtime adapter, so the passing gameplay evidence applies.
Evidence root: `Saved/ReinforcedColumn01/Candidate01/`.
`verification02.json` passes the bounded evidence checks:

- One actual rifle shot detached one fragment. One sustained local 18-shot
  burst did not detach neighbours or move the anchors/core. Three adjacent
  single shots then exposed both shallow cladding loss and deeper concrete loss.
  Four of 288 dynamic bodies moved in total: indices 49, 50, 51 and 59.
- All 288 fixed anchors and the continuous core remained in place. Four cavity
  traces reached steel or actual retained concrete 6.776–18.383 cm behind the
  former outer face; there is no full-envelope blocker at the removed surface.
- F6 restored the collection, materials, original bounds and reset generation 1.
  The next actual rifle shot detached one fragment again.
- Every recorded gameplay sample has global and player time dilation 1. No
  slowdown test or broad gameplay/performance matrix was run. Editor background
  CPU throttling was temporarily disabled to permit normal frame updates and
  was restored to its original true value; no preference file was saved.
- Cold reopening and a subsequent official Epic MCP level reload pass. The
  saved map contains one changed existing actor and one added actor; all 142
  unrelated actors and 486 protected source/vendor files remain unchanged.
  The editor has no dirty packages after reload.
- Native arguments and actual turn metadata confirm Astra/max; configuration
  and native arguments confirm default tier with fast mode disabled. The turn
  metadata itself omits a service-tier field. Project footprint measured
  107.004 GB against the 250 GB limit.

Review images: `review-intact.png` and `review-damaged-layers.png` are paired
normal gameplay views. `review-detail.png` shows the exposed steel, stone edge
and rough concrete at closer range. `review-reset.png` shows restoration.
`review-editor-intact.png` uses the original preservation camera.

Exact candidate paths and SHA-256 fingerprints are in `candidate-fingerprints02.json`.
The earlier manifest remains immutable; `BeforeInspection/` retains the earlier
native source/binary and initial handoff around the inspector-only change.
Editable source: `Assets/Source/ReinforcedColumn01/column.json` and `design.json`.
Generation and evidence scripts: `Scripts/ReinforcedColumn01/`.

## Authoring observations and review limits

The controller's checkpoint is addressed by actual managed data in
`managed-collection-comparison.json`, including every transform's parent, level,
state, geometry index and anchor flag:

| Managed data | Large vendor pillar | Candidate01 |
| --- | --- | --- |
| Hierarchy | 1 root, 355 level-1 nodes, 730 level-2 leaves | 1 root, 576 level-1 leaves |
| Initial state | 1,024 default; 62 kinematic (9 clusters, 53 leaves) | 288 dynamic; 289 kinematic (288 bonds plus root) |
| Persistent `Anchored` attribute | Absent | Present on all 288 bond anchors |

The candidate adapts the vendor's separation of fixed support and releasable
material to a flat set of per-fragment bonds inside the independently retained
core. It does not copy the vendor's geometry hierarchy literally. Explicit
persistent anchors prevent a subsequent local burst from releasing support;
the final trace proves this transition. This hierarchy difference is visible
for primary review. No further threshold changes were used to conceal it.

Earlier build/image/trace files are preserved diagnostics, not acceptance
evidence. In particular, older filenames containing `accepted` do not grant
technical, visual or owner acceptance. Use the `review-*` files and final build
identities above.

Two editor automation crashes were recorded: changing a live collection's
transform count invalidated its render proxy (`Editor05.log`), and a direct
Rider Python map load immediately after stopping PIE hit an engine tick-list
assertion (`Editor08.log`). The authoring script now rebuilds in an unsaved
empty world; cold reopen and official Epic MCP reload were verified afterward.
Use Epic MCP for level reloads and do not rebuild a collection's topology while
its old scene components remain registered. No runtime firing/F6 crash occurred
in the final smoke sequence.

The owner still decides the visual quality, fragment scale and shooting feel.
The independent primary reviewer should inspect the changed importer/allowlist,
source geometry and anchoring, preservation report, and actual final images.
This handoff does not reopen other columns, original lobby design work, collapse,
MSQ-150/151, or broader gameplay testing. Controller owns review closure and the
local task-scoped commit; exclude unrelated owner/controller document edits.
`Docs/Tasks/EnvironmentDestruction01.md` and `EnvironmentDestruction01Plan.md`
were changed by the controller during this run and are outside this delivery.

## Controller closure

MSQ-155 reviewed the exact 56-file final manifest, confirmed the Build08 runtime
evidence remains applicable to the inspector-only Build09 change, and found no
blocking defects. Its separate technical and visual-evidence verdicts are PASS;
see `Saved/ReinforcedColumn01/Review01/report.md` and `review.json`.
The unwelded but closed geometric junctions and retained dark lighting remain
documented informational observations. No relighting or further gameplay matrix
is part of this delivery. Owner principal play/design testing remains separate.

Controller closure changes only status/navigation documentation after review;
the reviewed code, assets and evidence are unchanged. Exact pre-closure task and
handoff bytes are preserved in `Saved/ReinforcedColumn01/Controller/BeforeClosure/`.
The immutable candidate manifests remain unchanged. The local MSQ-154 commit
excludes unrelated owner configuration, project and legacy-document edits.
