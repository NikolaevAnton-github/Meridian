# Column fragment variation and concrete relief

2026-09-26. Direct MSQ-156 follow-up under the owner's
[instruction](Approvals/ColumnVariation05-OwnerDirect01.json), without a new task
or independent reviewer. Source **revision 11** supersedes the active
[revision 07](ColumnShape04.md).

`Scripts/ReinforcedColumn01/varied_spalling.py` (08) redistributes the existing closed
fracture cells using monotone coordinate maps. This creates small and large
silhouettes without increasing the physical body count. Twenty-four connected
surface unions add compact, horizontal and vertical shapes; 33 interior pairs
are separated to retain **480 removable bodies and 120 anchors**. All original
stone-only leaves stay bonded to their concrete backing. Source face adjacency
and the existing local support groups constrain each union.

Concrete receives shared three-axis geometric relief at 34, 13 and 5.5 cm
scales. `profile_spalling.py` replaces the coarse radial core profile with an
86 cm nominal envelope plus irregular relief, retaining a thick removable
layer. A 2 cm profile grid drives a continuous monotone map. Concrete core
normals and cylindrical UVs continue across the old Voronoi face boundaries.
`author_spalling.py` runs `repair_core_uv.py` after the revision-11 import:
the horizontal concrete caps use planar UVs and explicit tangents, avoiding
the stretched texture from cylindrical projection on a horizontal surface.
The same mapping moves both sides of each fracture, the retained core,
anchors and sparse collision points. Stone faces remain planar with 1.8 cm
cladding; their UV projection is restored after tangential redistribution.
The 240 x 240 x 1800 cm envelope, materials, revision-07 inset steel and map
placement remain. No runtime code or damage/FX settings change.

The generated projected body bounds range from 10.7 to 155.9 cm in width and
8.9 to 121.5 cm in height. These are axis-aligned silhouette measurements,
not rectangular fragment shapes. There are 221 bodies below a 1.5 aspect ratio
and 136 above 2. Render geometry contains 171,447 core triangles and 1,475,172
fragment triangles.

The saved collection uses 600 convex hulls with 7,688 vertices, including its
120 support anchors. The separate core collision proxy has 13,818 triangles
at the existing 0.5 cm simplification tolerance. These authoring counts are
not performance measurements.

Source and design are under
`Assets/Source/ReinforcedColumn01/ReinforcedColumn02-Candidate01/`, with the
`11` suffix. Previous source revisions remain immutable; pre-import assets
and owner images are preserved under `Saved/ColumnVariation05/`.

Self-checks and authoring reports are stored in that evidence directory.
`source-check11.json` confirms closed positive-volume fragments and anchors,
finite coordinates and total volume 103,679,999.990 cm3. `core-seams11.json` distinguishes
the inherited collinear tessellation junctions from unmatched geometric edges;
there are no unmatched subsegments. The authoring scripts rebuild 120 hidden
0.8 cm anchor cubes instead of shearing their coarse geometry with the visual
relief field. Every corner and face center is inside the core, with at least
1.28519 cm X-axis clearance. This closes the inverted anchor found in the
revision-09 source check; revision 09 was not imported into Unreal.
The core authoring view deliberately hides every removable body and uses a
temporary inspection light; it is not firing evidence. No independent review,
firing session or performance benchmark is run.
`authoring-core11-final.png` shows the final cap UV correction. The saved
reinforcement package is byte-identical to the pre-change package. At handoff
all 144 original actors match, the original editor camera is restored, no
packages are dirty and the lobby map was not rewritten.
