# PurchasedArms02: source rifle controls and reload recovery

MSQ-62 implementation handoff, 2026-09-18. Technical verification is complete;
controller review and owner visual acceptance remain separate. The retained
`/Game/Maps/L_OpeningLobby_PainterStone01` is ready for Play, with PIE stopped.

## Result and boundaries

The native lobby game mode now spawns an adapted copy of the purchased
`BP_TFA_BaseCharacter`, derived from `OpeningLobbyCharacter`. The supplied action
graphs, first-person animation graph, hand IK, procedural offsets, notifies,
paired rifle animations, magazines, attachments, effects, audio and physics props
run together. Native code provides actual collision-aware movement and the lobby
camera. The previous ten-loop/two-reload pose sampler is retired.

The source is the unchanged content bundle at
`D:/devgames/Weapon/TacticalFPSAnimations`, not a standalone playable project.
Its shooting, ammunition and auxiliary actions are demonstrations. It contains
no evidenced hit/damage system, damaging grenade, health, reserve ammunition,
inventory or functional prone/lean system. Those mechanics have not been invented.
Original protagonist production and lobby architecture remain paused.

**Ammunition follows the source demonstration exactly:** the rifle starts at 30,
decrements on shots, and resets to 30 on the tick after underflow. Its independent
empty-fire selector plays the dry-fire demonstration. Reload animations do not
refill the source counter: in the final test, 24 shots left six rounds before and
after R reload. Both magazine graphs display that counter. This is not a finite
ammunition economy or an automatic empty-reload policy.

## Controls and source-to-project matrix

All package paths in this table are under
`/Game/InfimaGames/TacticalFPSAnimations/`. The principal orchestration is
`Common/Core/Characters/BP_TFA_BaseCharacter`; configuration is
`Weapons/AssaultRifle/Demo/Data/DA_TFA_AssaultRifle`. Its Demo/Data location is
essential configuration, not an arena dependency.

