# LobbyArchitecture-Rework01 / Candidate01

Status: **pending_independent_review**. This is a named 2D design candidate,
not approved architecture or in-engine evidence. The owner must select and
approve the identified package before a separate 3D production task.

The study resolves the entrance and adjoining colonnade in two ways. **A is the
designer's recommendation**: a continuous stepped portal maintains the art's
vertical emphasis and all approved glazing dimensions. **B is a substantive
alternative**: engaged piers and an 11.2 m bridge create a broad lower recess,
with the window stepping back above it. B deliberately changes the approved
upper glazing sill and height. The recommendation is not an independent verdict
or owner acceptance.

## Drawings

Each sheet has an editable SVG and a 1600 × 1200 PNG preview with the same stem.
Open the PNGs at native size; the SVGs remain scalable. Read the originals and
the spatial drawings before this recommendation when performing independent
review.

| Sheet / filename stem | Contents |
| --- | --- |
| `01-reference-reading` | Both primary images and the owner detail, embedded unchanged; separate qualitative depth diagram; visible evidence versus interpretation. |
| `02-baseline-and-constraints` | All three current GlassReview01 captures, unchanged subordinate Review02 image, diagnosis and full 60 × 24 m plan. |
| `03-A-plan-elevation` | A: entry/final-bay plan, entrance elevation, human elements, datum and depth sequence. |
| `04-A-sections` | A: centreline entrance section L, transverse pier section T, enlarged reveal P and final side-bay section S. |
| `05-A-spatial` | A: oblique approach, axial hall context and open parallel drawing of the +Y half. |
| `06-B-plan-elevation` | B: corresponding plan and elevation; explicit upper glazing delta. |
| `07-B-sections` | B: corresponding sections, upper setback and bridge return. |
| `08-B-spatial-comparison` | B: same cameras and open drawing; A/B recommendation and tradeoffs. |

`design.json` is the common dimension source. `generate.mjs` draws plans,
sections, elevations and projected planar faces directly into SVG. It emits no
mesh or DCC scene. `input-provenance.json` records the exact authoritative input
paths, sizes and SHA-256 hashes. `freeze.mjs` freezes or verifies the submission.

## Architectural reading

The primary art establishes a repeated heavy pier and beam system enclosing a
clear central axis and side aisles. At the entrance, the tall bright glazing is
framed by substantial stone, while doors and checkpoint stay human sized. The
inner-end image confirms the same monumental rhythm but uses a smaller, higher
window and a small door. That difference is intentional; the entrance glazing
has not been copied to the inner end.

| Classification | Actual source and evidence | Consequence / confidence |
| --- | --- | --- |
| Visible V1 | `OwnerReferences01/02-EntranceSecurity.png` and `01-InnerEnd.png`: visible front and side faces of repeated piers, with space and wall behind. | Keep free piers, their rhythm and the two side aisles. High confidence; current columns are not flush wall panels. |
| Visible V2 | `ArchitectureRework01Inputs/OwnerEntranceDetail.png`: the last shaft occludes the darker terminal wall; the broad entrance jamb lies farther to its right. | Distinguish free shaft, terminal shoulder and portal instead of one applied end-wall band. High confidence in occlusion/order. |
| Inferred I1 | The same crop: the dark shoulder is bounded by the beam underside and portal edge. | A recessed return is plausible, but darkness alone does not prove its depth. Medium confidence; no metre values recovered from art. |
| Visible V3 | Both primary views: the thick longitudinal beam has a distinct underside and a much taller wall zone above. | Retain the 2.4 × 2.8 m beam; design its end bearing, upper setback and side-soffit termination. High confidence in form hierarchy. |
| Inferred I2 | Beam/upper-wall junction in the crop and full entrance view. | A ledge or setback can clarify the joint. Exact section and hidden structure are not exposed. Medium confidence. |
| Visible V4 | Full entrance and detail: thin glazing frames sit beside broad stone jambs; a horizontal datum separates upper glazing from the low entrance field. | Use actual return depth, a thin inner frame and an explicit datum/spandrel. High confidence. |
| Visible V5 | Entrance image and `Review02/03-SecurityOblique.png`: station is screen-left of the detector toward the entrance. | Preserve accepted X/Y positions and human dimensions. High confidence in order; apparent size varies by lens. |
| New proposal P1 | A, sheets 03–05: stepped jamb, recessed shoulder, engaged end pier, upper setback and coffer perimeter. | All secondary metres are designed. A does not claim exact hidden geometry from the source. |
| New proposal P2 | B, sheets 06–08: broad bridge, deeper engaged end piers, upper-only portal and split side-bay coffer. | A more lateral entrance composition, requiring a glazing-schedule exception. |

