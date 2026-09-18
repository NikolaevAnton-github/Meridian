# PurchasedArms04: jump from Shift running

MSQ-64 worker handoff, 2026-09-18, **Correction01**. The jump and the controller-requested
presentation correction are verified. Controller review, acceptance, issue closure
and the local task commit remain controller-owned. The retained lobby is open,
PIE is stopped, and no maps or assets are dirty.

## Result

Space now jumps from the existing Shift run. Established fast movement uses
352 cm/s vertical takeoff instead of the ordinary 320 cm/s, with unchanged gravity.
The boost requires the source run/sprint state and actual planar speed above the
ordinary 360 cm/s. Stationary Shift does not grant extra height.

The character retains achieved horizontal speed through flight, including after
Shift is released. There is no horizontal launch impulse or dash. CharacterMovement
still owns velocity, acceleration, air control and collision. Landing restores
320 cm/s and clears the retained speed cap. Held Shift continues running;
released Shift returns to walking. Alt uses the same vertical boost with its
existing 720 cm/s tactical-sprint speed, without another amplified jump tier.
Mappings, source hold thresholds and busy/crouch/airborne gates are preserved.

The initial candidate had a presentation defect: restoring the physical run flags
also selected the lowered running animation underneath an idle-authored additive
jump. The rifle nearly disappeared from view. **Correction01 replaces that
incompatible animation combination through the entire landing tail**, while
preserving the physical speed and input state. The initial visual-success
conclusion is superseded; its exact report, videos and measurements are preserved.

## Implementation and diagnosis

The initial native adapter admits only the jump through the source `PlayJump` and
shared montage gates: it clears the speed flags during the synchronous call, then
restores them immediately. Other source actions retain their original gates and
busy/notifies. This physically correct change exposed a pose combination that the
vendor's original run/sprint prohibition had prevented.

The live asset audit confirms `A_TFA_FP_AR_Jump_Full` is a local-space additive
referenced to `A_TFA_FP_AR_Idle_Pose_Standing`. The source locomotion state machine
feeds an absolute run/sprint pose into the jump slot, and its Run End additive
sits downstream. At jump phase about 0.50 seconds, the initial held-Shift gun
control was approximately -32.40 cm in camera-space Z, versus -15.73 cm in the
ordinary reference. The controller's actual 1.50-second video frame shows almost
no rifle or arms. Montage activation alone did not establish visual correctness.

Correction01 introduces an animation-only `bUseOrdinaryJumpBase` snapshot. It is
computed on the game thread from a jump started in a fast state and the actual
montage instance, including paused flight and nonzero blend-out weight. It is
not tied only to `IsFalling`, `Landed` or `Montage_IsActive`, which end too soon.

Seven transition conditions in the existing FP AnimBP consume that snapshot:

- Standing-to-run/sprint requires the original condition and no protected jump;
  run/sprint-to-standing also permits a protected jump. Existing transition
  blends choose the ordinary standing/walking base for the additive jump.
- The run-transition layer stays in its reference-pose Run state while protected.
  It cannot add Run End over the airborne or landing montage. After the tail,
  its original transitions again follow the current held/released input state.

This changes explicit animation rules, avoiding hidden runtime edits to generated
node memory. Physical run/sprint flags, movement limits, camera/mesh anchors,
source clips, montage/notifies, and generic busy ownership are unchanged by the
correction. The jump still holds around montage time 0.65 while falling and
resumes its 0.85 landing tail at actual floor contact.

## Focused verification

All trajectory takes use the retained lobby's flat center aisle, starting at
(-1600, 0, 100), facing +X. The existing native input probe drives real bindings.
Measurements use capsule position/velocity, collision landing, evaluated pose
frames, and continued native movement-input delivery.

| Correction01 take | Planar speed in flight | Apex rise | Sampled travel | Recovery |
| --- | ---: | ---: | ---: | --- |
| Ordinary | 360 cm/s | 52.24 cm | 240.25 cm | Ordinary walk; presentation guard never enabled |
| Shift held | 540 cm/s | 63.20 cm | 392.14 cm | Running, with the full landing tail first |
| Shift released in flight | 540 cm/s | 63.21 cm | 395.45 cm | Walking after landing; momentum preserved in flight |
| Subsequent ordinary jump in that session | 360 cm/s | 52.24 cm | 238.43 cm | 320 cm/s; no boost or presentation leakage |
| Alt held | 720 cm/s | 63.22 cm | 522.39 cm | Same vertical boost; tactical sprint restored |

The Shift apex is about 21% higher and travel about 64% farther than walking.
Most of the distance difference comes from the existing 540 versus 360 cm/s
speeds; the +10% vertical takeoff adds about 10% flight time. No extra horizontal
velocity is applied. Sampled flight boundaries are about 0.67 versus 0.73 seconds.
Travel is measured from the last grounded sample to the first after collision
landing, with up to one telemetry interval of boundary uncertainty. The initial
and corrected takes agree within that sampling variation.

The correction uses four short video takes only: ordinary, Shift held,
Shift released plus the subsequent ordinary jump, and one Alt case. There are
1,707 samples at approximately 100-108 Hz. The animation guard remains enabled
through 0.434-0.438 seconds after landing, including the montage's blend-out;
physical held/released flags continue to follow input throughout. A repeated
Space press in the released-Shift flight still produces no extra jump.

Actual decoded video frames were inspected across takeoff, airborne, landing
and recovery phases. The rifle is visibly retained where the first candidate
lost it. At matched jump phase around 0.50 seconds the corrected held-Shift gun
control is about -15.69 cm in camera-space Z. Held and released Shift and Alt
use a compatible pose throughout the tail, then return through the existing
locomotion blends. These are unscaled presentation coordinates, not pixel-size
measurements. Owner visual acceptance remains separate.

