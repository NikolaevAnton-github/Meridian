"""Validate focused wake/reset and accepted real-rifle behavior from saved PIE evidence."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / 'Saved/LobbyColumnsPerf01'
t = json.loads((OUT / 'transitions01.json').read_text())
assert not t.get('error'), t.get('error')
before = t['before']['cladding']
assert before['idle'] and before['attached'] == 768
previous = before
for name in ('moved', 'restored'):
    current = t['samples'][name]['cladding']
    assert current['idle'] and current['full_updates'] >= previous['full_updates'] + 2
    assert current['attached'] == 768 and current['tile_hits'] == 0
    previous = current
fractured = t['samples']['external_fracture']['cladding']
assert fractured['root_broken'] and not fractured['idle']
assert fractured['full_updates'] > previous['full_updates']
assert fractured['tile_hits'] == fractured['concrete_impacts'] == 0
assert len(t['columns_after_reset']) == 16
for row in t['columns_after_reset']:
    assert row['prop']['ready'] and row['cladding']['idle']
    assert row['cladding']['attached'] == 768 and not row['cladding']['root_broken']

r = json.loads((OUT / 'rifle01.json').read_text())
assert not r.get('error'), r.get('error')
assert r['before']['cladding']['idle']
assert r['after']['rifle']['shots'] - r['before']['rifle']['shots'] == 10
assert r['after']['rifle']['dry_fire'] == r['before']['rifle']['dry_fire']
marked = {row['label']: row for row in r['marked']}
for height in (22, 810):
    a, b = marked[f'before-{height}'], marked[f'after-{height}']
    assert b['cladding']['concrete_impacts'] > a['cladding']['concrete_impacts']
    assert b['cladding']['released_concrete'] > a['cladding']['released_concrete']
    assert b['cladding']['attached'] < a['cladding']['attached']
    assert not b['cladding']['idle']
for row in r['samples']:
    for key in ('protected_core_moved', 'unsupported_wall_tiles', 'debris_inside_core',
                'retained_tile_simulating', 'retained_concrete_nonkinematic'):
        assert row['cladding'][key] == 0, (key, row['elapsed'])
    assert row['cladding']['retention_slots'] <= 80
reset = marked['reset']
assert reset['cladding']['idle'] and reset['cladding']['attached'] == 768
assert reset['prop']['reset_generation'] == r['before']['prop']['reset_generation'] + 1

summary = dict(stationary_sleep=True, external_movement_wake=True,
               external_fracture_wake=True, reset_columns=16,
               rifle_shots=10, base_and_top_damage=True, damaged_updates_active=True,
               core_stable=True, reset_returns_to_idle=True)
(OUT / 'analysis.json').write_text(json.dumps(summary, indent=2))
print(json.dumps(summary))
