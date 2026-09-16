# LobbyPainter-Floor01: current-map cleanup and native Painter floor pair

On 2026-09-15 the owner approved the current corrected stone, authorized removal
of previous lobby levels while retaining only the current level, and requested
the next materials. See ../Approvals/LobbyPainterStone01-Acceptance01.json.
This supersedes historical instructions to keep old lobby maps in Content and
create another candidate map. Use the surviving current map in place:
`/Game/Maps/L_OpeningLobby_PainterStone01`. Retain its architecture and owner edits.
The new material candidate is `LobbyPainter-Floor01/WorkerCandidate01`.

Execute through Multica Environment Artist, Astra/high/standard, subscription
authentication, concurrency one. The former max trial has ended. The direct
controller stays through production, fresh independent review and one bounded
correction/recheck if needed. No other material rollout or atmosphere work.

## Authority and current baseline

Read AGENTS.md, Docs/Design/GameBrief.md, Docs/PainterWorkflow.md and the scoped
stone approval. Inspect both actual OwnerReferences01 PNGs before authoring.
Use Docs/OpeningLobbyPainterStone01Review.md for stone identity and limitations;
the historical pending owner wording is superseded by the external approval.
Do not resume the rejected MaterialIntegration01 task or use its textures.

The controller verified the approved correction manifest before dispatch:
`Saved/OpeningLobby/PainterStone01/Worker/Correction01/manifest.json`, SHA-256
`69aadd32025c61a93210c4caf4b02fb1bf10c88882b5006300f52aeece66eec1`.
Current map SHA-256 is
`1694ce8033c6d3a109b720a37f4d608325d2adbe285b5610dd12937e311d169f`;
stone .spp SHA-256 is
`6cc3e43b29eb8fb96c753a1790835a806ecc9f716d2308fa6cf61a7e9cb18324`.
Recheck live project, map, PIE, dirty state and bytes before every editing phase.
Preserve later owner changes rather than restoring historical bytes. Never discard
dirty packages or save unrelated work. One writer owns the entire DCC operation.

## A. Remove obsolete lobby maps

Before floor edits, save a bounded exact rollback copy of the current clean map
outside Content under `Saved/OpeningLobby/PainterFloor01/Worker/Before/`.
Inventory the nine obsolete maps under `Content/Maps/`: L_OpeningLobby,
L_OpeningLobby_Layout02, L_OpeningLobby_Layout03, L_OpeningLobby_Architecture01,
L_OpeningLobby_Architecture01_GlassReview01,
L_OpeningLobby_Architecture01_LightStudy01,
L_OpeningLobby_ArchitectureReworkA01, L_OpeningLobby_FunctionalBuild01 and
L_OpeningLobby_MaterialIntegration01. No other maps are in the deletion scope.

Inspect package referencers/dependencies, map streaming/external actor state and
config references. Keep every mesh, material, texture, gameplay asset, source,
reference and evidence file needed by the current map. This is map cleanup, not
an unused-asset purge. Archive the exact obsolete map bytes once outside Content
under `Saved/OpeningLobby/PainterFloor01/Worker/RetiredMaps/`, with relative original
path, archive path, bytes and SHA-256 mapping. This preserves prior reviewed
identities without keeping obsolete levels in the project browser. Do not
rebaseline historical manifests. Preserve old sources/reviews and record their
new map-archive resolution explicitly. No recursive directory deletion.

Prefer official Epic MCP/editor asset operations to delete the enumerated unloaded
packages after the dependency audit. Do not force-delete a package referenced by
the surviving map or unrelated content. Resolve authorized startup/default/cook
map references to the retained map, preserving unrelated settings. Update exactly
GameDefaultMap and EditorStartupMap in Config/DefaultEngine.ini; audit additional
active configuration paths. Historical docs/scripts are evidence and need not be
rewritten. Verify only one lobby .umap remains and no runtime reference dangles.

## B. Author the floor and strip materials in Painter

Author two genuinely new native editable Painter materials: a polished green-grey
floor with larger irregular branching pale veins, and near-black floor strips with
subtle fine mineral structure. Use the actual owner reference pair. Keep mineral
scale and polished reflections credible at standing height and across the long
floor. Avoid generic clouds/noise, signature loops, tiled islands, swollen normals,
wet/plastic response and texture-created panel grids. Do not recolor/rescale the
approved column stone into the floor. No rejected pixels or old opaque dependencies.

