# GASPALS AI integration audit

Date: 2026-09-24. Existing migration reference: MSQ-121.
Status: **audit complete; current combat behavior fails the basic encounter check**.
Production corrections are not implemented by this audit.

The controller performed this audit personally under the [owner request](Approvals/GASPALSAIAudit01-OwnerRequest01.json), without a new task, Multica run or delegated review. The earlier [technical acceptance](GASPALSLocomotion01Acceptance.md) remains historical evidence of its stated build/source checks. It does not establish working combat after migration.

## Conclusion

The reported behavior is reproducible. The source GASPALS CharacterMovement pawn moves when commanded and the AI sees the player in a clear lane. The active source rifle pose, however, does not align the actual barrel with the target closely enough for the retained launch check. Combat keeps waiting for alignment. Existing tactical logic prevents lateral movement before the first shot and has no bounded recovery from this alignment failure. Together these defects explain an enemy that stands still while repeatedly trying to aim.

This is an integration failure between source locomotion/animation and the retained custom combat controller. GASPALS did not replace perception, tactical selection, navigation, weapon scheduling or projectile simulation. The imported graphs can evaluate successfully while the resulting physical pose fails their combat contract.

The audit also confirms a missed Mover dependency in enemy footsteps, an invalid Physics Control destruction loop and repeated missing physics pose-data warnings in the retained gameplay log. Those are separate defects; they do not explain the clean, undamaged stationary firing reproduction by themselves.

## Baseline and method

- Native/source baseline: `dde5c20bc936b41836fd2276eb5d488e360e38ae`, Candidate02 / Correction01.
- Loaded native DLL SHA-256: `600731ab8e22aba32834ec33bd2b26798377b69879f1de0f70d3a0f28667f3b8`.
- Live editor: UE `5.8.3-58210709+++UE5+Release-5.8`, PID 14348, retained `L_OpeningLobby_PainterStone01`.
- Active foundation: `BP_GASPALSEnemy_Candidate01`, complete source Masculine/Rifle path, `UGASPALSLocomotionAnimInstance`, CharacterMovement. The asset's Candidate01 name is retained within the delivered Candidate02 package.
- Read the active native AI, movement adapter, rifle/animation bridge, source graph exports, physics adapter, projectile/stimulus integration and migration decisions. Compared relevant legacy rifle correction and installed UE Physics Control implementation.
- Inspected the existing gameplay log before the audit's StartPIE at `12:32:09.071 UTC`. These prior sessions contain six logged enemy hits on the player: firing is intermittent, not universally impossible.
- Ran one diagnostic PIE session. Teleported only the transient player to controlled positions; recorded native decision inputs and actual rifle transforms. Temporarily disabled combat for two direct movement commands, then enabled it again.
- Initial editor background throttling produced approximately 3 FPS. Disabled that transient setting for the decisive captures; their frame deltas were approximately 0.0083-0.0099 seconds. Restored the original setting afterward.
- Rider attached to the editor, but the native breakpoint had no associated executable code and pause produced an unknown native frame without source values. No conclusion below relies on that debugger attempt. Removed the two agent breakpoints and detached; the eight existing user exception breakpoints remain unchanged.

No production C++, animation graph, asset, map or configuration was edited; no native build was run. The pre-existing owner modifications to `Config/DefaultEngine.ini` and `MeridianSquad.uproject` remain outside this audit commit. PIE was stopped, the retained editor remains open, and final state reports no PIE worlds and no dirty packages.

## Reproduction results

Raw evidence and the machine-readable summary are under `Saved/GASPALSAIAudit01/`. Files are append-only and fingerprinted in `evidence-manifest.json`.

| Experiment | Recorded result | Interpretation |
| --- | --- | --- |
| Initial lobby spawn/contact probes | Some positions were blocked by actual lobby geometry | These are not evidence of broken perception. Even `snapshot-clear-contact-01.json` was occluded; its label is not an assertion of clear sight. |
| Clear lane, roughly 16 m, `samples-long-open-lane.json` | 10.015 s, 96 samples; visible 96/96; motion ready 96/96; aim weight 1 throughout; barrel error **13.006-15.228 degrees**; launch gate `barrel_alignment` 96/96; shots 0; XY displacement 0 | Reproduces the primary firing and stationary behavior without physical hits, reload, lost contact or unsupported movement. |
| Direct forward walk, combat disabled, 2 s command | 29 samples over 3.000 s; speed reaches **200 cm/s**; sampled displacement 382.057 cm | CMC receives and executes movement. Capture includes stopping and does not start at the exact command instant. |
| Direct forward run, combat disabled, 1 s command | 20 samples over 2.003 s; speed reaches **500 cm/s**; sampled displacement 408.760 cm; `running_gait` veto while moving | Source gait selection works; blocking fire while running is intentional. |
| Combat enabled after movement, roughly 8 m | 49 samples over 5.015 s; visible and motion ready throughout; first pose gate then 48 alignment gates; shots 0; XY displacement 0 | The failure returns after successful movement and reacquisition. |

