# Standalone context helpers

[DirectWorkflow01](../../Docs/Tasks/DirectWorkflow01.md) retires the Multica worker
integration. There is no automatic Git hook, daemon gate, task brief/checkpoint,
role profile or required native usage instrumentation. Historical MSQ-138 evidence
stays under `Saved/ContextBudget02/` and in Git history.

Run the repository check after editing project entrypoints or policies:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/check_context_budget.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/check_context_budget.ps1 -Mode Staged -RelevantOnly
```

An existing Python 3.11+ is used; set `CONTEXT_BUDGET_PYTHON` if discovery fails.
No packages, services, credentials or task records are needed. The check validates
repository byte budgets, direct local navigation and immutable archive hashes.
Staged mode reads index blobs. Old generated runtime instruction blocks are
rejected in both modes. Existing protected manifest values cannot be rebaselined.

Optional output helpers, from a PowerShell session with process-local execution
policy allowing the existing `python.ps1` helper:

```powershell
. Scripts/ContextBudget/python.ps1
$contextPython = Get-ContextPython
& $contextPython Scripts/ContextBudget/context_budget.py run --label source-check --timeout 120 -- git diff --check
& $contextPython Scripts/ContextBudget/context_budget.py preview Saved/example.log --start 1 --lines 20 --bytes 2048
& $contextPython -m unittest discover -s Scripts/ContextBudget -p test_context_budget.py
```

`run` saves stdout/stderr separately under Saved, reports artifact paths and returns
the command exit code (124 on timeout); it never invokes a shell implicitly.
`preview` accepts at most 80 lines / 8192 bytes. Do not capture credentials or use
`run` to launch detached background services. Ordinary shell use does not require
either helper. Repository byte measurements are not native model token counts.
