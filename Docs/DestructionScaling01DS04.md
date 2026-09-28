# MSQ-164 / DS-04 handoff

Implemented in the [direct batch](DestructionScaling01Batch01.md), under the owner's [scoped exception](Approvals/DestructionScaling01-DirectBatch01.json).

Compatible mesh/material actors keep their rigid bodies for reuse. Prewarm has a finite allocation budget; acquisition grows when no compatible safe slot is available. Returned components spend two frames in quarantine to drain old contact events. Ownership, lifespan timer, delegates, materials/overlay, render/query flags, gravity, transforms, velocities and simulation state are reset before reuse.

The world owns strong resource references and immutable hull caches. Shared render groups update transforms without dirtying per instance and flush once per group. Compatible GC lifecycle commands are grouped into one solver enqueue per component, preserving FIFO revisions and all valid impulses. Lifetime guards cancel old occupants/reset work. World teardown invalidates guards and releases resources.

Diagnostics expose allocation, reuse, active/free state and failure counters. Focused evidence includes growth, cross-owner reuse, held return, immediate reuse interaction and F6. Final build/check identities are in the batch handoff.
