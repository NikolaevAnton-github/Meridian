"""Analyze actual input-driven jump trajectories and evaluated landing recovery."""
import json
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / 'Saved/PurchasedArms04/Worker'
JUMP = 'AM_TFA_FP_AR_Jump_Full'


def speed(row):
    return math.hypot(*row['velocity'][:2])


def pose(row):
    return next(p['evaluation'] for p in row['parts']
                if p.get('evaluation') and 'hand_l' in p.get('bones', {}))


def inspect(path):
    data = json.loads(path.read_text())
    rows = data['rows']
    assert not data['error'] and len(rows) > 200, path
    assert not any(r['paused'] for r in rows)
    spans, begin = [], None
    for index, row in enumerate(rows):
        if row['falling'] and begin is None:
            begin = index
        if not row['falling'] and begin is not None:
            spans.append((begin, index))
            begin = None
    assert begin is None and not rows[-1]['busy'], path
    jumps = []
    for a, b in spans:
        pre, land = rows[a - 1], rows[b]
        flight = rows[a:b]
        after = min(rows, key=lambda r: abs(r['t'] - land['t'] - .6))
        assert flight[0]['velocity'][2] > 300
        assert flight[-1]['velocity'][2] < 0
        assert all(r['montage'] == JUMP for r in flight)
        assert .85 <= land['reload_time'] < .9
        assert land['busy'] and not after['busy'] and after['montage'] != JUMP
        assert land['jump_z_velocity'] == after['jump_z_velocity'] == 320
        tail = [r for r in rows[b:] if r['t'] <= land['t'] + .35]
        assert any(pose(r)['action_time'] > 1.1 for r in tail)
        assert all(pose(r)['montage'] == JUMP for r in tail)
        evaluation_ids = {pose(r)['evaluations'] for r in flight + tail}
        assert len(evaluation_ids) > 60
        jumps.append({'request': pre['jump_starts'] + 1, 'first_airborne_t': flight[0]['t'],
            'last_grounded_t': pre['t'], 'landing_t': land['t'],
            'height_cm': max(r['location'][2] for r in flight) - pre['location'][2],
            'travel_cm': math.dist(pre['location'][:2], land['location'][:2]),
            'sampled_flight_seconds': land['t'] - pre['t'],
            'takeoff_setting_cm_s': flight[0]['jump_z_velocity'],
            'first_sample_vertical_cm_s': flight[0]['velocity'][2],
            'planar_speed_range_cm_s': [min(map(speed, flight)), max(map(speed, flight))],
            'last_airborne_montage_position': flight[-1]['reload_time'],
            'landing_montage_position': land['reload_time'],
            'evaluated_airborne_tail_frames': len(evaluation_ids),
            'recovered_t': after['t'], 'recovered_running': after['running'],
            'recovered_sprinting': after['sprinting'], 'recovered_speed_cm_s': speed(after)})
    assert rows[-1]['jump_starts'] == len(jumps), path
    unique_evals = len({pose(r)['evaluations'] for r in rows})
    return data, {'file': path.name, 'samples': len(rows), 'unique_evaluations': unique_evals,
                  'sample_rate_hz': len(rows) / rows[-1]['t'], 'jumps': jumps,
                  'recovered': not rows[-1]['busy'] and not rows[-1]['falling']}


