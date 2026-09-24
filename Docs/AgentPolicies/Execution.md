# Execution policy

Read for dispatch/review or tool administration; not routine startup.

## Dispatch and model settings

Use the existing Multica project. Administrative startup:
`Scripts/multica.ps1 -Action StartServices` (database/API/web only).
Administrative status, assignment and description writes use `suppress_run=true`
or CLI `--no-start`. Start the task runtime and dispatch only intended execution.
Keep production concurrency at one; stay active through handoff and bounded fixes.
Do not create a competing dispatcher or task database.

All executors/reviewers use max reasoning and standard speed under
[WorkerReviewerMax01](../Approvals/WorkerReviewerMax01.json). Use Astra for difficult
work; choose other available models when appropriate. Verify profile/native
arguments AND actual execution settings; labels alone are insufficient. Restore
task-local settings without restoring obsolete high/medium defaults. Explicit later
task-scoped owner exceptions apply only to that task.

Send bounded briefs: objective, scope, acceptance, relevant file/section paths,
current candidate, allowed writes and evidence destination. Do not embed global
history or repeat repository instructions. Keep full logs under `Saved/` and report
concise findings. Native input, cache and output are separate measurements.
For this project, prepare the bounded role-specific brief before dispatch and a
current checkpoint before resume using [the lifecycle commands](../../Scripts/ContextBudget/README.md).
The daemon validates them before injection; repair stale identity explicitly.
Use the role's required capabilities and check effective native settings. Keep
ordinary tool responses within 2,000 tokens; save complete outputs under Saved and
retrieve only needed ranges. See [context policy](Context.md) for budgets/usage.
A new Multica run ID does not prove a fresh model session: this runner can resume
the source session on rerun. Use a new scoped issue for independent work and verify
native fresh/resumed identity; keep intentional continuation on its valid checkpoint.

## Verification and closure

Define acceptance before implementing. Executor self-checks; one primary independent
reviewer owns substantive technical review; controller checks scope, evidence
applicability and finding closure. Additional reviewers need distinct criteria.
Small obvious changes can use self-checks/controller acceptance; record the route
briefly in the task. Details only when needed:
[review responsibilities](../AgentDevelopment.md#review-responsibilities) and
[authority](../Approvals/ReviewResponsibilities01.json).

Reuse applicable passing evidence with its candidate identity. Repeat checks only
for a recorded change, gap, contradiction or uncovered risk, limited to affected
behavior/transitions. Retry a failed action only with new evidence; after two
equivalent failures change the diagnostic approach.
Reuse existing validators; do not rebuild benchmarks or repeat routine asset A/B runs.
Technical, independent visual and owner acceptance remain distinct; review waivers
do not carry to other tasks. Controller makes the local task-scoped closure commit
under [TaskClosureCommits01](../Approvals/TaskClosureCommits01.json).

## Tools and asset metadata

Prefer Epic `unreal_epic` MCP at `http://127.0.0.1:8000/mcp` for Unreal editor work.
Discover relevant toolsets on demand and confirm project/live state before writes.
Rider code/debug is separate. Check installed DCC versions and real capabilities;
configuration and historical reports alone do not prove a working bridge.

Asset metadata uses separate PostgreSQL `meridian_assets`: use existing
register/inspect/validate in [AssetRegistry](../AssetRegistry.md). Preserve accepted
fingerprints and relationship uncertainty; registration does not accept changed
asset bytes. Consult [acceptance semantics](../AssetRegistryAcceptance.md) for this
operation. [AgentDevelopment](../AgentDevelopment.md) contains tooling history;
search the needed section instead of reading its full chronology.
