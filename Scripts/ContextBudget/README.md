# ContextBudget02 tooling (MSQ-138)

This repository policy instruments Git commits and this project's Multica daemon.
It does not replace Multica task state or enforce every host/tool boundary.
Generated evidence, active documents and native test homes belong under `Saved/`.

## Commands

On Windows, launch the administrative shell with `powershell -NoProfile -ExecutionPolicy Bypass` before dot-sourcing `python.ps1`; this changes execution policy only for that process.

PowerShell uses an existing Python 3.11+ installation. Set process-local
`CONTEXT_BUDGET_PYTHON` if automatic discovery cannot find it. No packages,
API keys, services or purchases are needed.

```powershell
. Scripts/ContextBudget/python.ps1
$contextPython = Get-ContextPython
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/check_context_budget.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/check_context_budget.ps1 -Mode Staged -RelevantOnly
& $contextPython Scripts/ContextBudget/install_hooks.py
& $contextPython Scripts/ContextBudget/install_hooks.py --remove
```

The installer wraps only the resolved repository-local `pre-commit`; it rejects
aliases of the versioned `.githooks/pre-commit` source. It preserves
the original at `pre-commit.context-budget-original`, runs it first, propagates its
exit status, leaves other hooks/LFS and `core.hooksPath` intact, and records exact
rollback identity under `Saved/ContextBudget02/hook-install.json`. Modified hooks,
symlinks and shared external hook directories require manual reconciliation.
For this delivery, controller activation follows independent review.

Staged validation reads the manifest, policies, maps, links and immutable archives
from index blobs. Unrelated staged changes skip the guard. Working-tree mode can
measure the exact generated Multica marker block separately; staging it fails.
Immutable snapshots/budgets cannot be silently changed relative to HEAD.
The existing snapshot hashes remain unchanged. Maps use optional `maps` manifest
entries with `path` and `max_bytes <= 5120`; they are validated, not injected.

## Active briefs and checkpoints

One current document pair per issue UUID lives at
`Saved/ContextBudget02/tasks/<issue UUID>/{brief,checkpoint}.json`.
`task_id` means the live issue UUID; daemon `run_id` identifies one execution.
Raw and serialized limits are 4096 bytes for briefs and 2048 for checkpoints.
No history is appended. Old evidence files are retained separately.

To create a brief, write these content fields to a UTF-8 JSON file under Saved:

```json
{
  "role": "code",
  "objective": "Implement the bounded authorized task; read its linked task document.",
  "allowed_writes": ["Scripts/ContextBudget"],
  "acceptance": ["Focused checks pass; preserve owner changes"],
  "pending": ["Implementation and focused validation"],
  "evidence": ["Docs/Tasks/ContextBudget02.md"]
}
```

```powershell
& $contextPython Scripts/ContextBudget/context_budget.py write brief --issue 01a0d43a-d711-7ad9-8931-d42f59ae7eff --input Saved/ContextBudget02/Worker/brief-content.json --candidate MSQ-138-Candidate01 --authority Docs/Approvals/ContextBudget02-OwnerStart01.json
```

The writer reads the issue through authenticated `multica issue get`, records
the current Git revision, exact title/description scope hash and authority hash.
It resolves the existing repo-local CLI when `CONTEXT_BUDGET_MULTICA` is unset,
then falls back to PATH. Controller shells with only a named CLI profile can add
`--controller-profile meridiansquad` to `write`, `validate` or `state` (or set
`CONTEXT_BUDGET_MULTICA_PROFILE`). This explicit administrative mode reads from
the repository parent to avoid the active in-place task marker. Task token,
task ID or task config-root environments reject controller mode; preparation
never accepts it. Worker/daemon reads retain their scoped credentials and cwd.
Do not clear task identity to turn a worker into an administrator.
The candidate label identifies the controller's current candidate; change it in
the brief when selecting a new candidate, and keep exact file fingerprints in
the evidence. Uncommitted source edits do not automatically redefine that label.
Brief identity is authoritative for checkpoint candidate matching; this is not
a source-content lock that prevents the executor from making authorized edits.

Checkpoint content has exactly `next_step` (nonempty string), `pending` (strings)
and `evidence` (existing repository-relative paths). The writer inherits current
brief identity and adds its hash:

```powershell
& $contextPython Scripts/ContextBudget/context_budget.py write checkpoint --issue 01a0d43a-d711-7ad9-8931-d42f59ae7eff --input Saved/ContextBudget02/Worker/checkpoint-content.json
& $contextPython Scripts/ContextBudget/context_budget.py validate --issue 01a0d43a-d711-7ad9-8931-d42f59ae7eff
```

Unknown fields, stale scope/revision/authority/candidate, replaced briefs, missing
evidence and closed/unknown live statuses fail. No cached task state authorizes
launch. Resume/cold resume requires a checkpoint. Replacing a brief deliberately
invalidates its previous checkpoint. Instructions point workers to the validated
brief/checkpoint before work. Agent custom env `MULTICA_CONTEXT_ROLE`, if set,
must agree with the brief role; the brief selects the profile even without it.

## Full artifacts and bounded retrieval

```powershell
& $contextPython Scripts/ContextBudget/context_budget.py run --label git-status --timeout 30 -- git status --short
& $contextPython Scripts/ContextBudget/context_budget.py preview Saved/ContextBudget02/Worker/python-tests.log --start 1 --lines 20 --bytes 2048
```

