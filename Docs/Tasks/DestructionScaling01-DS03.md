# MSQ-163 / DS-03: Reversible sleeping and repeated fragment interaction

Multica: MSQ-163 (`01a0e9bc-bd7a-797c-8d36-f0abb5f6cf4a`), parent MSQ-160, stage 3. Prepared only; unassigned, no execution authorized by this revision. Start this task in a separate owner chat. Dependency: Implemented and committed MSQ-162.

Authority: [ImplementationOnly02](../Approvals/DestructionScaling01-ImplementationOnly02.json). Read the [shared implementation boundaries](DestructionScaling01.md); no recursive history read or DS-01 benchmark restart.

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

Deliver the scoped implementation, `Docs/DestructionScaling01DS03.md`, build result and concise evidence for changed behavior under `Saved/DestructionScaling01/DS03/`. Record exact source/DLL identity for runtime checks. Commit verified task-scoped changes, restore editor state and stop. No performance acceptance gate or owner-rating gate before the next separately started task. Execution/review routing follows the shared policy and any explicit owner exception in that chat.

New chat opener: "Start MSQ-163. Read Docs/Tasks/DestructionScaling01-DS03.md and the indicated shared boundaries/predecessor handoff. Implement this task only, with build and focused correctness checks, without benchmark campaigns. Do not start successors."
