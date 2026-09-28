"""Run after representative damage; selected GC and render/support transitions only."""
import json
import re
import traceback
from pathlib import Path
import unreal as u

OUT=Path('D:/devgames/MeridianSquad/Saved/DestructionScaling01')

def run(name):
    w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    system=u.find_object(w,'DestructionFragmentWorld_0')
    report={'name':name,'checks':{},'samples':{}}
    path=OUT/(name+'.json')
    assert not path.exists()
    def sample(label):
        state=json.loads(system.get_state())
        report['samples'][label]=state
        return {x['handle']:x for x in state['fragments']}
    def check(label,value):
        report['checks'][label]=bool(value)
        assert value,label
    def position(row):
        return tuple(float(x) for x in re.findall(r'[-+]?\d*\.?\d+',row['position']))
    initial=sample('initial')
    concrete=next(x for x in initial.values() if x['local']<0)
    selected=concrete['handle']
    report['selected_concrete']=selected
    check('concrete_hold_queued',system.hold(selected)=='Queued')
    check('concrete_move_queued',system.move_held(selected,u.Transform(location=u.Vector(2200,700,400)))=='Queued')
    # Independent pieces away from the fired column, using two different owners.
    columns=[a for a in u.GameplayStatics.get_all_actors_of_class(w,u.Actor) if a.actor_has_tag('LobbyColumns01')]
    owners=[a.get_component_by_class(u.DemoColumnCladding) for a in columns[-2:]]
    cube=u.load_asset('/Engine/BasicShapes/Cube')
    lower=system.spawn_verification_fragment(owners[0],cube,u.Transform(location=u.Vector(2200,200,51)))
    upper=system.spawn_verification_fragment(owners[1],cube,u.Transform(location=u.Vector(2200,200,153)))
    lower_handle=system.select(lower.static_mesh_component,-1)
    upper_handle=system.select(upper.static_mesh_component,-1)
    material=u.load_asset('/Engine/EngineMaterials/DefaultMaterial')
    started=u.GameplayStatics.get_time_seconds(w)
    stage=0;callback=None;entered=False
    def tick(delta):
        nonlocal stage,callback,entered
        if entered:return
        entered=True
        t=u.GameplayStatics.get_time_seconds(w)-started
        try:
            if stage==0 and t>=.5:
                state=sample('concrete_held')
                p=position(state[selected])
                check('concrete_selected_pose',sum((a-b)**2 for a,b in zip(p,(2200,700,400)))<1)
                check('only_selected_held',[x['handle'] for x in state.values() if x['state']==3]==[selected])
                check('concrete_release_queued',system.release(selected,u.Vector(0,0,300),u.Vector(0,1,0))=='Queued')
                stage=1
            elif stage==1 and t>=.8:
                state=sample('concrete_released')
                check('concrete_release_moves',position(state[selected])[2]>410 and state[selected]['state']==1)
                check('concrete_second_impulse',system.impulse(selected,u.Vector(0,0,250))=='Queued')
                stage=2
            elif stage==2 and t>=4:
                state=sample('supported')
                check('lower_support_registered',lower_handle in state and state[upper_handle]['supports']>0)
                lower.destroy_actor()
                stage=3
            elif stage==3 and t>=5:
                state=sample('deleted_support')
                check('deleted_support_wakes',upper.get_actor_location().z<120)
                check('deleted_handle_stale',system.impulse(lower_handle,u.Vector())=='Stale')
                check('render_mapping_before',json.loads(system.get_state())['render_mismatches']==0)
                upper.static_mesh_component.set_material(0,material)
                system.hold(upper_handle)
                system.move_held(upper_handle,u.Transform(location=u.Vector(500,1400,180)))
                stage=4
            elif stage==4 and t>=5.5:
                sample('material_and_cell')
                check('cell_and_material_mapping',json.loads(system.get_state())['render_mismatches']==0)
                check('compatible_material_pooled',not upper.static_mesh_component.is_visible())
                upper.static_mesh_component.set_render_custom_depth(True)
                stage=5
            elif stage==5 and t>=6:
                sample('fallback')
                check('custom_depth_original_fallback',upper.static_mesh_component.is_visible())
                upper.static_mesh_component.set_render_custom_depth(False)
                stage=6
            elif stage==6 and t>=6.5:
                check('fallback_returns_to_pool',not upper.static_mesh_component.is_visible())
                owners[1].get_owner().destroy_actor()
                stage=7
            elif stage==7 and t>=7:
                sample('owner_deleted')
                check('deleted_owner_handle_stale',system.impulse(upper_handle,u.Vector())=='Stale')
                check('render_mapping_after',json.loads(system.get_state())['render_mismatches']==0)
                report['complete']=True
                path.write_text(json.dumps(report,indent=2))
                u.unregister_slate_post_tick_callback(callback)
        except Exception:
            report['error']=traceback.format_exc()
            path.write_text(json.dumps(report,indent=2))
            u.unregister_slate_post_tick_callback(callback)
        finally:entered=False
    callback=u.register_slate_post_tick_callback(tick)
    print(json.dumps({'scheduled':name,'simulation_seconds':7}))
