# LobbyFunctional-Revision01 / Candidate01

Five dimensioned 2D proposal sheets implement the owner's bounded Walkthrough01
direction. Status: **pending_independent_review**. This package does not authorize
3D production. Exact new dimensions and the central-passage interpretation of
the checkpoint await named-package owner approval after fresh independent review.

## Read the drawings

| Sheet | Evidence |
| --- | --- |
| `01-plan-circulation.svg` / `.png` | Whole hall, four infills and doors, checkpoint branches, closed old crossovers, adjacent open bays and both longitudinal aisles |
| `02-entrance-checkpoint.svg` / `.png` | Wall-to-wall plan, two net lane widths, front elevation, human/capsule scale and longitudinal section |
| `03-inner-elevator.svg` / `.png` | Complete inner-end elevation, opaque sign reservation, elevator plan and vertical reveal section |
| `04-room-faces.svg` / `.png` | Both mirrored entrance faces and both mirrored inner faces; detailed door recess and transverse enclosure section |
| `05-spatial-context.svg` / `.png` | Entrance and inner-end perspective drawings, whole-hall context, annotated current-capture crops |

All dimensions are metres. Full plan: +X right, +Y up. Entrance is X -30,
inner end X +30. Checkpoint plan: +Y left, +X down. Room-face elevations use
increasing X as their horizontal abscissa, with viewing normals explicitly
identified; paired faces are mirrored in the actual plan. Perspective cameras
are recorded in `design.json` and on sheet 05. They are drawing cameras, not
reconstructions of the art's unknown lens. Human height 1.80, eye 1.72, capsule
radius 0.34, capsule half-height 0.88, assumed walking speed 3.6 m/s are retained.

`design.json` is the common dimensional source. `shared` preserves historical
approved data, including superseded checkpoint/inner-end entries for comparison.
Active `rooms`, `checkpoint`, `elevator` and `routes` override those entries;
`retained_A` remains the selected A specification. Never implement the historical
`shared.station`, `shared.detector`, `shared.inner` or old crossovers as the new design.

## Evidence to proposal

Actual images were opened before developing the proposal. No new image generation
or DCC/editor operations were used. Unchanged source packages are referenced,
not copied. Two current captures are embedded in sheet 05 as annotated crops.
`input-provenance.json` records exact file sizes and SHA-256 values.

| Source / classification / confidence | Readable relationship | Design consequence |
| --- | --- | --- |
| OwnerReferences01/02-EntranceSecurity.png; visible, high | Thin tall glazing sits between heavy jambs; low security elements leave the main vertical field dominant | Retain A portal, glass and transom. Keep checkpoint desk at Z 1.02 and lane heads at Z 2.58 |
| OwnerReferences01/01-InnerEnd.png; visible, high | Repeated piers frame a central inner door and high window; lateral openings sit behind the colonnade | Retain pier/beam hierarchy. Latest owner direction replaces the central door/window and terminal voids |
| ArchitectureRework01/03-A-plan-elevation.png and 04-A-sections.png; approved drawing evidence, high | Main portal face -28.4, reveal -29.0, glazing -30; end pier face -28.8; beam Z 8.4..11.2; upper setback 0.6 | New entrance infills start at -28.8 and stop at first free-pier face -22.2; no flattening or relocation of portal/shoulder |
| ArchitectureRework01/05-A-spatial.png; approved drawing evidence, high | Portal, recessed shoulder, beam and side soffit form distinct depth layers | Preserve these masses; cap infills under the beam and leave the side-aisle soffit pocket intact |
| Current Worker/C2-75.png and C3-context-90.png; visible, high | Actual A portal projects from glazing, beam meets pier, terminal bay is currently open | Sheet 05 marks the observed junctions. New blind hall walls close only the terminal colonnade band |
| Current Worker/C1-90.png; visible, high | Small old door and high glazing remain in the current neutral candidate | Replace 1.04 x 2.18 door/frame and all 2.4 x 6.2 high glazing/grid; retain opaque wall around them |
| Hidden wall assembly / off-camera returns; inferred, medium | Art and neutral captures cannot establish construction thickness or hidden structure | The 0.36 wall, 0.24 door recess and 0.60 elevator reveal are explicit proposals |
| Walkthrough01 owner direction; authoritative requirement | Four terminal enclosures, inverse door orientation, two lateral checkpoint lanes, large elevator and no high window | Exact active dimensions below are new proposals, not measurements extracted from images |

Primary form remains the 60 x 24 x 18 hall, main axis, six paired free piers,
continuous beams and tall A entrance. Secondary additions are substantial but
quiet infill faces, recessed door returns and a broad elevator collar. Tertiary
detail is limited to frame/leaf division. No new ornament, materials, atmosphere,
name or logo is proposed.

