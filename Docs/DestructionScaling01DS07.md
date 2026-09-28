# MSQ-167 / DS-07 handoff

Implemented in the [direct batch](DestructionScaling01Batch01.md), under the owner's [scoped exception](Approvals/DestructionScaling01-DirectBatch01.json).

`DestructionCompactAuthoring.cpp` creates render-only facing sections from the exact source mesh descriptions, transforms, normals/tangents, all UV channels, colors and material assignments. Candidate01 contains 36 section meshes and one data asset (under 1 MB); 768 tiles and all 11,576 source triangles are preserved. Original assets and query geometry remain unchanged.

Intact sections share render groups across nearby columns. Damage expands only the affected section before removing its selected tile. Compatible detached ceramic and carried-facing pieces also share render groups; each retains separate exact physics/query identity. World-position grouping, swap-removal and owner cleanup keep handles correct. Material overrides split compatible groups; unsupported rendering settings retain the original renderer. Existing Nanite GC rendering continues for concrete.

Source provenance: `Assets/Source/DestructionScaling01/Candidate01/provenance.json`. Registry candidate: `DestructionScaling01-CompactFacing-Candidate01` (38 artifacts, 37 declared derivation relationships). Registration/validation succeeded; it does not grant owner visual acceptance. Final representative views and mapping checks are in the batch handoff.
