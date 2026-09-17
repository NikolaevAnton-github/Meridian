# Datum16BodyIntake01 — MSQ-54 technical intake

2026-09-17. **Usable repair base**, with useful whole-body proportions and garment
volumes. It is not a deformation-ready protagonist or an accepted design. Both
hands have five visibly separated digit shapes, but their joint flow, skinning
and rifle contact remain unverified. Retopology and fitting are required before
a rigged prototype. The full MSQ-54 deliverable remains incomplete.

## Source and execution

Untouched source:
`Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16UndersuitInput01/OwnerExports/tactical+jumpsuit+3d+model.fbx`.
Size **933,904 bytes**; SHA-256
`fc6340b6f36c529f15dac48ef06dca37aa72a07134b873e9e564f0addc6fa196`.

Actual local import succeeded in **Blender 5.2.1 LTS**, build `9e2066aef7ef`, using
an isolated background process, factory startup and disabled auto-execution.
No existing GUI, Unreal, Painter or DCC bridge was operated. The source was
imported with custom normals and animation enabled, image search disabled,
global scale 1 and bake-space-transform disabled. No source geometry or object
transform was edited, normalized, welded, repaired, remeshed, exported or saved
as a blend. Temporary diagnostic cameras and edge curves existed only in memory.

Raw FBX is **7400**, creator **Tripo**, with a header timestamp of
2026-09-17 17:49:32 (timezone unspecified). Its three object records are Geometry,
Material and Model, named `tripo_79ffcaee_2d55_4e30_8aed_9f2eba1d8ebc`. That embedded
identifier is not a verified provider job record. The metadata tree retains
scalar values and array type/count/head; full arrays remain in the exact FBX.
No actual settings/job sidecar was supplied. **P2.0, Quad target 20000, single
image and Private remain recommended settings, not established generation facts.**
Provider mode, credits, input actually submitted and output rights were not
independently verified; this intake made no provider or browser calls.

## Measured contents

| Check | Result |
| --- | --- |
| Imported objects / meshes | 1 / 1; no parent, modifiers, vertex groups or animation data |
| Vertices / edges / polygons | **22,109 / 47,118 / 24,974** |
| Triangles / quads / ngons | **5,991 / 18,983 / 0**; 76.01% of polygons are quads |
| Triangulated faces | **43,957** |
| Connected vertex-edge islands | **12**, inside one mesh object |
| Armatures / actions / shape keys | **0 / 0 / 0** |
| UV layers / imported images | **0 / 0** |
| Materials | 1, on all polygons; neutral 0.8 diffuse, Principled/output/Normal Map nodes, no image texture |
| Boundary edges | **456** in 69 connected boundary groups; 44 groups are simple closed cycles |
| Non-manifold edges | **556**, comprising 456 boundaries and **100 edges with more than two faces** |
| Non-manifold vertices / loose wire edges | **128 / 0** |
| Inconsistent two-face winding edges | **4** |
| Exact/near duplicate vertices; duplicate index/position faces | **0** in each test |
| Degenerate edges / faces / loop triangles; repeated-vertex faces | **0** in each test, at local epsilon 9.9951e-8 |
| Custom normals | Present; all 24,974 faces smooth; **675 corner normals opposed to their polygon normal across 424 faces** |

Normal lengths are approximately 0.99999973–1.00000023, so the conflict is
directional, not zero-length normals. Opposed corner normals are diagnostic
flags; smoothing, folded/nonplanar polygons and authored normals can contribute.
They do not establish 424 independently flipped surfaces. Exact duplicate tests
do not rule out arbitrary surface overlap or self-intersection. Inward ray
chords from the unchanged shoulder helper are retained as raw numerical data;
they are not interpreted as garment thickness or a self-intersection test.

Islands correspond spatially to torso/sleeves, trousers, hood, two gloves, two
boots and five small collar/cuff/ankle/waist regions. This is a bounds-based
interpretation, not semantic segmentation. The two main glove islands have
2,294/2,293 vertices and 2,454/2,463 polygons, with zero boundary edges. Separate
garment islands are not inherently defects and do not prove failed cloth seams.
There is no demonstrated continuous inner anatomical body or usable cloth wall
thickness beneath this surface.

