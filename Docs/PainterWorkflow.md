# Painter to Unreal workflow

## Verified setup

Verified on September 13, 2026:

- Adobe Substance 3D Painter 12.1.4, reported Python API 0.3.5.
- Community [SubstancePainterMCP](https://github.com/elliezu/SubstancePainterMCP)
  1.0.0, source commit `e382927cc1a3ea7d4bd6e48d28403d339a4613df`.
- MCP Python SDK 1.30.0. Runtime dependencies are pinned in
  `Tools/Requirements/painter-mcp.txt`.
- The bridge and virtual environment occupy approximately 76.8 MiB under
  `.tools/painter-mcp/`, which is excluded from Git.
- Painter remote scripting listens on IPv6 loopback `::1:60041` on this machine.
  The client uses `localhost`; IPv4 `127.0.0.1` is not the observed listener.

The bridge sends commands to the local Painter process and requires no LLM API
key. The project enables 15 workflow tools; arbitrary Python execution remains
disabled in this bridge. Project, mesh and export roots are scoped in
`.codex/config.toml`. Codex must reload the MCP configuration before these tools
appear in a new session. This stage was verified through the MCP SDK over stdio
and native Epic MCP, including real application operations.

## Installation and startup

From the project root in PowerShell, on a machine with the same Unreal location:

```powershell
& 'D:\UE_5.8\Engine\Binaries\ThirdParty\Python3\Win64\python.exe' -m venv .tools\painter-mcp\runtime
& '.\.tools\painter-mcp\runtime\Scripts\python.exe' -m pip install --index-url https://pypi.org/simple -r Tools\Requirements\painter-mcp.txt
& 'C:\Program Files\Adobe\Adobe Substance 3D Painter\Adobe Substance 3D Painter.exe' --enable-remote-scripting
& '.\.tools\painter-mcp\runtime\Scripts\python.exe' Scripts\painter_mcp_client.py painter_status
```

The remote-scripting argument must be present when the Painter process starts.
The diagnostic client runs configured MCP tools without invoking a language
model. It saves full responses under `Saved/AgentSetup/PainterProbe/`; `--quiet`
prints only the report location. `schema` lists the tools enabled for this project.
If relocating the project or applications, update paths in `.codex/config.toml`.

## Probe assets and recipe

| Artifact | Location |
| --- | --- |
| Mesh source | `Assets/Source/SmokeTest/PipelineProbe.blend` |
| Generated FBX | `Saved/Exports/SmokeTest/SM_PipelineProbe.fbx` |
| Painter source | `Assets/Source/SmokeTest/PipelineProbe.spp` |
| Fill recipe | `Scripts/Recipes/PainterProbeFill.json` |
| Exported PNGs | `Assets/Textures/SmokeTest/Painter/` |
| UE textures and material | `/Game/Development/SmokeTest/Painter/` |
| UE mesh using the material | `/Game/Development/SmokeTest/SM_PipelineProbe` |

The Painter project uses DirectX normals, per-fragment tangent space, the default
workflow, and 1024-pixel texture sets. The incoming texture set retains its FBX
material-slot name, `M_PipelineProbe_Green`. The new fill is named
`Pipeline Validation Copper`, with sRGB color `(0.8, 0.28, 0.08)`, roughness `0.42`
and metallic `0.35`. The layer recipe is additive; rerunning it creates another
layer, so inspect the existing project first.

The export uses Painter's installed `Unreal Engine (Packed)` preset, PNG, 8-bit,
and `size_log2=10`. The exact preset URL used in this check is
`resource://starter_assets/Unreal Engine (Packed)?version=8339356058946582545.spexp`.
The preview lists an optional Emissive file, but the actual successful export
contains three maps: the project has no emission channel. Verification explicitly
checks those three required maps and permits only that optional omission.

## Acceptance evidence

After the September 13, 2026 agent restart, native Painter MCP tools loaded in
Codex. A direct `painter_status` call reported `connected=true`, Painter 12.1.4,
and an open project, completing the client configuration check.

| Map | UE settings | Material connection |
| --- | --- | --- |
| Base Color | sRGB on, `TC_Default`, Color sampler | RGB to Base Color |
| Normal | sRGB off, `TC_Normalmap`, Normal sampler | RGB to Normal |
| ORM | sRGB off, `TC_Masks`, Masks sampler | R to AO, G to Roughness, B to Metallic |

All three PNGs are 1024 x 1024. Sampled ORM channels were approximately
`(1.0, 0.41961, 0.34902)`, matching the recipe within 8-bit quantization.
The sampled base color was approximately `(0.8, 0.27843, 0.07843)`.
AO uses the neutral value 1 in this probe; high-poly baking is a later check.

`Scripts/connect_painter_material.py` runs through Epic's ProgrammaticToolset,
using registered tools to configure the dedicated material graph. It verifies
all five output connections, compiles the material, assigns it to the mesh and
saves the assets. Read ProgrammaticToolset's execution-environment instructions
before running the script. The material was also reviewed through a fresh UE
asset thumbnail. Painter's audit returned no issues, and the saved project
reported `needs_saving=false`.

Detailed reports: `Saved/AgentSetup/PainterProbe/verification.json`,
`unreal-material.json`, `texture-pixels.json` and individual MCP responses.
The verification manifest records SHA-256 hashes and sizes for the eight new
source/texture/UE files, totaling about 13.6 MiB. Painter lock files and local
tool dependencies are excluded from Git; source assets use Git LFS.
