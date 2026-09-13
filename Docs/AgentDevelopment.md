# MeridianSquad agent development

## Constraints and decisions

- Ryzen 9800X3D, 32 GB RAM, RTX 5090. Project disk budget: at most 250 GB.
- Use only the existing $200/month Codex subscription. Paid APIs and additional
  cloud subscriptions are excluded. Available local models are allowed.
- Judge quality by accepted, verified tasks, including rework.
  Use Astra for difficult tasks and scripts for repeatable operations.
- Limit context, concurrent agents and heavy workloads.
  Allow only one agent to change the state of each open editor.
- Communicate with the user in Russian; write all project content in English,
  including documentation, code comments, names and commit messages.
- The owner selected Multica as the default route for project implementation.
  Direct chat handles requirements, dispatch, acceptance and administration.

## Stage 1: Codex and Unreal

Verified on this computer on September 13, 2026:

| Component | Status |
| --- | --- |
| Unreal Engine | 5.8.1, installed at `D:\UE_5.8` |
| Project | C++, `MeridianSquad`; one verified Blender-to-Unreal smoke-test mesh |
| Codex CLI | 0.153.4, signed in through ChatGPT |
| Blender | 5.2.1 LTS; installed community MCP 1.9.1 / addon 1.6, protocol 5 verified |
| Substance Painter | 12.1.4; project, fill layer, texture export and UE material verified through MCP |
| Substance Designer | 16.0.6; MCP connection not yet verified |
| Substance Sampler | 6.0.2, executable verified; MCP connection not yet verified |
| LM Studio | 0.4.24+1; no local model selected for the project yet |
| Multica | Local 0.4.43; read-only and complete asset tasks accepted; selected for implementation |
| PostgreSQL | Portable 17.11; Multica task database, loopback port 15432 |

The verified Sampler executable is
`C:\Program Files\Adobe\Adobe Substance 3D Sampler\Adobe Substance 3D Sampler.exe`.

The built-in `ModelContextProtocol` and `EditorToolset` plugins are enabled in
the `.uproject`. Project settings start MCP with the editor at
`127.0.0.1:8000/mcp`. The port binds to loopback. Tool discovery is enabled:
read detailed schemas on demand through `list_toolsets`, `describe_toolset`
and `call_tool`. `AllToolsets` is not needed yet. Epic MCP is experimental
in this version.

The client connection is configured in `.codex/config.toml` as `unreal_epic`.
Open this project in Unreal before starting a new Codex session.
Codex applies project settings only for a trusted directory.
An existing session may require an MCP/agent restart to load new tools.
The user's model and reasoning settings have not been changed.

The check on September 13, 2026 at 13:21 MSK passed:
`MeridianSquad.uproject` was running, port 8000 listened on `127.0.0.1`,
initialize negotiated protocol `2025-11-25`, and the initialized notification
returned HTTP 202. Three discovery tools and 19 toolsets were available.
Epic MCP returned `IsPIERunning=false` and the current level
`/Temp/Untitled_1`. The level was not saved and no assets were changed.

Repeatable check from the project root in PowerShell, without installing libraries:

```powershell
& 'D:\UE_5.8\Engine\Binaries\ThirdParty\Python3\Win64\python.exe' Scripts\check_unreal_mcp.py
```