Coarse location bins put **97/100 multi-face edges at the boots/ankles** and
three at the head/collar; all four winding inconsistencies are at the boots.
Boundary edges occur at boots/ankles (246), torso/sleeves (130), head/collar
(36) and trousers/hips (44). Opposed-normal faces occur at boots/ankles (295),
head/collar (60), torso/sleeves (50), hands/cuffs (15) and trousers/hips (4).
These bins identify repair priorities; each opening still needs an intentional
garment-edge versus accidental-hole decision.

## Scale, axes and pose

Raw FBX declares UpAxis **+Y**, FrontAxis **+Z**, CoordAxis **+X** and
UnitScaleFactor / OriginalUnitScaleFactor **100** (centimeters per source unit).
Blender imports a **+90-degree X rotation**, location zero and scale (1,1,1),
with determinant +1. Recorded post-import scene units are METRIC / scale_length 1.
Local bounds are X ±0.499755859, Y 0–0.944824219, Z ±0.096923858.
World bounds are **0.999511719 × 0.193847768 × 0.944824215** Blender units
(X width × Y depth × Z height), with soles effectively at Z=0. Interpreting
the declared meters gives approximately **99.9512 × 19.3848 × 94.4824 cm**.
This generated scale is not an approved stature; it is roughly a one-unit-wide
source and must be fitted in a separate production step.

The inspected model faces **world -Y**, with +Z up, arms extended horizontally
and palms down in T-pose. In this orientation X-positive is character-left and
X-negative is character-right; evidence filenames retain explicit axis labels.
Arm-span/height is about **1.058**. Broad bilateral silhouette symmetry is
present; cloth folds, topology and glove details differ. X=0 mirrored nearest
vertex residuals have median **0.0023921**, P95 **0.0056099**, maximum **0.0206815**
world units. These sample-dependent distances do not prove anatomical asymmetry.

Keep this source T-pose distinct from **MSQ52-RigContract01's A-pose** and exact
**161-bone** hierarchy/local transforms. The contract's 180.5439 cm diagnostic
mesh height is not approved protagonist stature. Preserve the **170 cm camera**,
**34/88 cm capsule** and existing rig transforms; resolve source orientation,
dimensions and pose on a derived original-model working copy in future work.

## Inspected visual evidence

Evidence root: `Saved/PlayerCharacter01/Datum16BodyIntake01/Worker/`.
All **48 gray/wire renders** were inspected through the four labeled contact
sheets; individual front and hand wire renders were also inspected at full
resolution. The original `Inputs/01-StartHere-FrontTpose.png` was inspected.
Wire overlays trace original polygon edges, not triangulated or repaired edges;
they show visible surfaces, not x-ray coverage. `views.json` records cameras.

| Evidence | Technical finding |
| --- | --- |
| `sheet1.png`: front/back/both sides/two obliques | Complete clothed T-pose, opaque hood, boots and gloves; broad front silhouette follows the input. Hood is a simplified face-shaped volume with no exposed eyes/skin. Sleeve, thigh and shin panels appear flatter and more rigid than the input's soft woven cloth. Side depth is plausible as reference, not measured against approved body dimensions. |
| `sheet2.png`: both hands, above/below/oblique, gray and wire | Each hand visibly has a thumb plus four separated finger forms. Palm and dorsal gaps rule out an obvious mitten or distal finger fusion in these views. Finger roots/web spaces are shallow and simplified; blunt fingertips, uneven thumb form and irregular poles/triangles around knuckles need refinement. Neither five usable articulated fingers nor grip/reload clearance is established. |
| `sheet3.png`: shoulders/armpits/elbows/wrists | Torso and shoulder volume is continuous within its main island, but armpit flow and compressed fold regions need bend-aware review. Long sleeve/forearm quads and triangle clusters follow surface panels, with uneven joint density. Cuff overlaps and separate gloves need seam/clearance handling during wrist twist. Elbow crops include surrounding sleeve and wrist context, not identified rig-joint locations. |
| `sheet4.png`: hips/crotch/knees/ankles | Crotch clearance exists in the static stance; triangulated/pole regions cross the groin and thigh panels. Knee loops largely follow sculpted folds and do not establish crouch behavior. Boot laces/tongues/collars are dense, fused-looking surface details; the proven multi-face/winding issues cluster here. Separate boot/trouser boundaries need inspection during ankle flex. |
| Back and oblique-back views | Broad back, seat, rear folds and collar closure are provider-inferred from unseen surfaces. They are smoother than the front and are not validated design details. The front-only input cannot approve their construction or thickness. |

