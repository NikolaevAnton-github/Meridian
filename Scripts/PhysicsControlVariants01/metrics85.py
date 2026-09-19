"""Objective response metrics, with raw ordinary-speed captures retained separately."""
import json
import math
import sys
from pathlib import Path
OUT=Path(__file__).resolve().parents[2]/'Saved/CombatSlice01/PhysicsControlVariants01/Worker'

def sub(a,b): return [x-y for x,y in zip(a,b)]
def norm(v): return math.sqrt(sum(x*x for x in v))
def mul(a,b):
    x,y,z,w=a; X,Y,Z,W=b
    return [w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z]
def inv(q): return [-q[0],-q[1],-q[2],q[3]]
def local(bodies,bone):
    p=bodies['pelvis']; b=bodies[bone]
    v=mul(mul(inv(p['rotation']),[*sub(b['position'],p['position']),0]),p['rotation'])[:3]
    return v,mul(inv(p['rotation']),b['rotation'])
def angle(a,b): return math.degrees(2*math.acos(min(1,abs(sum(x*y for x,y in zip(a,b)))/(norm(a)*norm(b)))))

def reactions(name,measure_bone=None):
    data=json.loads((OUT/(name+'.json')).read_text())
    rows=data['rows']; result=[]
    seen=set()
    for row in rows:
        d=row['dummy']
        if not d: continue
        for c in d.get('contacts',[]):
            if c['shot'] in seen: continue
            seen.add(c['shot'])
            if c['was_dead'] or c['health']==0: continue
            bone=measure_bone or c['bone']; origin,q0=local(c['before'],bone)
            post=[s for s in rows if row['world_time'] <= s['world_time'] <= row['world_time']+1.5 and s['dummy'] and s['dummy']['epoch']==d['epoch']]
            late=[s for s in rows if row['world_time']+3.5 <= s['world_time'] <= row['world_time']+4 and s['dummy'] and s['dummy']['epoch']==d['epoch']]
            result.append(dict(shot=c['shot'],profile=d.get('profile',0),bone=bone,contact_bone=c['bone'],t=row['t'],world_time=row['world_time'],
                impulse=norm(c['impulse']),impulse_count=c['impulse_count'],health=c['health'],
                peak_local_cm=max(norm(sub(local(s['dummy']['bodies'],bone)[0],origin)) for s in post),
                peak_local_degrees=max(angle(local(s['dummy']['bodies'],bone)[1],q0) for s in post),
                late_local_cm=max((norm(sub(local(s['dummy']['bodies'],bone)[0],origin)) for s in late),default=None),
                late_max_speed=max((norm(b['linear_velocity']) for s in late for b in s['dummy']['bodies'].values()),default=None),
                late_recovering=max((s['dummy']['recovering_controls'] for s in late),default=None)))
    return dict(case=name,error=data['error'],samples=len(rows),contacts=result,
        initial_counts=rows[0].get('counts'),final_counts=rows[-1].get('counts'),
        final_health=[x['health'] for x in rows[-1].get('fixtures',[])],
        overload_change=rows[-1]['combat']['overload_frames']-rows[0]['combat']['overload_frames'])

if __name__=='__main__':
    print(json.dumps([reactions(n) for n in sys.argv[1:]],indent=2))
