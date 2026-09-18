"""Compare evaluated poses at matched idle phases, not unrelated screenshot frames."""
import json
import math
import bisect
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / 'Saved/PurchasedArms03/Worker'


def part(row, name):
    return next(p for p in row['parts'] if p['component'] == name)


def phase(row):
    return next(p['phase'] for p in part(row, 'CharacterMesh0')['evaluation']['players']
                if p['node'] == 'AnimGraphNode_BlendSpacePlayer_3')


def poses(row):
    return {**{k: v for k, v in part(row, 'CharacterMesh0')['bones'].items()
               if k in ['ik_hand_gun', 'hand_l', 'hand_r']},
            **{k: part(row, k)['camera'] for k in ['SM_Sight_Front', 'SM_Sight_Rear']}}


def angle(a, b):
    dot = abs(sum(x*y for x, y in zip(a, b)))
    lengths = math.sqrt(sum(x*x for x in a) * sum(x*x for x in b))
    return math.degrees(2*math.acos(min(1, dot / lengths)))


def read(name):
    data = json.loads((OUT / (name + '.json')).read_text())
    assert not data['error'], data['error']
    unique, seen = [], set()
    for row in data['rows']:
        evaluation = part(row, 'CharacterMesh0')['evaluation']['evaluations']
        if evaluation in seen:
            continue
        seen.add(evaluation)
        unique.append(row)
    return unique


def window(rows, start, end):
    return [r for r in rows if start <= r['t'] <= end]


