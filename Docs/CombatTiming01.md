# CombatTiming01 / MSQ-82

Implemented and worker-verified on 2026-09-19, including the controller's bounded
input-edge, reset-cooldown and final-round feedback corrections. The rifle retains
its 0.085 s interval and consumes one
round per accepted launch. Multiple due shots can now occur in one frame, each
with its own birth pose, timestamp and residual flight. Technical/controller
acceptance, owner play/visual acceptance, issue administration, registry decisions
and the closure commit remain with the controller. No successor was dispatched.

Scope follows [the task](Tasks/CombatTiming01.md),
[execution authorization](Approvals/CombatTiming01-OwnerStart01.json), and the
[fixed time/self-hit contract](Approvals/CombatFoundation01-OwnerScope01.json).
The retained [MSQ-68 report](CombatFoundation01.md) and evidence are unchanged.
Its one-shot-per-frame/no-catch-up behavior is superseded by this report.

Evidence paths below are relative to
`Saved/CombatSlice01/CombatTiming01/Worker/`.

## Clocks, sampling and ordering

`ACombatProjectileWorld::AdvanceFrame` coordinates the single local rifle and
projectiles in `TG_PostUpdateWork`. In installed UE 5.8.1, `LevelTick.cpp` updates
the camera manager after `TG_PostPhysics` and before this group. Previous and
current view/capsule samples therefore describe the same interval. The rifle's
PrePhysics tick observes action eligibility and monitors reload interruption;
it no longer emits automatic rounds independently.

The firing clock is a double-precision accumulation of the delivered world tick
delta. The projectile clock multiplies each eligible flight duration by
`ProjectileTimeScale` once. The seam supports 1, 0.25 and exactly 0, and does not
modify player movement or the firing clock. Global engine time dilation would
already affect the incoming delta: a later world-time ability must choose one
policy and avoid applying its multiplier twice. No player-facing ability or
new binding is added here. Authored reload/animation timing remains on the
existing animation/world clock. Bullet safety expiry, impact display and
transient-prop retirement use real time, independently of frozen simulation age.

Input delivered before the coordinator belongs to the left boundary of its
simulation interval `[start, end)`. This is a sampled-input convention, not a
claim to know an OS event's physical subframe timestamp. A birth exactly at the
right endpoint belongs to the next interval. Each due event advances its own
phase by `max(0.05, ShotInterval)`, including a rejected capacity attempt.

Ordered input and state rules are explicit:

- A delivered eligible press stores one timestamped request independently of
  the eventual held state. Release cancels later automatic continuation but
  retains that initial request. Multiple same-sample press/release edges share
  a timestamp and cannot earn additional shots inside the minimum spacing.
  Semi presses inside the previous accepted shot's cooldown are rejected;
  held automatic fire may continue at the next allowed time.
- Reload/action barriers and successful mode changes cancel pending requests
  at that boundary. Eligibility must hold both in the PrePhysics observation
  and at coordination. A late animation unlock, reload commit or cancellation
  cannot authorize earlier shots in the interval that just elapsed. Held auto
  intent resumes at a new eligible boundary; locked time produces no debt.
- The validated hands-montage reload notify remains the only ammunition
  transfer. The existing once-only instance/mesh/montage checks are retained.
  Dry fire still requires release to rearm, with a 0.3 s feedback-rate limit.
- Reset clears pending/held firing and requires a fresh press without shortening
  the last accepted launch's minimum cooldown. Generation
  invalidation also stops births later in the current interval, suppresses
  stale presentation and cancels queued damage callbacks. A callback-created
  ordinary `Launch` starts at the next frame boundary with zero age/travel.
- Capacity denial reserves no bullet, consumes no round and produces no muzzle
  effect. Recovery uses future schedule slots; denied events never return as a
  burst. Depletion and zero reserve cannot create ammunition.

`GetRifleState` records the last 128 individual accepted births, IDs, positions,
velocities and sessions, plus input-edge and work counters. Verification does
not infer several shots from one `last_shot_time` value.

## Birth history and collision policy

The coordinator linearly interpolates view positions and upright capsule centers
between its endpoint samples, and uses shortest-arc quaternion interpolation for
aim. At each scheduled birth it performs the actual aim and view-to-muzzle cover
queries, then snapshots interpolated birth capsules. Newborn rounds receive only
post-birth flight and capsule motion. New launches do not overwrite older
suspended bullets' movement history. Capsule-size transitions use a conservative
maximum envelope; geometric shooter clearance and the 200 cm uncleared-launch
retirement remain intact.

