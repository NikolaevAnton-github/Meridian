# MSQ-166 / DS-06: parallel fragment calculation

Multica: MSQ-166 (`01a0e9bc-bdc8-79ed-9f1f-11f1c1e5bffc`), parent MSQ-160, stage 6. Prepared, unassigned, no execution authorized. Dependency: accepted DS-05 data/dependency model, DS-02 serial snapshot seam and DS-01 measurements. Read [shared acceptance](DestructionScaling01.md); owner start authorizes this task only.

## Outcome

Implement measured parallelism for expensive pure work: immutable snapshot, coarse worker jobs, then validated authoritative apply. Profile the entire path, including copy, scheduling, locks, waits and application.

## Work

- Snapshot stable IDs/revisions, transforms, velocities, flags, immutable hull geometry and candidate relationships at the correct physics phase. Jobs own their input/output storage.
- Parallelize supported calculations such as candidate selection, fragment poses, convex lowest points and impulse math. No arbitrary worker access to UObjects, world traces, shared mutable maps or borrowed Chaos pointers.
- Validate generation and pose/state revisions before applying results or queuing physics commands. Stale F6, deletion, movement, grab and reuse results must be rejected or recomputed.
- Schedule sufficiently early and in coarse batches. Measure a serial path for small workloads; avoid one task per fragment and launch-immediate-wait patterns. Preserve same-frame hit/history dependencies with explicit completion boundaries.
- Compare task worker contention with existing renderer/Chaos work. Enabling async physics or changing timestep is not a substitute for this task and requires a separate measured correctness experiment.

## Acceptance and handoff

Equivalent selected fragments, transforms, support decisions and ordering across serial/parallel paths under controlled input. Exercise F6, owner deletion, cross-cell motion and reuse while work is pending. No race, stale pointer or missed first hit. Report snapshot/job/wait/apply distributions and total frame p95/p99 at small and large loads; retain only useful defaults and preserve rejected experiments.

Deliver `Docs/DestructionScaling01DS06.md`, scoped implementation, meaningful concurrency/regression evidence and primary independent technical review. Verify installed UE 5.8 APIs and max/standard execution settings. Commit and stop before DS-07.

New chat opener: "Start MSQ-166. Read Docs/Tasks/DestructionScaling01-DS06.md and the indicated program/predecessor sections. Execute only this task; do not start successors."
