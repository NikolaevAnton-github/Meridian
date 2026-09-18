# PlayerCharacter01: visible first-person body integration plan

Owner scope update, 2026-09-18: **PAUSED_BY_OWNER**. The original-protagonist
plan below is preserved history and is not authorized for execution. Current work
is MSQ-61 / PurchasedArms01: purchased arms, movement, aiming and reloads in the
retained lobby, without player shadows. See Docs/ProjectState.md and
Docs/Approvals/PurchasedArms01-OwnerScope01.json. All older continuation wording
below is superseded until the owner explicitly resumes original-character work.

Current owner direction, 2026-09-17: **Concept02 / Candidate01, 16 / Datum** is
selected and **MSQ-52 is authorized for execution**. See the
[exact decision](../Approvals/PlayerCharacter01-Datum16Selection01.json) and
[bounded audit task](PlayerAnimationAudit01.md). This supersedes the historical
pending-selection and no-dispatch wording below. MSQ-54 still requires the
completed rig contract and coherent production reference views.

MSQ-52 subsequently completed its controller-verified technical audit:
[handoff](../PlayerAnimationAudit01.md), `MSQ52-RigContract01`, 186 selected
packages and 82 sequences. Use that measured contract before the MSQ-54 original
prototype; original-model deformation, retargeting and gameplay remain later gates.

Latest workflow update, 2026-09-17: integrate the owner's existing Tripo Studio
and Meshy subscriptions plus Hunyuan3D Studio through
[AI-assisted production Pipeline01](../PlayerCharacter01AI3DPipeline.md).
Its dated service research, component strategy, input-view rules, early
deformation tests and source/credit handling extend stages 2, 3 and 7 below.
The prior blanket paid-service exclusion is superseded only for those existing
web subscriptions; no new purchases, top-ups or separately billed APIs.
This is a completed research/planning update, with no generation or Multica
dispatch. No final design was selected; Datum16 is a planning example only.
All existing gameplay, original-character, preservation and review requirements
remain. Read this addendum before executing the historical stage descriptions.

Latest concept delivery: [PlayerArt-Concept02 / Candidate01](../PlayerArtConcept02.md),
ten more armored designs with helmet computer/HUD, IDs 16-25. Preferred 01/08
are the direction references; no final modeling selection has been made.

Latest concept direction: the owner likes prior variants **01 (Cutline)** and
**08 (Overlap)** and requests ten additional original variants, more armored
without a tank-like silhouette, with a helmet computer rendering the interface.
Follow [PlayerArtConcept02](PlayerArtConcept02.md) and its
[direction record](../Approvals/PlayerArtConcept02-Direction01.json); save the new
art under `Assets/Concepts/PlayerCharacter01/Concept02`. Fully concealed faces,
2043 lore, Astra/max/standard and owner-only evaluation remain binding. This
preference is not final named approval for modeling.

Prior delivery: [PlayerArt-Concept01 / Candidate01](../PlayerArtConcept01.md)
contains fifteen original closed-face 2043 alternatives and remains unchanged.
Owner selection is pending; this additional concept scope does not dispatch
modeling or other gameplay work.

Status: task family created on 2026-09-16 as MSQ-50 with MSQ-51 through MSQ-60,
following the owner's original-character and selected weapon-animation direction.
All tasks were initially backlog with no run dispatched. The owner's first
2026-09-16 direction authorizes MSQ-51 concept execution only: at least 15
original alternatives, all faces fully concealed, grounded in the lore and
2043, with Astra/max/standard concept production and owner-only evaluation.
MSQ-53 is now the owner selection gate, without an independent expert run.
Other tasks are not dispatched by this direction. See the
[task index and gates](PlayerCharacter01Tasks.md) and
[task-creation decision](../Approvals/PlayerCharacter01-TaskCreation01.json).
[Initial concept direction](../Approvals/PlayerArtConcept01-Direction01.json)
supersedes the initial concept count, artist settings and expert-review gate;
the initial creation record remains historical.
Unselected appearance and technical tuning remain proposals.

## Owner scope and proposed result

The owner requests a first-person protagonist in the existing lobby, with a
visible body when looking down, believable movement, a complete character
shadow, and foot steps when turning the camera. Existing arms/weapon animation
content is at `D:/devgames/Weapon`. The owner's subsequent clarification requires
a unique protagonist model created for this project. Ready-made Fab characters
are not the final-model route. Suitable free animation assets, including Epic's
packs, may be reused if their quality passes review. This supersedes the earlier
free-character shortlist. This document plans the work; it does not reopen the
deferred lobby environment tasks or approve a final character design.

