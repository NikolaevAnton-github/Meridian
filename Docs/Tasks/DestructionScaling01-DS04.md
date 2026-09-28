# MSQ-164 / DS-04: reuse fragment objects and batch submissions

Multica: MSQ-164 (`01a0e9bc-bd93-7eea-94bd-6630203989bb`), parent MSQ-160, stage 4. Prepared, unassigned, no execution authorized. Dependency: accepted DS-03 lifecycle and DS-02 identities and DS-01 benchmark. Read [shared acceptance](DestructionScaling01.md); execute this task only after owner start.

## Outcome

Reduce burst-time allocation, registration and cleanup costs and avoid repeated render/physics submissions. Pooling must not be presented as eliminating active rigid-body or contact cost.

## Work

- Cache immutable mesh/material/collision references and prewarm a bounded pool of compatible loose-piece actors/bodies where profiling supports it. Preserve first-hit behavior when the pool grows or is exhausted; record capacity without dropping pieces.
- On return/reuse, reset ownership/generation, delegates, timers, collision/query state, transform, sleep/held state and linear/angular velocity. Old callbacks and queued commands must not affect a new owner.
- Accumulate transforms by render group and mark rendering dirty once per batch. Batch compatible per-particle commands by solver/proxy while preserving required order and safe access phases.
- Measure allocation/registration/GC, batch build/apply time, render uploads and memory. Keep the existing exact physical representation; a new aggregate-body architecture is a separately scoped experiment if evidence requires it.

## Acceptance and handoff

Repeat burst/settle/reuse cycles, cross-owner reuse, pool growth, held-piece release, immediate hit after reuse, F6 during pending work and repeated PIE. No stale handle, body state, timer callback or projectile-history regression. Compare first-hit/burst p95/p99 and memory against DS-03 at identical workloads; report active solver cost separately.

Deliver `Docs/DestructionScaling01DS04.md`, scoped code/helpers, independent technical review and exact candidate evidence. Restore editor state and commit verified changes. Stop before DS-05.

New chat opener: "Start MSQ-164. Read Docs/Tasks/DestructionScaling01-DS04.md and the indicated program/predecessor sections. Execute only this task; do not start successors."
