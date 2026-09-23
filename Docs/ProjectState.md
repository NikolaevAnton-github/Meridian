# MeridianSquad current project state

Updated 2026-09-23. This is a navigation snapshot of current scope and decisions,
not a second task database or a new execution authorization. Read the relevant
linked task before work and verify live Multica/editor state when needed. Later
explicit owner instructions take precedence within their scope. When dated summaries
conflict, follow later scoped owner decisions and preserved approval records, not a
report's "latest" label.

Current execution requirement: **all project executors and reviewers use max
reasoning at standard speed**. See [the standing owner instruction](Approvals/WorkerReviewerMax01.json).
Verify native execution as well as saved profiles. The later
[MSQ-102 scoped decision](Approvals/CombatAI01-CAI00-OwnerStart01.json) permits
controller-selected reasoning for that task; Astra/high is selected, with shared
profiles restored to max afterward. The later
[MSQ-103 start](Approvals/CombatAI01-CAI01-OwnerStart01.json) also permits
controller-selected Astra/high for that task, restoring shared profiles to max afterward.
Earlier high/medium settings
below describe historical runs and are superseded for future work; profile
restoration must retain the new max requirement.

Current review workflow, 2026-09-19: the executor self-checks; one primary independent
reviewer owns technical review for substantive changes; the controller accepts
scope, applicable evidence and finding closure without a second full technical
review. Reuse passing evidence and justify only affected rechecks. See
[review responsibilities](AgentDevelopment.md#review-responsibilities) and
[the owner decision](Approvals/ReviewResponsibilities01.json). Existing visual
and owner gates remain; this administrative change does not expand gameplay scope.

## Owner priority: AI, shooting and environmental destruction

The owner places good AI, shooting and environmental destruction ahead of
dismemberment; see the [exact priority decision](Approvals/CombatPriorities01-OwnerScope01.json).
MSQ-73 advanced body damage/separation is deferred to low-priority stage 16,
after the priority combat work. Its technical prerequisite remains MSQ-72.
MSQ-74 now depends directly on MSQ-72, so dismemberment does not block destruction.
MSQ-78/MSQ-81 retain ordinary damage, reactions and death while advanced wounds
and separation remain explicit deferred scope. Other stage numbers are preserved;
the historical stage-7 ordering below is superseded. See the
[administrative verification](CombatPriorities01.md).

MSQ-102 is delivered for owner testing; see its handoff below. A bounded destruction
sample after the persistent hunter and a repeatable encounter, before extensive
tactical tuning, remains a scheduling recommendation. No implementation starts
from this priority update; existing owner gameplay-testing boundaries remain.

## Owner-test handoff: MSQ-103 persistent intent and running

The owner [starts the next task and delegates reasoning selection](Approvals/CombatAI01-CAI01-OwnerStart01.json).
[CAI-01](Tasks/CombatAI01/CAI-01.md) delivers **Candidate01/build05** on MSQ-102:
persistent encounter alert, bounded preliminary local search, explicit running and
an interruptible action lifecycle. Native build, 35 focused source/pure checks and
the sole independent source review pass. Controller acceptance matches all 79
manifest entries and preserved owner/map bytes. See the [handoff](CombatAI01-CAI01.md),
[review](CombatAI01-CAI01Review.md) and [acceptance](CombatAI01-CAI01Acceptance.md).
Executor/reviewer native Astra/high is verified; the shared profile is restored to
max/default and task runtime stopped. The retained lobby is reopened for owner Play.
S01/S06/S07/S10, visible running/braking, motion, feel and performance remain pending
owner testing. No agent Play/firing ran. Navigation retains its local one-layer,
28 m home-radius limits. MSQ-104 hearing/incoming-fire awareness and later successors
remain undispatched. Multica owns live execution status.

## Owner-test handoff: MSQ-102 baseline, contracts and observability

The owner [starts MSQ-102 and delegates reasoning selection](Approvals/CombatAI01-CAI00-OwnerStart01.json).
[CAI-00](Tasks/CombatAI01/CAI-00.md) delivers Candidate01/build02 on the matched
MSQ-70 baseline: bounded status/event traces, input contracts, reset generations
and stable per-agent seeds. The native build, 24 focused checks and sole independent
source review pass; controller acceptance matches all 30 manifest entries and
preserved owner/map bytes. See the [handoff](CombatAI01-CAI00.md),
[review](CombatAI01-CAI00Review.md) and [acceptance](CombatAI01-CAI00Acceptance.md).
One Multica executor and the reviewer ran at verified native Astra/high; executor
standard-speed arguments were explicit. The shared profile is restored to max and
task runtime stopped. The retained lobby is loaded for owner Play. Gameplay,
in-engine reset/export, motion/audio and performance remain pending owner testing;
no agent Play or firing probes ran. This capture contract does not establish full
policy/physics replay. MSQ-103 is now authorized above; later successors remain
undispatched. Multica owns live execution status.

## Prepared direction: surprising arcade combat AI

The owner reports that the delivered MSQ-70 opponent is too weak, does not run and
loses the player too easily. The owner requires continued search, footstep hearing
and awareness of incoming fire, then explicitly requests a very detailed plan as an
arcade shooter: surprise and quality without oppressive pressure. See the
[exact planning request](Approvals/CombatAI01-Planning01.json),
[design and architecture](Design/CombatAI01.md), and
[ordered implementation plan](Tasks/CombatAI01Plan.md).
The plan proposes a persistent hunter, tactical individual, coordinated three-enemy
encounter and later integration with actual destruction/abilities. The owner's later
[task-formalization request](Approvals/CombatAI01-TaskCreation01.json) creates
[MSQ-101 and 16 children, MSQ-102 through MSQ-117](Tasks/CombatAI01.md), all prepared
in backlog, unassigned and without runs. CAI package references map to those issues;
future integrations are unstaged and do not block the core path. Disarming and wound
integration are separate children preserving MSQ-99/100 independence. See
[setup verification](CombatAI01TaskSetup01.md). Limited sensory knowledge, pressure
permissions, architecture, tuning and future order are recommendations, not separately
approved implementation. The intended persistent-search direction supersedes the
old finite-search target; the existing build/evidence remain unchanged. No production,
editor change, gameplay test or implementation dispatch is authorized by task preparation.
The sole independent [planning review](CombatAI01PlanningReview.md) passes after two
bounded contract clarifications; controller acceptance is documentation-only.

## Owner-test handoff: MSQ-70 enemy combat

The owner [selected MSQ-70 outside Multica and will perform gameplay testing](Approvals/EnemyCombat01-OwnerStart02.json).
[EnemyCombat01](EnemyCombat01.md) delivers Candidate01/build03 directly on the
GASP/Mover and GASPALS armed foundation. Play defaults to one profile-1 opponent
with perception, bounded local navigation, aiming/finite-flight firing, finite
search/return, magazine/reload policy and physical recovery/death/reset handover.
F6 restarts the current mode; `msq.EnemyCombat fixtures` restores the three passive
profiles and `one` restores the combat opponent. Player hit/damage counters prepare
MSQ-71; player health/death remain later scope. The native build and
[sole independent source review](EnemyCombat01Review.md) pass, with EC70-R1 closed;
[controller acceptance](EnemyCombat01Acceptance.md) verifies scope, identity and
preservation. Gameplay, path reachability, motion and performance remain pending
owner testing. No agent Play, firing tests, screenshots or Multica execution ran.
The retained lobby editor is loaded with the build, Play stopped and no dirty
packages. Navigation covers one bounded floor layer; reserve ammunition is
unlimited and timed reload uses the Ready pose. Owner config/project/map bytes,
content sources and historical evidence remain preserved.
Earlier MSQ-70 undispatched statements below describe Multica/history and do not
supersede this direct delivery. MSQ-71 onward, MSQ-93 through
MSQ-96 and MSQ-99/100 remain separate and are not started.

## Owner-test handoff: GASPALS armed enemies

The owner [authorized direct integration outside Multica tasks](Approvals/GASPALSEnemy01-OwnerStart01.json).
[GASPALSEnemy01](GASPALSEnemy01.md) now delivers all three current GASP/Mover
fixtures with the prototype M4, Relax/Ready/Aim poses, independent aim/movement,
pitch and actual crouch. Existing damage, physical recovery, fall/get-up, death
and current impact/fall tuning are retained. Candidate01/build11 passes focused
checks and the [sole independent technical review](GASPALSEnemy01Review.md);
[controller acceptance](GASPALSEnemy01Acceptance.md) covers scope, identity and
19 registered artifacts. The modified existing AnimBP has a separate revision
manifest and exact pre-edit archive; historical fingerprints remain unchanged.
No source GASPALS mount is needed. Sources and owner settings are preserved.

The lobby editor is ready with Play stopped. Use `msq.EnemyRifle aim`, `crouch`,
`stand`, `ready`, `relax`, `move X Y walk` and `stop`; F6 recreates Ready fixtures.
Owner motion/play judgement remains separate. No Multica issue or task runtime
was dispatched. MSQ-70 retains enemy firing and autonomous combat; MSQ-99/100
and MSQ-93 through 96 retain their separate scope.

## Separate owner trial: GASPALS on UE 5.8

The owner requested a separate GASPALS project directly outside Multica.
[GASPALSUE58Trial01](GASPALSUE58Trial01.md) prepares
`D:/devgames/GASPALS_UE58/GASPALS.uproject` from pinned upstream UE 5.7 source on
the installed UE 5.8.3. The default map, Play startup, keyboard crouch/stand,
ragdoll/get-up and Play stop pass focused smoke checks. Camera deprecation and
an empty character-mesh-array warning remain documented. The editor is ready
for the owner's trial; complete feature compatibility and motion acceptance
are not claimed. Existing MeridianSquad and GameAnimationSample sources remain
preserved. This experiment does not dispatch or integrate any gameplay task.

The later [Tripo character experiment](TripoCharacter01ChatHandoff.md) is **stopped**.
The owner rejected the result for excessive deformation and requested a new-chat
handoff without retaining the trial model. Trial model assets and working copies
were removed, the original Downloads export was preserved, and the separate
editor returned to the default GASPALS map with Play stopped. Keep the notes and
wait for new owner instructions; do not automatically resume model work.

## Owner-test handoff: MSQ-98 GASP enemy foundation

The owner [requests task creation with GASP migration first](Approvals/GASPEnemyFoundation01-TaskCreation01.json).
[GASPEnemyFoundation01 / MSQ-98](Tasks/GASPEnemyFoundation01.md) delivered Candidate01 under
the [owner start and review waiver](Approvals/GASPEnemyFoundation01-OwnerStart01.json):
all three current fixtures use the local UE 5.8 GASP physical character with our
damage, recoverability, adaptive steps and existing controls. The Development
Editor build and six focused executor criteria pass; controller scope/evidence
acceptance and all 3,236 candidate identity checks pass. See the
[immutable handoff](GASPEnemyFoundation01Handoff.md) and
[controller acceptance](GASPEnemyFoundation01Acceptance.md). The registry contains
3,018 final plugin packages with passing validation. Source assets, historical
evidence, owner edits and the later cadence correction remain preserved.
One Multica Unreal executor ran at verified native Astra/max/standard. No independent
reviewer was dispatched; owner motion/play judgement remains separate. Small sole
compliance penetration (about 0.5-1.3 cm) remains documented. The active owner Play
session was preserved during closure. Movement commands are ready for MSQ-70;
autonomous AI combat is not part of this delivery.
The [owner editor-lifecycle approval](Approvals/GASPEnemyFoundation01-OwnerEditor01.json)
permits stopping the existing Play session and necessary controlled Unreal restarts
for MSQ-98; preserve owner changes and unsaved assets before doing so.

The owner's later screen recording led to a direct, personally requested correction
without a new task: [upright recovery handoff](GASPEnemyFoundation01HandoffCorrection01.md).
The current build captures a fresh GASP Ragdoll snapshot before releasing upright
recovery and retains the upright anchor through Mover's queued mode change.
The reproduced backward pose snap is corrected; the native build and focused
fall/get-up, repeated-hit, slowdown and movement checks pass. The editor is ready
for owner Play on the lobby. Candidate01 evidence remains unchanged and does not
represent the new binary; owner config/project edits and map are preserved.

The owner's follow-up recording then identified the remaining uncommanded
half-turn from the player-spawn side. [Correction 02](GASPEnemyFoundation01HandoffCorrection02.md)
preserves facing in both Mover's outgoing input and GASP's cached input at the
Ragdoll/Walking boundary. The native build and focused checks pass: seven idle
handoffs preserve facing, with continuous arm poses, including repeated hits,
commanded movement, F6 recreation, slowdown and a completed fall/get-up sequence.
This is another direct correction without a new task; assets and prior evidence
remain unchanged. Temporary render settings are restored and the editor is ready
for owner Play.

The owner then reported a remaining jerk after holds and retreat steps.
[Correction 03](GASPEnemyFoundation01HandoffCorrection03.md) blends physical
targets from the recovered body pose into live GASP animation over 0.55 game
seconds. The comparable return reduces peak rendered wrist acceleration by
about 90 percent and speed by about half. Build and focused interruption,
movement-during-blend, reset, slowdown, get-up and death checks pass. The corrected
binary is loaded for owner Play. This remains a direct personal fix without a
new task; owner motion acceptance is separate and prior evidence is preserved.

The owner requested a direct outside-task [rifle impact accent](GASPEnemyImpactBoost01.md),
then asked for a much stronger local body-part reaction. The next
[owner-test tuning](GASPEnemyImpactBoost02.md) uses 4 times the ordinary impulse
for a recent hit followed by committed living fall and 6 times for the lethal
hit, superseding 1.5/2 without stacking both on one shot. Weapon settings travel
with the projectile; ordinary hits and damage are retained. Per the continuing
[owner instruction](Approvals/GASPEnemyImpactBoost01-OwnerScope01.json),
the native Development Editor build passes, with no firing or gameplay tests;
the owner tests the motion.

The owner then liked the stronger impact and requested leg countermotion on
upper-torso lethal/knockdown hits. The direct
[rotation accent](GASPEnemyImpactRotation01.md) adds a bounded one-shot impulse
couple: calves backward/upward and the equal opposite chest reaction, after
GASP releases its drives. Existing x4/x6 local impacts remain. The native build
passes; the owner retains firing and motion evaluation under the continuing
build-only scope.

The owner then reported that the leg accent was barely noticeable and
[authorized one diagnostic shot](Approvals/GASPEnemyImpactRotation02-OwnerScope01.json).
The recorder confirmed activation but exposed the single-chest mass cap:
only 1,500 total leg impulse, versus a 10,200 lethal local impact.
The [whole-leg correction](GASPEnemyImpactRotation02.md) distributes a stronger,
more upward accent across thighs, calves and feet, with the equal opposite
reaction distributed across the pelvis and spine. Current defaults are ratio
1.5 and added-speed cap 500 cm/s. The native build passes and those defaults are
loaded in the restarted lobby editor. Post-correction firing and motion evaluation
remain with the owner; the prior diagnostic is not acceptance of the new motion.

The owner then requested less leg lift and a more natural ragdoll fall.
The [fall restriction follow-up](GASPEnemyAnatomicalFall01.md) reduces the leg
accent to ratio 0.75 / 220 cm/s, with a much smaller upward component, and
gradually narrows the fall-only hip cone to 50/25/20 in the existing constraint
frames. Knees and ankles retain the authored ragdoll ranges; leaving ragdoll
restores the previous per-instance recovery limits. The native build passes.
The updated defaults are loaded in the restarted lobby editor.
This [direct outside-task correction](Approvals/GASPEnemyAnatomicalFall01-OwnerScope01.json)
uses build-only verification; owner firing/motion acceptance remains pending.

MSQ-98 is high priority and consumes MSQ-92/current follow-ups. It precedes MSQ-93
and MSQ-70. The refinement order is now **MSQ-91 -> MSQ-97 -> MSQ-92 -> MSQ-98 ->
MSQ-93 -> MSQ-94 -> MSQ-95 -> MSQ-96**; MSQ-98 is an unstaged MSQ-67 child, outside
MSQ-90's unchanged native stages. MSQ-70 retains MSQ-69 and adds MSQ-98, keeping AI
combat and enemy firing separate from migration's movement handover. The later
direct GASPALS integration above supplies rifle presentation and aiming seams.
Earlier summaries' direct MSQ-92 -> MSQ-93 order is superseded by this decision.

[EnemyDisarm01 / MSQ-99](Tasks/EnemyDisarm01.md) and
[EnemyWoundReaction01 / MSQ-100](Tasks/EnemyWoundReaction01.md) are secondary,
low-priority MSQ-67 children depending on MSQ-98 and MSQ-70. They do not block base
combat or depend on each other. MSQ-99/100 remain prepared and undispatched. The
earlier zero-run planning snapshot is preserved in
[setup verification](GASPEnemyFoundation01TaskSetup01.md). The later authorization
covered MSQ-98 only and waived its independent review; other task review rules remain.
AnimGen, parkour gameplay, player replacement and paused art/lobby work remain outside
this delivery. MSQ-93 through MSQ-96 and MSQ-70 remain undispatched. Multica owns live status.

## Owner-test handoff: MSQ-92 adaptive recovery steps

The owner likes assisted retreat with Ctrl+F9 and requests matching weapon/world
slowdown. The later [cadence correction](CombatSlowdownCadence01.md) sets rifle
firing to the 0.25 world/bullet clock while hero movement remains at 0.65;
see the [exact clarification](Approvals/CombatSlowdownCadence01-OwnerScope01.json).
The native build and focused live cadence/normal-time restoration checks pass.
This small follow-up is loaded for Play; Candidate06 below remains immutable
historical evidence, not the identity of the newly built binary.

The owner [starts MSQ-92 and requests approximately 25 percent faster recovery](Approvals/PhysicsControlAdaptiveSteps01-OwnerStart01.json).
[PhysicsControlAdaptiveSteps01](Tasks/PhysicsControlAdaptiveSteps01.md) consumes
MSQ-97 Candidate07, closure commit `5cd5b67`, and refines step length, lift,
phase timing and bounded replanning on static flat support. The initial tempo
interpretation is recovery speed 1.25, preserving physical support/effort limits.
One Multica Unreal executor delivered Candidate06 (Candidate05 native code,
build06) with a passing build and 208 focused assertions. One independent primary
reviewer passes all six scoped criteria and verifies all 438 candidate entries.
Both runs used verified native Astra/max/standard. The controller accepts scope,
evidence applicability, preservation and finding closure. See the
[implementation](PhysicsControlAdaptiveSteps01.md) and
[controller handoff](PhysicsControlAdaptiveSteps01Handoff.md).
The comparable rifle-hit step takes 0.667 s instead of 0.833 s; twelve torso hits
produce three completed steps and settling. Adaptive placement, filtered bounded
replanning, physical blocked fallback and affected slowdown/reset transitions pass.
The final build is loaded and ready for owner Play. Owner motion judgement remains
separate; assisted motion, roughly 16 FPS capture and sampled sole-clearance limits
are retained. Owner edits, sources and historical evidence remain preserved.
MSQ-93 through MSQ-96 remain undispatched; Multica owns live execution status.
The historical handoffs below retain their original candidate evidence.

## Owner-test handoff: MSQ-97 physical recoverability

The owner selected [PhysicsControlRecoverability01 / MSQ-97](Tasks/PhysicsControlRecoverability01.md)
as the next task after discussing leg replanting and physical balance limits;
see the [exact next-task decision](Approvals/PhysicsControlRecoverability01-NextTask01.json).
The MSQ-90 order is now **MSQ-91 -> MSQ-97 -> MSQ-92 -> MSQ-93 -> MSQ-94 -> MSQ-95 -> MSQ-96**.
The owner [authorized MSQ-97 without an independent reviewer](Approvals/PhysicsControlRecoverability01-OwnerStart01.json).
One existing Multica Unreal executor delivered Candidate07 at verified native
Astra/max/standard. The build and 183 focused self-checks pass; all 47 candidate
manifest entries match current and frozen bytes. See [implementation](PhysicsControlRecoverability01.md)
and [controller handoff](PhysicsControlRecoverability01Handoff.md). The controller
accepts scope, candidate identity, evidence applicability and preservation; owner
motion/play judgement remains separate. The review waiver is limited to MSQ-97.
MSQ-92 is now delivered above; MSQ-93 through MSQ-96 remain undispatched.

The delivered task replaces automatic leg-hit support failure with displaced-leg
replanting, coordinated body recovery and a practical contact/momentum-based
recoverability estimate with bounded physical assistance. Successive recovery
steps may continue under torso fire beyond the old two-step cap; genuinely
infeasible support releases into physical falling even during a burst. Enemy
settings alter recovery capacity. Ctrl+F9 now enables a bounded assistance
preset rather than the rejected unlimited fall veto. Actual bullet penetration
through both legs remains a separate future projectile integration scenario.
MSQ-92 then refines adaptive step geometry/timing, reusing predecessor evidence.

The MSQ-97 handoff runtime was Candidate07, built on MSQ-91 Candidate07 plus
CombatTestToggles02 (`37af4b8`). A recorded 30-bullet torso episode completes
three steps during continuous fire and five overall with recovery speed 1.5;
the mannequin settles after a three-bullet resumed burst. Missing support still
releases drives with assistance on. Actual inter-leg contact, living recovery,
death, reset/recreation and affected slowdown transitions are evidenced. No binary
assets changed. Historical sources/evidence and owner edits remain preserved;
the owner's later Play session is left untouched. See the updated
[family plan](Tasks/PhysicsControlRefinement01Plan.md) for scope and verification.

## Owner-test handoff: MSQ-91 stance correction within MSQ-90

The later direct owner test adjustment, [CombatTestToggles02](CombatTestToggles01.md#combattesttoggles02-three-mannequins-and-optional-fall-prevention),
keeps only mannequins 1-3 in the original first row and adds Ctrl+F9 to prevent
full living balance-loss falls while retaining hit reactions and recovery steps.
This small outside-task correction does not start MSQ-92 or change the immutable
MSQ-91 Candidate07 evidence. Ctrl+F7 immortality remains a separate control.

The owner broadly likes MSQ-89 but reports unnatural leg-joint positions after
steps in an [original screenshot](Approvals/PhysicsControlRefinement01-LegPose01.png).
The owner agrees with the proposed refinements and explicitly requires uneven
surfaces because future destruction debris must be traversable; see the
[exact planning request](Approvals/PhysicsControlRefinement01-TaskCreation01.json).
[PhysicsControlRefinement01 / MSQ-90](Tasks/PhysicsControlRefinement01Plan.md)
contains six ordered tasks: MSQ-91 anatomical stance, MSQ-92 adaptive steps,
MSQ-93 torso/arm balance, MSQ-94 obstacle-aware get-up, MSQ-95 static uneven
support, and MSQ-96 moving/disappearing debris support. The parent and children
were prepared in backlog, unassigned, with zero runs. The owner subsequently
[authorized MSQ-91 without independent review](Approvals/PhysicsControlLegPose01-OwnerStart01.json).
[PhysicsControlLegPose01](Tasks/PhysicsControlLegPose01.md) delivers Candidate07
through one Multica Unreal executor at verified Astra/max/standard. The final
build and 183 focused self-checks pass, with controller scope/evidence acceptance.
Neutral leg frames and rest height no longer accumulate distorted step poses;
wide stances use the remaining corrective step or fail into physical recovery.
See [implementation](PhysicsControlLegPose01.md) and
[controller handoff](PhysicsControlLegPose01Handoff.md). Peak measured support-foot
drift is 0.415 cm and sole gaps are 0.225-0.550 cm. Final motion/play judgement
remains with the owner; the retained lobby is ready for Play. MSQ-92 through
MSQ-96 remain undispatched.

MSQ-70 supplies actual movement and MSQ-74 representative debris. MSQ-78 retains
an explicit future acceptance row for both player and enemy crossing a rubble
patch through ordinary movement, including changing support. Reactive steps and
contact fixtures do not prove that traversal. Original CombatSlice stage order
is unchanged; this planning request does not dispatch MSQ-70 or successors.
MSQ-89 Candidate05 and its reproduced defect remain preserved as historical
baseline/evidence. MSQ-91 Candidate07 is the corrected owner-test handoff, with
assisted flat-floor motion and final owner acceptance still separate. No independent
reviewer is launched for MSQ-91 under its explicit owner waiver; the separate MSQ-89
waiver remains recorded within its scope.

## Owner-test handoff: MSQ-89 reactive recovery steps

The owner says the MSQ-88 result looks good and likes the existing hit reaction,
then requests a task for short steps that help the mannequin retain balance after
hits. [PhysicsControlStepping01 / MSQ-89](Tasks/PhysicsControlStepping01.md) covers
one or two reactive recovery steps, support-leg selection, valid foot placement,
settling at the new position and retained physical collapse when recovery fails.
Direction follows actual body displacement/lean and hit impulse. See the
[exact feedback and task-creation request](Approvals/PhysicsControlStepping01-TaskCreation01.json).
Numeric tuning and the animation/procedural route remain implementation choices.
MSQ-89 was unassigned in backlog with zero runs at creation. The owner subsequently
[authorized execution](Approvals/PhysicsControlStepping01-OwnerStart01.json).
Use one Multica Unreal executor at verified Astra/max/standard and focused self-checks.
The owner subsequently [waived independent review for MSQ-89](Approvals/PhysicsControlStepping01-ReviewWaiver01.json).
The controller accepts scope, applicable evidence and preservation; owner motion/play
acceptance remains separate. One Multica executor delivered Candidate05 with a
passing build and 149 focused self-check assertions. The procedural step transfers
weight, lifts a foot, settles at a displaced stance and permits at most two steps;
unsafe support still releases into the retained physical fall and living get-up.
See [implementation](PhysicsControlStepping01.md) and
[controller handoff](PhysicsControlStepping01Handoff.md) for evidence and limits.
Support-foot drift is below 0.62 cm in completed measured episodes; post-step sole
gaps are about 0.20-0.58 cm. Flat static floors are the verified scope; assisted
motion and the retained weak-response sole compression remain documented limits.
The owner's subsequently opened Play session is preserved. Preserve MSQ-88 Candidate04
and all historical sources/evidence. Convenient get-up clip replacement was a
separate question and is not added to this stepping scope. Live Multica owns status.

## Owner-test handoff: MSQ-88 mannequin collision, grounding and recovery blend

The owner separately requested [optional combat test controls](CombatTestToggles01.md):
Ctrl+F7 toggles mannequin immortality and Ctrl+F8 toggles infinite reserve ammunition
with ordinary magazine consumption/reload. This direct correction does not start MSQ-88.

After playing MSQ-87, the owner reports that the overall system works but asks
for one follow-up covering arms passing through the body, feet hovering above
the floor and the visible transition from varied physical falls to the get-up
animation. [PhysicsControlRecovery01 / MSQ-88](Tasks/PhysicsControlRecovery01.md)
records selective self-collision, calibrated sole contact and a full skeletal
pose-snapshot blend based on the owner's Epic reference. The earlier MSQ-87
Candidate05 path blends physical-body targets toward a fixed first frame; it is not that snapshot
workflow. See [the exact feedback and task request](Approvals/PhysicsControlRecovery01-TaskCreation01.json).
The owner [authorized MSQ-88 execution without independent checks](Approvals/PhysicsControlRecovery01-OwnerStart01.json).
One Multica Unreal executor delivered Candidate04 at verified Astra/max/standard.
The build and focused self-checks pass: effective arm/body collision, calibrated
soles and an 89-bone snapshot blend into moving get-up are implemented. Measured
post-recovery sole gaps are about 0.52-0.58 cm against a 1 cm tolerance. See the
[implementation](PhysicsControlRecovery01.md) and
[controller handoff](PhysicsControlRecovery01Handoff.md). The owner subsequently
[reported that the current result looks good and likes the hit reaction](Approvals/PhysicsControlStepping01-TaskCreation01.json).
This is the retained experimental baseline for the planned stepping follow-up.
Assisted motion, foot sliding and retargeted shoulders remain documented limits;
the feedback does not establish unrestricted-pose or final-character acceptance.
Continuous recordings are supplied. The manual owner PIE session is preserved.
MSQ-87 Candidate05, its evidence and the subsequent
optional combat test controls remain intact. Live Multica owns task status.

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
