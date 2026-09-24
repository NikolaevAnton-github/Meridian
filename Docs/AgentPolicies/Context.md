# Context policy

Load only for instruction, worker-prompt or context-maintenance work.

The mandatory project input is AGENTS plus ProjectState, at most 8 KiB UTF-8 total.
Each is limited to 4 KiB. These are byte budgets, not claims about model tokens or
the application's hidden/tool context. Do not reduce the model context window or
silently truncate instructions to meet them.

Use three layers:

1. Entry: durable constraints and current scope with task/policy routes.
2. Task: one relevant brief, applicable policy, decisions and evidence sections.
3. Evidence: detailed reports, archives, manifests and logs queried only as needed.

An old delivery belongs in its task handoff, not the startup snapshot. Replace stale
scope; keep historical evidence unchanged. Read linked files only for the active
decision, requirement or verification. Explicit task requirements still apply.
Search large files by heading/identifier and read the relevant range. Do not dump
whole config files, MCP inventories, task lists, manifests or logs into model input.

Delegation defaults to fresh context with objective, scope, acceptance, file/section
paths, candidate identity and evidence destination. Avoid full-history forks for
bounded independent work. Keep task descriptions and profile prompts short; refer
to canonical project rules rather than copying them. Do not inherit unrelated task
resume sessions. This is a prompt discipline, not a second dispatcher/database.

## Enforced lifecycle

Use [ContextBudget tooling](../../Scripts/ContextBudget/README.md) for exact commands.
The installed Git hook checks staged context files, navigation and immutable
archive fingerprints. The Multica gate checks each project task before runtime
injection, including cold resume. Keep startup at 8 KiB, each policy/map at 5 KiB;
move detail into the relevant task/handoff rather than raising limits.

Before dispatch, write a validated brief (4 KiB maximum), selecting the task role,
candidate, owner authority, allowed writes and acceptance. Before resume, replace
the active checkpoint (2 KiB maximum) with remaining work and evidence paths.
Scope/revision/authority/candidate changes invalidate stale identity; closed tasks
cannot resume from an old checkpoint. Multica remains the live state authority.
Select code, Unreal, art or review capabilities for the actual task; document any
necessary profile extension. Preserve max reasoning and standard speed.

For source navigation, open one relevant [subsystem map](../Subsystems/README.md),
then only its relevant entrypoints. Ordinary tool output should be at most 2,000
tokens; request explicit larger ranges only for concrete missing evidence.
Capture full command results with `context_budget.py run`; retrieve bounded ranges
with `preview`. Native history limits do not preserve full diagnostics by themselves.
Avoid whole-file dumps and repeated passing test logs. Calls outside the repository
helpers/native integration still require this output discipline.

When changing context files, run `Scripts/check_context_budget.ps1`; the installed
hook separately checks the index. Automatic native usage records distinguish first,
bootstrap-proxy and peak input from cached/output totals. Compare compatible native
version, role, configuration, session kind and workload; inspect reported growth
before accepting a new baseline. See [ContextBudget02](../Tasks/ContextBudget02.md).

Existing conversation history cannot be removed by editing repository files.
Measure a fresh session separately from this migration session. Report repository
bytes independently from actual native input/cached/output token usage; do not claim
the total starting prompt has shrunk by the repository percentage.

This follows official guidance on [progressive disclosure and AGENTS](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra).
The preserved pre-change sources and lookup routes are in [ContextHistory](../ContextHistory.md).
