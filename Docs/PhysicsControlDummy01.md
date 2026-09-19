# PhysicsControlDummy01 / MSQ-84

Candidate10 retains the removable second Manny in the lobby: a supported
living pose, local physical rifle reactions, passive death, continued corpse
contacts, natural sleep/wake and repeatable reset. Y provides actual world/body
and bullet slowdown while the player remains at normal movement speed.
This is a stationary fixture with distributed world-space springs. It has no
autonomous balance, stepping, recovery from death, AI or final character art.

Prepared 2026-09-19 over MSQ-69 closure `02fb313`, under the
[task](Tasks/PhysicsControlDummy01.md) and
[owner start](Approvals/PhysicsControlDummy01-OwnerStart01.json).
The sole primary reviewer remains `/root/msq84_primary_review`; the controller
owns acceptance, status, registry decisions, closure commit and owner handoff.
Owner play acceptance is separate. No successor was dispatched.

The physical clock check passes in isolated free fall. **Grounded trajectory
correspondence fails:** the normal/quarter comparison differs by up to 36.659 cm
after 0.5 matched simulation seconds, exceeding the original 15 cm tolerance.
The captures also started with different awake/velocity states: normal had a
maximum body speed of 8.006 cm/s, while quarter was asleep. Timestep/contact
sensitivity is a plausible contributor; these captures do not isolate the cause.
The isolated coherent-clock pass does not turn the grounded check into a pass.
Exact correspondence of the grounded collapse remains a limitation for review.

All worker evidence names below are relative to
`Saved/CombatSlice01/PhysicsControlDummy01/Worker/`.

Owner-reported F8 editor shortcut conflict corrected: the current preview key is
Y. Candidate10 and the F8 evidence below remain historical; physics and time logic
are unchanged.

## Play and controls

Open `/Game/Maps/L_OpeningLobby_PainterStone01` and Play. The original enemy still
spawns at `(-1100, 0, 100)` cm, yaw 180 degrees, with its capsule settling on the
floor. The new `APhysicsControlDummy` spawns at `(-950, 110, 8)`, yaw 180 degrees.
Its cyan label identifies the supported fixture or passive corpse. It has no
standing movement capsule. Both fixtures use 100 health and the existing
25-damage rifle; four hits kill the new dummy.

| Input | Behavior |
| --- | --- |
| LMB / RMB / V / R | Existing fire, aim, mode and finite-ammunition reload controls. |
| F6 | Clear projectiles/feedback and reset both fixtures. Ammunition is unchanged. Restore preview time. |
| F7 | Retained original enemy movement preview. It does not animate the new dummy. |
| Y | Toggle this development preview between normal and 0.25 world/body/bullet time. Works before the first shot. |
| F10 | Destroy/recreate only the second dummy and restore preview time when disabling it. Works before firing. |
| Stop / Play | Clean teardown and a fresh session with both fixtures and the ordinary 30/90 ammunition. |

Approach the fixtures for comparison. The entrance pillars can obscure the body
after it falls from a distant/right-hand view. `Candidate08-ClearComparison`
records a clear closer view from the starting player location `(-1080,-100,100)`;
the actual player/camera transforms are in its telemetry. No lobby geometry or
player start asset was edited. F10 or `SetPhysicsDummyEnabled(false)` removes the
experiment. `bEnablePhysicsDummy` is also available on the manager defaults.

Candidate01..09 used F9; all F9 input captures below are historical evidence.
Installed UE 5.8 `Engine/Config/BaseInput.ini:44` also binds F9 to `shot showui`.
Candidate10 moves only the experiment's binding to F10. The engine's existing F9
screenshot shortcut and owner input configuration remain unchanged.

## Physical support and hit contract

The native PhysicsControl component controls all **22 PA_Mannequin bodies**:
pelvis; spine_02 through spine_05; neck_01, neck_02 and head; both clavicles;
upper/lower arms and hands; thighs, calves and feet. The actor refreshes the
existing rifle-idle pose once, records body transforms, pauses animation and
sets full physical blending. The controls target that fixed pose with
`bUseSkeletalAnimation=false`; this is not an animation-only hit effect.

