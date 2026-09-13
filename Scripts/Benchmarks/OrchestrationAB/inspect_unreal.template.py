"""Independent registered-tool inspection, executed only after worker completion."""
import json

RUN_ID = "__RUN_ID__"
FOLDER = "/Game/Development/Benchmark/" + RUN_ID

def ref(name):
    return {"refPath": FOLDER + "/" + name + "." + name}

def bounds(mesh):
    return execute_tool("editor_toolset.toolsets.static_mesh.StaticMeshTools.get_bounds", json.dumps({"mesh": mesh}))["returnValue"]

def triangles(mesh):
    return execute_tool("editor_toolset.toolsets.static_mesh.StaticMeshTools.get_triangle_count", json.dumps({"mesh": mesh, "lod_index": 0}))["returnValue"]

def slots(mesh):
    return execute_tool("editor_toolset.toolsets.static_mesh.StaticMeshTools.get_material_slots", json.dumps({"mesh": mesh}))["returnValue"]

def assigned(mesh, slot):
    return execute_tool("editor_toolset.toolsets.static_mesh.StaticMeshTools.get_material", json.dumps({"mesh": mesh, "slot_name": slot}))["returnValue"]

def properties(instance, names):
    return json.loads(execute_tool("editor_toolset.toolsets.object.ObjectTools.get_properties", json.dumps({"instance": instance, "properties": names}))["returnValue"])

def texture_size(texture):
    return execute_tool("editor_toolset.toolsets.texture.TextureTools.get_size", json.dumps({"texture": texture}))["returnValue"]

def expressions(material):
    return execute_tool("editor_toolset.toolsets.material.MaterialTools.get_expressions", json.dumps({"material_or_function": material}))["returnValue"]

def connection(material, prop):
    return execute_tool("editor_toolset.toolsets.material.MaterialTools.get_property_input", json.dumps({"material": material, "material_property": prop}))["returnValue"]

def compile_material(material):
    execute_tool("editor_toolset.toolsets.material.MaterialTools.recompile", json.dumps({"material_or_function": material}))

def level():
    return execute_tool("editor_toolset.toolsets.scene.SceneTools.get_current_level", "{}")["returnValue"]

def pie():
    return execute_tool("EditorToolset.EditorAppToolset.IsPIERunning", "{}")["returnValue"]

def exists(path):
    return execute_tool("editor_toolset.toolsets.asset.AssetTools.exists", json.dumps({"path": path}))["returnValue"]

def is_dirty(path):
    return execute_tool("editor_toolset.toolsets.asset.AssetTools.is_dirty", json.dumps({"asset_path": path}))["returnValue"]

def run():
    failures = []
    mesh = ref("SM_" + RUN_ID + "_Crate")
    result = {"run_id": RUN_ID, "level": level(), "pie": pie()}
    expected_slots = ["M_" + RUN_ID + "_Body", "M_" + RUN_ID + "_Metal"]
    expected_names = ["SM_" + RUN_ID + "_Crate"] + expected_slots + [
        "T_" + RUN_ID + "_" + part + "_" + suffix
        for part in ["Body", "Metal"] for suffix in ["BaseColor", "Normal", "ORM"]]
    # Capture saved state before this checker requests any material recompile.
    result["assets"] = {name: exists(FOLDER + "/" + name) for name in expected_names}
    result["dirty_before_inspection"] = {
        name: is_dirty(FOLDER + "/" + name) for name in expected_names if result["assets"][name]}
    for name, dirty in result["dirty_before_inspection"].items():
        if dirty:
            failures.append("asset_dirty:" + name)
    actual_bounds = bounds(mesh)
    result["bounds_cm"] = actual_bounds
    for end, expected in [("min", [-60, -40, 0]), ("max", [60, 40, 90])]:
        for axis, value in zip(["x", "y", "z"], expected):
            if abs(actual_bounds[end][axis] - value) > 0.01:
                failures.append("bounds:" + end + ":" + axis)
    result["triangles"] = triangles(mesh)
    if not 0 < result["triangles"] <= 2000:
        failures.append("triangle_limit")
    result["slots"] = slots(mesh)
    if sorted(result["slots"]) != sorted(expected_slots):
        failures.append("material_slots")
    result["materials"] = {}
    for part in ["Body", "Metal"]:
        name = "M_" + RUN_ID + "_" + part
        material = ref(name)
        details = {"assignment": assigned(mesh, name) if name in result["slots"] else None,
                   "textures": {}, "connections": {}}
        if details["assignment"] != material:
            failures.append(part + ":assignment")
        if not result["assets"][name]:
            failures.append(part + ":missing_material")
            result["materials"][part] = details
            continue
        nodes = expressions(material)
        details["expression_count"] = len(nodes)
        for suffix, srgb, compression, sampler in [
            ("BaseColor", True, "TC_Default", "SAMPLERTYPE_Color"),
            ("Normal", False, "TC_Normalmap", "SAMPLERTYPE_Normal"),
            ("ORM", False, "TC_Masks", "SAMPLERTYPE_Masks"),
        ]:
            texture = ref("T_" + RUN_ID + "_" + part + "_" + suffix)
            if not result["assets"]["T_" + RUN_ID + "_" + part + "_" + suffix]:
                details["textures"][suffix] = {"exists": False}
                failures.append(part + ":missing_texture:" + suffix)
                continue
            settings = properties(texture, ["sRGB", "compressionSettings"])
            size = texture_size(texture)
            details["textures"][suffix] = {"settings": settings, "size": size}
            if settings.get("sRGB") != srgb or settings.get("compressionSettings") != compression or size != {"x": 1024, "y": 1024}:
                failures.append(part + ":texture:" + suffix)
            links = {"BaseColor": [("MP_BaseColor", "RGB")], "Normal": [("MP_Normal", "RGB")],
                     "ORM": [("MP_AmbientOcclusion", "R"), ("MP_Roughness", "G"), ("MP_Metallic", "B")]}[suffix]
            for prop, pin in links:
                linked = connection(material, prop)
                if not linked.get("expression"):
                    details["connections"][prop] = {"source": linked, "sample": None}
                    failures.append(part + ":disconnected:" + prop)
                    continue
                try:
                    sample = properties(linked["expression"], ["texture", "samplerType", "constCoordinate"])
                except Exception as error:
                    details["connections"][prop] = {"source": linked, "inspection_error": str(error)}
                    failures.append(part + ":unsupported_connection:" + prop)
                    continue
                details["connections"][prop] = {"source": linked, "sample": sample}
                if linked["output_name"] != pin or sample.get("texture") != texture or sample.get("samplerType") != sampler or sample.get("constCoordinate") != 0:
                    failures.append(part + ":connection:" + prop)
        try:
            compile_material(material)
            details["compilation"] = "passed"
        except Exception as error:
            details["compilation"] = "failed"
            details["compilation_error"] = str(error)
            failures.append(part + ":compilation")
        result["materials"][part] = details
    if not all(result["assets"].values()):
        failures.append("missing_asset")
    if result["level"] != "/Temp/Untitled_1" or result["pie"]:
        failures.append("editor_state_changed")
    result["failures"] = failures
    result["passed"] = not failures
    return result
