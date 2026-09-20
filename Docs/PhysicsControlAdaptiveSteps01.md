# MSQ-92: adaptive recovery steps

Candidate06 is the immutable review package for disturbance-driven recovery steps
on static flat support. Its native sources and DLL are identical to Candidate05,
tested with Development Editor build06. The ordinary adjustable `RecoverySpeed`
default is now **1.25**. The focused executor evaluation passes **208/208 checks
across 1,606 recorded states**, with seven final CPU-skinned sole audits.
Independent technical review and owner motion/play judgement remain pending.

Execution follows [MSQ-92](Tasks/PhysicsControlAdaptiveSteps01.md) and the
[owner start and tempo instruction](Approvals/PhysicsControlAdaptiveSteps01-OwnerStart01.json).
The baseline is MSQ-97 Candidate07, closure commit `5cd5b67`; its 21 relevant
native/build/asset entries matched before mutation. Native session context,
process settings and configured profile all confirm Astra/max/default, with fast
mode disabled. No profile changes were made.

All evidence paths below are relative to
`Saved/CombatSlice01/PhysicsControlAdaptiveSteps01/Worker/` unless prefixed with
another task. `Candidate06/manifest.json` binds original paths to frozen copies
using `frozen_path`; `MSQ92-Candidate06-Evidence.zip` contains those copies and the
manifest. `candidate06-validation01.json` records the manifest/archive hashes,
entry verification and storage bound. Historical candidates remain unchanged.

## Behavior and implementation choices

At step entry, the controller combines measured body displacement, trunk lean
relative to the neutral trunk, mass-weighted horizontal velocity, capture error
and disturbed-foot motion. Hit impulse contributes a limited feed-forward term.
The existing direction calculation and actual support determine where and which
foot can move. A usable opposite foot still permits replanting a struck leg.
When a committed stance differs from neutral by more than 8 cm, the next ordinary
step chooses the leg that reduces that error along the recovery direction. This
avoids repeatedly opening the same foot when changing hit direction crosses the
existing lateral/sagittal classification boundary.

These numbers are implementation choices, not owner-approved tuning constants:

| Quantity | Selection or bound |
| --- | --- |
| Effective speed | `clamp(RecoverySpeed * (assist ? 1.2 : 1), 0.5, 1.8)`; ordinary 1.25, assisted 1.5 |
| Impulse contribution | `min(4 cm, horizontal impulse / body mass * 0.12 s)` |
| Placement demand | `1.1 * body offset + 0.65 * capture distance + 0.10 * horizontal speed + 0.35 * foot displacement + 1.5 cm/degree * lean excursion + impulse contribution` |
| Ordinary step length | `clamp(8 cm + demand, 8 cm, effective reach)`; ordinary reach 40 cm, assisted 45 cm |
| Urgency | Clamp the maximum of `body offset / 20 cm`, `speed / 100 cm/s`, `absolute lean / 35 degrees` to 0–1 |
| Length ratio | Selected length divided by `clamp(StepLength, 12, 40)`; `StepLength=30 cm` is the reference |
| Lift | `clamp(StepLift * (0.25 + 0.75 * ratio) + lean * 0.03, 6, 18) cm`; `StepLift=11 cm` is the reference |
| Transfer | `clamp(StepTransferSeconds, 0.12, 0.35) / speed * (1 - 0.15 * urgency)` |
| Swing | `clamp(StepSwingSeconds, 0.25, 0.75) / speed * clamp(0.80 + 0.25 * ratio, 0.85, 1.15) / (1 + 0.20 * urgency)` |
| Settle | `clamp(StepSettleSeconds, 0.2, 0.6) / speed` |

Defaults before division/adaptation remain 0.18/0.42/0.28 s. At speed 1.25 those
are nominally 0.144/0.336/0.224 s; geometry and urgency then modify transfer and
swing. Reaction is 0.10/1.25 = 0.08 s. A longer step can take slightly longer
while moving the foot faster. Speed and geometry adaptation are separate inputs.
Rifle impulse, damage, global/player slowdown and death/get-up playback are unchanged.

Each proposed arc must pass the existing floor placement and swept foot-box
checks, plus pure target solves at five transfer, twelve swing and four settle
samples. These use the retained reach, anatomical bend and fixed joint envelope;
they do not move the mesh or widen limits to fit a candidate. Ordinary placement
also reserves a following stance correction within `effective reach - 0.5 cm`.
If geometry is infeasible, a finite search tries at most four lengths, shortening
by 20 percent toward an 8 cm floor. Corrective steps aim toward neutral separation,
are capped to effective reach and can also be shortened. Failure releases to the
existing physical fallback. There is no restored two-step episode cap.

An active step freezes its lift and phase durations. A new disturbance waits at
least 0.04 world seconds for body response, then may update the landing endpoint:

- At most two accepted replans, 4 cm per update and 6 cm total per step.
- The change uses velocity difference times 0.12 s and a capped 3,000-unit impulse
  contribution times 0.08 s/body mass; changes below 0.5 cm are ignored.
