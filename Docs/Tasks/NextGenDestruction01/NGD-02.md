# NGD-02: Playable toolkit specimen, debris and reset contract

Multica issue: **MSQ-150**. Parent: [MSQ-74](../EnvironmentDestruction01.md).
Prepared 2026-09-25; unassigned backlog, no execution authorized.
Authority and shared rules: [toolkit integration plan](../EnvironmentDestruction01Plan.md)
and [owner task rewrite](../../Approvals/NextGenDestruction01-TaskRewrite01.json).
Prerequisite: [NGD-01](NGD-01.md). No dependency on new AI or MSQ-96 delivery.

## Work

Turn NGD-01's object into one reusable gameplay specimen with a declared material
response and supported damage states. Reuse vendor fracture/interior materials,
audio and effects where suitable; correct documented readability/behavior gaps.
A second material or the retired layered-column recipe is not an automatic gate.
New visual design still requires its own approval; identify the actual source and
bounded derivations instead of assuming a lobby asset is already selected.

Define intact/damaged/destroyed blocking and cover behavior, mass/impulse tuning,
large physical fragments versus cosmetic chips, stable settling/sleep, maximum
active/persistent counts, cleanup and encounter reset. Sleeping does not silently
remove visible gameplay collision. Keep one reproducibly movable piece; do not
freeze everything or disable collision to hide unstable piles.

Finalize the narrow change contract: object/fragment identity, changed bounds,
collision/cover revision, support invalidation before removal, and reset generation.
Declare eligible support, unstable/too-small fragments and nonblocking effects.
Check compatibility with MSQ-96's interface if delivered; otherwise document the
producer side and fixture-observed invalidation without implementing foot contacts.
Supply a bounded rubble patch and consumer example for MSQ-131 and MSQ-78.

## Acceptance

- Actual rifle hits produce the declared states and readable material interiors;
  significant visible remaining geometry/debris has truthful blocking collision.
- Large fragments collide with world/each other and settle without persistent
  overlap flicker or explosive behavior. Demonstrate awake/movable and settled states.
- Repeated damage and resets show bounded bodies/components/memory, clean listeners,
  no ghost blockers and no references surviving object replacement/reset.
- Break, collision change, cleanup and reset emit identifiable revisions/invalidation
  in time for consumers to stop using removed cover/support. Observe ordering with a
  small test consumer; real AI plans and foot-contact behavior are separate tasks.
- Handoff includes a representative rubble patch, support/collision table, limits,
  reset controls, exact fixture/candidate and reusable evidence for NGD-03/MSQ-131.

MSQ-131 owns AI invalidation/requery; MSQ-96 owns contact capability; MSQ-78 proves
ordinary player/enemy crossing. This task's fixture does not claim those results.
Follow the plan's independent review and owner visual/play gates. No lobby population.
Evidence: `Saved/NextGenDestructionIntegration01/NGD-02/<candidate>/`.
