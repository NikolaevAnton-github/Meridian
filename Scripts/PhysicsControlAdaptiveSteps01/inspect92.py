"""Compact measured step transitions; source records remain untouched."""
import json
import math
import sys
from pathlib import Path
OUT = Path(__file__).resolve().parents[2] / 'Saved/CombatSlice01/PhysicsControlAdaptiveSteps01/Worker'
for name in sys.argv[1:]:
    data = json.loads((OUT / (name + '.json')).read_text())
    print(name, 'error', data['error'], 'rows', len(data['rows']))
    previous = None
    for row in data['rows']:
        d = row.get('dummy')
        if not d:
            continue
        s, b = d['step'], d['balance']
        key = b['state'], s['phase'], s['completed'], s.get('replans'), s['started']
        if key != previous:
            print(json.dumps(dict(t=round(row['t'], 3), state=key, reason=b['reason'], step=s['reason'],
                length=s.get('selected_length_cm'), lift=s.get('selected_lift_cm'), times=s.get('phase_durations_seconds'),
                demand=s.get('entry_demand_cm'), lean=round(b['lean_degrees'], 2), reach=d['recoverability']['required_reach_cm'],
                drift=s['peak_support_drift_cm'], replan=s.get('replan_travel_cm'), impulse=s['impulse'],
                body_direction=s['body_direction'], velocity=s.get('entry_velocity_cm_s'))))
            previous = key
    print('events', [{k:v for k,v in e.items() if k != 'step'} for e in data['events']])
