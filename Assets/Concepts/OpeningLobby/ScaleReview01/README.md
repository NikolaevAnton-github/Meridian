# LobbyScale-Review01

Status: **pending_owner_approval**. Designer submission for independent visual
review, not owner acceptance or permission for 3D production. The owner requires
monumental architecture at least twice Layout02's scale. This package proposes
the specified exact 2x option, with explicitly identified human-size exceptions.
Dimensions are design estimates, not measurements recovered from photographs.

## Review files

Each numbered sheet has an editable SVG and a screen-readable PNG of the same
name. Open the PNGs at their native width of 1600 pixels; sheet 08 is taller.

| Sheet | Contents |
| --- | --- |
| `01-plan` | Six symmetric pier pairs, dimensioned envelope, clear aisles, doors, checkpoint, circulation, section directions, C1–C3 and scale bar |
| `02-longitudinal` | Section A, projected pier rhythm, lintel, end glazing, height and eye datum |
| `03-transverse` | Section B through X=4.2; clear spans, pier and lintel, side ceilings, human scale |
| `04-inner-elevation` | Interior inner end, small opaque door and high glazing |
| `05-entrance-elevation` | Interior entrance, doubled glazing fields, proposed small leaves and projected checkpoint |
| `06-checkpoint` | End circulation detail and enlarged equipment elevation at human scale |
| `07-common-scale` | Rejected Layout02 and candidate sections side by side, both 30 px/m |
| `08-art-board` | Three unchanged approved images paired with the corresponding proposed relationships |

`schedule.json` is the single structured dimension/camera source.
`generate.mjs` produces the drawings and arithmetic evidence using local Node
and Chrome. `manifest.json` records every package file's exact SHA-256 except
itself. `manifest.sha256` identifies the manifest without a circular self-hash.
The later approval must name that digest, not just this directory name.

## Dimensional interpretation

| Architectural element | Rejected Layout02 | Candidate |
| --- | --- | --- |
| Length / width / central ceiling | 30 / 12 / 9 m | 60 / 24 / 18 m |
| Central clear width | 5.6 m | 11.2 m |
| Square pier / shaft | 1.2 / 4.2 m | 2.4 / 8.4 m |
| Bay pitch / clear gap | 4.2 / 3 m | 8.4 / 6 m |
| Each side aisle clear width / ceiling | 2 / 4.6 m | 4 / 9.2 m |
| Lintel width / vertical depth / underside | 1.2 / 1.4 / 4.2 m | 2.4 / 2.8 / 8.4 m |
| Upper entrance glazing W × H; sill | 2.6 × 6.2 m; Z 2.7 | 5.2 × 12.4 m; Z 5.4 |
| Lower entrance glazing field W × H | 2.6 × 2.64 m | 5.2 × 5.28 m |
| Inner upper window W × H; sill | 1.2 × 3.1 m; Z 5.7 | 2.4 × 6.2 m; Z 11.4 |
| Parallel floor strips width; centres | 0.32 m; Y ±1.1 | 0.64 m; Y ±2.2 |

X runs from entrance −30 to inner end +30; Y runs across the hall and Z up.
The pier centres are X −21, −12.6, −4.2, +4.2, +12.6, +21, at Y ±6.8.
The width closes exactly: 4 + 2.4 + 11.2 + 2.4 + 4 = 24 m.
Pier-to-end-wall clear length is 7.8 m. Aisle route centres are Y ±10;
crossovers at X ±27 remain outside the pier rows and checkpoint footprint.
Projected elements in section A are beyond its Y=0 cutting plane. The end
elevations omit foreground piers; their dark vertical end bands are proposed
stone facing aligned with the pier rows. Mullion subdivisions are schematic.

## Explicit exceptions requiring owner approval

These are designer proposals, not requests previously made by the owner.

| Element | Old | Candidate and qualification |
| --- | --- | --- |
| Inner opaque door leaf W × H | 1.04 × 2.18 m | Retain 1.04 × 2.18 m; frame 1.22 × 2.32 m. Destination unspecified. |
| Entrance operable leaves | Not defined as operable assets. Two central schematic panels inferred as nominal 0.65 m each between mullion centre lines; lower field height 2.64 m. | Propose two nominal 1.04 × 2.64 m leaves, total 2.08 m. Fixed sidelights and overlight occupy the rest of the 5.2 × 5.28 m lower field. This is an additional human-size exception, not an exact doubling of old leaves. |
| Detector clear W × H | 1.14 × 2.28 m | Retain; outer frame 1.46 × 2.42 m, depth 0.55 m, posts 0.16 m, header 0.14 m. |
| Station body X × Y × Z | 0.85 × 2.2 × 0.96 m | Retain body dimensions. |
| Station worktop X × Y; top height | 0.95 × 2.3 m; Z 1.02 | Retain. Its 0.06 m thickness makes body height and working height distinct. |
| Checkpoint local spacing | Detector Y −1.05; station Y +0.95; X −12.3 | Retain local Y and footprint to keep a compact group; move X to −24.6. Only the group's longitudinal location doubles. |

Door swings, clear openings after frames, hardware, monitors, external access
and functional screening remain unresolved. The old decorative inner leaf had
a 0.01 m floor offset; drawings use nominal floor datum. No character scale,
movement or gameplay change is proposed. Retained capsule dimensions are
radius 0.34 m and half-height 0.88 m; the detector has 0.46 m nominal total
width clearance around its diameter. This arithmetic is not a collision test.

## Why Layout02 reads too small

