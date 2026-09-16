"""Fresh native opaque graphs and source imports; no historical material parents.

Each graph is created independently with native expressions and editable Custom
HLSL for centimetre-based triplanar projection. No project/engine material functions
are required. All imports are the canonical newly generated source PNGs.
"""
import json
from pathlib import Path
import unreal as u
from architecture01_lightstudy import props
from materialintegration01_unreal import ROOT, OUT, ASSETS, guard, write

SRC = ROOT / 'Assets/Source/OpeningLobby/MaterialIntegration01'
ROLES = json.loads((SRC / 'recipe.json').read_text())['roles']
LIB = u.MaterialEditingLibrary

PROJECTION = '''
float3 p = WorldCm / TileCm;
float3 w = pow(abs(SurfaceNormal), 16.0);
w /= max(w.x + w.y + w.z, 0.0001);
float3 sx = Texture2DSample(SurfaceTex, SurfaceTexSampler, p.yz).rgb;
float3 sy = Texture2DSample(SurfaceTex, SurfaceTexSampler, p.xz).rgb;
float3 sz = Texture2DSample(SurfaceTex, SurfaceTexSampler, p.xy).rgb;
return sx * w.x + sy * w.y + sz * w.z;
'''
NORMAL = '''
float3 p = WorldCm / TileCm;
float3 w = pow(abs(SurfaceNormal), 16.0);
w /= max(w.x + w.y + w.z, 0.0001);
// The new source's DirectX RG slopes are explicitly decoded from BC5.
float2 sx = Texture2DSample(SurfaceTex, SurfaceTexSampler, p.yz).rg * 2.0 - 1.0;
float2 sy = Texture2DSample(SurfaceTex, SurfaceTexSampler, p.xz).rg * 2.0 - 1.0;
float2 sz = Texture2DSample(SurfaceTex, SurfaceTexSampler, p.xy).rg * 2.0 - 1.0;
float3 gradient = float3(0, sx.x, sx.y) * w.x
                + float3(sy.x, 0, sy.y) * w.y
                + float3(sz.x, sz.y, 0) * w.z;
// Remove the interpolated normal component at bevels before normalization.
gradient -= SurfaceNormal * dot(gradient, SurfaceNormal);
return normalize(SurfaceNormal + gradient);
'''


