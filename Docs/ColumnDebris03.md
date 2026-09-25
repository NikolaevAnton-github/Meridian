# Column debris candidate — MSQ-156 direct follow-up

2026-09-26. Implemented directly under the owner's
[candidate-specific instruction](Approvals/ColumnDebris03-OwnerDirect01.json),
without a new task or independent testing. Owner visual/gameplay evaluation is
pending. No runtime performance improvement is claimed before that evaluation.

## Geometry

`Scripts/ReinforcedColumn01/merge_interior.py` derives immutable source revision
05 from revision 04. The current collection has **480 removable pieces**, down
from 644 (25.5% fewer). All **304 surface pieces** retain their exact geometry,
normals, UVs and material assignments. The **340 internal pieces become 176**.
Each union joins at most three adjacent source pieces within their original
support group; 100,874 shared internal triangles are removed. The remaining
fracture surfaces retain their original values. Fragment triangles total
1,471,054 instead of 1,571,928.

The core, its optimized collision proxy, reinforcement, 120 anchors, materials,
240 x 240 x 1800 cm envelope and 0–280 cm removable region are retained.
The native importer skips static-mesh reimport for this source so it preserves
the exact saved core collider and reinforcement. The existing flat supported
hierarchy, 50,000 strain threshold, 48 cm vendor bullet field, Nanite, convex
contacts, disabled collision strain, reinforcement collision filtering and
10 cm/s slow-debris removal threshold remain.

Collision authoring reuses the preserved revision-04 hull vertices from
`collision04.json`; merged pieces take the convex envelope of their source
hulls. This avoids regenerating detailed convexes from the dense render surface.
The first automatic hull rebuild is retained only as intermediate evidence.
Final collision has **601 hulls / 7,727 vertices**, compared with the baseline's
765 / 9,442. The maximum per hull is 37 vertices (baseline 27); merged pieces
are larger, while the total collision complexity and body count are lower.

Larger internal pieces can make individual deep breaks larger and change their
motion. This candidate intentionally does not change damage radius or impulse
to conceal that tradeoff; the owner will evaluate it.

## Visual debris

The column data asset uses the project-local `NS_RC03_ConcreteCrumbs`, derived
from the vendor's existing `NS_Breaking_Concrete`. It retains fine concrete mesh
particles and the existing dust/smoke emitters, removing the duplicate large
visual-fragment emitter. Fine debris uses GPU particles rather than Chaos bodies.
The native authoring helper recompiles the derived system; vendor assets are
unchanged.

The existing vendor break-event wiring is retained: a velocity gate and per-actor
0.2–0.3-second throttle govern bursts. There is no second effect spawned by the
adapter. The fine particle lifetime remains 0.8–1.75 seconds; this also means
already emitted particles may briefly finish after F6. No global effects budget
or new runtime destruction system is introduced.

## Implementation checks and evidence

Evidence is under `Saved/ColumnDebris03/`; `Before/` preserves the previous asset
bytes. Source revision 04 and earlier evidence are unchanged. The editable new
source is `Assets/Source/ReinforcedColumn01/ReinforcedColumn02-Candidate01/column05.json`.
`Scripts/ReinforcedColumn01/author_merged.py` performs the asset import and effect
assignment without saving the map.

- `source-check.json`: all removable pieces and anchors are closed with positive
  volume; coordinates are finite; column solid volume remains 103,679,999.9897 cm3.
  The core is unchanged and retains its previously documented seam/manifold limits.
- `DebrisBuild03.json` / `.log`: final Development Editor native build succeeded.
- `collision-final.json`: final collision counts and unchanged render geometry,
  hierarchy, initial states and anchoring after replacing the automatic hulls.
- `crumbs-build.json`: valid compiled Niagara system with GPU emitters
  ConcretePiecesSmall, Dust and SmokePuff.
- `editor-handoff.json`: cold editor readback, same 144 actors and transforms,
  unchanged map/core/reinforcement/vendor/owner files and no dirty packages.

No PIE, firing session, performance benchmark or independent review was run.
The previous [performance measurements](ColumnRuntimeRepair01.md) describe the
644-piece baseline and must not be reported as measurements of this candidate.