Apply only three component slot overrides, rechecking live identities: Floor /
StaticMeshActor_0, FloorStrip_-1 / StaticMeshActor_11 and FloorStrip_1 /
StaticMeshActor_22, each StaticMeshComponent0 slot 0. Keep the accepted stone's
four bindings and all native stone/source/texture bytes unchanged. Do not change
mesh defaults, geometry, transforms, dimensions, lights/exposure, glazing,
collision, owner checkpoint X -2090 cm, gameplay, doors or the blank logo field.

Write new .spp projects, layer/resource recipes and canonical channel exports
under `Assets/Source/OpeningLobby/PainterFloor01/`; use separate editable stacks
for floor and strips. New UE materials/textures belong only under
`/Game/OpeningLobby/PainterFloor01/`. New evidence and intermediate exports belong
under `Saved/OpeningLobby/PainterFloor01/Worker/`, exports in `Worker/Exports/`.
Reuse the existing authoring mesh if technically appropriate, preserving it.
Only create a small new authoring mesh/native source when necessary.

The profile has task-local advanced Painter tools and path roots. Verify live
Painter version, schemas, resource URLs and parameter metadata. Follow the
verified FillLayer authoring route and limitations in Docs/PainterWorkflow.md.
Native layers/resources and .spp are required; no ceremonial Painter wrapper,
unchanged stock smart material, external noise generation, bridge/config edits,
installs, downloads or paid services. At most two purposeful author QA revisions.
Save/reopen each .spp and reproduce its BaseColor, DirectX Normal and packed ORM
exports; record exact channel meanings, dimensions, physical projection scales,
sources and readbacks. Capture provenance even if Painter GUI preview is limited.

## Verification and handoff

Reuse existing snapshot/property/capture/channel/manifest logic through small
guarded `Scripts/OpeningLobby/painterfloor01_*.py` adapters. Historical helpers
hardcode source map/hash and evidence paths: do not run their mutating operations
unchanged after cleanup. No replacement validator or benchmark framework.

Record before/after complete scene properties; allow only the three listed
material overrides. Compare approved stone bytes and bindings exactly. Verify
native graph compilation, imported channel settings and absence of old opaque
dependencies. Save/reopen the current Unreal map and verify persisted assignments.
Use genuine matched 1920x1080 HFOV90 standing-height views of the entrance-to-hall,
inner-to-entrance, floor near/oblique, strip boundary and long repeated floor.
Capture actual live camera/tick readiness; reject queued origin frames. Include
one focused real standing PIE possession check, restore temporary settings and
leave the clean current map loaded, PIE off. No redundant full route rerun.

Deliver Docs/OpeningLobbyPainterFloor01.md and a nonempty unique
path/bytes/SHA-256 `Worker/manifest.json` with `Worker/identity.json`, binding
candidate, current map, two .spp files, exact baseline/retired-map archive records,
new native/source files, helpers and genuine evidence. Distinguish owner-approved
stone from new unaccepted floor bytes. Preserve original correction manifest and
all old review findings; map hash changes are expected for the new three bindings.
Aim for <=250 MB growth, retaining correction headroom under the 2 GB cumulative
lobby and 250 GB project caps. Measure actual disk usage. No asset deletion to
meet a target. Full logs stay in Saved. Return concise English handoff.

No delegation, comments/task administration, registry writes/rebaseline, commits,
pushes or later dispatch by the worker. Project/global MCP settings stay unchanged;
only the specified active map config references are authorized config edits.

## Fresh independent review

Controller dispatches a fresh Multica Visual Reviewer at Astra/high/standard.
Reviewer inspects actual references and before/final images, records first-look.md
before author conclusions, then audits exact identity/evidence. Write only
`Saved/OpeningLobby/PainterFloor01/Review01/`; no DCC or candidate mutation.

Judge separately: (1) cleanup scope, dependency safety and single current map;
(2) current owner architecture/stone preservation; (3) genuine new native Painter
authorship and reproducible channels; (4) floor mineral structure/scale/polish;
(5) strip distinction, continuity and response; (6) repetition and whole-hall
readability under fixed light; (7) saved/reopened native integration and mapping;
(8) genuine comparable captures, standing possession, restoration and honest scope.
Use PASS/FAIL/UNVERIFIED with image/data citations, required_corrections,
critical_unverified_requirements and owner_review_ready. Critical unknowns block
readiness. A scoped pass permits owner floor review; metal/ceiling, broad stone
rollout, final architectural detail, glazing B3, atmosphere and MSQ-7 stay pending.
