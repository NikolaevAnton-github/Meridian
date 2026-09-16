"""Bounded Correction02 native support and read-only legacy validators."""
import json,types,importlib,hashlib
from pathlib import Path
import unreal as u
from stage1_tools import state
from architecture01_lightstudy import props
ROOT=Path('D:/devgames/MeridianSquad')
OUT=ROOT/'Saved/OpeningLobby/MaterialsComplete01/Worker/Correction02'
ASSETS='/Game/OpeningLobby/MaterialsComplete01/Correction02'
MAP='/Game/Maps/L_OpeningLobby_PainterStone01'
SOURCE=MAP
p=ROOT/'Scripts/OpeningLobby/materialintegration01_unreal.py'
legacy=types.ModuleType('support_properties');legacy.__file__=str(p)
exec(compile(p.read_text(),str(p),'exec'),legacy.__dict__)
legacy.OUT=OUT;legacy.MAP=MAP;legacy.SOURCE=MAP;legacy.ASSETS=ASSETS
guard=legacy.guard;write=legacy.write;snapshot=legacy.snapshot;actors=legacy.actors;settings=legacy.settings
LIB=u.MaterialEditingLibrary
LABEL='MC02_ProvisionalNeutralFarField'

def check_bytes():
    receipt=OUT/'current-map.json'
    expected=json.loads(receipt.read_text())['sha256'] if receipt.exists() else '527827586708cb49c0ebfdf4500b8bdd677cc95b0f600471622906a27dbda919'
    actual=hashlib.sha256((ROOT/'Content/Maps/L_OpeningLobby_PainterStone01.umap').read_bytes()).hexdigest()
    assert actual==expected,(expected,actual)
    return actual

def save():
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    return write('current-map',dict(sha256=hashlib.sha256((ROOT/'Content/Maps/L_OpeningLobby_PainterStone01.umap').read_bytes()).hexdigest()))

def build():
    guard(True,True);check_bytes()
    assert (OUT/'Before/all-properties.json').exists() and (OUT/'support-plan.md').exists()
    assert not any(a.get_actor_label()==LABEL for a in actors())
    path=ASSETS+'/M_MC02_NeutralFarField'
    assert not u.EditorAssetLibrary.does_asset_exist(path)
    mesh=u.load_asset('/Engine/BasicShapes/Sphere');assert mesh
    m=u.AssetToolsHelpers.get_asset_tools().create_asset('M_MC02_NeutralFarField',ASSETS,u.Material,u.MaterialFactoryNew())
    m.set_editor_property('two_sided',True)
    m.set_editor_property('shading_model',u.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property('is_sky',True)
    world=LIB.create_material_expression(m,u.MaterialExpressionWorldPosition)
    n=LIB.create_material_expression(m,u.MaterialExpressionCustom)
    inp=u.CustomInput();inp.set_editor_property('input_name','WorldCm');n.set_editor_property('inputs',[inp])
    code='''// Provisional neutral inspection field: continuous horizon/zenith gradient.
float3 d=normalize(WorldCm);
float upper=smoothstep(0.0,0.70,max(d.z,0.0));
float lower=smoothstep(0.0,0.50,max(-d.z,0.0));
float radiance=lerp(12.0,2.0,upper);
radiance=lerp(radiance,3.0,lower);
radiance*=1.0+0.18*d.y;
return float3(radiance,radiance,radiance);'''
    n.set_editor_property('code',code);n.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT3)
    n.set_editor_property('desc','Neutral continuous horizon 12 / zenith 2 / lower 3, broad Y modulation 18 percent. Provisional inspection support only.')
    assert LIB.connect_material_expressions(world,'',n,'WorldCm')
    assert LIB.connect_material_property(n,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
    LIB.layout_material_expressions(m);LIB.recompile_material(m);assert u.EditorAssetLibrary.save_loaded_asset(m)
    a=u.get_editor_subsystem(u.EditorActorSubsystem).spawn_actor_from_class(u.StaticMeshActor,u.Vector(0,0,0))
    a.set_actor_label(LABEL);a.set_folder_path('MaterialsComplete01/Correction02_InspectionSupport')
    c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_material(0,m)
    a.set_actor_scale3d(u.Vector(2000,2000,2000))
    c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION);c.set_editor_property('cast_shadow',False)
    c.set_editor_property('affect_distance_field_lighting',False)
    c.set_editor_property('affect_dynamic_indirect_lighting',False)
    c.set_editor_property('receives_decals',False)
    a.set_actor_enable_collision(False)
    save()
    recipe=dict(candidate='LobbyMaterials-Complete01/Correction02',setup='Setup01',actor=a.get_name(),label=LABEL,mesh=mesh.get_path_name(),mesh_bounds=str(mesh.get_bounds()),location_cm=[0,0,0],scale=[2000]*3,radius_cm=100000,material=m.get_path_name(),hlsl=code,neutral_rgb=True,collision=False,shadow=False,visible=True,hidden_in_game=False,new_skylight_or_reflection=False,exception='One stock-engine distant neutral sphere; provisional inspection far field, no exterior design or final atmosphere.')
    source=ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/Correction02';source.mkdir(parents=True,exist_ok=True)
    (source/'recipe-Setup01.json').write_text(json.dumps(recipe,indent=2))
    return write('setup-Setup01',recipe)

