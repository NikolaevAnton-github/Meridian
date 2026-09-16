"""Bounded neutral LightStudy01; invoked only through the Architecture01 Epic tool."""
import json
import re
from contextlib import contextmanager
import unreal as u
import architecture01_unreal as work
import architecture01_reflection as reflection

SOURCE='/Game/Maps/L_OpeningLobby_Architecture01'
MAP=SOURCE+'_LightStudy01'
OUT=work.ROOT/'Saved/OpeningLobby/Stage2/Architecture01/LightStudy01'
BASEOUT=OUT.parent
SKY='LS01_NeutralFarField_InspectionOnly'
LIGHT='LS01_NeutralSkyLight_InspectionOnly'
PP='LS01_FrontLayerReflections_InspectionOnly'

def write(name,data):
    (OUT/(name+'.json')).write_text(json.dumps(data,indent=2))
    return data

def guard(study=True,clean=False,pie=False):
    s=work.state();work.require_project(s['project'])
    level=s['level'].replace('UEDPIE_0_','').split('.')[0]
    assert level==(MAP if study else SOURCE),s
    assert s['pie']==pie and not s['dirty_content'],s
    assert all(n==MAP for n in s['dirty_maps']),s
    if clean:assert not s['dirty_maps'],s
    return s

@contextmanager
def config(folder,study=True):
    """Temporarily configure existing validators/cameras; retain historical defaults."""
    import architecture01_capture as capture
    old=(work.MAP,work.OUT,capture.MAP,capture.OUT,capture.guard)
    work.MAP=capture.MAP=MAP if study else SOURCE
    work.OUT=capture.OUT=folder
    capture.guard=lambda candidate=False,clean=False:guard(study,clean=clean and not study)
    folder.mkdir(exist_ok=True)
    try:yield capture
    finally:work.MAP,work.OUT,capture.MAP,capture.OUT,capture.guard=old

def props(obj,schemas):
    cls=obj.get_class().get_path_name()
    if cls not in schemas:
        schemas[cls]=json.loads(u.ToolsetLibrary.list_struct_properties(obj.get_class()))
    names=list(schemas[cls])
    data=json.loads(u.ToolsetLibrary.get_object_properties(obj,names))
    assert set(data)==set(names),(cls,set(names)-set(data))
    return dict(class_path=cls,properties=data)

def snapshot(name,study):
    guard(study,True)
    folder=OUT/name;folder.mkdir(exist_ok=True)
    (folder/'expected-geometry.json').write_bytes((BASEOUT/'expected-geometry.json').read_bytes())
    with config(folder,study):audit=work.audit()
    schemas={};rows={}
    for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
        row=props(a,schemas)
        row.update(name=a.get_name(),transform=re.sub(r'0x[0-9A-Fa-f]+','POINTER',str(a.get_actor_transform())),hidden=a.is_temporarily_hidden_in_editor())
        row['components']={c.get_name():props(c,schemas) for c in a.get_components_by_class(u.ActorComponent)}
        rows[a.get_actor_label()]=row
    world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
    result=dict(actors=rows,world_settings=props(world.get_world_settings(),schemas),cvars=reflection.settings())
    (folder/'all-properties.json').write_text(json.dumps(result,separators=(',',':')))
    (folder/'property-schemas.json').write_text(json.dumps(schemas,separators=(',',':')))
    return dict(audit=audit,actors=len(rows),classes=len(schemas),state=guard(study,True))

