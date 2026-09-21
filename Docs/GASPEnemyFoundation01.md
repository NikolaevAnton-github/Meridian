# GASP enemy foundation — MSQ-98

Implementation record, 2026-09-21. Candidate01 replaces all three active fixtures
with the GASP foundation. The build and six focused executor criteria pass within
the limits below. Controller scope/evidence acceptance and owner motion/play
judgment remain separate under the task-specific independent-review waiver.

## Source and migration

The source is the owner's local `D:/devgames/GameAnimationSample`, loaded with
UE 5.8.1, CL 56057345. The adopted class is
`SandboxCharacter_Mover_Ragdoll`, including its parent Mover character,
`SandboxCharacter_Mover_ABP`, PhysicsControl asset, motion matching databases,
pose history, get-up chooser and Mover montage playback.

Epic AssetTools migrated the recursive hard/soft dependency closure into the
content plugin `/GASPEnemyFoundation01/`. The closure contains 3,017 packages,
4,701,229,766 bytes, with no unresolved package dependencies. It includes
transitive optional character, traversal, interaction and prototyping resources
referenced by the sample graphs; no source world/map was migrated. This is a
dependency closure, not a claim that every copied asset executes in this slice.

`Saved/CombatSlice01/GASPEnemyFoundation01/Worker/migration-result01.json` records
source and migrated file identities. `source-registry-full01.json` records the
dependency graph. `source-preservation-before01.json` preserves original Content,
Config and project-file fingerprints. The original sample is never edited. The
final comparison checks all 3,906 original files with zero changed, missing or
added files. The final plugin contains 3,018 packages, 4,701,512,573 bytes: the
migrated closure plus the new recovery Physics Asset. `asset-inventory01.json`
records every final hash beside its initial migration identity. Four migrated
Blueprints/ABPs were authored or recompiled: `SandboxCharacter_Mover`,
`SandboxCharacter_Mover_Ragdoll`, `SandboxCharacter_Mover_ABP` and
`SandboxCharacter_CMC_ABP`.

The UEFN mannequin retains its 93-bone skeleton and 23 physical bodies. Existing
pelvis, spine, limb, hand and foot names connect to the retained combat and
recovery solver directly; no animation retargeting is performed. GASP animations
and get-ups retain their original skeleton. The old Manny/Mixamo implementation
and all predecessor evidence remain available; the GASP path does not call its
two-clip get-up selector.

## Runtime ownership

`AGASPEnemyFixture` is the logical combat fixture and recovery adapter. Its child
GASP pawn owns the single visible skeletal mesh, physical bodies, capsule, Mover
and PhysicsControl component. The inherited legacy mesh is hidden and does not
simulate. The hidden pose source only evaluates bounded recovery targets.

| State | Animation and physical controls | Capsule / Mover |
|---|---|---|
| Locomotion | GASP motion matching and 45 capped source controls | GASP Walking consumes the persistent movement command |
| Disturbed balance / step | GASP ABP named snapshot from the retained recovery solver; source controls disabled; finite recovery drives only | Ragdoll mode tracks the actual physical pelvis with a stable upright heading |
| Falling / down | Fully simulated body; both control sets disabled; GASP pose history remains active | GASP ragdoll tracking follows the actual body |
| Getting up | GASP actual-pose history override, `CHT_GetUpMontages` selection and Mover montage; source controls only | GASP root motion; continued floor and clearance checks |
| Dead | Terminal simulated corpse; no powered controls or get-up | Ragdoll follows corpse; movement intent remains zero |

Every authority transfer destroys or disables the outgoing drive set before the
incoming set can act. Source profile writes and strength-curve writes are gated
by authority. Autonomous sample NPC get-up is disconnected. Source input/camera
setup is disconnected so the enemy does not bind player controls.

A source-profile hook applies finite caps immediately after profile changes;
per-frame evidence records enabled source/native control counts and any uncapped
source control. Source caps are child mass times 3,500 cm/s² for force and
180,000 cm²/s² for torque. Retained recovery caps remain support-dependent,
including the existing pelvis bound, assistance bounds and no-progress release.

