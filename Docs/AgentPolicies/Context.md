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

When modifying entrypoints/policies run:
`powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/check_context_budget.ps1`
The guard checks size, direct navigation targets and immutable archive fingerprints.
Fix overflow by moving detail into the existing relevant task/handoff. Do not raise
limits to accommodate a new diary. Scoped policies have a 5 KiB per-file limit.

Existing conversation history cannot be removed by editing repository files.
Measure a fresh session separately from this migration session. Report repository
bytes independently from actual native input/cached/output token usage; do not claim
the total starting prompt has shrunk by the repository percentage.

This follows official guidance on [progressive disclosure and AGENTS](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra).
The preserved pre-change sources and lookup routes are in [ContextHistory](../ContextHistory.md).