| Control / feature | Actual supplied behavior | Integration and observed verification |
| --- | --- | --- |
| WASD, mouse | Source sets simulated velocity and look; it is stationary by design. | Native CharacterMovement and mouse input provide real traversal. Source blend spaces receive actual local velocity, including backwards/diagonal motion and turns. Walk 360 cm/s. Actual PlayerStart, entrance/wall/elevator/return route passed. |
| Hold Left Shift | Run state, loop and end transition. | Real 540 cm/s run with supplied graph. Hold threshold 0.3 s; release and blocked-wall recovery tested. |
| Hold Left Alt | Tactical sprint and its transitions. | Real 720 cm/s sprint; source action/ADS gates retained. Hold threshold 0.3 s. Wall stops clear run/sprint presentation while held input can request it again when travel resumes. |
| C | Crouch toggle, procedural offset and crouched locomotion. | Real 56 cm half-height capsule and 180 cm/s crouch. A blocked stand request remains pending; pose and camera follow the actual crouch until clearance permits standing. Source blocks toggling while running/sprinting. |
| Space | Full jump demonstration, gated against busy/run/sprint/crouch. | Real jump, gravity and landing. Authored airborne portion holds at about 0.65 s during a longer fall; floor contact resumes the 0.85 s landing tail. Normal repeated jumps and a jump off a temporary PIE platform passed. Landing does not clear another action's busy state. |
| Hold RMB | ADS spring offset, aim audio, animation slots and FOV timeline. | Retained. Comfortable lobby default is 90 degrees; source aimed target is 78. Source timeline drives the active camera, including its slight authored overshoot. Held, released and newly requested aim through reloads tested. |
| Middle mouse | Canted ADS toggle. | Retained and tested with aiming, quick reload and automatic fire. It is not positional leaning. |
| LMB | Synced firing montages, recoil, muzzle flash, casing ejection and ammo display. | Semi and held auto tested. Automatic interval is approximately 0.083 s at gameplay frame rate. Input during a locked reload is ignored; firing works after unlock. Effects use the same first-person rendering space as the rifle. |
| V | Fire-mode switch and selector presentation; reachable semi, auto and empty-fire states. | All three reached through input, with semi/auto/empty/switch montages observed. Empty fire is a supplied demonstration state, independent of the counter. |
| Tap R | Ordinary tactical reload. | Source paired character/rifle montage and notifies retained. Hip/ADS, stationary/moving, changed aim/direction and repeated-input cases passed. |
| Hold R, at least 0.3 s | Magazine check. | Distinct mag-check montage observed; release does not also start ordinary reload. |
| Q | Quick reload, including aimed presentation. | Distinct source quick montage tested, including moving canted ADS and repeated input. |
| E | Explicit empty/emergency reload. | Source bolt/magazine handling and physics magazine drop retained. Hip/ADS, stationary/moving, changed aim/direction and recovery tested. |
| Tap / hold T | Inspect / empty inspection, 0.3 s hold branch. | Both distinct source actions observed through input and returned to idle. |
| H | Equip/re-equip montage. | Retained and tested. Lobby startup enters the ready pose directly; the vendor fade, delayed showcase setup and introductory equip are removed. This is not weapon inventory or switching. |
| J | Clear-malfunction variation array. | Both rack and magazine-swipe actions observed. No random gameplay jam probability is supplied. |
| F | Melee variation array. | Bash, left swing and right swing observed. These are gestures/audio, without supplied hit or damage logic. |
| X | Interaction variation array. | Grab, punch and push all observed through repeated input. No door/pickup interaction system is supplied. |
| U | Syringe action, attached prop, cap and thrown physics syringe. | Full source lifecycle observed at gameplay frame rate; cap and syringe remain shadowless, and no syringe remains attached after recovery. Nonzero syringe audio was recorded. No health values are supplied. |
| G | Quick grenade-throw gesture and audio/notifies. | Montage and recovery tested. No grenade projectile/explosion is supplied by this rifle action. |
| B | Grip attachment cycle and matching hand pose. | Default, vertical and angled states observed, including source attachment-change montage. No scope/silencer inventory is inferred. |
| Magazine display | Two magazine actors, bullet meshes, ammo-driven deformation and visibility notifies. | Main/reserve socket identity retained. Six remaining rounds produced 24 collapsed bullet meshes; both AnimBPs followed the counter, with the source one-frame update lag possible on a shot. Recovered main magazine position matched its receiver socket exactly in recorded samples. |
| Feedback | Aim/handling/fire/empty/cloth sounds; muzzle flash, laser and physics impacts. | Source dependencies and notify execution retained. Hip/ADS/canted fire video shows muzzle effects; 56 casing actors were observed in the sustained-fire case. Master output recordings contain firing/handling and syringe audio. |
| L | Optional authored head-camera motion. | Restored with corrected source-flag polarity; default off. Paired inspection takes prove a fixed returned view when off, 5.209 degrees of authored camera rotation when on, and a fixed view again after switching off. No synthetic shake was added. |
| P, wheel | Showcase FP/TP/bodycam/gun-camera switching and TP zoom. | Removed viewer controls for the bodyless lobby; no full-body swap or showcase camera can take over play. |
| NumPad 5 / NumPad 0 / Tab / vendor Escape | Freeze, showcase UI, tutorial panel and quit confirmation. | Removed. Tutorial UI and arena are outside the active dependency closure. Normal editor Escape remains available to stop PIE. |
| Z / other absent mechanics | Prone action asset exists but has no source character event or clips. | No prone, slide, vault, mantle, independent lean, damage, healing economy, grenade simulation or multiplayer gameplay was added. |

## Recovery diagnosis and correction

The PurchasedArms01 sampler advanced its locomotion clock, then reconstructed
additive reloads over a static hip/aim pose and overwrote the moving pose at full
weight until the last 0.15 seconds. That explains a visually near-static tail
despite continuing travel. Its normal ADS path used a different hip-to-aim pose
delta from the reload base, without the vendor hand IK. The two paths disagreed
at the left hand. The static hip base was also higher than the moving pose.

