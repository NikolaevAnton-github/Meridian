# Column concrete fins and embedded reinforcement

2026-09-26. Direct MSQ-156 follow-up under the owner's
[instruction](Approvals/ColumnRelief06-OwnerDirect01.json), without a new task
or independent reviewer. Source **revision 13** supersedes
[revision 11](ColumnVariation05.md). Final appearance remains an owner gate.

The owner image showed thin concrete fins and a reinforcement grid exposed
almost continuously. The accumulated relief maps and outermost radial-profile
normalization stretched existing undercuts. `relief_spalling.py` rebuilds the
shared cells from immutable revision 04 with the same revision-08 size
redistribution and merge groups, one bounded coordinate relief flow, and mild
radial expansion. It omits the sampled radial normalization. This retains
irregular broad fractures while reducing the thin projecting folds. The area
of side triangles facing inward radially falls from 11.314% to 3.300%; this
is a diagnostic comparison, not a proof that every triangle is intersection-free.

The longitudinal reinforcement axes move from +/-89.8 to +/-65.8 cm: **24 cm
deeper on each side**. Bar/tie diameters and 20 cm tie spacing remain. A
conservative source-ray check at 2 cm height intervals finds potential exposure
at 5.44% of samples after all debris is removed. Corner bars are counted on
both adjacent faces; this percentage is not an image coverage measurement.
The final oblique authoring view shows short exposed sections in recesses.

The stone-facing triangle positions, 240 x 240 x 1800 cm envelope, 480 body
grouping, support clusters and materials match revision 11 exactly. There
are still 120 hidden support anchors; their corners and face centers have
at least 5.43651 cm X-axis clearance inside the core. All removable solids
are closed with positive volume. Total core plus fragment volume is
103,680,000.003 cm3. Existing collinear core tessellation junctions have no
unmatched geometric subsegments.

The saved collection has 600 convex hulls and 7,976 hull vertices. The core
collision proxy has 2,848 triangles at the existing 0.5 cm simplification
tolerance. Render triangle counts are unchanged. `repair_core_uv.py` now
also gives steep lower-band ledges planar UVs to avoid the stretched cylindrical
projection; the imported core has valid normals and tangents. The authoring
helper applies this correction when importing revision 13 or later.

Evidence is in `Saved/ColumnRelief06/`: the preserved owner image and four
pre-change packages, source checks, core seam check, `relief-and-steel13.json`,
`preserved13.json`, asset/collision/UV reports, and final front/oblique views.
Those views deliberately hide all removable bodies and use a temporary
inspection light. They are authoring evidence, not a firing or performance test.
Revision 12 was a source-only iteration; it was not imported. Revisions 12/13
are retained under `Assets/Source/ReinforcedColumn01/ReinforcedColumn02-Candidate01/`.

At handoff, all 144 original actors match the preflight snapshot, the original
camera is restored within 0.0001 cm/degrees, no packages are dirty, and the
saved lobby map hash is unchanged. The footprint audit measured 121.77 GB,
below the 250 GB limit. No gameplay code, damage settings or FX were changed.
