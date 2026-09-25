# EnvironmentDestruction01: Next Gen toolkit gameplay integration

Multica issue: **MSQ-74**. Coordination parent under [CombatSlice01](CombatSlice01Plan.md).
Updated 2026-09-25 under the [owner task rewrite](../Approvals/NextGenDestruction01-TaskRewrite01.json).
Follow the [current plan and child mapping](EnvironmentDestruction01Plan.md).
Prepared scope only; no implementation is dispatched by this rewrite.

## Baseline and scope

The [Next Gen Destruction Toolkit migration](../NextGenDestruction01.md) is accepted.
Vendor demo acceptance proves package migration, not integration with our rifle,
cover, AI, support or lobby. The custom ED laboratory implementation is retired.
MSQ-140/141 retain historical done status; MSQ-142..147 are superseded/cancelled.

Use the imported toolkit for a bounded playable destruction fixture, initially one
identified existing vendor object/material in a task-owned test map or derivative.
Connect the current MeridianSquad rifle/projectile damage path to real breakage.
Make visible damage, weapon blocking and Pawn collision agree. Establish a usable
material response, bounded physical debris, reset, and change/support notifications;
then measure several objects and canonical slowdown. Reuse working vendor behavior
and extend only documented gaps. Do not rebuild the retired custom fracture system.

The three sequential children are NGD-01 (weapon/first object), NGD-02 (playable
specimen/debris contract), and NGD-03 (load/slowdown/handoff). Their exact Multica IDs,
prerequisites and acceptance are in the plan. MSQ-74 remains unassigned coordination.
MSQ-68 and MSQ-82 remain the established combat prerequisites; the migrated package
and current rifle baseline must be verified before implementation.

## Acceptance and consumers

- Actual MeridianSquad shots cause reproducible damage/break states. Retained solid
  geometry blocks shots; declared openings permit later shots whose sweep fits.
  Record the supported localization/granularity instead of promising runtime cutting.
- Significant visible fragments collide and settle; cosmetic chips are identified.
  Counts, lifetime, cleanup and reset are bounded without stale blockers/support.
- Stable object/fragment identity, affected bounds, collision/cover revision,
  support invalidation and reset generation form a documented consumer contract.
- Identified small-population runs cover intact, breaking and settled states,
  repeated resets and normal/slowdown/restoration behavior at stated settings.
- Handoff identifies the exact fixture, controls, candidate, limits, review closure
  and pending owner visual/play judgement. Migration evidence is not runtime proof.

MSQ-131 consumes NGD-02's usable specimen and notifications after new AI cover and
one-enemy MSQ-72; it owns invalidating plans and requerying routes/cover.
MSQ-96 independently owns support/contact capability on fixtures. NGD-02 documents
compatibility with that contract when available without depending on its delivery.
MSQ-78 consumes actual toolkit debris plus movement/support handoffs and proves
player/enemy crossing. These consumers do not gate destruction parent completion.

No lobby placement, architecture changes, structural collapse, renewed layered-column
production, whole-level destruction, new abilities or new art is granted. Preserve
vendor originals, original lobby/shared assets and owner edits. Use the plan's
review/evidence rules; earlier ED task-specific waivers do not transfer.
