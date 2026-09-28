"""Check preserved fragment topology and summarize actual gameplay evidence."""
import json
import argparse
import math
from collections import Counter
from pathlib import Path

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/DemoColumnExperiment06'
before = json.loads((ROOT / 'Saved/DemoColumnExperiment05/collection-before.json').read_text(encoding='utf-8-sig'))
after = json.loads((OUT / 'collection.json').read_text(encoding='utf-8-sig'))


def topology(data):
    # Flattening renames bones; identify unchanged fragment geometry instead.
    return Counter((g['faces'], g['bounds'], tuple(sorted((m, round(v['area_cm2'], 6))
                   for m, v in g['surface_by_material'].items()))) for g in data['geometry']
                   if data['hierarchy'][g['transform']]['children'] == 0)


assert topology(before) == topology(after), 'Original fragment face counts changed'
assert after['geometries'] == 730 and not after['leaves_without_convex']
assert after['anchored_count'] == 167
assert all(after['hierarchy'][b]['anchored'] for b in range(711, 731)), 'Original deep blocks must all stay anchored'
report = dict(original_fragment_topology_preserved=True, geometries=after['geometries'],
              faces=after['faces'], vertices=after['vertices'], probes={})
parser = argparse.ArgumentParser()
parser.add_argument('probes', nargs='+', help='Explicit accepted probe filenames; earlier failed evidence is preserved separately')
args = parser.parse_args()
for name in args.probes:
    path = OUT / name
    data = json.loads(path.read_text())
    rows = [data['before']] + data['samples'] + ([data['after']] if 'after' in data else [])
    c = [r['cladding'] for r in rows]
    result = dict(error=data.get('error'), before=c[0], after=c[-1],
                  max_slots=max(r['retention_slots'] for r in c),
                  max_carried=max(r['carried_tiles'] for r in c),
                  max_unsupported=max(r['unsupported_wall_tiles'] for r in c),
                  max_core_moved=max(r['protected_core_moved'] for r in c),
                  shots=rows[-1]['rifle']['shots']-rows[0]['rifle']['shots'],
                  max_retained_collision=max(r['retained_tile_collision']+r['retained_concrete_collision_shapes']+r['carried_collision_tiles'] for r in c),
                  max_retained_simulation=max(r['retained_tile_simulating']+r['retained_concrete_nonkinematic'] for r in c))
    result['max_retained_unsupported'] = max(r['retained_concrete_unsupported'] + r['retained_tile_unsupported'] for r in c)
    result['bulk_max_displacement_cm'] = max(math.dist(r['pieces'][b]['p'], rows[0]['pieces'][b]['p'])
                                             for r in rows for b in range(711, 731))
    report['probes'][path.stem] = result
    assert not result['error'], result
    assert result['max_slots'] <= 50, result
    assert result['max_unsupported'] == result['max_core_moved'] == 0, result
    assert result['max_retained_collision'] == result['max_retained_simulation'] == 0, result
    assert result['max_retained_unsupported'] == 0, result
    assert result['bulk_max_displacement_cm'] < .05, result
    for marker in data.get('marked', []):
        if marker['label'] in ('fresh-reset', 'final-fresh'):
            state = marker['cladding']
            assert state['attached'] == 1560 and state['retention_slots'] == state['carried_tiles'] == state['debris'] == 0
(OUT / 'analysis.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
