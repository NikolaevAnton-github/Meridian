# PhysicsControlRecovery01 — MSQ-88 executor handoff

2026-09-20. **Candidate04** corrects the retained six-mannequin experiment with
effective self-collision, measured foot placement and a complete skeletal snapshot
blended into moving get-up animation. The Development Editor build and focused
technical checks pass. Owner play and motion acceptance remain pending under the
[scoped execution decision](Approvals/PhysicsControlRecovery01-OwnerStart01.json).
No independent checks were dispatched.

The immutable handoff is
`Saved/CombatSlice01/PhysicsControlRecovery01/Worker/Candidate04/manifest.json`.
Its native sources, loaded DLL and Physics Asset are byte-identical to Candidate02,
which produced the recordings below. Candidate04 also freezes the final probes,
report and inventory. It supersedes Candidate03's planned idle-editor handoff after
manual owner Play was observed; gameplay bytes did not change.
`focused-results02.json` records evidence applicability;
`changed-files02.json` identifies the task changes. Earlier candidates and failed
recordings remain intact.

## Collision behavior and asset

The effective problem was the mannequin component's PhysicsBody response being
Ignore. Chaos's shape filter requires reciprocal blocking masks. The original
Physics Asset already permitted the required forearm/hand versus trunk pairs;
changing a world-space Physics Control's `bDisableCollision` alone would not fix
the component filter because these controls have no parent body.

The visible component now blocks WorldStatic and PhysicsBody. Pawn, WorldDynamic
and Visibility remain Ignore. `Candidate02-AsymmetricView02-collision.json`
records those live responses and the actual override asset. The rifle still uses
the existing authoritative physical-shape contact path; its native trace/damage
implementation was not changed. The two-calf and interruption recordings contain
actual rifle input, contact and health changes.

`/Game/Development/PhysicsControlRecovery01/PA_Manny_Recovery01` is a derivative of
the shared `/Game/Characters/Mannequins/Rigs/PA_Mannequin`. It has 22 bodies and the
same 92 excluded pairs as the source. `baseline-asset01.json` and
`derivative-asset01.json` contain every shape, exclusion and constraint limit.

| Setting | Candidate behavior |
| --- | --- |
| `lowerarm_l/r`, `hand_l/r` against `pelvis`, `spine_02/03/04/05` | All 20 combinations enabled; the source table already allowed them, and the component now admits contact |
| Overlapping adjacent bodies, including shoulder/chest attachments | Existing exclusions retained |
| Separate mannequins | Explicit Chaos pair exclusions between their bodies; source exclusions are submitted in the same pending map |
| Continuous collision detection | Enabled on each physical body |
| Both foot boxes | Local X dimension 6.5 → 7.0 cm; Y=25, Z=10 cm retained; centers and rotations retained |
| Arm, hand, pelvis and trunk shapes | Source shapes retained after audit and observed transitions |
| Joint limits | Source limits and the retained instance-only widening for the rifle idle remain |

Forearm capsules have radius about 5.30 cm and cylinder length 14.87 cm; upper-arm
capsules use radius 6 cm and length 25 cm. Hand boxes are 16×5×10 cm. Source
shoulder swing/swing/twist limits are 45/45/35 degrees, elbows 5/5/70, wrists
20/60/45. Adjacent constraint collisions stay disabled. No global enabling of
overlapping adjacent pairs was applied.

The engine audit used the installed UE 5.8.1 sources:
`PhysicsCore/Private/ChaosEngineInterface.cpp` for pending exclusions and
`Chaos/Collision/CollisionFilter.h` / `CollisionConstraintFlags.cpp` for pair
filtering. Reset resubmits both the own-asset and cross-fixture exclusions, avoiding
replacement of the own-asset list within one solver timestamp.

Inspected fall, prone, asymmetric, hit-interruption and corpse frames show arms
remaining outside the trunk and returning through supported poses. No persistent
embedded forearm or gross separation was observed in those views. Maximum locked
joint-anchor separation across the eight focused records was 0.675 cm. That metric
supports integrity only; it does not establish natural motion or exhaustive
self-collision coverage.

## Grounding and measured tolerance

The declared visible-sole tolerance is **1 cm above the traced floor**, with no
visible sinking. Calibration reads the actual LOD0 skinned foot/ball vertices,
stores sole landmarks in their driving bone coordinates, and places the idle pose
at the traced surface plus 0.15 cm. The foot collision box face is about 7.9 cm
from the ankle along local foot X; the measured skin extent is about 7.78 cm.
The physical ankle origin is therefore deliberately distinguished from the sole
and from the box bottom.

The old spawn Z=8, recovery origin `floor+10`, standing origin `floor+8` and 26 cm
support reach are removed from this path. Spawn Z is only a floor-search seed.
Reset and the final idle destination use sole calibration. During the moving
animation branch, the complete collision envelope supplies a vertical correction
against the measured floor before blending with the actual fallen snapshot.
The fallen mesh is never teleported for normal recovery.

