"""Run focused cases with the established native input driver and optional video recorder."""
import json
import subprocess
import sys
import time
from pathlib import Path
from client68 import epic, work

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/CombatFoundation01/Worker'

def run(case):
    assert not epic('EditorToolset.EditorAppToolset', 'IsPIERunning'), 'Existing PIE belongs to another session'
    work('performance')
    options = {'bSimulate': False, 'playMode': 'PlayMode_InViewPort', 'warmupSeconds': .6,
        'startTransform': {'location': dict(zip(['x', 'y', 'z'], case.get('location', [-1600, 0, 100]))),
                           'rotation': {'pitch': case.get('pitch', 0), 'yaw': case.get('yaw', 0), 'roll': 0},
                           'scale': {'x': 1, 'y': 1, 'z': 1}}}
    process = None
    capture_log = None
    try:
        if case.get('fps'):
            work('frame_rate', str(case['fps']))
        epic('EditorToolset.EditorAppToolset', 'StartPIE', {'options': options})
        if case.get('video_pid'):
            (OUT / 'Video').mkdir(parents=True, exist_ok=True)
            capture_log = (OUT / 'Video' / (case['name'] + '.capture.log')).open('x', encoding='utf-8')
            process = subprocess.Popen([sys.executable, str(ROOT / 'Scripts/CombatFoundation01/video68.py'),
                                        str(case['video_pid']), case['name'], str(case['duration'] + 2), str(OUT / 'Video')],
                                       creationflags=subprocess.CREATE_NO_WINDOW, stdout=capture_log, stderr=subprocess.STDOUT)
            ready = OUT / 'Video' / (case['name'] + '.ready.json')
            deadline = time.monotonic() + 15
            while not ready.exists():
                assert process.poll() is None, 'Capture stopped before readiness'
                assert time.monotonic() < deadline
                time.sleep(.1)
        work('verify', json.dumps(case))
        deadline = time.monotonic() + case['duration'] * 4 + 30
        while True:
            time.sleep(.7)
            result = work('verify_status')
            if result['done']:
                print(json.dumps(result), flush=True)
                assert not result['error'], result
                break
            assert time.monotonic() < deadline, result
        if process:
            code = process.wait(timeout=15)
            assert code == 0, 'Capture failed with exit code ' + str(code)
    finally:
        if process and process.poll() is None:
            process.terminate()
            process.wait(timeout=10)
        if capture_log:
            capture_log.close()
        if epic('EditorToolset.EditorAppToolset', 'IsPIERunning'):
            epic('EditorToolset.EditorAppToolset', 'StopPIE')
        work('performance', 'restore')

if __name__ == '__main__':
    if sys.argv[1] in ['ballistics', 'corrections']:
        assert not epic('EditorToolset.EditorAppToolset', 'IsPIERunning')
        work('performance')
        try:
            epic('EditorToolset.EditorAppToolset', 'StartPIE', {'options': {'bSimulate': False,
                 'playMode': 'PlayMode_InViewPort', 'warmupSeconds': .5,
                 'startTransform': {'location': {'x': -1600, 'y': 0, 'z': 100},
                                    'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0},
                                    'scale': {'x': 1, 'y': 1, 'z': 1}}}})
            report = work(sys.argv[1], sys.argv[2])
            print(json.dumps(report))
            assert report and not any(value is False for value in report.values()), report
        finally:
            if epic('EditorToolset.EditorAppToolset', 'IsPIERunning'):
                epic('EditorToolset.EditorAppToolset', 'StopPIE')
            work('performance', 'restore')
    else:
        for case in json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig')):
            if len(sys.argv) > 2 and sys.argv[2] != '-':
                case['name'] = sys.argv[2] + case['name']
            if case.pop('capture', False) and len(sys.argv) > 3:
                case['video_pid'] = int(sys.argv[3])
            run(case)
