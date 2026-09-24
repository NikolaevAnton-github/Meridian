# ContextBudget02 delivery

Delivered 2026-09-24 under **MSQ-138**; **MSQ-139** is its fresh, read-only installed
runner acceptance task. [Owner authority](Approvals/ContextBudget02-OwnerStart01.json).
No gameplay or deferred art task was dispatched.

## Installed controls

| Area | Result |
| --- | --- |
| Repository input | AGENTS and ProjectState total 6,993 UTF-8 bytes against an 8,192-byte limit. Policies and subsystem maps have separate 5 KiB limits. |
| Git and task entry | Installed preserving pre-commit hook validates staged blobs, including renamed link targets. The deployed Multica runner checks every matching project task before initial and cold-resume injection. |
| Task lifecycle | Validated 4 KiB briefs and replaceable 2 KiB checkpoints bind live task scope, revision, authority and candidate. Stale/closed identities fail; gated prompts consume the brief instead of requiring full issue JSON. |
| Tool output | Complete command output stays under Saved; bounded previews expose selected ranges. Native task profiles set `tool_output_token_limit=2048`; ordinary tool calls follow a 2,000-token output policy. |
| Source navigation | On-demand [AI, navigation, weapons and animation maps](Subsystems/README.md) identify actual entrypoints, boundaries and focused checks. |
| Capabilities | Code, Unreal, art and review roles apply task-local MCP/plugin/skill settings, including project configuration overlays. Required debugging/refactoring skills remain available. |
| Measurements | Every native attempt records metadata and compatible baseline/comparison results. Semantic identities ignore incidental credentials, disabled tools and task/broker paths; workload and enabled capability changes remain distinct. |

Use [the tooling README](../Scripts/ContextBudget/README.md) for commands, schemas,
controller profile selection and rebuilding. [Execution policy](AgentPolicies/Execution.md)
also records that a new Multica run ID can resume an old model session; independent
work needs a fresh scoped issue and verified native session identity.

## Verification

- [Primary technical review](ContextBudget02Review.md): PASS, six findings and the
  administrative CLI correction closed. [Subsystem map review](ContextBudget02MapsReview.md): PASS.
- Focused Python/Go checks cover staged mismatches and renames, preserving hooks,
  stale checkpoints, pre-injection/cold gates, bounded artifacts, scoped auth,
  native token semantics and stable comparison identities. Existing passing
  evidence was reused. The additive patch replays all 15 source files exactly.
- Codex 0.153.4 `config/read` verified all four roles at the actual project cwd.
  Fresh/resumed/repeated native probes verify accounting and comparison behavior.
- Installed run `01a0d48c-42ee-7ae3-a519-859d14bc8a0b` completed in a fresh session.
  Its real process used Astra/max/default and output cap 2048; role `code` enabled
  Rider. Native turn metadata confirms `gpt-6-astra`/max. Default tier is verified
  in effective configuration and launch arguments; turn metadata omits actual tier.
- Automatic collection recorded **18,753 first-input tokens**, **21,320 after the
  first response**, and **25,367 peak input tokens**, across five responses. The
  second request is a bootstrap proxy. Summed usage is 113,561 input including
  99,584 cached input, and 1,890 output including 893 reasoning tokens. These totals
  are not one context-window size. An immutable baseline was created automatically.

The native smoke is a new measurement, not a like-workload comparison with an old
70k session. Repository byte reduction and native token measurements are separate.

## Deployment and preservation

Installed Multica: 0.4.43, build `2ae2dbbb8-ContextBudget02`.
Exact binary/additive-patch hashes are pinned in [requirements](../Tools/Requirements/multica.json).
The prior patch and three preexisting local Multica source edits were preserved.
Owner changes in DefaultEngine.ini and MeridianSquad.uproject, the project Codex
configuration, agent profile and all four existing Git LFS hooks remain unchanged.

The global Codex config hash changed during acceptance. Its host integration
version changed from 26.917.62051 in the initial task copy to 26.917.71314. The newer
configuration was retained; this is not reported as byte preservation. The
[preservation audit](ContextBudget02GlobalConfigReview.md) found no ContextBudget
global writer. The replacement preceded the installed task by 21 seconds and is
consistent with a host refresh; exact writer attribution remains unproven. The
original failed byte comparison is preserved, and no old config was restored.

The task runtime was stopped after acceptance; the preexisting API/web/database
services remain available. The original CLI backup is
`Saved/ContextBudget02/Controller/multica-before-contextbudget02.exe`.
Rollback requires stopping only the idle daemon, verifying the saved executable
hash and restoring that backup. A rolled-back runner does not enforce the new gate.
Hook rollback uses the preserving installer described in the README.

Full local evidence is under `Saved/ContextBudget02/Worker/`, `Controller/`, and
`runs/01a0d48c-42ee-7ae3-a519-859d14bc8a0b/`; original native traces remain preserved.

## Boundaries

Enforcement covers this repository and its matching in-place Multica tasks.
Different worktree/root aliases need explicit integration. Host capabilities and
tool calls outside these helpers/native profiles are not universally intercepted.
Native output limits do not themselves retain complete diagnostics; use artifact
capture. Existing conversation history is not removed by these file changes.
