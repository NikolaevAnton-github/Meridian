# MeridianSquad agent instructions

## Start small

Read [ProjectState](Docs/ProjectState.md) once before choosing or dispatching work.
Then open the relevant task and only the decisions/sections needed for that work.
Links are navigation, not a recursive reading list. Do not reload instructions
already present in this session. Historical reports are not an execution queue;
later explicit owner instructions supersede earlier guidance within their scope.

Use bounded `rg` searches and section reads. Keep full tool results/logs in
`Saved/`; return only relevant findings. Discover tool names first, then the schema
of the selected tool, never the full catalog. Delegate with a short task brief and
paths rather than full conversation history. Load the policies below only when
their trigger applies; do not read all policies at startup.

## Standing rules

- Russian in the owner's direct chat; English in project content, code comments,
  names, commits and internal agent/Multica reports.
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
- Multica is the default implementation route, with one production worker. Direct
  chat handles administration and trivial local corrections without a task-sized
  workflow. No competing dispatcher/database. Stay active through verified delivery.
- Executors/reviewers use **max reasoning, standard speed**; verify configured and
  actual native settings. Restoring task-local settings must retain max.
- One writer per editor instance; one memory-heavy build/bake/render/model at a time.
  Confirm live project/editor/bridge capability before mutations.
- Substantive changes have one primary independent technical reviewer. Controller
  acceptance checks scope/evidence/finding closure, not a duplicate full review.
  Small obvious changes may use self-checks. Waivers remain task-scoped. Recheck only
  affected behavior/transitions for a concrete change, gap, contradiction or risk.
  Preserve independent visual and owner design/play gates.
- Controller commits verified task-scoped changes locally before final handoff,
  using an English message with the task ID; exclude unrelated owner edits.

## Load by task

| Trigger | Read |
| --- | --- |
| Dispatch, review, Multica or editor/registry operations | [Execution](Docs/AgentPolicies/Execution.md) |
| AI, combat, movement, physics or gameplay variants | [Gameplay](Docs/AgentPolicies/Gameplay.md) |
| Environment, character, materials, visual assets or narrative | [Art](Docs/AgentPolicies/Art.md) |
| Changing instructions, context routing or worker prompts | [Context](Docs/AgentPolicies/Context.md) |

Keep current scope in ProjectState, task details in `Docs/Tasks/`, exact decisions
in `Docs/Approvals/`. Replace stale summaries; do not append delivery history here.
When changing these entrypoints/policies run `Scripts/check_context_budget.ps1`.
AGENTS + ProjectState have an 8 KiB combined budget; move detail to the task/policy.
Multica remains the source of live task state.
