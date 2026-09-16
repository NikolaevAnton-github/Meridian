"""New opaque graph fed exclusively by native Painter exports."""
import json
from pathlib import Path
import unreal as u
from painterstone01_unreal import ROOT,OUT,ASSETS,MAP,guard,actors,write
from architecture01_lightstudy import props

SRC=ROOT/'Assets/Source/OpeningLobby/PainterStone01/Channels'
MAT=ASSETS+'/Materials/M_PainterStone01'
LIB=u.MaterialEditingLibrary
TARGETS={'RA01_PortalJamb_1','RA01_Shoulder_1','RA01_FirstPier_1','Pier_1_1'}
COLOR_CODE='''
float3 p = WorldCm / CoverageCm;
float3 weights = pow(abs(GeometryNormal), 16.0);
weights /= max(dot(weights, float3(1,1,1)), 0.0001);
float3 x = Texture2DSample(ChannelTex, ChannelTexSampler, p.yz).rgb;
float3 y = Texture2DSample(ChannelTex, ChannelTexSampler, p.xz).rgb;
float3 z = Texture2DSample(ChannelTex, ChannelTexSampler, p.xy).rgb;
return x*weights.x + y*weights.y + z*weights.z;
'''
NORMAL_CODE='''
float3 p = WorldCm / CoverageCm;
float3 weights = pow(abs(GeometryNormal), 16.0);
weights /= max(dot(weights, float3(1,1,1)), 0.0001);
float2 x = Texture2DSample(ChannelTex, ChannelTexSampler, p.yz).rg*2.0-1.0;
float2 y = Texture2DSample(ChannelTex, ChannelTexSampler, p.xz).rg*2.0-1.0;
float2 z = Texture2DSample(ChannelTex, ChannelTexSampler, p.xy).rg*2.0-1.0;
// DirectX normal Y is opposite increasing texture V. Reorient each UV plane.
float3 perturbation = float3(0,x.x,-x.y)*weights.x
                    + float3(y.x,0,-y.y)*weights.y
                    + float3(z.x,-z.y,0)*weights.z;
perturbation -= GeometryNormal*dot(perturbation,GeometryNormal);
return normalize(GeometryNormal + perturbation);
'''

# Correction01: preserve texel scale while varying color phase across large faces.
# Only the Painter BaseColor is sampled here; calibrated ORM/normal paths stay fixed.
VARIED_COLOR_CODE='''
float3 p = WorldCm / CoverageCm;
float3 weights = pow(abs(GeometryNormal), 16.0);
weights /= max(dot(weights, float3(1,1,1)), 0.0001);
float3 result = float3(0,0,0);
[unroll] for (int plane = 0; plane < 3; ++plane)
{
    float2 uv = plane == 0 ? p.yz : (plane == 1 ? p.xz : p.xy);
    float2 du = ddx(uv);
    float2 dv = ddy(uv);
    float2 grid = float2(uv.x - uv.y * 0.577350269, uv.y * 1.154700538);
    float2 cell = floor(grid);
    float2 f = frac(grid);
    bool lower = f.x + f.y < 1.0;
    float2 v0 = cell + (lower ? float2(0,0) : float2(1,1));
    float2 v1 = cell + (lower ? float2(1,0) : float2(0,1));
    float2 v2 = cell + (lower ? float2(0,1) : float2(1,0));
    float3 blend = lower ? float3(1-f.x-f.y, f.x, f.y)
                         : float3(f.x+f.y-1, 1-f.x, 1-f.y);
    blend = pow(max(blend, 0), 4.0);
    blend /= max(dot(blend, float3(1,1,1)), 0.0001);
    float2 o0 = frac(sin(float2(dot(v0,float2(127.1,311.7)), dot(v0,float2(269.5,183.3)))) * 43758.5453);
    float2 o1 = frac(sin(float2(dot(v1,float2(127.1,311.7)), dot(v1,float2(269.5,183.3)))) * 43758.5453);
    float2 o2 = frac(sin(float2(dot(v2,float2(127.1,311.7)), dot(v2,float2(269.5,183.3)))) * 43758.5453);
    float3 color = Texture2DSampleGrad(ChannelTex, ChannelTexSampler, uv+o0, du, dv).rgb * blend.x
                 + Texture2DSampleGrad(ChannelTex, ChannelTexSampler, uv+o1, du, dv).rgb * blend.y
                 + Texture2DSampleGrad(ChannelTex, ChannelTexSampler, uv+o2, du, dv).rgb * blend.z;
    result += color * (plane == 0 ? weights.x : (plane == 1 ? weights.y : weights.z));
}
return result;
'''


