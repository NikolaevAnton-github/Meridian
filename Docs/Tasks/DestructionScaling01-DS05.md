# MSQ-165 / DS-05: shared local support and event-driven updates

Multica: MSQ-165 (`01a0e9bc-bdaf-730f-bc24-9b9eae2be879`), parent MSQ-160, stage 5. Prepared, unassigned, no execution authorized. Dependency: accepted DS-04 and the DS-03 lifecycle. Read [shared acceptance](DestructionScaling01.md); owner start authorizes this task only.

## Outcome

Make support/pose maintenance follow changed nearby fragments, including piles formed from several owners. Remove redundant scans while preserving exact support and wake behavior.

## Work

- Precompute authored bone-to-facing relationships and immutable hull data. Gather reusable state once per safe phase rather than rebuilding leaf lists and locking physics separately for every candidate.
- Maintain a shared spatial candidate index and explicit support dependencies. Conservative broad-phase selection must retain every possible support; exact collision tests remain authoritative.
- Propagate moved, removed, fractured, grabbed and awakened support changes to affected dependents. Distinguish structural attachment from physical resting contact; use Chaos contacts/sleep where suitable instead of duplicating the solver.
- Queue dirty work and stagger nonurgent maintenance. First-hit/history decisions and urgent support-loss wake cannot be delayed arbitrarily. Preserve deterministic selection/mutation ordering where the existing contract needs it.
- Use the benchmark to distinguish remaining projectile blocker collection cost from fragment support work. Do not rewrite unrelated ballistic history merely to expand this task.

## Acceptance and handoff

Own-owner and mixed-owner stacks behave correctly when lower pieces are moved, removed or thrown. No hovering, missed wake or missed support across spatial-cell boundaries. Actor/component lifecycle, F6 and world recreation clear dependencies safely. Record exact query counts and support time for intact, moving and sleeping workloads; stationary work must decrease without hiding interaction.

Deliver `Docs/DestructionScaling01DS05.md`, focused regression fixtures, source/DLL-bound evidence and primary independent technical review. Commit the accepted task and stop before DS-06.

New chat opener: "Start MSQ-165. Read Docs/Tasks/DestructionScaling01-DS05.md and the indicated program/predecessor sections. Execute only this task; do not start successors."