- A smoothstep blend over 0.12 world seconds bounds endpoint speed to 50 cm/s.
  Replanning is allowed before half swing, only if the whole blend ends by
  85 percent swing. It never restarts the step clock or extends its deadline.
- Corrective, late or exhausted updates leave the hit's next-step request intact.
  A proposed joint-infeasible replan keeps the validated committed arc; invalid
  floor placement/path causes a physical fall. The blended path is checked again.

The predecessor's usable-support, finite actuator effort, reach and measured
progress rules remain active. In particular, contact loss, invalid capacity and
no progress still exhaust their original bounds. `CancelStep` now clears all
adaptive entry, geometry, timing and replan fields, including during reset/fall/death.

## Focused measurements and visible evidence

The primary pair uses profile 1, the same close camera, default speed 1.25 and
assistance off. At approximately 1 s the retained physical disturbance seam
applies `[600, 0, 0]` or `[6600, 0, 0]` kg cm/s to `spine_05`. This is an actual
body impulse, not a posed animation or a change to rifle impulse strength.

| First-step measurement | `Candidate05-Small` | `Candidate05-Large` |
| --- | ---: | ---: |
| Entry trunk lean / neutral excursion | 5.54 / 0.90 degrees | 8.61 / 3.19 degrees |
| Entry horizontal COM velocity (x, y) | (0.14, -1.36) cm/s | (2.18, -1.32) cm/s |
| Selected length / lift | 12.33 / 6.31 cm | 19.61 / 8.40 cm |
| Actual horizontal foot displacement | 12.25 cm | 19.50 cm |
| Actual pelvis displacement | 6.24 cm | 9.82 cm |
| Peak measured sole height | 5.85 cm | 7.61 cm |
| Transfer / swing / settle | 0.141 / 0.294 / 0.224 s | 0.139 / 0.309 / 0.224 s |
| Actual active step duration | 0.667 s | 0.700 s |
| Peak planted-foot drift | 0.251 cm | 0.261 cm |
| Completed steps / final result | 1 / STANDING | 2 / STANDING |

The stronger input moves the first foot 1.59 times farther. The additional
19.70 cm correction restores the final stance. Selected average swing travel
increases from about 41.9 to 63.6 cm/s. The sequence shows weight transfer,
placement and the following correction; the lift difference is modest and is
less clear in an isolated frame against the patterned floor. Use the continuous
videos for motion judgement. `selected-views01.json` ties initial, transfer,
apex and final PNGs to probe/video monotonic clocks without changing playback.

| Focused record | Outcome |
| --- | --- |
| `Candidate05-Replan` | Initial `[1800,0,0]` torso impulse, then `[0,-1300,0]` in early swing. One replan travels 1.775 cm at a measured maximum 20.995 cm/s; the 0.667 s step deadline is unchanged. Two steps finish, no fall. |
| `Candidate03-Blocked02` | A transient 16×30×24 cm obstacle is inserted at the landing target during swing at 1.292 s. FALLING follows at 1.325 s with drives released. DOWN at 2.792 s and retained get-up starts at 3.392 s. This short record does not claim completed get-up. |
| `Candidate03-Slow` | A real calf bullet starts a step; relative slowdown changes world to 0.25 and player action rate to 0.65 (custom dilation 2.6). Phase time follows world time, then recovery finishes after normal time resumes. |
| `Candidate03-Controls` | F6 during swing clears new adaptive state; F10 removes and recreates exactly profiles 1–3 with clean state. |
| `Candidate03-Rifle` / `Candidate03-ReferenceSpeed` | The same real `calf_l` bullet, 900-unit configured impulse, produces the same selected 12.84 cm geometry. Speed 1.25 versus 1.0 changes configured phases from 0.176/0.370/0.280 to 0.141/0.296/0.224 s. Actual duration is 0.667 versus 0.833 s; reaction is 0.08 versus 0.10 s. This measures the requested 25 percent speed increase independently of geometry. |
| `Candidate05-TorsoTempo` | Twelve actual `spine_03` bullets during a one-second automatic burst at default speed 1.25. Three steps finish, STANDING at 3.867 s, no fall. First-step replans exhaust the 2-update/6 cm limit without extending its 0.667 s duration. The second actual placement is 35.35 cm and completes in 0.700 s. Ctrl+F7 is on only to prevent health depletion; recovery assistance is off. |
| `Candidate03-ThreeRendered` | The overview visibly retains all three mannequin identities; shared behavior is exercised on profile 1. |

`self-checks04.json` records the 208 assertions and per-step measurements. Across
the accepted records, peak planted drift is 0.428 cm, final knee-to-toe divergence
is at most 14.15 degrees, and recorded final sole gaps are 0.283–0.471 cm. Seven
CPU skin audits independently check final rendered foot vertices within 0–1 cm
of the floor. Moving anatomical geometry retains segment lengths, bend direction
and the fixed target joint envelope. The smallest sampled swing gap is 0.122 cm
in the stronger torso episode; interior samples exceed the 0.1 cm check. This is
a sampled sole estimate, not a continuous skinned-mesh clearance proof.

