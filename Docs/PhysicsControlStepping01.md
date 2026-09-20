# PhysicsControlStepping01 — MSQ-89 executor handoff

2026-09-20. **Candidate05** adds bounded reactive recovery steps to retained
MSQ-88 Candidate04. The Development Editor build and focused self-checks pass.
Independent review is waived by the owner's later
[MSQ-89 decision](Approvals/PhysicsControlStepping01-ReviewWaiver01.json).
The controller owns scope/evidence acceptance and closure; motion and play
acceptance remain with the owner.

The immutable handoff is
`Saved/CombatSlice01/PhysicsControlStepping01/Worker/Candidate05/manifest.json`.
Its native sources, loaded DLL and retained Physics Asset match MSQ-89 Candidate04,
which produced the final stepping recordings. Candidate05 also freezes the final
probe scripts and this report. Earlier manifests and failed records remain intact.
All evidence paths below are relative to that task's `Worker/` directory.
`candidate-validation01.json` verifies every frozen file against its live source
and establishes the shared native/asset hashes with Candidate04.
`evidence-applicability01.json` identifies the recordings and reused evidence.

## Behavior and implementation

A weak disturbance retains the existing local physical reaction and recovery in
place. A larger recoverable disturbance can enter TRANSFER, SWING and SETTLE,
then stand at the displaced stance. One further step can respond to another hit
or measured residual imbalance. Each episode is limited to two steps; excessive
instability, unusable legs, lost support, invalid placement or failure to land
releases every drive into the retained physical fall.

Direction combines the applied impulse with actual pelvis displacement, trunk
lean and pelvis velocity after 0.10 world seconds. The anatomical torso plane
supplies the current heading; direction is evaluated in world space. No fixed
scene axis or hit-point coordinate selects the step. A sagittal step advances
the trailing foot. A lateral step opens with the outside foot, then can bring
the trailing foot toward a wide stance. If only one healthy foot is currently
supported, it becomes the planted foot. Both legs must remain usable.

The procedural route uses the installed native snapshot graph and an analytic
two-bone solve for each leg. All 89 skeletal bones supply the visible pose and
the Physics Control targets together, including toes and non-physical children.
The body transfers toward the support foot, crouches slightly, lifts the swing
foot along an arc, places it and settles. A bounded pelvis height correction
keeps both ankle targets reachable without moving the planted foot. The visible
physical bodies remain fully simulated; the struck region retains its temporary
softening. Instance joint limits follow the generated pose, as in the retained
get-up path.

The short preparation for an eligible step keeps leg targets and foot drives
firm while the trunk reacts. This avoids the old in-place buckling pose pushing
the feet too deeply into the floor before stepping, particularly at 30 FPS.
Weak disturbances continue through the unchanged in-place reaction branch.

Landing saves the complete new standing skeleton and support targets. There is
no actor translation carrying both feet, and ordinary recovery never resets to
`Home`. F6 explicitly restores the calibrated home stance and clears directions,
foot targets, phases, pending requests, episode counters and cooldown. Death
cancels the step immediately and destroys the drives while preserving the current
physical pose and momentum. Recovery does not restore health.

### Tunable proposals

These are engineering defaults, not owner-approved motion values. They are exposed
under `Physics Dummy|Stepping` on the native dummy.

| Property | Default |
| --- | --- |
| `StepTriggerInstability` | 0.32; existing fall threshold remains 1.0 |
| `StepLength` / `StepMaxReach` | 30 / 40 cm; effective length is bounded by both |
| `StepLift` | 11 cm |
| `StepTransferSeconds` / `StepSwingSeconds` / `StepSettleSeconds` | 0.18 / 0.42 / 0.28 world seconds |
| `StepCooldown` | 1.0 world second between settled episodes; 0.08 for an already requested second step |
| `StepFootStrength` | 24; existing body/region strengths remain |

The hard two-step budget, 8 cm maximum reach correction of pelvis height, 5 cm
support-slip safety release, 0.10 second support-loss grace and bounded landing
timeout prevent indefinitely assisted attempts. The measured support-foot
acceptance tolerance is **2 cm horizontally**, tighter than the release threshold.
The retained stable visible-sole tolerance is **0–1 cm above the floor**.

## Placement limits

The destination requires a WorldStatic floor beneath the center and all eight
projected corners of the actual calibrated foot box. Its offset from the ankle
and rotation are included. The complete foot arc is swept in twelve segments,
and the pelvis route checks floor and torso clearance. Floor queries ignore the
dummy itself. The clearance sweep has a 0.5 cm floor-contact margin; physical
contact remains active during the motion.