The upright recovery anchor avoids using GASP's prone-body heading projection
while stepping. The capsule follows physical displacement; returning to Walking
does not place the character back at its fixture origin. A raised locomotion
ankle receives a floor-calibrated landing target with neutral foot orientation;
the physical body moves through finite drives and measured contact still decides
whether the landing succeeded.

## Physics calibration and tuning

`PA_MSQ98_Recovery` is a separate derived Physics Asset. Each foot receives one
box measured from the adopted mesh's neutral foot/ball skin vertices (664 sampled
vertices); the bottom aligns to the lowest measured skin, thickness is 6 cm, and
the horizontal footprint uses 90% of the measured extent. Original non-foot
shapes and constraint frames remain. Effective forearm/hand versus trunk collision
is enabled while adjacent joint exclusions remain.

The fixed stepping envelopes for this skeleton are hip 90/45/40, ankle 25/35/75
and knee 8/15/95 degrees in the asset's swing1/swing2/twist frames. Generated
targets cannot widen these bounds. Every intermediate target still passes the
retained reach and joint-limit checks. Original source asset limits are preserved
in the physics audit alongside effective runtime limits.

The retained neutral-pose accommodation remains outside the fixed leg stepping
envelope. The step solver assigns the fixed leg bounds before validating generated
poses. Foot sweeps interpolate the actual foot orientation and use a 0.5 cm floor
contact margin, so a raised/rolled walking ankle can reach its calibrated landing
without a false floor obstruction.

Recovery tempo remains 1.25 by default. Ctrl+F9 retains bounded strength, speed,
reach and persistence assistance. No contact is fabricated from a floor ray.
The source component owner is excluded from support/clearance traces to prevent
the adopted pawn's own capsule from blocking its get-up.

MovieSceneAnimMixer is not enabled: the optional extension conflicts with the
retained purchased-arm AnimBP in this engine build. The two migrated sample ABPs
were recompiled without it. This does not replace GASP motion matching or its
runtime get-up system. Required GASP gameplay tags, DDCVar defaults and the
CharacterCapsule collision profile are scoped configuration additions; the
owner's existing engine/project configuration is preserved.

## Combat and integration interfaces

`SetMovementCommand(WorldDirection, bWalk)` accepts a persistent world-space XY
direction; `StopMovementCommand()` clears it. Physical recovery gates the output,
so a living enemy automatically resumes the pending command after recovery.
`GetMovementPawn()` exposes the owning GASP pawn to future navigation integration.
`SetHandOccupancy(left, right)` is an explicit extension point and creates no
weapon or autonomous behavior.

`ReceiveBullet` uses the existing authoritative regional projectile contact,
one health update and one physical impulse. `ApplyExternalDisturbance` uses the
same bounded recovery entry. Projectile queries exclude the GASP pawn's duplicate
world-blocker representation and retain the wrapper's physical-shape victim.
Death, corpse impacts and `ResetDummy` remain on the same combat interface.

MSQ-70 supplies perception, pursuit and firing decisions through these interfaces.
MSQ-93 retains expanded torso/arm counterbalance; MSQ-94 retains obstacle-aware
improvements; MSQ-95/96 retain uneven/moving support. This task does not accept
those future criteria. The player remains on the retained movement/camera/arms
implementation.

## Verification and handoff

The evidence root is `Saved/CombatSlice01/GASPEnemyFoundation01/Worker/`.
Final01, Final02 and Final03 recordings use the final native build, `build10.log`:
UE 5.8.1 Development Editor, succeeded in 14.04 seconds. `final-analysis02.json`
indexes 13 applicable recordings; `controls-analysis02.json` contains the control
and cadence assertions. Each case below has a same-name JSON observation and a
continuous MP4 under `Video/`.

