# MSQ-161 / DS-01: controlled mass-destruction benchmark

Multica: MSQ-161 (`01a0e9bc-bd30-7217-86b3-8f7961574d6d`), parent MSQ-160, stage 1. Prepared, unassigned, no execution authorized. Read the baseline and shared acceptance in [the program](DestructionScaling01.md). Dependency: Perf02 `68f911c` accepted. Owner start authorizes this task only.

## Outcome

Build a reusable load fixture and attribute the remaining cost before selecting production changes. Exercise repeatable impulses/strain and controlled grab/release adapters without implementing player abilities or changing authored structural protection. Unsupported repeat-interaction paths in the starting build must be reported as limitations, not bypassed to claim success.

## Work

1. Reuse `Scripts/LobbyColumnsPerf02/` capture/parser logic and existing projectile/reset checks. Add unique Saved outputs, exact source/DLL/settings binding and instrumentation only where required.
2. Capture intact, 1/4/16-column burst, sustained fire, moving debris, settled mixed-owner piles, a second impulse after settling, a selected-piece grab/release attempt and F6. Use fixed views/input schedules; record actual released/awake/sleeping/kinematic piece counts. Counts such as 100/500/2000 are optional workload points, not production limits.
3. Separate GT application work, Chaos step/contact work, render/shadow work and GPU time. Measure spawn/register/destruction/GC, body/shape/contact counts, collision queries, support work and memory. Identify overlap; do not add overlapping scopes.
4. Compare an appropriate standalone game run with PIE on the same hardware/settings. Preserve screenshots separately. Include first-hit, burst, wake and reset hitches, not only steady state. Bound any failed overload capture and preserve its evidence.

## Acceptance and handoff

- Repeatable fixtures, frame-aligned CSV, uncapped paired timing where headroom is measured, at least the established capture duration/sample quality for stable states. Record invalid counters rather than filtering them into a claimed gain.
- A ranked cost table and explicit whole-frame budget. Report current hardware, workload and the gap to 120 FPS; do not infer capacity from total CPU/GPU utilization.
- Identify which later tasks have a measured opportunity and which depend primarily on interaction correctness. Record decisions still needed for impact damage and the minimum target hardware.
- No new production optimization or behavior change. Keep original editor/settings/assets clean. Deliver `Docs/DestructionScaling01DS01.md`, Saved evidence, scoped helper changes and independent technical review of the fixture/evidence.

New chat opener: "Start MSQ-161. Read Docs/Tasks/DestructionScaling01-DS01.md and the indicated program/predecessor sections. Execute only this task; do not start successors."
