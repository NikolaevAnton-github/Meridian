"""Native stills and real readiness using the established capture implementation."""
import json
import types
import unreal as u
from painterfloor01_unreal import ROOT,OUT,SOURCE,MAP,guard,write,settings
from stage1_tools import state

source=(ROOT/'Scripts/OpeningLobby/reworka01_capture.py').read_text()
source=source.replace('L_OpeningLobby_ArchitectureReworkA01','L_OpeningLobby_')
cap=types.ModuleType('painterfloor01_existing_capture')
exec(compile(source,str(ROOT/'Scripts/OpeningLobby/reworka01_capture.py'),'exec'),cap.__dict__)
cap.VIEWS={'entrance-90':(-1850,0,0,-6), 'inner-90':(1850,0,180,-6), 'floor-near-90':(-1050,0,20,-42), 'strip-boundary-90':(-600,260,0,-35), 'long-floor-90':(-1200,0,0,-14)}
active=None
throttle_before=None

def runtime():
    world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    assert world
    pc=u.GameplayStatics.get_player_controller(world,0)
    pawn=u.GameplayStatics.get_player_pawn(world,0)
    manager=u.GameplayStatics.get_player_camera_manager(world,0)
    loc=manager.get_camera_location()
    rot=manager.get_camera_rotation()
    return dict(world_seconds=u.GameplayStatics.get_time_seconds(world),
        camera_xyz=[loc.x,loc.y,loc.z],camera_rotation=[rot.pitch,rot.yaw,rot.roll],
        hfov=manager.get_fov_angle(),possessed=pawn.get_controller()==pc,
        standing=pawn.get_component_by_class(u.CharacterMovementComponent).is_moving_on_ground(),
        state=state())

def run(operation,argument):
    global active,throttle_before
    folder,_,view=argument.partition(':')
    assert folder in ['Before','Trial01','Final']
    candidate=True
    guard(candidate,clean=True,pie=operation in ['camera','ready','shoot','standing','diagnostic'])
    cap.OUT=OUT/folder
    cap.OUT.mkdir(parents=True,exist_ok=True)
    cap.MAP=MAP if candidate else SOURCE
    cap.guard=lambda clean=False:guard(candidate,clean=clean)
    if operation=='prepare':
        assert active is None
        active=folder
        throttle_before=u.SystemLibrary.get_console_variable_int_value('Slate.bAllowThrottling')
        return cap.prepare()
    assert active==folder
    if operation in ['standing','diagnostic']:
        value=runtime()
        if operation=='standing':
            assert value['world_seconds']>1 and value['standing'] and value['possessed'],value
            return write(folder+'/standing-possession',value)
        return value
    if operation=='ready':
        value=runtime()
        requested=json.loads((cap.OUT/(view+'-camera.json')).read_text())
        value['ready']=value['world_seconds']>1 and max(abs(a-b) for a,b in zip(value['camera_xyz'],requested['requested_xyz_cm']))<1 and abs(value['hfov']-90)<.01
        return value
    if operation=='shoot':
        ready=run('ready',argument)
        assert ready['ready'],ready
        record=cap.shoot(view)
        record.update(runtime=ready,renderer=settings(),lighting='Original owner lights and postprocess; no adjustments',
            edits='None. Native 1920x1080 HighResShot PNG.',pose_scope='Still comparison only; not route movement evidence')
        (cap.OUT/(view+'-camera.json')).write_text(json.dumps(record,indent=2))
        return record
    result=getattr(cap,operation)(view)
    if operation=='restore':
        assert u.SystemLibrary.get_console_variable_int_value('Slate.bAllowThrottling')==throttle_before
        result['slate_throttle_unchanged']=throttle_before
        (cap.OUT/'capture-settings-restored.json').write_text(json.dumps(result,indent=2))
        active=None
    return result
