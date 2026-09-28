# MSQ-163 / DS-03 handoff

Implemented in the [direct batch](DestructionScaling01Batch01.md), under the owner's [scoped exception](Approvals/DestructionScaling01-DirectBatch01.json).

Lobby/stacking fragments use `DestructionFragmentWorld`: attached geometry remains with cladding; detached bodies transition among awake, asleep and temporarily held states. Supported low-speed bodies can enter ordinary reversible sleep. Contact, a direct impulse, support movement/removal and explicit manipulation wake the selected bodies. Release supplies linear/angular velocity and restores simulation.

The shared path bypasses legacy irreversible retention, age expiry and shard eviction. No gameplay fragment count cap was introduced. Both ceramic bodies and exact GC leaves remain collidable and targetable. GC control uses validated per-particle solver operations, not `AddImpulse` BoneName assumptions. Protected core/upper pieces cannot enter the released-fragment adapter. Concrete collision-driven damage remains disabled.

Focused evidence covers persistent lifetime, support loss, selected manipulation, thin-body CCD and F6 cancellation. Final results and source/DLL identity are in the batch handoff. Legacy non-stacking experiment behaviour remains outside this rollout; the central stacking demo shares the new lifecycle.
