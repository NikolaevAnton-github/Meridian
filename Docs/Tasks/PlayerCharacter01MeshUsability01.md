# MSQ-54: Datum16MeshUsability01

Authorized 2026-09-17 by the [owner instruction](../Approvals/PlayerCharacter01-MeshUsability01.json).
Determine whether the improved owner-supplied Tripo coverall can retain its
existing topology as a rigged game mesh. Do not assume full manual retopology is
necessary. This bounded assessment uses existing MSQ-54; the entire protagonist
prototype and later gameplay/finish tasks remain incomplete.

Delivered 2026-09-17: [measured report](../PlayerCharacter01MeshUsability01.md)
and [controller review](../PlayerCharacter01MeshUsability01Review.md).
Retain the bulk Revision02 topology; perform localized structural, fit and
weight repairs before any broader topology decision. Bind05 completed the
bounded native round trip and playback checks, with explicit joint/contact/FP
quality limitations. The execution brief below is preserved as the completed
assessment scope, not an instruction to repeat it or start successor work.

## Inputs and authority

Read current ProjectState, PlayerCharacter01Plan/Tasks, AI3D pipeline,
PlayerCharacter01BodyIntake01, PlayerAnimationAudit01 and the MetaHuman trial
handoff for relevant sources and limits. The current instruction supersedes
historical mandatory-retopology wording: prove actual failures before proposing
replacement topology. Datum16 selection and MSQ52-RigContract01 are satisfied.

Input directory:
`Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16UndersuitInput01/OwnerExports/`.
Use `Revision02/tactical+jumpsuit+3d+model.fbx` as the exact current candidate:
1,186,096 bytes; SHA-256
`aade1a13585f8639610e42a12cc350619ff4279e33325968f416bb4e8b8e8467`.
`Revision01/` contains the previous 933,904-byte source, SHA-256
`fc6340b6f36c529f15dac48ef06dca37aa72a07134b873e9e564f0addc6fa196`.
The controller recovered Revision01 from its existing Git LFS object and copied
Revision02 from the owner's working drop without changing that file. See
`SourceRevisions01.json`. Do not write anywhere in this input directory.

The owner's original drop path now contains Revision02. Its old registry record
and historical manifests describe Revision01 and are expected to detect changed
bytes. This predates the run; do not repair it by restoring or rebaselining.
Preserve both Config/DefaultEditor.ini and Config/DefaultEngine.ini owner edits.
The MetaHuman result is only a diagnostic reference, not the tested garment or
an approved alternate rig. Do not overwrite any prior task or Saved evidence.

Reuse notes: `animation_audit01_unreal.py` contains actual reference-pose and
skin-influence reads, but its `preview_pose()` replaces the mesh with the
mannequin. Adapt playback to retain and assert the candidate. The full
`/Game/InfimaGames/TacticalFPSAnimations/Common/Characters/Mannequins/Meshes/SKM_Manny`
has the required 161 bones; the Simple donor meshes have 89 and must not define
the complete hierarchy. No verified mannequin FBX/weight-transfer round trip
is already available. Use keyed/evaluated pose captures as in the corrected
MetaHuman Deformation03 helper, not unregistered-component socket transforms.
For the exact-rig trial, attach the rifle to the candidate's own `ik_hand_gun`;
a hidden donor carrier can only be reported as an incomplete diagnostic.

## Bounded execution and acceptance

1. Snapshot source/rig/config and protected asset hashes, current dirty packages,
   tool capabilities, storage and memory. Confirm the actual project/editor
   before any Unreal mutation through official Epic MCP. At controller intake
   there was no running Unreal or Blender process; recheck before launch.
2. Reuse the existing body/shoulder intake numerical helpers with new output
   paths. Import Revision02 in actual Blender, recording version/settings. Compare
   static dimensions, silhouette, folds, hands and original quad wireframe with
   Revision01 using matched views. Count vertices, triangles/quads/ngons, islands,
   boundaries, multi-face/winding defects, duplicates, normals, UVs, armature and
   weights. Distinguish deliberate garment openings from defects; a boundary is
   not automatically a failure. Do not overwrite the old intake or invoke its
   fixed output paths against the replaced owner file.