| Setting | Initial profile |
| --- | --- |
| Pelvis support | World-space linear and angular springs, 20 Hz. |
| Other 21 bodies | World-space linear springs at 4 Hz and angular springs at 8 Hz. |
| Drive damping ratio | 1, with bounded editable clamps. |
| Living hit response | Soften the struck arm, leg or trunk region to 0.2 strength, then restore to 1 over 0.3 world seconds. Pelvis support remains active. |
| Bullet impulse | One `AddImpulseAtLocation` on the actual struck body: incoming direction times `min(900 kg cm/s, body mass × 180 cm/s)`. |
| Collision | Retained PA primitives and joints; block WorldStatic, ignore pawn/dynamic collisions. Rifle contacts use the authoritative custom projectile path. |
| Joint limits | Widen ten runtime joint instances to include the selected pose, using Epic's `WidenLimitsForDriveTarget`. Keep these limits through death; restore source defaults before each reset. No PA asset edits. |
| Sleep | Natural Chaos inactivity. Each new physical hit wakes the body; no elapsed-time forced-sleep call. |

Support is distributed across the whole body, not just the pelvis. These elastic
world springs deliberately maintain a shooting fixture; they do not demonstrate
self-balancing. The fields in `PhysicsControlDummy.h` expose the bounded tuning.

The first lethal contact sets health to zero, increments death once, destroys
all living motors and disables their component tick. It does not reposition the
mesh, reinitialize simulation, reset velocity or replace the pose. The lethal
impulse is then applied once. Later physical hits keep health at zero and death
count at one. Immediate impulse telemetry can retain the old velocity because
Chaos processes the queued impulse on the following physics step; actual motion
and wake evidence comes from subsequent frames.

F6 destroys old controls, restores the initial pose, clears linear/angular
velocities, creates fresh controls, resets the contact epoch/history and restores
health. The first subsequent physics step can again have gravity/drive velocity;
the zero-velocity check is taken at reset return, separately from frame sampling.

## Projectile and time policy

The existing rifle's timestamped birth, aim convergence, finite flight and
nonpenetrating consumption remain authoritative. Aim selects the nearest world,
baseline enemy or second-dummy contact and does no damage. The new physical
branch uses `FBodyInstance` transforms and the actual physics asset's 22
sphere/capsule/box primitives, irrespective of health. World sweeps ignore the
dummy actor so they cannot produce a second contact. No invisible standing
capsule remains after death. The original enemy's dead-capsule exclusion and
post-death pass-through remain on their existing path.

The query history retains two rendered-frame poses and each bullet's birth pose.
It interpolates translation/quaternion endpoints within the retained 10 ms
projectile segments and 250 ms maximum processing interval. Capsule rotation
uses a local endpoint chord; inflated box corners are conservative. This is
physics-primitive collision, not triangle-accurate skin contact. Reset epochs
and discontinuity limits suppress teleport sweeps. After a lethal hit, later
scheduled queries in that same processing interval hold the actual frame-end
transition pose: Chaos has not simulated post-impulse subframe motion inside the
shot loop. The next rendered frame resumes physical history. No exact historical
subframe ragdoll trajectory is claimed.

F8 saves world/player/manager/projectile scales. World dilation becomes 0.25;
inverse player and manager actor dilation preserves their prior rates. The
projectile multiplier is 0.25 on the manager's compensated clock, applied once.
Firing births retain the 85 ms schedule. Apply/restore occurs at the end of the
manager frame to avoid mixing deltas. F8 exit, F6, disabling and EndPlay restore
the saved overrides. This is a development preview, not the later slowdown/stop
ability, resource system or an exact physics stop. The old zero-scale/self-hit
evidence is reused; only the new physical body's birth-history seam was checked.

## Focused results and applicability

The pre-verification contract and subsequent explicit implementation corrections
are preserved as `contract-before-verification01.json` and
`contract-correction02..05.json`. Tolerances include 1 cm **or** 1 degree local
response, recovery within 3 seconds, quiet body speed below 12 cm/s, reset position
within 1 cm, reset-return velocity within 0.01 cm/s, 15 cm matched-simulation
body correspondence, 3% bullet-speed and 5% player-speed error. Timing tolerances
are 1e-7 seconds for births, 1e-6 seconds for residual flight and 0.001 cm for
residual position. `clock-diagnosis07.json` preserves the failing grounded check
and the subsequent isolated clock diagnostic before its results.