The local interval is split at shot births and at a 10 ms grid. All bullets in a
collision substep query the same obstruction state before damage/callback delivery.
This preserves the conservative simultaneous-step policy at **substep** resolution,
rather than the former whole render frame. Both rounds hitting a one-hit foreground
target in that substep are consumed before its destruction can expose a rear target.
The next substep can see the changed blocker. Pending contacts sort by absolute
`flight_start + flight_duration * hit_fraction`, then shot ID for exact ties;
fractions from segments with different births/durations are not compared as times.

This is bounded reconstruction, not recorded continuous physics. Within the
supported interval, view/capsule motion is represented by the endpoint chord.
Acceleration, excursions that return between samples, multiple turns exceeding
the shortest-arc interpretation, teleportation and arbitrary deforming/topology
changes cannot be recovered from these samples. A capsule displacement over
250 cm between samples is a history barrier. Noncharacter visibility blockers
are checked by component identity, transform and bounds; a detected movement,
appearance, disappearance or bounds change is also a barrier. Their unrecorded
history is never substituted with current geometry for a historical hit.
Undetected out-and-back motion or a topology change with identical endpoint bounds
is outside this stationary-blocker contract. A new history after initialization
or explicit clearing starts from the available current samples.

## Work budget and overload

| Item | Bound / behavior |
| --- | --- |
| Supported delivered world interval | Up to 0.250 s, with a 1e-8 s boundary comparison tolerance. Controlled 5 ms through 250 ms intervals verified. |
| Collision substep | At most 10 ms; splits also occur at due births. |
| Steps per frame | Hard maximum 32. A 250 ms grid has 25 steps; even six possible birth splits fit within 31. |
| Birth attempts per frame | Hard maximum 6, sized for the retained 50 ms clamp, including endpoint/phase allowance. Ordinary half-open 250 ms windows at this interval contain five births. |
| Active projectiles | Existing default 128, hard maximum 256. At most 8,192 bullet-world sweeps per full-budget frame, plus capsule tests per character and at most 12 rifle aim/cover queries. |
| Shot presentation | One paired fire montage, recoil update and muzzle call per rendered frame with accepted births; no backlog of sound/montage/effect requests. |
| Existing safety limits | 3 simulation seconds / 30,000 cm travel, 120 real seconds since allocation; 48 impact records / 0.3 real seconds; 64 rifle VFX components / 4 real seconds; 64 cosmetic physics props / 8 real seconds. |

For an interval beyond 250 ms, an exhausted work budget, or detected invalid
history, the coordinator retires existing bullets, drops the unsupported interval,
disarms pending/held fire and rebases to its end. It applies no skipped-time damage
and refunds no ammunition. A release/new press resumes normally. There is no
growing debt. This is an explicit prototype safety outcome, including during
bullet stop, and is separate from the retained 120-real-second safety expiry.
The engine can clamp a real stall before delivering its world delta; actual
records label the delivered delta and wall observation separately.

Numeric checks allow 1 microsecond for scheduled times and simulation ages,
0.01 cm for analytic flight distance/position, 0.001 cm for birth pose, and
0.02 cm for long/fine-step position comparison. Float tuning/integration and
quaternion arithmetic justify these small tolerances. Collision destruction
can be conservatively delayed until the end of its at-most-10-ms query batch;
general physics is not claimed bitwise deterministic across frame partitions.

## Presentation and focused verification

PurchasedArms06 asset bytes, 90-degree hip / 78-degree ADS tuning and movement
parameters are unchanged. Several simulated rounds in a low-FPS frame share one
visible recoil/sound/muzzle/animation response. Presentation begins after camera
sampling, so a fire montage's vendor helper must not leave its temporary busy
flag blocking the next frame's authoritative cadence. The implementation clears
that flag only while the just-started fire montage still owns it. Reload and
other action locks remain effective. VFX retirement also runs after the new
post-camera flash so the existing cap holds at the frame boundary.

When a long frame accepts the last magazine round and then encounters an empty
attempt, its accepted fire presentation takes priority. The empty latch/status
still updates, but the dry montage cannot acquire a busy lock and suppress that
round's fire montage, recoil or muzzle. An empty-only frame can play one rate-limited
dry response; a later release/new press rearms it normally.

The independent Python oracle enumerates the intended half-open timestamp lattice,
checks every captured prefix, and compares analytical residual flight and birth
poses. Controlled inputs are distinct from actual Enhanced Input/rendered captures.