Results are stored in `Saved/AgentSetup/McpProbe/`; `latest.json` contains
the summary and check time. The script checks HTTP and editor reads;
loading a newly configured MCP into the current Codex session requires
a separate agent/MCP restart. `codex.cmd mcp get unreal_epic` already reads
the configuration. The project directory is marked as trusted in the user's
Codex config; its previous version is saved in `C:\Users\Origa\.codex\backups\`.

After the Codex session restart on September 13, 2026, native Epic MCP tools
were available to the agent. Direct `mcp__unreal_epic__call_tool` calls returned
`IsPIERunning=false` and `get_current_level=/Temp/Untitled_1`, verifying stage 1
from the restarted Codex session.

## Stage 2: Blender to Unreal

The first transfer passed on September 13, 2026. Codex used the installed
community Blender MCP to create a dedicated `PipelineProbe` scene, exported FBX,
then used official Epic MCP to import and inspect the resulting Unreal assets.
The startup Blender scene and Unreal level were preserved.

- Source: `Assets/Source/SmokeTest/PipelineProbe.blend`.
- Unreal mesh: `/Game/Development/SmokeTest/SM_PipelineProbe`.
- Material: `/Game/Development/SmokeTest/M_PipelineProbe_Green`.
- Blender dimensions: 2 x 1 x 0.5 m; Unreal dimensions: 200 x 100 x 50 cm.
- Expected bounds in cm: min `(0, -50, 0)`, max `(200, 50, 50)`.
  Actual bounds passed a 0.01 cm tolerance, confirming the positive X direction
  from the tail pivot as well as scale. Both sides had 24 triangles.
- The Blender source has one UV layer. Unreal has one material slot; its green material was bound,
  saved and visually checked through an Unreal asset thumbnail.
- The saved Blender file contains only the probe scene, object and material.
- Detailed results and SHA-256 hashes: `Saved/AgentSetup/BlenderProbe/`.
  The three source/Unreal asset files total approximately 92 KiB.

Start Blender with the installed addon using PowerShell:

```powershell
& 'D:\blender\blender.exe' --python "$PWD\Scripts\start_blender_mcp.py"
```

The bootstrap requires the installed community addon and a GUI session. It binds
to `127.0.0.1:9876`, disables content telemetry and external asset/generation
integrations for the session, and does not save startup preferences.
The project's `DISABLE_TELEMETRY=true` override also disables minimal anonymous
usage collection after the Blender MCP server is next restarted; during the
current session, the opt-out tool only disabled prompts/code/images/scene data.

`Scripts/create_pipeline_probe.py` creates the probe on a clean run and refuses
to overwrite existing source/export files. It runs inside Blender. The FBX export
is generated under `Saved/Exports/SmokeTest/`, outside Git. Export settings are
`axis_forward=-Y`, `axis_up=Z`, `apply_unit_scale=True`, and
`apply_scale_options=FBX_SCALE_NONE`, with no animation. These settings were
validated against Epic's `StaticMeshTools.import_file` defaults. A new workflow
using different import settings must recheck bounds rather than assume parity.

## Stage 3: Painter to Unreal

The first Painter transfer passed on September 13, 2026. The existing probe mesh
now uses a material driven by exported 1024 x 1024 Base Color, DirectX Normal and
ORM textures. The Painter source project, texture files and Unreal assets are
saved. Channel values, texture settings, graph connections, shader compilation
and the rendered result were checked. Painter's project audit reported no issues.

See [Painter workflow](PainterWorkflow.md) for the pinned bridge installation,
repeatable operations, verification evidence and the scope of this probe.
The transfer used the MCP SDK over stdio. After the agent restart on
September 13, 2026, native `substance_painter` tools appeared in Codex and
`painter_status` confirmed a working connection to Painter 12.1.4 with a project open.

## Stage 4: Local Multica pilot

Multica 0.4.43 is running natively on Windows with a production web build,
Go API, PostgreSQL 17.11 and one Codex runtime. Existing ChatGPT authentication
was reused; the optional server LLM is disabled. No Docker or WSL was installed.

Issue `MSQ-1` passed on its first attempt using Astra, medium reasoning and
standard speed. It verified the project rules in the existing project directory.
Multica restored its temporary `AGENTS.md` changes; project and user Codex
configuration hashes were unchanged. Stop/start and result persistence passed.

See [Multica pilot](MulticaPilot.md) for operation, pinned dependencies, evidence,
token measurements and limits. The read-only pilot was followed by the complete
asset comparison recorded below.

## Stage 5: Complete asset task and orchestration comparison

On September 13, 2026, two independent Astra medium/standard workers created the
same specified crate through Blender, Painter and official Epic Unreal MCP.
Direct BenchA and Multica BenchB both passed independent acceptance on their
first submission: 864 triangles, eight closed components, valid UVs, two Painter
sets, six maps and nine saved UE assets. Multica issue MSQ-2 is accepted and done.

Direct execution took 449.25 seconds; Multica took 334 seconds. Multica used more
uncached input but fewer model responses, less cached input and less output.
One sequential pair cannot establish a general causal saving. Native output
includes reasoning; Multica 0.4.43 adds reasoning again in its output counter.
The large shared preparation/measurement cost is recorded separately and was
disproportionate to one simple prop. Reuse the existing scripts and validators.

See [the full comparison](Benchmarks/OrchestrationABComparison.md), including
previews, native usage, quality evidence, storage, limitations and public hashes.
The finite direct measurement client is not a replacement task dispatcher.

## Storage

Git and Git LFS are prepared for source files, configuration, decisions and
binary assets. Caches, builds, local IDE state and `Saved/` are excluded from Git.
A Git repository alone is not a backup. The `origin` remote is configured as
`https://github.com/NikolaevAnton-github/Meridian.git`, and the development branch
is `main`. Commit authorship is configured locally for this repository as
Anton Nikolaev, using the email supplied by the user. Git Credential Manager
uses the `NikolaevAnton-github` account. Check Git status and the upstream branch
for synchronization state. An off-device backup has not been configured.
The local Multica database has one same-disk dump recorded in its pilot guide.
Copies of existing files from before setup are stored in
`Saved/AgentSetup/20260913-131612/`.

The template Android File Server is disabled for the current Windows stage,
and its token has been removed from tracked configuration. When adding Android,
configure this service separately with local credentials.

Files are the first system layer, not a replacement for the planned database.
Structured metadata, checks and asset relationships are stored in a database;
large source files and outputs will remain in files referenced by paths and hashes.
PostgreSQL now stores Multica's tasks, runs and related application data.
The minimal asset metadata registry is implemented in the separate local
`meridian_assets` database and accepted as MSQ-3: 3 assets, 48 artifacts and
59 evidence-backed dependency records with explicit certainty. See
[asset registry usage](AssetRegistry.md) and [acceptance](AssetRegistryAcceptance.md).
No graph database is installed. Keep task state in Multica, asset metadata in
the registry, and large source files and outputs in files/Git LFS.

## Next stages

1. Completed: verify Blender MCP and transfer one simple asset to UE with the
   correct scale, orientation and material. Results are recorded in stage 2.
2. Completed: verify Painter MCP, create a project and fill layer, export textures
   and connect them in UE. Add Designer and Sampler as tasks require them.
3. Completed: deploy local Multica using existing Codex authentication, limit
   concurrency to one and verify one complete read-only task.
4. Completed: one full asset task through Multica and an equivalent direct run,
   both independently accepted. The owner selected Multica for implementation;
   reuse acceptance scripts and native metrics.
5. Completed and accepted: the
   [minimal asset registry](Tasks/AssetRegistry.md) through Multica. It reuses
   PostgreSQL, distinguishes verified dependencies from declarations, and
   registers saved files without regenerating assets.
6. Use 10–15 real tasks to measure first-pass acceptance, rework, time and
   available subscription usage metrics; use the results to tune model selection.

## Documentation

- [Epic: Unreal MCP](https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor)
- [Codex: MCP connection](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)
- [Multica: self-hosting](https://github.com/multica-ai/multica/blob/main/SELF_HOSTING.md)
