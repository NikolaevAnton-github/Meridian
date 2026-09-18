# CombatIntegration01: integrated combat slice and feel

Multica issue: **MSQ-78**.
Stage 12 of [CombatSlice01](CombatSlice01Plan.md).
Predecessor: [Telekinesis01](Telekinesis01.md), using the completed combat/damage
handoffs from stages 1-10.

## Scope

Reuse the bounded lobby encounter to make rifle impact, enemy response, player
survival, body damage, selected destruction and three abilities work coherently.
Consolidate prototype controls/HUD and tune feedback, damage, pacing and resource
limits. Record all tuning deltas. This task does not add weapons, enemy classes,
more abilities or new architecture.

Select tests by newly coupled risk: destruction invalidating cover, pushed or
thrown objects damaging enemies, body separation during an ability, slowdown
during reload/impacts, and death/restart with active abilities/held objects. Reuse
earlier evidence for unchanged components; do not repeat the full feature matrix.

Include the [fixed time/self-hit policy](../Approvals/CombatFoundation01-OwnerScope01.json)
in newly coupled checks: normal player movement during world slowdown/stop,
all bullets following world time, self-injury on eligible contact, and reliable
restoration/cleanup after stop, death and restart.

## Acceptance

- One short fight supports rifle fire and each ability, has a clear completion,
  and can be lost/restarted without stale enemies, damage, time state or constraints.
- Cover and damage semantics agree across rifle, enemy, body and physics paths;
  controls do not conflict and feedback is readable at normal gameplay distance.
- Bounded captures demonstrate the selected cross-system checks. Measure introduced
  frame/physics costs at stated resolution/settings and actor counts; report limits
  honestly rather than hiding them through changed scene quality.
- An independent reviewer inspects actual combat footage and supporting runtime
  evidence. Correct reproducible blockers before controller closure. Owner combat
  feel/visual acceptance remains distinct from technical and independent review.

Deliver `Docs/CombatIntegration01.md`, an identified candidate and owner play route
under the parent plan's preservation and closure rules.
