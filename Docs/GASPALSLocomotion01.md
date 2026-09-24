# MSQ-121 / GASPALSLocomotion01 — Candidate01

Date: 2026-09-24. Executor delivery under [OwnerStart01](Approvals/GASPALSLocomotion01-OwnerStart01.json), [OwnerStart02](Approvals/GASPALSLocomotion01-OwnerStart02.json) and the [bounded brief](Tasks/GASPALSLocomotion01.md). Baseline: `b4ee7a221c135edb4703b821803be393e100b722` plus the preserved owner configuration/project edits. Implementation ran directly outside Multica. No issue, runtime, profile or registry administration and no commit was performed.

The active one-opponent and three-fixture spawn paths now use the original **GASPALS CharacterMovement character and complete animation/overlay stack**, explicitly selecting **Masculine + Rifle**. The native combat shell forwards existing commands to that source character. The old Mover pawn, isolated rifle-pose integration, upright balance controller and procedural recovery steps remain historical assets/code; they do not own the new active path.

Executor build and focused checks pass. Independent technical review, controller acceptance/registration/commit and owner motion/gameplay judgment remain separate. No agent PIE, simulation, gameplay, firing or performance probe ran.

## Source parity and adaptations

Source is the read-only `D:/devgames/GASPALS_UE58` project. Its original `GM_Sandbox` selects `CBP_SandboxCharacter` and `ABP_SandboxCharacter`; this playable character is the parity reference. No separate source demo enemy was identified. The entire source content plugin is local at `Plugins/GASPALS`, preserving the `/GASPALS` package/class identities used by source casts, choosers and linked layers. There is no runtime source-directory mount.

| Behavior | Actual source | Active destination / adaptation |
| --- | --- | --- |
| Pawn and CMC | `/GASPALS/Blueprints/CBP_SandboxCharacter`, native `ACharacter` | New `/Game/Development/GASPALSLocomotion01/Candidate01/BP_GASPALSEnemy_Candidate01` directly inherits this class. Source Character Blueprint bytes are unchanged. |
| Complete animation | `/GASPALS/Blueprints/ABP_SandboxCharacter` | Canonical class retained. Reparented to a native `UAnimInstance` subclass that adds only tactical lean. Original 1,084 graph nodes remain; source motion matching, databases, choosers, root steering, aim, IK and ragdoll/get-up stay upstream. |
| Masculine style | `/GASPALS/OverlaySystem/Overlays/Bases/Masculine/` | Child defaults explicitly select Masculine. `DA_OverlayBase_Masculine`, `ABP_OverlayBase_Masculine`, `Pose_Masculine_Stand_Idle`, `Pose_Masculine_Stand_Move`, `Pose_Masculine_Crouch`, `Poses_Masculine` and inherited base graph are local, unchanged. |
| Rifle layer and transitions | `/GASPALS/OverlaySystem/Overlays/Poses/Rifle/ABP_Overlay_Rifle`, inherited `ABP_OverlayPose_Base` | Original linked graph, pose assets, aim sweep, transitions and grip IK. Source `UpdateOverlayBase` / `UpdateOverlayPose` run after possession has populated the source mesh list. |
| Starts, stops, turns and directional selection | Source `PreCMCTick`, `GetDesiredGait`, `UpdateMovement_PreCMC`, `UpdateRotation_PreCMC`, animation chooser/database path | Wrapper supplies input before source PreCMC/CMC. Original source computes gait, acceleration, braking, friction, facing and directional speeds. Native code does not assign `MaxWalkSpeed` or substitute movement poses. |
| Aim and crouch | Source `CharacterInputState.WantsToAim`, `bIsAimInputDown`, CMC crouch | Existing AI/manual requests populate the actual source input. Grounded state, crouch, velocity and gait are read back from the source CMC/character. |
| Held rifle and muzzle | Original `OverlaySkeletalMesh`, held-object root/socket, source M4A1 | Uses the source attached component. Existing +Y barrel and local `(0,62,9)` fallback muzzle remain applicable: source and previous M4 imported/extended bounds agree. Actual transformed barrel/muzzle and geometry gates remain authoritative. |
| Tactical lean | Existing standing edge behavior | Four added nodes apply component-space additive `spine_01` rotation after the complete source pose. Native lean rotates around the actual rifle axis, interpolates at 120 degrees/world-second and resets during non-locomotion authority. Existing achieved socket displacement/clearance checks remain. |
| Console defaults | Source radius 30; thread-safe animation on; experimental state machine/debug off | Four graph inputs use scoped `msq.GASPALS.*` console variables with those exact defaults. Original owner/global variables are unchanged. Source demo engine/map/render settings are archived, not activated. |
| Strong impact / get-up | Source `StartRagdoll`, `UpdateRagdoll`, `StopRagdoll`, `GetGetUpAnimation`, `RagdollPose` snapshot | Source simulation, actor following, face-up/down get-up selection and montage are retained. A bounded ground/settling/clearance gate requests the original get-up. No custom balance or recovery-step solver. |

### Actual source speed selection

