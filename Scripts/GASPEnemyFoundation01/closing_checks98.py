"""Read recorded evidence and preserve the final focused acceptance measurements."""
import json
import math
from pathlib import Path
from evidence98 import inspect

OUT = Path(__file__).resolve().parents[2] / 'Saved/CombatSlice01/GASPEnemyFoundation01/Worker'


def read(name):
    return json.loads((OUT / (name + '.json')).read_text())


def nearest(rows, time):
    return min(rows, key=lambda row: abs(row['t'] - time))


def main():
    data = read('Final02-ControlsSlow')
    rows = data['rows']
    shots = rows[-1]['rifle']['recent_shots']
    intervals = [[b['time'] - a['time'] for a, b in zip(shots, shots[1:])
                  if a['session'] == b['session'] == session] for session in [2, 4]]
    assert len(intervals[0]) == 7 and len(intervals[1]) == 4
    assert all(abs(v - .085) < 1e-6 for v in intervals[0])
    assert all(abs(v - .340) < 1e-6 for v in intervals[1])
    slow = nearest(rows, 4.2)
    assert slow['global_dilation'] == slow['combat']['scale'] == slow['combat']['player_action_rate'] == .25
    assert abs(slow['global_dilation'] * slow['player_dilation'] - .65) < 1e-6
    assert math.dist(slow['player_velocity'], [0, 0, 0]) > 0
    before, after = nearest(rows, 6.2), nearest(rows, 6.9)
    assert before['rifle']['magazine'] == after['rifle']['magazine'] == 17
    assert before['rifle']['reserve'] == after['rifle']['reserve'] == 90
    assert after['dummy']['epoch'] > before['dummy']['epoch']
    assert after['global_dilation'] == after['player_dilation'] == after['combat']['scale'] == 1
    assert nearest(rows, 8.7)['counts']['dummy'] == 0
    assert nearest(rows, 9.8)['counts']['dummy'] == 3
    assert all(r['counts']['dummy'] == r['counts']['gasp_foundation'] for r in rows)
    assert all(r['counts']['orphan_foundation'] == r['counts']['legacy'] == 0 for r in rows)
    assisted = [r['dummy']['recoverability'] for r in rows if r.get('dummy') and r['dummy']['recoverability']['assistance']]
    bounds = {k: sorted(set(r[k] for r in assisted)) for k in ['strength', 'speed', 'reach_limit_cm', 'persistence_limit_seconds']}
    assert bounds == dict(strength=[1.5], speed=[1.5], reach_limit_cm=[45], persistence_limit_seconds=[3])
    on, off = nearest(rows, 1.4), rows[-1]
    assert on['combat']['immortal_dummies'] and on['combat']['recovery_assistance'] and on['rifle']['infinite_reserve']
    assert not off['combat']['immortal_dummies'] and not off['combat']['recovery_assistance'] and not off['rifle']['infinite_reserve']
    report = dict(case='Final02-ControlsSlow', samples=len(rows), normal_intervals_seconds=intervals[0],
        slow_intervals_seconds=intervals[1], global_scale=.25, bullet_scale=.25, rifle_clock_scale=.25,
        player_custom_dilation=slow['player_dilation'], effective_player_movement_scale=.65,
        moving_player_observed=True, reset_magazine_before_after=[17, 17], reset_reserve_before_after=[90, 90],
        reset_epochs=[before['dummy']['epoch'], after['dummy']['epoch']], assistance_bounds=bounds,
        toggles_restored=True, fixture_count_range=[0, 3], orphan_rows=0, child_wrapper_count_mismatches=0)
    with (OUT / 'controls-analysis02.json').open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2)
    names = ['Final01-ThreeRendered', 'Final01-MovingRifle', 'Final01-LegArm', 'Final01-FallInterruptResume',
        'Final01-DeathCorpse', 'Final02-ControlsSlow', 'Final03-Blocked', 'Pilot05-Movement',
        'Pilot08-SuccessiveTorso', 'Pilot09-MovingTorso', 'Pilot11-FallResume', 'Pilot11-Interrupt', 'Pilot11-Unsupported']
    reports = [inspect(name) for name in names]
    blocked = next(r for r in reports if r['name'] == 'Final03-Blocked')
    assert blocked['getups'] == 1 and blocked['final_authority'] == 'Locomotion'
    assert all(t['t'] > 7.5 for t in blocked['transitions'] if t['state'][0] == 'GettingUp')
    assert max(h['capsule_delta_cm'] for h in blocked['handovers']) < 2
    with (OUT / 'final-analysis02.json').open('x', encoding='utf-8') as stream:
        json.dump(reports, stream, indent=2)
    print(json.dumps(dict(controls=report, cases=len(reports), blocked=blocked)))


if __name__ == '__main__':
    main()