## Four terminal enclosures

| ID | X extent | Y extent | Door face / outward normal | Opposite face | Door centre X / visible leaf Y |
| --- | --- | --- | --- | --- | --- |
| E+ | -28.80..-22.20 | +5.60..+8.00 | Aisle / +Y | Hall blind | -25.50 / +7.76 |
| E- | -28.80..-22.20 | -8.00..-5.60 | Aisle / -Y | Hall blind | -25.50 / -7.76 |
| I+ | +22.20..+29.97 | +5.60..+8.00 | Hall / -Y | Aisle blind | +26.085 / +5.84 |
| I- | +22.20..+29.97 | -8.00..-5.60 | Hall / +Y | Aisle blind | +26.085 / -5.84 |

Each envelope is 2.40 gross width and 8.40 high, with 0.36 visible wall/end-cap
thickness. Its cap reaches the existing beam underside at Z 8.40. Entrance
length is 6.60; inner length 7.77. These lengths and wall thicknesses are the
controller/designer interpretation of room-like volumes, not owner-specified
metres. External wall faces are flush with pier band limits to preserve the
full 11.20 central width and 4.00 aisles. End caps abut engaged/free-pier or
inner-wall faces without floor-level slots. Wall tops meet the beam underside;
retained upper setback and soffit geometry are untouched.

Each closed door has a nominal 1.20 x 2.40 face/opening, 0.12 frame width,
0.24 recess from access-side wall to visible leaf face, 0.06 leaf thickness,
and flush Z 0 threshold. Frames have actual plan and vertical depth. Entrance
doors imply service access; inner doors imply stair access. The pale interior
plan tint is an unknown zone. No room usability, staircase fit, engineered
stair envelope, stair opening, interior floor plan or door operation is claimed.

## Checkpoint and baseline deltas

The central control line stays at X -24.60 and spans Y -5.60..+5.60. All units
share X -25.05..-24.15. In increasing Y order, the exact floor-level partition is:

| Y interval | Element | Width |
| --- | --- | --- |
| -5.60..-5.40 | Outer post contacting terminal wall | 0.20 |
| -5.40..-3.90 | Negative-side walkable lane, centre -4.65 | 1.50 net |
| -3.90..-3.70 | Inner post joined to desk | 0.20 |
| -3.70..+3.70 | Joined desk/barrier composition | 7.40 |
| +3.70..+3.90 | Inner post joined to desk | 0.20 |
| +3.90..+5.40 | Positive-side walkable lane, centre +4.65 | 1.50 net |
| +5.40..+5.60 | Outer post contacting terminal wall | 0.20 |

Posts have 2.40 clear height and 0.18 heads, overall 2.58. Joined desk/barrier
top is Z 1.02 with a 0.06 slab, no undercut, step or separate floating unit.
Each lane has 0.41 lateral margin per side for a centered 0.68 diameter capsule,
and 0.64 height above a 1.76-high capsule. These are drawn clearances, not a
certification of operation, accessibility or security control. The side aisles
remain deliberately open, so this does not claim a secured full-building boundary.

| Item | Current ReworkA01 baseline | Candidate01 proposal / scope |
| --- | --- | --- |
| Hall / piers / aisles | 60 x 24 x 18; six pier pairs at X -21,-12.6,-4.2,4.2,12.6,21, Y +/-6.8; 2.4 square x 8.4 high | Unchanged; 11.2 central and 4.0 aisle clear widths retained |
| A entrance and overhead | Portal depth 1.6; shoulder face -29.6; upper setback 0.6; beam 2.4 wide x 2.8 deep, Z 8.4..11.2 | Unchanged; side soffit Z 9.2 and entrance perimeter Z 8.4 retained |
| Terminal bands | Open passages below beams | Four envelopes with dimensions above; no new usable interior |
| Terminal crossovers | X +/-27 | Intentionally closed; adjacent open bay crossings at +/-16.8 |
| Detector / lane | One at X -24.6, Y -1.05; 1.14 x 2.28 clear; 0.55 depth | Two at same X, Y +/-4.65; 1.50 x 2.40 clear, 0.90 depth. Clear width +0.36, height +0.12, depth +0.35 |
| Station | Y +0.95; 2.30 top width, 0.95 top depth, Z 1.02 | Centred joined 7.40 width, 0.90 depth, Z 1.02; width +5.10, depth -0.05. Historical single station replaced |
| Inner door | 1.04 x 2.18; nominal frame 1.22 x 2.32 | Closed elevator opening 3.60 x 4.20, outer collar 4.40 x 4.60. Opening +2.56 W / +2.02 H |
| Elevator depth | Small historical door/frame | Collar front X 29.40 to visible leaf plane X 30, reveal 0.60. Leaf backing alone reaches 30.06; no shaft or cab envelope |
| Inner high window | 2.40 x 6.20, Z 11.40..17.60 with mullions/transoms | Entire assembly removed and opening made opaque; no retained translucent remnant |
| Future sign | None approved | 6.00 W x 6.00 H reservation, Y +/-3, Z 11.40..17.40; flush opaque wall. Dashed line is annotation only, not built trim |