`asset-checks-02.json` evaluates the real source and child `CalculateMaxSpeed` / `CalculateMaxCrouchSpeed` functions on restored CDO inputs. These are function results, **not runtime motion measurements**.

| Source gait / stance | Forward | Side | Backward |
| --- | ---: | ---: | ---: |
| Walk | 200 | 180 | 150 |
| Run | 500 | 350 | 300 |
| Sprint | 700 | 700 | 700 |
| Crouch | 225 | 200 | 180 |

Units: cm/s. Vector X/Y/Z means forward/strafe/backward. `CalculateDirection` uses actual CMC velocity against actor rotation; absolute angle feeds `Curve_StrafeSpeedMap`. Measured curve samples are 0 at 0/45 degrees, 1 at 90 degrees, and 2 at 135/180 degrees. Source lerps X→Y in 0..1 and Y→Z in 1..2 when strafing/controller desired rotation applies; orient-to-movement selects its original forward branch. Source `FixedSpeedSingleGait` supplies full movement input, so the existing walk/run request maps through the source gait selector without a synthetic speed override. Existing AI does not request sprint; its source assets/selection remain intact.

`WantsToAim` / `WantsToStrafe` drive source rotation and overlay behavior. `Ready` and `Relax` manual requests release aim; source timing and movement determine the displayed ready/relaxed state. They no longer force an immediate isolated static pose. The inherited rifle machine contains `Relaxed`, `Ready`, `Aiming`: aim input enters Ready/Aiming; Aiming exit requires released aim or sprint and its source minimum state time; ready/relaxed movement and timeout transitions are unchanged. The fire gate reads **actual Aiming state weight** from this linked machine (index 2, Aiming state 1), rather than trusting the requested stance.

## Physical and combat ownership

Ordinary valid bullet contacts apply damage and one localized impulse while retaining locomotion/combat authority. Only the affected skeletal subtree simulates temporarily; finite parent-space Physics Control drives restore its animation over 0.55 world-seconds. There is no world-space pelvis holding control. Pelvic ordinary contacts transfer their physical impulse to the adjacent simulated spine while CMC retains its support frame. Per-body blend weights fade back to animation; the component-wide force-physics flag is off for this path.

A hit of at least 40 damage, accumulated contacts of at least 60 damage within 0.65 world-seconds, or a hit during get-up requests original source ragdoll. Strong external disturbance uses impulse/body-mass at least 320. Existing fall/lethal impulse multipliers remain bounded at 6 and retain the profile impulse budget. Lethal damage enters Dead; corpse contacts still apply physical impulses. A component ordered after the source ragdoll update disables corpse angular motors so the source flail drive cannot reactivate a corpse.

Living ragdolls may get up after at least 1.1 world-seconds and 0.65 seconds of supported settling. The gate checks source ground contact, pelvis speed below 45 cm/s, angular speed below 1.5 rad/s, walkable floor and standing capsule clearance. Source `StopRagdoll` performs the snapshot/get-up. Combat resumes after the source montage completes on grounded CMC. Missing/failed/unsupported get-up returns to source ragdoll. This is a transition/clearance gate, not a balance solver.

The subclass never invokes the historical fixture/dummy tick or bullet recovery implementation; its inherited recovery physics tick is disabled in the actual native CDO. Reset destroys the owned source pawn/controller, localized controls and owned source display actors, then recreates the same source child. `PoseEpoch` advances. The source rifle stays attached during ragdoll/death; disarming is not added.

Existing AI policy, navigation, knowledge, tactics, weapon cadence/ammo/bursts, finite projectiles, sight and muzzle corridors are retained. Mobile/lean/launch consumers use a shared achieved-pose interface. Source CMC provides actual grounded state, gait, velocity and speed limit. Walking fire/spread uses that directional/stance limit; running fire remains blocked. Source aim weight and the actual barrel alignment still gate launch, including after a localized hit. Ordinary hits do not forcibly cancel tactics, but temporary physical misalignment can naturally delay a shot. Global slowdown and source/world physics clocks remain existing world-time behavior; player movement/camera/arms and bindings are untouched.

## Focused evidence

Frozen evidence: `Saved/GASPALSLocomotion01/Worker/Candidate01/`. `candidate-manifest.json` identifies every production file, DLL, evidence file and archive by SHA-256. `production.zip` preserves the complete scoped delivery and matching DLL. `changed-files.txt` is the exhaustive changed/new file list. Earlier construction failures are retained and superseded by the final passing results below.

