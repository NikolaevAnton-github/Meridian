# GASPALSEnemy01 primary independent review

Date: 2026-09-23. Reviewer: `/root/gaspals_source_audit`, Astra, max reasoning,
standard speed. Scope: the [direct owner authorization](Approvals/GASPALSEnemy01-OwnerStart01.json).

**Verdict: PASS for implementation correctness and the affected functional visual
checks. No open technical findings. Owner motion/play judgment remains separate.**

## Reviewed candidate and method

The writer confirmed production freeze for `GASPALSEnemy01-Candidate01`.
[Candidate01-identity.json](../Saved/CombatSlice01/GASPALSEnemy01/Candidate01-identity.json)
has SHA256 `6fe8152f99de22dc832c6c5b5259f670e8f326a51bfaa1060a87c07c7e7d5e32`.
The reviewer independently matched all 42 listed file/source/archive/preservation
hash checks, including the build11 DLL. Key reviewed identities are:

| File | SHA256 |
| --- | --- |
| `Source/MeridianSquad/GASPALSRifleAnimInstance.cpp` | `4ccb4d65cb5dd6806e58ff49f9c4083d13e9353ffe5da19aec4183e52519dc75` |
| `Plugins/GASPEnemyFoundation01/Content/Blueprints/SandboxCharacter_Mover_ABP.uasset` | `37b5f7490a38ce26536958b882696bcf0076bbd9f1704a3e2ead815c69f460ed` |
| `Scripts/GASPALSEnemy01/author.py` | `4613f6c15eddfd95c26b09859a9b41c8e12396dd4e60d25add59317d96b9539e` |

The authoring script's first docstring was corrected after the candidate freeze
to describe the canonical AnimBP adapter. Restoring only that line in memory
reproduced the previously reviewed script hash; executable code is unchanged.

Review covered the five native files in the manifest, relevant authoring and
recording scripts, saved graph/source inspection, runtime telemetry, and actual
extracted frames from the ordinary-speed WGC recordings. The reviewer did not run
the editor, builds or gameplay tests and did not edit production files. Continuous
video playback and owner motion acceptance are not claimed. Passing checks were
reused; only changed aiming behavior and a newly observed initial-turn defect
required additional writer recordings.

All evidence names below are under
[`Saved/CombatSlice01/GASPALSEnemy01/`](../Saved/CombatSlice01/GASPALSEnemy01/).
Matching MP4s and examined PNG frames are under `Video/`.

## Acceptance evidence

| Criterion | Result and applicable evidence |
| --- | --- |
| Native build and self-contained assets | **PASS.** `build11.log` succeeds on UE 5.8.3. `dependency-closure.json` scans hard and soft references for 15 new packages plus the modified foundation AnimBP: `external={}`. `final-editor-state.json` records no source `/GASPALS` registry assets, no source-plugin command-line mount, no dirty packages or Play worlds, and no leftover fixture/controller actors. |
| Skeleton and graph adaptation | **PASS.** `skeleton-compare.json` establishes 88 shared raw bones with matching indices, parents and reference transforms within numerical precision; the destination appends `props_root`, `prop_01`, `poi`. No body retarget is required for these imported clips. The original AnimBP class identity is retained for its Chooser context; the adapter adds 43 nodes with no reported Blueprint errors. Rifle blending, heading correction and left-hand IK occur before the retained physical snapshot/ragdoll/get-up overrides. |
| All three fixtures | **PASS.** `Final02-ThreeRendered.json`: 150 samples, three fixtures, three foundations, three command controllers, zero orphan foundations. Actual `Final02-ThreeRendered-Frames/004.00.png` clearly shows all three armed profiles. Shared behavior was checked on one representative, as authorized. |
| Relax / Ready / Aim, independent movement and crouch | **PASS.** `Pilot02-RiflePoses` supplies 299 samples and actual stance/crouch views. `Pilot03-AimMovement` supplies side/back movement and pitch coverage. Corrected `Fix03-AimedStop` supplies 390 samples and examined 3.30, 6.70, 8.40 and 12.70 second views for stopped aim and up/down pitch. Final rear-target fading leaves these settled samples' `abs(AO.X)<60` correction unchanged. Crouch changes capsule half-height from 86 to 60 cm and restores it to 86 cm. |
| Real hit, physical authority and armed return | **PASS.** Final `Fix04-CrouchHitAim` has 262 samples and one real shot, health 100 to 75, followed by Recovery, Falling, Down, GettingUp and Locomotion. Crouch resumes after get-up; standing restores the capsule. Actual 1.50, 7.30 and 9.50 second views show the corrected grip and armed return. `Rollout01-FallGetup` retains sustained-hit, queued movement and return evidence. Existing facing/snapshot and target-handoff behavior is retained. |
| Death, reset and relative slowdown | **PASS.** `Rollout02-DeathResetSlow` has 292 samples: health reaches zero/Dead, F6 recreates the armed fixtures at full health, and slowdown records world 0.25 with player custom dilation 2.6 (effective movement rate 0.65), then restores normal rates. Actual 3.50, 5.80 and 7.80 second views show corpse, reset and slowed armed movement. Controller counts recover to three and no orphan foundation is recorded. |
| Source and owner preservation | **PASS within the identified scope.** All 15 source-import hashes, the retained map, `DefaultEngine.ini`, and `.uproject` match the preservation records. Exact current pre-edit AnimBP bytes remain in `Assets/Source/GASPALSEnemy01/Before/`, SHA256 `4be002ac82435201716c18fbe6e1ec83624515dbe823548c2bcfcc2131b8b963`. The rejected copied AnimBP remains archived outside Content. Cleanup changes derived preview references and authoring user data, without a curve-edit operation. |

