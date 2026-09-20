"""Summarize measured events without dumping body/contact sample arrays."""
import json
import sys
from pathlib import Path
OUT=Path(__file__).resolve().parents[2]/'Saved/CombatSlice01/PhysicsControlRecoverability01/Worker'
for name in sys.argv[1:]:
    r=json.loads((OUT/(name+'.json')).read_text())
    print(name,'samples',len(r['rows']),'error',r['error'])
    prior=None
    for row in r['rows']:
        d=row.get('dummy')
        if not d:continue
        b,s=d['balance'],d['step']; rec=d.get('recoverability',{})
        key=(b['state'],s['phase'],s['completed'])
        if key!=prior:
            print(json.dumps(dict(t=round(row['t'],3),state=b['state'],reason=b['reason'],step=s['reason'],phase=s['phase'],
                completed=s['completed'],hits=d['physical_hits'],feet=b['usable_feet'],drives=b['enabled_drives'],
                lean=round(b['lean_degrees'],2),reach=round(rec.get('required_reach_cm',0),2),
                contact=rec.get('feet'),leg_contacts=len(rec.get('leg_contacts',[])))))
            prior=key
    last=r['rows'][-1]
    print('shots',last['rifle']['shots'],'auto',last['rifle']['automatic'],'fixtures',len(last['fixtures']))
