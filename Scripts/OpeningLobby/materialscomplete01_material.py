"""Native Painter ceiling import and dedicated Substrate optical graphs."""
import types,json
import unreal as u
from materialscomplete01_unreal import ROOT,OUT,ASSETS,guard,write
from architecture01_lightstudy import props
LIB=u.MaterialEditingLibrary
def adapter():
    p=ROOT/'Scripts/OpeningLobby/painterstone01_material.py'
    s=p.read_text().replace('from painterstone01_unreal import','from materialscomplete01_unreal import')
    s=s.replace('PainterStone01','MaterialsComplete01').replace('default_value=240','default_value=120').replace('physical_coverage_cm=240','physical_coverage_cm=120')
    s=s.replace('240 cm matches the native Painter authoring plane','120 cm coverage for fine mineral plaster')
    m=types.ModuleType('ceiling_graph');exec(compile(s,str(p),'exec'),m.__dict__);return m
def ceiling():return adapter().material()
def reload_graphs():
    guard(True,True)
    assets=[u.load_asset(p) for p in u.EditorAssetLibrary.list_assets(ASSETS,recursive=True,include_folder=False)]
    paths=[a.get_path_name() for a in assets]
    result=u.EditorLoadingAndSavingUtils.reload_packages([a.get_outermost() for a in assets])
    return write('graphs-reloaded',dict(paths=paths,result=str(result),method='EditorLoadingAndSavingUtils.reload_packages: native disk package reload',state=guard(True,True)))
def glass_revision():
    guard(True,True)
    assert not (OUT/'glass-QARevision01.json').exists()
    records=[]
    for role in ['Fixed','Leaf']:
        m=u.load_asset(ASSETS+'/Materials/M_MC01_Glass'+role)
        n=next(n for n in LIB.get_material_expressions(m) if isinstance(n,u.MaterialExpressionVectorParameter) and str(n.get_editor_property('parameter_name'))=='Transmission')
        previous=str(n.get_editor_property('default_value'))
        v=.9 if role=='Fixed' else .94
        n.set_editor_property('default_value',u.LinearColor(v,v,v,1))
        LIB.recompile_material(m);assert u.EditorAssetLibrary.save_loaded_asset(m)
        records.append(dict(role=role,previous=previous,neutral_transmission=[v]*3))
    return write('glass-QARevision01',dict(revision=1,reason='Remove the faint mauve cast observed on initial fixed-pane reflection/scattering by using spectrally neutral transmission. Preserve roughness distinction and real volume optics.',records=records))
def capabilities():
    schema={}
    for n in ['Material','MaterialExpressionSubstrateSlabBSDF','MaterialExpressionSubstrateTransmittanceToMFP']:
        schema[n]=json.loads(u.ToolsetLibrary.list_struct_properties(getattr(u,n).static_class()))
    write('glass-capabilities',dict(schemas=schema,blend_modes=dir(u.BlendMode),subsurface_types=dir(u.MaterialSubSurfaceType),substrate=u.SystemLibrary.get_console_variable_int_value('r.Substrate')))
    return dict(substrate=u.SystemLibrary.get_console_variable_int_value('r.Substrate'),classes=list(schema))
RECIPES={'Fixed':dict(albedo=[.45]*3,transmission=[.90,.91,.91],roughness=.32),'Leaf':dict(albedo=[.04]*3,transmission=[.92,.94,.94],roughness=.09)}
def glass():
    guard(True,True)
    result={}
    for role,r in RECIPES.items():
        name='M_MC01_Glass'+role;path=ASSETS+'/Materials/'+name
        assert not u.EditorAssetLibrary.does_asset_exist(path)
        m=u.AssetToolsHelpers.get_asset_tools().create_asset(name,ASSETS+'/Materials',u.Material,u.MaterialFactoryNew());assert m
        m.set_editor_property('blend_mode',u.BlendMode.BLEND_TRANSLUCENT_COLORED_TRANSMITTANCE)
        m.set_editor_property('two_sided',False);m.set_editor_property('is_thin_surface',True)
        m.set_editor_property('screen_space_reflections',True)
        m.set_editor_property('translucency_lighting_mode',u.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
        for n in list(LIB.get_material_expressions(m)):LIB.delete_material_expression(m,n)
        slab=LIB.create_material_expression(m,u.MaterialExpressionSubstrateSlabBSDF)
        slab.set_editor_property('sub_surface_type',u.MaterialSubSurfaceType.MSS_SIMPLE_VOLUME)
        mfp=LIB.create_material_expression(m,u.MaterialExpressionSubstrateTransmittanceToMFP)
        for param,value,target,pin in [('ScatteringAlbedo',r['albedo'],slab,'Diffuse Albedo'),('F0',[.04]*3,slab,'F0'),('SurfaceRoughness',r['roughness'],slab,'Roughness'),('Transmission',r['transmission'],mfp,'TransmittanceColor')]:
            vector=isinstance(value,list);n=LIB.create_material_expression(m,u.MaterialExpressionVectorParameter if vector else u.MaterialExpressionScalarParameter)
            n.set_editor_property('parameter_name',param);n.set_editor_property('default_value',u.LinearColor(*value,1) if vector else value)
            assert LIB.connect_material_expressions(n,'',target,pin)
        assert LIB.connect_material_expressions(mfp,'MFP',slab,'SSS MFP')
        assert LIB.connect_material_property(slab,'',u.MaterialProperty.MP_FRONT_MATERIAL)
        LIB.layout_material_expressions(m);LIB.recompile_material(m)
        assert u.EditorAssetLibrary.save_loaded_asset(m)
        result[role]=dict(path=m.get_path_name(),recipe=r,F0=.04,emission_connected=False)
    return write('glass-authorship',result)
def audit():
    opaque=adapter().audit();schemas={};records={}
    for role in RECIPES:
        m=u.load_asset(ASSETS+'/Materials/M_MC01_Glass'+role)
        nodes=LIB.get_material_expressions(m);seen=set()
        def visit(n):
            if not n or n.get_path_name() in seen:return
            seen.add(n.get_path_name())
            for c in LIB.get_inputs_for_material_expression(m,n):visit(c)
        front=LIB.get_material_property_input_node(m,u.MaterialProperty.MP_FRONT_MATERIAL);visit(front)
        assert isinstance(front,u.MaterialExpressionSubstrateSlabBSDF)
        assert seen=={n.get_path_name() for n in nodes} and len(nodes)==6
        assert not list(LIB.get_used_textures(m))
        opts=u.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True)
        deps=[str(d) for d in (u.AssetRegistryHelpers.get_asset_registry().get_dependencies(m.get_outermost().get_name(),opts) or [])]
        assert not any(d.startswith('/Game/') for d in deps)
        stats=LIB.get_statistics(m)
        records[role]=dict(material=props(m,schemas),nodes={n.get_path_name():props(n,schemas) for n in nodes},front_material=front.get_path_name(),dependencies=deps,statistics={k:getattr(stats,k) for k in ['num_pixel_shader_instructions','num_vertex_shader_instructions','num_samplers']},all_nodes_connected=True)
    write('glass-audit',records);write('glass-schemas',schemas)
    return dict(ceiling=opaque,glass={k:dict(nodes=len(v['nodes']),statistics=v['statistics']) for k,v in records.items()})
