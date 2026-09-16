"""Reuse FunctionalBuild01 native still capture with guarded task-only paths."""
import json
import types
import unreal as u
from materialintegration01_unreal import ROOT, OUT, MAP, SOURCE, guard, settings

# The established adapter supplies the exact four approved comparison cameras.
# Permit either named task map in its legacy camera assertion; guard below is exact.
source=(ROOT/'Scripts/OpeningLobby/functionalbuild01_capture.py').read_text()
source=source.replace("'L_OpeningLobby_FunctionalBuild01'", "'L_OpeningLobby_'")
module=types.ModuleType('materialintegration01_existing_capture')
exec(compile(source,str(ROOT/'Scripts/OpeningLobby/functionalbuild01_capture.py'),'exec'),module.__dict__)
capture=module._capture
capture.VIEWS.update({'stone-column-90':(-1660,0,30,12), 'floor-strip-90':(-900,0,0,-38),
    'checkpoint-metal-90':(-1700,120,180,-5), 'service-door-90':(-1680,1000,180,5)})
VIEWS=['entrance-90','inner-90','context-90','aisle-90','stone-column-90','floor-strip-90','checkpoint-metal-90','elevator-detail-90','service-door-90']
active_folder=None

def run(operation, argument):
    global active_folder
    folder, _, view=argument.partition(':')
    assert folder in ['Before','Pilot','Final']
    candidate=folder!='Before'
    guard(candidate,clean=True,pie=operation in ['camera','shoot','ready'])
    capture.OUT=OUT/folder
    capture.OUT.mkdir(parents=True,exist_ok=True)
    capture.MAP=MAP if candidate else SOURCE
    capture.guard=lambda clean=False:guard(candidate,clean=clean)
    if operation=='prepare':
        assert active_folder is None
        active_folder=folder
    else:
        assert active_folder==folder
    if operation=='ready':
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        manager=u.GameplayStatics.get_player_camera_manager(world,0)
        pos=manager.get_camera_location()
        record=json.loads((capture.OUT/(view+'-camera.json')).read_text())
        ready=u.GameplayStatics.get_time_seconds(world)>1 and max(abs(a-b) for a,b in zip([pos.x,pos.y,pos.z],record['requested_xyz_cm']))<1
        return dict(ready=ready,world_seconds=u.GameplayStatics.get_time_seconds(world),actual_xyz_cm=[pos.x,pos.y,pos.z])
    result=getattr(capture,operation)(view)
    if operation=='shoot':
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        exposure={}
        for a in u.GameplayStatics.get_all_actors_of_class(world,u.PostProcessVolume):
            if isinstance(a,u.PostProcessVolume):
                pp=a.get_editor_property('settings')
                exposure[a.get_actor_label()]={n:str(pp.get_editor_property(n)) for n in ['auto_exposure_method','auto_exposure_bias','auto_exposure_apply_physical_camera_exposure','override_auto_exposure_method','override_auto_exposure_bias']}
        result.update(renderer=settings(), actual_postprocess_exposure=exposure,
            source_capture_helper='Scripts/OpeningLobby/functionalbuild01_capture.py', edits='None; native HighResShot PNG',
            lighting='Original owner source lights and postprocess; no diagnostic lighting')
        (capture.OUT/(view+'-camera.json')).write_text(json.dumps(result,indent=2))
    if operation=='restore':active_folder=None
    return result
