# Datum16MetaHumanTrial01 — MSQ-54 experiment handoff

2026-09-17. **The live MetaHuman body conformation succeeded and produced a usable
experimental A-pose skin. It does not replace the original visible coverall or
the accepted 161-bone rig.** Construction details disappear, boots become
anatomical feet, and direct source animation leaves the right wrist 3.70–4.99 cm
from its measured source grip. Retain the result as a shape/skinning reference;
continue the original garment on MSQ52-RigContract01. This is a worker technical
finding, not independent visual review or owner acceptance. Full MSQ-54 remains
incomplete.

Canonical source: `Assets/Source/PlayerCharacter01/MetaHumanTrial01/`.
Experimental packages: `/Game/Development/PlayerCharacter01/MetaHumanTrial01/`.
Full evidence: `Saved/PlayerCharacter01/MetaHumanTrial01/Worker/` (called **Worker**
below). Open `Worker/index.html` locally for paired views, all ten digits and
native reload frames. The adjacent JSON files contain measurements and settings.

## Actual execution and preserved inputs

UE **5.8.1 / CL 56057345**, Blender **5.2.1 LTS**, and the installed Creator APIs
were used. Official Epic MCP confirmed the MeridianSquad project and live editor
state before mutations. The existing MCP transport and MSQ-52 preview, additive
evaluation, attachment, visibility and telemetry helpers were reused. No competing
dispatcher or animation harness was created.

Only `MetaHumanCharacter` was added to `MeridianSquad.uproject`, enabled for Editor
targets. Existing prerequisites loaded successfully. There was no interactive
account/license gate in the completed operations. No purchase, new provider
generation, separately billed API request or successor task was initiated.

Untouched source:
`Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16UndersuitInput01/OwnerExports/tactical+jumpsuit+3d+model.fbx`.
SHA-256: `fc6340b6f36c529f15dac48ef06dca37aa72a07134b873e9e564f0addc6fa196`.
Rig contract SHA-256:
`ba557918290e6e3be0ce1836afac19ff005e4b45fedd203beca43a2a2837e749`.

The editable derivative retains the original mesh in a separate hidden layer.
A uniform factor **1.9108729121** changes the imported full-source height from
94.4824 cm to the **temporary 180.5439 cm** MSQ-52 diagnostic mesh height. This
does not approve stature. Blender is +Z up, facing −Y; X positive is wearer-left.
The FBX uses forward −Y / up Z, applied units and scale 1. The 170 cm camera,
34/88 cm capsule and 90° FOV are unchanged.

The featureless hood island (1,535 vertices) was excluded from the solve copy,
leaving **20,574 vertices / 40,897 triangles**. Body-only input is 161.0433 cm
high. Other disconnected pieces, folds and source topology defects were retained;
none prevented Auto Solve. The original file and full scaled layer remain intact.

## Solve and export results

The successful operation used `BODY_ONLY`, pipeline `body_only`, Auto Solve,
no manual keypoints, and no joint-estimation override. A 1024×1024 camera input,
an open Creator asset editor and execution deferred outside the MCP HTTP callback
were used on Solve02. It returned **true in 41.079 s**. Character initialization
took **7.875 s**. These are operation timings, not a total production estimate.

Source-pose DNA was exported before `commit_posed_state_as_a_pose`. The subsequent
A-pose commit and separate body DNA/geometry export produced the fitted surface.
The distinction follows Epic's [From Custom Mesh workflow](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-from-custom-mesh-tool-in-unreal-engine):
source-pose DNA is an intermediate; the committed character and assembled outputs
are separate stages. This trial exported the committed body. A final full
character assembly, facial rig and original head/helmet integration were not
performed.

