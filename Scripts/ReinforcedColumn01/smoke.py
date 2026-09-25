"""Short normal-speed real-rifle evidence; the caller collects the completion file."""
import json
import time
import traceback
from pathlib import Path
import unreal as u

OUT=Path('D:/devgames/MeridianSquad/Saved/ReinforcedColumn01/Candidate01')

def objects():
    w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    assert w
    p=u.GameplayStatics.get_player_pawn(w,0)
    a=next(a for a in u.GameplayStatics.get_all_actors_of_class(w,u.Actor) if a.get_component_by_class(u.NGDPropComponent) and str(a.get_component_by_class(u.NGDPropComponent).object_id)=='RC01_ReinforcedColumn')
    return w,p,a,a.get_component_by_class(u.GeometryCollectionComponent)

def state():
    w,p,a,gc=objects()
    core=next(a for a in u.GameplayStatics.get_all_actors_of_class(w,u.StaticMeshActor) if a.get_name()=='StaticMeshActor_35')
    view,rot=u.GameplayStatics.get_player_controller(w,0).get_player_view_point()
    return dict(prop=json.loads(a.get_component_by_class(u.NGDPropComponent).get_state()),rifle=json.loads(p.get_component_by_class(u.CombatRifleComponent).get_rifle_state()),
        global_dilation=u.GameplayStatics.get_global_time_dilation(w),player_dilation=p.custom_time_dilation,
        core_transform=str(core.get_actor_transform()),core_bounds=str(core.get_actor_bounds(True)),
        view=[view.x,view.y,view.z],rotation=[rot.pitch,rot.yaw,rot.roll],player_location=str(p.get_actor_location()),
        pieces=[dict(location=[t.translation.x,t.translation.y,t.translation.z],scale=[t.scale3d.x,t.scale3d.y,t.scale3d.z]) for t in gc.get_current_transforms()])

def run(name,events,duration):
    path=OUT/(name+'.json')
    assert not path.exists()
    w,p,a,gc=objects()
    assert u.GameplayStatics.get_global_time_dilation(w)==1 and p.custom_time_dilation==1
    report=dict(method='Normal-speed PlayerController input -> EnhancedInput -> actual rifle and finite projectile',events=events,before=state(),samples=[])
    started=time.monotonic()
    index=0
    last_sample=-1
    handle=None
    in_tick=False
    def tick(delta):
        nonlocal index,handle,last_sample,in_tick
        if in_tick: return
        in_tick=True
        try:
            elapsed=time.monotonic()-started
            w,p,a,gc=objects()
            while index<len(events) and elapsed>=events[index][0]:
                _,op,*args=events[index]
                if op=='position': p.set_actor_location(u.Vector(*args[0]),False,True)
                elif op=='aim': assert u.NGDTools.aim_player(w,u.Vector(*args[0]))
                elif op=='fire': assert u.NGDTools.rifle_input(w,args[0])
                elif op=='key': p.probe_key(args[0],1. if args[1] else 0.,args[1])
                elif op=='capture': u.AutomationLibrary.take_high_res_screenshot(1280,720,str(OUT/(args[0]+'.png')))
                elif op=='trace':
                    report.setdefault('traces',[]).append(dict(time=elapsed,result=json.loads(u.NGDTools.sweep(w,u.Vector(*args[0]),u.Vector(*args[1]),.25))))
                else: raise ValueError(op)
                index+=1
            if elapsed-last_sample>.25:
                report['samples'].append(dict(elapsed=elapsed,**state()))
                last_sample=elapsed
            if elapsed>=duration:
                u.NGDTools.rifle_input(w,False)
                report['after']=state()
                path.write_text(json.dumps(report,indent=2),encoding='utf-8')
                u.unregister_slate_post_tick_callback(handle)
        except Exception:
            u.NGDTools.rifle_input(w,False)
            report['error']=traceback.format_exc()
            path.write_text(json.dumps(report,indent=2),encoding='utf-8')
            u.unregister_slate_post_tick_callback(handle)
        finally:
            in_tick=False
    handle=u.register_slate_post_tick_callback(tick)
    print(json.dumps(dict(scheduled=name,duration=duration)))
