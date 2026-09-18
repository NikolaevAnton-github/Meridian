"""Extract unmodified recorded frames using the shared monotonic capture clock."""
import json
import math
import struct
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/CombatFoundation01/Worker'
sys.path.insert(0, str(ROOT / 'Saved/PurchasedArms04/Worker/PythonPackages'))
import av

def main():
    destination = OUT / 'Review'
    destination.mkdir(exist_ok=True)
    selections = {'SurfaceResetFinal01': [('StoneImpact', .74), ('MetalImpact', 3.73), ('TargetReset', 8.3)],
                  'MovingAirborne01': [('MovingADS', 1.55), ('OrdinaryJumpFire', 5.28), ('ShiftJumpFire', 7.38)],
                  'AmmoDry01': [('EmptyMagazine', 4), ('TargetDestroyed', 11.7)]}
    evidence = []
    for name, requests in selections.items():
        rows = json.loads((OUT / (name + '.json')).read_text())['rows']
        meta = json.loads((OUT / 'Video' / (name + '.json')).read_text())
        chosen = {}
        for label, time in requests:
            row = min(rows, key=lambda r: abs(r['t'] - time))
            frame = min(meta['frames'], key=lambda r: abs(r['wall'] - row['capture_wall_monotonic']))
            chosen[frame['frame']] = label
            evidence.append({'source': name + '.mp4', 'label': label, 'requested_case_time': time,
                             'sample_case_time': row['t'], 'frame': frame['frame'], 'video_seconds': frame['elapsed'],
                             'clock_difference_seconds': frame['wall'] - row['capture_wall_monotonic']})
        with av.open(str(OUT / 'Video' / (name + '.mp4'))) as video:
            for i, frame in enumerate(video.decode(video=0)):
                if i in chosen:
                    path = destination / (chosen[i] + '.png')
                    assert not path.exists(), path
                    frame.to_image().save(path)
    with wave.open(str(OUT / 'Audio/SurfaceResetFinal01.wav')) as audio:
        info = {'channels': audio.getnchannels(), 'sample_width': audio.getsampwidth(),
                'rate': audio.getframerate(), 'frames': audio.getnframes()}
        assert info['sample_width'] == 2
        raw = audio.readframes(info['frames'])
        samples = struct.unpack('<' + 'h' * (len(raw) // 2), raw)
        info['rms'] = math.sqrt(sum((s / 32768) ** 2 for s in samples) / len(samples))
        info['peak'] = max(abs(s) for s in samples) / 32768
        info['duration_seconds'] = info['frames'] / info['rate']
        assert info['rms'] > .0001
    path = destination / 'frame-and-audio-evidence.json'
    assert not path.exists()
    path.write_text(json.dumps({'frames': evidence, 'audio': info}, indent=2))
    print(json.dumps({'frames': len(evidence), 'audio': info}))

def visual_correction():
    name = 'SurfaceVisualFinal02'
    data = json.loads((OUT / (name + '.json')).read_text())
    rows = data['rows']
    meta = json.loads((OUT / 'Video' / (name + '.json')).read_text())
    selected, evidence = {}, []
    for label, time in [('FinalStoneImpact', .74), ('FinalMetalImpact', 3.24), ('FinalReady', 7.4)]:
        row = min(rows, key=lambda r: abs(r['t'] - time))
        frame = min(meta['frames'], key=lambda r: abs(r['wall'] - row['capture_wall_monotonic']))
        selected[frame['frame']] = label
        evidence.append({'label': label, 'frame': frame['frame'], 'video_seconds': frame['elapsed'],
                         'case_time': row['t'], 'clock_difference_seconds': frame['wall'] - row['capture_wall_monotonic']})
    with av.open(str(OUT / 'Video' / (name + '.mp4'))) as video:
        for i, frame in enumerate(video.decode(video=0)):
            if i in selected:
                path = OUT / 'Review' / (selected[i] + '.png')
                assert not path.exists(), path
                frame.to_image().save(path)
    final = rows[-1]
    result = {'frames': evidence, 'samples': len(rows), 'shots': final['rifle']['shots'],
              'passed': data['error'] is None and final['rifle']['shots'] == 5 and final['rifle']['magazine'] == 25 and
                        final['rifle']['props'] == final['rifle']['effects'] == final['niagara_components'] ==
                        final['ballistics']['impacts'] == final['ballistics']['active'] == 0 and
                        all(t['health'] == 100 for t in final['ballistics']['targets'])}
    path = OUT / 'Review/visual-correction-checks.json'
    assert not path.exists()
    path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result))
    assert result['passed']

if __name__ == '__main__':
    visual_correction() if len(sys.argv) > 1 and sys.argv[1] == 'visual' else main()
