# Architecture01 controller review and current decision gate

2026-09-14. MSQ-6 remains **in review, incomplete**, with no assigned worker.
All ten implementation/review runs have finished. The last independent result
is **Review04: NOT READY**, with B3 (credible fixed glazing) still open.
This is a decision package for directing another correction, not an owner-ready
detail submission or an acceptance request for a known visual defect.
Owner detail acceptance remains pending; MSQ-7 stays backlog.

## Current identified result

The editor is on `/Game/Maps/L_OpeningLobby_Architecture01_GlassReview01`,
variant B under the unchanged LightStudy01 inspection lighting. The saved map
SHA-256 is `271c23e22489e270da4b7345f2f5b8b65396df44211333835f6810b4d6b39aad`.
The [worker handoff](OpeningLobbyArchitecture01.md) records editable sources,
the seven material assignments, evidence, controls and limitations.

The independent [Review04 report](../Saved/OpeningLobby/Stage2/Architecture01/Review04/report.md)
and [verdict](../Saved/OpeningLobby/Stage2/Architecture01/Review04/verdict.json)
confirm improved door-leaf separation and softer fixed-pane reflections.
The fixed fields nevertheless still read as smooth infill panels in the
required interior views. Transmission works in the separately labeled
reverse-side diagnostic; strong transmitted blur and calibrated haze are not
demonstrated. Neither shader transmission nor softer highlights close B3.

Actual decision views:

- [Approved entrance reference](../Assets/Concepts/OpeningLobby/OwnerReferences01/02-EntranceSecurity.png).
- [Current entrance overview](../Saved/OpeningLobby/Stage2/Architecture01/GlassReview01/Final/C2-75.png).
- [Current checkpoint context](../Saved/OpeningLobby/Stage2/Architecture01/GlassReview01/Final/C3-90.png).
- [Current glass detail](../Saved/OpeningLobby/Stage2/Architecture01/GlassReview01/Final/MetalGlass-90.png).

Review02's B1 stone and B2 floor passes retain their scope. Review04 establishes
no new metal or spatial regression. The owner-accepted 60 x 24 x 18 m scale and
human-size exceptions remain preserved. Still images do not verify temporal
stability or performance; final atmosphere is outside this stage.

## Verification and preserved history

Review04 checked all ten full Final views, the actual approved references,
saved native shader wiring and persistence. Exactly seven material bindings
changed across 2,101 actors and 2,125 components; geometry, collision, gameplay,
lights and recorded renderer settings match LightStudy01. All 581 candidate
snapshot files and 15 earlier review files stayed unchanged during review.
All 83 worker inventory entries match. The prior route and dimension checks
are carried only through preservation, including the original fascia-panel
timing caveat; they were not repeated for material-only changes.

The clean-map, stopped-PIE and restored temporary settings are supported by
worker records and independent saved-record review. The controller also
confirmed the actual GlassReview01 map and stopped PIE through official Epic
MCP at 02:02:55 UTC. Canonical project instructions were restored after the
Multica runtime block was removed. Original Architecture01, LightStudy01,
accepted Layout03, approved art and all historical candidates remain preserved.

Initial review failed stone, floor and glass. Correction01 closed stone/floor;
the reflection and frame-coating attempts did not close glass and were restored.
LightStudy01 improved inspection visibility. GlassReview01 tested two optical
treatments and retained B's partial improvement. Earlier failed reviews retain
their original dispositions; no result was converted into owner approval.

## Next scope decision

The controller asked the owner to choose the intended glazing appearance.
No answer has been received. GlassReview01 used light-diffusing fixed glass as
an explicitly disclosed working interpretation, not an owner-selected finish.
The bounded two-variant study and its independent review are now complete.
The next correction should begin from the owner's optical-direction response,
the approved reference and Review04's concrete fixed-surface finding. This is
not a claim that a preference response alone fixes B3, or that an exterior,
different lighting or any particular untested remedy is necessary.

Keep MSQ-6 incomplete and unassigned at this decision gate. Do not dispatch
MSQ-7 or register changed draft bytes as accepted. Record the owner's response
as a scoped direction before preparing the next bounded Multica correction.

## Execution accounting and controller correction

MSQ-9 is the rejected Layout02 task, now cancelled as superseded by MSQ-11;
its assets and evidence remain historical. MSQ-11 is done for the explicitly
accepted scale. MSQ-6 was created earlier and is the next production stage;
issue numbers do not describe the current execution order.

Ending the direct controller response immediately after the original MSQ-6
dispatch was premature follow-through. Multica continued independently.
The controller rule in AGENTS.md and AgentDevelopment.md now requires remaining
active through the run, handoff, review and bounded corrections until a verified
result or a concrete owner decision gate. Dispatch alone is not completion.

All ten MSQ-6 native sessions used `gpt-6-astra` with `high` reasoning. They do
not establish a causal link between the owner's direct-chat ultra-to-max change
and the controller's early ending. Six implementation and four independent
review runs completed; first-pass visual acceptance failed. Native totals from
the existing summarizer are 37,289,664 input tokens, including 35,503,616 cached
input tokens, and 222,675 output tokens, including 33,752 reasoning tokens once.
Uncached input is 1,786,048 tokens. These figures exclude direct controller
preparation/review and are not a subscription charge or API cost estimate.
See [native accounting](../Saved/OpeningLobby/Stage2/Architecture01/Controller/native-usage.json)
and [run records](../Saved/OpeningLobby/Stage2/Architecture01/Controller/final-runs.json).

Measured project storage was 11,352,577,789 bytes, with 999,958,340 bytes of
Stage 2 growth. Known external project profiles add 1,014,785,917 bytes, bringing
that measured scope to about 12.37 GB, within the 250 GB project and 2 GB lobby
growth limits. No paid service/API, asset deletion, registry write, commit or
push was performed in this stage. Generated evidence and logs remain in Saved/.