During setup the enemy also autonomously relocated from its spawn to another position. These observations exclude complete failure of pawn movement or every navigation path. They do not validate all obstacles, gait directions or tactical routes.

Angles are recomputed from the actual rifle local +Y world vector and the native observed target point minus the captured muzzle. The retained rifle uses the fallback muzzle at local `(0, 62, 9)`. `last_launch_gate` is a last-result field and can be stale when no launch check runs; the clear-lane conclusion additionally requires current sight, pose, motion and measured geometric error. The bounded 64-event trace is not a complete encounter replay.

## Findings

### F1 — P1: Source rifle aim does not satisfy the retained firing contract

**Confirmed in source and runtime; immediate gameplay blocker.**

[`EnemyCombatComponent.cpp`](../Source/MeridianSquad/EnemyCombatComponent.cpp), `CanShoot`, lines 223-246, requires an achieved aim pose and actual barrel alignment. The default tolerance is 6 degrees (`EnemyCombatComponent.h:36`). Its configurable range is clamped to 0.5-12 degrees. The stationary clear-lane error remains above even that upper bound.

The active adapter sets the controller rotation toward `GetRifleAimDirection` (`GASPALSLocomotionFixture.cpp:194-227`) and reads the source RifleOverlay state-machine weight (`GetRiflePose`). `UGASPALSLocomotionAnimInstance::NativeUpdateAnimation`, lines 67-86, contributes lean around the barrel axis; it does not implement the old rifle heading correction.

The historical [`GASPALSRifleAnimInstance.cpp`](../Source/MeridianSquad/GASPALSRifleAnimInstance.cpp), `GetRifleAimCorrection`, lines 96-122, explicitly compensates an authored barrel yaw bias and retained-root heading before grip IK. Its calibration vector is `(0.22681, 0.97307, 0.041112)`, approximately 13 degrees of yaw from +Y. The earlier [rifle report](GASPALSEnemy01.md) documents why physical alignment needed correction. This custom correction is absent from the new active source graph path, while the old strict geometric firing gate remains.

The missing equivalent alignment bridge and the measured error establish the broken contract. Separating the exact contributions of authored grip bias, root offset and source aim-offset evaluation requires a corrected-pose experiment; this audit does not claim every observed degree comes from one constant.

**Correction:** adapt actual source aiming to the weapon's physical axis and retained root, preserving source transitions and grip IK. Verify the achieved barrel, not just an aim state weight or control rotation. Removing the safety check or increasing tolerance would hide the mismatch and weaken launch safety.

### F2 — P1: A failed first shot suppresses combat movement indefinitely

**Confirmed policy defect, exposed by F1.**

[`EnemyCombatMobile.cpp`](../Source/MeridianSquad/EnemyCombatMobile.cpp):36 rejects non-approach lateral movement when `Shots == 0`. Within the rifle's effective range of 5,500 cm, the range policy normally holds its useful distance rather than requesting approach. In the reproduction the target is roughly 1,600 cm away and `range_intent` remains `hold_effective_range`.

[`EnemyCombatPolicy.cpp`](../Source/MeridianSquad/EnemyCombatPolicy.cpp), `AdvanceWeapon`, lines 52-75, treats failed alignment as a generic non-obstruction wait. After three seconds it adds a short retry delay and reports `physical aim pending; hold actual feet`. It does not fail the aim action into a bounded reorientation/reposition strategy. That cycle can continue indefinitely. Cover selection can sometimes move an enemy, but it is not a guaranteed escape from this condition; the decisive capture has `cover_phase=none` and `mobile_phase=none` throughout.

**Correction:** make useful tactical movement eligible independently of the lifetime shot counter; give persistent aim failure a specific bounded recovery path. Preserve current visibility, movement authority and actual muzzle checks. This rule existed before the migration; migration made its dependency on successful firing damaging.