This trial is verified on the retained flat static lobby floor. Queries reject
normals below Z=0.996 (about five degrees), more than 2 cm of destination height
change, or more than 1 cm of variation across a foot footprint. This is not a
claim of general slope, stair, moving-platform or navigation support. Missing
floor/clearance fails the attempt; the implementation does not force a foot into
an invalid destination.

## Focused results

`build07.log` records the successful UE 5.8.1 Development Editor build.
`Candidate04-focused-results02.json` contains **149 passing checks across 2,758
runtime samples**, including 13 CPU skin audits of 3,958 foot/ball vertices each.
The nine affected step records use a 30 FPS render cap; temporary performance
settings are restored by the retained runner. The unchanged six-fixture view is
reused from Candidate03. There is no per-profile behavior matrix.

Each name below has a runtime JSON and an ordinary-speed, continuous
`Video/<name>.mp4`, with WGC readiness/capture metadata. The renderer and physics
continue normally; the recordings use actual wall-clock presentation timestamps.
Only `SlowReset` changes world/player speed.

| Record | Focused observation |
| --- | --- |
| `Candidate04-Frontal` | One retreat; direction/heading dot = -0.997; stable stance moves 15 cm |
| `Candidate04-BodyLateralTurned` | Body turned 90 degrees; impulse is derived perpendicular to its actual torso front; one lateral step and 15 cm stance displacement |
| `Candidate04-WeakRifleFall` | Weak disturbance returns in place; real rifle contact consumes one round and takes HP 100→75; one step; excessive physical impulse causes a fall; complete snapshot get-up finishes at a stance 21.58 cm from the initial one, still HP 75 |
| `Candidate04-Rehit` | A second disturbance during swing produces exactly two completed steps with updated direction; final stance is displaced 13.02 cm; no queued third step |
| `Candidate04-Blocked` | Real wall fixture rejects the planned step before swing; drives release and the body falls; post-fall pelvis stays below 16.46 cm above the floor |
| `Candidate04-LegLoss` | Support-calf disturbance disables that leg during swing and releases all drives; retained living get-up completes 48.41 cm from the initial stance |
| `Candidate04-Death` | Explicit MaxHealth=25 test fixture; actual rifle contact during swing consumes one round, kills immediately and remains terminal |
| `Candidate04-SlowReset` | Step phase clock advances at 0.24999999 of the manager clock; effective player rate remains 0.65; Ctrl+F7/F8, F6 after stepping and F10 destruction/recreation pass; magazine remains 29 |
| `Candidate04-ResetDuring` | F6 during swing clears all step state, restores home and health in a new reset epoch, and leaves the magazine at 29 |
| `Candidate03-SixRendered` | All six numbered mannequins render; unchanged spawn, assets, idle and HUD make this view applicable to the final candidate |

The five untargeted fixtures keep HP 100, zero hits and zero deaths throughout
the focused samples. All FALLING, DOWN and CORPSE samples have zero enabled drives.
All stepping samples have the complete 89-bone pose. The affected get-ups capture
all 89 bones. The authoritative projectile contact/damage implementation was not
changed; the rifle, lethal contact and ammunition assertions use real native input.

### Actual foot and body measurements

| Completed episode | Peak support ankle drift, cm | Peak swing sole clearance, cm | Actual pelvis transfer toward support, cm |
| --- | ---: | ---: | ---: |
| Frontal | 0.398 | 10.566 | 4.819 |
| Turned lateral | 0.615 | 10.582 | 6.279 |
| Rifle | 0.594 | 10.695 | 6.769 |
| Second-hit episode, step 1 / 2 | 0.398 / 0.474 | 10.566 / 10.808 | 4.819 / 3.521 |
| Slowdown | 0.474 | 10.917 | 6.675 |

Drift compares the same actual ankle origin throughout the step. Landing compares
ankle to ankle target, not the offset foot center of mass. Post-step CPU-skinned
sole gaps are approximately 0.20–0.58 cm. Every post-step STANDING sample meets
the 1 cm tolerance. Stable standing, including reset/recreation and get-up, also
meets it.

The retained weak response briefly reports STANDING while instability is still
decaying from 0.08. At 30 FPS its right sole reaches -0.278 cm for approximately
0.20 seconds of that transition, before returning above the surface. This is
reported rather than described as stable grounding. Stable-ground checks require
zero instability; the separate post-step check includes every STANDING sample.

