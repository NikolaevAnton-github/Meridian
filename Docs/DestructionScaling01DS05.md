# MSQ-165 / DS-05 handoff

Implemented in the [direct batch](DestructionScaling01Batch01.md), under the owner's [scoped exception](Approvals/DestructionScaling01-DirectBatch01.json).

Cladding precomputes support-bone-to-tile relationships. Immutable collision hulls are cached by source mesh or collection/bone/scale. The shared world indexes every occupied spatial cell of each body's conservative bounds, then exact native shape queries validate local support candidates across owners.

Explicit resting-contact dependencies propagate movement, wake, grab and removal. NGD collision publication invalidates attached/static owner supports immediately. Static-component transform/lifetime sentinels stay cheap; nonurgent validation is staggered. Unchanged sleeping bodies skip geometry processing and repeated full support scans. A 0.01 cm accumulated support-motion tolerance prevents numerical contact jitter from waking a whole pile.

Worker output is validated before authoritative support application. Projectile history still samples both boundaries; managed fragment identity is preserved during body reuse. Final focused support/migration/reset results are in the batch handoff.