| Check | Actual result and limit |
| --- | --- |
| Live Creator conformation | **Pass.** Solve02 saved fitted body state in `MH_Datum16_Trial01`. |
| Source-pose preservation | **Pass.** `Solve02/SourcePose/Datum16_Solve02_Posed.dna` precedes A-pose commitment. |
| A-pose export / DCC import | **Pass.** `Solve02/APose/MH_Datum16_Trial01_Body.dna` and `.fbx`; imported fitted skin retained in `Datum16_APose02_Inspection.blend`. |
| Geometry | **Pass for experimental inspection.** Native GeometryScript LOD0: 30,455 vertices. Imported FBX: 32,334 vertices / 60,816 faces. These are different mesh representations. |
| UV presence | **Pass.** `DiffuseUV`: 32,334 distinct coordinates, 60,816 nonzero-area faces; U 1.0096–1.9904, V 0.0063–0.9927, tile **1002**. No original garment unwrap/texture transfer or overlap acceptance is implied. |
| Skin data | **Pass.** All native LOD0 vertices have valid weights; sums 0.999999952–1.000000045; 285 weighted bones, maximum **12 influences**. |
| Rig identity | **Fails exact production contract.** 342 Unreal bones; 150 common names with matching parents, 192 extra bones and 11 missing contract bones. FBX represents root as the armature object and exposes 341 bones. |
| Original garment fidelity | **Fail as the visible production coverall.** See comparison findings below. |
| Final production round trip | **Unverified.** No Blender-to-161-bone production reimport, final assembly, physics/cloth acceptance or FP camera fitting. |

The A-pose body references installed MetaHuman skeleton, post-process, gray
material and physics assets under `/MetaHumanCharacter/`. Nine experimental
packages loaded in the working editor; their direct hard `/Game` references are
present (`Worker/final-packages.json`). No new generated project package outside
the trial root was needed. This was not a fresh-process cold-load test.

The unregistered-component socket transforms in `apose-native-inspection.json`
are identity and **must not be used as bind-pose evidence**. Hierarchy and native
weight reads are valid. Bind distances below use the inspected FBX coordinates;
registered native components supplied the actual reload telemetry.

## Surface and finger inspection

Neutral gray front/back/side/oblique and joint views are in
`Worker/ComparePosedDNA02_Aligned/`; source and fit use matching cameras. The
posed-DNA mesh needed a **mesh-only +90° X diagnostic correction** after a faulty
scripted import. These images support surface comparison, not source-pose rig
acceptance. The default head is an unapproved scaffold. The separate A-pose FBX
is correctly oriented and is the deformation input.

| Region | Observation |
| --- | --- |
| Torso / legs | Broad volume and some large folds survive. Fine folds and panel transitions become soft, uneven surface bulges. |
| Collar / waist / pockets | Raised collar, zipper, belt loops, seams and pocket edges are lost. The exported body terminates at the standard head/body partition across the upper torso; it is not a complete original collar surface. |
| Wrists / cuffs | Glove and sleeve volumes join smoothly; hard cuff edges, straps and separation disappear. |
| Crotch / hips | Broad shape remains, but fabric construction and fold hierarchy are flattened. Crouch adds strong hip/knee compression. |
| Ankles / boots | Laces, cuff, sole and boot edges disappear. Separate anatomical toes remain. This alone prevents treating the fit as the visible boot. |
| Hands | All five digits on each hand remain separate, with no observed thumb/finger swap. Glove detail is smoothed; skin creases and faceted regions require cleanup. |

Left/right thumb, index, middle, ring and pinky were each flexed independently on
the exported A-pose skin and reviewed with palm/dorsal/oblique views. Use
`Worker/Deformation03/Hands04/` for fixed-camera isolated hand views. Each named
digit produces the largest displacement in its corresponding weighted region;
no mapping correction was justified. Manual landmarks were therefore not added.
Thumb flex also affects adjacent web/palm-weighted vertices by up to **15.4 mm**;
that is a weight/corrective quality concern, not evidence of a digit swap.

## Deformation and weapon compatibility