| Criterion | Focused result | Evidence case or artifact |
|---|---|---|
| 1. Three-fixture rollout | Pass. Three visible GASP fixtures retain profiles 1/2/3 at X -950, Y -320/0/320; shared behavior checked on profile 1. | `Final01-ThreeRendered`; final control recording also identifies class and child counts |
| 2. Movement, impact, recovery and resume | Pass. A real torso hit removes 25 HP, completes one step and returns to Walking at the recovered location. A severe rifle burst causes a physical fall; after two get-up interruptions the enemy completes a GASP get-up and resumes 288.9 cm of commanded movement. | `Final01-MovingRifle`, `Final01-FallInterruptResume`; `Pilot09-MovingTorso` supplies the unobstructed continuous movement view |
| 3. Displaced leg and successive impacts | Pass. The final leg-hit segment completes two steps and returns to locomotion at 3.15 s. The successive-torso case records three real hits, two completed steps and no fall. | `Final01-LegArm`, **0-3.2 s only**; `Pilot08-SuccessiveTorso` |
| 4. Safety, death and physical contact | Pass within flat-floor scope. Two living get-ups are interrupted from the current physical pose. Four live rifle contacts cause one death; nine corpse contacts leave powered controls at zero. Blocked recovery waits for clearance; support loss during get-up returns to unpowered falling. Actual left/right forearm-trunk callbacks carry positive normal impulse. | `Final01-FallInterruptResume`, `Final01-DeathCorpse`, `Final03-Blocked`, `Pilot11-Unsupported`; physics/skin audits |
| 5. Reset, recreation and relative slowdown | Pass. Shot intervals 0.085 s normal / 0.340 s slow; world, bullets and rifle clock 0.25; player custom dilation 2.6 yields net movement 0.65. F6 preserves magazine 17 and reserve 90. F10 removes/recreates 0/3 wrappers and 0/3 GASP pawns, with zero orphan rows. Ctrl+F7/F8/F9 toggle and restore. | `Final02-ControlsSlow`, `controls-analysis02.json` |
| 6. Evidence and interface handoff | Pass. Build, package identities, source preservation, ordinary-speed footage, clock anchors and ownership are supplied. | `Candidate01/manifest.json`, `Candidate01/implementation.zip`, `asset-inventory01.json`, this report and `Docs/GASPEnemyFoundation01Handoff.md` |

At the final fall/get-up authority transitions, observed capsule displacement
between adjacent samples is at most 0.235 cm; the blocked-case maximum is 0.091 cm.
Moving entry continues its physical motion before handover; explicit F6 reset
intentionally returns to the fixture origin. No analyzed row enables source and
native recovery controls together or leaves source controls uncapped. Each recorded
rifle contact applies exactly one impulse. These are sampled runtime checks backed
by synchronous profile gates, not a substep trace.

The final blocked case remains Down until the ceiling is cleared at 7.52 s,
starts get-up at 7.56 s and returns to locomotion at 10.03 s. The unsupported case
removes the actual floor at 6.14 s during get-up, releases controls by 6.18 s and
continues falling. The final blocked recording measures 190 positive
`lowerarm_r/spine_04` callbacks; the interrupted fall records positive left
forearm/hand contacts with pelvis and multiple spine bodies. Counts can include
symmetric component notifications and are not unique-impact counts.

Adaptive leg targets in the final leg-hit segment are 16.47 and 28.76 cm long,
with 7.40 and 10.70 cm lift. The moving hit reaches the bounded 40 cm target and
13.87 cm lift. Normal recovery speed is 1.25; Ctrl+F9 records strength 1.5, speed
1.5, reach 45 cm and persistence 3 s. Actual contact and support measurements
remain required. Settled sole/shape gaps in the moving and successive-torso cases
are approximately -0.5 to -0.8 cm; the leg/hand disturbance reaches about -1.3 cm.
Small compliance penetration remains a physical motion limitation.

### Evidence applicability

