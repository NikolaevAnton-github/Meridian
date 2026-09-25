# Column runtime repair — MSQ-156 follow-up

2026-09-26. Direct repair requested by the owner, explicitly without a new task.
This supersedes the runtime settings and untested gameplay status in
[ReinforcedColumn02](ReinforcedColumn02.md); its revision-04 fracture geometry is retained.

The previous delivery doubled the fragment surface to 1.57 million triangles,
left Nanite disabled, and added anchored intermediate clusters that shielded
fine fragments from the vendor's local strain sampling. Five real rifle hits
reached RC01 but detached nothing. Moving fragments additionally used expensive
particle/implicit contacts instead of their generated convex collision hulls.

The repair keeps all 644 removable pieces, 120 embedded anchors, reinforcement,
core, materials, and source geometry. It puts leaves directly under the anchored
root, preserves their effective 50,000 strain threshold, enables Nanite, and
uses volumetric convex contacts. Static mesh fallback geometry remains at 100%
because it supplies complex collision. The existing vendor field now has a
48 cm radius; 14 cm and 24 cm failed to release pieces at the tested impact.
Graph propagation is disabled. Only this column data asset disables
collision-generated strain, preventing loose chips against the retained core
from breaking the whole shell. Contacts and vendor bullet strain remain enabled.
The setting is applied at BeginPlay, including F6 replacement actors.

## Verification

Evidence is in `Saved/ColumnRepair01/`. `RepairBuild04.json` records the successful
native build and exact source/DLL hashes. `cold-final-verification.json` verifies
the saved assets after restart, all 144 scene actors, unchanged source triangle
counts/full collision fallback, 120 anchors, and preserved owner files.

Real rifle input travels through Enhanced Input and the normal finite projectile
path. `final-front.json` records five hits and 17 local detached pieces;
`front-grid.json` confirms retained rebar at 6.6 cm and exposed core between bars
at 40–65 cm behind the original skin. `final-reset.json` confirms zero hit/break
counters and exact restoration of all initial piece transforms after F6.
`final-side.json` records four hits and 11 local breaks on a second face, with
8.53 ms median and 14.99 ms p95. Anchors remain fixed in both series. All vendor specimen
collision-damage defaults remain enabled (`cold-runtime-settings.json`).

At the same camera, the broken baseline recorded 13.90 ms median per frame and
zero detached pieces (`before-visible.json`). The repaired intact column records
8.33 ms; the final five-shot series records 10.31 ms median and 22.39 ms p95.
An isolated eight-piece diagnostic improved from 132.60 ms to 9.33 ms median
after the contact/strain corrections. These are short local PIE measurements,
not a claim to reproduce the owner's entire previous FPS history. The early
`after-idle.json` comparison is invalid because its camera faced away; background
throttled diagnostic runs are also excluded.

Independent technical review: `Saved/ColumnRepair01/primary-review.md`.
Visual evidence: `Saved/ColumnRepair01/final-front.png`. Owner visual/play
acceptance remains separate. No new Multica task or worker run was created.
