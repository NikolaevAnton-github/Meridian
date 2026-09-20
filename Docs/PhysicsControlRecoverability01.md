# MSQ-97: bounded physical recovery

Candidate07 implements continuous recovery on static flat ground. A leg hit no
longer disables that entire leg, successive steps have no fixed two-step cap,
and Ctrl+F9 increases bounded recovery capacity instead of vetoing falls.
The final UE 5.8.1 Development Editor build succeeds. Executor verification passes
**183 checks across 2,603 recorded states and 20 CPU skin audits**.

Execution follows the [task](Tasks/PhysicsControlRecoverability01.md) and
[task-specific review waiver](Approvals/PhysicsControlRecoverability01-OwnerStart01.json).
This is an executor handoff, not independent review or owner motion acceptance.
The controller owns scope/evidence acceptance, issue status and the local closure
commit. MSQ-92 has not been started.

## Implementation and declared limits

`PhysicsControlRecoverability.cpp` measures mass-weighted body COM and velocity,
trunk rotation, actual foot geometry, recent Chaos ground contacts and slip.
The representative mannequin has 74.973 kg simulated mass. A usable foot requires
an upward solver contact impulse, shape-to-floor gap between -2 and 0.8 cm,
horizontal speed below 55 cm/s, vertical speed below 45 cm/s, and at least two
low footprint corners over flat static ground. Contact freshness is 0.16 world
seconds; sleeping bodies can retain a still-valid close contact. Floor normal Z
must be at least 0.996 and footprint floor-height variation at most 0.6 cm.
A nearby ray by itself does not establish support.

The planar capture estimate is `COM + horizontal_velocity * sqrt(height / 980)`;
height is bounded to 35-130 cm. Distance outside the actual support hull is
combined with reaction travel and braking distance:

`required_reach = hull_distance + speed * response + speed^2 / (2 * acceleration)`.

During a step, the validated future landing footprint may reduce the capacity
estimate, but never counts as a currently supporting foot. Available braking
acceleration is `min(380 * strength, friction * 980)` cm/s². A pending request
has its own clock, which additional hits do not restart. Placement direction
uses measured displacement, velocity, capture error and the real impulse;
the disturbed foot takes priority when the opposite foot can support it.

Recovery requires actual support, reachable placement, trunk lean below the
bounded configured threshold (48 degrees by default), pelvis drop below 42 cm
and trunk angular speed below 5 rad/s. Classification allows 0.14 seconds without
usable support and 0.20 seconds of insufficient capacity; every world drive is
already disabled during unsupported frames. Invalid-capacity time decays at
twice elapsed world time when feasible again. Failed landing has a 0.45 second
bounded extra window. Step support drift above 8 cm also releases the body.

No-progress time is replenished by measured capture-error improvement, useful
completed placement or supported settling, never merely by another bullet.
Landing requires real support, landing error below 3 cm and lean below 25 degrees.
The visible state remains UNSTEADY until supported stability lasts 0.25 seconds;
it does not flash STANDING between consecutive steps. The retained anatomical
leg solver, fixed joint envelope, calibrated sole offsets and living get-up
assets remain in use. Hits retain physical impulses and temporary compliance;
supported active recovery reserves bounded leg and trunk posture effort.

All drives are created disabled with finite limits, including F6/F10 creation.
When support permits them, each body receives a force cap of `mass * 3500 *
strength`; the pelvis uses `mass * 9000 * strength`. Torque caps are `mass *
180000 * strength`. UE units are kg cm/s² and kg cm²/s². Default summed caps are
303,789.25 force units and 13,495,079 torque units. The force limit is per solver
axis, not a measured total force. Zero means unlimited in PhysicsControl and is
never used as a capacity limit. Falling, down and dead states release all drives.
Get-up can use actual body-ground contact while feet are not yet planted; losing
that contact disables drives, pauses recovery time and eventually releases again.

This is a bounded assisted controller, not an inverse-dynamics balance solver.
World-space springs supply external assistance; their finite caps do not prove
human strength or exact contact force distribution. Friction is a configurable
capacity estimate checked against observed slip, not a solved friction cone or
the measured material coefficient. `pelvis_demand_ratio` estimates uncoupled
spring demand relative to its cap; it is not motor-load telemetry. Partial edge
contact, finite contact freshness, compliant joints and solver timing remain
approximations. The `1000` capture distance when no support hull exists is an
invalid-support sentinel, not a measured reachable distance.

## Enemy settings and owner controls

Settings are reusable properties on `PhysicsControlDummy`; all three existing
identities and hit-reaction profiles are preserved. They share ordinary defaults.