The new elevator is one centred assembly with two closed leaves indicated by a
meeting line. Neither its generous opening nor the diagram leaf backing states
a cabin dimension, capacity, shaft, destination or operating mechanism.

## Routes and required later verifier changes

The old crossover contracts at X +/-27 must be retired only for the scoped new
candidate when 3D is authorized; the historical tests and evidence remain valid
for the old map. Replace them with transverse routes through the adjacent open
bays X -19.8..-13.8 and +13.8..+19.8. Centre each crossing at X +/-16.8, giving
3.00 centre-to-pier-face distance and 2.66 nominal capsule margin.

Both aisle centre routes at Y +/-10 remain clear, nominal side margin 1.66.
The entrance central route splits from (-29.3,0) through (-26.6,+/-4.65), passes
the lanes to (-23.3,+/-4.65), and rejoins at (-21,0). Continue along the central
axis to (28.8,0). Service-door approaches branch from each aisle; inner-door
approaches branch from the central axis. Route tests end 0.65 before the wall
face at closed room doors and do not enter them. The short orange plan arrows
identify the door's access face, not a passage through its leaf.

`design.json.routes.polylines` and Worker `verification.json` record 11 scoped
route polylines and their lengths/times. Sampling every <=0.025 m subtracts
half the sample step from the minimum distance as a conservative continuous
clearance bound. The nominal 60 m hall traverse is 16.7 s at 3.6 m/s; actual
checkpoint and door approaches add distance. This is analytic 2D clearance,
not engine collision or player movement evidence. Later implementation must
check real capsule movement through both lanes, both alternate bays, both
aisles and all four closed-door approaches.

## Verification and remaining decisions

Author inspection opened all final PNG sheets after correcting misplaced arrows,
section/title overlap, encoding and perspective face ordering. The reused local
browser audit reports no overlapping or out-of-page text. `verify.mjs` records
201 passing checks, including all 117 historical ReworkA01 candidate entries,
the historical A drawing manifest entries, original art fingerprints, lane
closure, retained scale, door orientation and 9,865 route samples.

This is author verification. Fresh independent Multica review is still required
and was not performed or dispatched by this worker. Review must inspect actual
references and candidate images, report PASS/FAIL/UNVERIFIED per task criterion,
and precede the owner's approval of this exact manifest.

Owner decisions remain: approve or revise these exact enclosure/door/checkpoint/
elevator dimensions; confirm the 11.2 m central-only checkpoint interpretation;
accept the deliberate terminal crossover closures; accept the opaque sign
reservation size. Room/stair interiors, cab/shaft engineering, hardware and
operation, branding, final material/lighting/atmosphere remain deferred.

## Local reproduction and immutable identity

Node v24.13.0 and the already installed local Chrome renderer were used. No
installation, paid service, model generation, network lookup or project editor
connection was required. `generate.mjs` is the self-contained assembled drawing
source. Its component sources and `assemble.mjs` are retained for editing.
Drafting primitives, retained A geometry, perspective projection, browser render,
text audit and freeze patterns come from ArchitectureRework01. The local face
ordering correction prevents rear leaves appearing through blind walls; it
emits SVG polygons only.

Before freezing, commands from project root were:

```powershell
node Assets/Concepts/OpeningLobby/FunctionalRevision01/assemble.mjs
node Assets/Concepts/OpeningLobby/FunctionalRevision01/generate.mjs --render
node Assets/Concepts/OpeningLobby/FunctionalRevision01/audit-text.mjs
node Assets/Concepts/OpeningLobby/FunctionalRevision01/verify.mjs
node Assets/Concepts/OpeningLobby/FunctionalRevision01/freeze.mjs
```

The manifest stores project-relative paths, byte sizes and SHA-256 values for
package/evidence files. Its digest is in `manifest.sha256`. Generation, assembly,
text audit and repeat freeze refuse to overwrite an already frozen candidate.
Do not remove that guard from this package. An authorized future correction
needs a separate named identity and write scope from the controller.

Read-only verification after freezing:

```powershell
node Assets/Concepts/OpeningLobby/FunctionalRevision01/freeze.mjs --verify
```

Worker evidence is in `Saved/OpeningLobby/FunctionalRevision01/Worker/`. Only
these two authorized directories were written. Issue status/comments, project
config, assets, skills, registry and historical candidates were not edited;
no commits, pushes, delegation or owner-approval action was taken.