Physical-authority telemetry needs one timing qualification: the first sample
immediately after a hit can contain the previous animation update's `RifleAlpha=1`.
Source controls are already disabled, and the next animation update sets the rifle
alpha to zero. The inspected transitions support physical authority; a claim that
every non-locomotion sample contains zero rifle alpha would be inaccurate.

## Findings and closure

1. **R1 — authoring rerun disconnected the retained pose cache. Closed.**
   `Scripts/GASPALSEnemy01/author.py:94` now restores the original linked-layer to
   cached-pose connection after removing generated nodes, before rebuilding the
   adapter. Subsequent successful graph authoring supports the correction.
2. **R2 — aim was supplied after the source directional-input producer. Closed.**
   `GASPEnemyFixture.cpp:101` now calls `UpdateRifleInput` before source producers.
   `GASPEnemyRifle.cpp:54` supplies the owned command controller's control rotation
   at that point. Reset and EndPlay destroy that controller. Movement/aim recordings
   and reset counts cover the affected path.
3. **R3 — stopped rifle aim ignored retained root yaw. Closed.**
   Original `Pilot04-CrouchHitRecovery` at 9.008 seconds and `Rollout01-FallGetup`
   at 15.993 seconds showed approximately 43 degrees of barrel/target error.
   `GASPALSRifleAnimInstance.cpp:89` now uses retained `AO.X` and measured source
   barrel calibration; `author.py:202` applies the correction at `spine_01` before
   grip IK. A provisional full-vector correction introduced a pitch bias and was
   narrowed to yaw. Final evidence exercises substantial retained yaw, without
   resetting the root to manufacture alignment.
4. **R4 — rear-target correction destabilized the initial crouched grip. Closed.**
   `Fix03-CrouchHitAim` at 1.512 seconds, before any hit, showed 41.78 degrees of
   aim error and a 46.58 cm left-grip gap; its actual 1.50 second view confirmed the
   defect. `GASPALSRifleAnimInstance.cpp:103` now smoothly fades correction between
   60 and 110 degrees of absolute retained aim yaw. Rear targets use the source
   turn-in-place. `Fix04` repeats that initial turn/crouch and the affected physical
   return successfully; the failing recording remains preserved.

### Independent measurement checks

The recorded barrel direction is the imported M4's local positive-Y axis in world
space. Independent reconstruction from recorded `hand_r` rotation and the retained
75-degree attachment matches the measured component direction to approximately
`1.2e-7` or better at checked samples. Baseline `Pilot02` also validates this axis.
These measurements concern rendered presentation, not enemy firing accuracy.

| Recording / sample | Retained `AO.X` | Barrel/target angle | Left grip gap |
| --- | ---: | ---: | ---: |
| `Fix04-CrouchHitAim`, 1.509 s, before hit | 14.17 deg | 0.773 deg | 0.0079 cm |
| `Fix04-CrouchHitAim`, 9.919 s, after get-up/stand | 40.54 deg | 0.520 deg | 0.00049 cm |
| `Fix03-AimedStop`, 3.309 s, stopped | -14.45 deg | 0.826 deg | 0.0243 cm |
| `Fix03-AimedStop`, 6.512 s, upward aim | -14.79 deg | 1.444 deg | 0.0011 cm |
| `Fix03-AimedStop`, 8.012 s, downward aim | -14.90 deg | 0.393 deg | 0.0005 cm |

Final `Fix04` samples after 8.5 seconds retain roughly 40.5–40.8 degrees of root
relative yaw with maximum barrel error 0.561 degrees. Normal stance/turn/handoff
transitions remain gradual. The short invalid `Fix01` observer-recursion run and
superseded `Fix02`/`Fix03-CrouchHitAim` failures are excluded as passing evidence.

## Limits and handoff

This approves the identified armed-mannequin integration and its focused technical
evidence. It does not approve owner motion quality or implement autonomous combat,
navigation, disarming, wound gestures, or the deferred balance/terrain tasks. The
rifle remains attached during physical states; left-hand support returns with the
existing pose handoff. Controller scope acceptance, asset registration and the
required local closure commit remain controller responsibilities.
