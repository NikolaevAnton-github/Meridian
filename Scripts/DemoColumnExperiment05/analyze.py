"""Summarize stored authoring and real-projectile evidence without mutating assets."""
import json
import statistics
from pathlib import Path

OUT = Path('D:/devgames/MeridianSquad/Saved/DemoColumnExperiment05')
report = {}
for name in ('before', 'after'):
    data = json.loads((OUT / f'collection-{name}.json').read_text(encoding='utf-8-sig'))
    areas = [g['surface_by_material']['0']['area_cm2'] for g in data['geometry']
             if '0' in g['surface_by_material'] and data['hierarchy'][g['transform']]['children'] == 0]
    report[name] = {k: data[k] for k in ('transforms', 'geometries', 'vertices', 'faces', 'convex_hulls', 'leaves_without_convex')}
    report[name].update(exterior_leaves=len(areas), exterior_area_cm2=sum(areas),
                        median_exterior_cm2=statistics.median(areas), exterior_over_900=sum(a > 900 for a in areas))

for path in OUT.glob('play-*.json'):
    data = json.loads(path.read_text())
    rows = [data['before']] + data['samples'] + ([data['after']] if 'after' in data else [])
    counts = [r['cladding'] for r in rows]
    report[path.stem] = dict(error=data.get('error'),
                            before=counts[0], after=counts[-1],
                            max_slots=max(c['retention_slots'] for c in counts),
                            max_retained_concrete=max(c['retained_concrete'] for c in counts),
                            shots=data.get('after', rows[-1])['rifle'],
                            marked=[dict(label=r['label'], cladding=r['cladding'],
                                         prop=r['prop']) for r in data.get('marked', [])])

(OUT / 'analysis.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({k: v if k in ('before', 'after') else
                  {x: v[x] for x in ('error', 'max_slots', 'max_retained_concrete', 'after')}
                  for k, v in report.items()}, indent=2))