The first postprocessor also incorrectly required the blocked mannequin to remain
DOWN at the final sample. The retained get-up may retry and abort when its changing
clearance fails, so that assertion was corrected to the actual acceptance: no
step into the wall, physical fall, released fall drives and no suspended body.
`Candidate04-focused-results01.json` preserves both original failed assertions;
`focused-results02` corrects these two measurement assumptions without changing
runtime bytes or repeating gameplay.

## Visual evidence and remaining limits

Inspected timestamped frames show weight transfer, an elevated swing foot, landing,
the new stance, physical collapse and the retained snapshot get-up. Both feet,
trunk and floor are visible in the representative views. The two-step, blocked,
leg-loss, death and slowdown frames correspond to the runtime transitions.
The continuous clips are supplied for the owner's real-time motion judgement;
frame inspection and numerical checks do not establish natural weight or final
animation acceptance.

The retained WGC recorder delivers roughly 16–17 frames/second for these 30 FPS
runs, with a maximum observed capture gap of 0.203 seconds. Brief artifacts between
captured frames are not excluded. The simple collision shapes and retargeted
shoulders remain. Maximum locked-joint separation reaches 3.50 cm transiently in
the death recording at this timestep; no persistent embedded arm was observed in
the inspected views. The wall record includes short, aborted get-up retries.
This remains assisted procedural recovery, with modest persistent knee bend in
the displaced stance, not autonomous balance or final-character motion.

Candidate01 exposed final-leg overextension and an obstructed camera. Candidate02
exposed an ankle/center-of-mass mismatch in the landing check. Candidate03 passed
ordinary steps but exposed excessive pre-step buckling in the lateral 30 FPS
case. Candidate04 fixes these issues. Because its preparation and support choice
change the physical entry pose, the affected step/transition episodes were
recorded again. Unchanged six-fixture rendering, MSQ-88 prone recovery, collision
asset audit and unaffected corpse behavior reuse their applicable evidence.

## Changed files and preservation

`changed-files01.json` supplies hashes and a concise purpose for each task file.

| Files | Change |
| --- | --- |
| `Source/MeridianSquad/PhysicsControlStepping.cpp` | Step selection, full-pose IK, clearance, settling, safety release and telemetry |
| `Source/MeridianSquad/PhysicsControlDummy.h` | Step state, tunables and helpers; remove an inherited stray `фц` prefix before an include, with original bytes preserved in `PhysicsControlDummy-before.h` |
| `Source/MeridianSquad/PhysicsControlDummy.cpp` | Capture standing skeleton, keep local hit response during stepping, cancel steps on death |
| `Source/MeridianSquad/PhysicsControlBalance.cpp` | Integrate step preparation/transition, drive strengths, snapshot sampling mode and recovered stance |
| `Source/MeridianSquad/PhysicsControlBalanceProbes.cpp` | Transient turned-body and wall fixtures, restricted to editor PIE |
| `Scripts/PhysicsControlStepping01/` | Thin extensions to the existing Epic MCP, native-input, runtime/skin and WGC facilities; cases, evaluation and immutable handoff helpers |
| `Docs/PhysicsControlStepping01.md` | This implementation and evidence report |

No binary asset was created or changed; the retained derived Physics Asset and
its registry inventory remain intact. `preservation-after01.json` passes all 11
protected hash comparisons, including owner engine/project edits, lobby map,
original Mixamo sources/provenance, the retained Physics Asset, snapshot graph
and module dependencies. Git reports no changes under Content or Assets.
The controller's concurrently updated task/approval/instruction files are outside
the worker change list. Generated recordings and logs remain under Saved.

`storage-after01.json` measures 33.10 GB in the physical project tree against the
250 GB limit. It excludes 4,178 directory junction/symlink aliases, including
Multica task roots and package-cache links, and conservatively counts hardlink
files separately. The older 75.43 GB logical traversal counted aliases; this is
a measurement-method correction, not reclaimed storage. The complete MSQ-89
task tree was 0.423 GB before the final small candidate/report packaging. No owner
asset or historical candidate was removed.

Native Astra/max/default execution with fast mode disabled is recorded in
`native-execution01.json` and matches the controller's dispatch/profile evidence.
No profile administration occurred. `handoff-final01.json` records the retained
`L_OpeningLobby_PainterStone01` map, PIE stopped, no dirty map/content packages
and no transient probe actors immediately after the executor checks. The final
read in `handoff-owner-session01.json` subsequently found active PIE with native
player input and ammunition use. That owner-controlled session is preserved;
the executor did not stop Play, reset, move the camera or run another probe.
The editor writer lease is released to the owner/controller.
The controller retains task status, registration, acceptance and the local closure
commit; no independent reviewer or successor was dispatched.