Proposed first playable: one body, one rifle, responsive camera, directional
walking/jogging, turn-in-place, floor contact, jumping/landing, and synchronized
first-person and world presentation. Include running, jumping and crouching with
the pack's first-person arm motions and suitable independently sourced/authored
leg motions. The owner selected a compact reload set: standard/nonempty and
empty, each with an aimed variant. Basic aim/fire/reload is a separately
identifiable planned step; this scope discussion is not an implementation dispatch.
Enemies, powers, inventory, multiplayer and environmental destruction are later
features. A mannequin is an intermediate technical checkpoint, not completion
of the requested protagonist model.

## Verified starting point

Inspection was read-only, through files and official product documentation.
Asset playback and compatibility have not yet been verified in the editor.

- Installed engine: UE 5.8.1, `D:/UE_5.8`; project association: 5.8.
- `AOpeningLobbyCharacter` currently has capsule, camera and CharacterMovement,
  without a character mesh, animation blueprint or weapon. The game mode selects
  this C++ pawn directly. Inputs currently use legacy bindings; EnhancedInput is
  already a module dependency.
- Capsule radius/half-height: 34/88 cm. Camera: 170 cm above capsule bottom,
  FOV 90 degrees; walking 360 cm/s; maximum step 35 cm. Retain these initially
  so character integration does not silently change the lobby's perceived scale.
- Current controller yaw immediately rotates the pawn. Body-facing direction
  must be separated from view direction for planted feet and stepping turns.
- Weapon directory: Infima Tactical FPS Animation Pack - Assault Rifle,
  671 files / approximately 1.20 GiB. Contains rifle/magazines, materials,
  audio/VFX, two weapon Blender sources, Manny mesh variants, character/weapon
  skeletons and FP/TP animation assets. This is more than animation alone.
- The supplied TP animations cover upper-body actions, not leg locomotion.
  FP walk/run clip names do not demonstrate animated walking legs. No dedicated
  turn/pivot clip was found by filename. Actual mannequin coverage is unverified.
- The owner confirms the complete pack supports UE 5.8. The vendor FAQ specifies
  UE 5.4 or newer. Sampled local packages were saved in UE 5.4; this records their
  save version, not an incompatibility with 5.8. Embedded asset paths start with
  `/Game/InfimaGames/TacticalFPSAnimations/`, despite the shorter disk directory.
  Preserve this destination root during migration and validate dependencies.
  Do not resave the original `D:/devgames/Weapon` sources during upgrade.
- Installed UE template resources contain rifle walk and jog in eight
  directions, jump and aim assets under
  `D:/UE_5.8/Templates/TemplateResources/High/Characters/Content/Mannequins/Anims/Rifle`.
  Their suitability is a promising local starting point, not a playback verdict.

## Asset selection

