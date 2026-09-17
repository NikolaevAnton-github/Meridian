# Datum16MeshUsability01 — existing-topology assessment

2026-09-17, MSQ-54. **Retain the existing mesh as the working base; blanket
retopology is not justified by this assessment.** The original Revision02 surface
was fitted, bound and animated, including an actual Blender-to-Unreal round trip
and four TP reloads on its own 161-bone rig. Local garment defects, hand/contact
fit and several joint deformations remain. This completes a bounded assessment,
not the full protagonist prototype or owner visual acceptance.

Final diagnostic identity: `Datum16_Bind05`; exact files are frozen in
`Assets/Source/PlayerCharacter01/MeshUsability01/manifest.json`. The editable
source is `Datum16_Bind05.blend`, the controlled export is `Datum16_Bind05.fbx`,
and `Datum16_Bind05_DeformationFinal.blend` contains 19 keyed probes. The imported
mesh is `/Game/Development/PlayerCharacter01/MeshUsability01/Datum16_Bind05`.
All failed/intermediate candidates remain beside it.

## Inputs and static comparison

The tested owner source is
`Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16UndersuitInput01/OwnerExports/Revision02/tactical+jumpsuit+3d+model.fbx`,
1,186,096 bytes, SHA-256
`aade1a13585f8639610e42a12cc350619ff4279e33325968f416bb4e8b8e8467`.
Revision01 remains 933,904 bytes, SHA-256
`fc6340b6f36c529f15dac48ef06dca37aa72a07134b873e9e564f0addc6fa196`.
The original drop now contains Revision02 by owner action; old intake/registry
fingerprints remain historical evidence and were not rebaselined.

Actual imports used Blender **5.2.1 LTS**, build `9e2066aef7ef`, factory startup,
background mode and disabled auto-execution. Existing intake numerical and
render helpers were reused with revision-specific output paths. Both revisions
have 48 matched gray/original-polygon-wire views, including both hands and sides.

| Measured source property | Revision01 | Revision02 |
| --- | ---: | ---: |
| Vertices | 22,109 | 28,332 |
| Polygons | 24,974 | 32,376 |
| Quads / triangles / ngons | 18,983 / 5,991 / 0 | 24,264 / 8,112 / 0 |
| Triangulated faces | 43,957 | 56,640 |
| Connected islands | 12 | 9 |
| Boundary edges | 456 | 614 |
| Edges with more than two faces | 100 | 267 |
| Inconsistent two-face winding edges | 4 | 17 |
| Faces with opposed custom corner normals | 424 | 423 |
| UV layers / armatures / original weights | 0 / 0 / 0 | 0 / 0 / 0 |

Revision02 retains the coverall, hood, gloves and boots, with clearer forearm
panels, thumb/joint segmentation and boot straps. Its extra polygons do not
automatically improve deformation. The numerical structural flags increased,
especially around glove details. These are localized defects, not evidence that
every quad must be replaced. Boundary edges include intentional garment
openings; no global weld or hole-filling operation was performed.

Revision02 multi-face edges occur in hands/cuffs **151**, boots/ankles **101**,
head/collar **11**, and torso/sleeves **4**. Winding flags are respectively
**6, 10, 0, 1**. Trousers/hips have no multi-face or winding flags and four boundary
edges in the coarse region bin. There are **five zero-area source faces and six
degenerate triangulated faces**, three zero-area faces near the center-front
collar/zipper and one at each hand. Their indices/locations are in
`source-degenerate-locations.json`; keep them in the bounded local repair list.
No exact/near duplicate vertices, duplicate faces or zero-length edges were
found. The 614 boundary edges form 64 groups, 37 simple closed cycles; these
counts do not classify intent. Full lists remain in `Revision02/geometry.json`. Inward-ray
chords from the reused helper are not treated as garment thickness or a complete
self-intersection test.

## Fit, bind and measured round trip

The live editor was confirmed through official Epic MCP as MeridianSquad,
UE **5.8.1 / CL 56057345**, initially on the retained lobby with no dirty packages.
The full donor was absent from the selected project subset but present in the
original weapon pack. Its `SKM_Manny.uasset` was copied byte-for-byte into the
isolated experiment's `Donor/` directory and exported through Unreal. The
89-bone Simple meshes were not used to define the hierarchy.