def create(role):
    guard(True)
    assert role in ROLES
    recipe = ROLES[role]
    material_path = ASSETS + '/Materials/M_MI01_' + role
    incomplete = u.EditorAssetLibrary.does_asset_exist(material_path)
    assert not (OUT / 'Authorship' / (role + '.json')).exists(), 'Completed graph already authored'
    assert not incomplete or role == 'Stone', 'Only the documented initial Stone pin repair may resume'
    asset_tools = u.AssetToolsHelpers.get_asset_tools()
    sources = json.loads((SRC / 'provenance.json').read_text())
    record = next(r for r in sources['roles'] if r['role'] == role)
    imported = []
    for channel, entry in record['exports'].items():
        p = ROOT / entry['path']
        destination = ASSETS + '/Textures/' + p.stem
        exists = u.EditorAssetLibrary.does_asset_exist(destination)
        assert not exists or incomplete, destination
        task = u.AssetImportTask()
        task.set_editor_property('filename', str(p))
        task.set_editor_property('destination_path', ASSETS + '/Textures')
        task.set_editor_property('destination_name', p.stem)
        task.set_editor_property('automated', True)
        task.set_editor_property('replace_existing', False)
        task.set_editor_property('save', False)
        if not exists:
            asset_tools.import_asset_tasks([task])
        tex = u.load_asset(destination)
        assert isinstance(tex, u.Texture2D), task.get_editor_property('imported_object_paths')
        tex.set_editor_property('srgb', channel == 'BaseColor')
        tex.set_editor_property('compression_settings', {'BaseColor': u.TextureCompressionSettings.TC_DEFAULT,
                                'ORM': u.TextureCompressionSettings.TC_MASKS, 'Normal': u.TextureCompressionSettings.TC_NORMALMAP}[channel])
        tex.set_editor_property('flip_green_channel', False)
        tex.set_editor_property('mip_gen_settings', u.TextureMipGenSettings.TMGS_FROM_TEXTURE_GROUP)
        tex.set_editor_property('never_stream', False)
        tex.set_editor_property('address_x', u.TextureAddress.TA_WRAP)
        tex.set_editor_property('address_y', u.TextureAddress.TA_WRAP)
        assert u.EditorAssetLibrary.save_loaded_asset(tex, only_if_is_dirty=False)
        imported.append(dict(channel=channel, asset=tex.get_path_name(), source=entry))
    m = u.load_asset(material_path) if incomplete else asset_tools.create_asset('M_MI01_' + role, ASSETS + '/Materials', u.Material, u.MaterialFactoryNew())
    assert m
    if incomplete:
        write('technical-pin-repair', dict(role=role, cause='ComponentMask input is NAME_None, not Input',
                                          discarded_task_owned_incomplete_nodes=len(LIB.get_material_expressions(m)), visual_trial=False))
        # UE 5.8's DeleteAll iterates the collection it mutates; snapshot it first.
        for expression in list(LIB.get_material_expressions(m)):
            LIB.delete_material_expression(m, expression)
    m.set_editor_property('blend_mode', u.BlendMode.BLEND_OPAQUE)
    m.set_editor_property('two_sided', False)
    m.set_editor_property('tangent_space_normal', False)
    nodes = []
    def node(cls, x, y, **values):
        obj = LIB.create_material_expression(m, cls, x, y)
        for key, value in values.items():
            obj.set_editor_property(key, value)
        nodes.append(obj)
        return obj
    def connect(a, b, pin, out=''):
        assert LIB.connect_material_expressions(a, out, b, pin), (a.get_name(), b.get_name(), pin)
    def output(obj, name, channel=''):
        assert LIB.connect_material_property(obj, channel, getattr(u.MaterialProperty, 'MP_' + name))
    position = node(u.MaterialExpressionWorldPosition, -1200, -200, desc='Absolute world position in centimetres; no displacement')
    surface = node(u.MaterialExpressionVertexNormalWS, -1200, -50, desc='Unperturbed world-space surface normal')
    scale = node(u.MaterialExpressionScalarParameter, -1200, 120, parameter_name='TileSizeCm',
                 default_value=float(recipe['projection_cm']), desc='Identical physical projection scale on all three axes')
    sampled = {}
    for i, channel in enumerate(['BaseColor', 'ORM', 'Normal']):
        tex = u.load_asset(ASSETS + '/Textures/T_MI01_' + role + '_' + channel)
        obj = node(u.MaterialExpressionTextureObject, -1200, 350 + i * 230, texture=tex,
                   sampler_type={'BaseColor':u.MaterialSamplerType.SAMPLERTYPE_COLOR,
                                 'ORM':u.MaterialSamplerType.SAMPLERTYPE_MASKS,
                                 'Normal':u.MaterialSamplerType.SAMPLERTYPE_NORMAL}[channel],
                   desc='Fresh01 canonical ' + role + ' ' + channel)
        inputs = []
        for name in ['SurfaceTex', 'WorldCm', 'SurfaceNormal', 'TileCm']:
            ci = u.CustomInput()
            ci.set_editor_property('input_name', name)
            inputs.append(ci)
        custom = node(u.MaterialExpressionCustom, -650, i * 340,
                      code=NORMAL if channel == 'Normal' else PROJECTION,
                      output_type=u.CustomMaterialOutputType.CMOT_FLOAT3, inputs=inputs,
                      description=role + ' fresh world projection / ' + channel,
                      desc='Editable newly authored projection; no material-function dependency')
        for a, name in [(obj,'SurfaceTex'), (position,'WorldCm'), (surface,'SurfaceNormal'), (scale,'TileCm')]:
            connect(a, custom, name)
        sampled[channel] = custom
    output(sampled['BaseColor'], 'BASE_COLOR')
    output(sampled['Normal'], 'NORMAL')
    for i, (channel, property_name) in enumerate([('r','AMBIENT_OCCLUSION'), ('g','ROUGHNESS'), ('b','METALLIC')]):
        mask = node(u.MaterialExpressionComponentMask, -170, 230 + i * 110, r=channel=='r', g=channel=='g', b=channel=='b', a=False)
        connect(sampled['ORM'], mask, '')
        output(mask, property_name)
    spec = node(u.MaterialExpressionScalarParameter, -170, 650, parameter_name='DielectricSpecular',
                default_value=float(recipe['specular']), desc='Restrained dielectric response; no clearcoat')
    output(spec, 'SPECULAR')
    LIB.recompile_material(m)
    assert u.EditorAssetLibrary.save_loaded_asset(m, only_if_is_dirty=False)
    result = dict(role=role, native_asset=m.get_path_name(), imported=imported,
                  graph_nodes=[n.get_path_name() for n in nodes], recipe=recipe,
                  source='Scripts/OpeningLobby/materialintegration01_materials.py',
                  parent=None, material_functions=[], copied_assets=[], old_opaque_dependencies=[],
                  normal_space='World; DirectX BC5 RG decoded, reoriented by each physical projection plane',
                  displacement=False, opacity='Opaque')
    write('Authorship/' + role, result)
    return dict(role=role, textures=len(imported), expressions=len(nodes), material=m.get_path_name())