This is technical source interpretation, not independent concept review or owner
design acceptance. The soft hood remains an inferred under-helmet layer; it does
not replace the owner-selected Datum16 helmet. Static evidence cannot establish
deformation, skinning, weapon grip, trigger isolation, reload contact or rig
compatibility. No fitting, rigging, animation or Unreal round trip was attempted.

## Next repair/fitting priorities

1. Establish an explicit proportional master and dimensions against the selected
   design and fixed camera/capsule/rig contract. Preserve this exact source and
   reconcile its -Y-facing T-pose with the contract before binding a derived mesh.
2. Resolve the boot/ankle multi-face edges and winding, inspect collar defects,
   and classify all garment boundaries. Rebuild overlap/fused details where
   needed; do not globally weld intended cuffs, boots or garment separations.
3. Refine glove anatomy and web spaces, rebuild deliberate finger/thumb/wrist
   flow, then validate every finger and rifle contact. Existing separated digit
   shapes are useful starting geometry, not a motion pass.
4. Rework shoulder/armpit, elbow, crotch/hip, knee and ankle loops. Validate twist,
   arm elevation, crouch and joint compression on the exact contract; investigate
   normal conflicts after topology is stable. Add UVs and final detail later.

## Reproduction and preservation

Script: `Scripts/PlayerCharacter01/body_intake01.py`, importing numerical helpers
from the unchanged registered `shoulder_intake01.py`. Run with
`D:/blender/blender.exe --background --factory-startup --disable-autoexec --python Scripts/PlayerCharacter01/body_intake01.py`.
Optional `-- --inspect-only` skips rendering. The initial baseline is immutable
across subsequent executions: the script fails if protected source hashes change.

**187 protected files** (all character source/art files, rig-contract sources,
the shoulder helper and current `Config/DefaultEngine.ini`) were SHA-256 checked
before/after. They match; the imported mesh geometry digest also matches after
diagnostic rendering. Pre-existing owner modifications to AGENTS.md and
DefaultEngine.ini were left in place. A concurrent addition,
`Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16BodyIntake01/provenance.json`,
appeared between the initial Git check and numerical intake and was not written
or edited by this worker. It was already included in the first 187-file hash
baseline and remains unchanged. Final verification does not rebaseline sources.
No registry mutation, provider call,
delegation, task/status mutation, commit or push was performed.

`inspect01.log` retains the first successful numerical run, including a benign
Blender material API deprecation warning that PowerShell surfaced as exit 1.
The Blender script completed and verified preservation. `render01.*` records
the completed render process, exit 0; `localize01.*` records the added spatial
defect localization, exit 0. No failed diagnostic log was deleted. A default
`python` alias was unavailable; existing Blender Python handled final checks.
The first storage scan followed Windows junctions into shared external plugin
caches; its exact Python child was stopped and the attempt recorded. The final
scan excludes reparse points and measures project-local files, not repeated
external cache links.

`evidence-manifest.json` is finalized after Blender processes exit and logs stop
changing; it hashes evidence files plus this report and the script, excluding
only itself. The evidence footprint is approximately **68.7 MB**, below 150 MB;
exact listed bytes are in the manifest and project-local storage is in
`storage.json` (17.1065 GB, excluding reparse-point targets). Controller review,
source provenance registration and the task-scoped closure commit remain with
the controller. This bounded intake does not complete MSQ-54.

## Controller technical handoff

The controller inspected the input image, full front/back/side/oblique model
views, both hands in palm/dorsal/oblique views, and joint gray/wire evidence.
The usable repair-base verdict is supported. No repeat provider generation is
needed to establish the next repair step. This accepts the bounded inspection,
not production geometry, motion behavior or the owner's visual design.

A separate read-only numerical check confirmed the source identity, FBX metadata,
counts, island sums, topology flags, normals and all 70 frozen manifest entries.
The controller corrected one report label: the measured post-import scene unit
system is METRIC, not NONE. No source, script or frozen diagnostic file changed.
The original worker report is retained at
`Saved/PlayerCharacter01/Datum16BodyIntake01/Controller/worker-report-original.md`,
SHA-256 `24039ef2337f600e4cef4fa92587cbd04d453989176b27dfb0b035940e206a53`.
The frozen evidence manifest's report entry identifies that snapshot; this
correction and controller handoff do not rebaseline the worker evidence.

The source inventory preserves the intended StartHere-to-FBX relationship as
unverified because no actual provider job/input record was supplied. The original
FBX is retained through Git LFS. The completed intake leaves body fitting,
topology repair, exact-contract binding and motion probes outstanding.