Support tests use the transformed foot shape's bottom, a default 2 cm reach
(clamped to 0.5–3 cm), and usable-leg state. All drives release in falling, down
and corpse states. Removing the actual platform during get-up also releases every
drive and permits free fall.

The independent geometry measurement here means a second measurement method,
not an independent reviewer: `*-skin-reset.json` and `*-skin-recovered.json`
contain 3,958 actual CPU-skinned foot/ball vertices from the 89-bone LOD0 mesh.
Their per-foot minimum world Z gives the following gaps on floor Z=0:

| Measurement | Left sole, cm | Right sole, cm |
| --- | ---: | ---: |
| Retained baseline standing | 6.300 | 5.897 |
| Candidate reset, Back recording | 0.549 | 0.554 |
| Recovered from back | 0.527 | 0.542 |
| Recovered from prone | 0.521 | 0.579 |
| Recovered asymmetric, corrected camera | 0.525 | 0.535 |
| Recovered under slowdown | 0.526 | 0.541 |

Every recorded STANDING row in the focused set, including F6 settling, stays
inside the 1 cm sole tolerance. The F6 sequence peaks at 0.623 cm. Foot shape
bottoms settle near floor zero; short reset/settling samples include roughly
0.35 cm of solver penetration without the visible sole entering the floor.
The raised-platform fixture starts with floor Z=1000 and soles near 1000.5,
demonstrating floor-relative calibration. These measurements apply to standing;
feet can lift during the get-up motion.

## Snapshot, animation and physics handover

The implementation follows Epic's
[Animation Pose Snapshot](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-pose-snapshot-in-unreal-engine)
snapshot-variable mechanism. Both components are forced to LOD0, avoiding the
missing-bone reference-pose fallback described by Epic. Every captured get-up
snapshot in the evidence has all **89 skeletal bones**, including bones without
Physics Asset bodies.

`UDummyRecoveryAnimInstance` owns a native AnimGraph through `FAnimInstanceProxy`:

```text
Actual FPoseSnapshot ──┐
                      TwoWayBlend ──┐
Moving sequence ──────┘              TwoWayBlend → complete output pose
Calibrated idle FPoseSnapshot ───────┘
```

These are actual `FAnimNode_PoseSnapshot`, sequence-evaluator and two-way-blend
nodes. There is no separately authored Animation Blueprint asset. Explicit
sequence time advances with the existing world-scaled recovery clock throughout
the 0.75-second snapshot blend. The complete output supplies both visible
non-physical bones and the physical-body control targets. The visible mesh's
physical bodies remain simulated at physics blend weight 1.

The hidden pose source evaluates the same graph; it has no collision or rendered
geometry. Root transforms are rebased between component coordinates so alpha zero
reproduces the current fallen skeleton at its actual location. Orientation comes
from the live torso/shoulder plane and head-to-pelvis heading, including a twisted
pelvis. First-target position error is below 4e-13 cm in the focused records;
this is a coordinate check, not a visual smoothness score.

The retained source motion audit shows a nearly stationary beginning in both
Mixamo clips. The runtime traverses the back clip's first 2.3 seconds and the
stomach clip's first 1.2 seconds continuously over the first 0.15 recovery seconds,
then advances at the source rate. The original files, animation assets and full
time ranges remain unchanged. This is an explicit playback-rate adjustment,
including during the snapshot blend. It avoids a new visible pause after replacing
the old fixed-first-frame preparation. A one-second end blend reaches the calibrated
idle. The gameplay state changes to STANDING only after supported completion.

A hit during get-up disables all drives from the current physical pose and
velocities. A retry captures that new complete pose. Death leaves physics active
and prevents further get-up. Health is unchanged by recovery; only the explicit
existing F6 reset starts a fresh healthy epoch.

## Focused records and results

All paths below are relative to
`Saved/CombatSlice01/PhysicsControlRecovery01/Worker/`. Each accepted record has
a matching `Video/<name>.mp4`, `.capture.json`, `.ready.json` and runtime JSON.
Recordings are continuous Windows Graphics Capture of the actual PIE window,
with wall-clock presentation timestamps, normal playback speed and no editing.
Only the explicitly named slowdown episode changes game speed.

