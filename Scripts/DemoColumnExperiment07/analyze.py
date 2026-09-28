"""Verify protected geometry and the refined column's real-rifle evidence."""
import argparse
import json
import math
from collections import Counter
from pathlib import Path

OUT = Path('D:/devgames/MeridianSquad/Saved/DemoColumnExperiment07')
before = json.loads((OUT / 'collection-before.json').read_text(encoding='utf-8-sig'))
after = json.loads((OUT / 'collection.json').read_text(encoding='utf-8-sig'))
sizing = json.loads((OUT / 'sizing.json').read_text(encoding='utf-8-sig'))


def core(data):
    return Counter((g['faces'], g['bounds'], tuple(sorted((m, round(v['area_cm2'], 5))
                   for m, v in g['surface_by_material'].items()))) for g in data['geometry']
                   if data['hierarchy'][g['transform']]['anchored'])


assert core(before) == core(after), 'Protected core geometry changed'
cut = {s['source_bone'] for s in sizing['sources']}
def signature(g):
    return (g['faces'], g['bounds'], tuple(sorted((m, round(v['area_cm2'], 5))
            for m, v in g['surface_by_material'].items())))
unchanged = Counter(signature(g) for g in before['geometry'] if g['transform'] not in cut)
assert not (unchanged - Counter(signature(g) for g in after['geometry'])), 'An unselected piece changed'
assert after['anchored_count'] == 167 and not after['leaves_without_convex']
assert after['geometries'] == 730 + sizing['cut_sources']
assert .68 < sizing['median_linear_ratio'] < .74
assert all(len(s['children']) == 2 for s in sizing['sources'])
core_bones = [b for b, row in enumerate(after['hierarchy']) if row['anchored']]
report = dict(core_geometry_preserved=True, unchanged_pieces=sum(unchanged.values()),
              geometries=after['geometries'], sizing=sizing['median_linear_ratio'], probes={})
parser = argparse.ArgumentParser()
parser.add_argument('probes', nargs='+')
args = parser.parse_args()
for name in args.probes:
    data = json.loads((OUT / name).read_text())
    assert not data.get('error'), data.get('error')
    rows = [data['before']] + data['samples'] + [data['after']]
    c = [r['cladding'] for r in rows]
    keys = ('unsupported_wall_tiles', 'protected_core_moved', 'retained_tile_collision',
            'retained_concrete_physics_shapes', 'carried_physics_tiles', 'retained_tile_simulating',
            'retained_concrete_nonkinematic', 'retained_concrete_unsupported', 'retained_tile_unsupported')
    maxima = {k: max(r[k] for r in c) for k in keys}
    assert not any(maxima.values()), maxima
    assert max(r['retention_slots'] for r in c) <= 50
    assert max(r['active_ceramic_chips'] for r in c) <= 32
    displacement = max(math.dist(r['pieces'][b]['p'], rows[0]['pieces'][b]['p']) for r in rows for b in core_bones)
    assert displacement < .05, displacement
    report['probes'][name] = dict(shots=rows[-1]['rifle']['shots']-rows[0]['rifle']['shots'],
        max_retained=max(r['retention_slots'] for r in c), max_chips=max(r['active_ceramic_chips'] for r in c),
        ground_crumble=max(r['ground_crumble_events'] for r in c), shot_crumble=max(r['shot_crumble_events'] for r in c),
        max_core_displacement=displacement, invariants=maxima, after=c[-1])
    for marker in data.get('marked', []):
        if marker['label'] in ('fresh-reset', 'final-fresh'):
            s = marker['cladding']
            assert s['attached'] == 1560
            assert s['retention_slots'] == s['carried_tiles'] == s['debris'] == s['active_ceramic_chips'] == 0
(OUT / 'analysis.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({k: {a: b for a, b in v.items() if a != 'after'} for k, v in report['probes'].items()}))
