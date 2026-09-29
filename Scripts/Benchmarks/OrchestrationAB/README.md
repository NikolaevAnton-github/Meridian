# Orchestration A/B measurement and acceptance

These are retained evidence readers and asset checks from the September 13, 2026
comparison. [DirectWorkflow01](../../../Docs/Tasks/DirectWorkflow01.md) retires
the native worker launcher and Multica execution. Do not rerun that experiment.
Generated evidence and private native Codex homes stay under
`Saved/AgentSetup/OrchestrationAB/`; source and accepted decisions stay in Git.

See `Docs/Benchmarks/OrchestrationABComparison.md` and the frozen task before use.
Both BenchA and BenchB already exist. Do not rerun their creation or overwrite
their sources. Earlier execution sources remain in Git history.

The saved `.blend` files are isolated libraries. In Blender, append Scene/BenchA
or Scene/BenchB from the corresponding file. Unreal assets are under
`/Game/Development/Benchmark/BenchA` and `/Game/Development/Benchmark/BenchB`.

## Read-only measurement

```powershell
& '.tools/painter-mcp/runtime/Scripts/python.exe' 'Scripts/Benchmarks/OrchestrationAB/summarize_runs.py'
& '.tools/painter-mcp/runtime/Scripts/python.exe' 'Scripts/Benchmarks/OrchestrationAB/snapshot_controller_usage.py'
```

The summary reads saved native logs and Multica task evidence, never credentials
or services. The controller snapshot uses the recorded root thread and user
instruction boundary; supply different arguments for a different experiment.
Native output already includes reasoning. The pinned Multica output counter
adds reasoning again; preserve that difference when reconciling its API.
Do not sum cumulative usage snapshots, or confuse file events with patch calls.

## Acceptance

Only run acceptance while no worker owns the DCC instances. The first command
starts a separate headless Blender, and the PNG checker depends on its UV report.
The Unreal checker inspects the running project and recompiles the two materials;
it records saved/dirty state before recompilation. It must have exclusive UE
ownership. Results go under `Saved/AgentSetup/OrchestrationAB/Independent/RUN_ID`.

```powershell
& 'D:\blender\blender.exe' --background --factory-startup --disable-autoexec --python-exit-code 1 --python 'Scripts/Benchmarks/OrchestrationAB/inspect_saved_asset.py' -- BenchA
& '.tools/painter-mcp/runtime/Scripts/python.exe' 'Scripts/Benchmarks/OrchestrationAB/verify_maps.py' BenchA
& '.tools/painter-mcp/runtime/Scripts/python.exe' 'Scripts/Benchmarks/OrchestrationAB/inspect_unreal.py' BenchA
```

Use BenchB for the second result. Passing acceptance was already performed for
both; repeat only after a relevant asset change or a new concern. The original
executed versions remain in Saved. Checked-in copies only relocate source paths
and preserve output paths; syntax, path configuration and read-only measurement
entry points were checked after relocation.

The former `run_direct.py` native worker launcher was removed by DirectWorkflow01.
Historical execution records remain under Saved; the source is available in Git
before that migration. Read-only measurement tools remain for interpreting those
records and do not authorize worker execution or renewed asset production.
