"""Read concise transition evidence from the retained continuous runtime recorder."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'Saved/CombatSlice01/PhysicsControlBalance01/Worker'
for name in sys.argv[1:]:
    data=json.loads((ROOT/(name+'.json')).read_text())
    changes=[]
    previous=None
    for row in data['rows']:
        d=row['dummy']; b=d['balance']
        key=(b['state'],b['reason'],d['health'],d['epoch'])
        if key!=previous:
            changes.append(dict(t=round(row['t'],3),world=round(row['world_time'],3),health=d['health'],**b))
            previous=key
    print(json.dumps(dict(name=name,error=data['error'],counts=data['rows'][0]['counts'],
        ammo=[data['rows'][0]['rifle']['magazine'],data['rows'][-1]['rifle']['magazine']],
        max_lean=max(r['dummy']['balance']['lean_degrees'] for r in data['rows']),changes=changes),indent=2))
