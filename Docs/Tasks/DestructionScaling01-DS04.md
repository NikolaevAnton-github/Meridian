# MSQ-164 / DS-04: Fragment reuse, cached resources and batched submissions

Multica: MSQ-164 (`01a0e9bc-bd93-7eea-94bd-6630203989bb`), parent MSQ-160, stage 4. Prepared only; unassigned, no execution authorized by this revision. Start this task in a separate owner chat. Dependency: Implemented and committed MSQ-163, using DS-02 identities.

Authority: [ImplementationOnly02](../Approvals/DestructionScaling01-ImplementationOnly02.json). Read the [shared implementation boundaries](DestructionScaling01.md); no recursive history read or DS-01 benchmark restart.

## Outcome

Implement object reuse and batching to remove repeated allocation, registration and render/physics submissions.

## Implementation

- Cache immutable mesh/material/collision references. Add compatible loose-piece actor/body pools and a finite prewarm allocation; grow safely when needed instead of dropping fragments or using pool size as a gameplay cap.
- Reset ownership/generation, delegates, timers, collision/query state, transforms, sleep/held state and velocities on every return/reuse. Old callbacks and pending commands must not affect the next occupant.
- Accumulate transforms per render group and mark rendering dirty once per batch. Batch compatible solver/proxy commands while preserving required mutation order and safe physics access.
- Release pool resources on world teardown and reset without stale references. Keep allocation/active/free counters available for diagnosis, without a benchmark deliverable.
- Retain exact physical representation. Pooling does not replace active rigid bodies or contacts; no aggregate-body redesign in this task.

## Focused correctness and handoff

Build and check a bounded reuse cycle, cross-owner reuse, growth/exhaustion fallback, immediate hit after reuse, held-piece return and F6/world teardown with pending work. Verify clean body state and bounded ownership of cached resources. No required A/B timing, p95/p99 target or repeated long capture.

Deliver the scoped implementation, `Docs/DestructionScaling01DS04.md`, build result and concise evidence for changed behavior under `Saved/DestructionScaling01/DS04/`. Record exact source/DLL identity for runtime checks. Commit verified task-scoped changes, restore editor state and stop. No performance acceptance gate or owner-rating gate before the next separately started task. Execution/review routing follows the shared policy and any explicit owner exception in that chat.

New chat opener: "Start MSQ-164. Read Docs/Tasks/DestructionScaling01-DS04.md and the indicated shared boundaries/predecessor handoff. Implement this task only, with build and focused correctness checks, without benchmark campaigns. Do not start successors."
