# MSQ-54: Datum16ShoulderIntake01

2026-09-17. Bounded source intake completed and controller-verified.
**The returned FBX is usable as a shape reference and a repair/retopology starting
point. It is not a production-ready shoulder component.** A concave underside,
outer skin and substantial rim are present, but the mesh is open around small
details, its two apparent panels are connected, and final thickness, scale,
attachment construction and body clearance remain unresolved. MSQ-54's original
body and deformation prototype remains incomplete. No design acceptance is granted.

## Source and execution

Untouched source:
`Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16ShoulderManual01/OwnerExports/armor+shoulder+plate+3d+model.fbx`

- Size: **134,960 bytes**.
- SHA-256: `c1be7d5f1e82b955c9367f5335e45f1e191177bf298ba0112eb9604575d65078`.
- Binary FBX version **7400**; creator string **Tripo**. Header creation timestamp
  is `2026-09-17 17:04:47.000`, with no recorded timezone. A separate `CreationTime`
  field says `1970-01-01 10:00:00:000`; do not treat either as a verified job time.
- Raw FBX objects contain one Geometry, one Model of type Mesh, and one Material,
  all named `f47ec958_6f27_451d_88d5_3b8f4f73c214`. No raw armature, animation,
  texture or video objects were found.
- The creator string does not establish P2.0, requested Quad 3000, privacy,
  generation input, task ID, subscription allowance, output rights or credit cost.
  No owner-returned job record or export sidecar accompanies the FBX. The directory
  also contains the pre-existing preparation `README.md`.

Installed **Blender 5.2.1 LTS**, build `9e2066aef7ef`, successfully imported the
actual file with `bpy.ops.import_scene.fbx`. Each diagnostic process used
`--background --factory-startup --disable-autoexec --python-exit-code 1`; runtime
reported background mode true and automatic script execution false. No Blender,
Unreal Editor or Substance Painter application process was found at preflight;
existing bridge processes were left untouched. The two short Blender runs were
sequential and exited. No GUI session was controlled.

