# Column runtime repair — MSQ-156 follow-up

2026-09-26. Direct owner-authorized repair, with no new task or independent
reviewer, as explicitly requested. Owner visual/play acceptance remains separate.
The earlier rifle/Nanite repair is retained; this revision addresses sustained
physics cost and debris trapped inside the reinforcement.

## Current implementation

The 644 removable pieces, 120 anchors, fracture geometry, materials, reinforcement,
240 x 240 x 1800 cm envelope and placement are unchanged. Nanite, convex fragment
contacts, 50,000 local strain resistance and the vendor's 48 cm bullet field remain.
Collision-generated strain stays disabled only for this column data asset.

- Embedded reinforcement ignores the Destructible collision channel. Fragments
  initially enclose the rods; resolving those penetrations trapped them and kept
  the solver active. Reinforcement still blocks the existing weapon queries and
  player collision. The rule runs at BeginPlay for every instance and F6 replacement.
- The core uses a separate `SM_RC01_CoreCollision` mesh: **24,866 triangles** instead
  of sending the full **171,447-triangle** render surface to physical contacts.
  Geometry Script simplifies with a **0.5 cm geometric tolerance**. The visible
  source mesh, its normals/materials, Nanite and full render fallback are unchanged.
  This collision proxy also supplies core queries. The source core is not a closed
  manifold; the proxy retains that pre-existing limitation.
- Slow-moving debris uses a **10 cm/s** removal threshold instead of 1 cm/s, with
  the existing 3–5 second sleep interval and 1–2 second removal animation. Small
  residual motion no longer keeps debris alive indefinitely.
- `Scripts/ReinforcedColumn01/optimize_collision.py` regenerates the core collider;
  the current progressive authoring route calls it after building the source.
  The native authoring defaults reproduce the new debris threshold.

Fragment hulls were already economical (9,442 vertices in 765 hulls, maximum 27
vertices per hull) and are preserved. An attempted hull rebuild increased their
complexity; it was discarded without saving. Vendor assets and map bytes are unchanged.

## Measured behavior

Evidence: `Saved/ColumnPerformance02/`. Measurements use the same local PIE/editor,
normal game speed, background throttling disabled, and retained rendering settings.
The 8.33 ms floor is the existing approximately 120 FPS limit.

| Scenario | Active median / p95 | Settled median / p95 |
| --- | --- | --- |
| Before, all 644 pieces released | 106.01 / 147.17 ms | 79.80 / 96.79 ms |
| Repaired, same 644-piece release | 18.08 / 21.66 ms | 8.33 / 8.44 ms |
| Same repair after cold editor restart | 14.23 / 20.56 ms | 8.33 / 8.35 ms |
| Four instances, 120 pieces each, simultaneous | 11.17 / 14.41 ms | 8.33 / 8.34 ms |
| 30 real rifle shots across the front | 8.33 / 9.41 ms | 8.33 / 8.42 ms |

The full-release scenario applies strain directly to known pieces to create a
repeatable worst-case physics load. The rifle scenario uses normal player input,
Enhanced Input and finite projectile sweeps: 29 column hits release 108 pieces;
all 120 anchors stay fixed. By the end of its 37-second observation, no detached
visible/moving fragments remain. `rifle-front30-settledaim.png` shows the exposed
reinforcement and fallen debris. Temporary test copies were removed without saving
the map; all 144 original editor actors remain.

These are bounded local measurements, not a guarantee for an arbitrary number of
simultaneously destroyed columns. The first background-throttled probe and the
first rifle probe (camera not settled, zero column hits) are excluded. Failed and
intermediate diagnostics remain in the evidence directory rather than being replaced.

`PerfBuild02.json` identifies the final native build. Cold verification and F6
readbacks are recorded alongside the performance traces. `preserved-files.json`
checks the original map, data asset, reinforcement and unrelated owner files.
The previous direct-repair evidence and review remain under `Saved/ColumnRepair01/`;
that historical review is not represented as reviewing this owner-waived revision.
