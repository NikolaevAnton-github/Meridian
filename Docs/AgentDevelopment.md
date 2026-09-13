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

## Stage 1: Codex and Unreal

Verified on this computer on September 13, 2026:

| Component | Status |
| --- | --- |
| Unreal Engine | 5.8.1, installed at `D:\UE_5.8` |
| Project | C++, `MeridianSquad`; one verified Blender-to-Unreal smoke-test mesh |
| Codex CLI | 0.153.4, signed in through ChatGPT |
| Blender | 5.2.1 LTS; installed community MCP 1.9.1 / addon 1.6, protocol 5 verified |
| Substance Painter | 12.1.4; MCP connection not yet verified |
| Substance Designer | 16.0.6; MCP connection not yet verified |
| Substance Sampler | 6.0.2, executable verified; MCP connection not yet verified |
| LM Studio | 0.4.24+1; no local model selected for the project yet |

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

## Storage

Git and Git LFS are prepared for source files, configuration, decisions and
binary assets. Caches, builds, local IDE state and `Saved/` are excluded from Git.
A Git repository alone is not a backup. The `origin` remote is configured as
`https://github.com/NikolaevAnton-github/Meridian.git`, and the development branch
is `main`. Commit authorship is configured locally for this repository as
Anton Nikolaev, using the email supplied by the user. Git Credential Manager
uses the `NikolaevAnton-github` account. Check Git status and the upstream branch
for synchronization state. Separate backups have not been configured.
Copies of existing files from before setup are stored in
`Saved/AgentSetup/20260913-131612/`.

The template Android File Server is disabled for the current Windows stage,
and its token has been removed from tracked configuration. When adding Android,
configure this service separately with local credentials.

Files are the first system layer, not a replacement for the planned database.
Structured metadata, checks and asset relationships will be stored in a database;
large source files and outputs will remain in files referenced by paths and hashes.
Approve the specific schema after the first task is verified from start to finish.
PostgreSQL/a graph database has not been installed for the project.

## Next stages

1. Completed: verify Blender MCP and transfer one simple asset to UE with the
   correct scale, orientation and material. Results are recorded in stage 2.
2. Verify Painter MCP on the installed version: open a test project,
   create a material/layer, export textures and connect them in UE.
   Add Designer and Sampler as tasks require them.
3. Deploy a self-hosted Multica pilot using existing Codex authentication.
   Verify one complete task and limit concurrency. Do not develop a custom
   task dispatcher before this pilot.
4. Add asset metadata and dependencies to a database. Extract relationships
   from tools; distinguish verified facts from model assumptions.
5. Use 10–15 real tasks to measure first-pass acceptance, rework, time and
   available subscription usage metrics; use the results to tune model selection.

## Documentation

- [Epic: Unreal MCP](https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor)
- [Codex: MCP connection](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)
- [Multica: self-hosting](https://github.com/multica-ai/multica/blob/main/SELF_HOSTING.md)
