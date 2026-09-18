# ForcePush01: directional force push

Multica issue: **MSQ-76**.
Stage 9 of [CombatSlice01](CombatSlice01Plan.md).
Predecessor: [TimeSlow01](TimeSlow01.md).

## Scope

Implement a readable directional push for eligible enemies and simulated objects.
Record prototype controls, range/cone, visibility checks, strength/mass response,
cost/recovery, damage policy and exclusions. Use the established input table and
feedback conventions. Immovable architecture and the player remain excluded.

State whether activation can occur during rifle fire/reload and whether it
interrupts those actions. Rejected requests consume no resources and must not
change rifle locks, interrupt a valid reload transfer or trigger partial effects.

Living enemies need a stated stagger/knockdown/recovery behavior distinct from dead
body physics. Apply collision and any impact damage through the shared damage path,
with one event per stated interaction. Preserve cover/obstruction and support the
declared time-slow behavior; no unconditional impulses through walls.

## Acceptance

- Eligible visible targets receive the specified push; occluded, out-of-range,
  excluded and overly heavy targets follow the documented rule with useful feedback.
- Enemies recover correctly or die through the normal damage/death path. No active
  shooter remains in a state incompatible with its knocked-down presentation.
- Props and body parts collide stably; the push cannot multiply one collision into
  unbounded damage, actor spawning or extreme velocity.
- Check normal/slow time and death/restart cleanup for directly coupled states.
  Repeated input respects the chosen recovery/cost and input ownership.
- Check accepted/rejected activation during fire and reload under the declared
  compatibility policy; weapon state and reload notifies recover correctly.

No broader physics ability framework or environment remodeling. Follow the parent
plan; deliver `Docs/ForcePush01.md`, explicit limits and focused gameplay evidence.