The designer inspected all three approved PNGs and all three requested final
Layout02 PNGs. Approved image hashes were checked against Review02's existing
approval record. The art board embeds their original PNG bytes without changes;
display scaling does not alter those bytes. The source pair controls architecture;
the supplement controls the entrance/checkpoint relationship.

In the art, massive piers, deep continuous beams, upper glazing and narrow
continuous side aisles dominate the small doors and screening equipment. In
the rejected gameplay captures, the 4.2 m shafts and 4.6 m side ceilings occupy
much more humanly familiar proportions. A 1.8 m person is 43% of an old shaft's
height but 21% of the candidate shaft; the central ceiling rises from five to
ten human heights. This directly addresses scale hierarchy while preserving
the architectural width/height ratio. Uniform doubling alone does not prove
that perspective composition, material mass or monumentality will match the art.

The 30 m old hall also compresses travel: at the unchanged 3.6 m/s, unobstructed
end-to-end time is **8.3 s**. The 60 m candidate takes **16.7 s**. These are
distance/speed estimates, excluding acceleration, doors, turns and obstacles;
they are not timed gameplay results.

The old end captures are 1520 × 1181 while the art is approximately 16:9.
Their framing cannot support a matched visual verdict. The old security close-up
crops the adjacent pier and continuous aisle, losing the very mass-to-equipment
relationship that the supplement shows. Flat placeholder stone, lighting pools
and floor repetition also weaken the source's apparent material mass; this is a
visual observation, not a material-production instruction for this task.

The candidate's small inner door and retained checkpoint may look very small
against the doubled span. That is intentional for review, not a claim of exact
reference reconstruction. Roof build-up, wall thickness, unseen architecture,
off-camera connections and structural feasibility are unverified. No unshown
door destination or new narrative fact is established.

## Later matched gameplay capture checklist

Only after independent review and explicit owner approval of an identified
package may a separate worker implement it. Later capture all three positions
at 1920 × 1080, Z=1.72 m, pitch/roll=0, neutral readable lighting and the same
display settings. Poses and reference FOVs below are initial design estimates.

| View | XYZ, metres | Yaw | Estimated reference horizontal FOV | Also capture |
| --- | --- | --- | --- | --- |
| C1, entrance toward inner end | −19, 0, 1.72 | 0° | 75° | Same pose, unchanged gameplay 90° |
| C2, inner toward entrance | +19, 0, 1.72 | 180° | 75° | Same pose, unchanged gameplay 90° |
| C3, offset security view | −14, +3.5, 1.72 | 180° | 90° | Same unchanged gameplay view; record that the two FOVs coincide |

- Record actual project/map identity, camera transform, eye height, FOV and FOV
  convention, resolution/aspect, movement speed and capture filename. Reference
  focal lengths are unknown; log adjustments without claiming reconstruction.
- C1: show the small inner door, upper window, pier rhythm and both aisles. The
  initial pose has five pairs ahead and the first pair behind; verify actual framing.
- C2: show tall entrance glazing, leaves and complete checkpoint, station on
  screen-left of detector, with both continuous aisles legible.
- C3: show the entire checkpoint, adjacent +Y pier, lintel and the side-aisle
  connection together. Its offset makes the checkpoint screen-right and the
  +Y pier screen-left. Reject a replacement close-up, overhead plan or cropped image.
- Compare against each original approved view, without cropping reference or
  candidate to hide missing relationships. Distinguish framing failure from
  dimension failure; correct the documented estimate if necessary.
- Check primary implemented dimensions against the approved schedule with a
  proposed 0.05 m tolerance; record approved deviations. Reuse the existing route
  and technical verifier. Require an independent visual verdict and owner walkthrough.

## Review and approval decisions

Independent visual review is **not performed by this designer**. A separate
Visual Reviewer session must inspect the actual source images and rendered
drawings and return pass/fail/unverified for scale hierarchy, spatial proportions,
pier rhythm, entrance, inner end, security relationship and circulation. Its
report belongs under `Saved/OpeningLobby/ScaleReview01/Review/`. Critical or
unverified criteria block owner handoff. The designer cannot dispatch that run.

After that review, the owner must identify the package manifest hash and decide:

1. Exact architectural dimensions, six pairs and their spacing.
2. Each human-size exception above, including entrance leaves, station footprint
   and retained local checkpoint spacing.
3. Doubled glazing/floor strips, proposed upper infill and end-wall composition.
4. Circulation, capture estimates and proposed 0.05 m implementation tolerance,
   keeping unseen connections and the inner door destination unresolved.

Approval of LobbyArt-Review02's unchanged images remains separate. This submission
does not reapprove them or accept Layout02. MSQ-9 remains rejected; MSQ-6/MSQ-7
remain backlog. No status, comments, source art, other project documents, DCC
state, maps, configuration or asset-registry data were modified by this worker.

## Reproduction and evidence

From the existing project root: `node Assets/Concepts/OpeningLobby/ScaleReview01/generate.mjs --render`.
This uses installed Node v24.13.0 and Chrome headless, sequentially, with a
dedicated transient profile under the assigned Saved directory. It starts no
service and uses no paid API, cloud generation, install or DCC operation.
The generator verifies approved image hashes and records 38 arithmetic checks.
The designer's visual inspection record and full render logs are under
`Saved/OpeningLobby/ScaleReview01/`. Reproduction changes package bytes and must
be followed by visual inspection and manifest refresh; it cannot preserve an
old approval automatically. The submitted review package is below 30 MB.
