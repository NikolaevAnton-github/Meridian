"""Check borrowing, later-side admissions, retained supports and reset evidence."""
import argparse
import json
from pathlib import Path

OUT = Path('D:/devgames/MeridianSquad/Saved/DemoColumnExperiment09')
parser = argparse.ArgumentParser()
parser.add_argument('probe')
parser.add_argument('--fourth', action='store_true')
args = parser.parse_args()
data = json.loads((OUT / args.probe).read_text())
assert not data.get('error'), data.get('error')
rows = [data['before']] + data['samples'] + [data['after']]
c = [row['cladding'] for row in rows]
keys = ('unsupported_wall_tiles', 'protected_core_moved', 'carried_physics_tiles',
        'retained_tile_simulating', 'retained_tile_deep_overlap_pairs', 'debris_inside_core',
        'grounded_facing_tiles', 'retained_concrete_nonkinematic', 'retained_concrete_unsupported',
        'retained_tile_unsupported', 'retained_concrete_invisible')
maxima = {key: max(row[key] for row in c) for key in keys}
assert not any(maxima.values()), maxima
assert all(row['retention_slots'] <= 80 and row['retained_tiles'] <= 48
           and row['active_ceramic_chips'] <= 32 for row in c)
assert all(sum(row['retained_by_sector']) == row['retention_slots'] for row in c)
assert all(sum(row['retained_ceramic_by_sector']) == row['retained_tiles'] for row in c)
assert all(row['retained_tile_collision'] == row['retained_tiles'] for row in c)
assert all(row['retained_concrete_physics_shapes'] >= row['retained_concrete'] for row in c)
marks = {r['label']: r['cladding'] for r in data['marked']}
borrowed = max(v for r in c for v in r['retained_by_sector'])
assert borrowed > 20, borrowed
shots = rows[-1]['rifle']['shots']-rows[0]['rifle']['shots']
if any(e[1] == 'ammo' for e in data['events']):
    assert shots == sum(e[1] == 'fire' and e[2] for e in data['events'])
    assert rows[-1]['rifle']['dry_fire'] == rows[0]['rifle']['dry_fire']
settled = marks['fourth-face-settled' if args.fourth else 'settled-cap']
if args.fourth:
    assert shots == 30
    assert settled['retained_by_sector'][3] > 20
else:
    assert shots >= 120
    assert max(r['retention_slots'] for r in c) == 80
    assert settled['retention_replacements'] > 0
    assert settled['retention_support_vetoes'] > 0, 'Support protection was not exercised'
    assert all(v >= 16 for v in settled['retained_by_sector']), settled['retained_by_sector']
reset = marks['final-fresh']
assert reset['attached'] == 1560
assert reset['retention_slots'] == reset['carried_tiles'] == reset['debris'] == reset['active_ceramic_chips'] == 0
assert reset['retention_replacements'] == reset['retention_support_vetoes'] == 0
assert reset['retained_by_sector'] == reset['evictions_by_sector'] == [0, 0, 0, 0]
result = dict(shots=shots, dry_fire=rows[-1]['rifle']['dry_fire']-rows[0]['rifle']['dry_fire'],
              max_retained=max(r['retention_slots'] for r in c), max_borrowed_sector=borrowed,
              final_sectors=settled['retained_by_sector'], final_ceramic_sectors=settled['retained_ceramic_by_sector'],
              replacements=settled['retention_replacements'], support_vetoes=settled['retention_support_vetoes'],
              evictions=settled['evictions_by_sector'], invariants=maxima, reset_passed=True,
              stages={name: {k: v[k] for k in ('retention_slots','retained_by_sector','retained_ceramic_by_sector','retention_replacements')}
                      for name, v in marks.items()})
(OUT / (Path(args.probe).stem + '-analysis.json')).write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result))
