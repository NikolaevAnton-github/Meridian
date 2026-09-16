"""Editable native height extinction and matching direct-light attenuation."""
import json
import unreal as u
from uppervoid01_unreal import ROOT,OUT,ASSETS,MAP,guard,write,actors,props
LIB=u.MaterialEditingLibrary
SRC=ROOT/'Assets/Source/OpeningLobby/UpperVoid01'
FADE='''float h = saturate((WorldCm.z - FadeStartCm) / max(FadeEndCm - FadeStartCm, 1.0));
// Quintic extinction: zero derivatives at both endpoints, fixed world height.
float extinction = h*h*h*(h*(h*6.0-15.0)+10.0);
return 1.0-extinction;'''
def build(tag):
    guard(True,True)
    if tag=='Trial02':return revision()
    assert tag=='Trial01';assert (OUT/'archive-verification.json').exists()
    assert not u.EditorAssetLibrary.does_asset_exist(ASSETS+'/M_UpperVoid_Extinction')
    SRC.mkdir(parents=True,exist_ok=True)
    (SRC/'HeightTransmission.hlsl').write_text(FADE)
    mats=[]
    for name,domain in [('M_UpperVoid_Extinction',u.MaterialDomain.MD_POST_PROCESS),('M_UpperVoid_LightTransmission',u.MaterialDomain.MD_LIGHT_FUNCTION)]:
        m=u.AssetToolsHelpers.get_asset_tools().create_asset(name,ASSETS,u.Material,u.MaterialFactoryNew());assert m
        m.set_editor_property('material_domain',domain)
        if domain==u.MaterialDomain.MD_POST_PROCESS:m.set_editor_property('blendable_location',u.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING)
        def node(cls,**kwargs):
            n=LIB.create_material_expression(m,cls)
            for k,v in kwargs.items():n.set_editor_property(k,v)
            return n
        def wire(a,b,pin='',out=''):assert LIB.connect_material_expressions(a,out,b,pin)
        world=node(u.MaterialExpressionWorldPosition)
        start=node(u.MaterialExpressionScalarParameter,parameter_name='FadeStartCm',default_value=350.)
        end=node(u.MaterialExpressionScalarParameter,parameter_name='FadeEndCm',default_value=850.)
        inputs=[]
        for n in ['WorldCm','FadeStartCm','FadeEndCm']:
            i=u.CustomInput();i.set_editor_property('input_name',n);inputs.append(i)
        fade=node(u.MaterialExpressionCustom,code=FADE,inputs=inputs,output_type=u.CustomMaterialOutputType.CMOT_FLOAT1)
        for n,x in [('WorldCm',world),('FadeStartCm',start),('FadeEndCm',end)]:wire(x,fade,n)
        output=fade
        if domain==u.MaterialDomain.MD_POST_PROCESS:
            scene=node(u.MaterialExpressionSceneTexture,scene_texture_id=u.SceneTextureId.PPI_POST_PROCESS_INPUT0)
            output=node(u.MaterialExpressionMultiply);wire(scene,output,'A','Color');wire(fade,output,'B')
        assert LIB.connect_material_property(output,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
        LIB.layout_material_expressions(m);LIB.recompile_material(m);assert u.EditorAssetLibrary.save_loaded_asset(m)
        mats.append(m)
    rows=[]
    for a in actors():
        if not isinstance(a,u.PointLight):continue
        c=a.get_component_by_class(u.PointLightComponent);pos=a.get_actor_location();central=abs(pos.y)<1
        changes=dict(intensity=40000. if central else 18000.,attenuation_radius=1500. if central else 1200.,indirect_lighting_intensity=.2,light_function_material=mats[1])
        before=props(c,{})
        for k,v in changes.items():c.set_editor_property(k,v)
        a.set_actor_location(u.Vector(pos.x,pos.y,450 if central else 400),False,True)
        rows.append(dict(actor=a.get_name(),label=a.get_actor_label(),before=before,after=props(c,{})))
    assert len(rows)==18
    pp=u.get_editor_subsystem(u.EditorActorSubsystem).spawn_actor_from_class(u.PostProcessVolume,u.Vector(0,0,0))
    pp.set_actor_label('UpperVoid01_WorldHeightExtinction');pp.set_editor_property('unbound',True);pp.set_editor_property('priority',100.)
    pp.add_or_update_blendable(mats[0],1.)
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    recipe=dict(candidate='LobbyAtmosphere-UpperVoid01/WorkerCandidate01',trial=tag,fade_start_cm=350,fade_end_cm=850,formula=FADE,postprocess_location='SceneColorAfterTonemapping',lights=rows,new_postprocess_actor=pp.get_name(),materials=[m.get_path_name() for m in mats],exposure='Existing fixed manual bias -5 preserved',rationale='Height-based final extinction plus direct-light transmission and lowered fills; preserve lower hall and suppress reflected roof illumination')
    (SRC/'recipe.json').write_text(json.dumps(recipe,indent=2));write(tag+'/recipe',recipe)
    return dict(saved=True,lights=len(rows),postprocess=pp.get_name(),materials=recipe['materials'])
def revision():
    assert (OUT/'Trial01/all-properties.json').exists() and not (OUT/'Trial02/recipe.json').exists()
    rows=[]
    for a in actors():
        if isinstance(a,u.PointLight):
            c=a.get_component_by_class(u.PointLightComponent)
            assert c.get_editor_property('specular_scale')==1.
            c.set_editor_property('specular_scale',.2)
            rows.append(dict(actor=a.get_name(),property='LightComponent0.specularScale',before=1.,after=.2))
    assert len(rows)==18
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    recipe=json.loads((SRC/'recipe.json').read_text());recipe.update(trial='Trial02',revision=1,revision_reason='Reduce conspicuous direct-light reflection pools observed on glossy columns and aisle walls; retain all surface roughness/specular graphs',specular_light_scale=.2,revision_deltas=rows)
    (SRC/'recipe.json').write_text(json.dumps(recipe,indent=2));write('Trial02/recipe',recipe)
    return dict(saved=True,revision=1,light_specular_scale=.2,lights=18)
def audit(tag):
    if tag=='runtime-capabilities':
        import importlib,uppervoid01_runtime as r
        assert r.sample is None or r.sample.done
        assert r.walkrun is None or r.walkrun.done
        importlib.reload(r)
        engine=u.get_default_object(u.load_class(None,'/Script/Engine.Engine'))
        ep=props(engine,{})
        values={k:v for k,v in ep['properties'].items() if any(n in k.lower() for n in ['framerate','frame_rate','fixedtime'])}
        return write('Performance/runtime-capabilities',dict(engine_timing_settings=values,system_timing_apis=[n for n in dir(u.SystemLibrary) if any(k in n for k in ['frame','gpu','cpu'])],method='Read only native reflection; finished sampling module refreshed before actual-input run'))
    schemas={};records={}
    for path in u.EditorAssetLibrary.list_assets(ASSETS,recursive=True,include_folder=False):
        m=u.load_asset(path);nodes=LIB.get_material_expressions(m);stats=LIB.get_statistics(m)
        records[path]=dict(material=props(m,schemas),nodes={n.get_name():dict(properties=props(n,schemas),inputs=[str(x) for x in LIB.get_inputs_for_material_expression(m,n)]) for n in nodes},emissive=str(LIB.get_material_property_input_node(m,u.MaterialProperty.MP_EMISSIVE_COLOR)),statistics={k:getattr(stats,k) for k in ['num_pixel_shader_instructions','num_vertex_shader_instructions','num_samplers']})
    write('graph-audit-'+tag,records);write('graph-schemas-'+tag,schemas)
    return dict(assets=len(records),records={k:v['statistics'] for k,v in records.items()})
