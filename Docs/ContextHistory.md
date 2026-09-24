# Context history lookup

Use only when a current task/decision does not supply needed historical context.
The [frozen 2026-09-24 ProjectState](Archive/ProjectState/2026-09-24-BeforeContextBudget01.md)
preserves the entire previous 1,032-line snapshot byte-for-byte. Its relative links
resolve from its original directory, `Docs/`, not the archive directory. Old
"current", "latest" and dispatch statements are historical, not authorization.
Search headings or task IDs, then read a bounded section; never load it at startup.

| Needed history | Prefer the focused entry |
| --- | --- |
| Current AI replacement / cancelled old backlog | [UtilityGOAP01](Tasks/UtilityGOAP01.md) |
| GASPALS source migration / runtime correction | [migration](Tasks/GASPALSLocomotion01.md), [correction](GASPALSAIFix01.md) |
| Earlier tactical AI | [CombatAI01](Tasks/CombatAI01.md) |
| Combat progression / projectile foundation | [CombatSlice01](Tasks/CombatSlice01Plan.md) |
| Physical stance / balance / recovery | [PhysicsControlRefinement01](Tasks/PhysicsControlRefinement01Plan.md) |
| Earlier GASP enemy foundation | [GASPEnemyFoundation01](Tasks/GASPEnemyFoundation01.md) |
| Purchased arms and rifle | [PurchasedArms01](Tasks/PurchasedArms01.md), [PurchasedArms06](Tasks/PurchasedArms06.md) |
| Original protagonist | [PlayerCharacter01 plan](Tasks/PlayerCharacter01Plan.md); missing older index/pipeline paths are recorded in [Art](AgentPolicies/Art.md) |
| Deferred lobby / retained assets | [OpeningLobbyDeferred01](OpeningLobbyDeferred01.md) |
| Tooling history | [AgentDevelopment](AgentDevelopment.md) (search the relevant section) |

The [frozen root instructions](Archive/AgentInstructions/2026-09-24-before-compaction.md)
preserve the previous AGENTS bytes; its links resolve from the repository root.
Earlier snapshots remain in [the instruction archive](Archive/AgentInstructions/README.md).
Fingerprints and original byte counts are recorded in
[ContextBudget.json](../Tools/ContextBudget.json); `Scripts/check_context_budget.ps1`
verifies them. Neither snapshot is an additional active instruction source.
