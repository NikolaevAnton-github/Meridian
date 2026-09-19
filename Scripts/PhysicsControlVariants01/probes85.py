"""Focused deterministic two-clock oracle through the existing native timing probe."""
import json
from pathlib import Path
from client85 import epic, work
OUT=Path(__file__).resolve().parents[2]/'Saved/CombatSlice01/PhysicsControlVariants01/Worker'

def run():
    assert not epic('EditorToolset.EditorAppToolset','IsPIERunning')
    work('performance')
    try:
        epic('EditorToolset.EditorAppToolset','StartPIE',{'options':dict(bSimulate=False,playMode='PlayMode_InViewPort',warmupSeconds=.8)})
        reports=[]
        for name,rate,deltas,events in [
            ('Normal',1,[1/60]*60,[]),
            ('Slow',.65,[1/60]*60,[]),
            ('SlowLowFPS',.65,[.1]*10,[]),
            ('Transitions',1,[.1]*12,[dict(frame=3,type='player_rate',value=.65),dict(frame=3,type='scale',value=.25),dict(frame=8,type='player_rate',value=1),dict(frame=8,type='scale',value=1)])]:
            spec=dict(name='Candidate02-Timing'+name,kind='schedule',player_rate=rate,scale=.25 if rate<1 else 1,deltas=deltas,events=events,speed=1000)
            report=work('timing',json.dumps(spec))
            shots=report['rifle']['recent_shots']
            spacings=[b['action_time']-a['action_time'] for a,b in zip(shots,shots[1:])]
            checks=dict(action_spacing=all(abs(x-.085)<.00001 for x in spacings),
                ammo_conserved=report['rifle']['magazine']==30-len(shots),
                unique_ids=len({s['id'] for s in shots})==len(shots),
                clean=report['cleanup'],no_overload=report['world']['overload_frames']==0)
            if name!='Transitions':
                checks['manager_spacing']=all(abs((b['time']-a['time'])-.085/rate)<.00001 for a,b in zip(shots,shots[1:]))
                checks['residual_flight']=all(abs(b['age']-(report['world']['firing_clock']-b['birth_time'])*spec['scale'])<.00001 for b in report['world']['bullets'])
            reports.append(dict(name=name,checks=checks,shots=len(shots),action_spacings=spacings))
        contacts=work('probe','Candidate02-MultipleContacts')
        reports.append(dict(name='MultipleContacts',checks={k:v for k,v in contacts.items() if isinstance(v,bool)}))
        path=OUT/'focused-probes02.json'; assert not path.exists()
        path.write_text(json.dumps(reports,indent=2),encoding='utf-8')
        print(json.dumps(reports,indent=2))
    finally:
        if epic('EditorToolset.EditorAppToolset','IsPIERunning'): epic('EditorToolset.EditorAppToolset','StopPIE')
        work('performance','restore')

if __name__=='__main__': run()
