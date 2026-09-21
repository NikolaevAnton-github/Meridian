"""Compare the affected recovery handoff, using game-time pose derivatives."""
import json
import math
import sys
from pathlib import Path

from analyze_heading02 import analyze as heading

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/GASPEnemyFoundation01'


def subtract(a, b):
    return [x - y for x, y in zip(a, b)]


def length(a):
    return math.sqrt(sum(x * x for x in a))


def analyze(name):
    data = json.loads((OUT / 'Worker' / (name + '.json')).read_text())
    assert not data['error'], data['error']
    rows = data['rows']
    returns = []
    for i in range(2, len(rows)):
        before, after = rows[i - 1:i + 1]
        if 'RECOVERY' not in before['authority'] or 'LOCOMOTION' not in after['authority']:
            continue
        window = []
        for row in rows[i:]:
            if (row['world_time'] > after['world_time'] + .9 or
                    'LOCOMOTION' not in row['authority'] or
                    row['dummy']['physical_hits'] != after['dummy']['physical_hits']):
                break
            window.append(row)
        values = {}
        for field in ['visual', 'targets']:
            values[field] = {}
            for bone in ['hand_l', 'hand_r', 'pelvis', 'foot_l', 'foot_r']:
                velocities, accelerations = [], []
                # Cached animation poses were not driving the native recovery
                # controls. Compare only active source targets, while rendered
                # continuity must include the authority boundary itself.
                samples = window if field == 'targets' else rows[i - 2:i] + window
                for a, b in zip(samples, samples[1:]):
                    dt = b['world_time'] - a['world_time']
                    if dt <= .001:
                        continue
                    # Wrist relative to chest distinguishes arm motion from translation.
                    positions = [subtract(r[field][bone], r[field]['spine_05'])
                                 if bone.startswith('hand') else r[field][bone] for r in [a, b]]
                    v = [x / dt for x in subtract(positions[1], positions[0])]
                    if velocities:
                        accelerations.append(length(subtract(v, velocities[-1])) / dt)
                    velocities.append(v)
                values[field][bone] = dict(peak_speed_cm_s=max(map(length, velocities), default=0),
                    peak_acceleration_cm_s2=max(accelerations, default=0))
        returns.append(dict(t=after['t'], game_seconds=window[-1]['world_time'] - after['world_time'],
            interrupted=len(window) > 0 and window[-1] != rows[-1] and
                window[-1]['world_time'] - after['world_time'] < .8,
            values=values))
    assert returns, 'No recovery handoff observed'
    states = [r['full_state'] for r in rows if r['full_state']]
    return dict(case=name, handoffs=returns,
        conflicting_controls=sum(bool(s['gasp']['enabled_source_controls'] and
            s['balance']['enabled_drives']) for s in states),
        unbounded_controls=sum(s['gasp']['unbounded_source_controls'] for s in states),
        active_handoff_outside_locomotion=sum(s['gasp'].get('pose_handoff_active', False) and
            s['gasp']['authority'] != 'Locomotion' for s in states),
        duplicate_physics_ticks=sum(s['gasp'].get('source_component_tick_enabled', False) for s in states),
        final_authority=rows[-1]['authority'], events=data['events'])


if __name__ == '__main__':
    baseline, fixed = [analyze(name) for name in sys.argv[1:3]]
    comparison = {}
    for field in ['visual', 'targets']:
        comparison[field] = {}
        for metric in ['peak_speed_cm_s', 'peak_acceleration_cm_s2']:
            peaks = [max(h['values'][field][bone][metric] for h in report['handoffs']
                if h['game_seconds'] > .8 for bone in ['hand_l', 'hand_r']) for report in [baseline, fixed]]
            comparison[field][metric] = dict(before=peaks[0], after=peaks[1], ratio=peaks[1] / peaks[0])
    heading_report = heading(sys.argv[2])
    passed = (all(comparison[f][m]['ratio'] < .5 for f in comparison for m in comparison[f]) and
        heading_report['passed'] and not fixed['conflicting_controls'] and not fixed['unbounded_controls'] and
        not fixed['duplicate_physics_ticks'] and not fixed['active_handoff_outside_locomotion'])
    report = dict(passed=passed, comparison=comparison, baseline=baseline, fixed=fixed, heading=heading_report)
    destination = OUT / 'HandoffCorrection03' / ('analysis-' + sys.argv[2] + '.json')
    with destination.open('x') as stream:
        json.dump(report, stream, indent=2)
    print(json.dumps(dict(passed=passed, comparison=comparison, heading=heading_report)))
    raise SystemExit(0 if passed else 1)