| Acceptance row | Evidence and result |
| --- | --- |
| Two fixtures | Candidate06 and Candidate08 actual lobby clips; distinct supported Manny beside the retained armed enemy. Historical F9 capture Candidate07-BeforeFireToggle disables/recreates the dummy before any shot. F7 moves the baseline by 91.96 cm while it is disabled. Candidate10 F10 evidence is recorded separately below. |
| Living response | Candidate06-LivingRegions: actual spine_03, lowerarm_l and calf_l contacts. Responses are 0.714 cm / 1.801 degrees, 3.047 cm / 3.057 degrees and 2.241 cm / 1.421 degrees. Late maximum body speed about 8.01 cm/s, restored multipliers, pelvis error below 0.43 cm. Quiet-window head height 166.21–166.24 cm, target error below 0.61 cm and 1.20 degrees. The same primary reviewer closed R1/R2 and passed row 2 on exact Candidate06; those motor/body bytes remain identical in Candidate08. |
| Death continuity | Candidate06-DeathCorpseReset uses the default four-hit health sequence. Release snapshots have zero position/linear/angular-velocity delta and only floating-point quaternion comparison noise. One death, zero controls and one impulse on the lethal contact; actual falling views follow. |
| Corpse contacts | Candidate06 falling and asleep-hit telemetry passes. Candidate08-ClearComparison closes the obstructed-view gap: at t=15.423 a real rifle shot hits sleeping thigh_l, applies one impulse, wakes it for at least 0.905 seconds and moves that body 1.846 cm. Health/death/controls remain 0/1/0. All six rounds are consumed; F6 leaves 24/90 ammo. The original enemy receives no hits. |
| Contact/birth timing | Final `probe-Candidate08.json`: all 17 native checks plus unchanged-player-rifle check pass, including two births in 100 ms, death before the 85 ms birth, valid corpse convergence, only 15 ms residual flight, single corpse consumption, 2 mm world cover, near-body launch and pre-birth exclusion. `probe-baselineCandidate08.json` passes the 12 existing Correction01 checks plus unchanged-rifle check. |
| Slow preview | Candidate07-TimeNormal/TimeQuarter measure actual bullet speed 1000/250 cm/s, restoring to 1000; maximum integrated segment error 1.6e-13 cm. The default-speed lethal shot takes 23.132/92.524 ms. Actual player displacement is 360 cm/s in both walk windows. Candidate08-FreefallNormal/Quarter uses the same actor/rifle in empty space: 0.5 simulation seconds takes 0.5000/2.0001 seconds, maximum body-position difference 3.11 cm. Grounded collapse correspondence fails the original 15 cm check at 36.659 cm, with different initial awake/velocity states (normal maximum 8.006 cm/s, quarter asleep); cause is not isolated. No repeated impulse/death occurs on restore; the largest observed restored body step is 6.42 cm at 385.74 cm/s, consistent with the normal physics step. |
| Reset/cost | Candidate06 active and sleeping resets, Candidate07 slow active reset, Candidate08 native reset-return checks and fresh PIE pass. F6 restores scales to 1 and ammo is unchanged; subsequent real hits work. The one native incremental-cost capture is described below. |
| Preservation/handoff | Historical build11 and Candidate08 fresh load remain applicable to the unchanged gameplay. Candidate10 passes native UE 5.8.1 Development Editor build12 and a fresh retained-lobby load for the F10 correction. Its manifest/preservation records identify the exact DLL/source and unchanged owner assets/configuration. No new binary assets, source downloads, registry replacements, purchases or paused production. Primary review and controller acceptance remain separate. |

Historical Candidate07 changes only F8/F9 manager lookup relative to Candidate06. Candidate08
adds PIE-only freefall verification and immediate-reset assertions; production
motor/contact/time behavior is unchanged from Candidate07. Reuse the applicable
earlier passing clips/probes rather than repeating the full feature matrix.
Candidate09 preserves the owner's exact descriptor line endings around the new
PhysicsControl entry. Its parsed descriptor, all C++ sources and loaded DLL are
identical to Candidate08; no gameplay or plugin selection changes.

Earlier candidates remain preserved. Parent-space trials produced a crouched
pose and jitter; widening limits alone did not solve them. Candidate05's world
springs stabilized the pose but its calf response missed the declared threshold.
Candidate06 added bounded regional softening. Candidate06's first F8 test failed
before firing because it depended on a lazy rifle manager cache; Candidate07
fixes that dependency. These failed versions are not acceptance evidence.

The 1000 cm/s diagnostic shot is a temporary PIE measurement override, not a
changed default rifle speed. Changing that editor property during Candidate07's
recording reconstructed the owning actor and reset its custom dilation at
t=5.05; the displacement comparison was taken earlier, at t=4.7–4.98 while the
player scale was 4. Installed `UActorComponent::ConsolidatedPostEditChange`
calls `RerunConstructionScripts`. Do not use editor-property reconstruction
during the preview as gameplay evidence. Ordinary F8/F6 behavior and the
freefall diagnostic require no such intervention.

