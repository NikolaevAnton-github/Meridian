# MSQ-167 / DS-07: fewer render components through all fragment states

Multica: MSQ-167 (`01a0e9bc-bde2-7088-bb7b-6f64de039f35`), parent MSQ-160, stage 7. Prepared, unassigned, no execution authorized. Dependency: accepted DS-06 and current DS-01 render attribution. Read [shared acceptance](DestructionScaling01.md); owner start authorizes this task only.

## Outcome

Evaluate a compact intact-column representation and shared rendering for detached pieces while retaining separate stable physical identity and exact hit ownership. Start with one column/a small neighbouring group; extend only a proven candidate.

## Work

- Prototype a few intact sections/root proxies from the exact current geometry, UVs and materials. On damage, reveal only affected fragment representation without a delayed hole, double drawing or rebuilding the whole column at first hit.
- Use DS-04 batches and DS-02 identity to pilot shared rendering for compatible moving/sleeping debris. Standard ISM is not an independently simulated rigid-body container; keep validated physics/query ownership separate.
- Profile visible components, draw/shadow preparation, transform uploads, bounds/culling and any ray-tracing scene update cost. Larger groups must not erase the benefit in opposite views or moving piles.
- Preserve default/fallback material behavior and authored detail. VSM and GC Nanite are already enabled. Generated render-only assets, if needed, retain source relationships and use LFS; preserve original assets and follow registry policy when it applies.

## Acceptance and handoff

Independent same-view visual comparison for intact, first hit, damaged, moving, settled and F6 states. Exact collision/hit maps remain valid during transitions, swap removal, migration and owner deletion. Measure first-hit/burst hitches as well as steady-state RT/GPU and frame p95/p99. Review both intact and moving-debris experiments separately; keep only measured improvements and clearly record the accepted rollout.

Deliver `Docs/DestructionScaling01DS07.md`, candidate-bound technical and independent visual evidence, source/asset identities and primary review. Owner design/play acceptance remains separate. Commit accepted changes and stop before DS-08.

New chat opener: "Start MSQ-167. Read Docs/Tasks/DestructionScaling01-DS07.md and the indicated program/predecessor sections. Execute only this task; do not start successors."