| Property | Default | Effective bound / meaning |
| --- | ---: | --- |
| `RecoveryStrength` | 1 | 0.25-2; drive caps and braking capacity |
| `RecoverySpeed` | 1 | 0.5-1.8; reaction and step phase duration |
| `RecoveryReactionSeconds` | 0.10 s | 0.06-0.30 s, divided by effective speed |
| `StepMaxReach` | 40 cm | 12-45 cm; existing reachable-placement setting |
| `RecoveryPersistenceSeconds` | 2 s | 0.5-4 s without measured progress |
| `RecoveryFriction` | 0.6 | 0.1-1 capacity estimate |
| `RecoveryLegStrength` | 0.35 | 0.15-1 minimum temporary leg-strength multiplier |

Existing phase defaults are transfer 0.18 s, swing 0.42 s and settle 0.28 s,
divided by effective speed. Step length/lift and further replanning remain the
MSQ-92 refinement boundary. Legacy leg-disable/count-instability settings no
longer decide support or force a fall.

The HUD says **Ctrl+F9 bounded recovery assist: ON/OFF**. Assistance multiplies
strength by 1.5, speed by 1.2 and persistence by 1.5, adds 5 cm reach, and still
obeys the bounds above. Default effective values become 1.5 / 1.2 / 3 s / 45 cm;
summed force cap is 455,683.94. Assistance defaults off in each new session and
persists through F6 and F10 within a session. Ctrl+F7 remains separate immortality.
The old native input function name `ToggleDummyFallPrevention` is retained for
binding compatibility; its implementation toggles bounded assistance.

## Focused evidence

All filenames below are relative to
`Saved/CombatSlice01/PhysicsControlRecoverability01/Worker/`.
Each runtime record has a matching continuous `Video/<name>.mp4` and WGC capture
timestamps. Firing uses the retained native input/rifle/projectile path. Tracking
aim and inspection cameras are probe conveniences; inspection views hide only
the first-person presentation. No direct disturbance substitutes for rifle cases.

| Criterion | Record and measured result |
| --- | --- |
| Baseline leg failure | `Baseline-OneLeg01`: real `calf_l` hit at 1.038 s, fall at 1.138 s because the leg was disabled despite the other usable foot. Baseline sources/DLL are frozen in `Baseline01`. |
| Leg replant | `Candidate07-OneLeg`: one real `calf_l` bullet, health 75, one completed step, no fall. Left foot moves 30.90 cm; right foot net displacement 0.067 cm; pelvis moves 15.54 cm. Peak planted drift 0.324 cm. `Candidate06-OneLegComparable` preserves the baseline camera for the before/after comparison and recovers with two steps. |
| Continuous torso fire and resumption | `Candidate07-TorsoBurstResume`: 27 uninterrupted bullets, then 3 resumed bullets before settling; all 30 hit torso (29 `spine_03`, 1 `spine_02`). At speed 1.5 and Ctrl+F9 off, steps 1-3 complete at 1.927 / 2.625 / 3.361 s while fire is held. Release at 3.461 s, resume at 3.629 s. Five steps complete in total; STANDING at 5.027 s, no fall. Ctrl+F7 is on solely to prevent health depletion. |
| Feasible disturbance of both legs | `Candidate06-BothWeak`: simultaneous controlled 600-unit impulses on both calves, two steps, no fall. Peak required reach 9.54 cm within the 40 cm capacity; actual support remains available. These are two impulses, not a penetrating bullet. |
| Infeasible support loss with assistance | `Candidate06-NoSupportAssist`: remove the transient flat support platform at 1.031 s. Both feet lose contact; all 22 drives are disabled by 1.065 s, FALLING by 1.198 s despite Ctrl+F9. The pelvis continues physical downward motion; no new support is supplied. |
| Actual leg-to-leg collision and living recovery | `Candidate06-LegContactWeak`: one left-calf controlled impulse, actual magnitude 2,411.325 kg cm/s after the existing mass/velocity cap, at strength 0.25. `foot_l` contacts `calf_r` at 1.662 s with a 209.332 kg cm/s solver impulse. The opposite leg receives no injected impulse. Landing fails at 2.462 s, drives release, retained back get-up completes at 11.864 s, final health 100. |
| One bounded settings comparison | `Candidate06-TorsoRearOrdinary` / `Candidate06-TorsoRearFast`: same profile 1, camera and timed real torso-fire input. Only speed changes 1 to 1.5. Completed steps change 4 to 6; both settle without falling. This is a measured capacity example, not an enemy-profile ranking. |
| Changed transitions | `Candidate06-DeathDuring`: the second real bullet kills during SWING and clears drives immediately. `Candidate07-Controls`: F6 cancels a swing, F10 removes/recreates exactly profiles 1-3, assistance persists until switched off. `Candidate06-SlowEpisode`: active step follows world time at 0.25, while player action rate is 0.65 (custom dilation 2.6), then settles after normal time resumes. `Candidate07-ThreeRendered` visibly shows all three mannequins. |

