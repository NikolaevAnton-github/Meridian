# EnvironmentDestruction01: bounded destructible objects and cover

Multica issue: **MSQ-74**.
Stage 8 of [CombatSlice01](CombatSlice01Plan.md).
Predecessor: [EnemyBodyDamage01](EnemyBodyDamage01.md).

## Scope

Select a small explicit set of existing reusable nonstructural objects, initially
two or three specimens, for intact/damaged/destroyed states. Use removable gameplay
instances and preserved editable sources. State which objects are cover and which
are cosmetic debris. Existing columns, floor, ceiling and owner-authored architectural
assets remain structurally intact; deferred glass refinement is not reopened.

Connect rifle damage to visible breaks, suitable sound/particles and bounded
physics. Document mass, damage threshold, fragmentation and cleanup choices as
tuning. Adjust hit obstruction, player collision and enemy navigation/cover state
when a selected object breaks. Preserve the original map/assets for reset.

The owner subsequently requests movement over debris; see
[PhysicsControlRefinement01 / MSQ-90](PhysicsControlRefinement01Plan.md). Provide
one bounded representative rubble patch from these specimens for later traversal
in MSQ-78. Identify solid static support, eligible movable support, unstable or
too-small fragments, and nonblocking cosmetic debris. Document support invalidation
when pieces fracture, are replaced or are cleaned up, consuming the applicable
MSQ-96 contact contract when available. Do not silently disable all debris collision
or permanently freeze it to make traversal pass. Actual enemy movement remains
MSQ-70's responsibility; integrated player/enemy crossing remains MSQ-78's.

## Acceptance

- Each identified specimen reaches its stated damage states through actual rifle
  hits. Visual destruction and collision/hit blocking change together.
- An intact cover object protects the target; its declared destroyed state allows
  the expected shot or traversal. Enemy cover choices do not retain a destroyed
  position as valid indefinitely.
- Debris count, lifetime and collision are bounded; no explosive physics, permanent
  blocked route or sustained growth after encounter resets.
- Supply an identified reproducible traversable rubble patch and its support/
  cleanup contract for MSQ-78, including a physics-enabled piece that can move.
  This fixture handoff does not itself prove player or enemy traversal.
- Compare intact/damaged views and record scoped CPU/GPU/physics observations at
  stated settings. Technical results do not accept new art or extensive full-level
  destruction. Missing suitable sources require a bounded asset decision.

No whole-building fracture, structural redesign or new environment modeling without
the required concept/dimension approvals. Follow the parent plan; deliver
`Docs/EnvironmentDestruction01.md` and scoped source/runtime evidence.
