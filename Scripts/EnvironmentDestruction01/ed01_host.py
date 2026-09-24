"""Foreground host for ED-01 evidence, build, and scoped Epic MCP calls."""
import argparse
import base64
import ctypes
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from ed00_mcp import Client, APP

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/EnvironmentDestruction01/ED-01/MSQ-141-Candidate01'

def write(name, data):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open('x', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def sha(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()

def preserved():
    old = json.loads((ROOT / 'Saved/EnvironmentDestruction01/ED-00/MSQ-140-Candidate01/source-before.json').read_text())
    paths = list(old['fingerprints']['files'])
    paths += ['AGENTS.md', 'Config/DefaultEngine.ini', 'MeridianSquad.uproject',
              'Assets/Source/OpeningLobby/FunctionalBuild01/LobbyFunctionalBuild01.blend',
              'Assets/Source/OpeningLobby/MaterialsComplete01/SlabLayout01/recipe.json']
    return {p: sha(ROOT / p) for p in paths}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('operation')
    parser.add_argument('argument', nargs='?', default='')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.operation == 'preserve':
        rows = preserved()
        write('preservation-before.json', rows)
        print(json.dumps({'files': len(rows)}))
    elif args.operation == 'ready':
        start = time.perf_counter()
        last = None
        while time.perf_counter() - start < 45:
            try:
                c = Client()
                level = c.call('editor_toolset.toolsets.scene.SceneTools', 'get_current_level')
                assert level == '/Game/Maps/L_OpeningLobby_DestructionLab01', level
                print(json.dumps({'level': level, 'pie': c.call(APP, 'IsPIERunning')}))
                return
            except Exception as exc:
                last = str(exc)
                time.sleep(1)
        raise RuntimeError(last)
    elif args.operation == 'settings':
        home = ROOT / 'Saved/Multica/workspaces/meridiansqu-6f91832bf07d/msq-141-f6fd17b944f1/codex-home'
        configured = [s for s in (home / 'config.toml').read_text().splitlines() if any(s.startswith(k) for k in ('model =', 'model_reasoning_effort =', 'service_tier ='))]
        session = next((home / 'sessions').rglob('*.jsonl'))
        contexts = []
        for line in session.open(encoding='utf-8'):
            row = json.loads(line)
            if row.get('type') == 'turn_context':
                p = row['payload']
                contexts.append({k: p.get(k) for k in ('model', 'effort', 'summary', 'service_tier', 'collaboration_mode')})
        record = {'configured': configured, 'session': str(session.relative_to(ROOT)), 'native_turn_contexts': contexts,
                  'native_process_flags_observed': ['model=gpt-6-astra', 'model_reasoning_effort=max', 'service_tier=default', '--disable fast_mode']}
        write('worker-settings.json', record)
        print(json.dumps(record))
    elif args.operation == 'footprint':
        total, count = 0, 0
        for folder, directories, files in os.walk(ROOT, followlinks=False):
            for name in files:
                path = Path(folder) / name
                try:
                    total += path.stat().st_size
                    count += 1
                except (FileNotFoundError, PermissionError):
                    pass
        task_paths = ['Content/Development/EnvironmentDestruction01', 'Assets/Source/EnvironmentDestruction01',
                      'Saved/EnvironmentDestruction01/ED-01']
        task_bytes = sum(p.stat().st_size for part in task_paths for p in (ROOT / part).rglob('*') if p.is_file())
        record = {'workspace_bytes': total, 'workspace_decimal_gb': total / 1e9, 'files': count, 'ed01_bytes': task_bytes,
                  'scope': 'Workspace regular files including .git, Saved and local services; no followed symlink trees.'}
        write('footprint.json', record)
        print(json.dumps(record))
    elif args.operation == 'verify-preserved':
        before = json.loads((OUT / 'preservation-before.json').read_text())
        changed = [p for p, h in before.items() if sha(ROOT / p) != h]
        write('preservation-after-' + args.argument + '.json', {'files': len(before), 'changed': changed})
        print(json.dumps({'files': len(before), 'changed': changed}))
        assert not changed
    elif args.operation == 'build':
        commands = ['D:/UE_5.8/Engine/Build/BatchFiles/Build.bat', 'MeridianSquadEditor', 'Win64', 'Development',
                    str(ROOT / 'MeridianSquad.uproject'), '-WaitMutex', '-NoHotReloadFromIDE', '-MaxParallelActions=4']
        started = time.perf_counter()
        with (OUT / ('build-' + args.argument + '.log')).open('xb') as log:
            result = subprocess.run(commands, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        evidence = {'args': commands, 'exit_code': result.returncode, 'seconds': time.perf_counter() - started}
        write('build-' + args.argument + '.json', evidence)
        print(json.dumps(evidence))
        sys.exit(result.returncode)
    else:
        c = Client()
        if args.operation == 'sequence':
            from ctypes import wintypes
            user32 = ctypes.windll.user32
            pid = int((OUT / 'editor-pid.txt').read_text(encoding='utf-8-sig').strip())
            windows = []
            @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            def visit(hwnd, param):
                owner = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
                if owner.value == pid and user32.IsWindowVisible(hwnd):
                    title = ctypes.create_unicode_buffer(500)
                    user32.GetWindowTextW(hwnd, title, 500)
                    windows.append((hwnd, title.value))
                return True
            user32.EnumWindows(visit, 0)
            window = next((h for h, title in windows if 'Preview' in title), windows[0][0])
            user32.ShowWindow(window, 9)
            user32.SetForegroundWindow(window)
            start = time.perf_counter()
            path = OUT / (args.argument + '-complete.json')
            assert not path.exists(), path
            print(c.call('PythonTypes.ED01Tools', 'run', {'operation': 'runtime-sequence', 'argument': args.argument}), flush=True)
            samples = []
            try:
                while time.perf_counter() - start < 52:
                    samples.append({'elapsed': time.perf_counter() - start, 'foreground': int(user32.GetForegroundWindow())})
                    if path.exists():
                        result = json.loads(path.read_text())
                        write(args.argument + '-foreground.json', {'selected': window, 'windows': windows, 'samples': samples})
                        print(json.dumps({'error': result['error'], 'hits': len(result['hits']), 'snapshots': len(result['snapshots'])}))
                        assert result['error'] is None, result['error']
                        return
                    time.sleep(.5)
                raise TimeoutError('ED-01 sequence did not finish within 52 seconds')
            finally:
                if not path.exists():
                    c.call('PythonTypes.ED01Tools', 'run', {'operation': 'runtime-cancel', 'argument': ''})
        elif args.operation in ('start', 'stop'):
            print(c.call(APP, 'StartPIE', {'options': {'bSimulate': False, 'playMode': 'PlayMode_InEditorFloating', 'warmupSeconds': 3}})
                  if args.operation == 'start' else c.call(APP, 'StopPIE'))
        elif args.operation == 'register':
            instance = {'refPath': '/Script/PythonScriptPlugin.Default__PythonScriptPluginSettings'}
            toolset = 'editor_toolset.toolsets.object.ObjectTools'
            original = json.loads(c.call(toolset, 'get_properties', {'instance': instance, 'properties': ['bRemoteExecution']}))
            try:
                c.call(toolset, 'set_properties', {'instance': instance, 'values': json.dumps({'bRemoteExecution': True})})
                subprocess.run([sys.executable, str(ROOT / 'Scripts/EnvironmentDestruction01/ed01_register.py')], check=True)
            finally:
                c.call(toolset, 'set_properties', {'instance': instance, 'values': json.dumps(original)})
        elif args.operation == 'capture':
            image = c.call(APP, 'CaptureViewport', {'bShowUI': False, 'captureTransform': None, 'annotations': None})['image']
            with (OUT / (args.argument + '.png')).open('xb') as f:
                f.write(base64.b64decode(image['data']))
            print(args.argument + '.png')
        elif args.operation == 'pose':
            result = c.call(APP, 'SetCameraTransform', {'transform': {'location': {'x': -1260, 'y': 290, 'z': 172.15}, 'rotation': {'pitch': -6, 'yaw': -90, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
            print(result)
        else:
            result = c.call('PythonTypes.ED01Tools', 'run', {'operation': args.operation, 'argument': args.argument})
            print(result)

if __name__ == '__main__':
    main()
