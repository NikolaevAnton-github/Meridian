# PainterStone01 source: Correction01

Current candidate: **LobbyPainter-Stone01/Correction01**. One bounded correction
of Review01 R1/R2; focused independent recheck and owner direction remain pending.
The original source bytes are preserved in the controller BeforeCorrection01
archive. Original Worker exports/images and Review01 remain immutable.

## Native source and interpretation

PainterStone01.spp is editable native Painter 12.1.4/API 0.3.5 source. The same
240 x 240 cm UV 0-1 quad, StoneSample.blend and original exported FBX are retained.
This authoring quad is not lobby geometry. Resolution is 2048; normals use
DirectX and PerFragment tangent space. No reference, rejected or externally
generated texture pixels were imported. Three installed native Substance
resources remain building blocks; no unchanged smart material was inserted.

The two actual OwnerReferences01 PNGs show a dark green-grey stone body, irregular
small mineral relationships, sparse pale structure and quiet polished highlights.
The foreground column faces/returns were inspected separately from the more
strongly veined floor. Exact quarry identity and grain dimensions are unknown.
Original 1672 x 941 reference regions: InnerEnd x100-330/y180-580;
EntranceSecurity x135-355/y190-615. References were viewed without pixel editing.

## Current layer stack

Listed bottom to top; all six layers remain visible, with no masks/effects.
Exact version URLs, returned parameters, channel values and projection readback
are in layer-recipe.json and Correction01/Painter/final-source-evidence.json.

| UID | Native layer | Current contribution |
| --- | --- | --- |
| 120 | 01 Mineral groundmass | Modified marble_veined, BaseColor only. Seed 714; body sRGB [0.095,0.108,0.100], vein color [0.130,0.146,0.136], contrast 0. Existing damage/depth switches stay disabled. |
| 177 | 02 Interlocking mineral fragments | Replaced the ring-bearing color resource with native marble_fine. Seed 461, position 0.50, contrast 0.12, Disorder 78, Marbling 0.75. UV scale 4, offset 0.13/0.27; BaseColor Overlay 0.40. Creates a fine branching mineral network. |
| 186 | 03 Broken pale mineral threads | Unchanged native marble_fine; seed 1283, scale 3, offset 0.38/0.09; BaseColor Screen 0.045. |
| 195 | 04 Polished cut surface | Unchanged uniform roughness 0.24 and metallic 0. |
| 204 | 05 Subtle mineral roughness | Unchanged grunge_stone_details; roughness Overlay 0.16. |
| 213 | 06 Restrained microrelief | Unchanged grunge_stone_details; Height Normal 0.002. |

The original ring resource remains in the calibrated finish channels only.
It has no BaseColor contribution. Faint ring-shaped highlight modulation remains
visible under the original strong lights and is explicitly flagged for recheck.

## Export and native material

Final native exports are under
Saved/OpeningLobby/PainterStone01/Worker/Exports/Correction01/FinalReopened/.
All three match FinalSaved byte for byte after actual source reopen. Canonical
Channels files match these exports exactly. ORM and Normal also match the
original reviewed candidate byte for byte; their native Unreal assets were not
reimported. Only BaseColor was refreshed.

| Channel | Encoding and use |
| --- | --- |
| BaseColor | sRGB, default compression |
| ORM | Linear R=AO 255, G=roughness 51-71, B=metallic 0; masks compression |
| Normal | DirectX, linear normal compression, no green flip; R119-136/G117-138/B254-255 |

M_PainterStone01 keeps the same 13 connected expressions and three task textures.
Only its BaseColor custom node changes: smooth triangular blending of differently
offset samples breaks the simple 240 cm repeat while preserving the original
texel coverage, projection scale and material family. Fourth-power normalized
weights retain local detail. Explicit texture gradients retain ordinary mip
selection. No new texture dependency, tint, displacement, geometry or binding
is introduced. ORM and world-reoriented normal paths are unchanged.

Editable integration/sampling source: Scripts/OpeningLobby/painterstone01_material.py.
The sampling_variation operation applies once to the archived original graph;
its before/after code is in Correction01/native-sampling-change.json. The native
audit records 351 pixel instructions, 148 vertex instructions and four samplers;
this is not a performance benchmark or an arbitrary-curved-surface normal test.

For this correction, all helper outputs route to Worker/Correction01. Source and
original candidate evidence are reused read-only. Do not rerun historical creation
or binding operations over the current map. The current material is still bound
to exactly four existing component slots. Additional production requires the
controller's next authorization.

## Assessment and limitations

The corrected body is quieter, with branching dark/pale mineral structure instead
of the dominant dark rings. Fine structure is subdued at context distance; the
reviewer must judge whether its density matches the reference columns. Broad
highlights and their faint ring modulation persist from preserved finish inputs.
This is an author assessment, not independent acceptance.

Painter GUI preview limitations remain documented in initial Worker history.
No new GUI-capture investigation was attempted. Source evidence is native layer,
resource and parameter readback plus exact saved/reopened regeneration; visual
assessment uses the six unchanged-pose Unreal captures in Worker/Correction01/Final.

Handoff: Docs/OpeningLobbyPainterStone01.md. Exact candidate identity and inventory:
Worker/Correction01/identity.json and manifest.json. Full-lobby materials and final
atmosphere remain outside this candidate.
