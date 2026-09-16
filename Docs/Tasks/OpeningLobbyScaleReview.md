# Opening lobby scale drawings and independent review

Multica task: MSQ-10, a separate child of MSQ-4. The package is complete and
independently reviewed after a bounded dimension-label correction. See the
[owner handoff](../OpeningLobbyScaleReview.md). The owner explicitly approved
the identified complete package on 2026-09-14; the separate authorized next step
is [Layout03](OpeningLobbyLayout03.md). Requirements below preserve this
completed preproduction task's original scope and submission metadata.

Create a separate preproduction task under MSQ-4 following the owner's rejection
of MSQ-9. Output version: `LobbyScale-Review01`. This supplements the unchanged,
approved LobbyArt-Review02 images; it does not replace or reapprove those bytes.
No 3D editor operations or asset production are authorized by this task.

Read `Docs/VisualAcceptance.md`, `Docs/Design/GameBrief.md`,
`Docs/Tasks/OpeningLobbyConceptArt.md` and the dimensions in
`Docs/OpeningLobbyLayout02.md`. Inspect all three approved art images and
`Saved/OpeningLobby/Layout02/view-entrance-to-inner.png`,
`view-inner-to-entrance.png`, and `view-security-oblique.png` visually.

## Owner requirement and proposed interpretation

The architectural space must feel monumental and be at least twice the scale
of Layout02. Use the following exact 2x architectural option as the first
review candidate, not as dimensions recovered from photographs or owner approval.

| Element | Rejected Layout02 | Candidate for approval |
| --- | --- | --- |
| Interior length / width / central height | 30 / 12 / 9 m | 60 / 24 / 18 m |
| Central clear width | 5.6 m | 11.2 m |
| Square pier / shaft height | 1.2 / 4.2 m | 2.4 / 8.4 m |
| Bay pitch / clear longitudinal gap | 4.2 / 3 m | 8.4 / 6 m |
| Side-aisle clear width / ceiling | 2 / 4.6 m | 4 / 9.2 m |
| Lintel width / depth / underside | 1.2 / 1.4 / 4.2 m | 2.4 / 2.8 / 8.4 m |

Retain six symmetric pier pairs for this candidate. Use X from entrance -30 m
to inner end +30 m, Y across the hall, and Z up. Derive all geometry consistently
from the schedule. Do not enlarge the player or change gameplay to simulate
scale. Proposed exceptions requiring owner approval: normal human-size inner
door, checkpoint working height and detector passage. Show their old and
candidate dimensions explicitly, including entrance door leaves versus the
larger architectural glazing field. Do not silently claim these exceptions were
requested by the owner. The inner door's destination remains unspecified.

## Deliverables

Write source and review deliverables only under
`Assets/Concepts/OpeningLobby/ScaleReview01/`. Write scratch data and full logs
under `Saved/OpeningLobby/ScaleReview01/`. Keep output under 30 MB.

- An English README, a single structured dimension/camera schedule, and editable
  code-native SVG drawings with screen-readable PNG previews. Use installed
  local tools; no installation, cloud generation or new services.
- A dimensioned plan with all six pier pairs, clear aisles, doors, checkpoint,
  direction markers, camera positions and a scale bar.
- Longitudinal and transverse sections, and both end elevations; show a 1.8 m
  person and 1.72 m eye line at the same drawing scale. Include a side-by-side
  old/new cross-section at one common scale so the size change is obvious.
- A compact board pairing the approved art (unchanged, linked or embedded) with
  corresponding drawings, marking the hierarchy of massive stone, small doors
  and checkpoint, upper glazing and both continuous side aisles. Do not present
  schematic drawings as photorealistic or as proof of a future in-game view.
- A short audit of why Layout02 reads too small and a checklist for later matched
  16:9 gameplay captures at three eye-level positions. Camera estimates and
  unseen architecture are labelled. At 3.6 m/s, 60 m takes about 16.7 seconds
  without obstacles; include the old 8.3-second baseline.
- Record status `pending_owner_approval`, the exact package file hashes and
  specific decisions the owner will approve. Do not create a false approval.

Keep text legible at normal viewing size; split sheets instead of cramming a
single image. Generate the drawings from the shared dimension data and inspect
the PNGs. Check arithmetic, section/plan consistency and labelled dimensions.
Use vector primitives for technical drawings; do not regenerate approved art.

## Dispatch and acceptance

Use the Multica Spatial Designer profile: Astra/high/default, one runtime task.
The worker returns a concise English handoff and cannot edit task status,
comments, AGENTS.md, other documentation, configuration, maps or asset registry;
it cannot delegate, commit, push or start a later stage.

After the designer completes, dispatch the separate Multica Visual Reviewer
with a fresh session to inspect the package and source images. It writes only
its independent report under `Saved/OpeningLobby/ScaleReview01/Review/` and
returns concrete critical findings or a readiness verdict. Corrections go back
to the designer, then only affected criteria are rechecked. No final owner
approval is delegated to either agent. MSQ-9 remains rejected and MSQ-6/MSQ-7
remain backlog until the dimensions and subsequent 3D walkthrough are accepted.
