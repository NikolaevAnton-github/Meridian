# MeridianSquad current project state

Updated 2026-09-25. Verify live Multica/editor state when needed.
This snapshot grants no task execution or design approval. Read the relevant task,
not every linked document. Durable rules and policy routes: [AGENTS](../AGENTS.md).

## Active direction

- **Destruction:** [Next Gen toolkit migration](NextGenDestruction01.md) is accepted;
  the custom ED implementation is retired. [MSQ-74's new plan](Tasks/EnvironmentDestruction01Plan.md)
  retains the integration. [MSQ-156](ReinforcedColumn02.md) delivers revised column
  spalling. Independent review waived for this task; owner visual/gameplay check
  pending. Agents ran source/build/asset checks only.
  [MSQ-152 Build02](LobbyPlaytestFix01.md): fire fixed; 14 demo specimens with F6;
  technically complete, owner review waiver. MSQ-150/151 are
  [cancelled for now](Approvals/NextGenDestruction01-Cancellation01.json);
  owner play/design acceptance is separate.
  MSQ-140/141 stay historical done; MSQ-142..147 are cancelled as superseded.
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

Search `Docs/Tasks/` by task ID/name; read its scoped decisions and evidence as needed.
For tooling, use the [execution policy](AgentPolicies/Execution.md); historical
integration success never proves a live connection. For old decisions missing from
the task, search the [history index](ContextHistory.md) and read only the matching
section. Never load the history snapshot as routine startup context.

Keep this file to current scope and blockers. Delivery details belong in task
handoffs. The context budget and preservation checks are described in
[ContextBudget02](Tasks/ContextBudget02.md); source routes are indexed in
[Subsystems](Subsystems/README.md), loaded only for the relevant task.