## Cost, storage and evidence map

`MSQ84-Candidate07-Cost.csv` is one native CsvProfile capture in fresh PIE at
60 FPS, with the same minimal callback in enabled/disabled phases and no video
or body-JSON sampling. `cost07.json` excludes 30 frames at each phase boundary:
150 enabled and 240 disabled steady frames. Median incremental worker-thread
physics time is **0.231 ms**, game-thread physics **0.023 ms**, body sync
**0.015 ms**, actor ticking **0.033 ms**, and GPU **0.084 ms**. These categories
overlap and must not be summed. Total game-thread median is 5.294 versus 5.378 ms,
so the aggregate difference is below this short capture's noise. The capped
frame median is 16.667 ms in both phases; native capture peak is 16.751 ms.

Three historical F9 disable captures each contain a **400 ms native manager
delivered frame** (the corresponding Slate callback delta is 125 ms):
`Candidate06-ActiveReset.json`, `Candidate07-BeforeFireToggle.json` and
`Candidate09-TimeDisableExit.json`. Candidate09 had no video recorder. One video
capture lost foreground and its incomplete clip is excluded from visual evidence;
foreground loss does not explain all three observations. The retained log records
`ScreenShot00004/00005` around F9 events, consistent with the installed `shot showui`
binding. The screenshot side effect is established; its contribution versus
teardown or other costs to these stalls is not isolated. The existing 250 ms
fail-closed policy rejects an overloaded interval.

The separate minimal native-cost capture above had no comparable stall. It is
not a causal isolation of the historical F9 stalls or the new F10 scenario below.
This short local sample is not a frame-rate guarantee. Contact history is capped
at 32 events. Active projectiles default to 128 and are configurable with a hard
clamp of 256 (`CombatProjectileWorld.h:29`, `CombatProjectileWorld.cpp:160`).

`preservation-final09.json`, `source-inventory09.json`, `storage-final09.json`
and `handoff-manifest09.json` retain the Candidate09 counts, byte measurements and
SHA-256 identities. The project started at 71,511,234,228 bytes against the
250,000,000,000-byte cap. The Candidate09 full project census was 72,040,728,079
bytes, including preserved failed candidates, source/DLL snapshots, raw telemetry
and clips. The small Candidate10 correction records its additional evidence
separately and reuses that census.

| Evidence | Purpose |
| --- | --- |
| `Candidate09/manifest.json`, `Candidate08/manifest.json`, `build11.log`, `state-Candidate08.json`, `handoff-Candidate08.json` | Historical exact source/DLL, applicable native build/fresh load and clean teardown; descriptor-only Candidate09 preservation correction. |
| `metrics06.json`, `metrics07.json`, `freefall08.json`, `finalmetrics08.json` | Reproducible measurements; adjacent scripts retain calculations and raw case files retain input events. |
| `Video/Candidate06-LivingRegions.mp4` | Already reviewed living response. |
| `Video/Candidate06-DeathCorpseReset.mp4`, `Candidate06-SleepWake.json` | Applicable death/falling-hit and sleep/wake records. |
| `Video/Candidate08-ClearComparison.mp4` | Closer actual torso/hand/leg, death, falling and sleeping-body hit, then reset; no property overrides. |
| `Video/Candidate08-SleepContact-excerpt.mp4` | Short unobstructed sleeping-body contact from the previous clip, trimmed only with source timestamps retained. |
| `Video/Candidate07-TimeNormal.mp4`, `Video/Candidate07-TimeQuarter.mp4` | Comparable ordinary-speed recordings of actual preview physics and bullet motion. |
| `Candidate08-FreefallNormal.json`, `Candidate08-FreefallQuarter.json` | Same physical class in an explicitly isolated high placement, stationary flying player observer, unchanged default rifle/impulse; isolates the physical clock without establishing the cause of the grounded correspondence failure. |

Clips use the retained verified foreground recorder with real-time PTS; they are
not slowed playback. Some earlier in-viewport/foreground captures failed and
remain preserved with their logs. Experimental actors and controls are transient;
the new source is in `Source/MeridianSquad/PhysicsControlDummy*` and the existing
combat seam, with focused helpers under `Scripts/PhysicsControlDummy01/`.

## Candidate10 input correction

