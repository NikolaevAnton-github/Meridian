"""Check idle heading and arm continuity around the owner-reported GASP handoff."""
import json
import math
import sys
from pathlib import Path

from analyze_handoff01 import lean

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/GASPEnemyFoundation01'


def angle(a, b):
    length = math.sqrt(sum(x * x for x in a) * sum(x * x for x in b))
    if length < .001:
        return None
    return math.degrees(math.acos(max(-1, min(1, sum(x * y for x, y in zip(a, b)) / length))))


def analyze(name):
    data = json.loads((OUT / 'Worker' / (name + '.json')).read_text())
    assert not data['error'], data['error']
    rows = data['rows']
    returns = []
    for i, (before, after) in enumerate(zip(rows, rows[1:]), 1):
        if 'RECOVERY' not in before['authority'] or 'LOCOMOTION' not in after['authority']:
            continue
        window = []
        for row in rows[i:]:
            if (row['t'] > after['t'] + 3 or 'LOCOMOTION' not in row['authority'] or
                    row['dummy']['physical_hits'] != after['dummy']['physical_hits'] or
                    any(row['move_input'])):
                break
            window.append(row)
        if not window:
            continue
        arms = {}
        for side in ['l', 'r']:
            hand, shoulder = 'hand_' + side, 'clavicle_' + side
            offsets = [[x - y for x, y in zip(row['visual'][hand], row['visual']['spine_05'])]
                       for row in [before] + window]
            arms[side] = dict(maximum_frame_displacement_cm=max(
                math.dist(a, b) for a, b in zip(offsets, offsets[1:])),
                maximum_height_above_shoulder_cm=max(
                    row['visual'][hand][2] - row['visual'][shoulder][2] for row in window))
        walking = [r for r in window if r['mover_mode'] == 'Walking']
        returns.append(dict(t=after['t'], samples=len(window),
            observed_seconds=window[-1]['t'] - after['t'],
            maximum_heading_change_degrees=max(angle(before['heading'], r['heading']) for r in window),
            zero_walking_intents=sum(angle(r['orientation_post'], r['heading']) is None for r in walking),
            maximum_intent_error_degrees=max((angle(r['orientation_post'], before['heading']) or 0
                for r in walking), default=0),
            maximum_rendered_torso_lean_degrees=max(lean(r['visual']) for r in window), arms=arms))
    assert returns, 'No idle recovery-to-locomotion handoff observed.'
    passed = all(r['observed_seconds'] > 1 and r['maximum_heading_change_degrees'] < 5 and
        r['maximum_intent_error_degrees'] < 5 and r['zero_walking_intents'] == 0 and
        r['maximum_rendered_torso_lean_degrees'] < 20 and all(
            a['maximum_frame_displacement_cm'] < 12 and a['maximum_height_above_shoulder_cm'] < 0
            for a in r['arms'].values()) for r in returns)
    return dict(case=name, passed=passed, samples=len(rows),
        observer_fps=len(rows) / rows[-1]['wall'],
        real_hits=rows[0]['dummy']['physical_hits'] + sum(max(0,
            b['dummy']['physical_hits'] - a['dummy']['physical_hits']) for a, b in zip(rows, rows[1:])),
        reset_epochs=sorted({r['dummy']['epoch'] for r in rows}), handoffs=returns,
        final_heading=rows[-1]['heading'], final_authority=rows[-1]['authority'])


if __name__ == '__main__':
    reports = [analyze(name) for name in sys.argv[1:]]
    destination = OUT / 'HandoffCorrection02' / ('analysis-' + sys.argv[-1] + '.json')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('x') as stream:
        json.dump(reports, stream, indent=2)
    for report in reports:
        print(json.dumps(report))
    raise SystemExit(0 if reports[-1]['passed'] else 1)
