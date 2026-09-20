# PhysicsControlStepping01: reactive steps to retain balance after hits

Prepared 2026-09-20. Multica issue: **MSQ-89**, a planning-only follow-up
to MSQ-88 Candidate04 in the CombatSlice01 / MSQ-67 family. The owner likes the
current hit reaction and asks for a short retreat or stumble in response to the
hit direction while the mannequin attempts to remain standing. See the
[exact request and planning decision](../Approvals/PhysicsControlStepping01-TaskCreation01.json).
This record authorizes task creation only, not implementation or review.

Baseline: [MSQ-88 implementation](../PhysicsControlRecovery01.md),
[controller handoff](../PhysicsControlRecovery01Handoff.md), and commit `c618623`.
Keep its immutable candidates, sources, evidence and the owner's current edits.
The owner says the current result looks good and specifically likes its hit
reaction. Stepping should extend that retained experimental behavior.

## Intended behavior

- A weak disturbance keeps the existing localized hit response and recovery in
  place. A recoverable larger disturbance can trigger one short balance-recovery
  step, with a second step only when needed. This is a bounded first experiment,
  not continuous walking, chasing or navigation.
- Step toward the displaced balance, using actual body lean/motion together with
  the applied hit impulse. A hit from the front can produce a retreat; a lateral
  hit can produce a side step. Resolve directions consistently with the current
  body orientation and world space, not a fixed scene axis or the hit-point
  position alone. Retain local physical reactions during the step.
- Choose a usable support leg and a moving foot. Show weight transfer, foot
  lift, placement and settling into a new stance. Coordinate the pelvis, torso,
  animation/pose output and Physics Control targets so both feet do not simply
  slide along with a translated actor. Keep the planted foot stable within a
  declared, measured tolerance and preserve the visible-sole grounding baseline.
- Accept a foot destination only when it has a reachable floor surface and
  sufficient clearance. Do not step into walls, through the floor or over an
  unsupported edge. A blocked step must not create suspension or unlimited
  resistance to falling. Excessive disturbance, unavailable legs or loss of
  usable support still releases the body into the existing physical fall.
- Finish at the recovered position and update the standing support targets
  there. Ordinary recovery must not pull the mannequin back to its old home
  transform. F6 retains its explicit reset-to-home role.
- A new hit during stepping can update the bounded recovery attempt or cause
  collapse from the current physical pose. Avoid indefinitely queued steps,
  hard pose resets or healing. Death is terminal and immediately prevents new
  steps; corpse impacts and the retained living get-up remain available.

Step length, duration, trigger threshold, cooldown, maximum reach and correction
strength are tunable implementation proposals, not owner-approved numeric values.
Keep the first trial to at most two recovery steps per episode. Expose the useful
tuning values without creating a new six-profile comparison task. The executor
may choose a suitable procedural/IK or existing-animation route after inspecting
the installed capabilities; this plan does not select a new animation purchase,
paid service or replacement character asset.

## Focused acceptance for future authorized execution

Use one representative mannequin and ordinary-speed continuous recordings that
show both feet, the trunk and the floor. Reuse applicable MSQ-88 evidence. Confirm
all six fixtures render, without running a per-profile gameplay or visual matrix.

1. Demonstrate the retained weak-hit reaction and a recoverable hit that causes
   one or two visible steps, then stable standing at the new location. Cover a
   frontal and a lateral disturbance, including a turned body orientation, to
   establish the directional rule. Include real rifle input through the existing
   authoritative contact path. Record chosen foot, step phase, impulse/body
   direction and resulting stance rather than relying on actor displacement alone.
2. Demonstrate support-foot planting, swing-foot clearance and landing, without
   persistent visible skating, hovering or sinking. Reuse the 1 cm stable visible-
   sole tolerance unless a justified change is explicitly documented. Check one
   blocked or unsupported destination and usable-leg loss; no hidden suspension
   or forced foot placement into invalid space. Declare any floor/slope limits.
3. Check the newly coupled transitions: another hit during a step, a physical
   collapse followed by the retained living get-up at the displaced location, and
   terminal death during a recovery attempt. Reuse unaffected get-up/corpse tests;
   repeat only a subset invalidated by the step handover. There is no automatic
   return to the old stance origin and no healing.
4. Check one affected step under the retained world/player slowdown, and F6
   during/after stepping without ammunition refill. Clear instance-local step
   state on reset and fixture recreation, preserving Ctrl+F7/Ctrl+F8 behavior.
   Confirm the six fixtures still render; the owner judges weight and feel.

The executor supplies an identified candidate, a concise changed-file list,
focused results, continuous recordings, actual measurements and honest limits.
Numerical checks alone do not establish convincing weight transfer. Final motion
and play acceptance belong to the owner. This planning request dispatches no
independent checker and does not resume the cancelled MSQ-87 review. Follow the
applicable owner review direction when a later explicit execution start arrives;
the earlier MSQ-88 waiver is not rewritten as a universal project rule.

## Execution boundaries

Create the issue unassigned in backlog with zero runs. Do not start the task
runtime, assign an executor/reviewer or mutate gameplay/editor state for this
planning request. A later explicit start is required for implementation.

On authorized execution, use the existing Multica project, one production writer
at verified native Astra/max/standard and one heavy workload at a time. Confirm
the live project, map, PIE and dirty state through official Epic MCP before
mutations, preserving owner sessions. Use existing focused probes and recording
tools; do not rebuild the benchmark harness. Keep evidence under
`Saved/CombatSlice01/PhysicsControlStepping01/` and use Git LFS for new binary assets.

Preserve the six independent fixtures, current hit feel and damage path,
self-collision, calibrated feet, complete pose-snapshot get-up, original Mixamo
sources, purchased arms, lobby, F6/F10, optional combat test controls and the
0.25 world / 0.65 player slowdown. Any changed shared asset needs a scoped derivative
and appropriate registry inventory without replacing historical fingerprints.

No autonomous locomotion overhaul, enemy AI, pursuit/navigation, Mover migration,
full push/explosion ability, dismemberment, new art, lobby changes, paid service or
successor dispatch. Configurable replacement get-up clips were a separate question
and are not added to this stepping task. The controller owns future scope/evidence
acceptance, registry/status administration and the task-scoped closure commit.
