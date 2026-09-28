"""Restore the controller's original editor state without saving assets/config."""
import json
from pathlib import Path
import unreal as u

OUT=Path('D:/devgames/MeridianSquad/Saved/LobbyColumnsPerf02')
b=json.loads((OUT/'controller-before.json').read_text())
s=json.loads((OUT/'runtime-settings01.json').read_text())
es=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert es.get_game_world() is None
if (OUT/'editor-cap-original.json').exists():
    cap=json.loads((OUT/'editor-cap-original.json').read_text())
    engine=es.get_outer();bounds=engine.get_editor_property('SmoothedFrameRateRange')
    bounds.upper_bound.value=cap['upper'];engine.set_editor_property('SmoothedFrameRateRange',bounds)
w=es.get_editor_world()
es.set_level_viewport_camera_info(u.Vector(*b['camera']['location']),u.Rotator(
    pitch=b['camera']['rotation'][0],yaw=b['camera']['rotation'][1],roll=b['camera']['rotation'][2]))
prefs=u.get_default_object(u.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
prefs.set_editor_property('bThrottleCPUWhenNotForeground',b['throttle'])
for k in ['t.MaxFPS','r.VSync','r.ScreenPercentage']:
    u.SystemLibrary.execute_console_command(w,k+' '+str(s[k]))
for c in ['msq.Lobby.SharedFacing 2','msq.Lobby.ActiveFacing 1','msq.Projectile.BlockerRegistry 1']:
    u.SystemLibrary.execute_console_command(w,c)
loc,rot=es.get_level_viewport_camera_info()
r=dict(project=u.Paths.project_dir(),world=w.get_path_name(),game_world=str(es.get_game_world()),
       throttle=prefs.get_editor_property('bThrottleCPUWhenNotForeground'),
       camera=dict(location=[loc.x,loc.y,loc.z],rotation=[rot.pitch,rot.yaw,rot.roll]),
       dirty_maps=[str(x) for x in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()],
       dirty_content=[str(x) for x in u.EditorLoadingAndSavingUtils.get_dirty_content_packages()],
       editor_pool_actors=sum(a.actor_has_tag('LobbyFacingRenderOnly') for a in u.GameplayStatics.get_all_actors_of_class(w,u.Actor)))
r['editor_fps_upper_bound']=es.get_outer().get_editor_property('SmoothedFrameRateRange').upper_bound.value
assert not r['dirty_maps'] and not r['dirty_content'] and r['editor_pool_actors']==0
assert all(abs(a-bb)<1.e-5 for key in ['location','rotation'] for a,bb in zip(r['camera'][key],b['camera'][key]))
(OUT/'cleanup-final05.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r))