### F3 — P2: Enemy footstep stimulus producer still requires Mover

**Confirmed missed migration dependency.**

[`CombatStimulusWorld.cpp`](../Source/MeridianSquad/CombatStimulusWorld.cpp):87-92 obtains `UCharacterMoverComponent` from the foundation and skips the enemy when it is absent. The active CharacterMovement pawn has no such component. Its `EnemyTravel.Advance` and corresponding `Emit` are therefore skipped.

This affects that producer's gameplay footstep events and fallback audible steps. Source animation foley may still play independently. Player footsteps use CharacterMovement already, and stimulus delivery still accepts the enemy fixture; this finding does **not** establish that enemies cannot hear the player.

**Correction:** obtain grounding, achieved travel and gait through the active movement interface/CMC, with a deliberate decision about source foley versus duplicate fallback sound.

### F4 — P2: Reset/end-play destroys controls while iterating their owning array

**Confirmed by installed engine code and an existing runtime ensure.**

[`GASPALSLocomotionFixture.cpp`](../Source/MeridianSquad/GASPALSLocomotionFixture.cpp):103 calls `DestroyControls(PhysicsControl->GetAllControlNames())`.

In installed UE 5.8, `GetAllControlNames()` returns `const TArray<FName>&` into the name records (`PhysicsControlComponent.h:1493`, `.cpp:3167`). `DestroyControls`, `.cpp:769`, iterates that array; destruction removes names from those same records (`PhysicsControlComponentImpl.cpp:886`). The input aliases the container being mutated. UE's `DestroyControlsInSet` deliberately copies the names first.

The retained log records `Array has changed during ranged-for iteration!` at `12:17:32.918 UTC`, with the stack through `DestroySourcePawn`/`EndPlay`, and repeated failures to find `MSQ121_calf_r_foot_r` on destruction/reset. The frozen pre-audit log contains 40 destroy warnings. Two text occurrences of the ensure are one report plus its repeated rendering, not proof of two independent incidents.

**Correction:** copy the control-name array before destruction or use the suitable engine helper that copies it. Verify only reset and PIE teardown for this change. This is a lifecycle error, separate from the pre-hit aiming failure.

### F5 — P2: Physical hit controls repeatedly lack skeletal pose data

**Runtime defect confirmed; deeper cause not yet isolated.**

The pre-audit gameplay log contains **1,084** `Failed to find bone data for ...` warning lines for the active enemy during physical-control activity. These are repeated per-bone/frame messages, not 1,084 distinct incidents.

[`GASPALSLocomotionPhysics.cpp`](../Source/MeridianSquad/GASPALSLocomotionPhysics.cpp) configures local controls with `bUseSkeletalAnimation=true`. In installed `PhysicsControlComponentImpl.cpp`, the reported message comes from an unavailable cached pose/bone-data lookup. The separate missing-bone-index message is different; these logs do not prove that the skeleton lacks its bones.

**Correction/investigation:** establish pose-cache availability and mesh/tick/control lifetime at the first failed hit, then verify a localized hit and the directly affected recovery transition. The audit did not induce new physical hits or isolate whether initialization, cache ownership or parallel pose timing causes the cache failure. Do not attribute the stationary no-hit reproduction to this warning, or claim physical reactions are fully validated.

## Other integration risks and existing design limitations

| Area | Evidence and assessment |
| --- | --- |
| Proposed cover/lean anatomy | `EnemyCombatLean.cpp:17,59-60` uses fixed standing probe heights and a proposed head at 170 cm, chest at 140 cm and weapon/hand at 145 cm. Cover also uses fixed crouch samples. Capsule geometry was corrected in Candidate02, but these anatomical proposals were not derived from the new source pose. Actual source head/weapon positions vary. This can bias candidate selection; no isolated bad cover choice is established by this audit. Achieved lean and launch checks provide later safety checks. |
| Search and range behavior | Inside the large effective range, hold-position and protected observation are deliberate policy choices. The movement planner is a bounded custom collision grid, not a general NavMesh/Behavior Tree migration. These existing choices can look passive even after F1 is fixed. Any aggression redesign is a separate owner decision. |
| Legacy tuning fields | `PursuitSeconds` and `ReturnSeconds` occur only as declarations in the current enemy component. Changing them will not repair the active policy. Expose/document only operative controls when tuning. |
| Tactical geometry scope | Tactical traces use static-world geometry in several paths. Dynamic obstacles/destruction need an explicit future contract; this audit does not certify them. |
| Diagnostic labels | `alignment_and_launch_safety` and `physical aim pending` collapse several possible vetoes. Record the actual current gate, elapsed time and measured barrel error to make failures actionable. |

