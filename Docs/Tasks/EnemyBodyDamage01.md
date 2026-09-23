# EnemyBodyDamage01: regional damage and a dismemberment sample

Multica issue: **MSQ-73**.
Deferred, low-priority stage 16 of [CombatSlice01](CombatSlice01Plan.md).
Predecessor: [LobbyEncounter01](LobbyEncounter01.md).
Additional gate: EnemyPrototype01's verified damage-ready editable asset contract.

The [owner priority decision](../Approvals/CombatPriorities01-OwnerScope01.json)
places this expansion after good AI, shooting and environmental destruction.
The former stage 7 is superseded. MSQ-72 remains a technical prerequisite, not
an instruction to dispatch immediately after it. This task does not block MSQ-74,
the initial MSQ-78 integration or MSQ-81 review. It remains prepared backlog;
no implementation or asset production is authorized by the priority change.

## Scope

Implement a representative body-damage subset on the selected prototype: explicit
head/torso/limb regions and at least one supported limb-separation case. Define
damage thresholds, wound presentation, collision, detached-part lifetime and the
relationship between regional damage and enemy death. Treat values and severity
as prototype tuning; do not promise full anatomical simulation or all limb variants.

Keep a single damage application path; visual wounds, detached parts, living AI
and death physics must agree. Use suitable existing editable geometry, including
bounded segmentation/capping defined in the selected asset contract; the source
need not already be severable or supplied as a native DCC project. If closed
cut surfaces or the required regions cannot be produced within an approved source
scope, surface the exact missing asset decision before production. This task does
not authorize original protagonist work or an unapproved new enemy model.

## Acceptance

- The identified region receives the expected damage and reaction; the selected
  severing case has coherent surfaces, no stretched skin and stable detached parts.
- Repeated hits on a removed region cannot duplicate separation, damage events or
  rewards. A fatal result disables enemy combat immediately.
- Detached collision cannot trap the player; debris/effects are bounded and reset
  removes them. Living/dead states remain correct after subsequent hits.
- When implemented after the priority slice, check separation against the actual
  delivered AI, weapon and ability interfaces, including one affected interruption
  and reset. This task owns those new coupled checks; reuse prior passing evidence.
- Independent visual review inspects actual close and gameplay-distance views;
  record prototype limitations separately from technical results and owner taste.

Follow the parent plan. Deliver `Docs/EnemyBodyDamage01.md`, exact supported regions,
source changes and focused runtime/visual evidence. Do not close an asset-blocked
implementation as complete merely because a contract or stand-in exists.
