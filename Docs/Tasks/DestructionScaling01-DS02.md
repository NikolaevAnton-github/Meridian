# MSQ-162 / DS-02: stable fragment identity and serial snapshot/apply seams

Multica: MSQ-162 (`01a0e9bc-bd60-7be4-ad92-dcc8a82ecd63`), parent MSQ-160, stage 2. Prepared, unassigned, no execution authorized. Dependency: accepted DS-01 fixture/report and its committed baseline. Read [shared acceptance](DestructionScaling01.md); owner start authorizes DS-02 only.

## Outcome

Create a small shared fragment contract for the existing lobby NGD lane before changing rest behavior or introducing threads. Every gameplay fragment has owner/reset-generation/local identity and state/pose revisions independent of actor addresses, render indices or Hit.Item.

## Work

- Resolve exact hit identity before instance swap/removal, object reuse or deferred commands. Preserve existing projectile deduplication, first-hit ordering and both history boundaries.
- Extract owned immutable state snapshots and pure pose/hull-bottom/candidate calculations, still running serially. Keep exact engine queries, UObject mutation and solver commands in their current safe phases.
- Add narrow target, force/wake and hold/release test entry points with explicit unsupported-state results. Validate installed per-fragment APIs; do not assume GeometryCollection AddImpulse's BoneName selects one piece. No full abilities, new collision damage or retention-policy changes.
- Invalidate retired generations/revisions on reset, EndPlay, owner replacement, motion and state changes. Snapshot inputs/results must not retain borrowed components or raw Chaos pointers through those transitions.

## Acceptance and handoff

Compare the serial extracted path against the accepted baseline: identical selected pieces, poses, support candidates, ordering and supported transitions. No retargeting after instance swap or actor replacement. F6/deletion invalidate queued results and old IDs. Measure snapshot/copy/apply overhead and document exact phase/ownership contracts for DS-03 and DS-06. Existing rest/expiry behavior remains visible until DS-03 replaces it.

Deliver `Docs/DestructionScaling01DS02.md`, focused fixtures, source/DLL-bound evidence and one primary independent technical review. Keep unmodified specimens and owner assets intact. Commit the accepted change and stop before DS-03.

New chat opener: "Start MSQ-162. Read Docs/Tasks/DestructionScaling01-DS02.md and the indicated program/predecessor sections. Execute only this task; do not start successors."
