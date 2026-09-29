# MeridianSquad current project state

Updated 2026-09-29. [Zero point](CleanupBaseline01.md); lobby accepted.
Rules and policy routes: [AGENTS](../AGENTS.md).

## Active direction

- **Workflow:** [DirectWorkflow01](Tasks/DirectWorkflow01.md): Codex works directly;
  owner final testing/acceptance. Multica is an optional board only. Old worker,
  dispatch, reviewer and runtime context requirements are retired project-wide.
- **Grenade:** [direct G-key prototype](GrenadePrototype01.md), NGD sphere.
- **Destruction:** [MSQ-171 rollback](LobbyRollback01.md) restored the lobby under the
  [owner decision](Approvals/LobbyRollback01-OwnerScope01.json), with
  [owner acceptance](Approvals/LobbyRollback01-OwnerAcceptance01.json). Baseline:
  [MSQ-152 Build02](LobbyPlaytestFix01.md): 14 ready-made library specimens,
  working rifle integration and F6. Subsequent custom destruction columns,
  runtime code and active custom assets removed; original static architecture restored.
  Owner edits, Git history and evidence retained; old backups purged.
  MSQ-160, MSQ-162..168 and MSQ-170 are superseded by rollback; no further
  custom-column correction/scaling execution. MSQ-161 remains stopped.
  [NGD migration](NextGenDestruction01.md) remains; custom ED stays retired.
  MSQ-150/151 are
  [cancelled for now](Approvals/NextGenDestruction01-Cancellation01.json);
  owner play/design acceptance is separate.
  Initial [lobby scope](Approvals/NextGenDestruction01-LobbyScope01.json): place ready-made
  demo breakables in the retained lobby only; preserve existing architecture/edits.
- **Utility AI + GOAP**, [MSQ-122 program](Tasks/UtilityGOAP01.md) and
  [replacement plan](Tasks/UtilityGOAP01Plan.md), under the
  [owner decision](Approvals/UtilityGOAP01-TaskCreation01.json).
  MSQ-123..137 are prepared only, unassigned with zero runs at this snapshot.
  MSQ-105..117 are cancelled as superseded; MSQ-101 preserves their history.
  UG-00 removes obsolete active policy/custom navigation, retaining justified
  primitives; UG-01 immediately restores basic combat. No selectable legacy fallback.
- Current source baseline: canonical **GASPALS/CharacterMovement**, direct
  [AI correction Build07](GASPALSAIFix01.md), commit `7ba267f`.
  [Primary review](GASPALSAIFix01Review.md) closes the audited runtime defects.
  Source locomotion and moving fire/reload remain; custom enemy balance/recovery
  steps are inactive. Technical delivery does not grant owner motion/play acceptance.
- With the replacement direction established, the AI lane is MSQ-123..125, MSQ-71
  survival, MSQ-126 cover and one-enemy MSQ-72. MSQ-131's planned MSQ-150 contract
  is unavailable while MSQ-150 is cancelled. MSQ-127 later adds 2/3 enemies.
  MSQ-73 dismemberment is deferred; MSQ-99/100 and other mechanics remain separate.
  [Priority authority](Approvals/CombatPriorities01-OwnerScope01.json).

## Retained and paused scope

- Player: purchased arms/rifle, [PurchasedArms06 presentation](PurchasedArms06.md).
  [CombatSlice01](Tasks/CombatSlice01Plan.md) indexes gameplay tasks. Physics
  MSQ-92 is delivered; MSQ-93..96 remain undispatched. Read the
  [gameplay policy](AgentPolicies/Gameplay.md) for relevant baseline/slowdown rules.
- Original protagonist production/successors are paused; preserve all sources and
  experiments. [Direction](Approvals/PurchasedArms01-OwnerScope01.json).
- Original lobby architecture stays deferred under the [owner closure](Approvals/LobbyDeferred01-OwnerClosure01.json).
  Retained map: `/Game/Maps/L_OpeningLobby_PainterStone01`; preserve owner edits.
  New environment production still requires named art/drawing approval.
  [Preservation details](OpeningLobbyDeferred01.md).

## Lookup and maintenance

Search `Docs/Tasks/` by ID/name; read scoped decisions/evidence. Use the
[execution policy](AgentPolicies/Execution.md), [history index](ContextHistory.md)
and [source routes](Subsystems/README.md) only as needed. Keep current scope here
and task progress/delivery in task notes.
