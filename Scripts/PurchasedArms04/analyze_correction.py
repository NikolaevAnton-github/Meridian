"""Inspect only corrected jump/landing transitions and their actual recorded views."""
import json
import math
import sys
from pathlib import Path
from analyze04 import inspect, pose, speed

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/PurchasedArms04/Worker'
DEST = OUT / 'Correction01'
sys.path.insert(0, str(OUT / 'PythonPackages'))
import av
from PIL import Image, ImageDraw


def character_part(row):
    return next(p for p in row['parts'] if 'hand_l' in p.get('bones', {}))


def main():
    result = {'cases': {}, 'views': [], 'scope': 'Four jump/landing takes only; no repeated busy/crouch or unrelated matrix.'}
    all_rows = {}
    for name in ['Ordinary', 'ShiftHeld', 'ShiftReleased', 'Alt']:
        stem = 'Correction01-' + name
        data, summary = inspect(OUT / (stem + '.json'))
        rows = data['rows']
        all_rows[name] = rows
        first = summary['jumps'][0]
        fast = name != 'Ordinary'
        assert first['takeoff_setting_cm_s'] == (352 if fast else 320)
        assert all(abs(s - {'Ordinary': 360, 'ShiftHeld': 540, 'ShiftReleased': 540, 'Alt': 720}[name]) < .01
                   for s in first['planar_speed_range_cm_s'])
        active = [r for r in rows if first['first_airborne_t'] <= r['t'] <= first['landing_t'] + .3]
        assert active and all(r['animation_jump_base'] == fast for r in active)
        if fast:
            last_guard = max(r['t'] for r in rows if r['animation_jump_base'])
            assert last_guard > first['landing_t'] + .4
            summary['ordinary_base_until_t'] = last_guard
            summary['protected_landing_seconds'] = last_guard - first['landing_t']
        else:
            assert not any(r['animation_jump_base'] for r in rows)
        assert not rows[-1]['animation_jump_base']
        for jump in summary['jumps']:
            moving = [r for r in rows if jump['last_grounded_t'] <= r['t'] <= jump['recovered_t']]
            assert all(b['move_binding_samples'] > a['move_binding_samples'] for a, b in zip(moving, moving[1:]))
        if name == 'ShiftHeld':
            assert first['recovered_running'] and abs(first['recovered_speed_cm_s'] - 540) < .01
        if name == 'Alt':
            assert first['recovered_sprinting'] and abs(first['recovered_speed_cm_s'] - 720) < .01
        if name == 'ShiftReleased':
            assert len(summary['jumps']) == 2 and summary['jumps'][1]['takeoff_setting_cm_s'] == 320
            assert abs(summary['jumps'][1]['height_cm'] - 52.24) < .1
            assert not first['recovered_running'] and abs(first['recovered_speed_cm_s'] - 360) < .01
        phase_rows = []
        for phase in [.1, .3, .5, .65, .9, 1.15]:
            candidates = [r for r in rows if pose(r)['montage'] == 'AM_TFA_FP_AR_Jump_Full' and r['t'] < 2.3]
            row = min(candidates, key=lambda r: abs(pose(r)['action_time'] - phase))
            phase_rows.append(row)
        summary['gun_by_phase'] = [{'phase': pose(r)['action_time'], 't': r['t'],
                                    'camera_p': character_part(r)['bones']['ik_hand_gun']['p']} for r in phase_rows]
        if fast:
            # Inspect the compatible base well after the original 0.2 s transition.
            assert all(-18 < entry['camera_p'][2] < -10 for entry in summary['gun_by_phase'][1:])
        result['cases'][name] = summary

        video = OUT / 'Video' / (stem + '.mp4')
        frames_meta = json.loads(video.with_suffix('.json').read_text())['frames']
        with av.open(str(video)) as stream:
            frames = [f.to_image() for f in stream.decode(video=0)]
        assert len(frames) == len(frames_meta)
        recovery = min(rows, key=lambda r: abs(r['t'] - first['landing_t'] - .75))
        selected = [rows[0], *phase_rows, recovery]
        sheet = Image.new('RGB', (1280, 4 * 455), '#171717')
        draw = ImageDraw.Draw(sheet)
        for index, row in enumerate(selected):
            i = min(range(len(frames_meta)), key=lambda i: abs(frames_meta[i]['wall'] - row['capture_wall_monotonic']))
            actual = min(rows, key=lambda r: abs(r['capture_wall_monotonic'] - frames_meta[i]['wall']))
            full = frames[i]
            label = f'{name} t={actual["t"]:.3f} phase={pose(actual)["action_time"]:.3f} guard={actual["animation_jump_base"]}'
            frame_path = DEST / f'{name}-{index:02d}.png'
            assert not frame_path.exists()
            full.save(frame_path)
            tile = full.copy(); tile.thumbnail((640, 431))
            x, y = index % 2 * 640, index // 2 * 455
            sheet.paste(tile, (x, y + 24)); draw.text((x + 6, y + 6), label, fill='white')
            result['views'].append({'file': frame_path.name, 'video': video.name,
                'video_frame': i, 'sample_t': actual['t'], 'montage_phase': pose(actual)['action_time'],
                'alignment_seconds': frames_meta[i]['wall'] - actual['capture_wall_monotonic']})
        sheet.save(DEST / (name + '-sequence.jpg'), quality=93)
    ordinary, held = result['cases']['Ordinary']['jumps'][0], result['cases']['ShiftHeld']['jumps'][0]
    assert abs(ordinary['height_cm'] - 52.24) < .1 and abs(held['height_cm'] - 63.21) < .1
    result['passed'] = True
    result['total_samples'] = sum(c['samples'] for c in result['cases'].values())
    result['visual_status'] = 'Actual frames extracted; worker must inspect them before assigning visual acceptance.'
    path = DEST / 'analysis.json'
    assert not path.exists()
    path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({n: {'jumps': d['jumps'], 'gun_by_phase': d['gun_by_phase']} for n, d in result['cases'].items()}))


if __name__ == '__main__':
    main()