| Evidence in `Candidate01/Evidence/` | Result / scope |
| --- | --- |
| `build-04.json`, `build-04.log` | Development Editor Win64 native build PASS, exit 0. Build 01 name-shadowing and build 03 inspection-helper type deduction errors were corrected. |
| `editor-process-build04.json`, `final-asset-check.json` | Ordinary retained lobby, editor PID 50520, UE 5.8.3, matching DLL `178c50517627fb835ce07ef0aabce921aa1abe4a6199795d36977d35d06da472`. Source child/native parent/cvar seam passes; legacy physics tick is disabled. No PIE or dirty packages. |
| `asset-checks-02.json`, `check-cleanup.json` | 40 assertions: nine relevant Blueprint load/compile statuses, source identity/defaults, Masculine/Rifle, real source/child speed functions, original rifle states, 1,478 locally resolving dependency packages. CDO test inputs restored and the two task packages reloaded without saving test changes. |
| `graph-parity-check.json`, `anim-graph-before.json`, `anim-graph-final.json` | All 1,084 original nodes retained. Only original output wiring and four cvar pin literals change; four lean nodes added. No other source pin wiring/default changes. |
| `source-seams.json` | Source physics asset has 23 bodies/23 supported primitive shapes; zero unsupported bullet-sampling shapes. Held-rifle geometry/default evidence retained. |
| `motion-gate-check.json`, `motion-gate-build.log` | 21 assertions compile/run the actual production `FireMotion` header: directional/crouch caps, spread, overspeed, running, stationary aim, authority, airborne, vertical and invalid-limit gates. No engine world or gameplay. |
| `SourceGraph/`, `Reflection/`, `scoped-source-cvars.json` | Exported real source graphs, private/inherited properties, overlay defaults and the authored cvar adaptation. |
| `preservation-check.json`, `owner-project-addition.diff`, `lfs-attributes.txt` | 3,099 initial inputs captured; 3,034 existing binary assets unchanged. All 2,094 source files retain their original hashes. Owner engine config and lobby bytes unchanged; project edit is only plugin enablement. All 2,093 new/copied binary artifact paths use LFS. |

No full feature/animation matrix, visual acceptance or runtime physical success is claimed. Source Blueprint warnings about deprecated gameplay camera nodes remain in source code; their setup path is PlayerController-gated and is not the enemy camera. Packaging/cooking and network multiplayer are outside this editor-prototype verification.

## Preservation, registry input and changed scope

Initial bytes, including owner project/config, native sources and old active GASP binaries, remain in `Saved/GASPALSLocomotion01/Worker/Before/active-inputs.zip` with `identity.json`. The source project is unchanged. The copied original AnimBP is separately preserved at `Assets/Source/GASPALSLocomotion01/Before/ABP_SandboxCharacter.uasset`; a construction-stage derivative is retained under `Worker/Construction/`.

`Assets/Source/GASPALSLocomotion01/intake-manifest.json` and `revision-Candidate01.json` give exact source/destination fingerprints and adaptation relationships. `Scripts/AssetRegistry/manifests/GASPALSLocomotion01-Candidate01.json` prepares 2,098 new candidate artifacts for the controller. It does not assert independent/owner acceptance and no database records were changed. `.gitattributes` gains only task-scoped exact-byte preservation entries while existing LFS filters remain active. Nothing is staged or committed by the executor.

Production source changes are the new `GASPALSLocomotionFixture.h/.cpp` and `GASPALSLocomotionPhysics.cpp`, plus `GASPEnemyFixture.h`, `GASPEnemyRifle.cpp`, `PhysicsControlDummyWorld.cpp`, `CombatAIMobile.h`, `EnemyCombatComponent.cpp`, `EnemyCombatLean.cpp`, `EnemyCombatMobile.cpp`, `EnemyCombatObservation.cpp`. Other additions are the local GASPALS plugin, child Blueprint, source/provenance/registry files, bounded scripts under `Scripts/GASPALSLocomotion01/`, this report, the additive project plugin entry and task-specific Git attributes. The exhaustive per-path inventory is in the candidate manifest/list; controller administrative documents are excluded.

Capacity was inspected before intake: 51.48 GB project and 2.03 GB source plugin, against the 250 GB project ceiling. The frozen manifest records final measured project/archive/free-disk sizes. No duplicate project/worktree or new paid service was used. Native execution settings are preserved in `Worker/Before/execution-settings.json`: Astra, max reasoning, default/standard speed, fast disabled.

## Next owner Play

The editor is left on `/Game/Maps/L_OpeningLobby_PainterStone01` with the matching DLL, Play stopped and clean packages. Start ordinary Play for the existing one-opponent mode. Observe source Masculine movement, directional movement with the rifle, aim entry/exit and crouch; then ordinary hit response, clustered/strong knockdown, source get-up, death and corpse impulses. Use a column for existing standing torso lean. Try **Y** slowdown and **F6** reset through those transitions. Existing `msq.EnemyCombat status` / `trace` explains AI and fire gates; the fixture state adds source gait/speed, actual aim weight, local physical region count and source get-up count.

For manual source-state inspection, `msq.EnemyCombat fixtures` selects the three passive fixtures. Existing `msq.EnemyRifle aim`, `ready`, `relax`, `crouch`, `stand`, `move 0 1 walk`, `move -1 0 walk`, `move 0 -1 run`, `stop` and fixed-target/follow commands remain. Directions are world-space and must be interpreted against the achieved facing. Ready/Relax now obey the source transition timing described above. `msq.EnemyCombat one` restores the autonomous opponent. Visual parity, hit feel, get-up reliability in real contacts and usefulness of lean remain owner Play judgments.