def audit():
    guard(True, clean=True)
    schemas, records = {}, {}
    registry = u.AssetRegistryHelpers.get_asset_registry()
    options = u.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True,
                                              include_searchable_names=True, include_soft_management_references=True,
                                              include_hard_management_references=True)
    for role, recipe in ROLES.items():
        m = u.load_asset(ASSETS + '/Materials/M_MI01_' + role)
        nodes = LIB.get_material_expressions(m)
        connected, inputs = set(), {}
        def visit(n):
            if n is None or n.get_path_name() in connected:
                return
            connected.add(n.get_path_name())
            for child in LIB.get_inputs_for_material_expression(m, n):
                visit(child)
        for key in ['BASE_COLOR','ROUGHNESS','METALLIC','NORMAL','SPECULAR','AMBIENT_OCCLUSION','WORLD_POSITION_OFFSET','EMISSIVE_COLOR','OPACITY']:
            n = LIB.get_material_property_input_node(m, getattr(u.MaterialProperty,'MP_'+key))
            inputs[key] = n.get_path_name() if n else None
            visit(n)
        assert set(n.get_path_name() for n in nodes) == connected, role
        assert len(nodes) == 13, (role, len(nodes))
        textures = list(LIB.get_used_textures(m))
        assert len(textures) == 3 and all(t.get_path_name().startswith(ASSETS + '/') for t in textures)
        dependencies = [str(d) for d in registry.get_dependencies(m.get_outermost().get_name(), options)]
        assert not [d for d in dependencies if d.startswith('/Game/') and not d.startswith(ASSETS + '/')], dependencies
        assert not any(isinstance(n, u.MaterialExpressionMaterialFunctionCall) for n in nodes)
        stats = LIB.get_statistics(m)
        records[role] = dict(material=props(m,schemas), nodes={n.get_path_name():props(n,schemas) for n in nodes}, inputs=inputs,
                            dependencies=dependencies, textures={t.get_path_name():props(t,schemas) for t in textures},
                            statistics={k:getattr(stats,k) for k in ['num_pixel_shader_instructions','num_vertex_shader_instructions','num_samplers']},
                            all_nodes_connected=True, new_opaque_dependencies_only=True, physical_scale_cm=recipe['projection_cm'])
    write('native-material-audit', records)
    write('native-material-schemas', schemas)
    return {role:dict(expressions=len(r['nodes']), dependencies=r['dependencies'], statistics=r['statistics']) for role,r in records.items()}


def repair_unused():
    guard(True)
    m = u.load_asset(ASSETS + '/Materials/M_MI01_Stone')
    authored = set(json.loads((OUT / 'Authorship/Stone.json').read_text())['graph_nodes'])
    removed = []
    for node in list(LIB.get_material_expressions(m)):
        if node.get_path_name() not in authored:
            removed.append(node.get_path_name())
            LIB.delete_material_expression(m, node)
    assert len(removed) == 4
    assert set(n.get_path_name() for n in LIB.get_material_expressions(m)) == authored
    LIB.recompile_material(m)
    assert u.EditorAssetLibrary.save_loaded_asset(m, only_if_is_dirty=False)
    return write('technical-unused-node-repair', dict(removed=removed, reason='Native DeleteAllMaterialExpressions mutated its iteration collection', visual_trial=False))
