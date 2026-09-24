# ContextBudget02: automatic context lifecycle

Authorized by [the owner](../Approvals/ContextBudget02-OwnerStart01.json) after
[ContextBudget01](ContextBudget01.md). Multica issue: **MSQ-138**.
Scope is project tooling; gameplay and deferred art tasks are not dispatched.

## Required result

1. Install a versioned pre-commit integration for the context guard, preserving
   existing hooks and Git LFS. Validate staged blobs/paths, not merely working files.
   Run only for relevant changes. Reject missing/oversized/broken staged inputs.
2. Run the same bounded policy before each Multica task preparation, before runtime
   instructions are injected, including cold resume. A runtime-start check alone is
   insufficient. Reuse the existing launcher/daemon and installed local patches;
   no competing dispatcher or task database. Preserve existing launches elsewhere.
3. Add validated dispatch briefs (initial 4 KiB) and replaceable active checkpoints
   (initial 2 KiB), with task ID, candidate/revision, owner authority, pending work
   and evidence paths. No appended history; detect stale scope/candidate/closed
   task use. Multica remains authoritative for task status. Provide commands and
   examples that work now, not only a prose template.
4. Give context-facing scripts compact summaries by default; keep full results in
   Saved and expose bounded previews/ranges for retrieval. Preserve diagnostics and
   meaningful exit codes. Reuse existing scripts; no universal lossy MCP truncation.
5. Provide on-demand maps for AI, navigation, weapons and animation: actual source
   entrypoints, boundaries, invariants, focused checks and scoped task/decision links.
   Controller owns these documentation files; the executor validates navigation and
   bounds and supplies any needed schema. Do not rewrite production game code.
6. Automatically record native first input, input after bootstrap/observed growth,
   cached input and output with clear semantics, native version/model and fresh vs
   resumed identity. Reuse `Scripts/Benchmarks/OrchestrationAB/snapshot_controller_usage.py`
   or its established metadata parsing where applicable. Do not read raw transcript
   bodies into model input or double-count reasoning tokens. Compare like configs;
   establish measured baselines and report regressions without inventing thresholds.
7. Apply task-scoped role profiles for code, Unreal, art/materials and review through
   supported native configuration. Keep required capabilities, max reasoning and
   default speed. Preserve global/owner config; don't merely create unused templates.
   Inspect the generated/effective native configuration and perform bounded native
   validation. Measure any claimed context gain; retain limits when data is absent.

## Implementation boundaries

One production writer. Executor owns Scripts/ContextBudget/, the existing context
guard, Tools/ContextBudget*, versioned hooks, relevant launcher integration and a
reproducible additive patch to the installed Multica source. Preserve the previously
dirty Multica source and its pinned local patch; stage new binaries separately.
Do not replace/restart the running executor's binary. Controller deploys verified
tooling after handoff and reviewer closure. All generated evidence goes under
`Saved/ContextBudget02/`. No source-controlled credentials or raw private prompts.

Controller owns this task/approval, AGENTS, ProjectState, policy documentation,
subsystem maps and task closure. Coordinate interface names before editing them.
Keep entrypoints within the existing 8 KiB budget. Keep actual integration small;
explicitly identify host-controlled boundaries rather than claiming universal
enforcement where only repository/Multica execution is instrumented.

## Verification and handoff

Use focused meaningful tests: staged-vs-worktree mismatch; positive/negative hook
cases with existing hooks preserved; pre-injection guard and cold resume; valid and
stale checkpoints; bounded output plus complete artifacts; real recorded native
usage including resumed events; generated role configuration and a bounded native
smoke. No Unreal build/gameplay test. One heavy build/test process at a time.

Executor supplies changed files, reproducible patch/build instructions, exact
candidate/evidence identities, tests/limits, safe deployment and rollback steps.
Primary reviewer inspects actual changes and reuses passing evidence. Controller
checks all requested outcomes, preserves owner files, installs/activates verified
integration, records actual native settings and makes the task-scoped local commit.

## Delivery

Implemented and installed; see [the handoff](../ContextBudget02Handoff.md) for the
controls, actual fresh-session measurements, deployment identities and boundaries.
[Primary technical review](../ContextBudget02Review.md) and
[subsystem map review](../ContextBudget02MapsReview.md) pass. MSQ-139 is the completed
read-only installed-runner acceptance probe, with automatic native usage/baseline
evidence. No gameplay scope was reopened.
