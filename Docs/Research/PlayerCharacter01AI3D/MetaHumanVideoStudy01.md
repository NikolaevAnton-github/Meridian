# MetaHuman 5.8 custom-character video study

2026-09-17. Research under MSQ-54; no character conversion, project plugin change,
generation, animation solve or production-skeleton replacement was performed.

**Recommendation: evaluate From Custom Mesh on a preserved derivative of the
Datum16 source before committing to extensive manual body retopology.** The
workflow can supply standard MetaHuman topology, UVs and a fitted rig while
retaining an original appearance. It does not establish that our generated
coverall will convert cleanly, become separate clothing, or inherit the audited
rifle animations without adaptation.

## Evidence and scope

The requested video is Stefan3DAI's [Turn ANY Character into an Animated
Metahuman - Full AI Workflow](https://www.youtube.com/watch?v=4w7oA4oJMqs),
published 2026-07-05, duration 28:21. This report analyzes the complete timestamped
English transcript retained under
`Saved/PlayerCharacter01/MetaHumanVideoStudy01/Video/transcript.txt`, the separate
primary-documentation/installed-source audit in `Technical/findings.md`, and the
project's accepted intake and rig reports. The controller read the entire
transcript and inspected selected key frames in the actual video, including
custom-mesh input, refinement, posed DNA, bake targets, final assembly, FBX
settings, accessory setup and manual hand landmarks. This was a complete
transcript study plus targeted visual inspection, not uninterrupted audiovisual
playback. Frame observations are recorded below. Caption transcription contains
recognition errors; API/tool names below follow the primary documentation.

The central capabilities were introduced in **5.8**, rather than first appearing
in the 5.8.1 patch. **MetaHuman Creator / From Custom Mesh** performs character
conversion. **MetaHuman Animator Markerless Motion Capture** extracts animation
from recorded video. Installing the latter does not enable or replace Creator's
mesh workflow. [Epic 5.8 announcement](https://www.metahuman.com/news/metahuman-5-8-is-now-available)

## Timestamped workflow

| Video section | Operation and significance |
| --- | --- |
| [00:45–01:59](https://www.youtube.com/watch?v=4w7oA4oJMqs&t=45s) | UE 5.8, Creator Core Data and project plugins, Blender, a scale-reference body and AI-generated sources. Four different character proportions are used. Plugin installation and project enablement are separate prerequisites. |
| [02:00–04:27](https://www.youtube.com/watch?v=4w7oA4oJMqs&t=120s) | Prepare a clear neutral pose, with gaps between legs, arms/torso and individual fingers. A-pose is recommended, but the important input property is separability. Generate a detailed body and a separate detailed head; remove hair/accessories from the fitting surface. Assemble the reference in Blender. |
| [04:28–06:24](https://www.youtube.com/watch?v=4w7oA4oJMqs&t=268s) | Match scale against the reference, apply scale/rotation, export a static GLB, import it into Unreal and run Creator's From Custom Mesh / Combined Mesh / Auto Solve. The reported roughly two-minute solve on a 4070 Super is this author's observation, not our timing guarantee. |
| [06:25–08:20](https://www.youtube.com/watch?v=4w7oA4oJMqs&t=385s) | Save Pose as intermediate DNA before moving to the normalized character pose. Adjust the character, create the full rig and obtain texture sources. The saved source pose is needed for later projection onto the original geometry. |
| [08:21–10:27](https://www.youtube.com/watch?v=4w7oA4oJMqs&t=501s) | Generate a skeletal mesh from the saved DNA and export it as FBX. In Blender it matches the source pose while using MetaHuman topology/UVs. Separate head/body for the demonstrated bake and shift the body's UV tile by the exact required offset. |
| [10:49–13:32](https://www.youtube.com/watch?v=4w7oA4oJMqs&t=649s) | Bake source color and normals onto that mesh in Cycles using Selected to Active; diffuse bake uses color contribution only. Repair head/body transitions and assign resulting textures in Unreal. The demonstration concentrates on LOD0; it explicitly leaves broader LOD material replacement to the use case. |
| [13:49–18:25](https://www.youtube.com/watch?v=4w7oA4oJMqs&t=829s) | Export the final assembled head/body skeletal mesh, fit accessories in that final pose, optimize the actual accessory, bind it and transfer or assign weights. The rigid head accessory is fully weighted to the head bone. Export selected mesh/armature as FBX without added leaf bones, import and add it to the character. Additional moss geometry is derived from the weighted body. |
| [18:31–21:28](https://www.youtube.com/watch?v=4w7oA4oJMqs&t=1111s) | Install/enable Markerless, ingest video through Live Link Hub, create a MetaHuman Performance, choose the footage, enable body tracking, preview and process. Examples include generated and stock video, face/phone Live Link and a third-person character test. |
| [21:34–23:35](https://www.youtube.com/watch?v=4w7oA4oJMqs&t=1294s) | Acrobat example: automatic finger correspondence is wrong. Reset the body, place/add manual keypoints, solve again, then repeat the bake/accessory process. This is a concrete failure-and-correction example, especially relevant to our gloves. |
| [23:38–26:43](https://www.youtube.com/watch?v=4w7oA4oJMqs&t=1418s) | Alternative texture route: export the final MetaHuman mesh, isolate the needed face surface, prepare its UV/material layout, upload an unrigged copy to Tripo and preserve original UVs. Generate colors against the original reference, then reuse those maps in Unreal. This avoids the demonstrated high-to-low bake; it is a separate provider operation. |
| [26:44–28:21](https://www.youtube.com/watch?v=4w7oA4oJMqs&t=1604s) | A slender ballerina uses the same workflow; hair and dress remain separate accessories. The author's approximate hour-per-character claim is an edited tutorial estimate, not measured FPS production time or our budget. |

## Implementation details that change the result

**Two meshes and two poses must remain distinct.** The intermediate Save Pose
DNA describes the fitted source pose. Its generated mesh supports a spatially
matched bake, clothing wrapping or weight transfer. The final assembled
MetaHuman uses its normalized A-pose and is the rig reference for the tutorial's
accessories. Baking from the untouched T-pose onto an unrelated A-pose would
misproject surfaces. The intermediate DNA includes a body skeleton, weights and
RBF information but not the final facial rig; it is not the complete DCC export.
Unreal can turn it into a skeletal mesh for conventional FBX export to Blender.
Do not assume Blender natively supports the intermediate DNA: Epic identifies
Maya Pose Editor for external loading. [From Custom Mesh](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-from-custom-mesh-tool-in-unreal-engine),
[Export tool](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-export-tool-in-unreal-engine)

**The UV shift is an observed layout operation, not a universal preset.** The
tutorial separates the combined source-pose export into head/body bake targets
and moves the body UVs back into the target tile. Inspect the actual UV ranges,
materials and intended texture assignments before applying any offset. Keep
the correspondence to the final runtime meshes. Its simplified statements
about UDIM incompatibility should not become a claim that Unreal or Blender
cannot use UDIMs generally. In the AI-texture branch, preserving the original
UVs is essential; an automatic new unwrap would invalidate direct texture reuse.
Likewise, the shown 90-degree provider import rotation is specific to that
export/import convention, not a blanket rule for our source.

Blender has supported baking to UDIM tiles since 3.2. The tutorial's U=-1
translation prepares its separate body texture; it is not evidence of missing
UDIM support. [Blender Cycles 3.2 release notes](https://developer.blender.org/docs/release_notes/3.2/cycles/)

**Normal-map convention must be measured.** At 17:00 the author enables a green
channel flip for the demonstrated bake. Apply this only when the baked tangent
normal's Y convention differs from Unreal's expectation; do not flip a map
already exported for the engine. Verify with a known raised/recessed detail and
retain consistent mesh triangulation/tangent conventions. A color map and a
normal map alone are not a complete validated fabric/metal PBR material set.
[Marmoset tangent handedness](https://docs.marmoset.co/docs/tangent-handedness/)

**The reference template is optional.** The linked
[MetaHuman Conform Topology package](https://www.fab.com/listings/98f7b49d-f5dc-45c4-b590-52dbb4f951c0)
provides archetype head/body topology and UV guides, without joints, weights or
LODs. Its separate From Template purpose must not be confused with From Custom
Mesh. The author uses it as a size reference. Neither downloading this asset nor
purchasing the optionally shown Marmoset Toolbag is required for our first trial.

**Accessory parenting is not a complete general animation setup.** Weights,
matching hierarchy and bind pose must survive export. In Unreal, explicitly
inspect each added skeletal component's Leader Pose, Copy Pose or animation
class rather than assuming that dragging it under Body synchronizes its bones.
The generated MetaHuman Blueprint can perform setup off-camera. The installed
SDK explicitly follows Body for designated clothing parts, which does not prove
the same behavior for every arbitrarily named new component. Rigid equipment
may instead use an intentional bone/socket attachment. Cloth simulation and
extra accessory bones are separate decisions. [Epic modular character guidance](https://dev.epicgames.com/documentation/en-us/unreal-engine/working-with-modular-characters-in-unreal-engine)

**HD and Smart Mesh serve different purposes here.** At 02:48 the author
deliberately chooses a detailed HD source instead of a lighter mesh because
that source supplies bake detail; MetaHuman supplies the output topology. Our
earlier Quad 20,000 recommendation targeted an editable geometry foundation.
It was not tailored to this high-detail bake workflow. The returned body remains
useful for testing proportions and conformation; increasing its polygon count
through subdivision would not recover missing detail. Test the existing source
first. If fine detail later limits a validated result, obtain a suitable
high-detail derivative through the owner's existing web allowance, with retained
provenance. No new generation is required merely to evaluate this route.

## Applying it to Datum16

The preserved [body intake](../../PlayerCharacter01BodyIntake01.md)
reports 24,974 polygons, five separated digit shapes per hand, twelve connected
islands, 456 boundary edges and 100 edges incident to more than two faces.
Most of those multi-face defects are around the boots/ankles. The FBX has no
UVs, texture images, rig or animation. Its actual provider mode/settings remain
unknown; the recommendation of Quad 20,000 is not proof of the generation mode.

The imported source faces -Y, stands in T-pose and is approximately 94.48 cm
high under the file's declared unit interpretation. This is generated scale,
not an approved stature. Its hood, coverall folds, cuffs and boots describe an
outer garment surface. The solver follows that surface; it does not infer a
correct naked body beneath it or automatically extract a separate coverall.
Epic specifically identifies loose garments, folds, buckles and holes as risks
to fitting. The hood also lacks the facial landmarks used by the tutorial's
uncovered, bald heads. Body-only fitting is therefore worth testing before
forcing a complete facial solve that our concealed-face design does not need.
[Custom mesh requirements and limitations](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-from-custom-mesh-tool-in-unreal-engine)

There are two useful appearance outcomes to evaluate: a conformed visible
surface that retains the required coverall silhouette, or a fitted body/rig base
used to wrap and weight a separately retained garment. Neither is guaranteed;
compare actual folds, wrists, crotch and boot shapes before choosing. Separate
Datum armor remains separate fitted equipment. Conversion is no reason to
replace the selected silhouette, opaque visor or wearer-right helmet computer.

The [existing animation audit](../../PlayerAnimationAudit01.md) locks
an exact 161-bone hierarchy and bind transforms, finger/twist/weapon-IK chains,
and additive reload interfaces. A MetaHuman rig has not been shown to match
that contract. Two technical routes remain candidates: retain the audited
project skeleton and transfer the useful geometry/weights into its A-pose, or
explicitly adapt the animation integration to MetaHuman using reviewed retarget
copies. Compare those routes on representative motions before adopting a
different production rig. No skeleton reassignment or contract revision follows
automatically from this research. [Epic custom IK retargeting](https://dev.epicgames.com/documentation/metahuman/create-a-custom-ik-retargeter)

## Markerless capability and the installed project

The separate local audit confirms UE **5.8.1**, installed Creator binaries and
Core Data, and the owner's **MetaHuman Animator Markerless Motion Capture 1.0.0**
plugin with its DLLs and model payload. Live Link Hub and Capture Manager files
are present. This is installation evidence. The project does not explicitly
enable Creator or Markerless, and the inspected latest log does not prove they
loaded; no live conversion or capture has been tested.

Epic documents the experimental single-camera motion workflow as offline/local
Windows processing. For body-only capture: disable facial tracking, enable body
tracking and disable head movement mode. Export either to an existing MetaHuman
skeleton or to a performer skeleton for retargeting. Consequently, Markerless
can help fill our missing crouched leg motion, stepping turns or pivots even if
the project keeps its current production rig. Its useful role does not depend
on adopting a MetaHuman visible body. [Mono video capture](https://dev.epicgames.com/documentation/metahuman/metahuman-animation-from-mono-video-capture-in-unreal-engine),
[Processing and export](https://dev.epicgames.com/documentation/metahuman/metahuman-animator-02-process-and-export-your-animation-in-unreal-engine)

Creator is a different resource path: rigging and texture synthesis involve
Epic cloud services, so the whole combined workflow should not be described as
offline. Prior-session hardware evidence indicates RTX 5090/32 GB VRAM and
32 GB system RAM. A bounded run should measure memory with one heavy workload;
an installation check does not establish peak assembly cost. Existing sources
and project storage remain subject to the 250 GB cap.

## Proposed bounded evaluation before extensive retopology

1. Preserve the exact FBX and current rig contract; create one named derivative
   and record dimensions, axes and transforms. Establish temporary test scale
   against the fixed camera/capsule and measured rig, clearly separating it
   from any final owner-approved body height.
2. Correct only defects that disrupt the solve, including problematic boot and
   collar geometry. Keep intentional garment boundaries. Try body-only
   conformation first if the featureless hood prevents useful facial fitting.
   Retain the untouched source and both successful and failed diagnostic output.
3. Run Auto Solve; inspect both hands from multiple sides and explicitly check
   thumb/finger correspondence. Use manual keypoints only for identified errors,
   following the 21:58–22:57 example. Save source-pose DNA and the assembled
   A-pose outputs separately, then compare silhouette and joint volumes in gray.
4. Test a representative source-pose motion set before detail baking: arm raise and
   cross-body reach, elbow/forearm twist, closed rifle grip with isolated trigger
   finger, all four ordinary/empty aimed/unaimed reload cases with synchronized
   rifle/magazine motion, deep crouch and ankle flex. Preserve the 170 cm camera,
   34/88 cm capsule and 90-degree FOV. Source-rig playback is not a pass on a
   newly conformed surface or retargeted rig. These are bounded mesh/rig probes;
   full gameplay presentation still belongs to MSQ-55/56/57, not a circular
   prerequisite for their MSQ-54 prototype input.
5. Decide from the recorded fit, repair effort and weapon-contact results
   whether to use the MetaHuman rig, reuse its geometry on the current rig, or
   return specific failed regions to manual work. Only then finish UV/materials
   and make any justified high-detail source request. Keep the full MSQ-54
   original-model round trip and later MSQ-55–60 checks open until demonstrated.

## What the demonstration does not establish

The four varied characters support the workflow's breadth, while the manual
finger correction demonstrates that automatic correspondence can fail. The
tutorial does not measure our rifle grip/reload timing, first-person camera
clearance, look-down body continuity, fixed gameplay capsule, original glove
deformation, modular armor collision, planted feet, runtime material/LOD cost or
performance budget. Third-person movement and a successful motion-capture preview
are useful tests with a narrower scope. The author's speed and quality claims
are not acceptance evidence for MeridianSquad.

The earlier assumption that extensive manual retopology must precede any useful
rig trial should therefore be revised. MetaHuman warrants a small controlled
evaluation now; the result will determine which manual work remains necessary.

## Controller visual and local evidence

These are selected paused-frame observations, not measurements of the author's
project or claims that every setting was visible. Screenshots were inspected in
the browser tool trace; this report does not claim retained local PNG files.

| Time | Directly observed in the video |
| --- | --- |
| 04:50 | Blender contains the imported reference body beside the source mesh; this supports the scale-reference step. |
| 05:35 | Creator input shows Full Character, Head and Body, and Combined Mesh controls. |
| 06:35 | Manual Solve Actions and independent head/body refinement values are visible; Save Pose ordering is established by the transcript and Epic documentation. |
| 08:40 | Content Browser contains MH_dryad_PosedBody_DNA beside the character asset. |
| 10:10 | Blender has separate body geometry and the UV editor. The numeric U=-1 operation is documented from the transcript, not measured from this frame. |
| 11:15 | Cycles diffuse Color contribution and a 2048-pixel target image are visible. Selected to Active is still unchecked at this preparation instant; the transcript describes enabling it for the bake. |
| 14:05 | Final assembly Face folder contains a face skeletal mesh and DNA, distinct from the posed intermediate asset. |
| 16:45 | Blender FBX Armature settings show Add Leaf Bones unchecked. |
| 17:35 | Added accessory skeletal asset and Blueprint functions, including EnableMasterPose, are visible. The component's actual pose linkage is not established by this frame. |
| 19:40 | Footage track shows 1280x720, 24 fps. This is one example, not a maximum supported capture resolution. |
| 22:25 | Hand correspondence landmarks and source/target hands are visible during manual correction. |
| 25:25 | The texture-preparation copy is in A-pose in Blender. |
| 25:50 | Tripo import shows Use Original UV enabled and Y rotation 90 degrees. |
| 27:40 | The ballerina assembly has separate hair/skirt skeletal assets, consistent with the accessory workflow. |

Installed-version evidence was checked against files, not configuration alone:
UE Build.version is 5.8.1 / CL 56057345, compatible CL 55116800. Markerless and
Creator editor module BuildIds match that compatible build. Creator's installed
Core Data predicate passes for the texture archive and body texture assets.
This supports trying the feature; only a live editor test can establish actual
loading and successful solve/export in MeridianSquad.

The owner [research instruction](../../Approvals/PlayerCharacter01-MetaHumanStudy01.json)
also grants Blender tool-choice discretion. Background Blender remains useful
for repeatable source audits; a live MCP connection can be used when interaction
with the open scene is useful. A configured bridge is not evidence that it is
running. This research neither changed that setup nor ran a new DCC workload.

Research closure evidence is retained under
`Saved/PlayerCharacter01/MetaHumanVideoStudy01/`. The complete transcript has
SHA-256 `0398a2f698f9d61d883dd8127130a532a8b3dbe61aed7c7ec2ce73d37bc52f70`.
The untouched returned FBX still has SHA-256
`fc6340b6f36c529f15dac48ef06dca37aa72a07134b873e9e564f0addc6fa196`.
MSQ-54 received a description-only research handoff using `--no-start`;
status, assignment, original scope and run history are preserved. Production
remains incomplete, and this research does not close the full MSQ-54 issue.