`run` writes complete stdout and stderr separately, returns their manifest and the
command's exit status (124 on timeout). It never invokes a shell implicitly.
The summary does not dump log bodies. `preview` is limited to 80 lines / 8192 bytes.
Do not put credentials into captured command output. Commands that detach their
own services are outside this helper's lifecycle contract; do not use it to start
unobserved background work. Native role profiles also apply
`tool_output_token_limit=2048` for history retention. Installed Codex 0.153.4
accepted this key in strict mode and exposed the value through native config/read.
It does not itself save complete artifacts; use the capture helper first.
No model window or `project_doc_max_bytes` is reduced.

## Daemon integration and role configuration

The additive patch targets pinned Multica `2ae2dbbb8f9ed9ffe1739ecf5abfe31a940ee50c`.
Keep `Tools/Patches/multica-0.4.43-local.patch` and all existing local source edits.
`Scripts/multica.ps1` supplies `MULTICA_CONTEXT_PROJECT_ROOT` and the resolved
Python path to the existing daemon. The patch gates matching in-place project
issue tasks before runtime injection and again before cold reinjection. Gated
prompts/workflow consume the brief instead of requiring full issue JSON. Other
project paths keep their existing behavior. Worktree-mode/root aliases require
explicit integration and are not claimed as covered by this in-place deployment.

The gate runs with a 45-second deadline and only required nonsecret system paths
plus task-scoped Multica CLI identity. It never passes owner credentials or stores
tokens. Missing policy/Python/live issue/brief stops preparation before injection.
Logs and request/result metadata live in `Saved/ContextBudget02/runs/<run UUID>/`.

Profiles in `Tools/ContextBudgetRoles.json` are applied to the task-local native
config: merged home/project MCP allowlist, plugin enablement, supported per-skill disables,
max reasoning, default service tier and native output budget. Existing allowed
MCP configuration values stay in memory and the private native config, including
their auth. Global config/auth and agent definitions are not overwritten. Named
native profiles conflict with these task roles and fail explicitly. Code keeps
Rider and installed debugging-code/refactoring-code workflows; Unreal adds Epic;
art/review retain relevant Unreal/DCC tools. Disabled entries retain transport for
project env overlays; daemon-owned overrides enforce their disabled state after
custom argument filtering. Required
servers must already exist in the runtime/agent configuration; the manifest does
not invent service connections. A role allowlist is not action authorization.
Host/system/plugin capabilities discovered outside these native configuration
paths are not universally isolated; verify installed effective capabilities.

The native config keys follow the [official configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
and [plugin enablement documentation](https://developers.openai.com/plugins/build/plugins).
Installed-native evidence takes precedence over assumptions about newer docs.

## Native measurements and comparisons

`usage.py collect` is called synchronously after each daemon native attempt,
including failed/resumed/cold attempts. It reuses metadata parsing in
`Scripts/Benchmarks/OrchestrationAB/snapshot_controller_usage.py`. It scans only
the exact thread rollout; it never copies raw transcript bodies into its output.

Per-response records within a closed run interval are deduplicated by response ID.
Later resumes cannot change a completed measurement. Input includes cached input;
output includes reasoning. Neither is added again. First, second, peak and last
native request input are separate from summed usage. The second request is an
observed bootstrap proxy, not proof that every possible tool/skill is loaded.
Fresh/resumed/cold identity, native version/model/effort, configured service tier,
profile/config/MCP/argument signatures and workload are recorded. Actual service
tier is unknown if native turn metadata omits it; effective config is separate proof.

Complete finished observations automatically create an immutable baseline for
their comparison key, or compare to the existing baseline. Keys include native
version, model, effort, configured tier, session kind, role/effective config,
MCP/launch signatures, consumed brief/checkpoint and exact workload. MCP and native
config comparison signatures use structured semantic data: disabled servers and
credential values do not split baselines, task-owned paths are normalized, and
enabled brokers use stable logical connection/tool identities. Missing logical
identity explicitly makes the run incomparable. Exact raw hashes remain separate
evidence. Incompatible records are rejected.
Directional metric increases are reported for review without invented numeric
pass/fail thresholds. Missing traces/response records are explicit coverage gaps.

```powershell
& $contextPython Scripts/ContextBudget/usage.py compare --baseline Saved/ContextBudget02/Worker/native-evidence-final/fresh-usage.json --current Saved/ContextBudget02/Worker/native-evidence-final/fresh-repeat-usage.json --output Saved/ContextBudget02/Worker/comparison.json
```

## Verification and deployment

Focused Python tests: `python -m unittest discover -s Scripts/ContextBudget -p 'test_*.py' -v`.
Focused Go tests: `go test ./internal/daemon ./pkg/agent -run '^TestContextBudget' -count=1 -p 1`.
Both preserve logs under Saved. `build_candidate.ps1` builds only a staged runner;
it does not replace the installed executable, stop the daemon or commit.
See the worker handoff for exact fingerprints and controller deployment/rollback.
Controller must finish independent review and installed-daemon acceptance.

`native_smoke.py` uses the production Go config writer's exported role homes.
It checks all four through native `config/read` without model generation by
default. `--generate` requests five short subscription responses for a fresh
two-response baseline, one resumed response and a matching fresh repeat. Auth is
temporarily hard-linked into the private smoke home, never printed/attached, and
the link is removed on completion. Use `--config-cwd D:/devgames/MeridianSquad`
to verify actual trusted project layers; generation still uses the isolated
fixture. Do not run generation during a heavy build. Extend a task's role only
for authorized required capabilities by editing the versioned role allowlist,
regenerating task-native config and checking its effective state; global owner
config is not the extension mechanism.
