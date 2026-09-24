# ContextBudget02 primary core review

Status: PRIMARY TECHNICAL REVIEW PASS. CORE-01 through CORE-06, final source/package identity, and the administrative CLI correction are closed. Documentation maps also PASS. Installed-daemon acceptance and deployment remain controller-owned.

## Actionable findings

- **CORE-01 (P2, CLOSED): hook wrapper can call itself.** `install_hooks.py:18-49` permits `core.hooksPath=.githooks`; it then replaces the versioned `.githooks/pre-commit`, and WRAPPER executes that same path recursively. Reject source/target alias before mutations or implement that layout without self-wrapping. Preserve the original hook and rollback. Existing coverage tests `.local-hooks`, not this supported repository-local layout.

- **CORE-02 (P1, CLOSED): role filtering misses the project config layer and can prevent startup.** `context_budget.go:162-214` filters task-home MCP, while upstream `runtime_mcp.go:280-285` reads only user/home config. Native still merges repository `.codex/config.toml`: it declares enabled Unreal, Painter, and a Blender env-only overlay. Deleting Blender's home transport leaves that overlay invalid. A config-only native probe with code-role overrides and the trusted real project cwd failed `invalid transport in mcp_servers.blender`; no thread/model ran. Evidence: `role-project-config-probe/result.json`. Existing smoke uses a separate workdir and therefore misses this. Enforce restrictions across actual effective home/project layers while retaining allowed transport/auth and owner bytes; verify role server states at actual project cwd. Effective-config comparison fingerprints must include those layers too.

- **CORE-03 (P2, CLOSED): staged rename can bypass the relevant-only guard.** `context_budget.py:170-179` uses `git diff --cached --name-only`, which reports only the rename destination. A staged rename of a directly linked target makes the normal guard fail but relevant-only return passed/skipped. Reproduced in `rename-probe.json`. Include rename sources (for example, disable rename collapsing in the changed-path query) and add this case.

- **CORE-04 (P2, CLOSED): validated brief remains an additional read rather than the bounded dispatch path.** `daemon.go:8033` appends a pointer to the brief, but unchanged `prompt.go:223,439` still explicitly requires full `multica issue get --output json`; the runtime workflow also provides that read. A large live description therefore bypasses the brief's 4 KiB limit and duplicates task context. Route gated task starts/resumes through the validated brief/checkpoint while retaining live-state validation outside model input and necessary bounded comment updates. Preserve other projects' prompt behavior.

- **CORE-05 (P2, CLOSED): required coding skills are excluded.** `Tools/ContextBudgetRoles.json` omits `debugging-code` and `refactoring-code` from code/Unreal/review skill allows, despite the controller's explicit retention requirement. `applyContextBudgetNative` disables discovered skills not listed. Retain these capabilities and demonstrate required skills survive role selection.

- **CORE-06 (P2, CLOSED): comparison workload does not include the consumed brief.** `context_budget.go:339-343` hashes the short Multica prompt as workload, while `usage.py:13,32-36` excludes `brief_sha256` from compatibility. Replacing a brief's objective/acceptance under the same issue can therefore remain comparable. Include the consumed brief/checkpoint identity or an explicit stable workload identity, and reject changed workload comparisons. Also fix `native_smoke.py:124-131`: binding hashes loop-leftover `extra` before assigning the actual code-role launch args, so its recorded launch hash does not describe the measured launch.

## Reused evidence and accepted boundaries

Reused `Worker/python-tests.log` (12 passing tests) and `Worker/go-tests.log`; did not repeat them. Reviewed initial/cold fail-before-injection seam, exact managed-block cleanup, staged blob reads, immutable snapshots, live closed/stale checkpoint checks, complete command artifacts, bounded previews, response-ID deduplication and native token semantics. Native second-request input is accurately identified as a bootstrap proxy; native output includes reasoning and input includes cached input.

Worker v2 native config/read exposes **tool_output_token_limit=2048** and max/default. This is a different, supported key from the rejected `tool_output_limit`; the earlier audit's negative result must not be generalized to it. v2 smoke explicitly limits service-tier claims to configured evidence. Full artifacts still require capture; no universal host/MCP output enforcement is claimed or required for acceptance. Actual role layering (CORE-02) remains unverified/failing.

## Bounded correction closure: CORE-01 / CORE-03 / CORE-05

`easy-finding-closure.json` records exact current hashes and finding-specific results. The alias installer now rejects `.githooks` before mutation, preserves source bytes and creates no backup. The previously failing staged-rename case now rejects the broken staged link without skipping. Code/Unreal/review explicitly allow both required coding skills. These two disposable-fixture regressions were the only executions; no passing suite was rerun. Native role layering, prompt consumption and comparison correctness await the final corrected candidate.

## Remaining correction source review

CORE-04 now selects the validated brief prompt for gated issue/comment starts and updates runtime workflow step 1; ordinary project prompts remain on their prior path. CORE-06 now compares brief/checkpoint identities and hashes the actual code-role smoke arguments. Source changes are reviewed at `remaining-source-review-identities.json`; focused passing executor evidence and final package identity are still required.

CORE-02 remains open. Project overlays are now merged and excluded transports retained disabled, but the first actual-project native smoke failed. Generated CLI overrides still quote MCP key names; prior native output showed literal-quote plugin keys, so the installed parser behavior must be resolved and actual-cwd role output verified. No suite or model session was rerun for this reconciliation.

## CORE-02 / CORE-04 closure and remaining CORE-06 scope

