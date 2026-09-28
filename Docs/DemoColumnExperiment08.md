# DemoColumnExperiment08

[Owner direction](Approvals/DemoColumnExperiment08.json): correct inward concrete
motion, visible facing fracture on landing, overlapping fallen tiles, and further
reduce large concrete pieces. Baseline `b7c8ccd` and its Correction07 assets remain
preserved. Direct implementation without tasks, agents or independent reviewers;
owner visual/play judgement remains open.

## Candidate behavior

Only exterior concrete pieces with at least 3,000 square cm of lateral area are
selected for another cut. The cut targets a 64/36 split of visible area, making
the larger child approximately 80% of its parent's equivalent visible linear size.
Unselected pieces and the 167 protected core pieces retain their geometry.
Facing support footprints are rebuilt for the new concrete cuts.

Released concrete uses the column side's outward normal instead of the hit
triangle normal, which could point into a shot cavity. Its bounded launch speed
is 135–190 cm/s, with low spin and the previous low restitution retained. A narrow
physical barrier inside the anchored central square prevents debris entering
the protected core without adding a visible surface or blocking rifle queries.

Large ceramic facing meshes are partitioned into four matching convex pieces,
preserving their shape, total area, thickness, UV alignment and material. The
first substantial floor/pile impact removes all facing still carried by that
concrete piece and releases its ceramic shards. Independently falling large
facing pieces also fracture on a substantial landing impulse. Shards share the
existing retention controller; they are not recursively fractured.

Loose concrete, ceramic and retained debris collide with one another. Retained
pieces stop moving but keep stationary collision so later pieces can land on
them. Retention requires stable support on the floor or already retained debris;
temporary debris cannot become the sole support for a permanent piece. The shared
budget remains 50, with at most 30 ceramic pieces leaving room for concrete.
At most 32 ceramic shards are actively simulated; excess unretained shards are
evicted oldest-first. Unretained debris expires after 12 game seconds. Stationary
collision adds a bounded contact/query cost compared with Correction07's disabled
physical collision. F6 destroys the old specimen, core barrier and its debris.

## Evidence

Authoring and real-rifle helpers: `Scripts/DemoColumnExperiment08/`.
Generated source, inspections, build logs and runtime evidence:
`Saved/DemoColumnExperiment08/` (excluded from Git).

- Development Editor build `compile04` passed; the rebuilt native module was
  loaded in a fresh editor for the final probes.
- 191 large exterior pieces were split. The larger child's median equivalent
  visible linear size is 79.60% of its parent (20.40% smaller). The collection
  has 1,065 leaves; all 683 unselected pieces, including all 167 protected core
  pieces, retain their geometry. All leaves have convex collision.
- 82 original ceramic mesh variants produce 328 matching shard meshes, covering
  824 large facing instances. Generated shard areas sum to their source areas
  within the generator's 0.02% tolerance.
- The normal and three-face stress probes fired 94 real rifle shots in total.
  Normal concrete travel reached approximately 209 cm horizontally. Stress
  exercised 44 concrete landing crumbles, 27 independent tile breaks and one
  shot-induced crumble. The normal probe added one landing crumble and one
  independent tile break.
- Stress filled the shared retention budget with 30 ceramic pieces and 20
  concrete pieces, while active ceramic debris never exceeded 32. Two retained
  tiles had their entire bounds above the floor while remaining supported by
  other debris, confirming an actual second layer.
- Every sampled invariant passed: no moved core pieces, detached concrete
  overlapping the core, unsupported wall facing, retained unsupported debris,
  remaining facing on a landed concrete carrier, deeply overlapping retained
  parallel tile plates, or retained bodies still dynamically simulating. The
  167 protected core transforms had zero measured translation.
- F6 restored all 1,560 facing instances and cleared loose, carried and retained
  debris. The editor was returned to the previous view with 145 actors, all
  unrelated actor paths, labels and transforms unchanged, and no dirty packages.

Native debugging during authoring identified a failed Voronoi cut whose seed
fell outside the source box. Seeds now stay inside the box; flat boundary
quantiles select another surface-variance axis. The final authoring pass and
geometry checks passed. The temporary breakpoint was removed and the debugger
detached, preserving the pre-existing exception breakpoints.

`analysis.json`, `sizing.json`, `shards-authored.json`, `pile-layering.json`,
`editor-final.json`, `normal-ground.png` and `stacked-ground.png` contain the
final checks and visual evidence. These are bounded functional probes, not a
frame-rate benchmark or final owner visual acceptance. Collision remains active
for stationary retained pieces, so their contact/query cost is not zero.