def audit():
    guard(True,True);check_bytes()
    p=ROOT/'Scripts/OpeningLobby/materialscomplete01_correction_material.py'
    s=p.read_text().replace('from materialscomplete01_correction_unreal import','from materialscomplete01_support_unreal import')
    mod=types.ModuleType('support_graph_audit');exec(compile(s,str(p),'exec'),mod.__dict__)
    return mod.audit('final')

def reflection_trial():
    guard(True,True);check_bytes()
    assert not (OUT/'setup-Setup02.json').exists()
    import shutil
    archive=OUT/'Setup01/NativeArchive';archive.mkdir(parents=True,exist_ok=True)
    source=ROOT/'Content/OpeningLobby/MaterialsComplete01/Correction02/M_MC02_NeutralFarField.uasset'
    shutil.copy2(source,archive/source.name)
    shutil.copy2(ROOT/'Content/Maps/L_OpeningLobby_PainterStone01.umap',archive/'L_OpeningLobby_PainterStone01.umap')
    write('Setup01/archive',dict(entries=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in archive.iterdir()]))
    a=u.get_editor_subsystem(u.EditorActorSubsystem).spawn_actor_from_class(u.SphereReflectionCapture,u.Vector(-2500,0,950))
    a.set_actor_label('MC02_TrialLocalReflection');a.set_folder_path('MaterialsComplete01/Correction02_InspectionSupport')
    c=a.get_component_by_class(u.SphereReflectionCaptureComponent)
    c.set_editor_property('influence_radius',2300)
    c.set_editor_property('brightness',.7)
    c.set_editor_property('runtime_capture',True)
    c.set_editor_property('runtime_skylight_scale',u.LinearColor(0,0,0,1))
    c.refresh_capture(True,False)
    save()
    recipe=dict(setup='Setup02',actor=a.get_name(),label=a.get_actor_label(),type='SphereReflectionCapture',location_cm=[-2500,0,950],influence_radius_cm=2300,brightness=.7,runtime_capture=True,runtime_skylight_scale=[0,0,0],source='CapturedScene; no cubemap asset or painted reflection',sphere='Exact Setup01 settings retained',reason='Setup01 near-oblique fixed pane remains uniformly diffuse and lacks identifiable reflected scene/angular structure; test one local captured-scene reflection with no new diffuse light.',runtime_mode=u.SystemLibrary.get_console_variable_int_value('r.ReflectionCapture.Runtime'))
    return write('setup-Setup02',recipe)

def action(operation,argument=''):
    if operation=='state':return state()
    if operation=='snapshot':
        check_bytes();assert not (OUT/argument/'all-properties.json').exists()
        return snapshot(argument,True)
    if operation=='build':return build()
    if operation=='audit':return audit()
    if operation=='reflection_trial':return reflection_trial()
    if operation=='remove_trial':
        guard(True,True);check_bytes()
        trial=[a for a in actors() if a.get_actor_label()=='MC02_TrialLocalReflection']
        assert len(trial)==1
        schemas={};record=props(trial[0],schemas)
        record['components']={c.get_name():props(c,schemas) for c in trial[0].get_components_by_class(u.ActorComponent)}
        write('Setup02/rejected-actor-properties',record)
        import shutil
        dst=OUT/'Setup02/L_OpeningLobby_PainterStone01.umap';assert not dst.exists()
        shutil.copy2(ROOT/'Content/Maps/L_OpeningLobby_PainterStone01.umap',dst)
        write('Setup02/rejection',dict(reason='Installed r.ReflectionCapture.Runtime=0 skips runtime captures. Trial is not positive reflection evidence; no forbidden renderer changes made. Retain smallest sphere-only setup.',archive=dict(path=dst.relative_to(ROOT).as_posix(),bytes=dst.stat().st_size,sha256=hashlib.sha256(dst.read_bytes()).hexdigest())))
        assert u.get_editor_subsystem(u.EditorActorSubsystem).destroy_actor(trial[0])
        save();return dict(removed=1,chosen='Setup01',R1='Partial; fixed-pane visual likeness unresolved')
    if operation=='reopen':
        guard(True,True);check_bytes()
        assets=[u.load_asset(p) for p in u.EditorAssetLibrary.list_assets(ASSETS,recursive=True,include_folder=False)]
        r=u.EditorLoadingAndSavingUtils.reload_packages([a.get_outermost() for a in assets])
        write('graphs-reloaded',dict(paths=[a.get_path_name() for a in assets],result=str(r)))
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
        return snapshot('Final',True)
    if operation.startswith('capture_'):
        import materialscomplete01_support_capture as c
        if operation=='capture_prepare':c=importlib.reload(c)
        return c.run(operation[8:],argument)
    raise ValueError(operation)
