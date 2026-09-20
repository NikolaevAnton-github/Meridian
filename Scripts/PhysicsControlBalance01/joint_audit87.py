"""Evaluate recorded body transforms against the actual constraint definitions."""
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/CombatSlice01/PhysicsControlBalance01/Worker'
definitions=json.loads((OUT/'Candidate05-JointAnchors-joints-standing.json').read_text())['joints']
locked=[j for j in definitions if all(j['linear_'+axis]==2 for axis in 'xyz')]
free=[j for j in definitions if all(j['linear_'+axis]==0 for axis in 'xyz')]
assert len(locked)==21 and len(free)==2 and len(definitions)==23

def anchor(body,local):
    x,y,z,w=body['rotation']
    a,b,c=local
    tx,ty,tz=2*(y*c-z*b),2*(z*a-x*c),2*(x*b-y*a)
    rotated=[a+w*tx+y*tz-z*ty,b+w*ty+z*tx-x*tz,c+w*tz+x*ty-y*tx]
    return [p+q for p,q in zip(body['position'],rotated)]

def gap(bodies,j):
    return math.dist(anchor(bodies[j['child']],j['local_anchor1']),anchor(bodies[j['parent']],j['local_anchor2']))

cases=[]
for name in ['Candidate03-Core','Candidate03-LegInterruptedDeath','Candidate03-FrontSlow',
             'Candidate04-BlockedAndAnchors','Candidate03-Unsupported','Candidate05-JointAnchors']:
    data=json.loads((OUT/(name+'.json')).read_text())
    maximum=0; peak=None; maximum_free=0; native_delta=0
    for r in data['rows']:
        bodies=r['dummy']['bodies']
        for j in locked:
            distance=gap(bodies,j)
            if distance>maximum:
                maximum=distance;peak=dict(t=r['t'],state=r['dummy']['balance']['state'],child=j['child'],parent=j['parent'])
        maximum_free=max(maximum_free,max(gap(bodies,j) for j in free))
        if 'max_locked_joint_anchor_gap_cm' in r['dummy']:
            native_delta=max(native_delta,abs(max(gap(bodies,j) for j in locked)-r['dummy']['max_locked_joint_anchor_gap_cm']))
    cases.append(dict(name=name,samples=len(data['rows']),max_locked_gap_cm=maximum,peak=peak,
                      max_free_anchor_separation_cm=maximum_free,max_native_agreement_error_cm=native_delta))

result=dict(task='MSQ-87',locked_joint_count=len(locked),free_joint_count=len(free),
    free_joint_pairs=[dict(child=j['child'],parent=j['parent']) for j in free],
    basis='Actual runtime FConstraintInstance linear motion: 0=LCM_Free, 2=LCM_Locked; engine ChaosEngineInterface.h. Reconstruct world anchors from recorded physical body position/quaternion and unchanged local anchor translations.',
    correction='self-checks01 incorrectly applied a positional coincidence requirement to all joints, including two free calf/pelvis constraints. Both raw metrics and the failed check remain preserved. No physics or asset settings were changed.',
    cases=cases,passed=all(c['max_locked_gap_cm']<3 and c['max_native_agreement_error_cm']<.01 for c in cases))
path=OUT/'joint-acceptance01.json';assert not path.exists()
path.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
