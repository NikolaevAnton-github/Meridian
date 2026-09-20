# PhysicsControlRecovery01: self-collision, grounded feet and pose-snapshot get-up

Prepared 2026-09-20. Multica issue: **MSQ-88**, an unassigned backlog follow-up to
MSQ-87 Candidate05 in the CombatSlice01 / MSQ-67 family. The owner reports that the system generally works
but requests a task covering three visible defects. See the
[exact feedback and task request](../Approvals/PhysicsControlRecovery01-TaskCreation01.json).
This record does not dispatch implementation or review.

Baseline: [MSQ-87 implementation](../PhysicsControlBalance01.md),
[owner-test handoff](../PhysicsControlBalance01Handoff.md), and the immutable
candidate/evidence under `Saved/CombatSlice01/PhysicsControlBalance01/Worker/`.
Preserve the current experiment while correcting the following three areas.

## 1. Arms should collide plausibly with the body during a fall

Audit effective collision filtering, Physics Asset pair exclusions, arm/hand and
torso/pelvis shapes, and relevant joint limits. The current component blocks
WorldStatic and ignores the other channels, but the actual self-collision result
must be established from the effective per-body/pair settings. A control's
`bDisableCollision` flag alone is not a global explanation: its parent/child effect
requires a parent body, while these pose controls are world-space controls.

Enable and tune the required arm/hand versus trunk/pelvis collision pairs so arms
do not visibly pass through or remain trapped inside the torso during the affected
fall/recovery paths. Fit collision shapes to the visible body and retain sensible
limits. Avoid globally enabling overlapping adjacent pairs or introducing violent
separation, persistent jitter or unwanted player/other-mannequin collisions.
Preserve the authoritative rifle contact/damage path. Any Physics Asset change
must use a task-scoped derivative when the shared source is used elsewhere.

## 2. Feet should visibly rest on the floor

Remove the fixed-height assumption from initial standing, F6 reset, get-up placement
and recovered standing. Current spawn Z=8, recovery origin `GroundHeight + 10`,
standing origin `GroundHeight + 8` and a 26 cm support-proximity probe permit a
standing pose without actual sole contact; they are not a calibrated foot placement.

Determine floor height and actual sole/foot-shape geometry, then position the pose
and its physical targets consistently. Distinguish bone origin, visible sole and
collision shape bottom. Define a small justified contact tolerance before claiming
pass. Remove visible hovering without sinking feet into the floor or embedding the
fallen body. Support detection must remain compatible with usable-leg loss and
physical collapse; do not introduce a hidden suspension that prevents falling.

## 3. Blend the actual fallen skeleton into a moving get-up animation

Use the owner's [Epic Animation Pose Snapshot reference](https://dev.epicgames.com/documentation/unreal-engine/animation-pose-snapshot-in-unreal-engine).
Capture the complete actual skeletal pose at the appropriate transition boundary,
with consistent LOD/bone coverage. Use `Save Pose Snapshot` / `Pose Snapshot` or the
corresponding native full-skeleton mechanism and an Animation Blueprint/AnimGraph
blend into the playing back/stomach get-up animation.

The current path stores only physical-body world transforms, draws them toward
the fixed first animation frame for about 0.8 seconds, and then advances playback.
Replace that visibly separate pose-preparation phase with a coherent skeletal
transition. Align heading and location with the actual fallen body and floor;
support back, front and a representative asymmetric/twisted fall. Coordinate
Animation Blueprint output, physics blending and Physics Control targets so the
snapshot blend affects the visible mesh and does not fight independent drives.
Do not claim that adding a snapshot node alone solves collision or grounding.

Retain physical fall continuity and impact response. A new hit can interrupt the
get-up and return to physics from the current visible pose; death remains terminal,
with no healing. Preserve blocked/unsupported recovery. Keep the full original
Mixamo sources and motions; no animation purchase or new source-selection task is
needed. Document any derived alignment/blend changes and remaining limitations.

## Focused acceptance for future authorized execution

Use one representative mannequin and ordinary-speed continuous footage with a
clear view of arms, trunk and soles. Reuse unaffected MSQ-87 evidence and keep all
earlier failed/corrected records. No six-profile matrix or broad feature sweep.

1. Arms meet the body naturally in the demonstrated affected falls/recovery rather
   than passing through or remaining embedded; no new sustained jitter/explosive
   separation. Record the changed collision pairs/shapes and relevant observations.
2. Feet contact the floor within the declared tolerance at spawn/reset and after
   get-up. Record visible-sole and physical-shape/floor measurements. The fallen
   body still rests on the surface and loss of usable support still permits a fall.
3. Back, front and one representative asymmetric/twisted settled pose transition
   into get-up without a distinct snap or hold that forces the animation's initial
   pose. Inspect the entire transition at ordinary speed; a small transform step
   metric alone does not establish natural motion. The result stays at the actual
   recovery location and uses the correct orientation.
4. Check only the coupled transitions: one hit interruption/retry/death sequence,
   one affected recovery under retained slowdown, and F6 without ammunition refill.
   Reuse existing blocked/unsupported and contact evidence unless the new handover
   changes those paths; repeat only the affected subset. Confirm the six fixtures
   still render without comparing their subjective feel.

The executor self-checks and provides an identified candidate, focused results,
continuous recordings, changed-file list and honest limits. The owner evaluates
the visible result under the experiment's existing direct-testing direction; this
planning request does not launch an independent review or resume the cancelled
MSQ-87 review. General project review rules outside this scoped experiment remain.

## Execution boundaries

Leave the issue unassigned in backlog with zero runs until an explicit start.
On authorized execution, use the existing Multica project, one production writer
at verified Astra/max/standard and one heavy workload at a time. Check the actual
editor/project/map/PIE and dirty state through official Epic MCP; preserve owner
sessions. Register new/derived asset fingerprints without replacing accepted
historical ones, use Git LFS for binary assets, and keep generated evidence in Saved.

Retain the six-mannequin set, purchased arms, lobby, independent instance state,
single hit path, corpse impacts, F6/F10 and the 0.25 world / 0.65 player slowdown.
No autonomous locomotion overhaul, AI, Mover migration, dismemberment, full push or
explosion ability, new art, lobby editing, paid service or successor dispatch.
The controller owns future scope acceptance, closure and the task-scoped commit.