def sampling_variation():
    guard(True,True)
    m=u.load_asset(MAT)
    color=LIB.get_material_property_input_node(m,u.MaterialProperty.MP_BASE_COLOR)
    assert isinstance(color,u.MaterialExpressionCustom)
    previous=color.get_editor_property('code')
    assert previous==COLOR_CODE, 'Apply the bounded color sampling change only once.'
    color.set_editor_property('code',VARIED_COLOR_CODE)
    color.set_editor_property('desc','Correction01: native Painter color, triangular phase blending at unchanged 240 cm texel coverage')
    LIB.recompile_material(m)
    assert u.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)
    return write('native-sampling-change',dict(previous_code=previous,current_code=VARIED_COLOR_CODE,
        changed_node=color.get_path_name(),physical_coverage_cm=240,
        scope='BaseColor sampling only. Same Painter texture, no tint, UV scale distortion or new dependencies. ORM and Normal unchanged.'))

def material():
    guard(True,True)
    at=u.AssetToolsHelpers.get_asset_tools()
    existed=u.EditorAssetLibrary.does_asset_exist(MAT)
    imported=[]
    textures={}
    for channel in (['BaseColor'] if existed else ['BaseColor','ORM','Normal']):
        p=SRC/('T_PainterStone01_'+channel+'.png')
        assert p.is_file()
        t=u.AssetImportTask()
        for key,val in dict(filename=str(p),destination_path=ASSETS+'/Textures',destination_name=p.stem,
                            automated=True,replace_existing=existed,save=False).items():t.set_editor_property(key,val)
        assert existed or not u.EditorAssetLibrary.does_asset_exist(ASSETS+'/Textures/'+p.stem)
        at.import_asset_tasks([t])
        tex=u.load_asset(ASSETS+'/Textures/'+p.stem)
        assert isinstance(tex,u.Texture2D)
        for key,val in dict(srgb=channel=='BaseColor',compression_settings={
            'BaseColor':u.TextureCompressionSettings.TC_DEFAULT,'ORM':u.TextureCompressionSettings.TC_MASKS,
            'Normal':u.TextureCompressionSettings.TC_NORMALMAP}[channel],flip_green_channel=False,
            mip_gen_settings=u.TextureMipGenSettings.TMGS_FROM_TEXTURE_GROUP,never_stream=False,
            address_x=u.TextureAddress.TA_WRAP,address_y=u.TextureAddress.TA_WRAP).items():tex.set_editor_property(key,val)
        assert u.EditorAssetLibrary.save_loaded_asset(tex,only_if_is_dirty=False)
        imported.append(dict(channel=channel,source=p.relative_to(ROOT).as_posix(),asset=tex.get_path_name()))
        textures[channel]=tex
    if existed:
        m=u.load_asset(MAT)
        LIB.recompile_material(m)
        assert u.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)
        return write('native-reimport',dict(imported=imported,new_graph_unchanged=True))
    m=at.create_asset('M_PainterStone01',ASSETS+'/Materials',u.Material,u.MaterialFactoryNew())
    assert m
    for n in list(LIB.get_material_expressions(m)):LIB.delete_material_expression(m,n)
    m.set_editor_property('blend_mode',u.BlendMode.BLEND_OPAQUE)
    m.set_editor_property('tangent_space_normal',False)
    m.set_editor_property('two_sided',False)
    def node(cls,x,y,**kwargs):
        result=LIB.create_material_expression(m,cls,x,y)
        for key,value in kwargs.items():result.set_editor_property(key,value)
        return result
    def wire(a,b,pin='',out=''):
        assert LIB.connect_material_expressions(a,out,b,pin),(str(a),str(b),pin)
    def output(a,prop):assert LIB.connect_material_property(a,'',getattr(u.MaterialProperty,'MP_'+prop))
    world=node(u.MaterialExpressionWorldPosition,-1200,-180,desc='Centimetre world coordinates; scene geometry unchanged')
    normal=node(u.MaterialExpressionVertexNormalWS,-1200,-30,desc='Original geometric surface normal')
    coverage=node(u.MaterialExpressionScalarParameter,-1200,130,parameter_name='CoverageCm',default_value=240,
        desc='240 cm matches the native Painter authoring plane')
    samples={}
    for i,(channel,tex) in enumerate(textures.items()):
        texture=node(u.MaterialExpressionTextureObject,-1200,360+i*220,texture=tex,
            sampler_type={'BaseColor':u.MaterialSamplerType.SAMPLERTYPE_COLOR,'ORM':u.MaterialSamplerType.SAMPLERTYPE_MASKS,
            'Normal':u.MaterialSamplerType.SAMPLERTYPE_NORMAL}[channel],desc='New native Painter export: '+channel)
        inputs=[]
        for name in ['ChannelTex','WorldCm','GeometryNormal','CoverageCm']:
            inp=u.CustomInput();inp.set_editor_property('input_name',name);inputs.append(inp)
        sample=node(u.MaterialExpressionCustom,-650,i*330,code=NORMAL_CODE if channel=='Normal' else COLOR_CODE,
            inputs=inputs,output_type=u.CustomMaterialOutputType.CMOT_FLOAT3,description='PainterStone01 physical '+channel,
            desc='Editable world projection of actual Painter export; no old texture or material dependencies')
        for a,pin in [(texture,'ChannelTex'),(world,'WorldCm'),(normal,'GeometryNormal'),(coverage,'CoverageCm')]:wire(a,sample,pin)
        samples[channel]=sample
    output(samples['BaseColor'],'BASE_COLOR');output(samples['Normal'],'NORMAL')
    for i,(channel,prop) in enumerate([('r','AMBIENT_OCCLUSION'),('g','ROUGHNESS'),('b','METALLIC')]):
        mask=node(u.MaterialExpressionComponentMask,-150,250+i*100,r=channel=='r',g=channel=='g',b=channel=='b',a=False)
        wire(samples['ORM'],mask);output(mask,prop)
    spec=node(u.MaterialExpressionScalarParameter,-150,640,parameter_name='DielectricSpecular',default_value=.4,
        desc='Polished dielectric with 3.2 percent normal-incidence reflectance; no coat')
    output(spec,'SPECULAR')
    LIB.recompile_material(m)
    assert u.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)
    return write('native-authorship',dict(material=m.get_path_name(),imported=imported,
        physical_coverage_cm=240,expressions=len(LIB.get_material_expressions(m)),
        parent=None,old_opaque_dependencies=[],source='Scripts/OpeningLobby/painterstone01_material.py'))

