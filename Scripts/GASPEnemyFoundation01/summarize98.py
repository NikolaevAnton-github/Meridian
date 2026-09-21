"""Summarize recorded pilot behavior without converting observations into acceptance."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/GASPEnemyFoundation01/Worker'
for name in sys.argv[1:]:
    data = json.loads((OUT / (name + '.json')).read_text(encoding='utf-8'))
    rows = [r for r in data['rows'] if r.get('dummy')]
    transitions = []
    for row in rows:
        d = row['dummy']
        key = (d['gasp']['authority'], d['balance']['state'], d['step']['phase'])
        if not transitions or key != transitions[-1]['key']:
            transitions.append(dict(t=round(row['t'],3), key=key, reason=d['balance']['reason']))
    last = rows[-1]['dummy']
    conflict = [r['t'] for r in rows if r['dummy']['gasp']['enabled_source_controls'] and r['dummy']['balance']['enabled_drives']]
    result = dict(name=name, samples=len(rows), error=data['error'], duration=rows[-1]['t'], transitions=transitions,
        final_authority=last['gasp']['authority'], falls=last['balance']['falls'], getups=last['balance']['get_ups'],
        steps=last['step']['completed'], conflicts=len(conflict), hits=last['physical_hits'],
        positions={label: next(r for r in rows if r['t']>=t)['dummy']['gasp']['capsule_location']
                   for label,t in [('start',0),('end',rows[-1]['t'])]},
        selected_getup=last['gasp']['selected_getup'])
    print(json.dumps(result))
