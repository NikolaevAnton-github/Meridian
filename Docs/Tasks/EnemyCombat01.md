# EnemyCombat01: one functioning combat opponent

Multica issue: **MSQ-70**.
Stage 4 of [CombatSlice01](CombatSlice01Plan.md).
Predecessor: [EnemyPrototype01](EnemyPrototype01.md), with its asset contract.

## Scope

Implement one enemy that detects the player, pursues through reachable space,
stops/aims and fires, responds to incoming damage and dies. Use configurable
perception/range/timing and a small readable state model. Loss of sight must have
a stated finite search/return policy; no perfect tracking through walls.

Enemy fire uses the established hit/damage path and real obstruction checks.
Supply a damage event suitable for the next player-health task; during this stage
verify it on an instrumented receiver. Player death is not claimed yet. Establish
enemy cadence and ammunition/reload policy without inventing an inventory system.

Use existing lobby geometry and bounded navigation support. Do not move columns,
alter passages or add rooms to rescue pathfinding. Keep spawn and reset repeatable.
Dead actors stop AI, shots, timers and movement before death physics/presentation.

## Acceptance

- Demonstrate acquisition, reachable movement, obstruction/lost sight, attack,
  hit reaction and death on the identified enemy prototype.
- Enemy shots cannot pass through retained cover; verify damage events and timing
  separately from muzzle/sound presentation. No fire from dead actors or a stale
  target after reset.
- Unreachable destinations fail cleanly instead of oscillating or accumulating
  tasks. A bounded restart restores one opponent with no duplicate controllers.
- Inspect actual gameplay views for aim, movement and hit/death readability;
  technical AI checks do not accept final enemy art.

No squad tactics, enemy variants, progression or a full behavior framework.
Follow the parent plan; deliver `Docs/EnemyCombat01.md` and focused evidence.
