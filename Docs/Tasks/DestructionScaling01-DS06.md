# MSQ-166 / DS-06: Parallel fragment calculations with validated apply

Multica: MSQ-166 (`01a0e9bc-bdc8-79ed-9f1f-11f1c1e5bffc`), parent MSQ-160, stage 6. Prepared only; unassigned, no execution authorized by this revision. Start this task in a separate owner chat. Dependency: Implemented and committed MSQ-165, using the DS-02 serial reference.

Authority: [ImplementationOnly02](../Approvals/DestructionScaling01-ImplementationOnly02.json). Read the [shared implementation boundaries](DestructionScaling01.md); no recursive history read or DS-01 benchmark restart.

## Outcome

Implement coarse parallel jobs for independent fragment calculations and retain safe authoritative application.

## Implementation

- Snapshot owned IDs/revisions, transforms, velocities, flags, immutable hull geometry and candidate relationships at the correct physics phase.
- Move supported pure calculations, such as candidate selection, fragment poses, convex lowest points and impulse math, into coarse worker batches. Keep UObjects, world traces, mutable shared maps and borrowed Chaos pointers out of jobs.
- Validate reset-generation and state/pose revisions before apply. Reject or recompute results invalidated by F6, deletion, movement, grab or reuse.
- Schedule work early enough to overlap useful work; avoid one job per fragment and immediate wait after launch. Keep a serial path for small workloads and explicit completion boundaries for same-frame hit/history dependencies.
- Use the installed UE 5.8 task APIs and explicit job/storage lifetimes. Do not change async-physics mode or timestep as a substitute.

## Focused correctness and handoff

Build and compare serial/parallel outputs on a small controlled case. Check pending-work cancellation/invalidation during reset, deletion, cross-cell motion and reuse. No races, stale pointers, changed hit ownership or ordering. Supply optional diagnostic job/wait counters; no required parallelism benchmark or frame-time gate.

Deliver the scoped implementation, `Docs/DestructionScaling01DS06.md`, build result and concise evidence for changed behavior under `Saved/DestructionScaling01/DS06/`. Record exact source/DLL identity for runtime checks. Commit verified task-scoped changes, restore editor state and stop. No performance acceptance gate or owner-rating gate before the next separately started task. Execution/review routing follows the shared policy and any explicit owner exception in that chat.

New chat opener: "Start MSQ-166. Read Docs/Tasks/DestructionScaling01-DS06.md and the indicated shared boundaries/predecessor handoff. Implement this task only, with build and focused correctness checks, without benchmark campaigns. Do not start successors."