The original source layer is preserved in each working blend. Temporary stature
is **180.5439 cm**, using a source-to-centimeter factor of **192.0799523**; this is
a diagnostic fit, not owner-approved production stature. Leg stance was narrowed
up to 28%, blended out above the hips; sleeve height was adjusted by 1.6 cm with
a smooth transition. Regional hand correspondence later adjusted palm/digit
positions around the unchanged rig. The fixed 170 cm camera and 34/88 cm capsule,
accepted skeleton, source animations and existing configuration were not edited.

The donor was temporarily posed toward the source T-pose, weights transferred
from four nearest evaluated donor vertices, normalized and limited to eight
influences, and the garment fitted back into the contract A-pose. The initial
nearest-donor distance was 1.84 cm median, 6.80 cm P95 and 10.23 cm maximum;
this is correspondence distance, not a fit-acceptance threshold. Final hand
weights use source-defined digit regions and adjacent joints, with the proximal
palm on its own hand bone. There was no geometry replacement.

| Verification on Bind05 | Result |
| --- | --- |
| Original topology identity | All **28,332 vertices**, **60,797 edges**, and **32,376 polygon index lists** preserved in order |
| Native import | **29,084** dynamic-mesh vertices after import splitting; **56,640 triangles**, matching source triangulation |
| Surface identity across import | Bidirectional nearest-vertex maximum **0.000149 cm**, P95 **0.000089 cm** |
| Hierarchy | **161 bones**, zero missing/extra bones and zero parent mismatches |
| Bind position error | Maximum local **0.000339 cm**, component **0.000118 cm** |
| Bind quaternion comparison | Maximum angular difference **0.139 degrees**, within proposed quaternion absolute-dot threshold **0.999999** |
| Bone scale | No negative scale; maximum numerical deviation from contract **0.00001193**; not bitwise equality |
| Native skin weights | Zero invalid vertices, maximum eight influences; normalized within approximately **5e-8** |
| Material/dependency scope | Default diagnostic material; no imported textures, physics asset or completed material work. Candidate meshes/skeletons have no missing hard `/Game` dependencies |

`surface-verification-Bind05.json` measures bidirectional nearest-vertex agreement
between Blender A-pose surface and actual native imported geometry, rather than
relying on export success. Native extra vertices are import splits, not new
authored topology. The small derivative-only contract-matrix adjustment is
recorded; the accepted rig asset and contract file remain unchanged. The copied
reference donor still lists unavailable `ABP_Manny_PostProcess`; that dependency
does not belong to the tested candidate and was not silently repaired.

## Actual deformation and regional verdicts

`DeformationBind05Final/` contains **19 keyed, evaluated** probes: rest, both-arm
raise, left/right cross-body reach, left/right elbow bend plus forearm twist,
wrist flex, deep crouch, ankle flex and ten individual digits. `Detail05/` contains
**76** matched gray/wire closeups of the actual deformed surface and original
polygon edges. These temporary display copies use recalculated smooth normals;
the full deformation views retain the working mesh's custom-normal behavior.
Neither display path changes the saved source topology. Hand crops hide unrelated
body geometry beyond 25 cm of the wrist for visibility.

Independent source-defined distal regions contain **2,620 vertices** across all
ten digits. Bind05 records **zero movement in other labeled distal digits** for
each individual probe. This establishes isolated assignment for those regions;
it does not cover every web/palm vertex or prove anatomically correct thumb
opposition. The worst-case edge-strain counts identify remaining deformation
work: deep crouch stretches **252** edges above 2x and compresses **409** below
half length; left/right cross-body reach stretches **64/58** edges above 2x.
These strain counts include short pre-existing detail edges and cannot by
themselves establish topology as the cause.

