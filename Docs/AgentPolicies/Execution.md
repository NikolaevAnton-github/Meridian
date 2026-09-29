# Execution policy

Read for implementation, optional board administration or editor/registry work.

## Direct work

Codex implements authorized work directly in the owner's chat under
[DirectWorkflow01](../Approvals/DirectWorkflow01-OwnerRequest01.json). Do not start
Multica workers, dispatch tasks, generate runtime briefs/checkpoints, enforce
worker capability profiles or require an independent technical reviewer.
Historical tasks retain their scope/evidence but their old execution and review
routing no longer applies. Prepared backlog items are not authorization to execute
them. No replacement dispatcher or task database is needed.

Use max reasoning and standard speed where configurable. Do not modify global
settings or instrument native sessions merely to implement a project task.
Keep full diagnostic output under `Saved/` and return concise relevant findings.

## Checks and handoff

Make the requested change, run focused source/build checks where useful, fix
identified defects and state exactly what was checked. Reuse relevant existing
evidence; repeat a check only for an affected change or a concrete gap/risk.
After two equivalent failures, change the diagnostic approach.

The owner performs final testing, gameplay/design review and acceptance. Do not
describe a source/build pass as final acceptance. Extra reviewers are used only
on owner request. Named owner design approvals and immutable asset evidence remain
required within their applicable scope.

Commit checked task-scoped changes locally with an English task identifier;
a local identifier from `Docs/Tasks/` is sufficient. Exclude unrelated owner edits.

## Optional Multica board

Multica may store tasks and history; it is not an execution dependency or live-state
authority. `Scripts/multica.ps1 -Action StartServices` starts the optional local
board (database/API/web). `Start` is the same board-only action. No action launches
a worker; `StartRuntime` is unsupported. Do not re-enable the retired daemon.
Board writes must suppress execution (`suppress_run=true` / CLI `--no-start`).
Reading or editing task records never authorizes executing their content.

`Stop` stops board API/web only. The shared PostgreSQL service and its data remain
available for the separate asset registry. Existing board history, installation,
credentials and evidence are preserved; the shared binaries retain their existing
`.tools/multica/pgsql` location. No scheduled task or Windows service is required.

## Tools and asset metadata

Prefer Epic `unreal_epic` MCP at `http://127.0.0.1:8000/mcp` for Unreal editor work.
Discover relevant tools on demand and confirm live project/editor state before
writes. Rider code/debug is separate. Verify actual DCC/bridge capabilities;
historical reports or configuration alone do not prove a live connection.
Keep one writer per editor and one memory-heavy build/bake/render/model at a time.

Asset metadata uses separate PostgreSQL `meridian_assets`: use existing
register/inspect/validate in [AssetRegistry](../AssetRegistry.md). Preserve accepted
fingerprints and relationship uncertainty; registration does not accept changed
bytes. Consult [acceptance semantics](../AssetRegistryAcceptance.md) for this
operation. Search [AgentDevelopment](../AgentDevelopment.md) only for needed
historical tooling details; its old worker workflow is retired.
