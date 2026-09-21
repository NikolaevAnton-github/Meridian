"""Check the affected upright handoff against physical and animation-target evidence."""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/GASPEnemyFoundation01'


def lean(pose):
    direction = [a - b for a, b in zip(pose['spine_05'], pose['pelvis'])]
    length = math.sqrt(sum(x * x for x in direction))
    assert length > 1
    return math.degrees(math.acos(max(-1, min(1, direction[2] / length))))


def analyze(name):
    data = json.loads((OUT / 'Worker' / (name + '.json')).read_text())
    assert not data['error'], data['error']
    rows = data['rows']
    releases = []
    for i, (before, after) in enumerate(zip(rows, rows[1:]), 1):
        if 'RECOVERY' not in before['authority'] or 'LOCOMOTION' not in after['authority']:
            continue
        window = []
        for row in rows[i:]:
            if row['t'] > after['t'] + 1.2 or 'LOCOMOTION' not in row['authority']:
                break
            window.append(row)
        releases.append(dict(t=after['t'], samples=len(window),
            previous_getups=(before['full_state'] or next(
                r['full_state'] for r in reversed(rows[:i]) if r['full_state']))['balance']['get_ups'],
            maximum_lean_degrees={field: max(lean(r[field]) for r in window)
                for field in ['physical', 'visual', 'targets']},
            maximum_capsule_frame_displacement_cm=max(
                (math.dist(a['capsule'], b['capsule']) for a, b in zip([before] + window, window)), default=0)))
    assert releases, 'No supported recovery-to-locomotion handoff was observed.'
    full_states = [r['full_state'] for r in rows if r['full_state']]
    report = dict(case=name, samples=len(rows), mean_observer_fps=len(rows) / rows[-1]['wall'],
        real_rifle_hits=rows[-1]['dummy']['physical_hits'], releases=releases,
        maximum_return_lean_degrees={field: max(r['maximum_lean_degrees'][field] for r in releases)
            for field in ['physical', 'visual', 'targets']},
        getups=max(s['balance']['get_ups'] for s in full_states),
        interruptions=max(s['balance']['interruptions'] for s in full_states),
        completed_steps=max(s['step']['completed'] for s in full_states),
        conflicting_controls_at_recorded_transitions=sum(
            bool(s['gasp']['enabled_source_controls'] and s['balance']['enabled_drives']) for s in full_states),
        normal_and_quarter_time_observed={r['global_dilation'] for r in rows} == {0.25, 1.0},
        final_authority=rows[-1]['authority'], final_mode=rows[-1]['mover_mode'], events=data['events'])
    commands = [e for e in data['events'] if e['key'] == 'move' and any(e['value'])]
    stops = [e for e in data['events'] if e['key'] == 'move' and not any(e['value'])]
    if commands and stops:
        first = min(rows, key=lambda r: abs(r['t'] - commands[0]['t']))
        last = min(rows, key=lambda r: abs(r['t'] - stops[-1]['t']))
        report['commanded_travel_cm'] = math.dist(first['capsule'], last['capsule'])
    report['handoff_pass'] = all(
        max(r['maximum_lean_degrees'].values()) < 20 and r['maximum_capsule_frame_displacement_cm'] < 5
        for r in releases) and report['conflicting_controls_at_recorded_transitions'] == 0
    report['post_getup_recovery_observed'] = any(r['previous_getups'] > 0 for r in releases)
    late_shots = [e for e in data['events'] if e['key'] == 'rifle_after_getup']
    late_shots_requested = any(e[1] == 'rifle_after_getup'
        for e in data['config'].get('handoff_events', []))
    report['post_getup_rifle_hits'] = (rows[-1]['dummy']['physical_hits'] -
        next(r for r in reversed(rows) if r['t'] < late_shots[0]['t'])['dummy']['physical_hits']) if late_shots else 0
    report['coverage_pass'] = (not late_shots_requested or (
        report['post_getup_recovery_observed'] and report['post_getup_rifle_hits'] > 0))
    if commands:
        report['coverage_pass'] = report['coverage_pass'] and report.get('commanded_travel_cm', 0) > 10
    report['focused_pass'] = (report['handoff_pass'] and report['coverage_pass'] and
        report['normal_and_quarter_time_observed'] and 'LOCOMOTION' in report['final_authority'] and
        report['final_mode'] == 'Walking')
    return report


if __name__ == '__main__':
    reports = [analyze(name) for name in sys.argv[1:]]
    destination = OUT / 'HandoffCorrection01' / ('analysis-' + sys.argv[-1] + '.json')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('x', encoding='utf-8') as stream:
        json.dump(reports, stream, indent=2)
    for report in reports:
        print(json.dumps({key: value for key, value in report.items() if key not in ['events', 'releases']}))
    # A baseline may intentionally fail; the final supplied case is the candidate.
    raise SystemExit(0 if reports[-1]['focused_pass'] else 1)
