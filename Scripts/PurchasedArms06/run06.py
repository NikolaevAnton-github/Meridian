"""Reuse MSQ-62 input/video capture for a matched hip and ADS shooting take."""
import json
import faulthandler
import sys
import traceback
import ctypes
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/PurchasedArms06/Worker'
sys.path.insert(0, str(ROOT / 'Saved/PurchasedArms04/Worker/PythonPackages'))
sys.path.insert(0, str(ROOT / 'Scripts/PurchasedArms02'))


def work(operation, argument=''):
    from client import epic
    result = epic('Game.Scripts.PurchasedArms06.tools06.PurchasedArms06Tools', 'action',
                  {'operation': operation, 'argument': argument})
    result = json.loads(result) if isinstance(result, str) else result
    if isinstance(result, dict) and result.get('error'):
        raise RuntimeError(result['error'])
    return result


if __name__ == '__main__':
    if sys.argv[1].isdigit():
        import capture02
        with (OUT / 'Video' / (sys.argv[2] + '.capture.log')).open('w', encoding='utf-8') as log:
            faulthandler.enable(log)
            try:
                capture02.main(OUT / 'Video')
            except Exception:
                traceback.print_exc(file=log)
                user = ctypes.windll.user32
                user.GetForegroundWindow.restype = ctypes.c_void_p
                current = user.GetForegroundWindow()
                title = ctypes.create_unicode_buffer(512)
                user.GetWindowTextW(ctypes.c_void_p(current), title, 512)
                owner = ctypes.c_ulong()
                user.GetWindowThreadProcessId(ctypes.c_void_p(current), ctypes.byref(owner))
                log.write(json.dumps({'foreground_hwnd': current, 'foreground_pid': owner.value,
                                      'foreground_title': title.value}) + '\n')
                raise
    else:
        from client import epic
        import video_cases
        video_cases.work = work
        video_cases.OUT = OUT
        case = {'name': sys.argv[1], 'duration': 11, 'events': [
            [.3, 'V', 1], [.38, 'V', 0],
            [2, 'LeftMouseButton', 1], [3.1, 'LeftMouseButton', 0],
            [4.5, 'RightMouseButton', 1],
            [6, 'LeftMouseButton', 1], [7.1, 'LeftMouseButton', 0],
            [8.5, 'RightMouseButton', 0]]}
        assert not epic('EditorToolset.EditorAppToolset', 'IsPIERunning'), 'An existing PIE session is not owned by this capture.'
        try:
            video_cases.run(case, int(sys.argv[2]), Path(__file__))
        finally:
            if epic('EditorToolset.EditorAppToolset', 'IsPIERunning'):
                epic('EditorToolset.EditorAppToolset', 'StopPIE')
            work('performance', 'restore')