| Record | Observed result; runtime seconds |
| --- | --- |
| `Candidate02-Back` | Physical backward disturbance; full snapshot at 2.837; recovered at 10.022, HP 100 |
| `Candidate02-ProneBasis02` | Controlled rigid rotation/translation of the live ragdoll, then natural settling; stomach selected at 1.748; recovered at 10.299, HP 100 |
| `Candidate02-AsymmetricView02` | Two actual calf hits; both legs unavailable and drives off at 1.427; asymmetric settled pose; back get-up 3.932–11.116; HP remains 50 |
| `Candidate02-FrontSettledSlow` | Despite its early probe name this is a back get-up; 3.999 manager seconds correspond to 1.000 recovery second at world 0.25; player effective rate 0.65; recovered at 11.891 |
| `Candidate02-InterruptedDeathReset` | Get-up at 3.924; actual rifle interruption at 5.445 (HP 25); retry at 7.576; lethal hit at 9.096; corpse remains until F6 at 26.017; magazine remains 26 after reset |
| `Candidate02-BlockedAndAnchors` | Ceiling prevents recovery until removed at 7; get-up starts 7.166 and completes 14.354 |
| `Candidate02-UnsupportedView` | Actual floor removed during recovery; FALLING at 3.855, zero drives; pelvis falls from the raised platform to Z=-7380 by recording end |
| `Candidate02-SixRendered` | All six numbered fixtures visible; one manager/controller, no legacy target actors |

All 15,189 runtime samples in these eight records keep the five untargeted
fixtures at HP 100 with zero hits/deaths. Snapshot coverage, sole measurements,
drive release and absence of healing pass the bounded postprocessing checks in
`focused-results02.json`. Existing MSQ-87 rifle/corpse contact evidence is reused;
this task repeats the contact transitions directly coupled to the new handover.
No six-profile behavior matrix was run.

Visual inspection used timestamped frames across each complete recovery, denser
frames through the snapshot blend, and frames around interruption/death/reset.
The views show the back sit-up/crouch, prone push-up/kneel and asymmetric recovery
progressing into standing, without the former fixed-first-frame preparation.
**This frame inspection does not substitute for the owner's real-time motion
judgement.** The continuous ordinary-speed clips are supplied for that gate; no
claim of final natural-motion acceptance is made.

The recorder averages about 20 delivered frames/second. The longest capture gaps
(0.53–0.77 seconds) occur after each active recording while its large JSON is
written, outside the demonstrated recovery. Shorter capture gaps and frame-based
inspection limit conclusions about brief visual artifacts. `*-Frames/` retains
the exact extracted views; the MP4 remains the primary motion evidence.

Two ordinary forward disturbances rolled the ragdoll onto its back, so the prone
case uses an explicitly recorded physical start fixture (`*-seed.json`). It does
not force animation selection or seed the animation's initial pose. This proves
the stomach recovery path from a settled prone body, not the reliability of a
particular forward-fall stimulus. The asymmetry case uses real rifle hits; its
settled left/right sole heights differ by about 3.13 cm, with differing leg poses.

Preserved diagnostic records include Candidate01's early placement/playback
shortcomings, forward falls that rolled over, the first prone setup correction,
and earlier camera/API failures. `Candidate02-Asymmetric02` is numerically valid
but its camera cuts off part of recovery; `AsymmetricView02` closes only that
evidence gap. None of those records or immutable manifests was replaced.

## Build, preservation and delivery boundaries

`build09.log` records the successful UE 5.8.1 Development Editor build. Native
AnimGraph evaluation adds AnimGraphRuntime, RenderCore and RHI dependencies.
Module-local unity compilation is disabled because the added source files exposed
existing collisions between private helpers when unity grouping changed; the
unrelated rifle and character implementations were preserved.

`preservation-after01.json` compares the controller's protected files, original
Mixamo sources/provenance, retained MSQ-87 asset inventory, and the shared Physics
Asset against their recorded hashes. Owner engine/project edits and the lobby
map are preserved. The later Ctrl+F7/Ctrl+F8 test toggles and their documentation
are outside the worker change list. The derived `.uasset` uses the existing Git
LFS rule. `Scripts/AssetRegistry/manifests/PhysicsControlRecovery01.json` is supplied
for controller registration; this executor did not register assets or change
accepted fingerprints.

`storage-after01.json` measures 75.435 GB against the 250 GB limit. All recorded
worker PIE runs ended and restored their temporary performance settings. During
final handoff, a new manual Play session was already active, with player movement,
look and firing counters advancing outside the finished recorder.
`state-owner-session01.json` records that live lobby session and no dirty
map/content packages. It was preserved rather than stopped or reset. The planned
idle-editor assertion correctly rejected this changed live state; no clean-idle
handoff claim is made. F6 resets fixtures, F10 toggles them and Y retains the slowdown preview;
Ctrl+F7/Ctrl+F8 retain the later optional test controls.

Remaining limits: recovery still uses assisted world-space targets and simple
collision primitives. Floor-envelope correction provides vertical support, while
foot sliding and retargeted arm/shoulder motion remain subjects for owner judgement.
The source shoulder exclusions and idle-compatible limits are retained. This
focused result does not establish arbitrary tangled poses, all slopes or a general
locomotion balance system. Manny remains the technical placeholder.

The executor releases the editor writer lease with this handoff. No commit,
issue/profile administration, independent review, registry write, successor
dispatch, new service purchase or unrelated asset save was performed. The
controller owns evidence acceptance, registration, status and the closure commit;
the owner owns final play/motion acceptance.