The earlier isolated stationary-Shift, crouch and busy-input checks still stand:
stationary Shift gave ordinary height and zero travel; crouched and busy requests
were rejected. The correction does not alter those gates, so they were not rerun.
There was no shooting, full reload, ADS, traversal or unrelated animation sweep.

## Evidence and preservation

Evidence root: `Saved/PurchasedArms04/Worker/`. Current correction evidence:

- `Correction01/build.log`: native build passed. `editor-cold.log`,
  `cold-contract.json` and `log-check.json`: fresh editor loads the saved graph,
  all seven guards are present, the existing ADS component-space/+90-degree
  basis conversion is preserved, and no relevant script/Blueprint/load errors
  were found. Only the affected graph/load contract was checked.
- `Correction01/graph-audit-before.json`, `graph-fix.json`, `pose-diagnosis.json`:
  live additive reference, transition connections, exact binary change and
  phase-matched initial pose evidence. The controller's original review and
  extracted images remain under `Saved/PurchasedArms04/Controller/`.
- `Correction01-*.json`, `Correction01/analysis.json`: actual input, trajectory,
  pose, landing-tail protection, recovery and ordinary-jump reset checks.
- `Video/Correction01-Ordinary.mp4`, `Correction01-ShiftHeld.mp4`,
  `Correction01-ShiftReleased.mp4`, `Correction01-Alt.mp4`: actual foreground
  recordings. `Correction01/*-sequence.jpg`, selected PNGs and `visual-review.json`
  record the visual inspection. New frame selections use a shared monotonic
  timestamp to associate recordings with evaluated samples.
- `Correction01/starting-files.json` and `Rollback/`: exact initial-candidate
  source, report and AnimBP bytes. `Correction01/preservation-after.json` checks
  all 1,419 original task starting files: no missing files; only the four native
  source files and one adapted AnimBP differ. The retained map, every other
  Content package, vendor source, original-character source and configuration
  remain unchanged. No historical manifest was rewritten.
- `Assets/Source/PurchasedArms04/source-manifest.json`: new single-package
  revision over PurchasedArms03, including old/new/source hashes. The AnimBP
  remains under the existing Git LFS rule. The ADS graph was preserved within
  the changed package rather than claiming its entire file stayed identical.
- `editor-state-correction01-handoff.json`: no dirty assets/maps, PIE stopped.
  Editor PID is in `Correction01/editor-cold.pid`. `Correction01/changed-files.json`
  records the final paths/hashes; `storage-after.json` records the measured project
  size below 250 GB. `execution-receipt.json` verifies Astra/max/standard.

Earlier evidence remains unmodified. `Baseline01-*` was background-throttled to
about 3 Hz and is not presentation acceptance. `Jump01-Ordinary` stopped receiving
native W input despite the driver's held-key bookkeeping; its later foreground
replacement established continuous recovery. `focused-analysis02.json` preserves
that distinction. The initial `Views01` Shift visuals are now explicitly rejected
for jump presentation, while their physics evidence remains usable. The former
implementation report is in `Correction01/Rollback/Docs/PurchasedArms04.md`.

One read-only audit initially hit Epic's Python wrapper limitation for nested
transition graphs; the native graph-editor API resolved it before mutation.
Editor startup regenerated a disabled AndroidFileServer value; removing only that
line restored the exact original configuration bytes. Both events are recorded
locally and are not hidden as successful checks.

Videos are silent screen captures at about 12 frames/second. Frame inspection is
sampled; this is not a claim of every-pixel visibility on every game frame or
hitch-free performance. Networking, other movement modes and uneven-obstacle
coverage remain outside this bounded correction.

## Exact implementation inventory

Modified existing files:

- `Source/MeridianSquad/OpeningLobbyCharacter.cpp`
- `Source/MeridianSquad/OpeningLobbyCharacter.h`
- `Source/MeridianSquad/PurchasedArmsAnimInstance.cpp`
- `Source/MeridianSquad/PurchasedArmsAnimInstance.h`
- `Content/InfimaGames/TacticalFPSAnimations/Common/Core/Characters/ABP_TFA_FP_BaseCharacter.uasset`
- `Scripts/PurchasedArms02/capture02.py`: optional output directory; old default retained.
- `Scripts/PurchasedArms02/video_cases.py`: optional capture entry point; old default retained.

New files:

- `Docs/PurchasedArms04.md`
- `Assets/Source/PurchasedArms04/source-manifest.json`
- `Scripts/PurchasedArms04/analyze04.py`
- `Scripts/PurchasedArms04/analyze_correction.py`
- `Scripts/PurchasedArms04/bootstrap.py`
- `Scripts/PurchasedArms04/capture04.py`
- `Scripts/PurchasedArms04/client04.py`
- `Scripts/PurchasedArms04/correction04.py`
- `Scripts/PurchasedArms04/correction_handoff.py`
- `Scripts/PurchasedArms04/handoff04.py`
- `Scripts/PurchasedArms04/prepare_cases.py`
- `Scripts/PurchasedArms04/preserve.py`
- `Scripts/PurchasedArms04/review_views.py`
- `Scripts/PurchasedArms04/run_cases.py`
- `Scripts/PurchasedArms04/tools04.py`
- `Scripts/PurchasedArms04/unreal04.py`
- `Scripts/PurchasedArms04/video04.py`

Task adapters reuse the existing official Epic MCP transport, input/evaluation
probe, preservation utility and capture driver. No dispatcher or test framework
was introduced. Controller-owned AGENTS/ProjectState/task/approval edits and
`.multica/` remain outside the worker change set. The worker performed no status,
profile or registry administration, purchases, source cleanup or commits.
