"""Check only controller-requested correction evidence and extract comparable recorded views."""
import hashlib
import io
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'Saved/CombatSlice01/CombatFoundation01/Worker'
OUT = BASE / 'Correction01'
sys.path.insert(0, str(ROOT / 'Saved/PurchasedArms04/Worker/PythonPackages'))
import av


def main():
    result = {'checks': [], 'cases': {}, 'frames': []}
    def check(name, passed, detail=None):
        result['checks'].append(dict(name=name, passed=bool(passed), detail=detail))
    def read(name):
        path = BASE / (name + '.json')
        data = json.loads(path.read_text())
        rows = data['rows']
        result['cases'][name] = {'samples': len(rows), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        check(name + ': complete driver run', data['error'] is None and len(data['events']) == len(data['config']['events']))
        check(name + ': actual frame cap 60', all(r['frame_rate_limit'] == 60 for r in rows))
        return data, rows
    def window(rows, start, end):
        values = [r for r in rows if start <= r['t'] <= end]
        assert values, (start, end)
        return values
    def shots(rows):
        return [b for a, b in zip(rows, rows[1:]) if b['rifle']['shots'] > a['rifle']['shots']]

    legacy, old = read('Correction01-LegacyADSRelease')
    check('retired Smoke01 refresh order reproduces stale actual key and aim',
          all(not r['held'] and r['aim_key_down'] and r['aim_requested'] and r['fov'] == 78 and r['view_fov'] == 78
              for r in window(old, 1.7, 3.1)))
    ads, rows = read('Correction01-ADSReleaseReentry')
    # Source aim curves take roughly 0.37 s; inspect settled state after 0.4 s,
    # separately from immediate input acceptance and airborne fire eligibility.
    for label, start, end in [('after shot', 1.75, 1.95), ('after reload', 6.02, 6.1),
                              ('after second shot', 7.62, 7.7), ('final release', 8.82, 8.95)]:
        check('actual RMB release ' + label, all(not r['aim_key_down'] and not r['aim_requested'] and
              abs(r['fov'] - 90) < .01 and abs(r['view_fov'] - 90) < .01 for r in window(rows, start, end)))
    for label, start, end in [('initial', .62, .68), ('after shooting', 2.42, 2.55),
                              ('after reload', 6.62, 6.65), ('final reentry', 8.22, 8.3)]:
        check('actual RMB entry ' + label, all(r['aim_key_down'] and r['aim_requested'] and
              abs(r['fov'] - 78) < .01 and abs(r['view_fov'] - 78) < .01 for r in window(rows, start, end)))
    final = rows[-1]['rifle']
    check('ADS sequence really shoots and transfers reload', final['shots'] == 2 and final['transfers'] == 1 and
          final['transferred_rounds'] == 1 and final['magazine'] == 29 and final['reserve'] == 89)
    check('ADS comparison remains stationary', all(abs(r['location'][i] - rows[0]['location'][i]) < .01
          for r in rows for i in [0, 1]))

    cadence, rows = read('Correction01-Cadence60Retry')
    shot_rows = shots(rows)
    burst = [r for r in shot_rows if .7 < r['t'] < 2.71]
    gaps = [b['rifle']['last_shot_time'] - a['rifle']['last_shot_time'] for a, b in zip(burst, burst[1:])]
    mean_interval = statistics.mean(gaps)
    measured_fps = 1 / statistics.mean(r['delta'] for r in window(rows, .8, 2.6))
    check('ordinary frame scheduling measured near 60 fps', 59 < measured_fps < 61, measured_fps)
    check('two-second burst launches 24 rounds', len(burst) == 24, len(burst))
    check('automatic average cadence retains 85 ms phase', abs(mean_interval - .085) < .002, mean_interval)
    check('automatic scheduling never emits multiple rounds in one frame',
          all(b['rifle']['shots'] - a['rifle']['shots'] <= 1 for a, b in zip(rows, rows[1:])))
    locked = [r for r in rows if r['rifle']['reloading']]
    check('held trigger cannot fire through reload', locked and all(r['rifle']['shots'] == 24 for r in locked))
    resumed = [r for r in shot_rows if r['t'] > 3]
    check('held trigger resumes after reload without backlog', len(resumed) == 6 and
          min(b['rifle']['last_shot_time'] - a['rifle']['last_shot_time'] for a, b in zip(resumed, resumed[1:])) > .075)
    check('release stops firing', all(r['rifle']['shots'] == 30 and not r['rifle']['fire_held'] for r in window(rows, 6.3, 6.65)))
    check('burst and reload ammunition conserved', rows[-1]['rifle']['magazine'] == 24 and rows[-1]['rifle']['reserve'] == 66)
    result['cadence'] = dict(measured_fps=measured_fps, burst_shots=len(burst), mean_interval_seconds=mean_interval,
                             rate_per_second=1 / mean_interval, first_last_span_seconds=sum(gaps))

    airborne, rows = read('Correction01-Airborne')
    shot_rows = shots(rows)
    for label, start in [('ordinary', 5), ('Shift', 7)]:
        first = next(r for r in shot_rows if r['t'] > start)
        check(label + ' jump immediately fires with aim input accepted', first['t'] - start < .12 and first['falling'] and
              first['aim_requested'] and first['airborne_fire_held'])
        check(label + ' jump reaches full ADS before landing', any(r['falling'] and r['aim_requested'] and
              abs(r['fov'] - 78) < .01 and abs(r['view_fov'] - 78) < .01 for r in window(rows, start + .42, start + .55)))
        if label == 'Shift':
            check('Shift flight retains 540 cm/s', abs((first['velocity'][0] ** 2 + first['velocity'][1] ** 2) ** .5 - 540) < 1)
    check('two jumps and physical landings', rows[-1]['jump_starts'] == 2 and rows[-1]['landings'] == 2)
    check('held aimed fire continues through landing', any(7.7 < r['t'] < 8 and not r['falling'] and
          r['aim_requested'] for r in shot_rows))
    check('airborne observer clears after release', all(not r['airborne_fire_held'] for r in window(rows, 8.3, 8.8)))

    for name in ['corrections-Correction01', 'ballistics-Correction01']:
        native = json.loads((BASE / (name + '.json')).read_text())
        for key, value in native.items():
            if isinstance(value, bool):
                check(name + ': ' + key, value)
        if 'temporary_actors_remaining' in native:
            check(name + ': no temporary actors', native['temporary_actors_remaining'] == 0)
    material = json.loads((BASE / 'target-material-Correction01.json').read_text())
    check('target material audit has no Color parameter', 'Color' not in material['vector_parameters'])

    selections = {
        'Correction01-ADSReleaseReentry': [('ADSAfterShot', .9), ('HipAfterShot', 1.9), ('ADSReentry', 2.4),
            ('ADSAfterReload', 5.3), ('HipAfterReload', 6), ('ADSReentryAfterReload', 6.6)],
        'Correction01-Airborne': [('OrdinaryJumpFire', 5.25), ('ShiftJumpFire', 7.35),
            ('ShiftADSSettled', 7.47), ('LandingFire', 7.76)]}
    for name, frames in selections.items():
        rows = json.loads((BASE / (name + '.json')).read_text())['rows']
        meta = json.loads((BASE / 'Video' / (name + '.json')).read_text())
        selected = {}
        for label, time in frames:
            row = min(rows, key=lambda r: abs(r['t'] - time))
            frame = min(meta['frames'], key=lambda f: abs(f['wall'] - row['capture_wall_monotonic']))
            selected[frame['frame']] = label
            result['frames'].append(dict(source=name, label=label, frame=frame['frame'], case_time=row['t'],
                video_seconds=frame['elapsed'], clock_difference_seconds=frame['wall'] - row['capture_wall_monotonic'],
                aim_requested=row['aim_requested'], aim_key_down=row['aim_key_down'], camera_fov=row['fov'], view_fov=row['view_fov']))
        with av.open(str(BASE / 'Video' / (name + '.mp4'))) as video:
            for i, frame in enumerate(video.decode(video=0)):
                if i in selected:
                    destination = OUT / (selected[i] + '.png')
                    encoded = io.BytesIO()
                    frame.to_image().save(encoded, format='PNG')
                    if destination.exists():
                        assert destination.read_bytes() == encoded.getvalue(), destination
                    else:
                        destination.write_bytes(encoded.getvalue())
    result['passed'] = all(c['passed'] for c in result['checks'])
    result['checks_count'] = len(result['checks'])
    path = OUT / ('verification' + (sys.argv[1] if len(sys.argv) > 1 else '') + '.json')
    assert not path.exists(), path
    path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'passed': result['passed'], 'checks': result['checks_count'], 'cadence': result['cadence'],
                      'failed': [c for c in result['checks'] if not c['passed']]}))
    assert result['passed']


if __name__ == '__main__':
    main()