def main():
    results, loaded = {}, {}
    for path in sorted(OUT.glob('Jump01-*.json')) + sorted(OUT.glob('Views01-*.json')):
        data, result = inspect(path)
        results[path.stem], loaded[path.stem] = result, data
    # The first nonvideo ordinary take loses native W input during flight despite
    # the driver's held-key bookkeeping. Its trajectory is valid, but use the
    # foreground video take for continuous movement and landing recovery.
    ordinary = results['Views01-Ordinary']['jumps'][0]
    held = results['Jump01-ShiftHeld']['jumps'][0]
    released, subsequent = results['Jump01-ShiftReleased']['jumps']
    stationary = results['Jump01-StationaryShift']['jumps'][0]
    alt = results['Jump01-Alt']['jumps'][0]
    assert 51 < ordinary['height_cm'] < 53
    assert abs(ordinary['recovered_speed_cm_s'] - 360) < .01
    assert 62 < held['height_cm'] < 64
    assert held['recovered_running'] and held['recovered_speed_cm_s'] == 540
    assert 1.18 < held['height_cm'] / ordinary['height_cm'] < 1.24
    assert 1.60 < held['travel_cm'] / ordinary['travel_cm'] < 1.70
    assert stationary['takeoff_setting_cm_s'] == 320 and stationary['travel_cm'] == 0
    assert alt['takeoff_setting_cm_s'] == 352 and alt['recovered_sprinting']
    assert abs(alt['height_cm'] - held['height_cm']) < .1
    release_rows = loaded['Jump01-ShiftReleased']['rows']
    airborne_release = [r for r in release_rows if 1.25 < r['t'] < released['landing_t']]
    assert airborne_release and all(not r['running'] and r['jump_starts'] == 1 for r in airborne_release)
    assert all(abs(speed(r) - 540) < .01 for r in airborne_release)
    assert subsequent['takeoff_setting_cm_s'] == 320
    assert abs(subsequent['height_cm'] - ordinary['height_cm']) < .1
    assert all(abs(s - 360) < .01 for s in subsequent['planar_speed_range_cm_s'])
    for name in ['Views01-Ordinary', 'Jump01-ShiftHeld', 'Jump01-ShiftReleased', 'Jump01-Alt',
                 'Views01-ShiftHeld', 'Views01-ShiftReleased']:
        rows = loaded[name]['rows']
        for jump in results[name]['jumps']:
            active = [r for r in rows if jump['last_grounded_t'] <= r['t'] <= jump['recovered_t']]
            assert all(b['move_binding_samples'] > a['move_binding_samples']
                       for a, b in zip(active, active[1:])), name
    for name, key, when in [('Busy', 'busy', .7), ('Crouch', 'crouched', 1)]:
        data = loaded['Jump01-' + name + 'Gate']
        row = min(data['rows'], key=lambda r: abs(r['t'] - when))
        assert row[key] and data['rows'][-1]['jump_starts'] == 0
        assert not results['Jump01-' + name + 'Gate']['jumps']
    result = {'passed': True, 'cases': results,
        'ordinary_acceptance_take': 'Views01-Ordinary',
        'height_ratio_shift_over_ordinary': held['height_cm'] / ordinary['height_cm'],
        'travel_ratio_shift_over_ordinary': held['travel_cm'] / ordinary['travel_cm'],
        'measurement': 'Height from last grounded capsule center to airborne apex. Travel from last grounded '
                       'sample to first grounded sample after collision landing; boundary uncertainty is one '
                       'telemetry interval. All cases share the flat center aisle start transform.',
        'limits': 'PIE on the retained lobby, fixed forward input, supplied animation and collision. '
                  'No unrelated action/animation matrix or multiplayer coverage.',
        'early_baseline': 'Baseline01 uses 3 Hz background-throttled samples. It confirms the prior native '
                          'Shift rejection and ordinary jump request only; it is not visual/recovery acceptance.',
        'input_delivery_limit': 'Jump01-Ordinary stops receiving native W input during flight despite logical '
                                'held-key bookkeeping. It supports trajectory only. Views01-Ordinary replaces '
                                'its continuous-movement recovery evidence; native input advances each sample.'}
    target = OUT / 'focused-analysis02.json'
    assert not target.exists()
    target.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'passed': True, 'cases': len(results),
          'samples': sum(r['samples'] for r in results.values()),
          'ordinary': ordinary, 'shift_held': held, 'shift_released': released,
          'subsequent_ordinary': subsequent, 'alt': alt}, indent=2))


if __name__ == '__main__':
    main()
