"""Read failed target envelopes and stance without repeating physical experiments."""
import json
import math
import sys
from pathlib import Path
OUT = Path(__file__).resolve().parents[2] / 'Saved/CombatSlice01/PhysicsControlAdaptiveSteps01/Worker'
for name in sys.argv[1:]:
    data = json.loads((OUT/(name+'.json')).read_text())
    neutral = None
    prior = None
    for r in data['rows']:
        if not r.get('dummy'):
            continue
        d = r['dummy']; s = d['step']; b = d['balance']
        l,rr = [r['leg_bones'][f'foot_{x}']['p'] for x in ['l','r']]
        span = [a-b for a,b in zip(l,rr)]
        if neutral is None:
            neutral = span
        key = b['state'],s['started'],s['completed']
        if key != prior:
            print(json.dumps(dict(case=name,t=r['t'],state=key,foot=s['swing_foot'],corrective=s['corrective'],
                stance_error=math.dist(span[:2],neutral[:2]), stance_width=math.hypot(*span[:2]),
                joint_error=s['joint_limit_error_degrees'],height=s['height_correction_cm'],reason=b['reason'],
                target_bad_joints=[{k:j.get(k) for k in ['child','parent','target_clamp_error_degrees','observed_degrees']}
                    for j in s['leg_joints'] if j.get('target_clamp_error_degrees',0) > 1],
                trials=s.get('geometry_trials'),delta=s['body_direction'])))
            prior = key
