# MSQ-162 / DS-02: Stable fragment identity and serial state processing

Multica: MSQ-162 (`01a0e9bc-bd60-7be4-ad92-dcc8a82ecd63`), parent MSQ-160, stage 2. Implemented in the owner-started direct batch; local delivery verified, owner verdict pending. Multica board state was not changed. Dependency: Perf02 `68f911c`; MSQ-161 is not a dependency.

Current authority: [DirectBatch01](../Approvals/DestructionScaling01-DirectBatch01.json), superseding separate-chat and independent-review routing for MSQ-162..167. Delivery: [batch report](../DestructionScaling01Batch01.md). Original implementation scope: [ImplementationOnly02](../Approvals/DestructionScaling01-ImplementationOnly02.json). Read the [shared implementation boundaries](DestructionScaling01.md); no recursive history read or DS-01 benchmark restart.

## Outcome

Implement the shared identity and state-processing foundation used by the later optimizations. Deliver working code, not a new analysis or benchmark plan.

## Implementation

- Give each gameplay fragment an owner/reset-generation/local identity and state/pose revisions independent of actor addresses, render indices and Hit.Item. Resolve exact hit identity before swap/removal, reuse or deferred work.
- Consolidate repeated state gathering into owned immutable snapshots and reusable serial pose, hull-bottom and support-candidate calculations. Keep exact engine queries, UObject writes and solver commands in their safe phases.
- Add narrow selected-fragment target, impulse/wake and hold/release adapters, with explicit unsupported-state results. Preserve projectile deduplication, both history boundaries and first-hit ordering.
- Reject stale generations/revisions after F6, owner replacement/deletion, motion and state changes. Do not retain borrowed component arrays or raw Chaos pointers across these transitions. Leave lifecycle policy changes to DS-03.

## Focused correctness and handoff

Build the restored production source before runtime work: the stopped DS-01 diagnostic DLL is not the source baseline. Check serial behavior against the existing production path on representative first-hit, instance-swap and F6/deletion cases. Selected identity, ordering, poses and support decisions must remain correct. Document snapshot ownership and apply phases for DS-03/DS-06; no snapshot-overhead campaign is required.

Delivered implementation and [stage handoff](../DestructionScaling01DS02.md) are included in the direct batch. Final successful build, exact source/DLL identity, focused checks and approximate frame-time comparison are recorded in the batch report and `Saved/DestructionScaling01/`. The owner explicitly waived Multica execution and independent review for these six tasks. MSQ-168 remains unstarted; final visual/play/performance acceptance belongs to the owner.