At the isolated collision, right-calf velocity changes from
`[9.884, -3.476, -1.325]` to `[28.330, -18.620, -4.659]` cm/s.
Right support-foot slip rises from 0.238 to 19.417 cm/s in the next sample; peak
support drift reaches 3.571 cm. The support initially remains contact-feasible,
but the obstructed swing misses the bounded landing window. This is evaluated
through the same support/landing controller rather than a special collision-fall
flag. Joint coupling also transfers motion; these observations do not isolate
every component of velocity change to the contact impulse alone.

The unchanged candidate Physics Asset is
`/Game/Development/PhysicsControlRecovery01/PA_Manny_Recovery01`. All nine
opposite-side thigh/calf/foot pairs are enabled; 92 other selective exclusions
remain. `baseline-asset01.json` records geometry and exclusions, and byte
preservation establishes applicability to Candidate07. No binary asset derivative
or asset re-registration is required.

Across the successful focused recovery records, peak support drift is 0.704 cm,
maximum settled knee-to-toe mismatch 13.733 degrees, and maximum measured segment
length change below 0.23 cm. Twenty settled CPU skin audits place sole minima
0.220-0.478 cm above the floor, inside the retained 1 cm tolerance. These are
engineering diagnostics; the failed-contact fall is not included in successful
stance statistics. Actual Chaos motion can overshoot compliant joint constraints;
the target-envelope check is not a zero-overshoot claim.

WGC captures retain real elapsed playback time with roughly 15-17 captured FPS
while the probes request 30 game FPS. Occasional capture gaps reach 0.55 s in the
control/reset record; the final burst's maximum gap is 0.375 s. They are ordinary
speed continuous recordings, not guaranteed 30 FPS or frame-perfect motion
evidence. Owner motion/play judgement remains open.

## Candidate identity, corrections and preservation

`Candidate07/manifest.json` freezes the final native sources, loaded build DLL,
unchanged Physics Asset, task scripts and this report. `build08.log` is the final
successful build. `self-checks02.json` contains the 183 explicit assertions and
deciding measurements; `evaluate97.py` reuses the retained geometry audit and
reads evidence without rerunning gameplay. The earlier evaluation and its exact
script remain as `self-checks01.json` / `self-checks01-evaluator.py`.

Candidate07 changes from Candidate06 are restricted to finite disabled drive
creation, a telemetry-only strength denominator correction, removal of startup
diagnostic logging and correction of a stale preset comment. Spawn, F6/F10,
one-leg recovery, sustained torso fire and rendering were rechecked. Candidate06
evidence for the unchanged post-initialization settings, support-loss, collision,
death and slowdown branches is reused. `evidence-applicability01.json` records
the exact source diffs and hashes; no claim of identical Candidate06/07 DLLs is
made. Baseline and earlier candidate manifests remain immutable.

Earlier attempts are preserved. Candidates01/02 falsely rejected startup edge
contacts; Diagnostic03 identified contact aging before evaluation of the previous
physics snapshot, including a loading hitch. Candidate04 corrected that ordering
and low-edge support, then exposed rejection of a feasible future landing.
Candidate05 included future placement in capacity but torso hits could continually
remove posture effort. Candidate06 added the bounded supported posture reserve.
Ordinary-strength collision probes that never made contact and a larger two-leg
impulse that remained recoverable are retained as such, not counted as the
required collision or unrecoverable evidence. Front-side torso probes included
arm interception and were replaced by verified torso views. The first overview
was occluded by pillars; the final view shows all three. The first Candidate07
burst left only one round for resumption; `TorsoBurstResume` reserves three.

`preservation-after01.json` verifies six protected current files and nine earlier
frozen manifests, including MSQ-91 Candidate07 and MSQ-89 Candidate05. Owner
`DefaultEngine.ini`, `.uproject`, lobby map, original asset and recovery graph
sources remain unchanged. There are no Content/Assets changes. Physical project
storage was 34.18 GB before the final small evidence package, excluding directory
junction aliases, within 250 GB. No paid service, new asset, successor dispatch,
worker commit, registry change or issue-status administration was performed.

Configured profile, native process arguments and native session context confirm
**gpt-6-astra / max / default**, fast mode disabled (`native-execution01.json` and
the controller's saved profile/process records). No profile settings were changed.
One writer and one heavy workload were used throughout.

The original lobby and viewport camera were preserved. Each owned test ended PIE
and restored temporary frame-rate/throttling settings. Subsequent external Play
activity was left untouched. At writer-lease release, PIE was running with no
dirty packages; `handoff-release01.json` records that live state and the unchanged
camera. Editor PID 32184 uses the final build and remains available to the owner.
There is no pending capture or build process.

Projectile penetration through both legs remains a future integration case:
current projectiles stop at first contact. Uneven/moving terrain, walking/AI,
new get-up animations and expanded counter-motion remain outside this delivery.
