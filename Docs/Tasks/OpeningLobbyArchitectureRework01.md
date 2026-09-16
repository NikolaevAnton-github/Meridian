# LobbyArchitecture-Rework01: entrance and colonnade architectural design

Owner-authorized on 2026-09-14 in direct chat, following the owner's explicit
rejection of the current lobby's architectural and overall visual quality.
The owner accepted the proposal to develop and independently review two
architectural solutions before renewed 3D production. Multica task ID is recorded
in the controller handoff once created.

## Purpose and authority

Produce a convincing architectural proposal for the entrance assembly and its
connection to the last colonnade bay. The owner wants cinematic location quality:
designed depth, coherent monumental forms, meaningful secondary architecture and
creative resolution of junctions grounded in the supplied art. More surface
noise, panel seams, props, or a material-only correction does not satisfy this task.

Read `AGENTS.md`, `Docs/Design/GameBrief.md`, and `Docs/VisualAcceptance.md`.
Open the actual images, not only their descriptions:

- Primary: `Assets/Concepts/OpeningLobby/OwnerReferences01/02-EntranceSecurity.png`.
- Opposite-end consistency: `Assets/Concepts/OpeningLobby/OwnerReferences01/01-InnerEnd.png`.
- Owner's latest focused reference: `Assets/Concepts/OpeningLobby/ArchitectureRework01Inputs/OwnerEntranceDetail.png`.
- Subordinate view: `Assets/Concepts/OpeningLobby/Review02/03-SecurityOblique.png`.
- Current whole and oblique candidates: `Saved/OpeningLobby/Stage2/Architecture01/GlassReview01/Final/C2-75.png`, `C3-90.png`, and `C3-context-90.png`.

The approved art remains unchanged. `LobbyScale-Review01` and
`Docs/Approvals/LobbyLayout03-Scale01.json` remain the historical dimensional and
scale authorities. Their acceptance did not accept later architectural detail.
Use their 60 x 24 x 18 m hall, human dimensions, six pier pairs and circulation
as the starting constraints. Read `Assets/Concepts/OpeningLobby/ScaleReview01/schedule.json`
and its external approval in `Assets/Concepts/OpeningLobby/Approvals/`.

**Design freedom for this task:** the old Architecture01 requirement to reproduce
every proxy envelope within 0.05 m is NOT a limit on proposed secondary forms in
these drawings. Propose meaningful reveals, returns, piers, upper-wall setbacks,
portal jamb/header depth, sill/threshold relationships and beam/column junctions.
Retain the overall accepted hall scale. If a compelling solution needs another
dimensional change, identify it explicitly in a baseline/proposal delta schedule;
do not hide it or claim it is already approved. Distinguish visible evidence,
design interpretation and unresolved choices. This task authorizes proposals,
not modification of accepted maps, drawings, source art or approval records.

Inspect the current geometric treatment only as a diagnosed baseline:
`Scripts/OpeningLobby/architecture01_unreal.py` (`assembly`, `end_rectangle`) and
`architecture01_kit.py` (`PierCourse`, `EndPanel`, `Lintel`). Avoid making the old
procedural kit a design constraint. Do not claim all current columns are flush:
the baseline has aisles and projecting columns, but its entrance and secondary
depth relationships are underdeveloped.

## Bounded output

Package ID: **LobbyArchitecture-Rework01**.
Write only `Assets/Concepts/OpeningLobby/ArchitectureRework01/` and worker evidence
under `Saved/OpeningLobby/ArchitectureRework01/Worker/`. Preserve controller and
review folders. Use installed local tools; no DCC/editor operations, 3D scene or
mesh production, paid services, purchases, installs, new rooms/routes or narrative
facts. Code-native 2D plans, sections and axonometric/perspective drawings are
authorized. They must be identified as drawings, not in-engine render evidence.

Use the assigned `environment-reference-analysis` skill explicitly. The
`environment-architecture-production` skill may inform manufacturable detailing,
but grants no production permission. Record the actual loaded skill names/paths
in the handoff. Project copies are under `.agents/skills/`; Multica assigns the
same content. Do not create or alter skills during this run.

Deliver a compact, legible review package with:

