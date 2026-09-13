"""Create an isolated Blender scene and export a measurable static-mesh probe for Unreal."""

import json
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1]
source = root / "Assets/Source/SmokeTest/PipelineProbe.blend"
export = root / "Saved/Exports/SmokeTest/SM_PipelineProbe.fbx"
report_path = root / "Saved/AgentSetup/BlenderProbe/export.json"
for path in (source, export):
    if path.exists():
        raise FileExistsError(f"Refusing to replace an existing asset: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
if bpy.data.scenes.get("PipelineProbe") or bpy.data.objects.get("SM_PipelineProbe"):
    raise RuntimeError("The probe already exists in this Blender session")

scene = bpy.data.scenes.new("PipelineProbe")
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = "METERS"
bpy.context.window.scene = scene

# The tail pivot and distinct dimensions reveal unit, axis and sign errors on import.
outline = [(0, -0.3), (1.3, -0.3), (1.3, -0.5), (2, 0),
           (1.3, 0.5), (1.3, 0.3), (0, 0.3)]
count = len(outline)
vertices = [(x, y, z) for z in (0.0, 0.5) for x, y in outline]
faces = [tuple(reversed(range(count))), tuple(range(count, 2 * count))]
faces += [(i, (i + 1) % count, (i + 1) % count + count, i + count) for i in range(count)]
mesh = bpy.data.meshes.new("PipelineProbeMesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()
probe = bpy.data.objects.new("SM_PipelineProbe", mesh)
scene.collection.objects.link(probe)
probe.select_set(True)
bpy.context.view_layer.objects.active = probe
bpy.context.view_layer.update()

material = bpy.data.materials.new("M_PipelineProbe_Green")
material.use_nodes = True
material.diffuse_color = (0.08, 0.55, 0.12, 1.0)
shader = material.node_tree.nodes.get("Principled BSDF")
shader.inputs["Base Color"].default_value = material.diffuse_color
shader.inputs["Metallic"].default_value = 0.0
shader.inputs["Roughness"].default_value = 0.38
mesh.materials.append(material)

bpy.ops.object.mode_set(mode="EDIT")
try:
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(island_margin=0.04)
finally:
    bpy.ops.object.mode_set(mode="OBJECT")
mesh.calc_loop_triangles()

result = bpy.ops.export_scene.fbx(
    filepath=str(export), use_selection=True, object_types={"MESH"},
    global_scale=1.0, apply_unit_scale=True, apply_scale_options="FBX_SCALE_NONE",
    axis_forward="-Y", axis_up="Z", use_space_transform=True,
    bake_space_transform=False, use_mesh_modifiers=True, mesh_smooth_type="FACE",
    use_triangles=True, bake_anim=False, add_leaf_bones=False,
    path_mode="AUTO", embed_textures=False,
)
if "FINISHED" not in result:
    raise RuntimeError(f"FBX export failed: {result}")

# Write only this scene and its dependencies; preserve the user's startup scene.
bpy.data.libraries.write(str(source), {scene}, fake_user=True, compress=True)
report = {
    "blender_version": bpy.app.version_string,
    "source": str(source.relative_to(root)),
    "export": str(export.relative_to(root)),
    "object": probe.name,
    "dimensions_m": list(probe.dimensions),
    "scale": list(probe.scale),
    "vertices": len(mesh.vertices),
    "triangles": len(mesh.loop_triangles),
    "uv_layers": len(mesh.uv_layers),
    "material": material.name,
    "expected_unreal_bounds_cm": {"min": [0, -50, 0], "max": [200, 50, 50]},
    "export_settings": {"axis_forward": "-Y", "axis_up": "Z", "apply_scale_options": "FBX_SCALE_NONE"},
}
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
