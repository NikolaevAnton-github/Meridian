"""Summarize frozen audit telemetry without opening Unreal or changing evidence."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path


def span(values):
    values = list(values)
    return [min(values), max(values)]


def distribution(values):
    return dict(Counter(str(value) for value in values))


def angle(sample):
    target = sample['combat']['decision_input']['known_aim']
    direction = [a - b for a, b in zip(target, sample['muzzle'])]
    barrel = sample['barrel']
    dot = sum(a * b for a, b in zip(direction, barrel))
    length = math.sqrt(sum(a*a for a in direction) * sum(a*a for a in barrel))
    return math.degrees(math.acos(max(-1, min(1, dot / length))))


def summarize(path):
    data = json.loads(path.read_text(encoding='utf-8'))
    samples = data['samples']
    rows = [s['combat']['decision_input'] for s in samples]
    first, last = rows[0]['self_feet'], rows[-1]['self_feet']
    return {
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'world_interval': [data['start'], data['end']],
        'duration_seconds': data['end'] - data['start'],
        'samples': len(samples),
        'states': distribution(s['combat']['state'] for s in samples),
        'distributions': {key: distribution(r[key] for r in rows) for key in [
            'visible', 'motion_fire_gate', 'last_launch_gate', 'actual_crouch',
            'cover_phase', 'mobile_phase', 'shots', 'range_intent', 'pending_gate']},
        'barrel_error_degrees': span(angle(s) for s in samples),
        'source_aim_weight': span(s['gasp']['source_aim_weight'] for s in samples),
        'source_gait': distribution(s['gasp']['source_gait'] for s in samples),
        'delta_world_seconds': span(r['delta_world_seconds'] for r in rows),
        'max_ground_speed_cm_s': max(r['actual_ground_speed'] for r in rows),
        'feet_first_last': [first, last],
        'sampled_displacement_2d_cm': math.hypot(last[0]-first[0], last[1]-first[1]),
        'head_height_above_feet_cm': span(s['head'][2] - r['self_feet'][2] for s, r in zip(samples, rows)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, default=Path('Saved/GASPALSAIAudit01'))
    parser.add_argument('--output', type=Path, help='New file only; omit to print')
    args = parser.parse_args()
    result = {'schema': 1, 'samples': {p.name: summarize(p) for p in sorted(args.evidence.glob('samples-*.json'))}}
    log = args.evidence / 'editor-log-frozen.log'
    if log.exists():
        # Everything before the audit StartPIE belongs to the retained editor history.
        previous = log.read_text(encoding='utf-8', errors='replace').split(
            "[2026.09.24-12.32.09:071][558]LogModelContextProtocol: Dispatching toolset tool: 'EditorToolset.EditorAppToolset.StartPIE'")[0]
        lines = previous.splitlines()
        phrases = ['Failed to find bone data for', 'DestroyControl - failed to find controls/set',
                   'Array has changed during ranged-for iteration!', 'LogPlayerCombatReceiver:']
        result['prior_editor_log'] = {
            'sha256': hashlib.sha256(log.read_bytes()).hexdigest(),
            'cutoff_utc': '2026-09-24T12:32:09.071Z',
            'matching_line_counts_not_unique_incidents': {p: sum(p in line for line in lines) for p in phrases},
            'player_hit_lines': [line for line in lines if 'LogPlayerCombatReceiver:' in line],
        }
    encoded = json.dumps(result, indent=2)
    if args.output:
        with args.output.open('x', encoding='utf-8') as output:
            output.write(encoded + '\n')
        print(args.output)
    else:
        print(encoded)


if __name__ == '__main__':
    main()