1. An architectural reference reading. Show major solids/voids, successive depth
   planes, colonnade-to-entrance transition, soffit/upper-wall relationships and
   the monumental-window-to-human-door transition. Mark observations separately
   from inferred hidden geometry. Use original images unchanged in comparisons;
   annotations and diagrams remain separate from immutable source files.
2. Two materially different architectural variants, A and B, grounded in the
   same art and accepted overall scale. Differences must be visible in form and
   depth, not just labels, color, tiny offsets or decorative density. Develop
   portal/last-bay relationships sufficiently to judge which is stronger.
3. For each variant, an entrance elevation, dimensioned plan through the entry
   and last bay, an entrance section, and a transverse/side-bay section. Show
   primary and secondary dimensions, plane offsets, beam/column/upper-wall
   relationships, glazing/door setbacks and human silhouette/eye height.
4. For each variant, a clear spatial architectural drawing from an oblique
   approach showing the entrance and adjacent column bay together. Include enough
   whole-hall context to test the proposal against the monumental reference;
   a close-up or flat elevation alone is insufficient. Avoid unreadable overlays.
5. A concise A/B comparison with a recommendation, tradeoffs and explicit
   baseline/proposal dimension deltas. Resolve ordinary architectural junctions
   creatively; reserve owner questions for material choices between the actual
   alternatives or conflicts with accepted primary constraints.
6. One structured dimension source (`design.json` or equivalent), editable SVG
   drawings with readable PNG previews, and the local generation source. Existing
   `ScaleReview01/generate.mjs` may be inspected/reused without changing that file.
   Prefer at most eight well-composed sheets; split a sheet if readability needs
   it. Include a `README.md` mapping drawings, evidence/interpretations, A/B
   differences, reproduction, status and specific owner decisions.
7. An immutable-candidate manifest with relative paths, sizes and SHA-256; exclude
   the manifest itself from its entries and give its own digest in a sidecar.
   Status must remain `pending_independent_review` or `pending_owner_approval` as
   appropriate; neither means approval. Keep source/package/evidence under 80 MB.

## Acceptance before owner review

- Architectural richness is visible in the drawings: coherent depth hierarchy,
  credible portal assembly, purposeful secondary forms and connected colonnade,
  side aisle, end pier and upper structure. Explanatory prose cannot compensate
  for flat or unresolved drawings.
- The two variants offer a meaningful owner choice; each is substantially more
  developed than the current near-planar entrance. A recommendation cites visual
  and spatial evidence without declaring professional/owner acceptance.
- Plans, sections, spatial drawings and dimension data agree. Primary scale,
  human use, checkpoint relationships and circulation are preserved or explicit
  proposed deviations are clearly named. No hidden route or door function is
  invented. Numeric depths are proposals, not recovered measurements from art.
- Both actual primary references and the owner's crop were visually inspected.
  The result considers the whole composition and adjacent bay, not only isolated
  components. All labels are readable at normal display size.
- The designer inspects actual rendered PNGs and corrects clipping, overlap,
  inconsistent dimensions and visible drawing defects before handoff.
- An independent Multica Architecture review uses a fresh role session, forms
  its image-first judgement before reading designer conclusions, then audits
  dimensional consistency. Reviewer cannot modify the candidate or approve for
  the owner. Critical/unverified requirements require a bounded correction.

## Execution and handoff

Use the existing Multica Spatial Designer profile with task-local Astra **max**
if the live installed model catalog supports it; otherwise use the highest
supported level above high and record the actual value. Standard speed, existing
subscription, concurrency one. The controller validates and applies settings
before dispatch; do not change configuration yourself.

Return a concise English handoff with sheets, A/B distinction, design decisions,
remaining uncertainties, skills used, verification and reproduction. No other
document edits, comments/status/assignment changes, commits, pushes, registry
changes, delegation, installs or later-stage dispatch. One initial designer run
and one bounded design correction are the planned limit; after equivalent
failures change approach and provide a concrete diagnosis rather than looping.

The controller remains active through execution, actual-image inspection,
independent review and required bounded correction. Only the owner can select
and approve the identified named 2D package for subsequent 3D work. A later task
will build the chosen entrance/bay in neutral material before look development.
MSQ-6 remains incomplete; MSQ-7 remains backlog throughout this preproduction.
