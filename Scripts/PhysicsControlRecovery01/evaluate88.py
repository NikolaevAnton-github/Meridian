"""Summarize retained MSQ-87 recorder output for the affected MSQ-88 criteria.

This is evidence postprocessing, not a replacement gameplay/animation harness.
Visual motion acceptance is deliberately not inferred from numerical checks.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlRecovery01/Worker'
NAMES = ['Back', 'ProneBasis02', 'AsymmetricView02', 'FrontSettledSlow',
         'InterruptedDeathReset', 'BlockedAndAnchors', 'UnsupportedView', 'SixRendered']

def span(values):
    values = list(values)
    return [min(values), max(values)] if values else None

def balance(row):
    return row['dummy']['balance']

def summarize(name):
    data = json.loads((OUT / (name + '.json')).read_text())
    rows = data['rows']
    transitions = []
    previous = None
    for r in rows:
        d, b = r['dummy'], balance(r)
        key = (b['state'], b['reason'], d['health'], d['epoch'])
        if key != previous:
            transitions.append(dict(t=r['t'], state=b['state'], reason=b['reason'],
                hp=d['health'], epoch=d['epoch'], drives=b['enabled_drives'],
                animation=b['animation'], snapshot_bones=b['snapshot_bones'],
                snapshot_first_error_cm=b['snapshot_first_error_cm'],
                pelvis=d['bodies']['pelvis']['position']))
            previous = key
    up = [r for r in rows if balance(r)['state'] == 'GETTING UP']
    standing = [r for r in rows if balance(r)['state'] == 'STANDING']
    skin = []
    for path in sorted(OUT.glob(name + '-skin-*.json')):
        audit = json.loads(path.read_text())
        floor = audit['runtime']['balance']['ground_z']
        skin.append(dict(path=path.relative_to(ROOT).as_posix(), floor_z=floor,
            vertices=len(audit['foot_vertices']), skeleton_bones=audit['skeleton_bones'],
            sole_gap_cm={side: min(v['world'][2] for v in audit['foot_vertices']
                if v['bone'].endswith('_'+side))-floor for side in ['l','r']}))
    capture = json.loads((OUT / 'Video' / (name + '.capture.json')).read_text())
    stamps = [f['t'] for f in capture['frames']]
    slow = [r for r in rows if r['global_dilation'] == .25]
    same_epoch = [(a, b) for a, b in zip(rows, rows[1:]) if a['dummy']['epoch'] == b['dummy']['epoch']]
    checks = dict(
        recorder_ok=data['error'] is None,
        six_fixtures=all(r['counts'] == dict(dummy=6, legacy=0, manager=1, controller=1) for r in rows),
        snapshot_full_lod0=all(balance(r)['snapshot_bones'] == balance(r)['skeleton_bones'] == 89
            and balance(r)['lod'] == 0 for r in up),
        no_healing_within_epoch=all(b['dummy']['health'] <= a['dummy']['health'] for a,b in same_epoch),
        released_drives=all(balance(r)['enabled_drives'] == 0 for r in rows
            if balance(r)['state'] in ['FALLING','DOWN','CORPSE']),
        standing_sole_tolerance=all(-.1 <= balance(r)[k]-balance(r)['ground_z'] <= 1
            for r in standing for k in ['sole_left_z','sole_right_z']),
        measured_skin_tolerance=all(-.1 <= gap <= 1 for a in skin for gap in a['sole_gap_cm'].values()),
        other_instances_unchanged=all(f['health'] == 100 and f['hits'] == f['deaths'] == 0
            for r in rows for f in r['fixtures'] if f['profile'] != 1),
        continuous_capture_complete=stamps[-1] >= data['config']['duration']-.5)
    result = dict(name=name, checks=checks, samples=len(rows), duration=rows[-1]['t'],
        events=data['events'], transitions=transitions,
        standing_gaps_cm={k: span(balance(r)[k]-balance(r)['ground_z'] for r in standing)
            for k in ['sole_left_z','sole_right_z','foot_l_shape_bottom_z','foot_r_shape_bottom_z']},
        actual_skinned_soles=skin,
        snapshot_first_error_cm=span(balance(r)['snapshot_first_error_cm'] for r in up),
        blending_motion_times=[dict(t=r['t'], state_seconds=balance(r)['state_seconds'],
            animation_time=balance(r)['animation_time']) for r in up
            if balance(r)['state_seconds'] < .76][::8],
        max_locked_anchor_gap_cm=max(r['dummy']['max_locked_joint_anchor_gap_cm'] for r in rows),
        magazine=[rows[0]['rifle']['magazine'],rows[-1]['rifle']['magazine']],
        last_pelvis=rows[-1]['dummy']['bodies']['pelvis']['position'],
        capture=dict(frames=len(stamps), seconds=stamps[-1],
            max_gap_seconds=max(b-a for a,b in zip(stamps,stamps[1:])),
            backend=capture['backend']))
    if slow:
        a, b = slow[0], slow[-1]
        result['slowdown'] = dict(manager_seconds=b['t']-a['t'],
            recovery_seconds=balance(b)['state_seconds']-balance(a)['state_seconds'],
            effective_player_rate=span(r['global_dilation']*r['player_dilation'] for r in slow))
    return result

def main():
    dest = OUT / (sys.argv[1] if len(sys.argv)>1 else 'focused-results02.json')
    assert not dest.exists(), dest
    results = [summarize('Candidate02-'+name) for name in NAMES]
    reference = json.loads((OUT/'Candidate02/manifest.json').read_text())
    identity = []
    for row in reference:
        if row['path'].startswith(('Source/','Binaries/','Content/')):
            current = hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()
            identity.append(dict(path=row['path'], sha256=current, unchanged=current==row['sha256']))
    result = dict(candidate='Candidate04', gameplay_evidence_candidate='Candidate02',
        sole_tolerance_cm=1, standing_measurement='Every recorded STANDING row, including reset settling',
        skin_method='LOD0 CPU-skinned foot/ball vertices, minimum world Z per foot minus traced floor',
        visual_acceptance='Not inferred from numerical checks; continuous recordings and inspected frames accompany the owner motion gate',
        cases=results, reused_gameplay_identity=identity)
    dest.write_text(json.dumps(result,indent=2),encoding='utf-8')
    failed=[(r['name'],k) for r in results for k,v in r['checks'].items() if not v]
    print(json.dumps(dict(report=dest.relative_to(ROOT).as_posix(), failed=failed,
        unchanged_gameplay=all(r['unchanged'] for r in identity),
        cases=[dict(name=r['name'], samples=r['samples'], capture=r['capture']) for r in results]),indent=2))
    assert not failed and all(r['unchanged'] for r in identity)

if __name__ == '__main__':
    main()
