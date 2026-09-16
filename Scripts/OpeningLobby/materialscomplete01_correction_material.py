"""New optical and honed broad-stone graphs. No accepted graph mutations."""
import json
import unreal as u
from materialscomplete01_correction_unreal import ROOT,OUT,ASSETS,MAP,guard,write,actors,LIB,snapshot
from architecture01_lightstudy import props
STONE='/Game/OpeningLobby/PainterStone01/Materials/M_PainterStone01'
RECIPES={'Fixed':dict(albedo=.90,transmission=.72,roughness=.48),'Leaf':dict(albedo=.65,transmission=.88,roughness=.18)}

ETCH_CODE='''
// Native procedural micro-slope field; no colour, emission or texture pixels.
float3 p = WorldCm / 2.0;
float3 i = floor(p), f = frac(p);
f = f*f*(3.0-2.0*f);
float3 v = 0;
[unroll] for (int z=0;z<2;z++)
[unroll] for (int y=0;y<2;y++)
[unroll] for (int x=0;x<2;x++) {
    float3 c=i+float3(x,y,z);
    float3 h=frac(sin(float3(dot(c,float3(127.1,311.7,74.7)),dot(c,float3(269.5,183.3,246.1)),dot(c,float3(113.5,271.9,124.6))))*43758.5453)*2-1;
    float3 w=lerp(1-f,f,float3(x,y,z));
    v+=h*w.x*w.y*w.z;
}
float footprint=max(length(ddx(p)),length(ddy(p)));
v*=saturate(1-footprint);
v-=GeometryNormal*dot(v,GeometryNormal);
return normalize(GeometryNormal+v*Slope);
'''

def refine_glass(_=''):
    guard(True,True);assert (OUT/'Trial01/graph-archive.json').exists()
    assert not (OUT/'authorship-Candidate02.json').exists()
    result={}
    for role in ['Fixed','Leaf']:
        m=u.load_asset(ASSETS+'/M_C01_Glass'+role)
        r=dict(albedo=.92 if role=='Fixed' else .85,transmission=.70 if role=='Fixed' else .82,roughness=.50 if role=='Fixed' else .25,slope=.045 if role=='Fixed' else .025)
        for n in LIB.get_material_expressions(m):
            if isinstance(n,(u.MaterialExpressionVectorParameter,u.MaterialExpressionScalarParameter)):
                key=str(n.get_editor_property('parameter_name'))
                if key=='ScatteringAlbedo':n.set_editor_property('default_value',u.LinearColor(*([r['albedo']]*3),1))
                if key=='Transmission':n.set_editor_property('default_value',u.LinearColor(*([r['transmission']]*3),1))
                if key=='SurfaceRoughness':n.set_editor_property('default_value',r['roughness'])
        m.set_editor_property('tangent_space_normal',False)
        slab=LIB.get_material_property_input_node(m,u.MaterialProperty.MP_FRONT_MATERIAL)
        world=LIB.create_material_expression(m,u.MaterialExpressionWorldPosition)
        normal=LIB.create_material_expression(m,u.MaterialExpressionVertexNormalWS)
        slope=LIB.create_material_expression(m,u.MaterialExpressionScalarParameter)
        slope.set_editor_property('parameter_name','EtchSlope');slope.set_editor_property('default_value',r['slope'])
        n=LIB.create_material_expression(m,u.MaterialExpressionCustom)
        inp=[]
        for key in ['WorldCm','GeometryNormal','Slope']:
            i=u.CustomInput();i.set_editor_property('input_name',key);inp.append(i)
        n.set_editor_property('inputs',inp);n.set_editor_property('code',ETCH_CODE)
        n.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT3)
        n.set_editor_property('desc','Subpixel-filtered 2 cm low-amplitude etched-glass micro slopes. No normal change at distant pixel footprints.')
        for a,key in [(world,'WorldCm'),(normal,'GeometryNormal'),(slope,'Slope')]:assert LIB.connect_material_expressions(a,'',n,key)
        assert LIB.connect_material_expressions(n,'',slab,'Normal')
        LIB.layout_material_expressions(m);LIB.recompile_material(m);assert u.EditorAssetLibrary.save_loaded_asset(m)
        result[role]=dict(path=m.get_path_name(),recipe=r,F0=.04,thin_surface=True,simple_volume=True,no_emission=True,normal_code=ETCH_CODE)
    source=ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/Correction01'
    (source/'recipe-Candidate02.json').write_text(json.dumps(result,indent=2))
    return write('authorship-Candidate02',result)

