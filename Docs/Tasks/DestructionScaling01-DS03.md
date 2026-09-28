# MSQ-163 / DS-03: reversible fragment rest and repeated interaction

Multica: MSQ-163 (`01a0e9bc-bd7a-797c-8d36-f0abb5f6cf4a`), parent MSQ-160, stage 3. Prepared, unassigned, no execution authorized. Dependency: accepted DS-02 identities/serial snapshot seam and DS-01 fixture/report. Read [shared acceptance](DestructionScaling01.md); owner start authorizes DS-03 only.

## Outcome

Prototype a reversible lifecycle on one column, then validate it across the lobby. Use DS-02 stable identities and revisions for attached, dynamic-awake, dynamic-asleep and temporarily-held transitions.

## Work

- Exercise DS-02 target/impulse/grab/release routes through the existing NGD/Chaos integration. Preserve projectile deduplication and both history boundaries.
- Replace forced NeverSleep and permanent kinematic retention for the scoped gameplay fragments with ordinary rest and explicit wake paths. Preserve collision and targeting after settling. A grab/release returns the selected piece to simulation with correct velocity, without affecting every bone in its collection.
- Audit expiry/shard eviction against the persistent interaction contract. Make workload/capacity visible; do not silently delete gameplay fragments. Keep cosmetic classification and any finite production retention policy explicit rather than inventing one.
- Use conservative support invalidation/waking until DS-05 optimizes it; correct support-loss handling across owners must not depend on a future task. Test rest beyond the old 12-second lifetime and old retention limits within the finite workload.
- Validate installed per-particle APIs. Do not assume GeometryCollection AddImpulse's BoneName selects a single fragment. Generation/revision checks reject stale commands after F6, owner deletion and reuse.
- Record the owner's impact-damage policy before implementing collision-driven fracture. Independent of that decision, direct force, contact wake, support-loss wake and selected-piece manipulation can be completed. Full player abilities and structural collapse remain outside scope.

## Acceptance and handoff

First hit, thin-piece hit, settle, second impulse, grab/release, high-speed throw, moving/deleted support, external fracture, owner deletion and F6 all preserve identities and valid physical states. No floating shell, stale velocity or permanent frozen pile. Reuse projectile contract checks. Compare one-column and 4/16-column workload costs against DS-02; report any additional cost of the stronger lifecycle honestly.

Deliver the committed implementation, reusable interaction fixtures, `Docs/DestructionScaling01DS03.md`, source/DLL-bound Saved evidence and one primary independent technical review with relevant visual/play evidence. Keep unmodified specimens and owner assets intact; document the exact rollout boundary. Stop before DS-04.

New chat opener: "Start MSQ-163. Read Docs/Tasks/DestructionScaling01-DS03.md and the indicated program/predecessor sections. Execute only this task; do not start successors."
