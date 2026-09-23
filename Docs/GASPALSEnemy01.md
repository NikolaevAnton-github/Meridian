# GASPALS enemy rifle integration

Date: 2026-09-23. Work identifier: **GASPALSEnemy01**.

Delivered directly under the [owner's request](Approvals/GASPALSEnemy01-OwnerStart01.json), outside Multica task creation/runtime. Executor checks and the [sole independent technical review](GASPALSEnemy01Review.md) pass. Controller acceptance and owner motion/play judgement remain distinct.

## Delivered behavior

All three existing GASP/Mover enemy fixtures carry the temporary GASPALS M4A1 and support Relax, Ready and Aim, moving/stopped rifle poses, independent aim heading, pitch and actual Mover crouch. Existing fixture profiles and the combat damage path remain in place.

Physical Recovery, Falling, Down, GettingUp and Dead authority suppress the rifle layer and left grip IK. The rifle stays attached to the physical right hand. The retained recovery snapshot, facing correction, get-up and 0.55-second physical target handoff remain downstream; rifle weight returns gradually after locomotion resumes. The latest x4 fall/x6 lethal impact scaling and leg/fall tuning were not edited.

An observation taken immediately after a hit can still show the previous animation update's rifle weight. Physical source controls are already disabled; the next animation update sets the rifle weight to zero.

## Owner controls

Start Play in the retained lobby and open the existing console with **Tilde (`~`)**. Console commands apply to all three fixtures. Enter one command at a time, then close the console to inspect the result.

| Command | Result |
| --- | --- |
| `msq.EnemyRifle relax` | Lowered rifle pose |
| `msq.EnemyRifle ready` | Ready pose; this is the spawn/reset default |
| `msq.EnemyRifle aim` | Aim and follow the player's camera position |
| `msq.EnemyRifle crouch` | Request actual Mover crouch |
| `msq.EnemyRifle stand` | Return to standing capsule/locomotion |
| `msq.EnemyRifle target -500 0 250` | Aim at a fixed world position in centimeters; use `aim` first to select the aiming pose |
| `msq.EnemyRifle follow 0` | Stop following the player and clear the fixed target |
| `msq.EnemyRifle move 0 1 walk` | Move along world +Y while retaining the aim command |
| `msq.EnemyRifle move -1 0 walk` | Move along world -X |
| `msq.EnemyRifle move 0 -1 run` | Run along world -Y |
| `msq.EnemyRifle stop` | Stop commanded movement |

Existing **LMB** firing, **F6** fixture reset, **Y** relative slowdown and **F10** fixture enable/disable controls are preserved. F6 clears the rifle target, crouch and movement commands and recreates Ready fixtures. Player movement/camera/arms bindings are unchanged. These commands are a small test seam; they do not implement enemy combat AI.

## Implementation and selective transfer

This is a native adaptation of selected GASPALS animation data. It does not directly reuse the source overlay Blueprint graph or replace the current pawn with the source Character/CharacterMovementComponent pawn.

| Source/adopted element | Integration |
| --- | --- |
| Six standing Relax/Ready/Aim Idle/Move poses | Local derivatives and explicit pose evaluation/blending |
| Three crouched Relax/Ready/Aim poses | Local derivatives; selected from actual Mover crouch state |
| Standing/crouched pitch sweeps | Local mesh-space additive derivatives, source time mapping `0.5 - pitch/180` |
| M4A1 mesh, skeleton and two materials | Four local derivatives, references remapped inside `/GASPALSEnemy01` |
| Source `overlay_rifle` socket | Exact hand_r-relative component offset: location `(-7.60517584, 1.43000278, -0.04438320)` cm, yaw 75 degrees |
| Source `HandIK_Left` grip | Bone-space left TwoBoneIK relative to hand_r, using the prop's measured grip position; animated wrist orientation and elbow pole retained |
| Existing GASP Mover AnimBP | Same generated class identity; native rifle parent and 43 added graph nodes before the PreRagdoll cache |
| Source overlay base/layer interface, sample pawn, camera, input, game mode and configuration | Not imported |

The upper-body mask starts at `spine_01`, depth 3, with mesh-space rotation blending. The existing lower-body motion matching, Mover, feet and physical authority pipeline remains active. Pose curves remain baked in the imported sequences; source animation-modifier authoring metadata was removed from the derivatives.

`GASPEnemyRifle.cpp` supplies the attachment and commands. A transient non-player command controller feeds the requested rotation into the source aim/input seam **before** the source producer creates both Mover default inputs and its custom direction/rotation payload. Reset and EndPlay destroy this controller with the fixture. Crouch uses `UCharacterMoverComponent::Crouch/UnCrouch`; measured capsule half height changes from 86 to 60 cm.

### Skeleton and class compatibility

The source skeleton has 88 raw bones. All 88 match the adopted GASP skeleton by index, name, parent and reference transform. The adopted skeleton appends `props_root`, `prop_01` and `poi` (91 raw, 93 including virtual bones). The derivative sequences are reassigned only after this check; the extra unanimated helpers retain their reference pose. This route required no motion retargeting and did not modify either skeleton.

A provisional copied AnimBP was rejected because the retained Chooser contexts require the original `SandboxCharacter_Mover_ABP_C` identity. The controller authorized one bounded in-place adapter to that package. Its exact current pre-edit bytes were archived, not replaced with an older candidate. The provisional copy is retained outside active Content.

### Aim correction and review findings

The retained downstream OffsetRootBone can keep an animation heading different from capsule heading. Replacing the upstream neutral AO result with rifle poses initially lost yaw compensation, producing a recorded ~43-degree stopped/post-get-up barrel error. The correction consumes the existing GASP `AO.X` root-relative yaw and turns the upper body before grip IK. A measured source barrel vector accounts for the authored rifle pose/attachment yaw bias as pitch changes. The imported pitch sweep remains unchanged.

The correction fades between 60 and 110 degrees of root-relative yaw. Rear targets first use the retained turn-in-place behavior; this avoids a physical spine twist when the source AO angle crosses +180/-180 during aim/crouch entry. Final evidence retains a ~40.5-degree root offset after get-up and measures <=0.561-degree settled barrel error, so the result was not obtained by resetting the root.

The earlier authoring-rerun disconnect and inconsistent aim/custom-input payload were corrected. Their source findings and the yaw/initial-turn findings are owned by the sole primary reviewer. Original failing recordings and intermediate builds are retained.

## Focused verification

Evidence root: `Saved/CombatSlice01/GASPALSEnemy01/`. Recordings use the existing ordinary-speed WGC recorder and native input harness. `verification-summary.json` summarizes existing recordings without executing additional tests.

| Evidence | Result and applicability |
| --- | --- |
| `build11.log` | MeridianSquadEditor Win64 Development succeeds on UE 5.8.3 |
| `Pilot02-RiflePoses` | 299 samples: Relax/Ready/Aim, crouch/stand; capsule half height 86/60 cm |
| `Pilot03-AimMovement` | Standing side/back movement, stopped aiming, pitch up/down and crouch movement; original movement acceptance retained |
| `Fix03-AimedStop` | 390 samples: corrected side/back stopped aim and pitch; settled window errors 0.395–1.444 degrees with nonzero root-relative yaw; final rear-cone change has no effect within the exercised settled <60-degree range |
| `Fix04-CrouchHitAim` | 262 samples: stable pre-hit crouched grip, real rifle hit (100→75 HP), Recovery→Falling→Down→GettingUp→Locomotion, commanded crouch return and standing; settled post-get-up barrel error <=0.561 degrees with AO.X 40.54–40.81 degrees |
| `Rollout01-FallGetup` | Three fixtures, actual repeated impacts, fall/get-up and return to commanded movement; physical-authority evidence retained |
| `Rollout02-DeathResetSlow` | 292 samples: death/corpse impacts, F6 epoch 1→2 recreation, 0.25/1.0 world scale and armed crouch/movement; final three foundations/controllers, zero orphans |
| `Final02-ThreeRendered` | 150 samples and clear actual view of profiles 1/2/3; final barrel errors 0.875/0.974/0.875 degrees |

Selected unmodified frames:

- `Video/Fix04-CrouchHitAim-Frames/001.50.png`, `007.30.png`, `009.50.png`: stable pre-hit grip, recovered crouch and standing aim.
- `Video/Fix03-AimedStop-Frames/003.30.png`, `004.90.png`, `006.70.png`, `008.40.png`, `012.70.png`: stopped movement, pitch and resumed stance.
- `Video/Rollout02-DeathResetSlow-Frames/003.50.png`, `005.80.png`, `007.80.png`: corpse, reset/recreation and slowed movement.
- `Video/Final02-ThreeRendered-Frames/004.00.png`: all three armed fixtures.

The initial copied-AnimBP pilot, first observer-recursion run, 43-degree yaw defect, intermediate pitch-bias correction and initial rear-turn instability remain preserved. They are not passing candidate evidence. No full animation/feature matrix or per-profile comparison was performed.

## Source and immutable identities

Original source: `D:/devgames/GASPALS_UE58`, PolygonHive/GASPALS local HEAD `835e0bcf97e9ed7f2dc51efdd6aaa3b44b04121f` (upstream gameplay basis `a6d3812545063f0954b4b80d632848f2eb8032e2`). The source project is unchanged. Source and destination package paths/hashes are recorded in `pose-import.json` and `prop-import.json`; those are intake-stage fingerprints. **Final derivative bytes** are recorded in:

`Saved/CombatSlice01/GASPALSEnemy01/Candidate01-identity.json`

SHA256: `6fe8152f99de22dc832c6c5b5259f670e8f326a51bfaa1060a87c07c7e7d5e32`.

That identity contains 15 imported derivatives, the modified canonical AnimBP, five native implementation files, the plugin descriptor, final DLL hash and owner-preservation hashes. The only existing content package changed is:

`Plugins/GASPEnemyFoundation01/Content/Blueprints/SandboxCharacter_Mover_ABP.uasset`

Its exact pre-edit package is `Assets/Source/GASPALSEnemy01/Before/SandboxCharacter_Mover_ABP.uasset`, SHA256 `4be002ac82435201716c18fbe6e1ec83624515dbe823548c2bcfcc2131b8b963`. The rejected copied-class package is in `Assets/Source/GASPALSEnemy01/ProvisionalCopiedAnimBP/`. Original MSQ-98 manifests and evidence were not rebaselined.

The controller owns `Assets/Source/GASPALSEnemy01/source-manifest.json`, the new revision registration manifest, registry acceptance and local closure commit. Historical registry fingerprints remain historical; the active modified package needs its new revision identity recorded separately.

### Self-contained load and final editor state

`dependency-closure.json` checks hard and soft package references for all 15 derivatives plus the adapted AnimBP: 16 packages, **no `/GASPALS/` references**. Copied preview-mesh and animation-modifier/source-pose metadata were removed/remapped. Existing adopted GASP/Engine dependencies are intentionally reused.

The final build was loaded in a fresh editor without the external plugin argument. `final-editor-state.json` reports zero `/GASPALS` registry assets. `fresh-editor-final.log` records that session; the targeted GASP dependency/Blueprint/Script/Python error scan is empty.

Editor PID 36760 is left open on `/Game/Maps/L_OpeningLobby_PainterStone01`, UE 5.8.3, with Play stopped, no dirty packages and no transient fixtures/controllers. Background throttling is restored, `t.MaxFPS=0`, and the harness has no pending performance override. Owner `DefaultEngine.ini`, `.uproject` and lobby-map hashes match the initial preservation record.

## Limits and next scope

This delivers armed mannequin presentation and command seams. The M4 is the source yellow prototype prop, has no independent collision and stays on the right hand during falls/death. Enemy firing, perception, navigation and autonomous combat remain MSQ-70; disarming and wound gestures remain later work. Pitch is bounded to +/-70 degrees, and rear-target aim waits for body turning. Dynamic pose/physical transitions intentionally release the left grip; settled grip/aim measurements do not promise zero transient error. A shipping/package cook and network replication were not part of this focused editor integration. Owner subjective movement and weapon-pose judgement remains separate.
