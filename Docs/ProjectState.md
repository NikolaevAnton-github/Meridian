# MeridianSquad current project state

Updated 2026-09-17. This is a navigation snapshot of current scope and decisions,
not a second task database or a new execution authorization. Read the relevant
linked task before work and verify live Multica/editor state when needed. Later
explicit owner instructions take precedence within their scope. When dated summaries
conflict, follow later scoped owner decisions and preserved approval records, not a
report's "latest" label.

## Current focus: original protagonist and one rifle

The owner requested an original full-body first-person protagonist, original FP
arms and one rifle. Existing/free animations may be reused after quality and
provenance review; a stock character is not the delivered model. Preserve the
original weapon sources, all concept packages and existing owner experiments.
The setting is fixed at **2043**. Faces and eyes remain concealed; the helmet's
computer/HUD is ordinary equipment, not the source of powers or restored command
contact. Use [GameBrief](Design/GameBrief.md) and [StoryCanon](Design/StoryCanon.md).

The owner requested research into the newly purchased Tripo Studio and Meshy web
subscriptions plus free Hunyuan3D Studio, and integration into the production
sequence. Research and task synchronization are delivered; no production model,
new generation or worker run resulted from that preparation.

**Selected design:** the owner chose **Concept02 / Candidate01, 16 / Datum**
and authorized MSQ-52 on 2026-09-17. See the
[exact decision](Approvals/PlayerCharacter01-Datum16Selection01.json) and
[animation audit execution scope](Tasks/PlayerAnimationAudit01.md).
MSQ-53's named design-selection gate is satisfied. MSQ-52's technical audit and
`MSQ52-RigContract01` are complete and controller-verified; see the
[handoff](PlayerAnimationAudit01.md). MSQ-54 is the next production stage and must
reconcile derived reference views and validate the original-model round trip.
The original selection instruction dispatched MSQ-52 only. The owner subsequently
requested an owner-operated Tripo input package: the bounded MSQ-54 preparation
is delivered as [Datum16ShoulderManual01](PlayerCharacter01TripoManualPilot01.md).
Use its single StartHere image for the first manual shoulder-cap generation;
the additional illustrated views are reference-only, not a validated Multi-view
set. The next step is the owner's returned FBX. No controller Tripo generation
or complete body-prototype run was authorized or performed by this preparation.
The owner alone evaluates this concept batch; no independent concept reviewer or
MSQ-53 expert run. Later MSQ-60 integrated review remains required.

### Delivered art

| Package | Current meaning and evidence |
| --- | --- |
| Concept01 and Concept02 | 15 original concepts plus 10 armored variants, IDs 01-25; [Concept01](PlayerArtConcept01.md), [Concept02](PlayerArtConcept02.md). Preference for 01/08 did not select the final model. |
| Chevron25Refine03 / 25C | Four angular V-shaped overlapping cuirass plates; [task and package links](Tasks/PlayerArtChevron25Refine03.md). Earlier 25/25A/25B remain preserved; 25A's layering interpretation was rejected. |
| Datum16TrellisInput01 | Isolated white-background single-figure input and TRELLIS.2 usage notes; [task](Tasks/PlayerArtDatum16TrellisInput01.md). No TRELLIS installation or generation was performed. |
| Datum16MultiView01 | Eight separate white-background views; [task](Tasks/PlayerArtDatum16MultiView01.md). Prior A-pose package remains unchanged. |
| Datum16MultiViewTpose01 | Eight separate 1254 x 1254 PNGs, horizontal straight arms at shoulder height, palms down; Front/Back/profiles/45-degree/axial views; [task](Tasks/PlayerArtDatum16MultiViewTpose01.md). All 75 prior package files were preserved. |

The art is input preparation. Hidden surfaces are inferred and exact 3D consistency
is unverified. Galleries, exact prompts and manifests remain under
`Assets/Concepts/PlayerCharacter01/`. The selection record above supersedes old
pending-selection text; immutable package manifests remain unchanged.
Concept-art tasks used Astra/max/standard and owner-only evaluation; their saved
profiles/native arguments were restored. Later implementation retains the recorded
Astra/high/standard baseline unless a new scoped instruction changes it.

### AI3D production sequence and tasks

Read the [production pipeline](PlayerCharacter01AI3DPipeline.md),
[plan](Tasks/PlayerCharacter01Plan.md) and [task index](Tasks/PlayerCharacter01Tasks.md).
Their existing task family covers the work; do not create parallel provider/armor
task databases. The ordered production approach is:

1. Use the selected Datum16 and completed MSQ52-RigContract01; reconcile the
   authoritative production views during MSQ-54.
2. Inspect existing owner exports; establish one proportional master and production
   skeleton, then perform the smallest justified AI source trial.
3. Fit separate armor/components to that master in Blender; resolve joint topology,
   weights and source-pose deformation before the original prototype handoff.
4. Test first-person presentation, body movement and hand/rifle/reload interaction
   through MSQ-55/56/57. Return geometry failures to MSQ-54.
5. Finalize UVs, bakes, native Painter materials and LODs in MSQ-58 only after the
   preceding deformation, presentation and gameplay probes succeed; integrate,
   independently review and correct the identified final candidate in MSQ-59/60.

The canonical editable source root is `Assets/Source/PlayerCharacter01/`; selected
AI inputs/exports belong under `AI3D/<provider>/<candidate>/` inside that root.
Use existing Tripo/Meshy **web allowances only** within the scoped task. No new
purchases, top-ups or separately billed API usage are authorized. Read the dated
provider research and verify changing capabilities/terms before execution:

- [Tripo](Research/PlayerCharacter01AI3D/TripoResearch01.md): segment before quads/rig.
- [Meshy](Research/PlayerCharacter01AI3D/MeshyResearch01.md): multiview and Smart
  Topology are separate routes.
- [Hunyuan3D](Research/PlayerCharacter01AI3D/HunyuanResearch01.md): hosted V3.1 exposes
  2-8 views; free quotas are temporary and hosted commercial-output terms still
  require verification. Do not infer hosted rights from local-model licensing.

Last verified Multica state, 2026-09-17:

| Tasks | State / scope |
| --- | --- |
| MSQ-50 | `in_progress`; parent board state, not evidence of an active worker. |
| MSQ-51 | `done`; concept deliveries preserved. |
| MSQ-53 | `done`; owner selected Concept02 / Candidate01, 16 / Datum. No expert run. |
| MSQ-52 | `done`; controller-accepted animation audit and MSQ52-RigContract01. 186 source-identical packages, 82 sequences, 19 representative playback cases; later original-rig/gameplay gates remain. |
| MSQ-54 | Bounded manual-input preparation delivered; awaiting owner Tripo export. The original body/deformation prototype remains incomplete. |
| MSQ-55 through MSQ-60 | `backlog`; presentation, movement, rifle, finish, integration and final review. |

The [task synchronization audit](Tasks/PlayerCharacter01AI3DTaskAudit01.md) verified
description-only updates to MSQ-50 and MSQ-52 through MSQ-60. All 33 non-target records
(including MSQ-51), all statuses/assignments/dependencies/stages and player run histories were
preserved; zero issues or runs were added. Multica remains the source of live state.

## Lobby: retained and deferred

The owner closed remaining lobby work on 2026-09-16, deferring it until gameplay
has been integrated and a new owner scope is supplied. **Do not resume old lobby
directions or dispatch their backlog.** MSQ-4/6/7/14/20/28/30 are administratively
cancelled with `CLOSED_BY_OWNER_DEFERRAL`; this neither rejects retained assets nor
grants visual acceptance or completes deferred verification. See
[deferral summary](OpeningLobbyDeferred01.md) and
[exact owner closure](Approvals/LobbyDeferred01-OwnerClosure01.json).

- MSQ-31/32 are done. The owner accepted UpperVoid01's height-corrected atmosphere:
  accepted bytes are HeightCorrection03, restored exactly during HeightCorrection04.
  HC04's spatial trial remains rejected history. HC-R1 was closed by owner acceptance,
  not technically eliminated. See [review](OpeningLobbyUpperVoid01Review.md) and
  [acceptance](Approvals/LobbyUpperVoid01-Acceptance01.json).
- The retained lobby map is `/Game/Maps/L_OpeningLobby_PainterStone01`. Earlier maps
  were archived outside `Content` and retired with owner authorization. For any
  newly authorized edit, work on this map in place with a bounded rollback snapshot;
  preserve owner geometry/edits, sources and history. See
  [map-retention decision](Approvals/LobbyPainterStone01-Acceptance01.json) and
  [owner-edit record](Approvals/LobbyFunctionalBuild01-OwnerEdit01.json).
- Preserve all 107 material bindings, accepted stone/floor/metal assets and current
  slab variants, lighting/atmosphere, glass/support and gameplay. SlabLayout01 passed
  its scoped opaque review; that is not owner acceptance of the slab candidate.
  Its 120 x 240 cm slabs / 5 mm joints were working dimensions, not exact owner-approved
  sizes. Glass and unrelated final walkthrough work remain outside UpperVoid acceptance.
  See [material review](OpeningLobbyMaterialsComplete01Review.md).
- Glass remains deferred. Recorded slab planning limits were 450 MB per batch and
  2.4 GB for the lobby; the hard total project cap is still 250 GB. These limits do
  not dispatch deferred work. Preserve failed Painter evidence and genuine native
  sources; use [PainterWorkflow](PainterWorkflow.md) for any authorized continuation.
- Preserve the accepted overall scale and named drawing/production decisions. Read
  [visual acceptance](VisualAcceptance.md) and the relevant linked approval before
  any new environment scope. Older proxy envelopes do not automatically constrain
  a new design proposal; dimensional changes require explicit owner review.

Historical map hashes identify specific earlier candidates, not the current live
editor state. Use the relevant acceptance manifest and inspect current bytes when
needed; do not infer live identity from old paragraphs saying "current map".

## Tooling and instruction maintenance

The owner requires a local Git commit of verified task changes after each task
closure, before final handoff. The controller owns this step; see
[the standing instruction](Approvals/TaskClosureCommits01.json) and AGENTS.md.

The owner permits launching existing apps and local services needed for authorized
work without repeated confirmation. At the 2026-09-17 audit, Multica database/API/web
were started on loopback ports 15432/8080/3000 while the task runtime stayed stopped.
Check actual state before use. Administrative startup and the process-scoped
PowerShell invocation are documented in the [audit](Tasks/PlayerCharacter01AI3DTaskAudit01.md).
No task execution follows merely from bringing services online.

Use [AgentDevelopment](AgentDevelopment.md) for verified tooling history,
[AssetRegistry](AssetRegistry.md) for the separate `meridian_assets` database and
[registry acceptance](AssetRegistryAcceptance.md) for evidence semantics. Check live
versions/connections; historical successful integration does not prove availability.

Keep durable rules in [AGENTS.md](../AGENTS.md), replace stale scope in this snapshot,
and keep detailed task/approval evidence in its existing files. The
[instruction archive](Archive/AgentInstructions/README.md) preserves the exact
pre-compaction file for historical lookup; it is not an active instruction source.