The subordinate oblique clarifies checkpoint presentation but cannot override the
primary art or establish hidden returns. The source views do not establish a
single exact camera. No apparent perspective ratio has been silently converted
to an accepted dimension. The standalone qualitative diagram in sheet 01 is an
interpretation of ordering; the original embedded PNG bytes remain unchanged.

## Shared constraints and resolved junctions

The overall hall stays **60 × 24 × 18 m**. The six free pier pairs remain at
X = −21, −12.6, −4.2, +4.2, +12.6, +21 and Y = ±6.8, with 2.4 m square shafts
8.4 m high. The central floor clearance remains 11.2 m, side aisles 4 m and bay
pitch 8.4 m. Engaged terminal piers are thickened end-wall forms, not additional
free pier pairs.

The continuous beams remain between |Y| = 5.6 and 8, Z = 8.4 and 11.2. Each
variant sets the upper wall back above that beam, leaving a visible ledge. This
secondary section repeats along both colonnades and returns into the existing
inner-end wall; it is not a new floor, room or route. Above Z 11.2, the central
clear width changes from 11.2 to 12.4 m in A or 13.6 m in B. This change is
explicitly proposed, not covered by historical scale approval.

The final side-bay ceiling remains at Z 9.2 within a 0.35 m perimeter whose
underside is Z 8.4. The frame closes against the side wall, longitudinal beam,
terminal pier and first free pier face. B adds a 0.4 m cross rib at X = −25.
These are local overhead-clearance changes; floor aisle width stays 4 m. All
other side-bay ceiling fields remain at the baseline Z 9.2.

The glass and door planes stay at X = −30. The lower field stays 5.2 × 5.28 m;
the two leaves remain 1.04 × 2.64 m. A 0.6 m deep dark collar makes the small
door a legible element within the monumental field: 0.14 m side jambs and a
0.24 m head, retaining the nominal 2.08 × 2.64 m leaf envelope. Net opening,
hardware and operation remain unresolved. The floor continues at Z 0 through
the reveal; there is no raised sill or new exterior connection.

A's 0.12 m datum splice is deliberately thin and is not described as a structural
lintel. The 0.2 m zone above the tall glass meets the accepted ceiling datum;
hidden support above or behind this junction is unspecified. B's 1.8 m deep
bridge has a 0.4 m backing return to X = −30 so its spandrel closes against the
glazing datum. The broad bridge is architectural form; its structural support
has not been engineered.

The detector remains at X = −24.6, Y = −1.05 with 1.14 × 2.28 m clear opening;
the station remains at X = −24.6, Y = +0.95 with a 0.95 × 2.3 m worktop at Z 1.02.
Crossovers remain at X = ±27. At the entrance crossover, the minimum distance
from the centreline to new floor masses is 1.4 m in A and 0.8 m in B. Subtracting
the accepted capsule radius 0.34 leaves nominal margins 1.06 and 0.46 m. The
worktop front is 1.925 m from the crossover. These are analytic clearances in
the drawing data, not collision or navigation tests. Side-aisle centre routes
at Y = ±10 remain clear through the hall.

The inner door remains 1.04 × 2.18 m at X = +30, with a 2.4 × 6.2 m high window
starting at Z 11.4. Its destination and operation are still unknown. The floor
strips remain 0.64 m wide at Y = ±2.2. The human reference stays 1.8 m tall with
eye height 1.72 m and nominal walking speed 3.6 m/s (60 m in approximately
16.7 seconds, before turns or pauses).

## A/B dimension deltas

The baseline is the visible `architecture01_unreal.py` assembly: ordinary
`EndPanel` cladding is 0.01 m thick, with bands 0.02 m thick at centre X = −29.98
and front face −29.97. This diagnoses thin visible treatment; it does not
establish the hidden structural wall thickness. `PierCourse` already forms a
substantial 2.4 m square shaft, and the old kit is not a limit on this proposal.

| Item | Baseline | A | B |
| --- | --- | --- | --- |
| Main portal face / depth from pane | Near-planar visible treatment | X −28.4 / 1.6 | X −28.6 / 1.4, above Z 6 only |
| Inner reveal plane / depth from pane | Undeveloped | X −29.0 / 1.0 | X −29.2 / 0.8 |
| Main jamb face width, each | Not a developed portal | 1.7, abs(Y) 2.9–4.6 | 1.6, abs(Y) 3.0–4.6 |
| Shoulder | X −30 | X −29.6, abs(Y) 4.6–5.6 | X −29.6; lower recess reaches abs(Y) 5.6 |
| Engaged end pier face | X −29.97 | X −28.8 (+1.17) | X −27.8 (+2.17) |
| Terminal gap to first free pier face X −22.2 | 7.77 | 6.6 (−1.17) | 5.6 (−2.17) |
| Upper-wall inner abs(Y) | 5.6 | 6.2 (+0.6 setback) | 6.8 (+1.2 setback) |
| Upper central clear width | 11.2 | 12.4 | 13.6 |
| Upper glazing width / sill / head | 5.2 / 5.4 / 17.8 | Unchanged | 5.2 / 6.0 / 17.8 |
| Upper glass height | 12.4 | 12.4 | 11.8 (−0.6) |
| Entrance horizontal band width / height / depth | 5.2 / 0.12 / thin cladding | 5.2 / 0.12 / 1.6 | 11.2 / 0.72 / 1.8 + 0.4 backing |
| Final side-bay soffit | Flat Z 9.2 | Z 9.2 inset; perimeter Z 8.4 | Same, plus cross rib at X −25 |
| Threshold | Nominal Z 0 | Flush, 1.6 m reveal apron | Flush, 2.2 m recess apron |
| Hall, six free pairs, human elements, checkpoint positions, routes | Accepted schedule | Retained | Retained |