Reproduce from the project root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& D:/blender/blender.exe --background --factory-startup --disable-autoexec --python-exit-code 1 --python Scripts/PlayerCharacter01/shoulder_intake01.py
```

Evidence root: `Saved/PlayerCharacter01/Datum16ShoulderIntake01/Worker/`.
`geometry.json` is the final numerical inspection; `fbx-metadata.json` records the
raw FBX hierarchy with array lengths and first values, not a duplicate source.
`geometry-initial.json` retains the earlier polygon-center ray diagnostic and
factory-material inventory; those two portions are superseded by the final
triangle-center diagnostic and import-only inventory. Both runs used the same
source identity and produced the same geometry counts.

## Measured geometry

| Check | Result |
| --- | --- |
| Imported mesh objects | 1, no parent; 9 vertex/edge-connected islands |
| Vertices / edges / polygons | **2,836 / 6,013 / 3,176** |
| Triangles / quads / ngons | **801 / 2,375 / 0**; approximately 74.8% quads by polygon count |
| Blender triangulated count | **5,551** |
| Main shell island | 2,478 vertices, 2,834 polygons, **18 boundary edges** |
| Eight small islands | 358 vertices, 342 polygons total, **105 boundary edges** |
| Boundary / wire edges | **123 / 0** |
| More than two incident faces | **0 edges** |
| Non-manifold edges including boundaries | **123**, all have one incident face |
| Boundary groups | **17 closed edge cycles**, lengths 3 to 9; these are small openings, not the broad underside cavity |
| Local inconsistent winding | **0** two-face edges failing BMesh's contiguous-winding check |
| Exact coincident vertex excess | **0** |
| Near-coincident vertex pairs | **0** within `9.9951171875e-8` local units |
| Duplicate faces | **0** by sorted vertex IDs and by exact sorted vertex positions, regardless of winding |
| Degenerate edges / polygons / triangulated faces | **0 / 0 / 0** at the stated length epsilon and its square as area epsilon |
| Repeated-vertex polygons | **0** |
| UV layers | **0** |
| Imported material / texture images | **1 / 0**; all polygons use material slot 0 |
| Armatures / actions / shape keys / vertex groups / modifiers | **0 / 0 / 0 / 0 / 0** |

Island vertex/polygon/boundary-edge counts, ordered by lowest source vertex index:
`2478/2834/18`, `49/56/8`, `49/44/16`, `50/56/9`, `9/8/8`,
`53/52/16`, `52/46/16`, `48/40/16`, `48/40/16`.
The small islands occupy fastener-sized regions; eight islands do not prove eight
complete independent screws. Several are open rings or small patches.

All 3,176 faces are smooth shaded and custom corner normals are present. Normal
lengths are approximately 0.99999984 to 1.00000019. **Ten corner normals across
eight faces oppose their polygon's geometric normal**; minimum dot product is
**-0.741712**. Affected zero-based polygon IDs: `388, 919, 1822, 2557, 2603, 2870,
2875, 2884`. This is a localized normal/shading defect; a consistent edge winding
check does not validate custom normals or prove outward orientation globally.

BMesh reports zero non-manifold vertices under its surface-fan definition, which
allows these boundary fans; this does not mean the object is closed. The formal
signed-volume sum is `0.0722033377` local units cubed and Euler characteristic is
`-1`. Because the source has open boundaries and multiple islands, neither value
is accepted as solid volume or proof of a valid solid.

## Dimensions and thickness limits

FBX declares Y up, front-axis index Z with positive sign, X coordinate axis, and
`UnitScaleFactor = OriginalUnitScaleFactor = 100` centimeters per FBX unit. Blender
imports a metric scene with scale length 1. The object has zero translation,
unit scale, approximately **+90 degrees X rotation**, and positive transform
determinant **1**. No transform was applied or normalized.

World bounds in imported Blender meters:

- X: `-0.368896455` to `+0.368896455`.
- Y: `-0.499755859` to `+0.499755889`.
- Z: approximately `0` to `0.645996094`.
- Extents: **0.737793 x 0.999512 x 0.645996 m**.

Local extents are `0.737793 x 0.645996 x 0.999512`. This approximately one-meter
longest dimension is export scale, not an approved wearable size. Do not import it
unchanged as a fitted shoulder or infer final millimeter thickness from it.

Final diagnostic rays start just inside each of the **5,551 triangulated face
centroids**, along the negative geometric triangle normal. **5,538** rays hit
another surface; **13** miss. One first hit belongs to the same polygon and is
explicitly flagged. The raw first-hit distances span **0.000022397 to 0.709221**
local units, with median **0.0667162**. **4,389** hits have normal dot product below
`-0.5`. These are chords through whatever surface lies along a normal, including
bevels and other parts; they are **not a wall-thickness distribution or minimum
thickness certification**. The near-zero and long outliers need local inspection
on a future repair copy. No self-intersection, collision or global minimum-wall
solver was run. Manifold topology alone would not establish those properties.

## Actual image inspection

All eight camera directions were inspected in gray and wireframe, alongside
original `Concept02/16.png` and the expected `Inputs/01-StartHere-Outer45.png`,
solely for source interpretation. No independent concept review was performed.

| Evidence image pair | Reading |
| --- | --- |
| `oblique_a_gray.png`, `oblique_a_wire.png` | Outside silhouette and the seam between the broad plate and upper return; fastener details and dense triangular fans are visible. |
| `minus_z_gray.png`, `minus_z_wire.png` | Inside: real recessed inner surfaces and raised perimeter, with no mounting straps, lining or designed attachment interface. |
| `plus_x_gray.png`, `plus_x_wire.png` | Side: open concavity beneath the arch, outer/inner skins and thick rounded edges. |
| `plus_z_*`, `minus_x_*`, `plus_y_*`, `minus_y_*`, `oblique_b_*` | Additional matched outside, opposite-side and end views. |

All images are 1000 x 1000 orthographic renders using the same center and camera
scale; exact transforms are in `views.json`. Gray studio lighting removes texture
distraction while retaining imported shading. Wire images trace original polygon
edges using disposable in-memory curves, with ordinary surface occlusion; they
are not x-ray images and do not add triangulation edges. No diagnostic curves or
camera were saved as an asset or model candidate.

The source is **not a flat card or fully solid plug**: the side and inside views
show a concave cap with separate inner surface and a finite rim. It retains a
readable cap/return silhouette and an outside seam from the input. The underside
has shallow recessed panels within a broader arch. However, the return and rim
look bulky and rounded; a thin, consistently shallow wearable shell at final
scale has not been demonstrated. Useful starting thickness exists geometrically,
but its production value depends on fitting and rebuilding local sections.

The apparent large and small plates are in **one connected shell island**;
the visible seam does not provide independently articulating pieces. Small detail
islands remain in the same Blender object without named part hierarchy. Screw
recesses and rims are softened or irregular, broad facets contain shading waviness,
and wire views show long narrow triangles converging on fasteners and the seam.
Those areas need deliberate topology if retained. Fastener-scale boundary cycles
and small main-shell holes prevent calling the whole mesh watertight. The expected
illustration's metal finish is absent, consistent with an untextured return;
hidden mounting construction was never established by that single image.

## Bounded repair recommendation and remaining gates

On a separately authorized derived copy, first fit the preserved reference to
the common body/undersuit master and record proposed dimensions. Then retopologize
the broad outer facets and seam while constructing a controlled inner offset and
rim. Resolve whether the visual seam is a groove in one rigid cap or an actual
part joint before separation. Rebuild the small fasteners/recesses and local open
patches deliberately; indiscriminate welding would not resolve these separated
surfaces. Correct winding and custom normals on the derived result, then check
self-intersections and minimum thickness at the selected scale. Add the inferred
attachment/lining only after its construction is resolved. UVs, bakes and finish
follow successful fitting and motion probes.

This is likely a **bounded cap retopology and hidden-surface rebuild**, rather
than a normal-only fix. No further provider generation is necessary to make that
technical decision. No repair, welding, normalization, export, production blend,
body master, rig or new component candidate was created in this intake.

Before production usability can pass under **MSQ52-RigContract01**, the controller
still needs the common original master and the exact 161-bone contract. Its A-pose,
38.0198 cm shoulder-joint separation, 55.0222 cm shoulder-to-wrist chain and source
transforms are fitting constraints, not approval of protagonist dimensions. Test
the wearer's right cap through arm elevation, forward/cross-body reach, shoulder
and upper-arm twist, aim, fire, and ordinary/empty reloads both aimed and unaimed.
Inspect cap-to-neck/chest/upper-arm/undersuit clearance, rigid attachment behavior,
and rifle/hand contacts in local and world representations. Preserve the existing
170 cm camera and 34/88 cm capsule; do not cure intersections by silently moving
them. Original-model Blender/Unreal round trip, skinning, FP visibility and later
gameplay tests remain outstanding. None were attempted here.

## Preservation and handoff

`preservation.json` verifies every pre-existing file in Datum16ShoulderManual01,
the authoritative `Concept02/16.png`, and `Config/DefaultEngine.ini` against
pre-import hashes. The imported vertex/edge/polygon digest also remains unchanged
after all rendering: `0581a6376922b7d92cffae9a5a14d139811e42fad8cf9dae5784c2914da8a28d`.
The source FBX remains byte-identical. Evidence occupies approximately **13 MB**,
below the **100 MB** worker limit; no owner assets were removed.

Only the authorized script, this report and the worker evidence directory were
written. Pre-existing changes in `AGENTS.md`, `Config/DefaultEngine.ini`, the
untracked task brief/export and `.multica/` were left to the controller. There were
no provider/browser calls, installs, registry writes, delegation, task/comment
mutations, commits or pushes. The bounded task brief explicitly forbids worker
comments and task mutations, so controller delivery uses this report and the final
worker handoff rather than a Multica comment. The controller owns review, source
inventory, live task updates and the task-scoped closure commit.

## Controller technical handoff

The controller inspected actual outside, inside, side and wireframe renders,
the numerical evidence and the script. A separate read-only technical check
cross-checked polygon counts against raw FBX arrays, material/UV inventory,
boundary classification, source preservation and all 24 evidence-manifest files.
The bounded intake passes; production geometry and owner visual acceptance remain
outstanding. No repeat generation is needed to establish the next repair step.

The original worker report is retained at
`Saved/PlayerCharacter01/Datum16ShoulderIntake01/Controller/worker-report-original.md`.
Its SHA-256 is `19c8c6ba7c7ae02bc7802d91dbeeb44e0f0fb87cd2f8434ced384345903cee27`;
the worker's frozen `final-verification.json` identifies that pre-controller
snapshot. This appended controller handoff does not rebaseline the worker evidence
or the earlier input-art package. The source inventory retains the intended
StartHere-to-FBX relationship as unverified because the actual Tripo job record
has not been supplied. The source FBX is retained through Git LFS.
