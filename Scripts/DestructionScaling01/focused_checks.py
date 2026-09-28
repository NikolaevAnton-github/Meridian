"""Transient PIE checks for selected bodies, cross-owner support, pooling and F6."""
import json
import traceback
from pathlib import Path
import unreal as u

OUT=Path('D:/devgames/MeridianSquad/Saved/DestructionScaling01')

def run(name):
    w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    assert w
    system=u.find_object(w,'DestructionFragmentWorld_0')
    assert system
    columns=[a for a in u.GameplayStatics.get_all_actors_of_class(w,u.Actor) if a.actor_has_tag('LobbyColumns01')]
    owners=[a.get_component_by_class(u.DemoColumnCladding) for a in columns[:2]]
    cube=u.load_asset('/Engine/BasicShapes/Cube')
    u.SystemLibrary.execute_console_command(w,'msq.Destruction.Parallel 2')
    pieces=[]
    handles=[]
    report={'name':name,'checks':{},'samples':{}}
    def spawn(owner,location,scale=(1,1,1)):
        actor=system.spawn_verification_fragment(owner,cube,u.Transform(location=u.Vector(*location),scale=u.Vector(*scale)))
        assert actor
        pieces.append(actor)
        handles.append(system.select(actor.static_mesh_component,-1))
        assert handles[-1]>0
        return actor
    # Clear floor in the lobby; exact cube hulls establish unambiguous support.
    spawn(owners[0],(2200,200,51))
    spawn(owners[1],(2200,200,153))
    thin=spawn(owners[0],(1900,200,200),(1,1,.02))
    assert system.impulse(handles[2],u.Vector(0,0,-2000))=='Applied'
    performance=u.get_default_object(u.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
    old_throttle=performance.get_editor_property('bThrottleCPUWhenNotForeground')
    performance.set_editor_property('bThrottleCPUWhenNotForeground',False)
    started=u.GameplayStatics.get_time_seconds(w); stage=0; callback=None; entered=False
    def sample(label):
        state=json.loads(system.get_state())
        report['samples'][label]=state
        return {x['handle']:x for x in state['fragments']}
    def check(label,passed):
        report['checks'][label]=bool(passed)
        assert passed,label
    def tick(delta):
        nonlocal stage,callback,entered
        if entered:return
        entered=True
        # Physics assertions use simulation time: an unfocused editor may advance
        # only a fraction of wall time. Never mistake throttling for a failed wake.
        t=u.GameplayStatics.get_time_seconds(w)-started
        try:
            if stage==0 and t>=4:
                s=sample('settled')
                check('thin_ccd_above_floor',thin.get_actor_location().z>-.5)
                check('cross_owner_support',s[handles[1]]['supports']>0)
                check('selected_hold',system.hold(handles[0])=='Applied')
                check('move_support',system.move_held(handles[0],u.Transform(location=u.Vector(2500,200,51)))=='Applied')
                stage=1
            elif stage==1 and t>=5:
                sample('support_moved')
                check('dependent_falls',pieces[1].get_actor_location().z<120)
                check('release_selected',system.release(handles[0],u.Vector(0,0,250),u.Vector(0,1,0))=='Applied')
                stage=2
            elif stage==2 and t>=5.4:
                check('release_moves',pieces[0].get_actor_location().z>51)
                check('unsupported_release',system.release(handles[1],u.Vector(),u.Vector())=='UnsupportedState')
                stage=3
            elif stage==3 and t>=14:
                s=sample('beyond_old_expiry')
                check('persists_beyond_12_seconds',all(h in s for h in handles))
                check('second_impulse',system.impulse(handles[2],u.Vector(0,0,180))=='Applied')
                # Reset a held body while pure jobs/physics commands may be pending.
                system.hold(handles[1])
                pawn=u.GameplayStatics.get_player_pawn(w,0)
                pawn.probe_key('F6',1.,True)
                pawn.probe_key('F6',0.,False)
                stage=4
            elif stage==4 and t>=16:
                s=sample('reset')
                check('old_handles_stale',all(system.impulse(h,u.Vector(1,0,0))=='Stale' for h in handles))
                check('no_old_held_body',not any(x['state']==3 for x in s.values()))
                new_columns=[a for a in u.GameplayStatics.get_all_actors_of_class(w,u.Actor) if a.actor_has_tag('LobbyColumns01')]
                new_owner=new_columns[0].get_component_by_class(u.DemoColumnCladding)
                before=json.loads(system.get_state())
                actor=system.spawn_verification_fragment(new_owner,cube,u.Transform(location=u.Vector(2200,200,80)))
                new_handle=system.select(actor.static_mesh_component,-1)
                check('reused_new_identity',new_handle>max(handles))
                check('pool_reuses_body',json.loads(system.get_state())['reused']>before['reused'])
                check('immediate_hit_after_reuse',system.impulse(new_handle,u.Vector(0,0,150))=='Applied')
                stage=5
            elif stage==5 and t>=17:
                state=json.loads(system.get_state())
                check('serial_parallel_compared',state['parallel_jobs']>0 and state['serial_comparisons']>0)
                report['complete']=True
                u.SystemLibrary.execute_console_command(w,'msq.Destruction.Parallel 1')
                performance.set_editor_property('bThrottleCPUWhenNotForeground',old_throttle)
                (OUT/(name+'.json')).write_text(json.dumps(report,indent=2))
                u.unregister_slate_post_tick_callback(callback)
        except Exception:
            report['error']=traceback.format_exc()
            (OUT/(name+'.json')).write_text(json.dumps(report,indent=2))
            u.SystemLibrary.execute_console_command(w,'msq.Destruction.Parallel 1')
            performance.set_editor_property('bThrottleCPUWhenNotForeground',old_throttle)
            u.unregister_slate_post_tick_callback(callback)
        finally:entered=False
    callback=u.register_slate_post_tick_callback(tick)
    print(json.dumps({'scheduled':name,'duration':17}))