| Evidence | Verified result |
| --- | --- |
| `controlled-Candidate01-Cadence{10,30,60,120,144}.json` | Each `[0,2)` interval produces the independent 24 timestamps `0 + n*0.085`, leaving 6 rounds. 10 FPS includes two births in a frame. |
| Controlled Hitch150, Hitch250, Jitter, Clamp50 | Exact 150/250 ms and jittered input intervals retain timestamps/counts/ammunition. The 50 ms clamp produces 20 births in `[0,1)` within the work caps. |
| Controlled Extreme | One 2 s interval performs zero steps/births, retires the old rounds and leaves no debt; only a new press restarts firing. |
| Birth / MoveTurn long and fine captures, scales 1/.25/0 | Distinct births at 0/.085/.170 have ages .250/.165/.080 at scale 1, quarter values at .25, exact zero at stop. Moving/turning poses and residual distances match the independent calculation and 5 ms comparison. |
| Cover25 / Cover300 long and fine captures | Moving/turning launch queries do not spawn through near cover; the 2 mm thin wall consumes each traveled bullet once. |
| Native Contracts and `Correction01/controlled-Native01-Contracts.json` | Absolute-time ordering with reversed insertion, one-hit shielding at 250 ms and 5 ms frame intervals, callback reset cancelling later births, deferred callback bullets, and changed-geometry rejection. |
| ReleaseRepress, Empty, Mode, Reset, ActionLock | No obsolete shots, duplicates or ammunition creation across the stated boundaries. |
| `controlled-Isolated01-ReloadCommit.json`, ReloadCancel, `Actual02-Reload10.json` | One valid transfer/cancellation boundary, no firing during reload, no catch-up on unlock, finite reserve and duplicate-notify rejection. Actual 10 FPS reload transfers six rounds once and ends at 20/84 after 16 launches. |
| `Correction01/controlled-Native01-CapacityRecovery.json` | After capacity rises at .500, accepted timestamps are 0, .510, .595 and .680; four ammo debits, no replay of denied slots. |
| Correction01 BackwardBirth / OlderHistory, long and fine | Backward in-frame births have no pre-birth self contact. An older frozen round survives a later .085 birth, then contacts once at .155 with retained shooter attribution; newer rounds remain frozen. |
| Correction01 SemiQuick / AutoQuick / EmptyQuick / SameSampleRepress / Spacing50 / Spacing85 / barrier ties | One retained delivered press, bounded empty feedback, correct minimum spacing and explicit reload/action/reset priority. |
| Correction02 ResetSpacing85 / ResetSpacing50 / ResetSemiSpacing | Reset at .010 cannot bypass an accepted launch's cooldown: subsequent births occur at .085 / .050 / the later legal semi press at .090, with two total ammunition debits. |
| `Correction02/AfterFix-OneRound10.json` and video | One accepted round receives one fire presentation; the same-frame empty attempt plays no competing dry montage. A later empty press produces one dry montage. |
| `Correction01/Input01-{QuickPair10,EmptyPair10,SampledTap10}.json` | Actual low-FPS raw key pairs produce two semi shots or two dry montages. Enhanced Input delivers their press/release callbacks on adjacent samples; native direct-edge probes separately cover one coordinator interval. |
| `Actual02-Airborne.json`, hip/ADS footage, `Correction01/Input01-StopSelf60.json` | Two ordinary/Shift takeoffs and physical landings with airborne ADS/fire; actual normal movement at 360 cm/s during bullet stop, zero newborn age/travel, one attributed own hit, quarter/normal resume and reset cleanup. |

Actual cadence captures use equal **observed firing-clock windows**, rather than
assuming the recording's requested two seconds were sampled exactly:

| Requested cap | Distinct world observations / wall second | Median delivered frame | Accepted / expected |
| --- | ---: | ---: | ---: |
| 10, final input correction | 9.99 | 100.000 ms | 24 / 24 |
| 30 | 30.01 | 33.333 ms | 24 / 24 |
| 60 | 60.04 | 16.667 ms | 24 / 24 |
| 120 | 118.59 | 8.334 ms; one 45.913 ms frame | 24 / 24 |
| 144 | 143.37 | 6.945 ms | 24 / 24 |

These are measured cap requests, not claims of perfectly fixed hardware frame
rates. The original corrected 10-cap observation includes extra wall overhead
(9.40 observations/s); the final input-correction capture above independently reconfirms
the same 24 timestamps and 20 bounded presentation calls. Actual injected stalls
named Hitch150/Hitch250 measured **139.909 / 225.089 ms** delivered deltas; both
retain all 24 expected births. Exact 150/250 ms coverage is the labelled controlled
probe. A 500 ms wall sleep yields the engine's 400 ms delivered clamp, one overload
and no accumulating automatic debt.

Ordinary-speed recordings are `Video/Actual02-HipADS60.mp4`,
`Video/Actual02-HipADS10.mp4`, `Video/Actual02-Airborne.mp4`, and the final input
correction's `Correction01/Video/Input01-HipADS10.mp4`. Their real-time PTS and
capture metadata are alongside them; external capture samples about 12 frames/s
and does not represent the game's render FPS. Hip/ADS audio WAVs are separate in
`Audio/`. Representative actual frames were visually inspected for coherent
weapon poses, muzzle feedback, readable ammunition and reset. Owner visual
acceptance remains separate.