| Region | Verdict | Evidence, cause and minimum next work |
| --- | --- | --- |
| Hood bulk / central torso panels | **Retain topology with fit/weight corrections** | Silhouette and panels survive fitting and native poses. No widespread topology failure demonstrated. Keep the original surface; resolve head/neck fit and final dimensions before detailing. |
| Collar / neck seam | **Local topology repair plus fit/weights** | Eleven multi-face edges in the source head/collar bin; native reload views expose neck/collar separation. Classify overlapping garment rims, repair only accidental internal connections, then refit and blend neck weights. An open neckline is not itself a defect. |
| Shoulders / armpits, both sides | **Unresolved joint quality; retain bulk topology provisionally** | Raise works as a skin-response test, but cross-body poses compress the shoulder and produce folded/inverted-looking patches. Four structural flags exist in the broad torso/sleeve bin. Isolate those local defects, improve shoulder/upper-arm weight transitions and rest fit, then judge whether a few local joint loops need repair. Current failure is not sufficient evidence for whole-sleeve retopology. |
| Elbows / forearms, both sides | **Retain topology with fit/weight corrections** | Actual elbow bend and 80-degree forearm twist execute. Existing folds and panel edges compress, especially toward cuffs; gross arm continuity is retained. Improve twist distribution and cuff transition before changing topology. |
| Wrists / cuffs | **Local topology repair plus fit/weights** | Source glove/cuff defects and uneven cuff transitions remain visible; wrist flex produces excessive pinching. Preserve intentional separate sleeves/gloves, remove only fused/internal detail connections, and feather the hand/forearm transition. |
| Four fingers on each hand | **Retain most topology; local detail repair and continued fit/weights** | Individual digit assignment is proven on the actual surface after correcting transfer errors. Knuckle creases and irregular joint detail remain visible. Repair localized multi-face/folded detail and refine joint weights; no evidence requires replacing all finger surfaces. Rifle-surface contact is not passed. |
| Thumbs / web spaces | **Unresolved deformation quality; localized repair expected** | Each thumb moves independently, but its control flex produces poor web compression and an unnatural hinge. The simple source-space fit and analytical weights remain contributors. Refit the thumb base/opposition and paint the web before assigning the failure to topology; repair only confirmed local non-manifold detail. |
| Hips / crotch / thighs | **Retain topology with fit/weight corrections** | No multi-face/winding flags in this source bin. Crouch executes but compresses the groin and thigh folds. Adjust hip fit and weights; no blanket trousers retopology is justified. |
| Knees, both sides | **Unresolved** | The 140-degree deep-crouch probe produces severe knee-fold compression and pointed silhouette artifacts. Static topology alone does not establish the cause. Rebalance knee/corrective influences and fold placement, then repeat the bounded bend before deciding on local loops. |
| Ankles / boots | **Local topology repair plus fit/weights** | 101 multi-face edges and ten winding flags in source boot/ankle bins. Flex retains the boot design, but sole/lace/cuff irregularities and compressed overlaps remain. Repair localized sole/lace/tongue connections and normals; keep the rest of each boot. |

These verdicts distinguish existing topology from the quality of this provisional
bind. They do not claim a watertight garment, production anatomy, continuous
self-intersection clearance, final corrective rig, or approved silhouette.

## Native rifle/reload and close FP diagnostic

The existing MSQ-52 playback helper was adapted to **assert Bind05 and retain it**
instead of resetting the component to a mannequin. The rifle attaches to this
candidate's own `ik_hand_gun` at identity; there is **no hidden donor carrier**.
Native `AnimPreviewInstance` uses the source additive bases, rate 1, synchronized
absolute rifle sequences, main/reserve magazine paths and original visibility
intervals. No source animation, socket or compatible-skeleton list was edited.

All four ordinary/empty, aimed/unaimed TP cases reach **3.666667 s**, with
**13 telemetry samples each** and **zero character/rifle timestamp difference**.
Exact final values and 2–3 native screenshots per case are in
`Compatibility05/Playback/` and `reload-summary-Bind05.json`. Source wrist-space
comparison tests the attachment/rig interface; it cannot approve glove-surface
contact. The visible palms/fingers do not fully conform to the rifle and magazine,
and cuffs compress. **Playback/timing passes; contact quality remains failed or
unverified where the sparse views cannot resolve it.** No dropped-magazine physics,
gameplay IK, full-rate contact solve or FP reload implementation was added.

