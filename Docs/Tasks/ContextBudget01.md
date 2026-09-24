# ContextBudget01: bounded project context

Date: 2026-09-24. Direct administrative maintenance under the
[owner request](../Approvals/ContextBudget01-OwnerRequest01.json).

## Architecture and acceptance

The prior mandatory AGENTS and ProjectState totalled 84,008 bytes. ProjectState
alone contained 1,032 lines of current and historical handoffs. Requiring it for
every task pulled unrelated history into model input before useful task work.

The entrypoints now contain durable constraints/current scope and conditional
routes. Execution, gameplay and art details load only when their task trigger
applies. Historical content remains in exact frozen snapshots with a separate
[lookup index](../ContextHistory.md); task reports and owner decisions remain intact.
Bounded search/section reads, concise tool discovery and fresh delegation briefs
prevent recursive document/catalog/history loading.

Acceptance: combined entrypoints <= 8 KiB, each <= 4 KiB; policies <= 5 KiB each;
direct local navigation targets resolve; archived originals retain exact SHA-256;
owner decisions remain accessible and operative; unrelated owner edits stay intact.
The [guard](../../Scripts/check_context_budget.ps1) checks the size/link/fingerprint
criteria using [budgets and baselines](../../Tools/ContextBudget.json). It rejects
overflow instead of truncating instructions. Run it when changing entrypoints or
policies. No model context-window reduction or artificial early compaction is used.

## Validation and limits

The checked entrypoints fell from 84,008 to 6,894 bytes (91.79% less).
This is the repository startup-reading reduction, not a percentage reduction of
the whole model prompt. `Saved/ContextBudget01/verification.json` records exact
file sizes, 73 direct local link targets and both matching archive SHA-256 values.
Isolated guard cases passed: valid fixture succeeds; excess size, a missing link
and modified snapshot bytes each fail with a nonzero exit code. The fixture and
results remain in `Saved/ContextBudget01/`, outside Git.

Two old protagonist references were already absent from the checkout:
`Docs/Tasks/PlayerCharacter01Tasks.md` and `Docs/PlayerCharacter01AI3DPipeline.md`.
The art policy retains the requirement to recover/verify them before resumed
production; no missing content or owner approval is fabricated.

Metadata-only native rollout inspection found these pre-change input measurements:

| Session | First recorded input tokens | After initial reads |
| --- | ---: | ---: |
| Current owner chat | 23,998 | 33,054 |
| Sampled MSQ-120 Multica execution | 22,442 | 33,199 |

The owner-chat host also supplies base instructions, a model-switch instruction
block and skill descriptions. The sampled Multica run adds a 15,163-character
runtime brief. The available 348-tool catalogue is deferred; its aggregate size
is not evidence of eager prompt injection. No complete 70k-token attribution or
fresh-session total after this change is claimed. The audit records source paths
and separates character sizes from native token counts.

No integration was disabled and no upstream runner fork was introduced: the
measured largest removable project source was the mandatory document chain.
Native model settings and plugin capabilities are preserved. Host template
duplication and generic Multica instructions are separate integration concerns.

Verification results and the bounded local injection audit are retained under
`Saved/ContextBudget01/`. This administrative change uses controller self-checks
and acceptance with a bounded independent review of policy preservation and the
guard; the helper also audited injection sources.
Primary review passes after restoring the explicit GameBrief route for gameplay
requirements and the new-evidence prerequisite for retrying failed actions.
The reviewer inspected those corrections without repeating passing checks. Native
reviewer metadata confirms Astra/max; configured service tier is default, while
the actual tier is absent from the rollout and is not asserted as independently
verified. Full audit/review details remain in the Saved evidence above.
No gameplay/build test or production run is needed. Config/DefaultEngine.ini and
MeridianSquad.uproject owner changes are excluded from the closure commit.

The guard measures repository bytes, not exact model tokens. Native session input,
cache and output must be reported separately. Editing files cannot remove messages
already in an existing conversation. Host instructions, enabled skill descriptions
and tool metadata contribute additional input outside these two project files.
The implementation follows official [contextual loading guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra).
