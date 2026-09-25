"""Compact read-only summaries of the immutable live input traces."""
import json
import sys
from pathlib import Path
OUT = Path('D:/devgames/MeridianSquad/Saved/LobbyPlaytestFix01/Candidate01')
for name in sys.argv[1:]:
    p=json.loads((OUT/(name+'.json')).read_text())
    if 'error' in p:
        print(json.dumps(dict(name=name,error=p['error'])))
        continue
    b,a=p['before'],p['after']
    shots=[s for s in a['rifle']['recent_shots'] if s['id']>b['rifle']['last_shot_id']]
    intervals=[round(y['action_time']-x['action_time'],6) for x,y in zip(shots,shots[1:])]
    print(json.dumps(dict(name=name,shots=a['rifle']['shots']-b['rifle']['shots'],presses=a['rifle']['input_presses']-b['rifle']['input_presses'],
        releases=a['rifle']['input_releases']-b['rifle']['input_releases'],magazine=a['rifle']['magazine'],reserve=a['rifle']['reserve'],
        transfers=a['rifle']['transfers']-b['rifle']['transfers'],automatic=a['rifle']['automatic'],
        barriers=a['combat']['geometry_barriers']-b['combat']['geometry_barriers'],overloads=a['combat']['overload_frames']-b['combat']['overload_frames'],
        intervals=intervals,props=[{k:x[k] for k in ['id','delivered_hits','break_events','reset_generation']} for x in a['props'] if x['delivered_hits'] or x['break_events']])) )
