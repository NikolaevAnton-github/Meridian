# PlayerSurvival01: health, death and combat restart

Multica issue: **MSQ-71**.
Stage 5 of [CombatSlice01](CombatSlice01Plan.md).
Predecessor: [EnemyCombat01](EnemyCombat01.md).

## Scope

Connect enemy hits and eligible own-bullet hits to player health with configurable initial/maximum values,
readable incoming-damage feedback and a minimal health display. Keep the stable
first-person camera usable; no unrequested camera-shake system or auto-regeneration.
At zero health stop normal movement/actions and provide a clear restart action.

The [owner's fixed projectile policy](../Approvals/CombatFoundation01-OwnerScope01.json)
permits self-injury. Consume the MSQ-68 collision-time damage event without a
permanent shooter immunity filter; preserve its bounded launch-clearance rule.

Restart the local encounter baseline: one player, one enemy, original spawn,
health, magazine/reserve, AI state and transient effects. Define handling of death
while firing/reloading and ensure pending notifies cannot mutate the new life.
Do not treat the supplied syringe gesture as a healing mechanic.

## Acceptance

- An unobstructed enemy hit changes health once; cover blocks the hit. Health
  clamps at valid values, and death occurs once without post-death weapon damage.
- An eligible player-fired bullet damages its shooter once on later contact;
  launching a shot does not itself cause a spurious self-hit.
- Death during a shot/reload and restart do not leak controls, timers, targets or
  ammunition transfers. The camera and purchased shadowless arms return correctly.
- A repeatable fight/death/restart cycle restores exactly one player and enemy
  with the specified health/ammunition; counts do not grow after repeated resets.
- Display, controls and state agree in actual play and after saved-package reload.

No healing economy, armor system, full save game or game-over cinematic. Follow
the parent plan; deliver `Docs/PlayerSurvival01.md` and focused runtime evidence.