The controller's preserved baseline audit measured about 2.107 cm lateral
left-hand handover and 2.217 cm moving hip-gun drop. It found no clock reset or
literal post-completion timer. Old capture pauses and movement release at the
first completion could not establish an uninterrupted post-completion freeze.
The new baseline records kept moving for over four seconds after completion and
also found phase-matched post-completion motion. The evidenced problem is the
static tail and incompatible pose handover, not an accumulating attachment drift.

The replacement uses the source animation graph's continuous locomotion,
additive slots, source playback rates, spring offsets, grip overlays and hand IK.
Paired weapon montages and original animation notifies control action timing and
magazine lifecycle. `PurchasedArmsAnimInstance` now hosts that graph and records
evaluated-frame telemetry; it no longer constructs a separate competing pose.

The continuous matrix includes ordinary and empty reloads in all four states:
stationary hip, stationary held ADS, moving hip and moving held ADS. It retains
4.33–4.59 seconds after action completion, covering multiple gait cycles. The
later videos retain 5.33–5.58 seconds. Metrics compare evaluated camera-space
transforms to separate no-reload controls at the same evaluated blend-space phase.
Repeated evaluation IDs are excluded from the final pose comparison.

| Recovery measurement | Observed result |
| --- | --- |
| Largest recovered gun-position residual | 0.012802 cm |
| Largest recovered left/right-hand residual | 0.014812 cm |
| Largest recovered rotation residual | 0.032816 degrees |
| Moving post-tail motion energy / phase-matched control | Approximately 0.989–1.014 in 150 ms windows; zero detected freeze windows |
| Main magazine seat after recovery | 0 cm positional difference from receiver socket in recorded transforms |
| Moving matrix speed | 360 cm/s maintained through the required recovery interval |
| Pauses / player presentation shadow violations | None in the accepted recovery samples |

These are unscaled presentation centimeters, before the 0.3 first-person render
scale, not pixel measurements or a guarantee for arbitrary future assets. The
authored empty-reload tail retains a small residual before completion; it is not
reported as a persistent post-action drift.

## Integration details and acceptance evidence

- Native standing capsule remains radius 34 / half-height 88 cm; standing eye is
  170 cm above the capsule bottom. Crouched eye is 106 cm. Camera-height smoothing
  and crouch callbacks preserve the mesh's camera-space anchor.
- The adapted Blueprint's inherited capsule default is explicitly 34/88 too.
  The vendor default radius was 5 cm, which CharacterMovement restored during
  uncrouch despite BeginPlay's correct instance size. The corrected class default
  participates in the engine's actual clearance test; no post-clearance resize
  bypass was added. Cold reload and 1,270 targeted samples confirm radius 34
  throughout open crouch, blocked stand, clearance and subsequent wall contact.
- Source BeginPlay and Tick execution outputs are disconnected. Showcase setup,
  UI and perspective functions are disabled. Enhanced Move supplies only raw
  source input; native code owns travel/look/jump. The saved mapping contains
  22 key entries for 19 retained source actions; L and Space are native bindings.
- All attached primitive components, including Niagara muzzle effects, receive
  first-person/no-shadow policy. Dropped props retain world physics and normal
  rendering space, with shadow flags disabled. The policy is also applied during
  camera calculation to cover notify-spawned presentation before rendering.
- Source FP mesh configuration and the active character use arms-only Manny.
  TP config references are cleared. Some shared source assets remain hard
  dependencies; no body is instantiated or exposed by the retained controls.
- Source demo console overrides and attached showcase spotlight are disabled.
  Lobby materials, lighting, architecture and map bytes are unchanged.

