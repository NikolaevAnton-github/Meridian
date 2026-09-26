# Column shape follow-up — MSQ-156

2026-09-26. Direct implementation under the owner's
[candidate-specific instruction and corrections](Approvals/ColumnShape04-OwnerDirect01.json),
without a new task or independent review. Current source: **revision 07**.

## Current revision 07: thicker angular fragments

The owner viewed revision 06 and found it better overall, but its debris too
thin and rounded. The latest instruction requires a smaller core, deeper
reinforcement and thicker, straighter fragments matching the two supplied
screenshots. It explicitly requests no further testing.

`angular_spalling.py` removes the earlier large smooth coordinate waves, restores
polygonal stone fracture rims and uses a gentler radial depth compression. The
core is reduced relative to revision 06, leaving thicker concrete behind the
cladding. Small 0.6 cm faceted relief remains on the concrete. All 16 standalone
thin stone chips are joined to their concrete backing; corresponding interior
unions are split to retain **480 physical bodies** and 120 anchors.

The 28 longitudinal bars move inward by **21 cm** on each face: their axes are
at 89.8 cm from the center, 30.2 cm behind the original outer face. Bar diameter,
tie diameter/vertical spacing and embedded ends remain. The perimeter ties and
cross-links are rebuilt to fit this inset cage. The intact column dimensions,
placement, stone appearance, damage/FX route and collision approach remain.

Source revision 07, its design and sparse collision point data are under
`Assets/Source/ReinforcedColumn01/ReinforcedColumn02-Candidate01/`. Generation and
import logs are in `Saved/ColumnShape04/Thicker07/`; `Before/` preserves revision
06 assets and scripts. No new preview meshes, captures, source validation suite,
PIE, firing session, cold-reload test or benchmark are run for revision 07 under
the owner's instruction. The authoring operation still creates/saves the assets
and their matching simplified collision. Its completion report records 600
convex hulls with 7,556 vertices and a 3,861-triangle core collision proxy; these
are authoring counts, not performance measurements. Earlier measurements below do not
describe the current candidate. Final appearance and shooting feel remain with
the owner.

## Superseded revision 06

The following records the preceding delivered version and its exact evidence.
It superseded [ColumnDebris03](ColumnDebris03.md) before the owner's next correction.

## Geometry and appearance

Source revision 06 reshapes the existing **480 removable pieces** and their
matching core interfaces together. A monotone radial deformation compresses the
removable depth with irregular relief at 62, 23 and 9 cm spatial scales. Pieces
become thinner, variably tapered flakes; deeper local pockets retain thicker
chunks. The retained concrete forms shoulders that pass around the unchanged
reinforcement. No new bodies or runtime deformation are introduced.

The fixed concrete share of the lower 0–280 cm band increases from **31.2% to
78.9%**. Sixty source rays reach the core at **4.03–42.30 cm** depth, retaining
2–6 distinct removable pieces before it. Of 1,176 samples along the interior
longitudinal bars on all four faces, 321 are fully covered, 249 cross the concrete
surface and 606 are exposed. This quantifies intermittent embedding; it is not a
visual acceptance score or a shot-count prediction.

The 240 × 240 × 1800 cm envelope, exact outer stone vertices/normals/UVs,
reinforcement, materials, placement and upper architecture are retained. The
same shared deformation moves the 120 bond anchors into the revised core;
1,680 sampled anchor positions remain inside, with 0.752 cm minimum clearance
along the test axis. The conservative continuous central prism is 102.46 cm wide.

## Physics and verification

The existing sparse revision-04 hull points receive the same deformation and
are combined through the unchanged revision-05 merge mapping. Final collision
has **600 hulls / 7,012 vertices**, maximum 32 per hull, compared with 601 / 7,727
before this follow-up. The core's separate collider is regenerated at the same
0.5 cm tolerance: **15,766 triangles**, previously 24,866. Render triangle counts
remain 171,447 for the core and 1,471,054 for fragments.

Nanite, the flat supported hierarchy, 50,000 strain resistance, 48 cm bullet
field, disabled collision strain, reinforcement collision filtering, 10 cm/s
debris removal and the lighter GPU crumbs effect are retained. These budgets
do not establish runtime performance for the new shape. No PIE, firing, F6 or
performance benchmark was run by the agent.

Evidence is under `Saved/ColumnShape04/`:

- `source-check06.json`: closed positive-volume fragments/anchors; finite data;
  total column volume 103,680,000.011 cm3. `core-seams06.json` retains the known
  collinear tessellation junctions with no unmatched geometric boundary.
- `progression06.json`: depth, support, unchanged steel/materials, normals/UVs
  and positive deformation Jacobians. The first finite-difference probe was
  unsuitable for rounded coordinates and remains in `progression06.log`; the
  passing probe differentiates the unrounded map with a smaller step.
- `asset-build06.json`, `core-collision06.json`, `editor-handoff.json`: authored
  and cold-reloaded assets, exact actor preservation and no dirty packages.
  The unchanged C++/DLL hashes reuse successful `ColumnDebris03/DebrisBuild03`.
- `Before/` preserves all previous column assets. Vendor/map/owner files,
  reinforcement asset, data asset and crumbs system remain byte-identical.

The intact, shallow, deep-front and detail native captures use the existing
camera and temporary inspection light. They are **non-gameplay authoring
previews**, with selected pieces deliberately omitted. Direct inspection shows
steel disappearing into concrete shoulders, while deeper pockets remain. Broad
angular fracture regions remain; exact vendor geometry parity is not claimed.
`authoring-deep-shape06.png` is a diagnostic duplicate of the detail view after a
failed camera command; use `authoring-deep-front-shape06.png` for the wide deep view.

The editor import exceeded the Rider bridge's 300-second response limit but
completed in the editor; it was not repeated. Temporary preview state was
discarded after matching all 144 original actors. The saved map was not rewritten.
Native setting evidence records the direct controller's actual `ultra` context
and configured `default` tier; actual tier is absent from turn metadata. This is
not represented as a verified max/default worker run. No Multica run was created.
