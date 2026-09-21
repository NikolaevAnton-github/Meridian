# MSQ-98: preserve facing through the GASP recovery handoff

Date: 2026-09-22 (work began 2026-09-21). Continues the owner's request for a direct personal fix without
a new task. The new eight-second recording is
`D:/devgames/20260921-2039-08.6055180.mp4`, SHA-256
`e8c3901ffc7e770561db47d2c3bc5f6b19e1961e6ac2b2ed7a68c206d3d419bd`.
It shows five semi-automatic hits from the player-spawn side, followed by an
uncommanded half-turn. Immortality is on and recovery assistance is off.

This closes the heading transition left unresolved in
[correction 01](GASPEnemyFoundation01HandoffCorrection01.md). No Multica task,
executor or independent reviewer was dispatched. Owner play judgement is separate.

## Cause and correction

The sample's parent `Get_OrientationIntent` switch has no Ragdoll branch and
returns zero in that mode. Its child input producer normally replaces this
with the physical ragdoll direction. However, once Walking is queued, the child
stops that override while the parent still observes Ragdoll. The zero direction
survives in `MoverDefaultInputs_PreSim`; idle Walking converts it to rotation
zero and then to +X, commanding a turn away from the spawn side.

The native reproduction records facing -X before the hit, a zero input at the
Walking boundary, then +X and an uncommanded 180-degree turn. A Rider debugger
stop confirms the recovered Standing/Recovery state at `ReleaseRecoveryAuthority`.
The deeper installed-engine breakpoint had no executable mapping, so per-frame
Mover input observations and the retained graph exports establish that boundary.

`AGASPEnemyFixture` now composes the original Mover input producers in their
existing order. It corrects only an otherwise-zero orientation while leaving
Ragdoll, using the foundation's current forward direction. Both the outgoing
command and the sample's separate PreSim cache receive that direction. Nonzero
orientation, movement commands, custom ragdoll data and montage input are retained.
Reset recreates the producer binding with the new foundation. This is native
integration code only; no Blueprint, animation or other asset was changed.

## Focused results

The Development Editor build passes on UE 5.8.1, CL 56057345. The corrected binary
is loaded in the open editor. Three successful native-input/WGC cases cover:

- The same four frontal torso hits that reproduced the turn: 180 degrees before,
  zero uncommanded heading change afterward.
- Five frontal hits, a commanded turn from 180 to -90 degrees, another hit,
  F6 recreation, and a hit/recovery in quarter time followed by normal time.
  Seven real hits across two reset epochs; the new commanded facing is preserved.
- Repeated firing, a physical fall and completed get-up, further real rifle hits,
  supported recovery and resumed movement. The earlier stale-pose correction
  also passes its existing focused analyzer on this recording.

Across the corrected recordings, 34 real hits produce seven observed supported
recovery-to-idle handoffs. Each preserves heading exactly, with no zero Walking
orientation. The inspected returns have at most 4.31 degrees rendered torso lean
and 3.05 cm rendered wrist displacement per observed frame relative to the chest;
hands stay at least 47 cm below the clavicle. The frontal recording was visually
inspected and shows neither the unwanted turn nor an abrupt arm throw on return.
Ordinary impact recoil and commanded turns remain active.

The first attempted correction changed only the outgoing command; its failed
recording exposed the separate PreSim cache. A later recording at about 19 FPS
fell instead of completing a supported recovery and its video capture failed;
it is excluded from acceptance. A concurrently running owner MotionDemo occupied
most GPU capacity. Successful final checks used temporary 40-percent screen
percentage and averaged 44.5-59.1 observer FPS. These are focused physical runs,
not a performance benchmark or a full animation matrix. Render, frame-cap and
background-throttle settings were restored afterward.

## Evidence and preservation

Evidence is under `Saved/CombatSlice01/GASPEnemyFoundation01/`:
`OwnerVideo02/`, `HandoffCorrection02/analysis-final.json`, debugger/build records,
preservation hashes, `fixed-spawn-sequence.jpg` and the closure manifest. The
passing case names are `Correction02-SpawnFixed03`, `Correction02-GetupRegression01`
and `Correction02-SpawnResetMovement01`; observations and videos are in `Worker/`
and `Worker/Video/`. The baseline is `Correction02-SpawnBaseline02`.

`Scripts/GASPEnemyFoundation01/cases-heading02.json` reuses `run98.py` and its
existing capture/input driver; `analyze_heading02.py` checks idle heading,
orientation and arm continuity. Use fresh case names for additional captures.

Owner config/project edits, the lobby map and the GASP Blueprint retain their
pre-change hashes. Candidate01 and correction 01 evidence remain unchanged.
The editor is left on the lobby with no PIE, dirty packages or pending performance
override. Debugger attachments and agent breakpoints are removed.
