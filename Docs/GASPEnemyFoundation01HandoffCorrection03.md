# MSQ-98: smooth the supported recovery return to GASP

Date: 2026-09-22. Direct personal correction under the owner's continuing
instruction to fix the motion without a new task. No Multica run, executor or
independent reviewer was dispatched. Owner motion judgement remains separate.

## Problem and change

The owner still felt a jerk after our holds and retreat steps finished.
Corrections 01 and 02 fixed the stale fallen snapshot and unwanted turn; their
gross pose-continuity checks did not establish a smooth change of velocity.
The remaining exit enabled the source drives immediately while the animation
switched from the recovery target to GASP over 0.15 seconds.

`AGASPEnemyFixture` now captures the actual physical bone transforms on a
supported Recovery-to-Locomotion exit. It blends the physics targets from that
world-space pose toward the live GASP animation over 0.55 game seconds, using a
quintic easing curve with zero endpoint slope and curvature. The world-space
start survives Mover's capsule reanchoring. Bodies are not teleported and their
velocities are not cleared. Source force limits, collision and joint-limit
handling remain active; native and source drives are never enabled together.

A small component runs Physics Control's supported manual update sequence after
animation and the sample's PostABPTick: update caches, blend targets, update
controls. It inherits the original tick prerequisites, including those installed
after adoption. The inherited balance initializer's normal component tick is
disabled again to prevent duplicate updates. F6 removes the old dependencies and
rebinds the newly spawned foundation.

New hits cancel the blend immediately and reclaim recovery authority. Movement
commands can start during the blend. Falling, death and reset discard it. GASP's
ordinary get-up montage exit is retained; a later supported recovery uses the
new blend. No animation, Blueprint, physics asset or engine source was edited.

## Focused verification

UE 5.8.1 Development Editor build passes and is loaded in the open editor.
The same four spawn-side rifle hits were recorded before and after the change.
Over the first 0.9 game seconds of the supported return:

| Wrist motion relative to chest | Before | After |
| --- | ---: | ---: |
| Peak rendered speed | 173.27 cm/s | 85.62 cm/s |
| Peak rendered acceleration | 9276.31 cm/s² | 891.29 cm/s² |
| Peak active target speed | 378.95 cm/s | 93.43 cm/s |
| Peak active target acceleration | 9547.40 cm/s² | 2210.51 cm/s² |

Rendered derivatives include the authority boundary. Target derivatives start
with the newly active source targets: the previous cached animation pose was
not driving native recovery. This avoids treating an unused cache change as
physical motion. These are sampled comparisons of two physical runs, not a
claim of frame-rate-independent maxima. Observer rates were about 92 and 80 FPS.
The ordinary-speed WGC recording and its extracted transition frames show a
gradual arm return. Facing is unchanged, rendered torso lean stays below 4.23
degrees in this reproduction, and the largest wrist displacement is 1.27 cm
per observed frame.

Additional focused cases pass their applicable criteria:

- A real fifth bullet interrupts the blend about 0.20 game seconds after release.
  The subsequent recovery completes; a movement command starts 0.26 seconds into
  its next blend and travels about 54 cm.
- Retreat steps, a commanded turn, another hit, F6 recreation, quarter time and
  restoration of normal time retain stable handoffs and the requested facing.
- Repeated firing produces two completed GASP get-ups, later real hits, supported
  recovery and resumed movement. The existing affected-transition analyzer passes.
- A lethal burst releases all drives, registers one death and leaves the body
  fallen, with no active handoff.

There are no simultaneous native/source drives, unbounded source controls,
duplicate component ticks or handoff states outside Locomotion in the recorded
transitions. The interrupted case intentionally has short idle windows and no
slowdown request; its applicable criteria are recorded separately rather than
using the older full-duration aggregate. This is not a full animation matrix.

## Evidence and preservation

Evidence root: `Saved/CombatSlice01/GASPEnemyFoundation01/HandoffCorrection03/`.
It contains build logs, the baseline/final kinematic comparison, regression and
death acceptance, preservation hashes, extracted video frames and a closure
manifest. Native-input observations and WGC videos are in `Worker/` and
`Worker/Video/`, with these names:

- `Correction03-SpawnBaseline01`, `Correction03-SpawnFixed02`
- `Correction03-Interrupt01`, `Correction03-ResetSlow01`, `Correction03-Getup01`
- `Correction03-Death01`

`analyze_smooth03.py` adds the derivative comparison to the existing observers
and heading analyzer. `handoff_probe01.py` adds a state-triggered event hook for
the interruption check. Case inputs are preserved in the evidence directory;
use fresh names for reruns.

The first attempt failed because the inherited initializer re-enabled the
original component tick. Its failed recording, analysis and source diff remain
preserved. The replacement tick's runtime path was confirmed in Rider at
`UpdateFoundationPhysics` / `UGASPEnemyPhysicsTick::TickComponent`, with
Locomotion authority and the adopted PhysicsControl object. The earlier attempted
breakpoint in the optimized release body had no executable mapping. Debugger
attachments and agent breakpoints were removed.

Owner config/project files and the lobby retain their pre-change hashes. Git
shows no binary asset changes; Candidate01 and corrections 01/02 are preserved.
The editor is on the lobby with no PIE or dirty packages. Temporary frame-cap
and background-throttle settings are restored.
