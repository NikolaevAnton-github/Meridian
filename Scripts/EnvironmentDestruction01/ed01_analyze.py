"""Acceptance assertions over real rifle and reset evidence; native CSV summary."""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/EnvironmentDestruction01/ED-01/MSQ-141-Candidate01'

def verify(label):
    data = json.loads((OUT / (label + '-complete.json')).read_text())
    assert data['error'] is None
    states = {s['label']: s for s in data['snapshots']}
    slow = label.startswith('slow')
    checks = {}
    def check(name, result):
        checks[name] = bool(result)
    check('real_rifle_hits', len(data['hits']) == (3 if slow else 5) and all('BP_TFA_BaseCharacter' in h['shooter'] for h in data['hits']))
    check('two_separated_local_regions', states['A-removed']['shell']['broken'] == 1 and states['two-regions']['shell']['broken'] == 2)
    check('first_hit_releases_piece9', data['hits'][0]['shell']['last_piece'] == 9)
    check('second_region_releases_piece22', data['hits'][2]['shell']['last_piece'] == 22)
    check('subsequent_actual_rifle_hits_visible_core', data['hits'][1]['victim'] == 'StaticMeshActor_35' and abs(data['hits'][1]['position'][1] + 124) < .01)
    check('local_surface_removed', all(abs(states['two-regions']['traces'][k]['impact'][1] + 124) < .01 for k in ('A', 'B')))
    check('untouched_geometry_stays_blocking', all(s['traces']['untouched']['actor'] == 'DestructibleCladding_0' and abs(s['traces']['untouched']['impact'][1] + 120) < .01 for s in data['snapshots']))
    check('fixed32_components', all(s['shell']['components'] == 32 and len(s['actual_mesh_components']) == 32 and s['actual_mesh_components'] == states['intact']['actual_mesh_components'] and len(s['actual_simulating_components']) == s['shell']['simulating'] for s in data['snapshots']))
    check('two_physical_bodies_max_in_sequence', max(s['shell']['simulating'] for s in data['snapshots']) == 2)
    check('reset_restores_geometry_and_body_counts', all(states['reset' + str(i)]['shell']['generation'] == i and states['reset' + str(i)]['shell']['broken'] == 0 and states['reset' + str(i)]['shell']['simulating'] == 0 and all(p['rest_position_error_cm'] < .001 for p in states['reset' + str(i)]['shell']['pieces']) for i in ((1,) if slow else (1, 2, 3))))
    if not slow:
        check('rebreak_after_each_reset', states['repeat1']['shell']['broken'] == 1 and states['repeat2']['shell']['broken'] == 1)
    check('detached_geometry_moves', all(p['rest_position_error_cm'] > 20 for p in states['settled']['shell']['pieces'] if p['broken']))
    check('debris_settles', states['settled']['shell']['awake'] == 0)
    expected_world, expected_hero = (.25, 2.6) if slow else (1, 1)
    check('canonical_time_scales', all(abs(s['scales']['world'] - expected_world) < .001 and abs(s['scales']['projectile'] - expected_world) < .001 and abs(s['scales']['hero_custom'] - expected_hero) < .001 and abs(s['projectile']['player_action_rate'] - expected_world) < .001 for s in data['snapshots']))
    check('moving_debris_does_not_cancel_firing', states['settled']['projectile']['geometry_barriers'] == states['intact']['projectile']['geometry_barriers'])
    return {'checks': checks, 'passed': all(checks.values()), 'hits': [{k: h[k] for k in ('shot_id', 'victim', 'position', 'damage')} for h in data['hits']],
            'break_ms': [h['shell']['last_break_ms'] for h in data['hits'] if h['victim'] == 'DestructibleCladding_0'],
            'final_generation': states['reset1' if slow else 'reset3']['shell']['generation']}

def stats(values):
    values = sorted(values)
    return {'samples': len(values), 'mean_ms': sum(values) / len(values), 'p95_ms': values[math.ceil(len(values) * .95) - 1], 'max_ms': values[-1]}

def profile(label):
    with (OUT / (label + '.csv')).open(newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    names = ['FrameTime', 'GameThreadTime', 'RenderThreadTime', 'GPUTime', 'Exclusive/GameThread/Physics', 'Exclusive/AllWorkers/Physics']
    numeric = [r for r in rows if r.get('FrameTime') and r['FrameTime'].replace('.', '', 1).isdigit()]
    result = {name: stats([float(r[name]) for r in numeric if r.get(name)]) for name in names if name in rows[0]}
    return {'frames': len(numeric), 'duration_sum_frame_seconds': sum(float(r['FrameTime']) for r in numeric) / 1000,
            'fields': result, 'metadata_tail': rows[-1] if not numeric or rows[-1] != numeric[-1] else None}

def main():
    checks = {name: verify(name) for name in ('normal05', 'slow04')}
    profiles = {name: profile(name) for name in ('normal05', 'slow04', 'cost01')}
    result = {'runtime': checks, 'profiles': profiles}
    path = OUT / 'verification-summary.json'
    with path.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print(json.dumps({'passed': all(c['passed'] for c in checks.values()),
        'failed': {k: [n for n, ok in v['checks'].items() if not ok] for k, v in checks.items()},
        'cost': profiles['cost01']['fields']}))
    assert all(c['passed'] for c in checks.values())

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        result = profile(sys.argv[1])
        print(json.dumps({k: result[k] for k in ('frames', 'duration_sum_frame_seconds', 'fields')}))
    else:
        main()