## Subsystem coverage and limits

| Subsystem | Audit result |
| --- | --- |
| Spawn, ownership, controller, update | Correct active fixture/source pawn/CMC found; AI ticks and produces observations and decisions. The source gait path does not depend on local Enhanced Input in the selected default stick mode. |
| Sight and memory | Clear sight repeatedly refreshes target memory; occluded setup positions correctly lose sight. Source search uses remembered observations. No sight failure explains the primary reproduction. Hearing producer exception: F3. Full hearing/forgetting scenarios were not replayed. |
| Tactical intent and movement | Direct walking/running and one autonomous relocation work. F2 explains stationary combat; cover proposal risk remains. No exhaustive pathfinding or cover acceptance matrix. |
| Animation and aim | Source graphs evaluate and reach aim weight 1; physical barrel contract fails (F1). A valid graph/state is insufficient acceptance evidence. |
| Fire/reload/projectile/damage | The decisive run stops before projectile creation with full magazine, not in reload. Source ownership correction remains present; retained logs prove some projectiles reach the player. Cadence, complete reload and moving-fire behavior were not reaccepted. |
| Local hit, ragdoll/get-up, death/reset | Reviewed adapter and prior logs; F4/F5 remain open. No new ragdoll, corpse, full recovery or damage matrix was run. |
| Performance and time | Full-rate decisive run rules out background 3 FPS as its cause. No scale/load, slowdown or long-duration performance certification. |
| Content and evidence | Source exports and loaded native identity checked. No source assets were altered or re-registered. Original candidate manifests and acceptance reports remain unchanged. |

The prior build, 55 focused correction assertions and retained source/asset checks answered narrower questions, particularly ownership and capsule geometry. They did not run the achieved-barrel-to-first-shot-to-mobile-action chain. Earlier pure motion-gate checks likewise cannot detect F1. This missing integration check explains how a technically accepted migration could still fail basic combat in play.

## Recommended correction order and bounded acceptance

1. **F1: physical aim bridge.** In a clear lane require observed target, achieved pose, barrel within tolerance and a finite burst. Include a turned target and the transition back to settled aim; retain muzzle obstruction protection.
2. **F2: policy recovery.** With first-shot alignment deliberately unavailable, require a bounded diagnostic/recovery outcome and eligible useful movement. No indefinite silent aim loop. Then verify the normal first burst to lateral movement transition.
3. **F4: control destruction.** Copy names and check one reset plus teardown for the ensure and leftover controls.
4. **F5: localized hit cache.** Capture first invalid cache and correct its lifetime/order; check one hit and the affected return to combat. Extend only if evidence identifies another transition.
5. **F3: step producer.** Use active CMC state and verify one measured enemy stride emits the intended event without duplicate foley.
6. Check representative cover/lean proposal geometry against the actual new pose after aiming works. Change it only where measurements demonstrate disagreement.

The audit does not recommend reverting the entire migration or replacing the AI framework. The immediate repair boundary is the movement/pose/combat adapter plus the existing policy's failure handling. Owner judgment of motion and combat feel remains separate from these technical checks.

## Evidence and reproducibility

- [Diagnostic tools](../Scripts/CombatAI01/GASPALSAudit01/README.md): transient PIE operations and capture semantics.
- `Saved/GASPALSAIAudit01/audit-summary.json`: deterministic calculations for all five capture series and prior-log counts.
- `samples-long-open-lane.json` and `samples-reacquire-after-motion.json`: decisive combat observations.
- `samples-manual-walk.json` / `samples-manual-run.json`: movement adapter isolation.
- `samples-combat-baseline.json`: mixed visibility setup; not used as clean-sight proof.
- `snapshot-*.json`: full reflected live state, component inventory and decision trace tails.
- `editor-log-frozen.log`: retained editor log frozen after cleanup; pre-audit counts stop at the recorded StartPIE marker.
- `editor-before.json`, `editor-after.json`, `session-notes.json`: editor identity, cleanup and tool limitations.
- `evidence-manifest.json`: SHA-256/size manifest for evidence and relevant source files.

Large runtime evidence stays under ignored `Saved/`. The report, exact owner request, capture scripts and analyzer are committed locally with the existing MSQ-121 identifier. This audit creates no new execution queue entry.