The ten ordinary-speed WGC videos are under `Video/` with `.capture.json` source
times and `.ready.json` clock origins. Captured cadence is 15.6–16.3 FPS, with
maximum individual gaps of 0.093–0.188 s. Source timestamps are retained rather
than speeding up the recording. The full transition remains available, but short
motion details need the telemetry as well as the capture. `visual-self-check01.json`
records the executor's inspected views; it is not the independent review.

## Evidence applicability and retained attempts

`evidence-applicability02.json` records exact source diffs, hashes and the six
reused Candidate03 records. Version 02 corrects the predecessor contact record's
name to `Candidate06-LegContactWeak`; version 01 remains preserved. After
Candidate03, only stepping source and its DLL changed: subsequent-foot choice,
the future stance reservation, and bounded partial corrective placement. The
reused episodes enter from neutral (actual entry error below 2 cm, versus the new
8 cm selector), pass geometry on the first trial, and remain well inside the new
39.5 cm stance reservation. Their selected paths, timings and drives are unchanged.
The primary pair, replan and repeated torso episode were recorded on final native
Candidate05. Candidate06 adds the complete delivery package, with no native edit.

Predecessor evidence is reused only for the unchanged criteria below:

| MSQ-97 evidence | Applicable scope |
| --- | --- |
| `Candidate07-OneLeg`, `Candidate07-TorsoBurstResume` | Rifle hit/contact routing, successive recovery request/progress behavior and finite support/effort controller. New scaling and tempo use MSQ-92 evidence. |
| `Candidate06-NoSupportAssist` | Actual contact feasibility, zero powered drives without support and bounded assistance capacity. |
| `Candidate06-LegContactWeak` | Retained Physics Asset inter-leg contacts, physical fall and living get-up. MSQ-92 independently exercises blocked landing and release. |
| `Candidate06-DeathDuring` | Unchanged damage/death branch and terminal drive release. Shared cancellation additionally clears adaptive fields, checked here through reset/fall. |

No new damage/death/get-up animation matrix or per-profile motion comparison was
run. Sixteen relevant native/asset files remain byte-identical to MSQ-97; the
applicability record lists them. `PhysicsControlRecoverability.cpp`, recovery and
animation implementation, rifle/projectile/HUD files and the Physics Asset are
unchanged. Adaptive work is restricted to `PhysicsControlDummy.h`,
`PhysicsControlStepping.cpp`, `PhysicsControlBalance.cpp` and
`PhysicsControlBalanceProbes.cpp`, plus task tooling/report.

Candidate01–05 and their original manifests remain preserved. Candidate02–04
torso attempts exposed infeasible long arcs and the repeated same-foot stance
choice. Pure whole-arc validation, bounded shortening and then stance-aware foot
selection resolve those recorded failures. After repeated geometry failures,
diagnosis used recorded joint/stance measurements instead of rerunning the same
case unchanged. The earlier blocked-wall attempt missed the swing; a later hook
was reset by predecessor status polling. Neither counts as fallback evidence.
`Blocked02` inserts the obstacle successfully and records the physical fall.
An early Candidate01 capture ended before its requested tail; it is retained and
excluded. Older failing self-check outputs and evaluator copies remain intact.

## Handoff and limits

Development Editor build06 succeeds; native Candidate05/DLL identity is retained
in Candidate06. Preservation checks confirm the owner's engine settings, project
descriptor and retained lobby map, unchanged animation/asset bytes, and the
MSQ-97 Candidate07, MSQ-91 Candidate07, MSQ-89 Candidate05 and five MSQ-92 frozen
manifests. `preservation-after01.json`, `storage-after01.json` and final package
validation record the results. Generated records remain outside Git; project
storage, including the final package and archive, stays below 250 GB. No Content
or Assets write, asset-registry operation, commit or issue/profile administration
was performed by the executor. Unrelated owner/controller changes are preserved.

The executor released the editor writer lease on editor PID 40712 after official
Epic MCP confirmed the intended project and retained lobby, no PIE, no dirty
packages and no transient probe actors. See `handoff-candidate06.json` and
`writer-release01.json`. The final build is loaded and ready for owner Play;
task-owned captures, input runs and builds have ended. Temporary test timing and
performance settings were restored by the existing runner.

This remains finite externally assisted recovery, with an estimated support/
momentum model and sampled geometric validation. Compliant actual joints can
overshoot their targets. The roughly 1.2 mm minimum sampled swing clearance and
capture cadence are relevant limits for the primary reviewer. Static flat support
is the only terrain envelope; navigation, pursuit, general walking, expanded
counter-motion, new abilities and MSQ-93 onward remain outside scope. Final
tuning can change after owner play feedback. The controller owns independent
technical review dispatch, scope/evidence acceptance, closure administration and
the required local task commit.
