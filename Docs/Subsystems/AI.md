# AI source map

Baseline: direct GASPALS correction Build07. **Utility AI + GOAP is approved direction,
not yet implemented by this map.** [Program](../Tasks/UtilityGOAP01.md),
[source disposition](../Design/UtilityGOAP01SourceInventory.md). Read the selected
child's acceptance and current owner decision before editing old policy code.

| Responsibility | Entry |
| --- | --- |
| Current component API, decision inputs, action state | [EnemyCombatComponent.h](../../Source/MeridianSquad/EnemyCombatComponent.h) |
| Lifecycle, enable/reset/status | [EnemyCombatComponent.cpp](../../Source/MeridianSquad/EnemyCombatComponent.cpp) |
| Current policy and combat tick | [EnemyCombatPolicy.cpp](../../Source/MeridianSquad/EnemyCombatPolicy.cpp) |
| Sensory evidence ingestion | [EnemyCombatSenses.cpp](../../Source/MeridianSquad/EnemyCombatSenses.cpp), [CombatAISenses.h](../../Source/MeridianSquad/CombatAISenses.h) |
| Action contracts | [CombatAIAction.h](../../Source/MeridianSquad/CombatAIAction.h) |
| Cover/observation/tactics | [EnemyCombatCover.cpp](../../Source/MeridianSquad/EnemyCombatCover.cpp), [EnemyCombatObservation.cpp](../../Source/MeridianSquad/EnemyCombatObservation.cpp), [CombatAITactics.h](../../Source/MeridianSquad/CombatAITactics.h) |

Boundaries: decisions command the fixture; canonical GASPALS/CMC owns movement.
Current movement must not wait for the first shot or stop merely for fire/reload.
Every launch still needs actual sight/aim/muzzle safety. Knowledge must retain
provenance and expiry; unimplemented player health stays unknown.

Verification: select the affected criterion from [GASPALSAIFix01](../GASPALSAIFix01.md)
and its [primary review](../GASPALSAIFix01Review.md). Existing analysis entry:
[analyze.py](../../Scripts/CombatAI01/GASPALSFix01/analyze.py). Older scripts under
`Scripts/CombatAI01/` validate their named candidate; inspect applicability first.
Technical verification does not approve owner combat feel. Open [Navigation](Navigation.md)
or [Weapons](Weapons.md) only when the change crosses those contracts.