def run(command):
    if command=='setup:B':
        guard(True)
        assert (OUT/'setup-A.json').exists() and not (OUT/'setup-B.json').exists()
        actors={a.get_actor_label():a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()}
        sky=actors[SKY]
        # Second and final setup: quieter neutral far-field gradient to retain reflections.
        values={'zenith Color':dict(r=6,g=6,b=6,a=1),'horizon color':dict(r=1.5,g=1.5,b=1.5,a=1),'refresh material':True}
        assert u.ToolsetLibrary.set_object_properties(sky,json.dumps(values))
        sky.call_method('RefreshMaterial')
        sky.set_actor_enable_collision(False)
        for c in sky.get_components_by_class(u.PrimitiveComponent):
            c.set_collision_profile_name('NoCollision');c.set_editor_property('cast_shadow',False)
        actors[LIGHT].get_component_by_class(u.SkyLightComponent).recapture_sky()
        return write('setup-B',dict(changed_sky_parameters=values,sky=props(sky,{}),actors=[SKY,LIGHT,PP],renderer=reflection.settings(),state=guard(True),purpose='Lower neutral horizon luminance with a broad grey zenith gradient; no scenery, sun, clouds or stars. All other setup A settings retained.'))
    if command=='setup:A':
        guard(True,True)
        assert not (OUT/'setup-A.json').exists()
        sub=u.get_editor_subsystem(u.EditorActorSubsystem)
        assert not any(a.get_actor_label().startswith('LS01_') for a in sub.get_all_level_actors())
        sky=sub.spawn_actor_from_class(u.load_class(None,'/Engine/EngineSky/BP_Sky_Sphere.BP_Sky_Sphere_C'),u.Vector(0,0,0))
        sky.set_actor_label(SKY);sky.set_folder_path('LightStudy01/NeutralInspectionOnly')
        # Existing engine sphere is a far field, not a pane backing or authored exterior.
        mesh=sky.get_component_by_class(u.StaticMeshComponent)
        bounds=mesh.static_mesh.get_bounds();radius=bounds.sphere_radius
        scale=100000/(radius*mesh.get_editor_property('relative_scale3d').x)
        sky.set_actor_scale3d(u.Vector(scale,scale,scale))
        values={'colors determined by sun position':False,'sun brightness':0,'cloud opacity':0,'cloud speed':0,'stars brightness':0,
                'zenith Color':dict(r=12,g=12,b=12,a=1),'horizon color':dict(r=12,g=12,b=12,a=1),
                'cloud color':dict(r=12,g=12,b=12,a=1),'overall Color':dict(r=1,g=1,b=1,a=1),'refresh material':True}
        assert u.ToolsetLibrary.set_object_properties(sky,json.dumps(values))
        sky.call_method('RefreshMaterial')
        mesh=sky.get_component_by_class(u.StaticMeshComponent)
        sky.set_actor_enable_collision(False)
        for c in sky.get_components_by_class(u.PrimitiveComponent):
            c.set_collision_profile_name('NoCollision');c.set_editor_property('cast_shadow',False)
        light=sub.spawn_actor_from_class(u.SkyLight,u.Vector(0,0,900))
        light.set_actor_label(LIGHT);light.set_folder_path('LightStudy01/NeutralInspectionOnly')
        light.set_actor_enable_collision(False)
        c=light.get_component_by_class(u.SkyLightComponent);c.set_mobility(u.ComponentMobility.MOVABLE)
        c.set_editor_property('source_type',u.SkyLightSourceType.SLS_CAPTURED_SCENE)
        c.set_editor_property('sky_distance_threshold',50000.0)
        c.set_editor_property('intensity',1.0)
        c.set_editor_property('lower_hemisphere_is_black',False)
        c.recapture_sky()
        pp=sub.spawn_actor_from_class(u.PostProcessVolume,u.Vector(0,0,0))
        pp.set_actor_label(PP);pp.set_folder_path('LightStudy01/NeutralInspectionOnly');pp.set_actor_enable_collision(False)
        pp.set_editor_property('unbound',True);pp.set_editor_property('priority',10.0)
        settings=pp.get_editor_property('settings')
        assert reflection.settings()['r.Lumen.TranslucencyReflections.FrontLayer.Allow']==1
        settings.set_editor_property('override_lumen_front_layer_translucency_reflections',True)
        settings.set_editor_property('lumen_front_layer_translucency_reflections',True)
        pp.set_editor_property('settings',settings)
        return write('setup-A',dict(sky_parameters=values,sky_radius_cm=100000,sky_mesh=mesh.static_mesh.get_path_name(),sky_material=mesh.get_material(0).get_path_name(),sky_light=props(c,{}),postprocess=settings.export_text(),actors=[SKY,LIGHT,PP],renderer=reflection.settings(),state=guard(True)))
    if command=='record_setup_A':
        # Resume only the completed A setup after the first report held a stale BP component.
        guard(True)
        assert not (OUT/'setup-A.json').exists()
        actors={a.get_actor_label():a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()}
        assert all(n in actors for n in [SKY,LIGHT,PP])
        sky=actors[SKY];mesh=sky.get_component_by_class(u.StaticMeshComponent)
        scale=100000/(mesh.static_mesh.get_bounds().sphere_radius*mesh.get_editor_property('relative_scale3d').x)
        sky.set_actor_scale3d(u.Vector(scale,scale,scale))
        c=actors[LIGHT].get_component_by_class(u.SkyLightComponent);c.recapture_sky()
        return write('setup-A',dict(sky_parameters=props(sky,{}),sky_radius_cm=100000,sky_light=props(c,{}),postprocess=actors[PP].get_editor_property('settings').export_text(),actors=[SKY,LIGHT,PP],renderer=reflection.settings(),state=guard(True),report_recovery='Reacquired component after engine BP construction; corrected stock child scale before any A image.'))
    if command=='support_inspect':
        guard(True)
        result={}
        for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
            if a.get_actor_label() not in [SKY,LIGHT,PP]:continue
            result[a.get_actor_label()]=dict(actor=props(a,{}),components={c.get_name():props(c,{}) for c in a.get_components_by_class(u.ActorComponent)},collision=a.get_actor_enable_collision())
        write('support-live',result)
        return dict(actors=list(result),state=guard(True))
    if command=='save_reopen':
        guard(True)
        assert (OUT/'setup-A.json').exists()
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
        return write('save-reopen',snapshot('Reopened',True))
    if command=='preflight':
        guard(False,True)
        assert not u.EditorAssetLibrary.does_asset_exist(MAP)
        assert not (OUT/'Source').exists()
        result=snapshot('Source',False)
        result['renderer']=reflection.settings()
        result['sky_class']=u.load_class(None,'/Engine/EngineSky/BP_Sky_Sphere.BP_Sky_Sphere_C').get_path_name()
        result['sky_properties']=json.loads(u.ToolsetLibrary.list_struct_properties(u.load_class(None,result['sky_class'])))
        return dict(report='preflight.json',actors=result['actors'],state=write('preflight',result)['state'])
    if command=='create':
        guard(False,True)
        assert (OUT/'LiveBefore/MetalGlass-90.png').exists() and (OUT/'LiveBefore/C3-90.png').exists()
        assert not u.EditorAssetLibrary.does_asset_exist(MAP)
        assert not (work.ROOT/'Content/Maps/L_OpeningLobby_Architecture01_LightStudy01.umap').exists()
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).new_level_from_template(MAP,SOURCE)
        return write('created',dict(state=guard(True,True),source=SOURCE,destination=MAP,method='LevelEditorSubsystem.new_level_from_template',snapshot=snapshot('Template',True)))
    if command.startswith('capture:'):
        import architecture01_capture as capture
        _,folder,op,view=command.split(':')
        assert folder in ['LiveBefore','A','B','Final']
        assert op in ['prepare','camera','shoot','restore']
        assert view in capture.VIEWS or view in ['','gameplay']
        study=folder!='LiveBefore'
        guard(study,pie=op in ['camera','shoot'])
        with config(OUT/folder,study):result=getattr(capture,op)(view)
        if op=='shoot':
            p=OUT/folder/(view+'-camera.json');record=json.loads(p.read_text())
            record['renderer']=reflection.settings();record['inspection_setup']=folder
            p.write_text(json.dumps(record,indent=2))
        return result
    if command=='sky_schema':
        guard(True,True)
        cls=u.load_class(None,'/Engine/EngineSky/BP_Sky_Sphere.BP_Sky_Sphere_C')
        default=u.get_default_object(cls)
        return dict(properties=props(default,{}),methods=[n for n in dir(default) if any(k in n.lower() for k in ['sun','refresh','construct'])])
    if command.startswith('snapshot:'):
        name=command.split(':')[1];assert name in ['Reopened','FinalState']
        return snapshot(name,True)
    if command=='spawn_check':
        s=guard(True,True,True)
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        pawn=u.GameplayStatics.get_player_pawn(world,0);pc=u.GameplayStatics.get_player_controller(world,0)
        move=pawn.get_component_by_class(u.CharacterMovementComponent)
        capsule=pawn.get_component_by_class(u.CapsuleComponent)
        camera=pawn.get_component_by_class(u.CameraComponent)
        s.update(game_mode=u.GameplayStatics.get_game_mode(world).get_class().get_path_name(),movement_mode=str(move.movement_mode),speed=move.max_walk_speed,capsule_radius=capsule.get_unscaled_capsule_radius(),capsule_half_height=capsule.get_unscaled_capsule_half_height(),camera_fov=camera.field_of_view)
        assert s['possessed'] and s['game_mode']=='/Script/MeridianSquad.OpeningLobbyGameMode'
        assert move.movement_mode==u.MovementMode.MOVE_WALKING and s['speed']==360
        assert s['capsule_radius']==34 and s['capsule_half_height']==88 and s['camera_fov']==90
        return write('standing-spawn',s)
    if command=='final_state':
        import architecture01_capture as capture
        assert capture._settings is None
        return write('final-state',dict(state=guard(True,True),renderer=reflection.settings(),capture_restored=True))
    raise ValueError(command)
