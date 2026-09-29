# MeridianSquad agent instructions

## Start small

Read [ProjectState](Docs/ProjectState.md) once before starting work.
Then open the relevant task and only the decisions/sections needed for that work.
Links are navigation, not a recursive reading list. Do not reload instructions
already present in this session. Historical reports are not an execution queue;
later explicit owner instructions supersede earlier guidance within their scope.

Use bounded `rg` searches and section reads. Keep full tool results/logs in
`Saved/`; return only relevant findings. Discover tool names first, then the schema
of the selected tool, never the full catalog. Load the policies below only when
their trigger applies; do not read all policies at startup.

## Standing rules

- Russian in the owner's direct chat; English in project content, code comments,
  names, commits and internal reports.
- Existing apps/services needed for authorized work may be launched without asking
  again. Starting services or preparing tasks does not authorize their execution.
- Use the existing $200/month Codex subscription; no new paid services, purchases,
  top-ups or separately billed APIs. Existing Tripo/Meshy web allowances are scoped
  to protagonist AI3D; verify free Hunyuan terms. Local models need measured capacity.
- Total project footprint, including history/services/generated data: 250 GB maximum.
  Avoid duplicate Unreal worktrees/unbounded caches; never delete owner assets.
- Preserve owner edits, sources, accepted/rejected candidates and exact evidence.
  Never restore old worker bytes over owner edits or rebaseline immutable manifests.
  Git tracks code/config/decisions/sources; binary assets use LFS. Logs/generated data
  stay outside Git. Never expose or commit credentials.
- Codex performs tasks directly in the owner's chat. Do not dispatch Multica
  workers or create mandatory executor/reviewer workflows. Multica is optional
  task storage/a board only; no runtime, task execution or agent automation.
  [DirectWorkflow01](Docs/Approvals/DirectWorkflow01-OwnerRequest01.json) supersedes
  earlier dispatch, review-routing and live-state requirements project-wide.
- Use **max reasoning, standard speed** where settings are controllable; retain
  max when restoring settings. Do not add worker-profile checks to direct tasks.
- One writer per editor instance; one memory-heavy build/bake/render/model at a time.
  Confirm live project/editor/bridge capability before mutations.
- Run focused source/build checks appropriate to the change and report their
  limits. The owner performs final testing and acceptance. Extra reviewers are
  used only on owner request. Preserve owner design approvals and asset evidence.
- Commit checked task-scoped changes locally before final handoff,
  using an English message with the task ID; exclude unrelated owner edits.

## Load by task

| Trigger | Read |
| --- | --- |
| Implementation, optional board or editor/registry operations | [Execution](Docs/AgentPolicies/Execution.md) |
| AI, combat, movement, physics or gameplay variants | [Gameplay](Docs/AgentPolicies/Gameplay.md) |
| Environment, character, materials, visual assets or narrative | [Art](Docs/AgentPolicies/Art.md) |
| Changing instructions or context routing | [Context](Docs/AgentPolicies/Context.md) |

Keep current scope in ProjectState, task details in `Docs/Tasks/`, exact decisions
in `Docs/Approvals/`. Replace stale summaries; do not append delivery history here.
When changing these entrypoints/policies run `Scripts/check_context_budget.ps1`.
AGENTS + ProjectState have an 8 KiB combined budget; move detail to the task/policy.
Current owner instructions and project task notes define active work; board access
or a Multica task ID is never required to start, continue or deliver it.
