# Asset task: Multica versus direct Codex

This is the common task specification for two fresh Codex runs. The controller
supplies `RUN_ID` as `BenchA` or `BenchB`; replace that placeholder everywhere.
Create the asset yourself using the connected Blender, Painter and official Epic
Unreal MCP tools. You own all three editor instances for this run. Other runs'
outputs, scripts and reports are forbidden inputs. Do not delegate or run another
language model. Write all reports and project content in English.

## Deliverable

Build a small beveled industrial crate from eight closed box components, joined
into one static mesh. Coordinates and dimensions below are in meters. Touching
or intersecting components are allowed; do not use Boolean operations.

| Part | Count | Dimensions X/Y/Z | Center X/Y/Z | Material |
| --- | --- | --- | --- | --- |
| Body | 1 | 1.12 / 0.72 / 0.70 | 0 / 0 / 0.45 | Body |
| Lid | 1 | 1.20 / 0.80 / 0.10 | 0 / 0 / 0.85 | Body |
| Corner posts | 4 | 0.08 / 0.08 / 0.72 | +/-0.56 / +/-0.36 / 0.44 | Metal |
| Feet | 2 | 1.12 / 0.12 / 0.08 | 0 / +/-0.26 / 0.04 | Metal |

Use a geometric bevel of 0.01 m and two segments on each component; apply the
bevels and object transforms before export. Preserve the dimensions in the table.
Use coherent outward normals and no zero-area faces. Keep eight connected mesh
components and at most 2,000 triangles. The final pivot is `(0,0,0)`, at the center
of the base. Expected overall bounds are `(-0.60,-0.40,0)` to `(0.60,0.40,0.90)` m.
Use exactly one UV layer, finite coordinates in `[0,1]`, nonzero UV triangle areas,
and non-overlapping UV interiors within each material. There are exactly two
material slots named `M_RUN_ID_Body` and `M_RUN_ID_Metal`.

Create a dedicated Blender scene `RUN_ID` and object `SM_RUN_ID_Crate`.
Do not delete or modify the pre-existing scenes or objects. Save a compressed
`.blend` containing only the new scene and its dependencies. Export the selected
mesh as triangulated FBX with no animation or embedded textures.

## Painter and Unreal

Create a NEW Painter project from your FBX, with DirectX normals, per-fragment
tangent space, default workflow and 1024-pixel texture sets. The baseline Painter
project is saved and clean. Replacing the open project is authorized for this
benchmark; do not overwrite the baseline or another run's source file. Use the
typed project and recipe tools, inspecting their plans before mutations.
The installed bridge requires a backup even for a clean open project. Put that
temporary copy at your run's source folder `BaselineBackup.spp` and pass
`replace_current=true`. The controller will archive this generated backup.

Create one fill layer per texture set:

| Set | Base Color (sRGB) | Roughness | Metallic |
| --- | --- | --- | --- |
| Body | 0.10 / 0.28 / 0.40 | 0.55 | 0.0 |
| Metal | 0.35 / 0.37 / 0.40 | 0.30 | 1.0 |

Export PNG, 8-bit, 1024x1024 using the installed `Unreal Engine (Packed)` preset.
Require Base Color, DirectX Normal and Occlusion/Roughness/Metallic for each set:
six maps total. No high-poly baking, procedural wear, external generation or asset
downloads are required. AO is the neutral value 1; the tangent normal is flat.
Save your Painter project, and check its audit result.

Import your FBX into Unreal with existing scale/orientation conventions and no
automatic material or texture import. Create/import six textures and two material
assets, assign them to the correct static-mesh slots and save all nine UE assets.
Use each material's actual Painter outputs: Base Color RGB -> Base Color; Normal
RGB -> Normal; packed R -> Ambient Occlusion, G -> Roughness, B -> Metallic.
Use sRGB on and default compression/color sampler for Base Color, sRGB off and
normal-map compression/normal sampler for Normal, and sRGB off with masks
compression/masks sampler for packed ORM. Recompile and inspect connections.
Do not change the current level, place actors, start PIE, or alter other assets.

## Paths and names

- Blender: `Assets/Source/SmokeTest/OrchestrationAB/RUN_ID/Crate.blend`.
- Painter: `Assets/Source/SmokeTest/OrchestrationAB/RUN_ID/Crate.spp`.
- Generated FBX: `Saved/Exports/SmokeTest/OrchestrationAB/RUN_ID/SM_RUN_ID_Crate.fbx`.
- Exported maps: `Assets/Textures/SmokeTest/Painter/OrchestrationAB/RUN_ID/`.
- UE folder: `/Game/Development/Benchmark/RUN_ID`.
- UE mesh: `SM_RUN_ID_Crate`; materials: `M_RUN_ID_Body`, `M_RUN_ID_Metal`.
- UE textures: `T_RUN_ID_Body_BaseColor`, `T_RUN_ID_Body_Normal`,
  `T_RUN_ID_Body_ORM`, and the three corresponding `Metal` names.
- Your working scripts and full logs: `Saved/AgentSetup/OrchestrationAB/RUN_ID/`.
- Your final machine-readable checks: that run folder's `worker-report.json`.

Writes are limited to these new run-specific paths and editor objects/assets.
Do not edit AGENTS, configuration, shared scripts, documentation or Git state.
Do not read any other benchmark run, including its scripts and material assets.
Existing smoke-test documentation and recipes listed below are allowed references.
Do not repeatedly poll asynchronous jobs: use returned state/timing guidance.
After two equivalent failures, change the diagnostic approach; record every failure.

## Acceptance and reporting

Verify saved source/export files; mesh dimensions, pivot, applied transforms,
triangle count, UVs and two slots; Painter's two sets and six maps; UE bounds
`(-60,-40,0)` to `(60,40,90)` cm within 0.01 cm, matching triangle count,
texture dimensions/settings, five material connections per material and slot
assignments. Check and save an Unreal asset thumbnail if practical. A controller
will independently inspect the actual files and editor assets after the run.

Return a concise final report with completed paths, measured checks, errors and
any acceptance criteria you could not verify. Do not claim an unchecked criterion
passed. Include an ordered stage list and number of failed tool calls in
`worker-report.json`. Stop when the deliverable and checks are complete; no polish
or additional tasks. The controller handles issue acceptance and Git commits.

## Shared references and tool hints

- `Scripts/create_pipeline_probe.py`: tested Blender FBX scale settings and isolated save.
- `Docs/PainterWorkflow.md` and `Scripts/Recipes/PainterProbeFill.json`: typed Painter recipe/export.
- `Scripts/connect_painter_material.py`: registered Epic material/object tool calls; adapt paths and slots.
- `Scripts/check_unreal_mcp.py`: read-only endpoint/project diagnostic if needed.

Discover current schemas through the MCP tools. Epic ProgrammaticToolset can batch
registered calls; read its execution-environment instructions and the output
schemas of tools used. It does not permit importing the `unreal` module. In a
Python shell command on this Windows system, prefer a UTF-8 script file over
complex `python -c` quoting. Available interpreter:
`D:\UE_5.8\Engine\Binaries\ThirdParty\Python3\Win64\python.exe`.
