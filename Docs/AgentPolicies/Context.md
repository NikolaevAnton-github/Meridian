# Context policy

Load only for instruction or context-maintenance work.

The mandatory project input is AGENTS plus ProjectState, at most 8 KiB UTF-8 total.
Each is limited to 4 KiB. These are repository byte budgets, not model token or
application-context measurements. Do not reduce the model context window or
silently truncate instructions to meet them.

Use three layers:

1. Entry: durable constraints and current scope with task/policy routes.
2. Task: relevant objective, applicable decisions, sources and acceptance.
3. Evidence: detailed reports, archives, manifests and logs queried only as needed.

Replace stale scope rather than appending delivery history to startup files.
Keep historical evidence unchanged. Read links only for the active requirement or
verification; search large files by heading/identifier and read the relevant range.
Avoid whole config files, MCP inventories, task lists, manifests and logs.

## Direct workflow

[DirectWorkflow01](../Approvals/DirectWorkflow01-OwnerRequest01.json) retires Multica
dispatch, runtime injection, role profiles and mandatory brief/checkpoint gates.
Task notes in `Docs/Tasks/` and the current owner request are sufficient for direct
work. Multica may retain optional board records but is not needed for context,
progress tracking, resuming work or delivery. Do not create a replacement workflow.

The old automatic pre-commit wrapper and native-session measurement integration
are removed. [ContextBudget tooling](../../Scripts/ContextBudget/README.md) retains
only standalone repository validation and optional bounded command output helpers.
It has no service, authentication, issue-state or worker-profile dependency.

When changing context files, run `Scripts/check_context_budget.ps1`. It checks
startup/policy/map budgets, direct navigation and immutable archive fingerprints.
Policies and subsystem maps remain limited to 5 KiB each. Keep original manifests
and archived bytes intact; do not rebaseline them to make a check pass.

For source navigation, open one relevant [subsystem map](../Subsystems/README.md),
then only its needed entrypoints. Prefer tool output within 2,000 tokens; save full
diagnostics under `Saved/` and retrieve bounded ranges. Optional `run`/`preview`
helpers are conveniences, not prerequisites for shell commands or project work.

Existing conversation history cannot be removed by editing repository files.
Report repository bytes separately from native input/cached/output token usage.
Do not claim the whole starting prompt shrank by the repository percentage.
Preserved pre-change sources and lookup routes are in [ContextHistory](../ContextHistory.md).
