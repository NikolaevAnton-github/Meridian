# MSQ-165 / DS-05: Shared local support and updates driven by changes

Multica: MSQ-165 (`01a0e9bc-bdaf-730f-bc24-9b9eae2be879`), parent MSQ-160, stage 5. Prepared only; unassigned, no execution authorized by this revision. Start this task in a separate owner chat. Dependency: Implemented and committed MSQ-164 and the DS-03 lifecycle.

Authority: [ImplementationOnly02](../Approvals/DestructionScaling01-ImplementationOnly02.json). Read the [shared implementation boundaries](DestructionScaling01.md); no recursive history read or DS-01 benchmark restart.

## Outcome

Replace repeated broad scans with shared local support dependencies and updates restricted to affected fragments.

## Implementation

- Precompute bone-to-facing relationships and immutable hull data. Gather state once per safe phase instead of rebuilding lists or repeatedly locking the same physics data.
- Maintain a shared spatial candidate index and explicit support dependencies across owners. Conservative candidate selection must include every possible support; exact tests remain authoritative.
- Invalidate affected dependents when support moves, disappears, fractures, is grabbed or wakes. Distinguish structural attachment from resting physical contact; use Chaos contact/sleep information where appropriate.
- Queue changed work and stagger nonurgent maintenance. First-hit/history decisions and urgent support-loss wake remain timely. Preserve deterministic selection/mutation order where required.
- Keep projectile blocker/history semantics intact. Reuse available state within the scoped fragment path; do not expand into unrelated ballistic rewrites.

## Focused correctness and handoff

Check own-owner and mixed-owner support, spatial-cell crossing, moved/deleted lower pieces, sleep/wake, F6 and world recreation. Verify that unchanged sleeping fragments avoid repeated full scans while affected neighbours update correctly. Use targeted counters/assertions if needed; no timed workload campaign.

Deliver the scoped implementation, `Docs/DestructionScaling01DS05.md`, build result and concise evidence for changed behavior under `Saved/DestructionScaling01/DS05/`. Record exact source/DLL identity for runtime checks. Commit verified task-scoped changes, restore editor state and stop. No performance acceptance gate or owner-rating gate before the next separately started task. Execution/review routing follows the shared policy and any explicit owner exception in that chat.

New chat opener: "Start MSQ-165. Read Docs/Tasks/DestructionScaling01-DS05.md and the indicated shared boundaries/predecessor handoff. Implement this task only, with build and focused correctness checks, without benchmark campaigns. Do not start successors."
