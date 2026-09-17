# MSQ-54: Datum16BodyIntake01

On 2026-09-17 the owner returned the generated full-body foundation after the
Datum16UndersuitInput01 handoff. This continues the promised local source
inspection. It does not dispatch a complete production body, rig or gameplay.

Source: Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16UndersuitInput01/OwnerExports/tactical+jumpsuit+3d+model.fbx
SHA-256: fc6340b6f36c529f15dac48ef06dca37aa72a07134b873e9e564f0addc6fa196
Size: 933904 bytes. Preserve exact bytes and filename, all prior art/packages,
rig-contract/source data and Config/DefaultEngine.ini.

Read Docs/ProjectState.md, the undersuit input README/task, the AI3D pipeline
and Docs/PlayerAnimationAudit01.md. The selected appearance is Datum16;
the under-armor input includes a fully opaque soft hood, coverall, gloves and
boots. The hood is an inferred layer under the unchanged final helmet design.
Suggested owner settings were P2.0 / Quad target 20000 / single image / Private,
with no texture, rig or later processing. These remain recommendations until
supported by an actual job/settings record, not facts inferred from the filename.

## Bounded worker scope and acceptance

Use an isolated installed D:/blender/blender.exe background process with factory
startup and auto-execution disabled; verify actual version/import capability.
Do not operate an existing GUI, Unreal or Painter. One DCC workload at a time.

Reuse numerical inspection helpers from Scripts/PlayerCharacter01/shoulder_intake01.py
by import where practical; do not modify that registered script or rebuild the
benchmark harness. Add a thin body-specific script and views, not another framework.
Skip shell-thickness diagnostics if irrelevant to this clothed body inspection.

Write only:
- Scripts/PlayerCharacter01/body_intake01.py
- Docs/PlayerCharacter01BodyIntake01.md
- Saved/PlayerCharacter01/Datum16BodyIntake01/Worker/ (maximum 150 MB)

1. Verify source identity and successful import; record raw FBX metadata and
   actual object/mesh/armature/action/UV/material/image contents. Count vertices,
   edges, triangles/quads/ngons, triangulated faces and connected islands.
   Check boundaries, non-manifold edges, duplicate/degenerate surfaces, winding
   and custom normals. Distinguish diagnostic flags from proven defects.
2. Record bounds, declared units, axes and transforms, neutral pose and obvious
   proportional/asymmetry issues. Generated size is not approved protagonist
   stature. The contract's 180.5439 cm diagnostic mesh height is not owner approval.
3. Render gray and wire evidence with readable front/back/side/oblique views,
   plus close views of BOTH hands including palm/dorsal or oblique directions
   that actually expose finger separation. Inspect shoulders/armpits, elbows,
   wrists, hips/crotch, knees and ankles. Identify missing/fused fingers, webbing,
   joint-loop limitations, thin/fused cloth or invented back surfaces. Do not
   claim five usable articulated fingers from a frontal silhouette alone.
4. Inspect actual renders and the Inputs/01-StartHere-FrontTpose.png reference.
   This is technical model intake and source interpretation, not independent
   concept review or owner design acceptance. A static source cannot establish
   deformation, skinning, grip/reload contact or rig compatibility.
5. Provide a concise measured verdict: usable reference, usable repair base, or
   unsuitable, with specific next repair/fitting priorities and limitations.
   Keep T-pose source distinct from the contract's A-pose bind, exact 161-bone
   transforms and 170 cm camera / 34/88 cm capsule. Do not move these to fit a model.

Do not weld, repair, remesh, normalize, re-export, save a production blend,
create/fit a master or bind a rig in this intake. No external generation,
provider/browser calls, paid API, installs, delegation, other editing, registry
mutation, comments, task/status changes, commits or pushes. Controller reviews
the handoff, records source provenance, updates the live issue and commits.
Keep prior failed diagnostic attempts and finalize the evidence manifest only
after logs stop changing; do not hash a manifest into itself. MSQ-54 stays incomplete.