CORE-02 is closed against v4 effective native configuration and corrected source: the code role enables only Rider; Unreal enables Rider/Epic; art enables Blender/Epic/Painter; review enables Rider/Blender/Epic/Painter. Excluded transports remain present but disabled, including the Blender overlay dependency. Every role shows max/default and output budget 2048. Native dotted overrides now omit literal quotes and reject unsupported key spellings. Reused `Worker/native-root-smoke.log`, `Worker/native-profiles-v4/effective-native-config.json` and `smoke-result.json`; no repeated model/config probe was run by the reviewer.

CORE-04 is closed against the bounded prompt/runtime-workflow changes and focused passing Go evidence. `Worker/core-fixes-go.json` resolves to passing daemon/agent checks; Python evidence resolves to 16 passing tests. The required brief/checkpoint identity fields and corrected smoke launch hash also close the original CORE-06 subissues.

**Remaining CORE-06 (P2): semantic comparison identity must exclude incidental broker/auth state.** `daemon.go:8033` currently records `MCPSHA = contextBudgetDigest(effectiveMcpConfig)`, including disabled server objects. `plugin_hook_mcp.go:96,122` and `remote_mcp_broker.go:117,144` generate random per-task token URLs/ports, so otherwise identical role runs can form a new series every time. `context_budget.go:309-312` also fingerprints the entire private config with only textual home/root substitution; embedded credentials remain comparison inputs.

Targeted correction: preserve exact byte hashes for evidence, but derive comparison fingerprints from structured semantic data. Exclude disabled MCP entries from comparison capability data. For enabled brokers, use stable logical connection/server and exposed tool identities rather than generated listener URLs/tokens; fail explicitly as incomparable if stable identity is unavailable. Remove credential values while retaining relevant auth mechanism/key names and nonsecret behavioral settings. Apply the same semantic projection to `mcp_sha256` and the MCP/auth portions of `effective_config_sha256`; changing only one leaves the other key unstable. Normalize task-owned path values structurally, preserving genuine user configuration differences. Prompt/launch construction already excludes run_id and ended_at; avoid a broad rewrite there.

Focused proof needed: two bindings with the same brief/checkpoint, enabled capabilities and nonsecret behavior but different run UUID/time, task directory and broker/auth token must share the comparison key and reuse one baseline. Changing an enabled tool/server, actual workload or relevant setting must remain incompatible. No suite-wide repetition or extra native generation is required for this identity test. Final staged binary/source-manifest reconciliation remains a separate delivery check after this finding closes.

## CORE-06 semantic source correction

Reviewed `context_budget_identity.go` and its MCP/config call sites. Exact hashes remain evidence-only. Semantic comparison omits disabled MCP entries, substitutes logical enabled broker/tool descriptors, removes credential values, structurally normalizes task-owned paths and marks missing enabled broker identity incomparable. Both MCP and native-config comparison hashes use the projection. Source is sufficient for the reported gap; focused stability/change proof and final delivered identities remain pending. Current hashes are in `core06-source-identities.json`.

## CORE-06 focused evidence closure

CORE-06 is closed. `Worker/semantic-identity-go.json` resolves to a passing daemon test result. The inspected test changes task directory, run identity, credential-bearing arguments/headers/environment, disabled-server data and broker URL/port; config and MCP semantic hashes remain equal while exact hashes differ. Changed enabled tool schema and native output setting change the respective semantic fingerprints, and unknown enabled broker identity is rejected as incomparable. `Worker/semantic-identity-test.json` records these equal/different results; `native-semantic-signatures.json` binds the native sample. Measurement schema 4 separates the corrected comparisons from earlier baselines.

Reused the focused executor proof without rerunning it. Exact reviewed source/evidence hashes are in `core06-closure-identities.json`. All substantive findings are now closed; only final source/patch/binary reconciliation remains.

## Final package reconciliation

The 20:36 candidate matches staged binary SHA-256 `74e8cfed8eaab7ecb97fabd21912bc4af370e53cadd034f6a0cc8f4465285a95` and additive patch `db29fe56b9b776b92b9fc9710a9e5d1c8c6ab5a25dbe387603d4a214262f368c`. All 15 manifest files match current source and the replayed tree. The three preexisting local source changes and prior local patch remain unchanged. Build capture reports exit 0; no reviewer rebuild or suite repetition. The bounded final reconciliation covered the compact live-state command, closed native run interval parser, related regression tests and documented role/measurement limits. Exact identities are in `package-reconciliation.json`.

The additional `Worker/semantic-baseline-proof.json` (fixture-only, passing captured Python command) demonstrates one immutable baseline is reused after run/time/home/auth rotation; tool/schema and behavioral-setting changes remain incompatible. This supplements CORE-06 closure without more native generation.

Controller acceptance then identified a separate administrative CLI environment gap: explicit named profile and neutral cwd are required to create an owner brief while another task marker exists. The worker is preparing a narrow fix and focused auth/argv/cwd proof; final acceptance remains pending that review. Live deployment remains controller-owned.

## Administrative CLI correction closure

PASS. `context_budget.py:226-244` resolves an explicit executable, then the existing repo-local CLI, then PATH. Only explicit controller profile selection adds `--profile` and reads from the repository parent to avoid the active project task marker. Any task token, task ID or task config-root environment rejects that mode. `prepare()` always calls `live_issue(..., allow_controller=False)`; worker reads retain scoped auth and project cwd. No environment credential is cleared, copied into evidence or borrowed from owner configuration. The README documents controller invocation and the boundary.

Reused `Worker/admin-cli-tests.json`: three focused checks passed, covering argv/cwd resolution, worker auth retention/profile rejection, and live brief/checkpoint behavior. The controller separately reported real brief/checkpoint creation and validation success using its named profile. Reviewed delta/evidence hashes are in `admin-cli-closure-identities.json`; all Go manifest sources, staged executable and patch remain identical to the reconciled package. No further technical finding or reviewer-side validation remains.
