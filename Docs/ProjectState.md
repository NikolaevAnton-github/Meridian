# MeridianSquad current project state

Updated 2026-09-20. This is a navigation snapshot of current scope and decisions,
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

Current review workflow, 2026-09-19: the executor self-checks; one primary independent
reviewer owns technical review for substantive changes; the controller accepts
scope, applicable evidence and finding closure without a second full technical
review. Reuse passing evidence and justify only affected rechecks. See
[review responsibilities](AgentDevelopment.md#review-responsibilities) and
[the owner decision](Approvals/ReviewResponsibilities01.json). Existing visual
and owner gates remain; this administrative change does not expand gameplay scope.

## Planned follow-up: MSQ-88 mannequin collision, grounding and recovery blend

After playing MSQ-87, the owner reports that the overall system works but asks
for one follow-up covering arms passing through the body, feet hovering above
the floor and the visible transition from varied physical falls to the get-up
animation. [PhysicsControlRecovery01 / MSQ-88](Tasks/PhysicsControlRecovery01.md)
records selective self-collision, calibrated sole contact and a full skeletal
pose-snapshot blend based on the owner's Epic reference. The current MSQ-87 path
blends physical-body targets toward a fixed first frame; it is not that snapshot
workflow. See [the exact feedback and task request](Approvals/PhysicsControlRecovery01-TaskCreation01.json).
MSQ-88 is unassigned in backlog; implementation and review are not dispatched.
Preserve MSQ-87 Candidate05 and its evidence. The owner retains direct visual
testing for this experiment; the three reported defects remain unresolved.

## Owner-test handoff: MSQ-87 gradual mannequin instability and get-up

The owner selected gradual loss of stability: buckling legs, torso lean and pose
recovery, followed by a physical fall when disturbance or support loss is excessive,
then living get-up when support permits. [PhysicsControlBalance01](Tasks/PhysicsControlBalance01.md)
records the planned behavior and focused acceptance under
[the task-creation request](Approvals/PhysicsControlBalance01-TaskCreation01.json).
The owner [authorized trial execution](Approvals/PhysicsControlBalance01-OwnerStart01.json).
One existing Multica Unreal executor delivered Candidate05 at verified native
Astra/max/standard. The build and 38 focused self-checks pass. The owner then
[waived independent review for this task](Approvals/PhysicsControlBalance01-OwnerTesting01.json)
and will test it directly; the dispatched review was cancelled without a verdict.
See [implementation](PhysicsControlBalance01.md) and
[controller handoff](PhysicsControlBalance01Handoff.md). The six mannequins now
lose stability, fall alive and recover with assisted back/stomach get-up, including
interruption and blocked/unsupported paths. Standing/recovery retain pose springs
and possible foot sliding; this is not autonomous locomotion. Owner play/motion
acceptance remains pending. Live Multica owns task status. Kimodo remains optional.
The owner subsequently selected and requested download of Mixamo back/stomach
get-up sources. [MixamoGetUp01](../Assets/Source/PhysicsControlBalance01/MixamoGetUp01/README.md)
preserves both original FBXs at 30 FPS without key reduction, with source mesh,
skeleton and exact provenance. Manny retargeting and bounded integration preserve
their full 251/259-frame ranges. Original sources and earlier evidence remain intact.

## Authorized tooling setup: MSQ-86 local Kimodo

The owner requested a local NVIDIA Kimodo installation under `D:/devgames` for
animation experiments. [KimodoLocal01 / MSQ-86](Tasks/KimodoLocal01.md) has installed
an isolated environment under `D:/devgames/Kimodo`, with local launchers, CUDA
verification and 10.05 GB of source, dependencies and public models. See
[the handoff and continuation](KimodoLocal01.md) and
[the owner instruction](Approvals/KimodoLocal01-OwnerScope01.json).
The owner subsequently started the Chrome UI and explicitly requested a get-up
animation. [GetUp01](KimodoGetUp01.md) records one successfully generated and saved
six-second floor-to-standing candidate (NPZ and BVH). Full UI and one real text
generation are now demonstrated for that session; server restart/lifecycle was
not retested. The owner-started server and result tab remain available. Gameplay
balance/get-up and Unreal integration are not dispatched; the candidate is not
production-accepted. The six-mannequin gameplay and owner edits remain preserved.

## Owner-play handoff: MSQ-85 Physics Control variants

On 2026-09-19 the owner played and liked MSQ-84, adopted Physics Control and
requested removal of the old enemy from active gameplay, six mannequins with
different stronger hit reactions, and partial player movement/firing slowdown
while the world slows more. See [the exact decision](Approvals/PhysicsControlVariants01-OwnerScope01.json)
and [PhysicsControlVariants01 / MSQ-85](Tasks/PhysicsControlVariants01.md).
Initial adjustable preview values are 0.25 world/body/all-bullet time and 0.65
player movement/firing time. Earlier normal-player SLOWDOWN statements below are
historical and superseded; full stop is unchanged and remains later MSQ-75 scope.
The former old-enemy comparison requirement is superseded for active gameplay;
all source assets, implementations and historical evidence remain preserved.
This authorizes the bounded implementation/review, not MSQ-70 or paused art/lobby work.
The owner subsequently stopped excessive per-profile testing and independent
visual comparison: [OwnerVariantTesting01](Approvals/OwnerVariantTesting01.json)
limits handoff verification to six rendered mannequins and actual hits on one.
The owner compares the variants. The executor run and primary review were stopped.
Candidate04 is built and handed off under the narrowed scope: six profiles, no
legacy enemy and applicable real-hit evidence on one. See
[implementation and controls](PhysicsControlVariants01.md). The owner's subsequent
PIE session is preserved. Broad technical/visual review is not claimed.

## Verified experiment: MSQ-84 second Physics Control dummy

On 2026-09-19, after playing the enemy prototype and discussing continued bullet
impacts on dead bodies, the owner requested a plan and task for a second Physics
Control dummy. [PhysicsControlDummy01 / MSQ-84](Tasks/PhysicsControlDummy01.md)
defines one removable Manny beside the retained enemy: powered living reactions,
death to passive ragdoll, continued corpse impacts, sleep/wake, reset and a bounded
body-and-bullet slow-motion development preview. See the
[exact request and planning scope](Approvals/PhysicsControlDummy01-TaskCreation01.json).

The owner authorized execution on 2026-09-19: see
[the start record](Approvals/PhysicsControlDummy01-OwnerStart01.json). Candidate10
passes the eight scoped technical/prototype visual rows after one Multica Unreal
executor and the sole primary review role completed implementation and bounded
correction at Astra/max/standard. See [implementation](PhysicsControlDummy01.md)
and [controller acceptance](PhysicsControlDummy01Review.md).

The supported second Manny responds locally to hits, releases drives on death,
receives falling/sleeping corpse impacts and resets without ammunition refill.
Y previews coherent quarter-speed bodies/bullets with normal player movement;
F10 toggles the fixture, avoiding Unreal's F9 screenshot shortcut. F6/F7 retain
their existing roles. The grounded normal/quarter trajectory comparison remains
failed (36.659 cm versus 15 cm); the separate physical-clock check passes.
Distributed world supports do not demonstrate autonomous balance.

The original enemy remains the comparison baseline. Owner play acceptance and
adoption are separate. Full time ability, balance/get-up, AI, Mover migration,
new art and deferred lobby work remain outside the experiment. MSQ-67 stays open;
MSQ-70 and successors remain undispatched. Owner edits, source assets and historical
evidence are preserved under `Saved/CombatSlice01/PhysicsControlDummy01/`.

## Verified gameplay baseline: MSQ-69 enemy prototype

The owner requested the next gameplay task on 2026-09-19; see
[the exact start record](Approvals/EnemyPrototype01-OwnerStart01.json) and
[EnemyPrototype01 / MSQ-69](Tasks/EnemyPrototype01.md). Live Multica confirms
MSQ-82 is done, with verified closure commit `be8d2ae`. One Multica Unreal executor
delivered the prototype and one bounded correction at Astra/max/standard. The
same primary independent reviewer closes the correction and passes the technical
and prototype visual criteria; see [controller review](EnemyPrototype01Review.md).

The retained lobby spawns one transient Manny enemy with seven damage regions,
100 health, rifle hit response, death/ragdoll and reset. F7 toggles demonstration
movement; F6 resets targets/feedback without refilling ammunition. See the
[implementation](EnemyPrototype01.md), [Contract01](EnemyPrototype01-Contract01.json)
and [correction](EnemyPrototype01Correction01.md). The source audit verifies an
editable template body and bounded forearm capping feasibility; production caps,
matching stump/skin transitions and detached-piece physics remain later criteria.
No additional source-selection gate is needed for that demonstrated technical route.

The 71 original focused checks and 12 correction checks pass with applicable
evidence reused. The correction excludes a newly killed enemy's cached spheres
from later same-frame aim queries, preserving the 85 ms schedule and residual
bullet flight. Candidate06/08 provide independently reviewed actual visuals.
Owner play/final-art acceptance remains separate. No new model production,
purchases, paused protagonist work or final enemy styling is authorized.
MSQ-70 (enemy AI/combat) and successors remain undispatched; player health follows
later. The retained lobby, owner configuration, purchased arms and earlier
verified evidence remain preserved. The parent remains open for the family.

## Verified prerequisite: MSQ-82 combat timing

The owner placed **MSQ-82 / CombatTiming01** next after MSQ-68 and authorized
execution; see the [task](Tasks/CombatTiming01.md),
[order decision](Approvals/CombatTiming01-NextTask01.json), and
[start record](Approvals/CombatTiming01-OwnerStart01.json). One Multica worker
implemented timestamped shots, distinct bullet births/residual flight and bounded
catch-up through 250 ms. Focused build/runtime and independent/controller checks
pass, including 446 evaluator assertions; see [implementation](CombatTiming01.md)
and [controller review](CombatTiming01Review.md). Controlled and actual low-FPS
cadence agree with the 85 ms schedule. Reset spacing, quick taps and the final
round's presentation are corrected. Stop/self-hit and finite ammunition remain.

The retained procedural recoil still recovers more slowly at 10 FPS and produces
a transient ADS sight displacement; the reports document measured evidence and
causal limits. This timing closure does not claim that visual limitation is fixed
or confer owner play/visual acceptance. Owner configuration, assets and historical
evidence are preserved. A newly opened owner PIE session is left untouched.

MSQ-69 depends on this completed stage 2 and is now authorized by the later owner
start record above. Later stages remain undispatched. The parent remains open for
the sequential family; technical closure alone grants no successor authorization.

## Verified baseline: MSQ-68 combat foundation

The owner authorized **MSQ-68 / CombatFoundation01** implementation, with
[fixed projectile/time/self-hit rules](Approvals/CombatFoundation01-OwnerScope01.json).
Player movement stays normal during world slowdown and complete stop; all bullets,
including the player's, follow world time and can injure their shooter. Stage 1
now implements finite-flight hits, ammunition and testable collision/time seams;
player health and the player-facing ability remain later tasks. One Multica
production worker at Astra/max/standard completed implementation and bounded
corrections. Focused runtime, independent source/visual and controller reviews
pass; see [implementation and controls](CombatFoundation01.md) and
[controller acceptance](CombatFoundation01Review.md). The retained lobby is ready
for Play with transient targets. F6 resets targets and feedback without refilling
ammunition; Stop/Play restores 30/90. Owner play/visual acceptance remains separate.
MSQ-69 now follows completed MSQ-82 under the owner start record above; verify live
Multica for execution state. The parent stays open for the remaining family.

On 2026-09-18, the owner requested tasks for the proposed gameplay progression
and sequential execution; see the [exact task-creation decision](Approvals/CombatSlice01-TaskCreation01.json).
The [CombatSlice01 plan](Tasks/CombatSlice01Plan.md) covers rifle hits/damage and
finite ammunition; enemy asset readiness and combat; player health/restart;
a small lobby encounter; representative body/environment damage; time slowdown,
force push and telekinesis; integrated combat; episode design/implementation;
and independent final review.

The original preparation created parent **MSQ-67** and children **MSQ-68 through
MSQ-81** as unassigned backlog with one ordered stage per child and zero runs.
That setup snapshot precedes the MSQ-68 execution authorization above. See the
[setup verification](CombatSlice01TaskSetup01.md). Multica owns
live status; stage/depends_on metadata is descriptive and the controller must
verify prerequisites before explicitly dispatching each authorized run. The
parent is coordination only. Use one production worker, max reasoning and standard
speed, focused checks and task-scoped closure commits.

Prototype defaults remain tunable proposals. Damage-ready enemy sources and the
named episode design are explicit later gates. New art/modeling, structural lobby
changes and unresolved narrative staging are not approved by task preparation.
Original protagonist work and deferred lobby architecture remain paused. Existing
owner edits, accepted assets, source/evidence history and the retained lobby stay
preserved. No gameplay or editor changes were made during the historical task
preparation; follow live Multica and the MSQ-68 handoff for execution evidence.

## Latest rifle presentation baseline: muzzle flame brightness

After playing the lobby on 2026-09-18, the owner reports general satisfaction and
requests a slightly brighter rifle muzzle flame. [PurchasedArms06](Tasks/PurchasedArms06.md)
is a bounded brightness adjustment over PurchasedArms05; see the
[exact feedback](Approvals/PurchasedArms06-OwnerScope01.json). MSQ-66 increases the
existing flame RGB by 20%, preserving alpha, size, timing, smoke and gameplay.
Focused hip/ADS visual review and saved-package reload pass; see
[implementation](PurchasedArms06.md) and [controller review](PurchasedArms06Review.md).
The later owner-owned PIE session is left untouched. Owner acceptance of the
new tuning remains separate. Lobby lighting and all paused work stay preserved.

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
