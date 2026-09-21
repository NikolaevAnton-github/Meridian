# MSQ-98: upright recovery handoff correction

Date: 2026-09-21. Direct controller correction authorized by the owner's chat
instruction to fix the recorded bugs personally, without creating a task.
No new Multica task, executor run or independent reviewer was dispatched.
This is a later correction to MSQ-98; Candidate01 and its acceptance evidence
remain immutable. Owner motion/play judgement remains separate.

The owner's 14.53-second recording shows an abrupt backward collapse and rebound
at 7.667-8.133 seconds after firing has stopped, and a smaller stance/heading
reset later. The original recording in `D:/devgames/` is preserved, SHA-256
`b8f9d1c1350479db566262880e436bad1d8e56f2cd78a6b922e877bb6c1dcee3`.
The visible immortality setting explains constant 100 HP.

## Cause and bounded change

Runtime reproduction, a Rider native debugger stop and the retained Blueprint
graph exports identify the recovery-to-GASP handoff. The migrated get-up gate
skips GASP's `SavePoseSnapshot("Ragdoll")` on an upright recovery exit. GASP's
`Blend Out Pose` animation state still reads that named snapshot. After a real
fall/get-up it therefore targets the previous fallen pose; before any capture
it can fall back to the reference pose. Re-enabled physical controls follow
that stale animation target despite the character already being stable.

In the failing reproduction, the animation target reaches 92.64 degrees from
vertical and the visible torso reaches 72.34 degrees during locomotion, without
a fresh hit. The debugger confirms that the recovery stability gate has passed;
it also confirms that queuing Walking leaves Mover in Ragdoll temporarily.

`GASPEnemyFixture.cpp` now captures the current named Ragdoll snapshot before
releasing upright recovery authority. It also retains the upright anchor while
Mover consumes the queued mode change, avoiding the prone-heading calculation
in that interval. Recovery strengths, thresholds and get-up selection are
unchanged. This correction changes no Blueprint, animation, map or other asset.

## Focused verification

The Development Editor native build succeeds on UE 5.8.1, CL 56057345. The new
binary was loaded by a controlled editor restart on the retained lobby map.
The existing native-input/WGC runner was extended with a lightweight observer;
it records physical bodies, rendered bones and cached animation targets each
frame, and full control/state information at transitions. This avoids the
frame-rate reduction caused by the full body/skin audit.

`Correction01-BaselineRepeat01` reproduces the defect before the code change.
`Correction01-FixedAfterGetup03` passes the affected transitions: real rifle
bursts at quarter and normal time, adaptive steps, falling, interruption of
get-up by a hit, completed get-up, reload, another real rifle hit followed by
upright recovery, and a subsequent movement command.

| Affected handoff measure | Before | Corrected |
| --- | ---: | ---: |
| Maximum physical torso lean | 71.77 degrees | 6.54 degrees |
| Maximum rendered torso lean | 72.34 degrees | 5.98 degrees |
| Maximum animation-target lean | 92.64 degrees | 5.50 degrees |
| Maximum capsule displacement per observed frame | 0.280 cm | 0.251 cm |

Measurements cover the first 1.2 seconds of each supported recovery-to-locomotion
handoff, ending early if another authority takes over. Acceptance requires each
lean to stay below 20 degrees, capsule displacement below 5 cm, and no simultaneous
source/native controls at recorded transitions. The final check also requires
an actual hit and supported handoff after a completed get-up; that specific
return has 4.47 degrees maximum rendered lean. Final state is Walking/Locomotion.
Movement covers 112.85 cm. The final 34-second recording contains 3,180 observer
samples, 29 real hits, four completed recovery steps, one completed get-up and
one get-up interruption. It averages 93.44 observer samples per second.

The affected capture interval was visually inspected. The abrupt backbend is
absent. The smaller heading/arm reset in the owner video was not independently
root-caused; the upright-anchor correction covers the adjacent transition, but
this check does not establish that every possible idle turn is eliminated.
These are focused, nondeterministic physical runs, not a full feature matrix or
a frame-matched performance comparison. An earlier fixed run exhausted its
magazine before the post-get-up shot and was excluded from that acceptance
criterion. A malformed intermediate JSON run is retained as failed evidence.

## Evidence and reuse

Generated evidence lives under `Saved/CombatSlice01/GASPEnemyFoundation01/`:

- `OwnerVideo01/`: recording observations and derived frame sequences.
- `HandoffCorrection01/`: debugger state, build log, preservation hashes,
  reproduction/fixed contact sheets, case specifications, final analysis and manifest.
- `Worker/Correction01-BaselineRepeat01.json` and
  `Worker/Correction01-FixedAfterGetup03.json`: frame/state observations.
- Matching videos in `Worker/Video/`; final editor state in
  `Worker/Correction01-FinalEditorState.json`.

For a bounded rerun, use `Scripts/GASPEnemyFoundation01/run98.py` with
`Scripts/GASPEnemyFoundation01/case-handoff01.json` and the live editor PID,
then `analyze_handoff01.py <case-name>`. Use a fresh case name for subsequent
captures; evidence files are not overwritten. The analyzer exits unsuccessfully
when the final supplied case fails the affected handoff or required coverage.

Owner changes in `Config/DefaultEngine.ini` and `MeridianSquad.uproject`, and the
retained lobby map, match their pre-change SHA-256 values. The editor is left
open on the lobby with no PIE or dirty packages. Temporary frame-rate/throttle
overrides were restored. Existing candidate manifests and registry acceptance
are preserved; they do not describe the identity of this newly built binary.