Static frames 1–16 are retained in
`Solve02/Datum16_APose03_Deformation.blend`. These evaluate the actual FBX skin
with Blender linear skinning, without Unreal corrective post-processing, IK,
cloth or physics. Exact bone adjustments and moved-vertex measurements are in
`Worker/Deformation03/probes.json`.

| Probe | Result |
| --- | --- |
| Arm raise | **Executed; skin-response pass, production quality unverified.** Both shoulders raised 115° from the imported A-pose. 17,191 vertices move; armpit compression and lost cuff/shoulder detail remain. |
| Cross-body reach | **Executed; skin-response pass.** New surface follows the shoulder/elbow chain; shoulder and inner-arm compression need corrective review. |
| Elbow / forearm twist | **Executed; skin-response pass.** Bent forearm plus 80° axial twist; wrinkles compress and the forearm volume needs review. |
| Isolated trigger finger | **Correspondence / independent flex pass.** Right index flex moves the intended digit; maximum adjacent middle-weighted movement is 2.8 mm. Actual trigger contact remains unverified. |
| Deep crouch | **Executed; deformation quality not accepted.** Thigh −105°, knee +140°, ankle −35°, pelvis adjusted to reference foot height. New skin bends, with pronounced hip/knee compression; no balance/collision or gameplay crouch claim. |
| Ankle flex | **Executed; skin-response pass, boot design fail.** +25°/−20° ankle rotations work, but the surface is a foot rather than the original boot. |
| Rifle grip | **Fails direct integration.** Candidate lacks `ik_hand_gun`; diagnostic right-wrist offset from the source grip is 3.70–4.99 cm. |
| Four reload cases | **Native playback/timing pass on the new surface; contact/integration fail.** Details below. |

The four **TP** cases use `AnimPreviewInstance` and the unchanged authored local
additive bases, rate 1, with absolute rifle animation and source magazine visibility
intervals. A **hidden original 161-bone carrier** supplies the missing rifle
attachment. The visible measured character is the new fitted body. This is a
diagnostic workaround, not a repaired MetaHuman integration.

| Case | End / samples | Maximum character–rifle time difference | Right-wrist offset from accepted source recording |
| --- | --- | --- | --- |
| Ordinary | 3.666667 s / 13 | 0 s | 4.17–4.49 cm |
| Ordinary aimed | 3.666667 s / 13 | 0 s | 3.70–4.10 cm |
| Empty | 3.666667 s / 13 | 0 s | 4.24–4.99 cm |
| Empty aimed | 3.666667 s / 13 | 0 s | 3.71–4.32 cm |

Offsets compare the candidate wrist in rifle-root space with the nearest sample
of the retained MSQ-52 recording; maximum reference phase mismatch is 0.0383 s.
`Worker/Compatibility/Playback/Contact04-TP-*` contains 13 telemetry samples and
2–3 screenshots per case. These sparse captures do not verify continuous finger,
handguard or magazine-surface contact. Magazine paths/visibility were evaluated
through the existing helper; no dropped-magazine physics was added. FP reloads,
ADS/camera fit and production hand IK remain unverified.

## Retained failed attempts

- **Solve01 crashed** in `SharedPointer.h:1133` with a MetaHumanCharacterEditor
  stack and an invalid image-size warning. `Worker/Crash01/`, `Unreal02.log` and
  `solve01-start.json` retain evidence. Solve02 changed editor initialization,
  camera/image parameters and callback scheduling together; the exact causal
  contribution of each change is not isolated.
- The first geometry export, `Solve02/SourcePose/MH_Datum16_Trial01_Body.fbx`,
  still contained the template A-pose. It is rejected as fitted geometry and
  retained with `Datum16_Solve02_Inspection.blend` / `Worker/Compare02/`.
- The scripted source-pose DNA import used the default native `DNAConfigHolder`
  because the saved DNA configuration is protected from Python access. Geometry
  was Y-up while bones were Z-up. The raw result and the separate display-corrected
  copy remain preserved. Native menu selection was exposed, but activation could
  not be verified with the available UI transport. No native-menu generation
  success is claimed, regardless of diagnostic screenshot filenames.
