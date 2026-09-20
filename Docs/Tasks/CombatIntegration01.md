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
with its later [relative slowdown override](../Approvals/PhysicsControlVariants01-OwnerScope01.json):
player movement/firing slow less than the world during slowdown, all bullets
follow world time, and eligible own-projectile contact can injure the player.
Full stop remains in its later ability scope. Check restoration/cleanup after
the implemented time states, death and restart.

The owner's later debris-traversal requirement is assigned here by
[PhysicsControlRefinement01 / MSQ-90](PhysicsControlRefinement01Plan.md).
Consume MSQ-91 through MSQ-96 stance/support handoffs, MSQ-70 movement and MSQ-74
representative destruction output. The six new tasks can prove reactive support
capabilities on fixtures; this task retains the open real-traversal gate. Preserve
the existing stage/predecessor, check these additional handoffs before the coupled
acceptance, and do not dispatch any prerequisite from this planning amendment.

## Acceptance

- One short fight supports rifle fire and each ability, has a clear completion,
  and can be lost/restarted without stale enemies, damage, time state or constraints.
- Cover and damage semantics agree across rifle, enemy, body and physics paths;
  controls do not conflict and feedback is readable at normal gameplay distance.
- Both the player and the adopted enemy enter, cross and leave one declared
  traversable patch of actual MSQ-74 debris through ordinary movement. For the
  enemy, show credible foot contact/clearance and one affected hit-recovery return
  to locomotion. Include a piece that actually shifts or loses support and safe
  behavior when that contact fails. State the supported envelope and the handling
  of impassable rubble. Check newly coupled cleanup/reset; reuse earlier evidence.
  Recovery steps in place, teleportation, cosmetic/frozen chunks, disabling
  collision or routing around the whole patch do not satisfy this crossing row.
- Bounded captures demonstrate the selected cross-system checks. Measure introduced
  frame/physics costs at stated resolution/settings and actor counts; report limits
  honestly rather than hiding them through changed scene quality.
- An independent reviewer inspects actual combat footage and supporting runtime
  evidence. Correct reproducible blockers before controller closure. Owner combat
  feel/visual acceptance remains distinct from technical and independent review.

Deliver `Docs/CombatIntegration01.md`, an identified candidate and owner play route
under the parent plan's preservation and closure rules.
