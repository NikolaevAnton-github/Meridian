"""Explicit 1920x1080 PIE evidence with transient reference FOV overrides."""
import json
import unreal as u
from stage1_tools import state
from layout02_verification import ROOT,require_project

OUT = ROOT/'Saved/OpeningLobby/Layout03'
MAP = '/Game/Maps/L_OpeningLobby_Layout03'
_settings = None
VIEWS = {'C1-90':(-1900,0,172,0,0),'C1-75':(-1900,0,172,0,0),
         'C2-90':(1900,0,172,180,0),'C2-75':(1900,0,172,180,0),
         'C3-90':(-1400,350,172,180,0),'C3-context-90':(-1260,350,172,180,15),
         'EndEntrance-110':(-2370,0,172,180,25),'EndInner-110':(2370,0,172,0,25)}

def prepare():
    global _settings
    s = state()
    require_project(s['project'])
    assert not s['pie'] and s['level'].split('.')[0] == MAP
    assert _settings is None
    obj = u.get_default_object(u.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
    names = ['NewWindowWidth','NewWindowHeight','CenterNewWindow','NewWindowPosition']
    _settings = obj,{name:obj.get_editor_property(name) for name in names}
    obj.set_editor_property('NewWindowWidth',1920)
    obj.set_editor_property('NewWindowHeight',1080)
    obj.set_editor_property('CenterNewWindow',True)
    return 'Transient floating PIE size 1920x1080; original settings retained in memory.'

def restore():
    global _settings
    assert not state()['pie']
    if _settings:
        obj,values = _settings
        for name,value in values.items():
            obj.set_editor_property(name,value)
        _settings = None
    return 'Original play settings restored without saving configuration.'

def capture(view):
    s = state()
    require_project(s['project'])
    assert s['pie'] and 'L_OpeningLobby_Layout03' in s['level']
    world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    pc = u.GameplayStatics.get_player_controller(world,0)
    pawn = u.GameplayStatics.get_player_pawn(world,0)
    camera = pawn.get_component_by_class(u.CameraComponent)
    assert camera.field_of_view == 90
    if view == 'gameplay':
        pc.set_view_target_with_blend(pawn,0.)
        u.SystemLibrary.execute_console_command(world,'fov 90',pc)
        return 'Possessed player camera active; gameplay FOV unchanged at 90.'
    assert view in VIEWS
    spec = VIEWS[view]
    fov = float(view.split('-')[-1])
    pc.set_view_target_with_blend(pawn,0.)
    # FOV is a camera-manager console override in this PIE world only.
    # The pawn component and all player defaults retain their original 90 degrees.
    u.SystemLibrary.execute_console_command(world,'fov '+str(fov),pc)
    record = dict(view=view,map=MAP,requested_xyz_cm=spec[:3],yaw=spec[3],pitch=spec[4],roll=0,horizontal_fov=fov,
                  fov_convention='Horizontal at explicit 1920x1080 PIE aspect',resolution=[1920,1080],
                  gameplay_fov=camera.field_of_view,eye_height_cm=172,
                  camera_type='Possessed first-person gameplay camera' if fov == 90 else ('Supplemental end-band inspection FOV override; pawn component remains 90' if view.startswith('End') else 'Reference-only PIE camera-manager FOV override; pawn component remains 90'),
                  estimate_adjustment='Supplemental eye-level end-band visibility view; 110-degree lens is not gameplay or reference matching' if view.startswith('End') else ('C3 context moves X from -14 to -12.6 m and pitch from 0 to +15 degrees; eye height retained; geometry unchanged' if 'context' in view else None))
    (OUT/(view+'-camera.json')).write_text(json.dumps(record,indent=2))
    return json.dumps(record)

def shoot(view):
    assert view in VIEWS
    world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    assert world
    pc = u.GameplayStatics.get_player_controller(world,0)
    manager = u.GameplayStatics.get_player_camera_manager(world,0)
    pos,rot = manager.get_camera_location(),manager.get_camera_rotation()
    path = OUT/(view+'-camera.json')
    record = json.loads(path.read_text())
    record.update(actual_xyz_cm=[pos.x,pos.y,pos.z],actual_rotation=[rot.pitch,rot.yaw,rot.roll],actual_hfov=manager.get_fov_angle())
    path.write_text(json.dumps(record,indent=2))
    u.SystemLibrary.execute_console_command(world,'HighResShot 1920x1080 filename="'+str(OUT/(view+'.png'))+'"')
    return 'Explicit 1920x1080 capture requested: '+view

def lighting():
    s = state()
    require_project(s['project'])
    assert not s['pie'] and s['level'].split('.')[0] == MAP
    assert not s['dirty_content'] and not s['dirty_maps']
    actors = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
    pp = next(a for a in actors if a.get_actor_label() == 'Layout03NeutralExposure')
    settings = pp.get_editor_property('settings')
    settings.set_editor_property('auto_exposure_bias',-5.)
    pp.set_editor_property('settings',settings)
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    return 'Layout03 manual exposure reduced from -3 to -5 EV after first capture; geometry unchanged.'
