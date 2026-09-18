# CombatTiming01: frame-rate-independent rifle cadence and projectile timing

Multica issue: **MSQ-82**.
Stage 2 of [CombatSlice01](CombatSlice01Plan.md).
Predecessor: [CombatFoundation01 / MSQ-68](CombatFoundation01.md), verified in
[the controller review](../CombatFoundation01Review.md), commit `da76c7d`.
The owner requested this follow-up as the **next task before MSQ-69**; see
[the exact decision](../Approvals/CombatTiming01-NextTask01.json).

## Problem and outcome

MSQ-68 schedules an 85 ms rifle interval but emits at most one shot per game
frame and discards a sufficiently late schedule. Ordinary frame rounding no
longer accumulates, yet low FPS and hitches can reduce the firing rate. Replace
this prototype limit with bounded scheduling that preserves the intended shot
count and projectile timing across a declared supported range of frame times.
Rendering and input sampling remain discrete; do not claim unlimited hitch
recovery, bitwise deterministic physics or an increase in rendered frame rate.

## Scope

- Schedule authoritative shots by simulation timestamps, not by render-frame
  count. Permit multiple due shots within a frame when appropriate. Preserve
  the 0.085 s tuning, semi/auto semantics and one round per accepted launch.
  A time accumulator, local substeps or event-ordered stepping may be used;
  choose the smallest coherent solution, not a new global simulation framework.
- Give each due bullet its actual scheduled birth time and only the elapsed
  flight time after birth. Keep launch pose/aim, near-cover checks, moving
  characters and obstruction queries temporally consistent within the supported
  interval. Do not spawn every overdue round at the current muzzle pose, move
  newborn rounds through the whole frame, or backdate a hit through geometry
  using unrecorded history. Document interpolation/history limits explicitly.
- Order trigger press/release, action locks, reload commit/cancellation, mode
  changes and reset against due shots under a stated input-sampling contract.
  Do not replay missed shots from before a reload, after release/reset or from
  another firing session. Capacity/no-ammo rejection must conserve ammunition
  and never produce a phantom shot or later backlog burst.
- Bound catch-up time, steps, births and feedback work. Declare the supported
  hitch window (at least 250 ms), numerical tolerances and treatment of time
  beyond the budget. Size the work budget for the shortest supported weapon
  interval, including the retained 50 ms clamp, rather than only the default
  85 ms interval.
  Extreme stalls must not create an unbounded loop, effects burst or growing
  debt. Retain the existing projectile and transient-effect safety limits unless
  a necessary bounded change is documented and verified.
- Preserve the MSQ-68 time/self-hit contract: world-scaled bullet motion and age,
  exact stop/resume, normal player movement, moving-player contact with a frozen
  own bullet, geometric launch clearance, per-bullet birth capsule history and
  reset-safe callback dispatch. State which clocks drive firing and bullet
  simulation; avoid double scaling. The later player-facing time ability and
  remaining player-action timing choices are outside this task.
- Preserve PurchasedArms06 presentation and existing movement/ADS feel. Define
  how several simulated shots map to bounded recoil, sound, muzzle and animation
  presentation without restarting all montages as a stack of overdue effects.
  Preserve the documented simultaneous-step obstruction policy, or explicitly
  replace it with a tested temporal policy that prevents array-order tunneling.
  When comparing segments with different birth times/durations, use absolute
  contact timestamps; their normalized hit fractions are not comparable times.

No enemies, player health, new ability bindings, new art, lobby changes,
networking or project-wide physics settings overhaul is part of this task.

## Focused acceptance

1. Use a known trigger/time schedule and an independent expected timestamp/count
   calculation. Verify the unchanged rifle interval at 30, 60, 120 and 144 FPS
   plus 10 FPS (below the rifle's shots-per-second rate), with enough ammunition
   and capacity. Compare equal firing-clock windows, including endpoint rules,
   rather than only rounded average rate. The low-FPS case must exercise more
   than one due shot in a frame. Measured real captures and controlled timestep
   checks must be labelled separately if hardware cannot sustain a requested cap.
2. Inject bounded 150/250 ms hitches and jittered frame intervals. Within the
   declared catch-up budget, counts, ammunition and scheduled times agree with
   the reference. An extreme stall beyond that budget has the documented bounded
   outcome and no accumulating backlog. Record actual frame times and work caps.
3. A controlled long-frame case verifies distinct bullet births, residual flight
   distances/ages and collision once. Include moving/turning launch pose, near or
   thin cover, and a one-hit foreground target shielding another target. Compare
   the same timeline at finer steps; any permitted tolerance must be justified.
4. Focused long-frame boundaries cover trigger release/repress, one reload commit
   or cancellation, depleted magazine/reserve, capacity denial, mode change and
   callback-triggered reset. No duplicates, obsolete-session shots or ammo creation.
   Reuse prior unaffected reload-variant evidence instead of the full matrix.
5. Exercise the changed time paths at bullet scales 1, 0.25 and exactly 0. New
   rounds during stop stay at their proper birth positions; simulated age stays
   frozen. A moving player can contact a suspended own round once, with correct
   attribution; resume and reset remain clean. New launches must not erase older
   bullets' capsule history or create pre-birth self-contact.
6. Successful native build/fresh load and short actual hip/ADS firing footage at
   normal and low FPS show bounded, coherent presentation. Check only directly
   affected moving/airborne transitions. Stop/reset removes transient state;
   owner configuration, retained map/assets and historical evidence are preserved.

## Execution and handoff

Use one existing Multica Unreal executor at Astra/max/standard, verified in the
profile, native arguments and actual run. Follow the parent's preservation,
one-writer and focused-review rules. Reuse `Scripts/CombatFoundation01/` and its
existing transport/probes; add only bounded timing cases, not another harness.
Confirm live editor/project/PIE/dirty state before mutation and preserve an owner
session. The controller reviews the implementation and bounded corrections,
then closes and commits this task before MSQ-69 can begin.

Deliver `Docs/CombatTiming01.md` describing scheduling, clocks, birth/collision
ordering, presentation, supported frame/hitch range, measured results and exact
overload limits. Preserve earlier MSQ-68 reports unchanged. Store logs, exact
candidate hashes, comparisons and recordings under
`Saved/CombatSlice01/CombatTiming01/`. Technical acceptance remains separate from
owner play/visual acceptance. No successor is automatically dispatched.