Use the existing weapon pack for rifle and authored hand actions. The vendor
describes its Blueprint gameplay as a showcase, so build the project's gameplay
state around the assets instead of replacing the project with that demo.
See the [vendor listing](https://www.fab.com/listings/1ae386ab-4a40-4a0f-ac17-621e2d9d1028).

### Selected weapon-pack subset

The owner explicitly prefers a compact selection over the whole showcase.
The following is the planned initial subset; animation quality remains subject
to inspection on the original character.

| Content | Planned selection |
| --- | --- |
| Rifle | One rifle configuration, one magazine type and one chosen sight/grip setup; required skeletons, materials, textures, firing/handling audio and muzzle effects. |
| Idle and aim | Standing/crouched idle, aiming pose and the necessary aim/movement transitions. |
| Fire | Ordinary and aimed firing, plus empty-trigger feedback; choose the initial fire mode during gameplay tuning. |
| Standard reload | One nonempty/tactical reload: `A_TFA_FP_AR_Reload`, with `A_TFA_FP_AR_Reload_Aimed` for aiming. |
| Empty reload | One empty reload: `A_TFA_FP_AR_Reload_Empty`, with `A_TFA_FP_AR_Reload_Empty_Aimed` for aiming. |
| Arm locomotion | Directional walk and aimed-walk loops, run/sprint, jump start/fall/land, crouched idle and crouch start/end transitions. |
| Equip/holster | One normal equip/holster set, only where the character's weapon state needs it. |
| World representation | Matching TP upper-body actions, corresponding FP/TP rifle clips and required magazine attachment/depletion assets, synchronized with the same gameplay events. |

The reload scope is two gameplay cases in two view states, not four competing
reload styles. Interpret the owner's contrast with empty as a magazine that still
contains ammunition. Proposed default: when capacity is already full, reload
input does nothing. Final chamber/capacity rules remain gameplay tuning.

Local inventory confirms all four reload sequences in Character FP/TP and
Weapon FP/TP. Crouch start/end sequences (including aimed versions), crouched
idle and a crouched locomotion blend space are present; no separately named
crouched-walk sequence was found. Inspect that blend space's inputs before
claiming dedicated crouch-walk coverage. The magazine has a depletion animation;
its reload attachment/hand-transfer/visibility timing requires inspection rather
than an assumed standalone magazine-reload clip.

Omit Quick/Emergency reload variants, inspections, jam clearing, syringe healing,
grenades, melee and other interactions from this initial slice. The author's
level, environment props and showcase controller are not production dependencies
by default. Keep their original source files untouched outside the game subset.

Migrate selected sequences with their required skeletons, shared materials/audio
and other verified references. Demo montages and notifies can reference showcase
code; adapt reviewed timing into project-owned montages/events rather than copying
the whole demo or blindly deleting shared folders. Check dependency closure and
the cooked selection once integration exists. The vendor documents an
[art-only extraction route](https://docs.infimagames.com/product/tactical-fps-animation-packs/guides-and-tutorials/editor/how-to-safely-remove-the-demo-code-logic).

### Applying the arm motion to the original character

The vendor's [custom-character guide](https://docs.infimagames.com/product/tactical-fps-animation-packs/guides-and-tutorials/editor/how-to-assign-a-custom-character-model-in-unreal-engine-5-ue5-manny)
supports a custom mesh with the matching Manny hierarchy and assignment to
`SKEL_TFA_Mannequin`. Build the original body/hands around this compatible rig
contract where practical. The supplied mannequin is a rig/pose reference, while
the delivered body, outfit and visible arms remain original geometry.

Use the FP clips for the original local arms during walking, running, jumping and
crouching. Align shoulder placement, arm reach, wrist/finger weights, weapon grip
and reload contact with the new proportions. If the rig differs, retargeting is
available, but exact finger/weapon contact still needs correction and inspection.

These FP movements do not supply complete animated legs. Independently sourced
or authored body locomotion supplies pelvis/legs; project state synchronizes
speed, jump phases, crouch and action timing between both. The world body uses
appropriate upper-body poses/actions with the same leg motion. Do not apply
camera-oriented FP poses blindly to the whole shadow body.

The vendor [FAQ](https://docs.infimagames.com/product/tactical-fps-animation-packs/getting-started/faq)
also describes head-bone camera motion in the supplied animations. Keep our
stable gameplay camera separate and tune any visual shake deliberately so
character animation cannot unintentionally steer the aim.

Free animation candidates checked on 2026-09-16:

| Source | Proposed use | Selection rule |
| --- | --- | --- |
| Installed UE 5.8 rifle template animations | First movement/retarget prototype | Inspect these first: already local, with directional walk/jog coverage. |
| [Game Animation Sample, Epic](https://www.fab.com/listings/880e319a-a59e-4ed2-b268-b32dac7fa016) | Preferred additional source for natural locomotion/transitions and animation references | Audit its current clip inventory for stationary turns and armed lower-body suitability; migrate a bounded subset. A locomotion sample does not automatically solve FPS turning. |
| [Lyra Starter Game, Epic](https://www.fab.com/listings/93faede1-4434-47c0-85f1-bf27c0820ad0) | Shooter locomotion/turning reference and possible clip source | Inspect if installed assets and the selected sample leave a specific gap; do not migrate its full gameplay architecture. |
| [Animation Starter Pack, Epic](https://www.fab.com/listings/98ff449d-79db-4f54-9303-75486c4fb9d9) | Compact fallback animation source | Its 62 classic-mannequin animations require compatibility/retarget checks; not the default quality target. |

Epic's [August 2026 update](https://www.unrealengine.com/tech-blog/download-the-latest-game-animation-sample-project-now-updated-for-ue-5-8)
confirms Game Animation Sample support for UE 5.8. Use it selectively; sample
ragdoll, climbing and smart-object systems are not requirements for this task.

## Original protagonist production

Create the character's original body, clothing, equipment, boots, hands/gloves
and head in Blender, with editable native sources. Author the final materials
and texture sources in Painter. The visible first-person arms belong to this
same original character; reuse the supplied arm animations on the new mesh.
A purchased/free character with recolored textures does not meet this direction.

1. Preserve the fifteen original Concept01 proposals. Develop ten additional
   variants from the owner's preferred 01/08 direction through
   [PlayerArtConcept02](PlayerArtConcept02.md): more armor without tank-like
   bulk, an interface-rendering helmet computer, and fully concealed faces in
   the lore-grounded 2043 setting. Use Astra/max/standard concept production.
   The owner alone evaluates this concept batch; do not dispatch an
   independent expert review. Define
   silhouette, proportions, outfit construction, equipment placement, palette
   and materials. Include front/side/back views, hands/sleeve detail, a look-down
   composition and the full-body shadow silhouette as specified by the bounded
   concept task. The protagonist's MERIDIAN membership and 2043 setting are
   fixed; outfit and biography details remain proposals, not approved canon.
2. Obtain the owner's selection of an identified concept package before original
   character modeling. Record the chosen version and remaining design choices.
   The existing lobby art approval does not approve this character's design.
3. Build an original deformation-ready body/outfit blockout at the agreed scale.
   Establish standing height, eye position, shoulder width, arm reach and hand
   size against the existing capsule/camera and supplied rifle before detail.
   Test shoulder, elbow, wrist, hip, knee and ankle deformation and the first-person
   view before sculpting/final texturing, including forearm twist, finger grip,
   reload reach and crouching. Keep equipment clear of weapon handling and the
   camera's supported pitch/FOV range.
4. Use a UE-compatible skeleton/retarget contract where practical. Reusing a
   skeleton does not determine the model's appearance. Preserve required hand,
   twist and IK support; verify the actual weapon-pack skeleton rather than
   assuming every Manny-compatible rig is identical. Fit grip and reload contact
   points without altering the original supplied animation/source bytes.
5. Complete detail, game-ready topology, UVs, baking, Painter layers, skin weights,
   physics asset and LODs after the deformation and camera prototype passes.
   Derive local body/arms and complete world-body variants from one original
   character source with matching proportions, seams and materials. Set measured
   geometry/material/texture budgets during the prototype and retain import
   settings with the Blender/Painter sources. Concept selection and final in-game
   appearance acceptance are separate reviews.

Prioritize what the FPS camera exposes: hands, gloves, sleeves, chest equipment,
waist, thighs and boots. A complete head/body silhouette is required for the
world representation; cinematic facial animation is not part of this first
delivery. Do not bake a missing head into the shared source just to fix clipping.

Free animation selection has its own quality gate: preview selected clips on the
original rig and compare first-person plus observer recordings for foot sliding,
weight transfer, starts/stops, turn contacts, hand contact and consistent movement
style. Retarget and correct suitable clips; replace or author clips that fail.
Free availability and a shared skeleton do not establish animation acceptance.

## Character architecture

Use one authoritative character and gameplay state with coordinated visual parts:

1. **Camera and collision:** CharacterMovement drives the capsule. The camera
   remains stable at eye height, with independently controlled look direction.
   Optional small movement/recoil offsets must not let head animation shake or
   steer the player's aim. Keep crouch/camera smoothing separate from foot IK.
2. **Visible body:** local torso/hips/legs follow the body animation pose at world
   scale. A dedicated local mesh/section arrangement excludes camera-intersecting
   head and overlapping arms. Preserve enough torso for a coherent look-down
   view; check the shoulder transition across the supported pitch/FOV range.
3. **First-person arms and rifle:** retain the pack's authored first-person
   actions on the newly authored character arms, with the arms/weapon configured
   for UE's native first-person rendering where appropriate. Derive the arms
   and body from the same original outfit/proportions; any supplied mannequin
   arms are temporary technical references only.
4. **Complete world body and rifle:** an owner-hidden world representation
   supplies a complete head/body/weapon shadow and applicable reflections. It
   shares locomotion and weapon action state with the visible parts. Avoid double
   shadows by giving each visual representation explicit shadow ownership.

UE 5.8 exposes `FirstPerson` and `WorldSpaceRepresentation` primitive types;
first-person primitives do not cast scene shadows. This is why the complete
world representation is required. Keep visible feet and world-body feet aligned,
and ensure owner-hidden meshes still evaluate their animation. Validate against
the lobby's actual renderer and lights, not only in a preview window.
See [Epic's first-person rendering guide](https://dev.epicgames.com/documentation/en-us/unreal-engine/first-person-rendering).

Prototype the body/arms seam early. Rendering everything with a weapon-specific
FOV can distort legs; rendering unmodified first-person arm poses as the world
body can create implausible shoulders and shadows. Treat the pack's TP upper-body
poses as the starting point for the world body's weapon actions.

## Movement and animation behavior

- Begin with a bounded animation state machine and directional blend spaces,
  driven by actual horizontal velocity, acceleration, movement mode and body yaw.
  Use explicit start/stop/pivot clips where the selected source supports them.
  Consider Motion Matching only if clip coverage and a measured prototype justify
  the added integration; choosing a sample does not require adopting its systems.
- While stationary, allow a small yaw difference between camera and torso/body.
  At a tunable threshold (initial trial roughly 45-60 degrees), play left/right
  stepping turns. Cover larger turns through suitable 90/180-degree clips or
  controlled sequences, including direction reversal and rapid mouse rotation.
  Use hysteresis to avoid repeatedly starting turns at the threshold.
- Coordinate pelvis/root rotation with foot-contact phases. Feet must lift and
  replant; continuously rotating the mesh over fixed feet does not pass. If no
  suitable source clips exist, author the small missing turn set in Control Rig
  or Blender and verify it in motion.
- While moving, support forward/backward/diagonal/strafe motion relative to view
  and body direction. Match clip stride and playback rate to real displacement;
  add bounded stride/orientation warping if needed after the basic blend works.
- Foot IK adjusts sole orientation and pelvis height on slopes/steps, with
  contact-state locking and smooth release. Disable/adapt ground constraints
  during airborne phases and prevent leg overextension. IK alone does not create
  walking or stepping-turn animations.
- Layer TP weapon actions/aim above locomotion. Preserve lower-body motion during
  reload and apply hand-to-weapon constraints only when the action permits them.
  Retarget with explicit chains and pose alignment; compatible names alone do not
  establish skeleton compatibility. See [Epic's IK retargeting guide](https://dev.epicgames.com/documentation/en-us/unreal-engine/ik-rig-animation-retargeting-in-unreal-engine).

## Sequential delivery plan

| Stage | Work and output | Pass condition |
| --- | --- | --- |
| 1. Original character concept | Preserve fifteen Concept01 alternatives; add ten Concept02 variants from preferred 01/08, with more armor and helmet computer/interface. Fully concealed faces, 2043 lore, Astra/max/standard artist and owner-only evaluation. | MSQ-53 records the owner's selection of an identified concept package; no independent expert run. Directional preference does not replace named approval before modeling. |
| 2. Animation audit and small migration | Inventory dependencies, skeletons, montage slots/notifies, additive/root-motion settings and FP camera assumptions; preview representative weapon/leg clips on a technical mannequin. Record provenance and selected subset. | Selected assets load in UE 5.8.1, sources remain intact, each required movement has a candidate clip or explicit authoring task. |
| 3. Original model and deformation prototype | Create the approved body/outfit/hands in Blender, establish the rig, fit the weapon grip, and test representative aim/reload/walk/turn poses before final detail. | Proportions match the concept, visible joints deform cleanly and the custom arms can use the existing weapon actions. |
| 4. Body/camera/shadow prototype | Integrate the original prototype body, custom FP arms/rifle and complete world shadow into the project character and pawn selection. Retain walkthrough scale. | Look down and turn in the lobby without head interiors, double arms, separated feet/shadow or forced camera bob. |
| 5. Locomotion and planted turns | Directional walk/run, crouch transitions and movement, stationary turn steps, jump/land and foot IK; cover the planned FP arm motions with suitable body locomotion. Correct or author missing/unsuitable clips. | Animation quality passes on the original character from first-person and observer views, including rapid yaw reversals. |
| 6. One weapon gameplay slice | Aim, fire, ammo, empty state, the selected standard/empty reloads with aimed variants and basic recoil; synchronize FP arms, TP body, rifle and magazine. Use existing audio/VFX. | Gameplay owns timing/ammo once; visible copies cannot double-fire or consume extra ammunition. Near-wall shots and interrupted actions behave consistently. |
| 7. Original character finish | Complete detail, topology/UV/bakes, Painter materials, skinning corrections, LODs and coherent body/arm/world variants. | Identified model matches the selected concept and passes neutral-light/lobby review with editable original sources. |
| 8. Lobby integration and review | Full route, camera limits, shadows, wall proximity, movement/weapon combinations, performance sample, fresh independent review and required correction. | No required defects remain; exact assets/code, controls, evidence and known limitations are documented for owner playtest. |

Concept preparation and the animation audit can be planned independently; editor/
DCC mutation stays sequential under one writer. Stages 4-5 form the first playtest
of the original body. An earlier Manny test may resolve rendering/animation risks,
but cannot replace original character production or its visual review. Stage 7
completes the character's appearance after the major deformation risks are resolved.

For the weapon slice, distinguish a camera aiming trace from a physical
muzzle obstruction check, exclude the player's own meshes, and handle weapon
wall proximity with an explicit pose/offset. A render-depth trick alone must not
permit firing through a wall. No enemies or destruction are needed for a temporary
hit-feedback test.

## Review checklist

Use recorded real PIE interaction, not only animation-preview screenshots:

- Look down at idle, while walking forward/back/sideways/diagonally, and through
  start/stop transitions. Torso and legs remain coherent; planted soles do not
  visibly skate or float.
- Turn left/right 45/90/180 degrees while stopped, repeatedly reverse direction,
  then enter movement mid-turn. Feet visibly step and the pelvis does not snap.
- Traverse the actual entrance, checkpoint, column routes and elevator approach;
  use a temporary unsaved fixture for slope/step tests if the lobby lacks one.
- Jump/land; crouch under clearance and try standing while blocked.
  Camera never enters torso/head and foot IK does not pull airborne feet down.
- Verify full head/body/rifle silhouette under a suitable existing lobby light,
  feet-to-shadow attachment and no duplicate arms/weapons/shadows. Use a separate
  neutral test setup for diagnosis without changing accepted lobby atmosphere.
- Weapon slice: idle/moving aim/fire/reload, both standard and empty reloads with
  aimed variants, full-capacity no-op, interruptions, held input, wall proximity,
  magazine/hand timing and synchronized world shadow.
- Check at 30/60/120 FPS where supported and record a warmed-up 1440p performance
  comparison with the existing pawn. Establish measured CPU/GPU/animation cost;
  the provisional overall 60 FPS target is not a promise before profiling.

## Execution and preservation

The bounded Multica records exist under MSQ-50. The current owner instruction
authorizes additional MSQ-51 concept execution via [PlayerArtConcept02](PlayerArtConcept02.md)
using Astra/max/standard and concurrency one. Concept art is stored under
`Assets/Concepts/PlayerCharacter01/Concept02`; preserve Concept01 unchanged.
MSQ-53 records the owner's named
selection without an independent expert run. No other task is dispatched by this
direction, and original modeling still requires that selection plus the rig
contract. Later implementation retains its Astra/high/standard baseline and
fresh independent integrated review; the concept-only exception does not remove
MSQ-60. The direct controller remains active through the concept handoff to the
owner. Use the existing task records and check their owner gates; no competing
dispatcher or task database is introduced.

Before editor mutations, confirm the live project/map, PIE state and dirty
packages. Use the existing project and current lobby; retain owner edits,
environment assets, accepted lighting and deferred task history. Keep a bounded
rollback snapshot of changed gameplay/config/map assets, not a duplicate project.
Prefer configuring the new pawn through the existing game-mode path; change a
level override only if inspection proves it necessary.

Free Fab animation content and the existing local weapon assets fit the authorized
reuse route; the final character model is original production. Check the current
price/version and record the applicable license/provenance at acquisition.
Do not buy assets or use paid services. Measure archive, staging,
import, cache and rollback growth against the project's 250 GB cap before sample
downloads. Keep only required migrated dependencies; avoid collecting entire
samples without a specific need. Git stores code/config/decisions and asset
sources; binary assets use LFS, generated evidence stays under `Saved/`.

## Open choices and principal risks

- Final outfit remains unselected. Initial fire mode, movement tuning and
  detailed chamber/ammunition rules remain proposed gameplay choices; the compact
  standard/empty reload set with aimed variants is now recorded owner direction.
- Original character design, modeling, deformation and materials are substantial
  production work. Approve the concept and validate a rigged body/arm prototype
  before investing in final detail; maintain a single coherent outfit across views.
- Missing stationary turn animations and foot-contact quality are the main
  locomotion risk; assess them before committing to an animation framework.
- The existing pack's skeletons, original content root and separate weapon/
  magazine animation timing require a careful first migration.
- Estimate original-art effort after stage 1 and animation/retarget effort after
  stages 2-3; do not equate dropping a mesh into the map with completing full-body
  first-person behavior.
