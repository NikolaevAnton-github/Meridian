# MSQ-54: Datum16ShoulderIntake01

The owner returned `armor+shoulder+plate+3d+model.fbx` on 2026-09-17 in
`Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16ShoulderManual01/OwnerExports/`.
The prior manual-pilot decision explicitly assigns later source inspection to
the controller. This is that bounded inspection, not a full-body production run.

Read Docs/ProjectState.md, Docs/PlayerCharacter01TripoManualPilot01.md and
Docs/Approvals/PlayerCharacter01-TripoManualPilot01.json first. Preserve all
existing bytes, including the returned FBX, art, package manifest and owner config.

## Worker scope

Use the installed `D:/blender/blender.exe` in an isolated background process
with factory startup and auto-execution disabled. Verify actual Blender version
and import capability. Do not operate an existing GUI session or Unreal/Painter.
Only one DCC workload may run. Keep generated evidence under
`Saved/PlayerCharacter01/Datum16ShoulderIntake01/Worker/` (maximum 100 MB).

Write only in that evidence directory and these two new tracked files:

- Scripts/PlayerCharacter01/shoulder_intake01.py
- Docs/PlayerCharacter01ShoulderIntake01.md

Inspect the untouched source, SHA-256
`c1be7d5f1e82b955c9367f5335e45f1e191177bf298ba0112eb9604575d65078`,
134960 bytes. Record FBX metadata, objects, components, vertices/edges/faces,
triangle/quad/ngon counts, triangulated count, normals/winding, boundary and
non-manifold edges, duplicate/degenerate geometry, bounds/units/transforms,
UVs/materials/images, armature and animation contents. Use deterministic checks
and name their limitations (self-intersection/thickness are not guaranteed by
manifold topology). Do not modify, weld, repair, normalize or re-export source.

Produce readable gray outside, inside and side views plus wireframe evidence
at consistent framing. Inspect actual images, then assess whether a shallow
concave shell and useful thickness exist, what is missing/fused, and the likely
bounded repair path. No need for elaborate rendering or a benchmark harness.
Do not create a production blend, body master, rig or new geometry candidate.

Primary art is Assets/Concepts/PlayerCharacter01/Concept02/16.png. The expected
single-image input is Datum16ShoulderManual01/Inputs/01-StartHere-Outer45.png.
These may be inspected for source interpretation; do not act as an independent
concept reviewer or grant design acceptance. The wearer-right deltoid cap is
one component; hidden construction is inferred and final scale is unapproved.
Do not claim requested P2/Quad3000/privacy/credits were used without evidence.
No Tripo job/settings record or sidecars have been returned with this FBX.

Report measured source facts, technical usability/repair needs, unknowns and
remaining body-fit/arm-elevation/aim/reload tests under MSQ52-RigContract01.
MSQ-54 stays incomplete. No new generation, browser/provider calls, paid API,
installs, other editing, delegation, registry mutation, comments, task changes,
commits or pushes. The controller reviews the evidence, inventories source,
updates live task state and commits the bounded intake.
