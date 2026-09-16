# Environment visual acceptance

Current lobby disposition, 2026-09-16: all remaining lobby tasks and pending
owner-review gates are closed by owner deferral until a new post-gameplay list.
See [the owner decision](Approvals/LobbyDeferred01-OwnerClosure01.json).
Prior scoped acceptances and review evidence are preserved. Historical lobby
authorization/status wording below does not authorize further dispatch.

## Current architectural recovery direction, 2026-09-14

The owner subsequently rejected the current Architecture01 result's overall
architectural quality: weak entrance depth, underdeveloped column/wall/soffit
relationships and insufficient cinematic design. The owner authorized
`Docs/Tasks/OpeningLobbyArchitectureRework01.md`, a separate skills-assisted 2D
design task with two entrance/colonnade variants and independent review.
This is design authorization, not approval of new geometry. The original art
and scale approvals retain their scoped historical meaning. Proposed secondary
architecture may depart from old proxy envelopes when explicitly dimensioned;
the new task must identify primary-constraint conflicts rather than silently
flattening the design to fit them. No renewed 3D production precedes approval of
the named package. Overall architectural likeness is a separate requirement;
local defect corrections and prior material passes cannot establish it.

MSQ-12's `LobbyArchitecture-Rework01/Candidate01` subsequently passed independent
MSQ-13 drawing-stage review. The owner then selected A and explicitly authorized
max-effort execution. See the [external decision](Approvals/LobbyArchitectureRework01-VariantA.json)
and [bounded neutral assembly task](Tasks/OpeningLobbyArchitectureReworkA01.md).
That task uses Astra/max/standard for production and independent review as a
task-specific exception to the historical model guidance below. Owner acceptance
of the resulting 3D quality remains pending.

The remaining text records the established scale and prior review workflow.

The owner rejected MSQ-9 after walking through Layout02: its architectural
scale lacks the intended monumentality and must be at least twice as large.
On 2026-09-14 the owner approved the exact LobbyScale-Review01 dimensioned
package, including its human-size exceptions; see the
[approval record](../Assets/Concepts/OpeningLobby/Approvals/LobbyScale-Review01.json).
Steps 1-3 below are complete for that manifest. The next authorized stage is
[Layout03 neutral blockout](Tasks/OpeningLobbyLayout03.md), followed by steps 4-5.
Layout03/Correction01 subsequently passed technical and independent visual
review on 2026-09-14. The owner then explicitly accepted its in-game scale,
deferred detail assessment and authorized continuing. The
[scoped decision](Approvals/LobbyLayout03-Scale01.json) closes the neutral
scale gate for that identified map and authorizes
[MSQ-6 architecture/material production](Tasks/OpeningLobbyArchitecture01.md).
Detail quality and final atmosphere require their subsequent reviews and owner
decisions. See [the handoff](OpeningLobbyLayout03.md).
LobbyArt-Review02 remains the approved visual reference. Neither Layout02 nor
its estimated dimensions are accepted. Preserve both rejected prototypes and
their historical technical evidence.

## Required sequence

1. A spatial designer inspects the actual approved art and prepares one named
   package containing a dimensioned plan, longitudinal and transverse sections,
   both end elevations, a 1.8 m human silhouette and 1.72 m eye line. Show room,
   pier, bay, aisle, lintel, glazing, door and checkpoint dimensions, circulation,
   camera positions, and estimated walking time. Distinguish owner requirements,
   design estimates and unresolved decisions. Pair the drawings with the art.
2. An independent visual reviewer uses a separate session and does not edit the
   candidate. The reviewer inspects the source images and rendered drawings,
   checks dimensions against the common source data, and reports pass/fail/
   unverified for scale hierarchy, spatial proportions, pier rhythm, entrance,
   inner end, security relationship and circulation. Each finding cites a
   specific view or dimension. Critical or unverified criteria block handoff.
3. The owner explicitly approves the identified art-and-dimensions package,
   including any proposed exceptions to the scale instruction. Draft drawings
   are review material; they do not authorize 3D layout or asset production.
4. One Multica implementation worker builds only that approved spatial design.
   Inspect an early neutral-light blockout before detailed materials or models.
   Compare all three approved directions using matched aspect ratio and recorded
   eye height, camera pose and FOV. Also inspect the unchanged gameplay FOV.
   Do not substitute a cropped checkpoint close-up or overhead plan for the
   required checkpoint/column/aisle view. Reference focal length remains an
   estimate; record it instead of claiming exact camera reconstruction.
5. Reuse the existing technical verifier. Require separate technical and visual
   verdicts, then owner walkthrough acceptance. A route passing, an agent's
   self-assessment, or a request to continue does not accept spatial design.

Use a proposed 0.05 m tolerance for implemented primary dimensions, checked
against the approved schedule; owner-approved deviations must be recorded.
Visual composition remains a judgement with evidence, not a guarantee derived
from dimensions or an automated image-similarity score. A role name alone does
not establish professional design competence or independent model judgement.

## Model and execution policy

On 2026-09-15 (owner local date), the owner requested another maximum-reasoning
trial for the next lobby task. Spatial Designer, Environment Artist and Visual
Reviewer were configured as Astra/max/standard, including the matching native
`model_reasoning_effort="max"` argument. This next-task-only exception overrode
the baseline below. Concurrency one and subscription authentication were retained.
The bounded Painter stone sample, independent review and correction/recheck are
complete at the owner material-direction gate; see
[the exact review record](OpeningLobbyPainterStone01Review.md). All three profiles,
original instructions and native arguments were restored to the saved high
baseline in `Saved/OpeningLobby/NextTaskMax01/Controller/`. Restoration evidence is
`Saved/OpeningLobby/PainterStone01/Controller/profiles-restored.json`. The earlier
setting change itself did not dispatch a run or grant visual acceptance.

Use GPT-6 Astra with high reasoning and standard speed for spatial design and
independent visual review. Use medium for routine implementation from an
approved, dimensioned specification; raise to high for unresolved architecture
or difficult implementation. Do not silently resolve design uncertainty in 3D.
Maximum reasoning is not a substitute for the required visual review.

Keep Multica runtime concurrency at one. Designer, implementation and visual
review are sequential bounded runs using the existing project. Visual reviewers
may write their own reports but cannot modify the candidate or approve on the
owner's behalf. No paid API/service or additional image-generation purchase.
Direct chat handles dispatch, review and administrative state changes.

Before this change, all five Multica profiles (Pilot, Asset Benchmark, Code,
Unreal, Concept Art) used Astra/medium/default. Both MSQ-9 worker sessions confirm
Astra/medium; its direct controller and technical reviewer confirm Astra/ultra.
Evidence: `Saved/OpeningLobby/Layout02/OwnerReview/model-audit.json` and the
historical native rollout paths recorded there. User-level Codex settings are
unchanged. Model selection and reasoning are explicit per-role settings, not
inferred from an agent's display name.