The source variable named `bAnimateCamera` actually drives a reference-pose blend
on `head` when true. The first restored L implementation selected that locked
camera, so it did not expose the authored head rotation. Native selection now
uses the inverse condition and starts with the head lock enabled for the stable
default. Source animation bytes and the head-only blend graph remain unchanged.
`Correction01/source-head-poses.json` and `camera-head-branch.json` record the
diagnosis. `Correction02-CameraOff/On.json` each contains 539 evaluated inspection
action samples: returned rotation is 0 degrees off, up to 5.209331 degrees on,
matches the source camera exactly, and returns to 0 after L is switched off.
The earlier walking-only toggle and Correction01 camera pair are preserved as
incomplete/failing evidence, not proofs of the corrected option.

Evidence root: `Saved/PurchasedArms02/Worker/`.

The controller verified the actual executor as Astra/max at standard speed,
including native arguments and disabled fast mode, in
`Saved/PurchasedArms02/Controller/native-settings.json`. The worker did not change
profiles or dispatch another writer.

| Evidence | What it establishes |
| --- | --- |
| `build07.log`, `cold-load-final.json`, `editor-state-handoff.json` | UE 5.8.1 native build succeeded; fresh editor loaded all 400 packages; retained map open, no dirty assets/maps, PIE stopped. Final editor PID is recorded in `editor07.pid`. |
| `Walk02/runtime-verification.json` | Existing lobby verifier passed in 31.578 s, from actual PlayerStart (-2850, -105, 90.15), through mouse control, entrance wall contact, elevator approach and return. No teleport/direct movement calls in this route. |
| `final-graph-contract.json`, `dependency-closure.json` | Actual saved parent/config/mesh/input and disconnected startup/tick; zero missing hard dependencies and zero arena/tutorial UI packages. |
| `Recovery02-*.json`, `recovery-analysis02.json`, `final-evaluated-analysis.json` | Eight continuous reload cases, four controls, evaluated gun/hands, action/locomotion phase, seat and shadow measurements. |
| `Features01-*.json`, `actions-analysis.json` | Individual source controls, short/held branches, all melee/grip/fire states; additional interaction run covers grab/punch/push. |
| `Interactions03-Ordinary/Empty/QuickCanted/RunTransitions/InteractVariants.json` | Changed aim, turns/direction, repeated input, gated fire and movement transitions. |
| `Interactions03-Jump.json`, `Interactions04-LongFall/WallRun/WallSprint.json` | Actual jumps, extended airborne hold and run/sprint wall recovery. Temporary geometry was created only in PIE and never saved to the lobby. |
| `Correction01-Capsule.json`, `Correction01/targeted-verification.json`, `Correction02-CameraOff/On.json` | Correct class-default clearance contract, unchanged 34 cm radius, achieved stance/height, standing wall collision, and actual authored camera motion off/on/return. |
| `Feedback01-Shooting.json`, `Feedback05-Syringe.json`, `Feedback05-Magazine.json` | Dynamic VFX/physics, prop cleanup, ammunition-driven magazine deformation, and complete shadow checks. |
| `Video/Views01-*.mp4`, `*-comparison.png` | Ordinary-speed pre/tail/post comparable hip/ADS views; real-time presentation timestamps. Four videos were visually inspected. |
| `Video/Feedback01-Shooting.mp4`, `Video/Feedback05-*.mp4`, `Audio/*.wav`, `Video/Correction02-Camera*.mp4` | Firing, syringe/magazine and authored camera-motion views. Use the nonzero Feedback01/05 recordings; background-muted probes are not audio passes. |

External video capture samples approximately 11–12 frames/s while gameplay
telemetry remains roughly 100–120 evaluated frames/s. Videos use measured real
timestamps and do not pause or accelerate the simulation. One repeated evaluated
frame in the earlier standing hip-empty case is excluded by the final analysis.
Audio files are captured mixer output and are not synchronized movie soundtracks;
their duration can be shorter than the gameplay interval. Rendered nonzero output
does not independently verify the owner's physical speaker configuration.

