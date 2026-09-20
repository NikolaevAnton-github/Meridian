# PhysicsControlDebrisSupport01: moving and disappearing debris support

Multica issue: **MSQ-96**.
Stage 7 of [PhysicsControlRefinement01](PhysicsControlRefinement01Plan.md).
Predecessor: [PhysicsControlUnevenGround01](PhysicsControlUnevenGround01.md).
Planning only; follow the parent authorization, preservation and verification rules.

## Scope

Extend foot contact and recovery placement to eligible physics-driven support.
Track support identity and relative contact position/orientation so feet respond
to translation and rotation while contact remains physically feasible. Account
for support velocity and stability; reject loose, small or tipping pieces that
cannot carry a useful contact. Document size, motion/stability and mass-related
eligibility choices without treating a mass threshold alone as proof of stability.

Support may shift, tilt, roll, break or disappear during landing or standing.
Revalidate contact and release safely into a remaining corrective step or physical
fall when it is lost. Do not weld feet indefinitely to a departing chunk, freeze
chunks to pass, or keep stale references after fracture/cleanup/reset. Retain
bounded two-way physics rather than using the support as an invisible kinematic
platform. Use a small removable dynamic fixture set; MSQ-74 owns actual destruction.

## Acceptance

- Show a usable support translating and rotating during real contact, with
  support-relative foot motion, bounded slip/penetration and credible settling.
  Static or permanently frozen rubble alone cannot pass this task.
- Show an unstable or insufficient piece being rejected and one support change
  that exceeds recovery capacity. The body releases/falls instead of following an
  impossible anchor, standing in air or injecting unbounded physics energy.
- Exercise support invalidation by replacement/removal as a fracture/cleanup
  fixture, including during landing. Check affected fall/get-up, relative slowdown,
  and reset/recreation so contact references and constraints do not survive their
  objects. Record scoped physics cost, piece counts and observed motion limits.
- Deliver the support eligibility/invalidation contract for MSQ-74 and MSQ-78.
  Fixture completion proves contact capability only. Real movement across produced
  rubble remains an explicit open acceptance row in MSQ-78, requiring MSQ-70
  movement and MSQ-74 destruction; do not claim that one/two steps satisfy it.

Deliver `Docs/PhysicsControlDebrisSupport01.md` and focused evidence under
`Saved/CombatSlice01/PhysicsControlDebrisSupport01/`. No fracture pipeline, AI or
navigation implementation, unrestricted climbing, new art or successor dispatch.
