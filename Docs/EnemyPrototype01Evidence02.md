# EnemyPrototype01: evidence supplement 02

This 2026-09-19 supplement preserves the original contract, candidate manifest,
handoff and all earlier evidence. No gameplay code or asset bytes changed.
Use `Worker/handoff02.json` and `Worker/candidate-manifest02.json` for the final
review packet, together with [the implementation report](EnemyPrototype01.md)
and `EnemyPrototype01-Contract01.json`.
All Worker paths below are under `Saved/CombatSlice01/EnemyPrototype01/`.

## Explicit volume correction

The controller correctly identified the incorrect `volume_m3` label in
`Worker/mesh-topology-audit01.json`. That value, **1357.7568057763824**, was the
untransformed mesh-local volume in cubic centimetres.

`Worker/mesh-topology-audit02.json` already corrected the selected template-source
calculation. The separate `Worker/mesh-topology-units03.json` now records the actual
imported object's 4x4 matrix and the conversion explicitly:

`world_volume_m3 = abs(local_signed_volume * determinant(mesh.matrix_world.to_3x3()))`

The measured determinant is `9.999999974752427e-7`, approximately the cube of the
0.01 centimetre-to-metre length scale. The corrected result is
**0.001357756802348376 m3**, agreeing with audit02 with zero reported difference.
The original mislabeled evidence remains untouched. This calculation concerns
only disposable topology/capping feasibility; it adds no UV, material, retained
stump, skinning-transition or detached-body physics acceptance.

## Unobstructed reset views

On direct visual inspection, the Message Log window opened by the earlier invalid
Static cover fixture obscured part of `Video/Candidate07-ActiveRagdollReset`.
Its telemetry remains applicable, but it is not the primary visual evidence.

Only that affected 13-second visual scenario was repeated on the unchanged final
binary as `Candidate08-ActiveRagdollReset`. Its 782 sampled frames and ordinary
speed video show a hit/death, F6 while the body is still moving, a second death,
settled physics and another reset. Representative actual frames were inspected;
the body is unobstructed. No new overloads or geometry barriers occur during the
recorded scenario; its largest sampled world interval is 16.758 ms. The overload
counter is already five before the first recorded input and stays five throughout
(1.667 seconds dropped during pre-recording warmup). The scenario finishes with
health 100 and ammunition 22, and no replacement gameplay
matrix was run. The original 71 passing checks over 2,403 rows remain the primary
technical evaluation; this recording resolves only the visual evidence gap.

Use `Video/Candidate06-*` for stationary/moving hits and rifle hold/fire pose,
and `Video/Candidate08-ActiveRagdollReset*` for the corrected active-reset views.
`Worker/evidence-supplement02.json` fingerprints the additional evidence and
documents its relationship to the unchanged original candidate.
