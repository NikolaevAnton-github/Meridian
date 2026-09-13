# Orchestration A/B measurement and acceptance

This is the finite harness for the September 13, 2026 comparison. It is not a
task dispatcher. Multica owns scheduling, issue state and execution history.
Generated evidence and private native Codex homes stay under
`Saved/AgentSetup/OrchestrationAB/`; source and accepted decisions stay in Git.

See `Docs/Benchmarks/OrchestrationABComparison.md` and the frozen task before use.
Both BenchA and BenchB already exist. Do not rerun their creation or overwrite
their sources. The direct client refuses an existing output directory or home.

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

`run_direct.py` is a one-turn native app-server measurement client pinned to the
installed Codex version. It uses ChatGPT login, records usage and native logs,
rejects unexpected interactive requests, and does not retry or dispatch another
task. Its common CLI arguments must match the benchmark Multica agent. The
source includes no authentication values. Setup/controller actions and shared
verification costs must be accounted separately from worker task tokens.
