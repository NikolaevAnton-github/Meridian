# Datum16MeshUsability01 controller review

2026-09-17, MSQ-54. The bounded existing-topology assessment is complete.
**Retain Revision02 as the working base; blanket retopology is not justified.**
This accepts the assessment evidence, not a finished protagonist, final
deformation/contact quality or owner visual approval. Full MSQ-54 remains
`in_progress` and unassigned; no successor was dispatched.

The [worker report](PlayerCharacter01MeshUsability01.md) records the regional
verdicts. [The evidence gallery](../Saved/PlayerCharacter01/MeshUsability01/Worker/index.html)
and editable `Assets/Source/PlayerCharacter01/MeshUsability01/Datum16_Bind05.blend`
preserve the actual candidate. Both original owner export revisions are retained
under named `OwnerExports/Revision01` and `Revision02` paths.

## Findings and limits

- Revision02 contains **24,264 quads plus 8,112 triangles**, or **56,640 native
  triangles**. All 28,332 source vertices, 60,797 edges and 32,376 polygon index
  lists remain in order. The native import's 29,084 vertices include splits.
- Actual Blender-to-Unreal import matches the **161-bone hierarchy**, with no
  missing, extra or differently parented bones. Maximum local bind position
  difference is 0.000339 cm, angular difference 0.139 degrees and bone-scale
  numerical deviation 0.00001193. This is measured numerical agreement, not
  bitwise equality. Accepted rig assets and source animations are unchanged.
- Nineteen evaluated probes exercise arms, wrists, digits, crouch and ankles.
  Four ordinary/empty aimed/unaimed TP reloads use the candidate's own rig and
  `ik_hand_gun`, with synchronized rifle playback and no hidden donor carrier.
  Timing passes; the sparse contact views do not establish continuous contact.
- Collar, glove/cuff and boot structural defects need local repair. Shoulders,
  knees and thumb/web deformation remain visibly poor or unresolved. Fitting
  and weights contribute, so those failures do not prove that whole regions
  require replacement topology. The thumb closeup has conspicuous web/hinge
  collapse; this is retained as failure evidence, not a successful hand result.
- Rifle grip is unfinished. The 170 cm camera image is a TP control-pose
  diagnostic, not authored FP animation, ADS alignment or MSQ-55 acceptance.
  Original UVs, production materials and armor completion are outside this check.

The controller inspected source/wire evidence, representative deformation views,
the final left-thumb Detail05 image and Bind05 native reload frame 001. A focused
independent reviewer inspected both hands' fixed-camera rest/index/middle/thumb
gray and wire evidence. Early weight-group-only metrics and moving/occluded
views were inadequate. Bind05 plus Detail05 resolved that evidence gap: the
ten source-defined sampled distal digit sets show zero unintended movement,
with a fixed camera target and 0.31 m scale. This excludes neither untested
palm/web leakage nor poor thumb opposition or weapon contact.

All six candidate mesh/skeleton packages have no missing hard `/Game`
dependencies. The copied reference donor alone retains the unavailable
`ABP_Manny_PostProcess` dependency; it does not belong to Bind05. It is inventoried
as an experimental reference, with external references documented rather than
invented as complete registry relationships.

## Verification and preservation

Controller verification passed **52 frozen artifact hashes**, **859 evidence
hashes** and **650 of 650 protected file hashes**. Exact manifest identities:

| Manifest | SHA-256 |
| --- | --- |
| `Assets/Source/PlayerCharacter01/MeshUsability01/manifest.json` | `3a180c778b1335abccc6801b65e4defbe25dfb50497e3a0ca71573364449ef31` |
| `Saved/PlayerCharacter01/MeshUsability01/Worker/evidence-manifest.json` | `ae75963a9bdfa8f62b562900c91b8a606306712927497da102e02c48e6b4584a` |

The owner's original drop FBX and both existing Config edits were preserved and
excluded from the task commit. Revision01 was recovered from its existing Git
LFS object into a separate named path; Revision02 was copied without changing
the owner drop. Historical manifests and registry fingerprints were not
rebaselined. Validation of old `Datum16UndersuitInput01` still reports exactly
the one pre-existing replaced drop file; its historical identity is unchanged.

The separate local asset registry registered and validated **57 artifacts and
22 relationships** for `Datum16MeshUsability01`. This is an inventory of
experimental, intermediate, rejected and source identities; registration does
not promote them to production acceptance. Derivation claims remain declared
where only the documented workflow supports them. Native candidate hard
references have observed evidence.

The pre-manifest project measurement was 18,658,198,768 bytes, a measured
829,683,903-byte increase, excluding reparse-point targets. Subsequent small
metadata and Git/LFS staging add bytes within the 250 GB budget. Serial process
observations measured Blender at 1.531 GB and Unreal at 4.877 GB working-set
high-water; these are not complete system-wide peak VRAM measurements.

## Execution closure

Primary Multica run `01a0b0ec-78c3-7cfe-a225-2aff4a827e24` completed. Native
execution evidence confirms `gpt-6-astra / high / default`, fast mode disabled
and one production worker. The previous MetaHuman max override was task-local;
the assessment used the documented implementation baseline. Exact saved agent
model, reasoning, service tier, custom arguments, instructions and concurrency
were restored after completion.

Queued correction `01a0b0fe-8255-787d-b169-4a08f2421d14` was canceled before
dispatch: the primary worker had already resolved its circular-metric and
camera/occlusion findings. The independent review found no remaining must-fix
evidence gap for this bounded assessment. No correction execution or successor
was needed. The issue description and unassignment used administrative
suppression; no additional run was created. Unreal and Blender are closed, and
the task runtime is stopped. Local project services remain available.

Controller evidence is in
`Saved/PlayerCharacter01/MeshUsability01/Controller/`: technical and independent
reviews, input preservation, native execution verification, profile restoration,
registry validation, administrative closure and staging/commit verification.
The local closure commit contains only verified MSQ-54 scope under the standing
[task-closure instruction](Approvals/TaskClosureCommits01.json).