Maximum right-wrist difference from the accepted source recording in rifle-root
space is **0.00873 cm ordinary**, **0.00235 cm ordinary aimed**, **0.01007 cm empty**,
and **0.00231 cm empty aimed**. The nearest reference sample differs by at most
0.03555 s; this sampling uncertainty is recorded rather than hidden.

`Compatibility05/FP-Diagnostic-Camera170-TPControlPose.png` inspects the actual
new sleeve/glove surface from the fixed 170 cm camera with a TP control pose.
The rifle sits low in the view and cuff/surface issues remain. This is a bounded
close presentation check, not an authored FP animation, ADS alignment or MSQ-55
camera-fit acceptance.

## Preserved failures and corrected interpretation

- The first Unreal startup used `-ExecutePythonScript`, which exited automatically
  after registration. Subsequent sessions used `-ExecCmds` and live Epic MCP.
- The initially named full-donor project path was absent. The original weapon-pack
  file supplied the unchanged isolated donor instead; no substitute rig was used.
- A repeated numerical intake hit its preservation guard after new task outputs
  appeared. Rendering then reused the saved measurements and untouched revision
  input without replacing the initial intake baseline.
- Bind01's nearest transfer leaked heavily across fingers. Bind02 narrowed hand
  assignments but mislabeled part of the index fingertip as thumb, causing spikes.
  Bind03 tested a bounded inverse alternative. Measured determinants disproved
  the initial singular-matrix hypothesis; Bind04 fixed the thumb-region extent.
- Weight-group-only isolation appeared clean in Bind04, but independent
  source-space labels caught **1.824 cm** of index-edge movement during middle
  flex. Bind05 uses the measured source digit boundaries. This was a weight/fit
  error, not a demonstrated finger-topology failure.
- An aimed clip lookup used `_Aim`; the actual selected source suffix is `_Aimed`.
  The corrected four source cases were subsequently collected to completion.

All attempts remain identifiable. No failed candidate was rebaselined as a pass.

## Preservation and controller handoff

The initial preservation set contains **650 files**, including both owner source
revisions/drop, character art/source history, all pre-existing Content and Config,
the accepted rig and project descriptor. Verification found **650 unchanged**.
The owner-edited `DefaultEditor.ini` and `DefaultEngine.ini` were preserved.
The editor returned to the retained lobby and shut down; only the transient
engine basic-shape material was dirty and was discarded without saving. No DCC
process or run-owned playback is left active.

Native execution arguments verified **Astra / high / standard**, using the
existing subscription. No new generation, service purchase or separately billed
API was used. Workloads ran serially. Storage and process high-water observations
are retained in Worker; the project remains well below **250 GB**. These process
samples are measured observations, not an assertion of complete system-wide peak
VRAM telemetry.

The final detailed Blender render process reached a measured **1.531 GB** working
set high-water mark; the largest recorded Unreal process high-water mark was
**4.877 GB**. Process observations are retained in `editor-memory-*.json`;
measurements use decimal GB. The final sample had
approximately **10.89 GB** system RAM free. The Blender process exit-code property
was unavailable through the sampled PowerShell handle; its complete log records
all 76 renders and normal `Blender quit`, and the process is no longer running.
The final pre-manifest project measurement was **18,658,198,768 bytes** versus
**17,828,514,865 bytes** initially, an **829,683,903-byte** increase. This includes
Git, generated evidence and project service files while excluding reparse-point
directory targets; final small metadata files are additional bytes. No asset was
deleted to reclaim space.

The worker did not edit approval/task/state/index/pipeline records, owner exports,
registry or profiles, and made no issue comments/status changes, commits or pushes.
A controller-side `.gitattributes` update appeared during the run and was retained;
the report, Python helpers and PowerShell sheet helper now resolve to `-text`.
The final manifest step checks all binary LFS and exact-byte policies. The
controller must review/register these diagnostic
identities, restore saved profiles, update current task records and make the
task-scoped local closure commit. The full MSQ-54 remains `in_progress` and
incomplete; no successor was dispatched.
