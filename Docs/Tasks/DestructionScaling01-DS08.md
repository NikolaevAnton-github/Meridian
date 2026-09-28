# MSQ-168 / DS-08: Physics update cleanup and integrated optimization handoff

Multica: MSQ-168 (`01a0e9bc-bdf9-784c-8920-01f1a8032378`), parent MSQ-160, stage 8. Prepared only; unassigned, no execution authorized by this revision. Start this task in a separate owner chat. Dependency: Implemented and committed MSQ-162 through MSQ-167; no DS-01 performance prerequisite.

Authority: [ImplementationOnly02](../Approvals/DestructionScaling01-ImplementationOnly02.json). Read the [shared implementation boundaries](DestructionScaling01.md); no recursive history read or DS-01 benchmark restart.

## Outcome

Complete the planned physics-side cleanup, integrate all optimizations and hand the playable result to the owner for evaluation.

## Implementation

- Remove redundant physics callbacks/subscriptions, repeated body/shape/filter setup and unnecessary work on unchanged sleeping bodies in the implemented fragment lifecycle. Keep required wake/contact notifications and immediate hit correctness.
- Use selective contact/query/CCD work only where the active state requires it. Preserve high-speed thin-piece and stack safety; do not disable necessary collision or CCD merely to reduce work.
- Resolve integration defects between identities, sleep/wake, pooling, shared support, worker results and rendering. Do not leave known stale-state or lifecycle defects as future optimization work.
- Keep collision geometry/fidelity, physics rate, bidirectional interaction and gameplay fragments intact. Collision simplification, lower rates, one-way debris, deletion or visual-only substitutes require a separate owner decision.
- Provide a short owner play-check guide using available interactions and F6. Full grenade/telekinesis abilities and collision-driven chain fracture remain outside scope unless separately authorized.

## Focused correctness and handoff

Build the integrated result and perform short checks of the transitions changed by this task, including reset and a representative mixed-owner/repeated interaction case. State implemented changes, functional limitations and known unresolved defects. Do not run a final load envelope campaign, long soak, matched PIE/standalone matrix or FPS acceptance test. Owner evaluation follows this handoff; no guaranteed FPS claim.

Deliver the scoped implementation, `Docs/DestructionScaling01DS08.md`, build result and concise evidence for changed behavior under `Saved/DestructionScaling01/DS08/`. Record exact source/DLL identity for runtime checks. Commit verified task-scoped changes, restore editor state and stop. No performance acceptance gate or owner-rating gate before the next separately started task. Execution/review routing follows the shared policy and any explicit owner exception in that chat.

New chat opener: "Start MSQ-168. Read Docs/Tasks/DestructionScaling01-DS08.md and the indicated shared boundaries/predecessor handoff. Implement this task only, with build and focused correctness checks, without benchmark campaigns. Do not start successors."
