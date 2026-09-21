"""Read-only source and execution preflight; write evidence only under Saved."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import stat
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/GASPEnemyFoundation01/Worker'
OUT.mkdir(parents=True, exist_ok=True)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(name, data):
    with (OUT / name).open('x', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2)


def capacity():
    size = 0
    files = 0
    excluded_reparse_points = []
    for folder, directories, names in os.walk(ROOT, followlinks=False):
        kept = []
        for name in directories:
            path = Path(folder) / name
            if path.stat(follow_symlinks=False).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                excluded_reparse_points.append(path.relative_to(ROOT).as_posix())
            else:
                kept.append(name)
        directories[:] = kept
        for name in names:
            path = Path(folder) / name
            info = path.stat(follow_symlinks=False)
            if not info.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                size += info.st_size
                files += 1
    result = dict(project_bytes=size, files=files, cap_bytes=250_000_000_000,
        scope='Project root including Saved and Git; junction aliases not counted twice; external shared caches/services excluded',
        excluded_reparse_points=excluded_reparse_points)
    write('capacity-before01.json', result)
    return result


def main():
    preserved = []
    for item in json.loads((OUT.parent / 'Controller/preservation-before.json').read_text(encoding='utf-8-sig')):
        path = Path(item['Path'])
        preserved.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=digest(path), expected=item['Hash'].lower()))
    assert all(p['sha256'] == p['expected'] for p in preserved), preserved
    write('preservation-before01.json', preserved)
    sessions = list((Path(os.environ['CODEX_HOME']) / 'sessions').rglob('*.jsonl'))
    contexts = []
    for session in sessions:
        with session.open(encoding='utf-8') as stream:
            for line in stream:
                item = json.loads(line)
                if item.get('type') == 'turn_context':
                    contexts.append({k: item['payload'].get(k) for k in ['model', 'effort', 'service_tier']})
    assert contexts, 'No actual native session context'
    context = contexts[-1]
    assert context['model'] == 'gpt-6-astra' and context['effort'] == 'max', context
    assert context['service_tier'] in [None, 'default', 'standard'], context
    processes = json.loads(subprocess.check_output(['powershell', '-NoProfile', '-Command',
        'Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Compress'], encoding='utf-8'))
    by_id = {p['ProcessId']: p for p in processes}
    native = by_id[os.getpid()]
    while native['Name'] != 'codex.exe':
        native = by_id[native['ParentProcessId']]
    command = native['CommandLine']
    assert '--disable fast_mode' in command and all(x in command for x in ['max', 'default', 'gpt-6-astra'])
    profile = next(p for p in json.loads((OUT.parent / 'Controller/agents-before.json').read_text(encoding='utf-8-sig')) if p['id'] == 'd3ed0aae-f7e4-40d2-9568-9aa9b11fdf51')
    assert profile['model'] == 'gpt-6-astra' and profile['thinking_level'] == 'max' and profile['service_tier'] == 'default'
    write('native-execution01.json', dict(context=context, process_id=native['ProcessId'], fast_mode_disabled=True,
        native_settings_verified=True, profile={k: profile.get(k) for k in ['id','model','thinking_level','service_tier','cli_args']}))
    paths = list((ROOT / 'Source').rglob('*'))
    paths += [ROOT / 'Binaries/Win64/UnrealEditor-MeridianSquad.dll']
    write('native-baseline01.json', [dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=digest(p)) for p in paths if p.is_file()])
    result = capacity()
    print(json.dumps(dict(native=context, preserved=len(preserved), project_bytes=result['project_bytes'])))


if __name__ == '__main__':
    if '--capacity' in sys.argv:
        result = capacity()
        print(json.dumps({k: result[k] for k in ['project_bytes', 'files', 'cap_bytes']}))
    else:
        main()