- **Deformation02 renders are rejected**: render-time animation reevaluation
  reset the posed surface. Deformation03 keys each pose before rendering. Early
  full-body hand crops were occluded, and middle-finger-driven cameras moved;
  fixed rest-camera `Hands04` views resolve that evidence issue without new poses.

## Recommended production route

Keep **MSQ52-RigContract01**. Retain the original garment, glove, collar and boot
construction, resolve the required production references, then retopologize and
fit those surfaces to the exact 161-bone master. The MetaHuman A-pose may help
as a broad shape guide or reviewed weight-transfer starting point; its outer
cloth fit is not a clean anatomical underbody. Preserve garment detail separately
and prove the contract round trip, twists, trigger grip, four reloads and crouch
on the original surface. No successor was executed.

| Route | Remaining work / risk |
| --- | --- |
| Exact 161-bone contract (recommended) | Substantial garment topology, weighting, corrective and hand-contact work, but retains the already measured animations, attachment chains and gameplay interface. The trial does not remove this work. |
| MetaHuman integration | Retains fitted topology/UVs/weights, but still needs original garment reconstruction, 11 missing contract bones/interfaces, retargeting, MetaHuman corrective/physics validation, head/helmet and full assembly, plus all camera/contact tests. Higher integration surface without solving garment fidelity. |

Measured FBX bind distances explain why shared bone names do not prove fit:
shoulder separation **33.45 cm** versus contract **38.02 cm**, left upper arm
**31.60** versus **27.77 cm**, forearm **28.25** versus **27.25 cm**, and
wrist-to-middle-distal **17.01** versus **15.95 cm**. Missing bones are
`center_of_mass`, `interaction`, `weapon_l/r`, `ik_hand_root/gun/l/r` and
`ik_foot_root/l/r`. No existing skeleton or compatible-skeleton list was edited.

## Cost, preservation and controller handoff

The editor's measured peak working set was **14.984 GB**; the final sample used
5.263 GB with 8.654 GB system RAM free. GPU usage at that sample was **13,013 /
32,607 MiB**, a system-wide observation rather than an isolated editor peak.
Only one heavy workload ran at a time. Storage rose from **17.152 GB** to about
**17.6 GB**; `Worker/storage-final.json` contains the final exact count. The method
counts regular project files including Git and Saved, without traversing reparse
directories. No owner asset was deleted. The 250 GB limit remains satisfied.
The final measurement was **17,584,117,372 bytes**, a **432,171,652-byte** increase;
trial sources use 80.81 MB, trial Unreal packages 125.95 MB and Worker evidence
196.16 MB. Final small manifests are additional metadata after that measurement.

**619 pre-existing files were hashed:** 618 remain byte-identical; the only
change is the intended Creator plugin enablement in `MeridianSquad.uproject`.
The pre-existing `Config/DefaultEngine.ini` edit, original source, rig contract,
accepted art and lobby content are preserved. Controller-owned documentation
changes were not edited by this worker. No dirty map/content remained before
shutdown; the editor is closed as it was initially. `editor-shutdown.json` and
the completed Unreal log record cleanup.

`Assets/Source/PlayerCharacter01/MetaHumanTrial01/manifest.json` freezes the
Worker01 sources, experimental packages, report and scripts. Binary files are
covered by Git LFS, including the added local `*.dna` rule. Full failures and
diagnostics remain under Worker; use `evidence-manifest.json` to identify that
evidence set. The source README identifies the usable and rejected variants.
Task-specific root attributes preserve the report/script bytes through Git
line-ending conversion; the project descriptor hash records this handoff state.

No issue status/comment, profile, registry acceptance, commit or push was made.
The controller owns review, task/state updates, profile restoration and the
verified closure commit. This handoff closes only the bounded experiment.