def bind():
    guard(True,True)
    mat=u.load_asset(MAT);assert mat
    source=json.loads((OUT/'Source/inventory.json').read_text())
    lookup={(a.get_name(),c.get_name()):c for a in actors() for c in a.get_components_by_class(u.MeshComponent)}
    changes=[]
    for row in source:
        if row['label'] not in TARGETS:continue
        assert len(row['materials'])==1
        c=lookup[(row['actor'],row['component'])]
        assert c.get_material(0).get_path_name()==row['materials'][0]
        delta=dict(actor=row['actor'],label=row['label'],component=row['component'],slot=0,
            old=row['materials'][0],new=mat.get_path_name(),source_overrides=row['overrides'])
        c.set_material(0,mat);changes.append(delta)
    assert len(changes)==4
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    return write('bindings',dict(changed=len(changes),rows=changes,state=guard(True,True)))

def audit():
    guard(True,True)
    schemas={};m=u.load_asset(MAT);assert m
    nodes=LIB.get_material_expressions(m)
    seen=set();inputs={}
    def visit(n):
        if not n or n.get_path_name() in seen:return
        seen.add(n.get_path_name())
        for child in LIB.get_inputs_for_material_expression(m,n):visit(child)
    for key in ['BASE_COLOR','ROUGHNESS','METALLIC','NORMAL','SPECULAR','AMBIENT_OCCLUSION','WORLD_POSITION_OFFSET','EMISSIVE_COLOR','OPACITY']:
        n=LIB.get_material_property_input_node(m,getattr(u.MaterialProperty,'MP_'+key))
        inputs[key]=n.get_path_name() if n else None;visit(n)
    assert seen=={n.get_path_name() for n in nodes} and len(nodes)==13
    textures=list(LIB.get_used_textures(m));assert len(textures)==3
    import_sources={t.get_path_name():list(t.get_editor_property('asset_import_data').extract_filenames()) for t in textures}
    for t in textures:
        expected=(SRC/(t.get_name()+'.png')).resolve()
        assert [Path(p).resolve() for p in import_sources[t.get_path_name()]]==[expected],import_sources
    opts=u.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True,
        include_searchable_names=True,include_soft_management_references=True,include_hard_management_references=True)
    reg=u.AssetRegistryHelpers.get_asset_registry()
    assets=[m]+textures
    # Registry returns None for texture packages with no package dependencies.
    dependencies={a.get_path_name():[str(d) for d in (reg.get_dependencies(a.get_outermost().get_name(),opts) or [])] for a in assets}
    assert len([d for d in dependencies[m.get_path_name()] if d.startswith(ASSETS+'/Textures/')])==3
    assert not [d for deps in dependencies.values() for d in deps if d.startswith('/Game/') and not d.startswith(ASSETS+'/')]
    for tex in textures:
        iscolor=tex.get_name().endswith('BaseColor');isnormal=tex.get_name().endswith('Normal')
        assert tex.get_editor_property('srgb')==iscolor
        assert tex.get_editor_property('compression_settings')==(
            u.TextureCompressionSettings.TC_DEFAULT if iscolor else u.TextureCompressionSettings.TC_NORMALMAP if isnormal else u.TextureCompressionSettings.TC_MASKS)
        assert tex.blueprint_get_size_x()==2048 and tex.blueprint_get_size_y()==2048
    stats=LIB.get_statistics(m)
    record=dict(material=props(m,schemas),nodes={n.get_path_name():props(n,schemas) for n in nodes},inputs=inputs,
        textures={t.get_path_name():props(t,schemas) for t in textures},dependencies=dependencies,import_sources=import_sources,
        statistics={k:getattr(stats,k) for k in ['num_pixel_shader_instructions','num_vertex_shader_instructions','num_samplers']},
        all_nodes_connected=True,new_opaque_dependencies_only=True)
    write('native-material-audit',record);write('native-material-schemas',schemas)
    return dict(expressions=len(nodes),dependencies=dependencies,statistics=record['statistics'])
