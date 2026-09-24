# Navigation and movement source map

Current local navigator is scheduled for removal by
[UG-00](../Tasks/UtilityGOAP01/UG-00.md); encounter navigation is
[UG-02](../Tasks/UtilityGOAP01/UG-02.md). Those prepared tasks are not dispatched by
this map. Preserve canonical GASPALS/CMC and justified geometry primitives.

| Responsibility | Entry |
| --- | --- |
| Ground/segment probes, planning and path progress | [EnemyCombatNavigation.cpp](../../Source/MeridianSquad/EnemyCombatNavigation.cpp) |
| Path state and tuning | [EnemyCombatComponent.h](../../Source/MeridianSquad/EnemyCombatComponent.h) |
| Actual source movement commands | [GASPALSLocomotionFixture.cpp](../../Source/MeridianSquad/GASPALSLocomotionFixture.cpp) (`ApplySourceCommands`) |
| Stance and cover geometry | [GASPALSLocomotionCover.cpp](../../Source/MeridianSquad/GASPALSLocomotionCover.cpp) |
| Move/action ownership | [CombatAIAction.h](../../Source/MeridianSquad/CombatAIAction.h) |

Inspect `GroundPoint`, `WalkSegment`, `PlanPath`, `ContinuePath` or `FollowPath` for
the affected path; read adjacent helpers only when necessary. Proposed and achieved
stance geometry differ and must remain truthful. Source CMC owns locomotion;
custom enemy balance/recovery steps are inactive. No selectable legacy-navigation
fallback belongs in the approved replacement.

Verification route: [current correction](../GASPALSAIFix01.md) for movement before
shots, moving fire/reload, achieved anatomy and clean reset. The historical
[navigation check](../../Scripts/CombatAI01/CAI02Navigation/check.py) is candidate
specific; reuse only applicable criteria, not its obsolete movement assumptions.
Movement feel and source equivalence remain owner judgements. Open [AI](AI.md)
for policy ownership or [Animation](Animation.md) for physical authority transitions.
