# NGD-02: Lobby demo props, debris and reset contract

Multica issue: **MSQ-150**. Parent: [MSQ-74](../EnvironmentDestruction01.md).
Updated 2026-09-25; unassigned backlog, no implementation dispatched.
Authority and shared rules: [toolkit integration plan](../EnvironmentDestruction01Plan.md)
and the later [owner lobby scope](../../Approvals/NextGenDestruction01-LobbyScope01.json).
Prerequisite: [NGD-01](NGD-01.md). No dependency on new AI or MSQ-96 delivery.

## Work

Stabilize NGD-01's placed demo props in `/Game/Maps/L_OpeningLobby_PainterStone01`,
using one representative source for the complete gameplay/support contract and
checking changed behavior on the other placed types. Declare material responses
and supported damage states. Reuse vendor fracture/interior materials,
audio and effects where suitable; correct documented readability/behavior gaps.
A second material or the retired layered-column recipe is not an automatic gate.
New visual design still requires its own approval; identify the actual source and
bounded derivations. Existing demo props are the selected initial route; existing
lobby architecture is not thereby selected for conversion to destructible assets.

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
Supply a bounded rubble patch from the placed props in this lobby and a consumer
example for MSQ-131 and MSQ-78. Keep current owner architecture and circulation.

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
  reset controls, exact lobby actor set/candidate and evidence for NGD-03/MSQ-131.

MSQ-131 owns AI invalidation/requery; MSQ-96 owns contact capability; MSQ-78 proves
ordinary player/enemy crossing. This task's fixture does not claim those results.
Follow the plan's independent review and owner visual/play gates. Work on the
initial lobby placement; do not expand dressing or redesign the architecture.
Evidence: `Saved/NextGenDestructionIntegration01/NGD-02/<candidate>/`.