### Retained low-FPS ADS recovery limitation

The controller identified a visibly enlarged receiver/rear sight after releasing
fire at 10 FPS while still holding ADS. Focused new `Correction02/BeforeFix-ADSRelease10/60`
telemetry/video and `ads-recovery-triage.json` isolate that transition. Aim remains
requested at FOV 78, the ADS procedural translation varies by less than
0.00000003 cm during recovery, the fire montage continues advancing, and no new
shots occur after release. This is not an unintended return to hip or a stuck
ADS request.

The retained Blueprint's `Procedural Offsets.dsl` (export under
`Saved/PurchasedArms02/Worker/SourceGraphs/BP_TFA_BaseCharacter/`) interpolates
TargetRecoil toward identity with `min(world delta, .016) * 22`. Its separate
CalculateSpring uses delivered world delta. Both captures measure the predicted
0.647999972 target-translation multiplier per frame, within 0.000000028 of 0.648.
Consequently, falling to one tenth of the release sample's target recoil takes
0.600001 s at 10 FPS versus 0.100016 s at 60 FPS. Near test time 2.1 s, current
recoil Y is -5.85 versus -1.18 cm and the gun socket sits about 4.75 versus
10.03 cm forward of the camera. By 3.8 s the socket positions converge to
10.622 / 10.625 cm; the decoded held-ADS views also converge.

This establishes a retained frame-dependent procedural-recoil contribution to
the visible difference. The Blueprint bytes, recoil spring/tuning and AddRecoil
implementation are unchanged. The original rifle already applied one AddRecoil
call per accepted frame; the new low-FPS presentation likewise calls it once per
frame, after the character's procedural-offset update. Post-camera montage
presentation changes the sampled montage phase by up to a frame, and random
recoil varies, so this is not a historical-binary pixel comparison or a claim of
identical low/normal-FPS presentation. No unrelated arms retuning was performed.
The enlarged low-FPS recovery remains an explicitly documented visual limitation
for controller/owner assessment. Its source/capture hashes and exact decoded
frame mappings are in the triage JSON.

## Corrections, preservation and handoff

The first actual 10 FPS capture (`Actual01-Cadence10.json`) records the real
20-versus-24-shot failure caused by the fire montage's busy flag. It remains
preserved; Actual02 and the final input correction supply the passing captures.
The first synthetic ReloadCommit request did not start a reload because an earlier
mode montage still held a lock. It is excluded from acceptance; the isolated
replacement verifies an actual transaction. `verification02.json` preserves an
evaluator's incorrect 66-degree ADS assumption and its blocked-movement setup.
The corrected evaluator uses the retained 78-degree target, and the dedicated
clear-space stop/self-contact capture supplies the missing movement evidence.

Correction02 also preserves `BeforeFix-OneRound10.json`: one real round with zero
fire presentations and one competing dry montage. The corrected fresh-editor
record has one round/one fire presentation, then one dry montage only after a
later empty press. These failure records are not relabelled as passing evidence.

Native builds and fresh loads pass. The combined focused evidence evaluator
records **446 passing checks, zero failures** in `verification-complete.json`;
earlier `verification-final.json` belongs to the prior input-correction stage.
The final source changes are checked by the new reset and final-round probes;
unchanged paths reuse the earlier scoped evidence rather than repeating the full
matrix. Candidate01, Actual02, Correction01 and Correction02 remain distinct.
The exact source, report, script and evidence hashes are in `handoff-manifest.json`
and `handoff.json`. Snapshots before the input correction and of that correction
remain under `BeforeInputCorrection01/` and `InputCorrection01/`; Correction02 has
its own `BeforeCorrection02/` and `FinalCorrection02/` source snapshots.

The preservation inventory checks 1,427 starting files. No owner source or asset
is missing; only the four scoped existing rifle/projectile source files changed.
All Content, retained lobby, muzzle brightness, purchased/original source bytes,
owner `Config/DefaultEngine.ini`, MSQ-68 reports and historical evidence remain
preserved. New probes/scripts/report and small extensions to the existing
MSQ-68 transport/recorder are task-scoped additions. No asset resave is required.
Project storage remains about 28.5 GB within the 250 GB cap; exact bytes are in
`preservation-final.json` and `storage-final.json`.

The saved profile, native process arguments and actual turn context verify
Astra/max/default, disabled fast mode and subscription login. No profile change,
paid API, purchase, registry mutation, commit or successor dispatch was performed.
The final official Epic handoff records the retained map, stopped PIE, clean
packages, restored performance settings and zero leaked prototype editor actors.
The controller's AGENTS/ProjectState/approval updates and the owner's config edit
remain outside the worker's change list.
