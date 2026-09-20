# PhysicsControlLegPose01 — MSQ-91 executor handoff

2026-09-20. **Candidate07** corrects the reproduced post-step leg reversal and
accumulating stance error on the retained MSQ-89 Candidate05 baseline.
The Development Editor build and **183 focused self-checks pass** across 2,425
runtime samples and 22 CPU skin audits. Independent review is waived by the
[owner's MSQ-91 authorization](Approvals/PhysicsControlLegPose01-OwnerStart01.json).
The controller owns scope/evidence acceptance, status and the closure commit.
Final visual, motion and play judgement remains with the owner.

The immutable handoff is
`Saved/CombatSlice01/PhysicsControlLegPose01/Worker/Candidate07/manifest.json`.
Its native sources, loaded DLL and Physics Asset are identical to Candidate06.
Candidate07 also freezes this report and the completed evidence tools.
Paths below are relative to that task's `Worker/` directory unless stated otherwise.

## Reproduction and cause

`Baseline01` matches all 14 native/binary/asset entries of retained MSQ-89
Candidate05. The original defect was recorded **before runtime source changes**,
using the same two impulses and fixed rear/side cameras used for the final views.
`Before-Rear` and `Before-Side` each contain two completed recovery episodes.

After the first baseline step, the right knee's geometric bend direction differs
from its toe direction by about 60.8 degrees. After the second episode the left
difference reaches 120.1 degrees. The comparable final candidate reads 13.5 degrees
left and 1.4 degrees right, close to the calibrated idle. This is a bone-position
diagnostic of the reproduced reversal, not a clinical joint-angle measurement.
The actual before/after images show the corresponding knee/calf change.

The old solver projected the entire old thigh vector onto the plane normal to
the **new** hip-to-ankle axis. Moving the pelvis behind a planted foot could reverse
that projected direction. It then retained the solved skeleton as the next
reference, including accumulated rotations and reduced pelvis height. Independent
shortest-arc rotations did not preserve a complete anatomical frame.

## Implementation

`NeutralBones` now captures the complete calibrated idle skeleton only on reset
or completion of the retained get-up. Landing still remembers the displaced
standing skeleton, but never replaces the neutral one with the solved step.
Lengths, bend reference and bone roll therefore remain independent of episode
history. Reset captures a fresh neutral and clears all added transient state.

Each leg first derives its bend direction in the original neutral leg plane,
then projects that direction onto the current leg plane. A complete frame maps
both segment direction and roll from the neutral skeleton to the solved thigh
and calf. Foot rotations stay calibrated and planted ankle targets remain fixed;
the correction does not turn or slide a planted foot to disguise unreachable IK.
The full 89-bone pose continues to drive the visible skeleton and physics targets.

The intended resting pelvis comes from the current foot midpoint plus the
neutral pelvis-to-feet offset. Its height is calculated anew rather than adding
another correction to a previously lowered stance. Transfer lean fades out
before landing, avoiding a hip-limit conflict from retaining that lean after a
long foot placement. The existing small crouch fades during settling.

A stance outside the bounds below remains UNSTEADY and requests the remaining
corrective step. The previously planted foot moves to restore the neutral foot
separation relative to the newly landed support foot. A pending correction cannot
be cleared by instability decay or labelled STANDING during the short cooldown.
The episode still permits at most two steps. Failed reach, joint feasibility,
placement or exhausted budget releases into the retained physical fall/get-up.

### Effective bounds

These are scoped engineering values for the retained Manny rifle pose, not
universal anatomical limits or owner-approved motion tuning.

| Bound | Effective value |
| --- | --- |
| Nominal first step | Retained 30 cm; exposed length bounded to 12–40 cm and by `StepMaxReach` |
| Corrective step reach | `StepMaxReach`, bounded to 12–45 cm; 0.01 cm numerical comparison tolerance |
| Steps per episode | At most two, including a stance correction |
| Reach reserve | 1 cm below the sum of immutable thigh/calf lengths |
| Pelvis reach correction during a step | At most 8 cm downward; otherwise physical fall |
| Permitted settled pelvis correction | At most 4 cm downward; otherwise correction or fall |
| Settled width along neutral across-leg axis | 0.55 × neutral width through neutral width + 16 cm |
| Settled foot-separation-vector deviation | At most 36 cm from neutral |
| Planted ankle target | Unchanged throughout each step |
| Physical support drift | 2 cm verification tolerance; retained 5 cm safety release |
| Generated angular target | Reject if exact joint-limit projection changes it by more than 3 degrees |
| Stable visible sole clearance | Retained 0–1 cm above the floor |

The neutral projected width is about 39.7 cm. Broad lateral steps now close with
a second step and finish at about 39.5–39.6 cm ankle separation. A single sagittal
step can retain a staggered stance: measured separation is about 47.2 cm, with
the width and reach bounds still satisfied. The nominal timing, lift, support-loss
grace, landing timeout and flat static floor checks remain those of MSQ-89.

Stepping uses a fixed instance joint envelope. It no longer widens leg limits
every frame to admit the generated target. The source Physics Asset is unchanged.
The authored ragdoll envelope already excludes parts of the retained idle
(approximately 58-degree hip swing and 38-degree ankle twist in offset constraint
frames), and cannot alone accommodate the transfer/swing. The fixed replacement
admits that bounded motion while retaining hip/knee twist limits from the asset.

| Joint | Authored Swing1 / Swing2 / Twist | Fixed stepping envelope | Observed signed ranges, same order |
| --- | --- | --- | --- |
| Left hip | 55 / 30 / 20 | 75 / 35 / 20 | 37.34…74.58 / -4.58…20.59 / -3.21…14.28 |
| Right hip | 55 / 30 / 20 | 75 / 35 / 20 | 24.29…59.66 / -20.91…4.72 / -13.76…3.15 |
| Left knee | 5 / 5 / 60 | 8 / 15 / 60 | -5.53…3.67 / 4.75…13.61 / -46.76…2.06 |
| Right knee | 5 / 5 / 60 | 8 / 15 / 60 | -3.32…8.01 / 2.01…13.98 / -46.13…10.08 |
| Left ankle | 10 / 20 / 35 | 20 / 30 / 65 | -22.36…1.83 / 6.67…20.04 / -59.59…-29.08 |
| Right ankle | 10 / 20 / 35 | 20 / 30 / 65 | -15.15…10.82 / -16.62…-1.19 / -60.21…-30.25 |

All values are degrees in this asset's offset constraint frames. In particular,
the knee's constraint twist coordinate is not anatomical axial tibial twist.
The two retained calf-to-pelvis constraints keep their 90/90 swing limits, free
twist and free linear axes. Telemetry computes the exact Chaos swing/twist
decomposition from actual body and constraint frames. Earlier Candidate02 API
axis-projection readings are not used for the table above.

These physical constraints are compliant: the largest recorded individual-axis
excess is a transient 2.36 degrees at the left ankle; the right knee reaches
8.01 against 8. The solver targets require at most 1.08 degrees of projection in
the 40 cm case, below the explicit 3-degree rejection tolerance. The report does
not claim exact enforcement with zero transient overshoot. Neutral standing,
falling and the retained get-up keep their existing lifecycle; get-up joint-limit
adaptation is unchanged and is not represented by the stepping table.

## Focused results and recordings

`build07.log` is the passing final UE 5.8.1 Development Editor build.
`focused-results02.json` contains 183 passing assertions, the observed joint
ranges, per-episode geometry, capture timing and 22 CPU skin audit summaries.
Each record below has a runtime JSON and a complete ordinary-speed
`Video/<name>.mp4`, with WGC readiness and capture metadata.

| Record | Result |
| --- | --- |
| `Before-Rear`, `Before-Side` | Reproduced baseline reversal before edits; matched cameras and two impulses |
| `Candidate05-Rear`, `Candidate05-Side` | Left then right step; aligned settled legs; directly comparable final views |
| `Candidate05-RepeatedReset` | Four successive episodes, both swing legs, no accumulating crouch/twist, then F6 restores home and clears new state |
| `Candidate06-Lateral` | Default lateral opening plus corrective step; neutral width restored |
| `Candidate06-TurnedLateral` | Opposite lateral disturbance with body turned 90 degrees; two steps finish at neutral width |
| `Candidate06-Corrective` | 40 cm first step and 40 cm corrective step from one disturbance; exactly two steps, no third request |
| `Candidate05-Infeasible` | PIE-only adversarial +40 cm intended pelvis height during swing; rejection, all fall drives off, actual collapse, full 89-bone living get-up finishes standing |
| `Candidate05-ResetDuring` | F6 during swing restores home/neutral and clears all new and retained step state |

Peak measured support-foot drift is **0.415 cm**. Planted targets never move
during a step. Actual thigh/calf segment lengths remain within the focused
1 cm tolerance around their approximately 43.4/42.3 cm reference lengths.
Geometric knee flexion during measured stepping ranges from 17.37 to 74.03
degrees; settled post-step samples range from 17.51 to 31.18. Maximum settled
knee-to-toe direction difference is 13.65 degrees, versus 120.12 in the reproduced
baseline. No knee reversal or hyperextension is observed in these samples.

After episodes two and four the standing pelvis target returns to 94.9807 cm;
actual settled pelvis height is about 94.45 cm, matching the initial physical
stance rather than progressively crouching. CPU-skinned sole gaps across 22
audits are **0.225–0.550 cm**, within the retained 1 cm tolerance. Continuous
stable sole telemetry is approximately 0.219–0.550 cm. All five untargeted
mannequins retain full health with no hits or deaths.

The final rear/side, landing, corrective swing, collapse and recovered frames
were inspected directly. Timestamped extracts are in each video's `-Frames/`
directory. The continuous recordings retain actual wall-clock timing, with a
30 FPS render cap and roughly 16.3–17.1 captured FPS. Maximum capture gap is
0.219 seconds. Motion between captured frames is not fully evidenced; the clips
and measured geometry do not replace owner motion/play judgement.

### Evidence applicability and preserved failures

Candidate06 changes only the corrective reach numerical comparison and the
pending-correction state label relative to Candidate05. Neither branch executes
in the reused rear, side, repeated sagittal, infeasible-reach or reset-during
records. The three affected corrective records were rerun on Candidate06.
`evidence-applicability01.json` records this mapping and the exact source diff.
Candidate07 has identical native/binary/asset bytes to Candidate06.

Unchanged MSQ-89 evidence remains applicable to static footprint/path rejection,
six-fixture rendering, native rifle/ammunition and terminal death controls,
relative slowdown clocks and the hard step-budget/input queue logic. Their old
leg-pose or precise physical trajectories are not claimed as new-pose evidence.
The MSQ-88 source, collision and unrelated prone-recovery evidence is retained.
There is no per-profile or full animation matrix.

All earlier candidates and failed checks remain intact. Candidate01 exposed the
insufficient neutral-only ragdoll joint envelope. Candidate03 exposed the hip
conflict from transfer lean persisting into landing; its 37 cm follow-up confirmed
the same issue. Candidate05 exposed a transient STANDING label while a correction
was pending, and rejected a computed 40.00000000000003 cm correction at a strict
40 cm comparison. Candidate06 fixes those two conditions. `focused-results01.json`
preserves the earlier 150 passes and four failed corrective expectations;
the final 183-pass result is a new evaluation, not an overwritten failure.

## Changed files and preservation

`changed-files01.json` supplies the complete task-scoped list and hashes.

| Files | Change |
| --- | --- |
| `Source/MeridianSquad/PhysicsControlStepping.cpp` | Neutral frame IK, absolute rest stance, corrective step, fixed joint feasibility and measured telemetry |
| `Source/MeridianSquad/PhysicsControlDummy.h` | Neutral skeleton and bounded corrective-step state |
| `Source/MeridianSquad/PhysicsControlBalance.cpp` | Preserve pending corrections through decay/cooldown; disable per-target leg-limit widening while stepping |
| `Source/MeridianSquad/PhysicsControlBalanceProbes.cpp` | PIE-only infeasible pelvis-target fixture; does not teleport physical bodies |
| `Scripts/PhysicsControlLegPose01/` | Thin extensions of the existing Epic MCP, native-input and WGC recorder; focused cases, measurements and immutable packaging |
| `Docs/PhysicsControlLegPose01.md` | This report |

`preservation-after01.json` verifies all 10 protected fingerprints, including
owner engine/project edits, the retained lobby, original Mixamo sources and
provenance, Physics Asset and recovery graph code. No Content or Assets file
changed. No registration is needed for a new binary asset. Historical manifests,
rejected candidates and owner task/approval edits remain intact.

`native-execution01.json` verifies actual Astra/max/default execution with fast
mode disabled against the native session and dispatch arguments. No worker
profile or issue-status administration occurred. `storage-after01.json` measures
33.49 GB in the physical project tree against the 250 GB cap, excluding 4,180
junction/symlink directory aliases. Small final report/candidate additions do not
materially change that measurement; no owner asset was removed.

`handoff-final01.json` records the retained lobby with PIE stopped, no dirty map
or content packages and no transient probe actors. The editor remains available
for owner Play (process 21004, ordinary editor logs under `Saved/Logs/`); close
the editor normally when no longer needed. The writer lease is released at
handoff. The worker leaves acceptance, local closure commit and status to the
controller. No reviewer or successor was dispatched.

This remains assisted procedural recovery on flat static floors with the retained
rifle idle and get-up assets. It is not adaptive gait, debris/terrain support,
autonomous locomotion or final-character animation. Residual idle knee bend,
retargeted shoulders, compliant joint overshoot and the capture-rate limit are
explicit retained limits. The owner's final visual/motion acceptance is pending.