def create(_=''):
    guard(True,True)
    assert (OUT/'correction-response-plan.md').exists() and (OUT/'coverage-plan.json').exists()
    result={}
    for role,r in RECIPES.items():
        path=ASSETS+'/M_C01_Glass'+role
        assert not u.EditorAssetLibrary.does_asset_exist(path)
        m=u.EditorAssetLibrary.duplicate_asset('/Game/OpeningLobby/MaterialsComplete01/Materials/M_MC01_Glass'+role,path)
        assert m
        for n in LIB.get_material_expressions(m):
            if isinstance(n,(u.MaterialExpressionVectorParameter,u.MaterialExpressionScalarParameter)):
                key=str(n.get_editor_property('parameter_name'))
                if key=='ScatteringAlbedo':n.set_editor_property('default_value',u.LinearColor(*([r['albedo']]*3),1))
                if key=='Transmission':n.set_editor_property('default_value',u.LinearColor(*([r['transmission']]*3),1))
                if key=='SurfaceRoughness':n.set_editor_property('default_value',r['roughness'])
        LIB.recompile_material(m);assert u.EditorAssetLibrary.save_loaded_asset(m)
        result[role]=dict(path=m.get_path_name(),recipe=r)
    path=ASSETS+'/M_C01_BroadStone'
    assert not u.EditorAssetLibrary.does_asset_exist(path)
    m=u.EditorAssetLibrary.duplicate_asset(STONE,path);assert m
    original=LIB.get_material_property_input_node(m,u.MaterialProperty.MP_ROUGHNESS)
    mul=LIB.create_material_expression(m,u.MaterialExpressionMultiply)
    mul.set_editor_property('const_b',.35)
    add=LIB.create_material_expression(m,u.MaterialExpressionAdd)
    add.set_editor_property('const_b',.57)
    assert LIB.connect_material_expressions(original,'',mul,'A')
    assert LIB.connect_material_expressions(mul,'',add,'A')
    assert LIB.connect_material_property(add,'',u.MaterialProperty.MP_ROUGHNESS)
    spec=LIB.get_material_property_input_node(m,u.MaterialProperty.MP_SPECULAR)
    spec.set_editor_property('default_value',.35)
    spec.set_editor_property('desc','Honed broad mineral cladding: 2.8 percent dielectric F0. Accepted BaseColor, normal, ORM sources and projection retained.')
    LIB.layout_material_expressions(m);LIB.recompile_material(m)
    assert u.EditorAssetLibrary.save_loaded_asset(m)
    result['Stone']=dict(path=m.get_path_name(),roughness='0.57 + 0.35 * accepted ORM.G',specular=.35,F0=.028,unchanged='BaseColor, mineral world projection at 240 cm, normal, metallic, AO; all source textures read-only')
    source=ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/Correction01';source.mkdir(parents=True,exist_ok=True)
    (source/'recipe-Candidate01.json').write_text(json.dumps(result,indent=2))
    return write('authorship-Candidate01',result)

def bind(_=''):
    guard(True,True);assert not (OUT/'bindings.json').exists()
    rows=json.loads((OUT/'coverage-plan.json').read_text())['rows']
    lookup={(a.get_name(),c.get_name()):c for a in actors() for c in a.get_components_by_class(u.MeshComponent)}
    for r in rows:
        c=lookup[(r['actor'],r['component'])]
        assert c.get_material(0).get_path_name()==r['old']
        assert [m.get_path_name() for m in c.get_editor_property('override_materials')]==r['source_overrides']
        assert u.load_asset(r['new'])
    changed=[r for r in rows if r['new']!=r['old']]
    for r in changed:lookup[(r['actor'],r['component'])].set_material(0,u.load_asset(r['new']))
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    return write('bindings',dict(rows=changed,changed=len(changed),state=guard(True,True)))

def reload(_=''):
    guard(True,True)
    assets=[u.load_asset(p) for p in u.EditorAssetLibrary.list_assets(ASSETS,recursive=True,include_folder=False)]
    result=u.EditorLoadingAndSavingUtils.reload_packages([a.get_outermost() for a in assets])
    write('graphs-reloaded',dict(paths=[a.get_path_name() for a in assets],result=str(result)))
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
    return snapshot('Final',True)

def audit(argument='final'):
    guard(True,True);schemas={};records={}
    for path in u.EditorAssetLibrary.list_assets(ASSETS,recursive=True,include_folder=False):
        m=u.load_asset(path);nodes=LIB.get_material_expressions(m);seen=set();inputs={}
        def visit(n):
            if n is None or n.get_path_name() in seen:return
            seen.add(n.get_path_name())
            for c in LIB.get_inputs_for_material_expression(m,n):visit(c)
        for key in ['FRONT_MATERIAL','BASE_COLOR','ROUGHNESS','SPECULAR','NORMAL','METALLIC','AMBIENT_OCCLUSION','EMISSIVE_COLOR','WORLD_POSITION_OFFSET']:
            n=LIB.get_material_property_input_node(m,getattr(u.MaterialProperty,'MP_'+key));visit(n)
            inputs[key]=n.get_path_name() if n else None
        assert seen=={n.get_path_name() for n in nodes}
        stats=LIB.get_statistics(m)
        assert stats.num_pixel_shader_instructions>0 and stats.num_vertex_shader_instructions>0
        opts=u.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True)
        deps=[str(d) for d in (u.AssetRegistryHelpers.get_asset_registry().get_dependencies(m.get_outermost().get_name(),opts) or [])]
        assert all(not d.startswith('/Game/') or d.startswith('/Game/OpeningLobby/PainterStone01/Textures/') for d in deps)
        records[path]=dict(material=props(m,schemas),editor_data=props(m.get_editor_property('editor_only_data'),schemas),nodes={n.get_path_name():dict(properties=props(n,schemas),inputs=list(LIB.get_material_expression_input_names(n)),connected=[c.get_path_name() if c else None for c in LIB.get_inputs_for_material_expression(m,n)]) for n in nodes},outputs=inputs,dependencies=deps,textures=[t.get_path_name() for t in LIB.get_used_textures(m)],statistics={k:getattr(stats,k) for k in ['num_pixel_shader_instructions','num_vertex_shader_instructions','num_samplers']},all_nodes_connected=True)
    write('graph-audit-'+argument,dict(passed=True,records=records));write('graph-schemas-'+argument,schemas)
    return dict(passed=True,materials=len(records))
