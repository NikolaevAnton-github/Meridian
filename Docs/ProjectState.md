# MeridianSquad current project state

Updated 2026-09-18. This is a navigation snapshot of current scope and decisions,
not a second task database or a new execution authorization. Read the relevant
linked task before work and verify live Multica/editor state when needed. Later
explicit owner instructions take precedence within their scope. When dated summaries
conflict, follow later scoped owner decisions and preserved approval records, not a
report's "latest" label.

Current execution requirement: **all project executors and reviewers use max
reasoning at standard speed**. See [the standing owner instruction](Approvals/WorkerReviewerMax01.json).
Verify native execution as well as saved profiles. Earlier high/medium settings
below describe historical runs and are superseded for future work; profile
restoration must retain the new max requirement.

## Current gameplay baseline: airborne actions and physical landing

After playing PurchasedArms04 on 2026-09-18, the owner reported premature landing
motion after the Shift jump, requested removal of jumping during Alt tactical
sprint, and required immediate aiming and firing after ordinary and Shift takeoff.
[PurchasedArms05 / MSQ-65](Tasks/PurchasedArms05.md) implements the correction; see
[exact owner scope](Approvals/PurchasedArms05-OwnerScope01.json).
Focused checks pass after correcting a post-contact Run End overlay and a canceled
takeoff edge. Ordinary and Shift jumps permit immediate airborne ADS and firing,
including held Shift and continuous fire through landing. Alt rejects Space at
activation and during tactical sprint. A genuine flight phase is held until floor
contact; ordinary/Shift trajectories remain unchanged. See
[implementation](PurchasedArms05.md) and [controller review](PurchasedArms05Review.md).
The retained lobby is ready for Play. Technical/controller verification is separate
from owner visual acceptance. Original character and environment work remain paused.
The earlier PurchasedArms04 timing conclusion and Alt jump behavior below are
superseded; their evidence remains preserved.

## Previous gameplay baseline: jump from Shift sprint

The owner requests a slightly higher and farther jump from Shift fast movement.
[PurchasedArms04 / MSQ-64](Tasks/PurchasedArms04.md) adds it over the PurchasedArms03
baseline; see the [exact scope](Approvals/PurchasedArms04-OwnerScope01.json).
The owner also made [focused verification](Approvals/FocusedVerification01.json)
a standing rule: check only directly affected behavior and related transitions,
without full animation/feature sweeps. Original character and environment work
remain paused.

The focused checks and bounded presentation correction pass: Shift + Space now
retains 540 cm/s travel, raises takeoff from 320 to 352 cm/s, and uses a compatible
jump base through landing. Measured apex is about 63 cm versus 52 cm for ordinary
jumping. Shift release preserves airborne momentum; the next ordinary jump resets
correctly. See [implementation](PurchasedArms04.md) and
[controller review](PurchasedArms04Review.md). The retained lobby is ready for Play.
Technical/controller verification is separate from owner visual acceptance.

## Heading-independent rifle aiming baseline

After the next lobby play session on 2026-09-18, the owner reported increasing
rifle aiming misalignment when turning away from the initial spawn heading.
[PurchasedArms03 / MSQ-63](Tasks/PurchasedArms03.md) corrects the ADS translation
from world coordinates to the camera-attached mesh basis. The focused heading,
aim re-entry, canted and pitch checks pass; the saved AnimBP loads in a fresh
editor with the retained lobby ready for Play. See the
[implementation](PurchasedArms03.md) and [controller review](PurchasedArms03Review.md).
The [exact instruction](Approvals/PurchasedArms03-OwnerScope01.json) explicitly
limits verification to directly affected behavior; do not repeat the full movement
or action matrix from MSQ-62. Original character and environment work stay paused.

## Integrated purchased rifle gameplay baseline

On 2026-09-18, after playing PurchasedArms01, the owner reported post-reload bobbing
pauses, aimed left drift and a hip rifle dip, and requested all purchased rifle-pack
functionality including full movement and shooting, excluding the vendor arena and
tutorial hints. [PurchasedArms02 / MSQ-62](Tasks/PurchasedArms02.md) provides the baseline; its
[exact owner instruction](Approvals/PurchasedArms02-OwnerScope01.json) supersedes
the minimal gameplay exclusions below. Original protagonist and environment
architecture remain paused. Keep the retained lobby and shadowless presentation.

MSQ-62 now integrates the supplied rifle action/animation graphs with real lobby
movement, fixing the reload tail/pose handover and crouch collision restoration.
The final authored-camera toggle is verified and defaults off. See
[controls, feature parity and source limitations](PurchasedArms02.md) and the
[controller review](PurchasedArms02Review.md). The retained lobby is ready for Play;
technical/controller verification is separate from owner visual acceptance.
The purchased bundle supplies shooting/action presentation, not a damage/health
system or finite ammunition economy. Its arena, tutorial UI and body showcase
controls remain excluded. Historical sources and unrelated owner edits are preserved.

## PurchasedArms01 baseline and preserved history

On 2026-09-18 the owner requested that all original-protagonist changes be rolled
out of the active game for now, and that the purchased arms and animations be
used for a minimal walkable lobby. Arms and weapon must cast no shadows because
there is no body. Keep movement, aiming and reloads; remove unrelated pack content
and mechanics. See the [exact decision](Approvals/PurchasedArms01-OwnerScope01.json)
and [PurchasedArms01 execution scope](Tasks/PurchasedArms01.md).

MSQ-61 implements this temporary walkthrough; see the
[play controls and implementation](PurchasedArms01.md) and
[controller review](PurchasedArms01Review.md). Purchased arms and one rifle use
WASD/mouse movement, hold-RMB aiming and R reloads, with all player presentation
shadows disabled. Unused packages are preserved outside active Content in the
hash-manifested PurchasedArms01 archive. Owner visual acceptance remains separate.

The controller canceled the active
MSQ-54 run `01a0b392-4907-70fb-950c-618b0f7879ee`; its Blender calculation stopped.
MSQ-50 and MSQ-54 are parked in backlog. MSQ-55 through MSQ-60 remain undispatched
backlog. Prior MSQ-51/52/53 deliveries and evidence are preserved.

Use the existing native OpeningLobbyCharacter and OpeningLobbyGameMode, retained
lobby map and audited purchased art subset. No original-protagonist mesh had been
connected to that native pawn. Archive original-only development content and
unneeded migrated pack assets outside Content with preserved bytes and a manifest.
Keep source art, owner exports, helper scripts and Saved evidence as inactive
history. Do not continue body repair or infer acceptance of any paused candidate.
The original-art requirement is suspended for this temporary purchased-arms scope.

## Original protagonist: paused, history preserved

The selected Datum16 concept and MSQ52-RigContract01 remain historical decisions.
Primary BodyRepair01 and Correction01 C08 were frozen with unresolved defects;
Correction02 was incomplete when the owner changed direction. None is accepted
for the active game. All old continuation and successor-dispatch language is
superseded by PurchasedArms01 until a new owner instruction.

The exact pre-change project snapshot is preserved in
[the 2026-09-18 archive](Archive/ProjectState/2026-09-18-BeforePurchasedArms01.md).
For historical source navigation only, see [the task index](Tasks/PlayerCharacter01Tasks.md),
[animation audit](PlayerAnimationAudit01.md) and [AI3D pipeline](PlayerCharacter01AI3DPipeline.md).
These records are not an execution queue. Original sources remain under
`Assets/Source/PlayerCharacter01/`; the untouched purchased project remains at
`D:/devgames/Weapon`. No source deletion or paid generation is authorized.

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