The final three-fixture moving case resumes 18.1 cm before the retained lobby wall
stops further travel. `Pilot09-MovingTorso` uses the same upright handover and
corrected foot path in the central opening and resumes approximately 469 cm after
3 s. Later code changes concern falling-body anchoring, observational contact
counters and the three-slot spawn. `Pilot05-Movement` is reused only for the
unchanged command interface: walk 158.4 cm/s, run 360 cm/s, stop and restart.

`Pilot08-SuccessiveTorso` is reused for stationary successive-hit stepping. Later
rotating-foot sweep changes are covered by the moving case and final displaced-leg
sequence. `Pilot11-FallResume`, `Pilot11-Interrupt` and `Pilot11-Unsupported` use
the corrected actual-Chaos-body anchor; subsequent native changes only add contact
counters and replace the three fixture spawns. Their isolated state behavior
remains applicable to the final shared controller. Old Manny footage is not used
to verify the new body or GASP transitions. MSQ-92's accepted tempo/bounded-solver
rationale remains applicable; affected behavior is observed again on GASP.

Earlier failed pilots and logs remain unchanged. `Pilot10-Interrupt` and
`Pilot10-Unsupported` exposed stale animated-pelvis anchoring and are superseded by
Pilot11. `Pilot10-Blocked` is superseded by Final03. `Final01-ControlsSlow` does not
establish automatic cadence because its V press/release coalesced after fixture
creation; Final02 supplies valid cadence evidence. `Final01-LegArm`'s later hand
impulse causes a fall and the recording ends during get-up; only its completed
leg-recovery segment is used for criterion 3. Positive arm/trunk contact is
established by the final fall and blocked recordings instead.

The existing MSQ-68/85/87/91/97/92 observer, native input driver and WGC recorder
are reused through the task adapter. MP4s are continuous and have no edited timing.
Requested gameplay sampling is 30 FPS; WGC captures approximately 15 FPS, with
startup and frame hitches preserved in capture timestamps. Sampled PNG inspection
confirms the three bodies, foot placement, fall/get-up states, visible ceiling and
corpse state; it is not owner motion acceptance. `visual-check01.json` records
the inspected frames. MSQ-82's low-FPS recoil limitation is not re-evaluated.

### Controls, preservation and remaining scope

Play uses the retained lobby and purchased arms. F6 resets fixtures without
refilling ammunition; F10 toggles them; Y toggles relative slowdown; Ctrl+F7 toggles
fixture immortality, Ctrl+F8 infinite reserve and Ctrl+F9 bounded recovery assistance.
Movement commands are an API for MSQ-70, not autonomous enemy AI.

The capacity audit measures 44,980,474,533 bytes, about 45 GB, before the small
candidate snapshot. The retained map hash is unchanged; the owner's exact engine
config prefix and project-file semantics are preserved, with Mover the sole
appended project plugin. See `owner-preservation-after01.json` and
`source-preservation-after01.json`.

The candidate manifest fingerprints all production files and selected evidence.
Its ZIP preserves native code, task scripts, configuration, the compiled module
and five authored/new packages without duplicating the unchanged animation library.
The controller owns asset registration and the closure commit; binary packages
match the repository's LFS rules. Do not rebaseline this manifest.

Severe disturbances can exhaust the physical controller and fall; there is no
arbitrary successful-step count that guarantees survival. Tight wall geometry can
stop movement. The support-removal probe uses a movable diagnostic platform and
can emit Mover's base-relative start-location warning; it establishes safe support
loss only, not moving-platform acceptance. MSQ-93 through MSQ-96 and MSQ-70 remain
later scope. The optional MovieSceneAnimMixer incompatibility and small sole
compliance penetration remain recorded limitations.

The executor stopped every capture-owned PIE session and restored background
throttling and the FPS override. A new Play session started during closure and was
preserved: `final-editor-state01.json` records three fixtures/three GASP pawns,
no dirty packages, background throttling true, MaxFPS 0 and no pending harness
override. No worker commit, registry write, issue-status change or successor
dispatch was performed.
