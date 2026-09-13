# Run through Epic MCP ProgrammaticToolset after importing the three textures.
import json

MATERIAL = {"refPath": "/Game/Development/SmokeTest/Painter/M_PipelineProbe_Painter.M_PipelineProbe_Painter"}

def expressions():
    return execute_tool("editor_toolset.toolsets.material.MaterialTools.get_expressions",
                        json.dumps({"material_or_function": MATERIAL}))["returnValue"]

def add_sample():
    return execute_tool("editor_toolset.toolsets.material.MaterialTools.add_expression",
                        json.dumps({"material_or_function": MATERIAL,
                                    "expression_class": {"refPath": "/Script/Engine.MaterialExpressionTextureSample"}}))["returnValue"]

def set_properties(instance, values):
    assert execute_tool("editor_toolset.toolsets.object.ObjectTools.set_properties",
                        json.dumps({"instance": instance, "values": json.dumps(values)}))["returnValue"]

def get_properties(instance, names):
    value = execute_tool("editor_toolset.toolsets.object.ObjectTools.get_properties",
                         json.dumps({"instance": instance, "properties": names}))["returnValue"]
    return json.loads(value)

def connect(expression, pin, property_name):
    execute_tool("editor_toolset.toolsets.material.MaterialTools.connect_to_output",
                 json.dumps({"expression": expression, "output_name": pin, "material_property": property_name}))

def input_source(property_name):
    return execute_tool("editor_toolset.toolsets.material.MaterialTools.get_property_input",
                        json.dumps({"material": MATERIAL, "material_property": property_name}))["returnValue"]

def layout():
    execute_tool("editor_toolset.toolsets.material.MaterialTools.layout_expressions",
                 json.dumps({"material_or_function": MATERIAL}))

def recompile():
    execute_tool("editor_toolset.toolsets.material.MaterialTools.recompile",
                 json.dumps({"material_or_function": MATERIAL}))

def assign():
    return execute_tool("editor_toolset.toolsets.static_mesh.StaticMeshTools.set_material",
                        json.dumps({"mesh": {"refPath": "/Game/Development/SmokeTest/SM_PipelineProbe.SM_PipelineProbe"},
                                    "slot_name": "M_PipelineProbe_Green", "material": MATERIAL}))["returnValue"]

def save(paths):
    return execute_tool("editor_toolset.toolsets.asset.AssetTools.save_assets",
                        json.dumps({"asset_paths": paths}))["returnValue"]

def run():
    nodes = expressions()
    if len(nodes) > 3 or any("MaterialExpressionTextureSample_" not in n["refPath"] for n in nodes):
        raise RuntimeError("Unexpected graph in the dedicated smoke-test material")
    while len(nodes) < 3:
        nodes.append(add_sample())
    nodes.sort(key=lambda n: n["refPath"])
    texture_settings = {}
    for node, suffix, sampler in zip(nodes, ["BaseColor", "Normal", "ORM"],
                                      ["SAMPLERTYPE_Color", "SAMPLERTYPE_Normal", "SAMPLERTYPE_Masks"]):
        texture = {"refPath": "/Game/Development/SmokeTest/Painter/T_PipelineProbe_" + suffix + ".T_PipelineProbe_" + suffix}
        set_properties(node, {"texture": texture, "samplerType": sampler, "constCoordinate": 0})
        texture_settings[suffix] = get_properties(texture, ["sRGB", "compressionSettings"])
    links = [(0, "RGB", "MP_BaseColor"), (1, "RGB", "MP_Normal"),
             (2, "R", "MP_AmbientOcclusion"), (2, "G", "MP_Roughness"), (2, "B", "MP_Metallic")]
    for node_index, pin, property_name in links:
        connect(nodes[node_index], pin, property_name)
    layout()
    recompile()
    actual_links = {}
    for node_index, pin, property_name in links:
        source = input_source(property_name)
        assert source["expression"]["refPath"] == nodes[node_index]["refPath"], property_name
        assert source["output_name"] == pin, property_name
        actual_links[property_name] = source
    assert assign()
    paths = ["/Game/Development/SmokeTest/Painter/M_PipelineProbe_Painter",
             "/Game/Development/SmokeTest/SM_PipelineProbe"]
    paths += ["/Game/Development/SmokeTest/Painter/T_PipelineProbe_" + suffix
              for suffix in ["BaseColor", "Normal", "ORM"]]
    assert save(paths)
    return {"passed": True, "material": MATERIAL, "texture_settings": texture_settings,
            "connections": actual_links, "saved_assets": paths}