`design.json.deltas` is the structured counterpart, including the distinction
between accepted primary constraints and proposed secondary forms.

## Why recommend A

In sheet 05 the jamb runs continuously from the floor to the high window head;
the recessed shoulder gives the beam and engaged pier their own readable
termination. Sheet 03 preserves the slender bright field and the small doorway
at its base. This follows the primary image more closely than a strong transverse
bridge. It also leaves more space in the final bay and keeps the approved upper
glazing schedule.

B offers a real spatial choice. Sheet 08 shows the lower entrance as a wide
recess between deeper engaged piers, with a distinct canopy-like bridge and a
second upper plane. Its bridge and extra coffer rib strengthen lateral enclosure.
The cost is a more horizontal focal composition, less room at the crossover,
and the explicit 0.6 m glazing exception. A's cost is stronger oblique masking
of the glass by its continuous jamb. Neither option adds tertiary ornament to
substitute for mass and depth.

## Cameras, verification and reproduction

The oblique drawings use X = −14, Y = +3.5, eye Z = 1.72, yaw 192°, pitch +16°,
HFOV 106°, aspect 16:9. The wide drawing lens allows the portal head, complete
checkpoint and adjacent shaft to share one frame. It is not the gameplay FOV,
which remains 90°. The axial context uses the accepted provisional C2 pose
X = +19, Y = 0, Z = 1.72, yaw 180°, pitch 0°, HFOV 75°, aspect 16:9. Neither
camera is claimed to reconstruct the source photograph. The parallel drawings
open the +Y half at the centreline and omit enclosing ceiling/wall planes to
expose connections.

Installed Node 24.13.0 and local Google Chrome render SVG/PNG without external
packages, a DCC, a local model, network generation or paid services. Development
command from the project root was:

```powershell
node 'Assets/Concepts/OpeningLobby/ArchitectureRework01/generate.mjs' --render
```

`--render=<sheet-stem>` renders one sheet. The generator refuses to overwrite a
frozen candidate when `manifest.json` exists. For an authorized later correction,
copy the small textual generation source and `design.json` into a separately
identified candidate within the allowed package area, update its paths/ID, and
render there. Do not regenerate this immutable submission or alter old approvals.

Read-only verification of the frozen submission:

```powershell
node 'Assets/Concepts/OpeningLobby/ArchitectureRework01/freeze.mjs' --verify
```

Worker evidence is under `Saved/OpeningLobby/ArchitectureRework01/Worker/`:
`verification.json` covers retained dimensions, closed width partition, pier
spacing, glazing/band agreement, actual serialized plan depth, positive bounds,
nominal crossover/aisle clearances and unchanged source hashes.
`visual-inspection.md` records actual PNG inspection and presentation corrections.
The designer's visual inspection is separate from the controller's required
fresh independent image-first review. No engine, structural or owner acceptance
is inferred from these checks.

Loaded skill: **environment-reference-analysis** at
`.agents/skills/environment-reference-analysis/SKILL.md`. No other skill was
applied. The controller's recorded task configuration is GPT-6 Astra, max
reasoning, default service tier, subscription authentication, concurrency one;
the designer did not modify runtime settings.

## Decision gate

The controller must inspect the actual images and obtain a fresh independent
review of this manifest. After any required bounded correction, the owner must
choose A or B and approve the identified named package, including the secondary
depth/soffit/upper-wall deltas and, if choosing B, the upper glazing exception.
Door functions, off-camera connections, hidden structure and material response
remain unresolved. No new narrative fact, route or production authorization is
introduced. MSQ-6 remains incomplete and MSQ-7 remains backlog; this worker made
no task, status, comment, registry, commit or push changes.

`manifest.json` lists relative project paths, bytes and SHA-256 for the submitted
package and selected worker evidence, excluding itself and its digest sidecar.
`manifest.sha256` identifies the manifest. Approval must refer to that digest;
the candidate's pending status is not approval.
