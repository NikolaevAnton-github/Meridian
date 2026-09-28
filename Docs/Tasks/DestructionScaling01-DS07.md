# MSQ-167 / DS-07: Compact intact and shared debris rendering

Multica: MSQ-167 (`01a0e9bc-bde2-7088-bb7b-6f64de039f35`), parent MSQ-160, stage 7. Prepared only; unassigned, no execution authorized by this revision. Start this task in a separate owner chat. Dependency: Implemented and committed MSQ-166, DS-04 batching and DS-02 identities.

Authority: [ImplementationOnly02](../Approvals/DestructionScaling01-ImplementationOnly02.json). Read the [shared implementation boundaries](DestructionScaling01.md); no recursive history read or DS-01 benchmark restart.

## Outcome

Implement fewer render components for intact columns and shared rendering for compatible moving/sleeping debris, preserving appearance and physical interaction.

## Implementation

- Build compact intact sections/root proxies from the exact current geometry, UVs and materials. Damage switches only the affected representation, without a delayed hole, double drawing or rebuilding the entire column on first hit.
- Implement shared rendering for compatible detached pieces using stable handles and batched transforms. Keep separate validated physics/query identity; standard ISM is not an independently simulated-body container.
- Use sensible spatial groups and correct bounds/culling. Preserve swap-removal, cell migration, owner deletion, material overrides/fallbacks and shadows across every state.
- Preserve authored detail and original assets. VSM and Geometry Collection Nanite are already enabled. Derived render-only assets retain source relationships, use LFS and follow registry policy when applicable.
- Roll out the working representation from a small correctness fixture to the intended lobby scope. This task must deliver the rendering implementation, not stop at profiling or an experiment recommendation.

## Focused correctness and handoff

Build, inspect a few representative intact/damaged/moving/settled/reset views, and check exact hit/render mappings across transitions and migration. Owner makes the final visual/play/performance judgement after the optimization sequence. No mandatory same-view A/B campaign, separate visual capture campaign or RT/GPU improvement gate.

Deliver the scoped implementation, `Docs/DestructionScaling01DS07.md`, build result and concise evidence for changed behavior under `Saved/DestructionScaling01/DS07/`. Record exact source/DLL identity for runtime checks. Commit verified task-scoped changes, restore editor state and stop. No performance acceptance gate or owner-rating gate before the next separately started task. Execution/review routing follows the shared policy and any explicit owner exception in that chat.

New chat opener: "Start MSQ-167. Read Docs/Tasks/DestructionScaling01-DS07.md and the indicated shared boundaries/predecessor handoff. Implement this task only, with build and focused correctness checks, without benchmark campaigns. Do not start successors."
