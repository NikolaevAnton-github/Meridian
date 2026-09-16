"""Candidate adapter of Architecture01 native PIE captures; no persistent settings."""
import json
import unreal as u
from stage1_tools import state
from reworka01_data import OUT,MAP,D
from reworka01_unreal import guard

_settings=None
VIEWS={'C1-90':(-1900,0,0,0),'C2-90':(1900,0,180,0),'C2-75':(1900,0,180,0),
       'C3-context-90':(-1260,350,180,15),
       'A-oblique-106':(-1400,350,192,16),'A-oblique-90':(-1400,350,192,16),
       'Terminal-soffit-90':(-2260,1000,195,35),'Terminal-junction-90':(-2400,300,160,35)}

def prepare(_=''):
    global _settings
    guard(clean=True);assert _settings is None
    obj=u.get_default_object(u.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
    throttle=u.get_default_object(u.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
    names=['NewWindowWidth','NewWindowHeight','CenterNewWindow','NewWindowPosition']
    _settings=(obj,{n:obj.get_editor_property(n) for n in names},throttle,throttle.get_editor_property('bThrottleCPUWhenNotForeground'))
    obj.set_editor_property('NewWindowWidth',1920);obj.set_editor_property('NewWindowHeight',1080)
    obj.set_editor_property('CenterNewWindow',True);throttle.set_editor_property('bThrottleCPUWhenNotForeground',False)
    (OUT/'capture-settings-before.json').write_text(json.dumps(dict(play={k:str(v) for k,v in _settings[1].items()},throttle=_settings[3]),indent=2))
    return dict(prepared=True,resolution=[1920,1080])

def camera(view):
    s=state();assert s['pie'] and 'L_OpeningLobby_ArchitectureReworkA01' in s['level']
    world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    pc=u.GameplayStatics.get_player_controller(world,0);pawn=u.GameplayStatics.get_player_pawn(world,0)
    component=pawn.get_component_by_class(u.CameraComponent);assert component.field_of_view==90
    if view=='gameplay':
        u.SystemLibrary.execute_console_command(world,'fov 90',pc);return dict(gameplay_hfov=90)
    x,y,yaw,pitch=VIEWS[view]
    pawn.set_actor_location(u.Vector(x,y,100),False,True)
    pc.set_control_rotation(u.Rotator(pitch=pitch,yaw=yaw,roll=0))
    fov=float(view.split('-')[-1]);u.SystemLibrary.execute_console_command(world,'fov '+str(fov),pc)
    record=dict(view=view,map=MAP,requested_xyz_cm=[x,y,172],yaw=yaw,pitch=pitch,horizontal_fov=fov,
        resolution=[1920,1080],gameplay_fov=90,exposure='Unchanged Layout03 manual exposure: bias -5, physical camera exposure disabled',
        camera_type='Drawing comparison (106 degree lens)' if fov==106 else ('Reference comparison' if fov==75 else 'Gameplay HFOV'),
        movement_evidence=False,pose_method='Transient possessed-pawn placement only for still evidence')
    (OUT/(view+'-camera.json')).write_text(json.dumps(record,indent=2));return record

def shoot(view):
    assert view in VIEWS
    world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world();assert world
    manager=u.GameplayStatics.get_player_camera_manager(world,0)
    pos=manager.get_camera_location();rot=manager.get_camera_rotation()
    path=OUT/(view+'-camera.json');record=json.loads(path.read_text())
    record.update(actual_xyz_cm=[pos.x,pos.y,pos.z],actual_rotation=[rot.pitch,rot.yaw,rot.roll],actual_hfov=manager.get_fov_angle())
    path.write_text(json.dumps(record,indent=2))
    u.SystemLibrary.execute_console_command(world,'HighResShot 1920x1080 filename="'+str(OUT/(view+'.png'))+'"')
    return record

def restore(_=''):
    global _settings
    assert not state()['pie']
    if _settings:
        obj,values,throttle,old=_settings
        for name,value in values.items():obj.set_editor_property(name,value)
        throttle.set_editor_property('bThrottleCPUWhenNotForeground',old)
        report=dict(play={k:str(obj.get_editor_property(k)) for k in values},throttle=throttle.get_editor_property('bThrottleCPUWhenNotForeground'),
            matched=all(obj.get_editor_property(k)==v for k,v in values.items()) and throttle.get_editor_property('bThrottleCPUWhenNotForeground')==old)
        (OUT/'capture-settings-restored.json').write_text(json.dumps(report,indent=2));_settings=None
        assert report['matched'];return report
    return dict(restored=True)