Preserved failed probes are not acceptance evidence: `BaselineHip01` and the early
Feedback02/03/04 syringe runs were background-throttled or muted; the first
BlockedCrouch probe used an unavailable Python spawn API; Feedback02-Syringe used
an unavailable visibility method. The first LongFall fixture allowed an
intermediate platform landing and was replaced by Interactions04-LongFall. Early
PrintWindow video probes were unusable; the delivered videos use foreground
screen-region capture. An early dependency query was mistakenly attempted in PIE
and was replaced with editor-world registry and fresh-load checks. A null source
Look trigger warning exposed an unsaved input-map mutation; the map was force-saved,
then verified after restart and its ten unused input dependencies preserved outside
Content. The final editor log has no Blueprint runtime, missing-package or input
trigger errors; its stale MCP-session diagnostic was resolved by reinitialization.
The later Interactions04-BlockedCrouch recording exposed the 5 cm default-radius
regression and is superseded by Correction01-Capsule. The controller's targeted
review caused these bounded capsule/camera corrections; the passing reload suite
was not repeated. Capture timing is evidence of evaluated behavior, not a claim
of hitch-free performance.

Rider was connected and used for native inspection and comparable viewport views.
No `debugging-code` skill was available in this executor's installed skill catalog.
The cause and verification use actual graph/node exports and evaluated runtime
poses, rather than claiming a debugger session that did not occur.

## Preservation and exact change inventory

The preservation check covers 1,184 starting files. There are no missing files;
the only changed starting files are the six authorized code/configuration files
below. Vendor bytes, original protagonist/owner sources and retained Content
assets remain unchanged. The old PurchasedArms01 archive and manifest were not
rewritten. Required archived assets were copied only after checking their hashes.
Unneeded staged packages are preserved under Worker/UnusedStaging, with both move
manifests. New active provenance is separate from historical acceptance.

`Assets/Source/PurchasedArms02/source-manifest.json` lists all 400 active dependency
packages and source/active SHA-256 values: 86 pre-existing packages and 314 newly
added packages, totaling 525,123,042 bytes. Six of the newly added copied assets
were adapted; exact source copies remain in Worker/Rollback. All binary paths
resolve to the existing Git LFS filter. `.gitattributes` was not edited.

Changed existing text files:

- `Source/MeridianSquad/OpeningLobbyCharacter.h` and `.cpp`: source graph adapter,
  real movement/camera/clearance/jump, presentation policy and PIE-only probes.
- `Source/MeridianSquad/PurchasedArmsAnimInstance.h` and `.cpp`: evaluated source
  graph host and telemetry, replacing the custom sampler.
- `Source/MeridianSquad/OpeningLobbyGameMode.cpp`: adapted source pawn entry point.
- `Config/DefaultInput.ini`: native Space jump and L camera-animation bindings.

Adapted newly copied binary assets, relative to the pack root:

- `Common/Core/Characters/BP_TFA_BaseCharacter.uasset`
- `Common/Core/Characters/ABP_TFA_FP_BaseCharacter.uasset`
- `Common/Core/Inputs/IMC_TFA_Default.uasset`
- `Weapons/AssaultRifle/Demo/Data/DA_TFA_AssaultRifle.uasset`
- `Weapons/AssaultRifle/Meshes/ABP_TFA_AR.uasset`
- `Weapons/AssaultRifle/Meshes/ABP_TFA_AR_Magazine.uasset`

New text: this report, the source manifest, and the task-local Python files in
`Scripts/PurchasedArms02/`. Their exact path list and hashes, plus the 314 binary
paths, are in `Saved/PurchasedArms02/Worker/changed-files.json`. Scripts reuse the
existing Epic transport and lobby verifier; they are not a dispatcher or task
database. Generated logs, captures, sampled poses and rollback data stay in Saved.

Measured project storage is 26,093,601,119 bytes (26.1 GB), below the 250 GB cap. No service
purchase, separately billed API, registry mutation, issue/profile administration,
commit or owner-source cleanup was performed by the worker. The controller owns
independent review, any bounded correction, task status and the closure commit.
