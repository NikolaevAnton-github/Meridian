"""Check the central demo and every NGD specimen across the production F6 input."""
import json
import time
from pathlib import Path
import unreal as u

OUT=Path('D:/devgames/MeridianSquad/Saved/LobbyColumnsPerf02')
w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
assert w
pawn=u.GameplayStatics.get_player_pawn(w,0)
def snapshot():
    result={}
    for a in u.GameplayStatics.get_all_actors_of_class(w,u.Actor):
        prop=a.get_component_by_class(u.NGDPropComponent)
        if not prop:continue
        p=json.loads(prop.get_state()); clad=a.get_component_by_class(u.DemoColumnCladding)
        result[p['id']]=dict(prop=p,lobby=a.actor_has_tag('LobbyColumns01'),
                           cladding=json.loads(clad.get_state()) if clad else None)
    return result
report=dict(before=snapshot()); stage=0; started=time.monotonic(); handle=None
def tick(delta):
    global stage,handle
    elapsed=time.monotonic()-started
    if stage==0 and elapsed>=1:
        pawn.probe_key('F6',1.,True);stage=1
    elif stage==1 and elapsed>=1.5:
        pawn.probe_key('F6',0.,False);stage=2
    elif stage==2 and elapsed>=4:
        report['after']=snapshot()
        before=report['before']; after=report['after']
        report['same_ids']=set(before)==set(after)
        report['all_ready']=all(r['prop']['ready'] for r in after.values())
        report['all_generations_advanced']=all(r['prop']['reset_generation']==before[k]['prop']['reset_generation']+1 for k,r in after.items())
        report['non_lobby_not_pooled']=all(not r['cladding'] or r['cladding']['shared_tiles']==0 for r in after.values() if not r['lobby'])
        report['non_lobby_attached_preserved']=all(not r['cladding'] or r['cladding']['attached']==before[k]['cladding']['attached'] for k,r in after.items() if not r['lobby'])
        (OUT/'reset-all03.json').write_text(json.dumps(report,indent=2))
        u.unregister_slate_post_tick_callback(handle)
handle=u.register_slate_post_tick_callback(tick)
print(json.dumps(dict(started=True,props=len(report['before']),duration=4)))
