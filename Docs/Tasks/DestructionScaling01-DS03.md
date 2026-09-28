# MSQ-163 / DS-03: Reversible sleeping and repeated fragment interaction

Multica: MSQ-163 (`01a0e9bc-bd7a-797c-8d36-f0abb5f6cf4a`), parent MSQ-160, stage 3. Implemented in the owner-started direct batch; local delivery verified, owner verdict pending. Multica board state was not changed. Dependency: Implemented and committed MSQ-162.

Current authority: [DirectBatch01](../Approvals/DestructionScaling01-DirectBatch01.json), superseding separate-chat and independent-review routing for MSQ-162..167. Delivery: [batch report](../DestructionScaling01Batch01.md). Original implementation scope: [ImplementationOnly02](../Approvals/DestructionScaling01-ImplementationOnly02.json). Read the [shared implementation boundaries](DestructionScaling01.md); no recursive history read or DS-01 benchmark restart.

## Outcome

Replace permanent fragment freezing with a reversible lifecycle and roll it out to the scoped lobby fragments.

## Implementation

- Implement attached, dynamic-awake, dynamic-asleep and temporarily-held states using DS-02 IDs/revisions. Replace forced NeverSleep and permanent kinematic retention with ordinary sleep and explicit wake paths.
- Keep settled pieces collidable and targetable. Direct impulse, contact, moved/deleted support and grab must wake the correct pieces; release/throw returns the selected piece to simulation with the intended velocity.
- Remove the old 12-second expiry and shard eviction as implicit deletion policies for gameplay fragments. Preserve fragments; expose allocation/capacity failures without silently dropping pieces. Do not invent a new runtime fragment cap.
- Implement conservative support-loss invalidation across owners now; DS-05 will optimize it. A held piece may be temporarily kinematic, but must leave that state correctly.
- Use validated per-particle APIs, not an assumed GeometryCollection AddImpulse BoneName selector. Preserve protected cores/upper sections and existing first-hit/projectile contracts.
- Keep collision-driven fracture disabled unless separately authorized. That open impact-damage decision does not block force, wake, grab or release implementation.

## Focused correctness and handoff

Use a small representative interaction fixture to check settle beyond the old lifetime, second impulse, selected grab/release, thin/high-speed pieces, moved/deleted support, F6 and owner deletion. No hovering, collection-wide accidental manipulation, stale velocity or permanent frozen pile. Extend the implementation across the lobby without a mandatory 1/4/16 performance matrix.

Delivered implementation and [stage handoff](../DestructionScaling01DS03.md) are included in the direct batch. Final successful build, exact source/DLL identity, focused checks and approximate frame-time comparison are recorded in the batch report and `Saved/DestructionScaling01/`. The owner explicitly waived Multica execution and independent review for these six tasks. MSQ-168 remains unstarted; final visual/play/performance acceptance belongs to the owner.