def compare(reference, candidates, minimum_matches=15, interpolate=False):
    metrics = {k: {'position_cm': 0., 'rotation_deg': 0.} for k in poses(reference[0])}
    matches, worst_phase = 0, 0.
    coverage = {}
    state_maxima = {'fov_difference_deg': 0., 'ads_target_position_difference_cm': 0.,
                    'ads_target_rotation_difference_deg': 0., 'ads_current_position_difference_cm': 0.,
                    'ads_current_rotation_difference_deg': 0., 'settled_ads_position_cm': 0.,
                    'settled_ads_rotation_deg': 0.}
    state_fields = ['aim_requested', 'canted', 'crouched', 'source_stance', 'grip',
                    'camera_animation', 'source_head_lock']
    matched_records = []
    ordered = sorted(reference, key=phase)
    phase_points = [phase(r) for r in ordered]
    maximum_bracket = 0.
    for row in candidates:
        if interpolate:
            at = phase(row)
            index = bisect.bisect_right(phase_points, at)
            left, right = ordered[(index-1) % len(ordered)], ordered[index % len(ordered)]
            lower = phase(left) - (1. if index == 0 else 0.)
            upper = phase(right) + (1. if index == len(ordered) else 0.)
            alpha = (at-lower) / (upper-lower) if upper > lower else 0.
            maximum_bracket = max(maximum_bracket, upper-lower)
            expected = {}
            for name, a in poses(left).items():
                b = poses(right)[name]
                sign = 1 if sum(x*y for x, y in zip(a['q'], b['q'])) >= 0 else -1
                q = [(1-alpha)*x + alpha*sign*y for x, y in zip(a['q'], b['q'])]
                norm = math.sqrt(sum(x*x for x in q))
                expected[name] = {'p': [(1-alpha)*x + alpha*y for x, y in zip(a['p'], b['p'])],
                                  'q': [x/norm for x in q]}
            r = left if alpha < .5 else right
            difference = 0.
        else:
            r = min(reference, key=lambda r: abs(phase(r) - phase(row)))
            difference = abs(phase(r) - phase(row))
            expected = poses(r)
        if difference > .001:
            continue
        matches += 1
        worst_phase = max(worst_phase, difference)
        for field in state_fields:
            assert row[field] == r[field], (field, row[field], r[field])
        state_maxima['fov_difference_deg'] = max(state_maxima['fov_difference_deg'], abs(row['view_fov'] - r['view_fov']))
        assert abs(row['view_fov'] - 78.) <= .001 and abs(r['view_fov'] - 78.) <= .001
        for kind, key in [('target', 'TargetAimDownSightsOffset'), ('current', 'CurrentAimDownSightsOffset')]:
            a, b = row['offsets'][key], r['offsets'][key]
            state_maxima[f'ads_{kind}_position_difference_cm'] = max(
                state_maxima[f'ads_{kind}_position_difference_cm'], math.dist(a['p'], b['p']))
            state_maxima[f'ads_{kind}_rotation_difference_deg'] = max(
                state_maxima[f'ads_{kind}_rotation_difference_deg'], angle(a['q'], b['q']))
        for checked in [row, r]:
            a, b = [checked['offsets'][k] for k in ['CurrentAimDownSightsOffset', 'TargetAimDownSightsOffset']]
            state_maxima['settled_ads_position_cm'] = max(state_maxima['settled_ads_position_cm'], math.dist(a['p'], b['p']))
            state_maxima['settled_ads_rotation_deg'] = max(state_maxima['settled_ads_rotation_deg'], angle(a['q'], b['q']))
        segment = str(row['heading_target'][1])
        bucket = coverage.setdefault(segment, {'matches': 0, 'turning_matches': 0, 'yaw_min': 360., 'yaw_max': 0.,
                                               'turning_yaw_min': 360., 'turning_yaw_max': 0., 'bins_15_deg': {}})
        yaw = row['control'][1] % 360
        bucket['matches'] += 1
        bucket['yaw_min'] = min(bucket['yaw_min'], yaw)
        bucket['yaw_max'] = max(bucket['yaw_max'], yaw)
        if abs(row['heading_error'][0]) > .1:
            bucket['turning_matches'] += 1
            bucket['turning_yaw_min'] = min(bucket['turning_yaw_min'], yaw)
            bucket['turning_yaw_max'] = max(bucket['turning_yaw_max'], yaw)
            bin_label = str(int(yaw // 15) * 15)
            bucket['bins_15_deg'][bin_label] = bucket['bins_15_deg'].get(bin_label, 0) + 1
        matched_records.append({'t': row['t'], 'reference_t': r['t'], 'yaw': yaw, 'pitch': row['control'][0],
                                'phase_difference': difference,
                                'evaluation': part(row, 'CharacterMesh0')['evaluation']['evaluations']})
        # Cached, unselected branches retain stale clocks/weights. Match the
        # continuously advancing aimed blendspace, selected by bIsAiming, only.
        for checked in [row, r]:
            player = next(p for p in part(checked, 'CharacterMesh0')['evaluation']['players']
                          if p['node'] == 'AnimGraphNode_BlendSpacePlayer_3')
            assert abs(player['weight'] - 1.) <= .001
            assert checked['aim_requested'] and not checked['montage']
            assert checked['grip'] == 0 and not checked['crouched']
            assert not checked['camera_animation'] and max(map(abs, checked['simulated_velocity'])) == 0.
        for name, pose in poses(row).items():
            other = expected[name]
            metric = metrics[name]
            metric['position_cm'] = max(metric['position_cm'], math.dist(pose['p'], other['p']))
            metric['rotation_deg'] = max(metric['rotation_deg'], angle(pose['q'], other['q']))
    assert matches >= minimum_matches, (matches, minimum_matches)
    assert all(value <= .001 for value in state_maxima.values()), state_maxima
    return {'matches': matches, 'candidates': len(candidates), 'max_phase_difference': worst_phase,
            'minimum_matches': minimum_matches, 'coverage': coverage,
            'interpolated_reference': interpolate, 'maximum_reference_bracket_cycles': maximum_bracket,
            'equal_state_fields': state_fields, 'state_tolerance_cm_or_deg': .001,
            'state_maxima': state_maxima, 'matched_samples': matched_records, 'metrics': metrics}


def main():
    before, after, variants = [read(n) for n in ['Before01', 'After01', 'Variants01']]
    result = {'gates': {'position_cm': .05, 'rotation_deg': .05, 'phase_difference': .001},
              'before': {}, 'after': {}, 'variants': {}}
    segments = [('90', 7, 9.5), ('180', 12, 14.5), ('-90', 17, 19.5), ('return0', 22, 22.9)]
    for name, rows in [('before', before), ('after', after)]:
        reference = window(rows, 2, 4.9)
        for label, start, end in segments:
            result[name][label] = compare(reference, window(rows, start, end), 30 if name == 'after' else 1)
        result[name]['held_turn'] = compare(reference, window(rows, 5, 22.9), 500 if name == 'after' else 100)
    result['preserved_initial_pose'] = compare(window(before, 2, 4.9), window(after, 2, 4.9))
    result['held_turn_all_phases'] = compare(window(after, 2, 4.9), window(after, 5, 22.9), 1800, interpolate=True)
    assert all(b['turning_matches'] >= 40 for b in result['held_turn_all_phases']['coverage'].values())
    result['variants']['reentry180'] = compare(window(after, 2, 4.9), window(variants, 5.8, 7.4))
    canted_ref = window(variants, 12.5, 14.9)
    result['variants']['canted180'] = compare(canted_ref, window(variants, 9, 10.9))
    result['variants']['canted_pitch0'] = compare(canted_ref, window(variants, 17, 18.9))
    result['variants']['canted_pitch180'] = compare(canted_ref, window(variants, 21, 23.8))
    result['variants']['normal_pitch180'] = compare(window(after, 2, 4.9), window(variants, 26, 27.9))
    result['variants']['normal_pitch0'] = compare(window(after, 2, 4.9), window(variants, 30, 31.9))
    result['variants']['return_normal180'] = compare(window(after, 2, 4.9), window(variants, 34, 35.8))
    result['variants']['recoil_recovered180'] = compare(window(after, 2, 4.9), window(variants, 38, 39.9))
    result['checks'] = {}
    for name, rows in [('before', before), ('after', after), ('variants', variants)]:
        result['checks'][name] = {
            'evaluations': len(rows), 'max_speed_cm_s': max(math.sqrt(sum(v*v for v in r['velocity'])) for r in rows),
            'shadow_violations': sum(any(p['shadow_flags']) for r in rows for p in r['parts']),
            'paused_samples': sum(r['paused'] for r in rows),
            'mouse_samples': rows[-1]['look_binding_samples'],
            'ammo_before_after': [rows[0]['ammo'], rows[-1]['ammo']],
            'shots': [{'label': r['screenshot_requested'], 't': r['t'], 'control': r['control'],
                       'canted': r['canted'], 'aim': r['aim_requested'], 'fov': r['view_fov']}
                      for r in rows if 'screenshot_requested' in r],
        }
    groups = [*result['after'].values(), result['held_turn_all_phases'], result['preserved_initial_pose'], *result['variants'].values()]
    result['pass'] = all(m['position_cm'] <= .05 and m['rotation_deg'] <= .05
                         for group in groups for m in group['metrics'].values())
    (OUT / 'analysis03.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'pass': result['pass'], 'held_turn_coverage': result['held_turn_all_phases']['coverage'],
                     'all_phases_metrics': result['held_turn_all_phases']['metrics'],
                     'maximum_interpolation_bracket': result['held_turn_all_phases']['maximum_reference_bracket_cycles'],
                     'matched_state_maxima': result['after']['held_turn']['state_maxima'],
                     'counts': {name: {k: v['matches'] for k, v in result[name].items()} for name in ['before', 'after', 'variants']}}, indent=2))


if __name__ == '__main__':
    main()