Candidate10 changes only `CombatRifleComponent.cpp:126`: the second-dummy
`BindKey` uses `EKeys::F10` instead of `EKeys::F9`. A byte-exact replacement check
against Candidate09 confirms every other byte of that file is unchanged. The
other eight source/build files and the owner descriptor match Candidate09.
`Candidate10/manifest.json` identifies all eleven candidate files, including the
new DLL. `Correction01/build12.log` records a successful native Development
Editor build with only `CombatRifleComponent.cpp` compiled. Official Epic MCP
confirms the fresh UE 5.8.1 editor loaded the retained lobby without dirty
packages; `Correction01/loaded-module.json` identifies its loaded project DLL.

The bounded input lookup found no F10 binding in installed `BaseInput.ini`,
project `DefaultInput.ini` or the component before correction. No engine or
owner configuration was changed. F6/F7/F8 and physics, support, contacts, death,
timing and tuning remain byte-identical. The applicable Candidate06..09 visual,
contact, clock and reset evidence above is reused; no full matrix was repeated.
The failed grounded check remains failed.

`Candidate10-F10Toggle.json` records one five-second, 60 FPS scenario through the
retained native `pawn.probe_key` input driver, with no video recorder. F10 at
0.4/1.0 seconds disables/recreates the dummy before firing. F8 at 1.6 seconds
produces world/player/manager/projectile scales `[0.25,4,4,0.25]`; F10 at 2.6
seconds disables it and restores `[1,1,1,1]`, and F10 at 3.5 seconds recreates one
dummy at normal time. All 300 samples retain zero shots and 30/90 ammunition;
actor enumeration finds at most one dummy and exactly one baseline and manager.
`Candidate10-FreshSession.json` adds 72 samples in a fresh 1.2-second PIE session:
one ready living dummy, all scales 1 and ordinary ammunition.

Screenshot counts before / after F10 / after the fresh session are **10/10/10**
files, including **7/7/7** built-in `ScreenShot*.png` files. All file hashes and
modification timestamps match. Screenshot-action log counts are **0/0/0**; the
one unchanged screenshot-related log mention only enables the startup tracing
channel. The log prefix is preserved, so a log restart cannot explain the zero
delta. No unintended screenshot action occurred in this scenario.

Across the 300 F10 samples, native manager frame time has median **16.667 ms**,
p95 **16.667 ms** and maximum **16.795 ms**. Slate callback delta has median
**16.645 ms**, p95 **17.291 ms** and maximum **19.033 ms**. No 400 ms delivered
frame or new overload occurs in this measured window. The cumulative overload
counter was already 1 at the first sample, before any F10 input, with 0.319203
seconds dropped; both values remain unchanged throughout the scenario. Its
earlier cause was not investigated. Fresh-session overload count is zero. The
coarser Python callback wall intervals peak at 32 ms and are reported separately
in `Correction01/focused-results.json`. This single short capture neither
guarantees hitch-free operation nor isolates the cause of the historical F9
stalls; it remains separate from the minimal native-cost capture.

`Correction01/before.json` preserves the original 483 evidence-file identities;
`Correction01/PhysicsControlDummy01-before.md` preserves the exact earlier report
identified by `handoff-manifest09.json`. `Correction01/preservation.json` and
`handoff-manifest10.json` record correction applicability and final identities.
Original Candidate01..09 manifests and evidence remain unchanged. The editor is
left on the retained lobby with PIE stopped, no dirty packages and no leaked
dummy. The handoff returns to the same primary reviewer
`/root/msq84_primary_review`; controller acceptance and closure remain pending.

## Sources

Reuse the existing `SKM_Manny_Simple`, `SK_Mannequin`, `PA_Mannequin` and
`A_EnemyTemplate_Idle` packages and their materials. Their editable sources and
the retained EnemyPrototype01 FBX exports are unchanged; no experimental asset
copy or new LFS binary is needed. Existing provenance is recorded in
[EnemyPrototype01](EnemyPrototype01.md).

The API contract was checked against the installed
`Engine/Plugins/Animation/PhysicsControl/Source/PhysicsControl` component/data
implementation and engine body/constraint APIs. The
[Epic UE 5.8 GASP article](https://www.unrealengine.com/tech-blog/download-the-latest-game-animation-sample-project-now-updated-for-ue-5-8),
published 2026-08-12 and fetched 2026-09-19, provides the powered-ragdoll reference.
The full sample and Mover pawn were not imported. The release-notes fetch timed
out; it was not used as runtime evidence.