3. Create a native editable working derivative preserving an untouched source
   layer. Fit orientation, temporary scale and T/A rest pose to the exact existing
   161-bone rig. Preserve hierarchy and reference transforms, source animations,
   170 cm camera and 34/88 cm capsule. Temporary test stature is not owner-approved
   production stature. Record all geometric fitting and any local corrections.
   Keep a topology-preserving fitted version as the baseline: no wholesale
   decimation, remeshing, subdivision or retopology before testing.
4. Establish a credible initial bind using the compatible source character and
   bounded regional weight work. Verify normalization, influences, unweighted
   vertices and all ten digit assignments. Cross-finger weight leakage or a bad
   rest-pose fit cannot establish that the topology itself fails. Correct such
   causes with bounded evidence-led work, retaining before/after versions.
5. Test deformation on the actual Revision02 surface: shoulder raise and cross-body
   reach, elbow bend/forearm twist, wrist flex, ten individual digits and rifle
   grip, hip/knee deep crouch and ankle flex. Use repeatable poses and clear
   neutral-gray/wire closeups of both sides. Distinguish shading/normal, fit,
   skin-weight, pose and topology failures. Preserve failures and corrected views.
6. Perform a real Blender-to-Unreal round trip on isolated experimental assets
   using the exact rig contract. Validate imported hierarchy/rest transforms,
   scale, material dependencies and source-geometry identity. Reuse existing
   MSQ-52 playback/contact helpers for four ordinary/empty aimed/unaimed TP reload
   cases with synchronized rifle and magazine, actual source timing and additive
   bases. Capture actual new-surface deformation and hand/contact evidence, not
   motion on a hidden donor alone. If blocked, establish the exact cause and
   mark downstream checks unverified; an export success is not a motion pass.
7. Inspect the actual arm/glove surface at a representative close first-person
   distance. A bounded presentation probe is allowed; full MSQ-55 integration is
   excluded. No gameplay or lobby mutation. A plain control-pose/diagnostic shot
   must not be called an authored FP animation or complete camera-fit pass.
8. Deliver a per-region verdict: retain unchanged topology, retain with fit/weight
   corrections, local topology repair, or unresolved. A proposed full retopology
   must have concrete widespread failures after credible binding; do not perform
   it in this task. No need to finish armor, UVs, textures or cosmetic detailing.
   There is no approved hard polygon cap; the chat's counts were planning ranges.
9. After two equivalent failures change the diagnostic approach. Reuse validators
   and harnesses; do not build new orchestration. One production worker, one DCC
   writer and one heavy workload. Measure peak memory and storage growth under
   the 250 GB cap. Preserve dirty owner work if a restart is needed.

## Output and handoff

- `Assets/Source/PlayerCharacter01/MeshUsability01/`: editable Blender source,
  fitted/bound variants, exports, settings/provenance and final immutable manifest.
- `/Game/Development/PlayerCharacter01/MeshUsability01/`: isolated test assets.
- `Scripts/PlayerCharacter01/mesh_usability01_*`: only thin reusable task helpers.
- `Saved/PlayerCharacter01/MeshUsability01/Worker/`: full evidence, logs, failures,
  matched images, actual playback and an image index with meaningful labels.
- `Docs/PlayerCharacter01MeshUsability01.md`: concise English report, exact source
  and candidate identities, regional findings, corrections made, actual checks,
  pass/fail/unverified limits and the smallest justified next work.

Use Astra/high/standard with verified native arguments for this implementation
run; the earlier max override applied to the completed MetaHuman trial. The
controller handles issue administration, approval/task/state records, registry,
review, saved-profile restoration and the local closure commit. The worker must
not change those files, issue comments/status, profiles, commits or dispatch
successors. No new generation, paid APIs or independent concept review.
