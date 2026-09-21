# Rifle fall and lethal impact accents

Date: 2026-09-22. Direct outside-task follow-up to the current MSQ-98 enemy
baseline under the [owner instruction](Approvals/GASPEnemyImpactBoost01-OwnerScope01.json).
No new task, Multica run or independent review was dispatched.

The rifle now defaults to `FallImpulseMultiplier = 1.5` and
`DeathImpulseMultiplier = 2.0`. Each projectile captures these settings at launch.
Ordinary hits, damage, recoverable stepping and corpse hits retain their existing
behavior. Both multipliers are bounded to 1-2 and act on the existing mass-limited
base impulse; direct legacy probe calls retain multiplier 1 by default.

A newly lethal hit receives twice its ordinary impulse once. Death takes
precedence over the fall accent for the same shot. A living hit retains its
ordinary impulse and remembers an additional half impulse for at most 0.5 game
seconds. If the enemy enters a committed fall within that window, it applies
the extra impulse once in the bullet direction, at the original body-local
contact transformed to the body's current position. Recoverable leaning and
steps do not consume or apply the bonus. A new hit replaces the pending contact;
fall, death, reset and external pushes discard it. Hits on an already falling
or down enemy do not arm another fall accent. A subsequent separate lethal shot
can still receive its death multiplier.

The recent-hit window is a bounded attribution heuristic, not a counterfactual
physics simulation proving which bullet caused a delayed collapse. Contact
diagnostics record the lethal multiplier and any separately applied fall bonus.

UE 5.8.1 Development Editor build passes (21 actions, exit code 0). Per owner
scope, no shots, gameplay probes or motion tests were run. Build and editor logs
and current preservation hashes are under
`Saved/CombatSlice01/GASPEnemyFoundation01/ImpactBoost01/`.
Historical candidate manifests and passing motion evidence remain unchanged;
they do not verify this new tuning. Final shot/motion evaluation is the owner's.
