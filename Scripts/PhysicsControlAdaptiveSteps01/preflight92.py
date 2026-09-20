"""Verify the dispatched immutable baseline, preserved files and native worker."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlAdaptiveSteps01/Worker'
OUT.mkdir(parents=True, exist_ok=True)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(name, data):
    path = OUT / name
    assert not path.exists(), path
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')

preserved = []
for item in json.loads((OUT.parent / 'Controller/preservation-before.json').read_text(encoding='utf-8-sig')):
    path = Path(item['Path'])
    preserved.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=digest(path), expected=item['Hash'].lower()))
assert all(p['sha256'] == p['expected'] for p in preserved)
write('preservation-before01.json', preserved)
baseline = ROOT / 'Saved/CombatSlice01/PhysicsControlRecoverability01/Worker/Candidate07'
rows = []
for item in json.loads((baseline / 'manifest.json').read_text()):
    if item['path'].startswith(('Source/', 'Binaries/', 'Content/')):
        rows.append(dict(**item, current=digest(ROOT / item['path']), frozen=digest(baseline / item['path'])))
assert all(p['sha256'] == p['current'] == p['frozen'] for p in rows)
write('baseline-identity01.json', dict(commit='5cd5b67', manifest_sha256=digest(baseline / 'manifest.json'), files=rows))
session = next((Path(os.environ['CODEX_HOME']) / 'sessions').rglob('*.jsonl'))
context = None
with session.open(encoding='utf-8') as stream:
    for line in stream:
        item = json.loads(line)
        if item.get('type') == 'turn_context':
            context = {k: item['payload'].get(k) for k in ['model', 'effort', 'service_tier']}
            break
assert context['model'] == 'gpt-6-astra' and context['effort'] == 'max', context
assert context['service_tier'] in [None, 'default', 'standard'], context
processes = json.loads(subprocess.check_output(['powershell', '-NoProfile', '-Command',
    'Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Compress'], encoding='utf-8'))
by_id = {p['ProcessId']: p for p in processes}
native = by_id[os.getpid()]
while native['Name'] != 'codex.exe':
    native = by_id[native['ParentProcessId']]
command = native['CommandLine']
assert '--disable fast_mode' in command
assert 'max' in command and 'default' in command and 'gpt-6-astra' in command
settings = dict(model='gpt-6-astra', reasoning='max', service_tier='default')
profile = next(p for p in json.loads((OUT.parent / 'Controller/agents-before.json').read_text(encoding='utf-8-sig')) if p['id'] == 'd3ed0aae-f7e4-40d2-9568-9aa9b11fdf51')
assert profile['model'] == 'gpt-6-astra' and profile['thinking_level'] == 'max' and profile['service_tier'] == 'default'
write('native-execution01.json', dict(context=context, process_id=native['ProcessId'], settings=settings, fast_mode_disabled=True,
    profile={k: profile[k] for k in ['id','model','thinking_level','service_tier','cli_args']} if 'cli_args' in profile else
    {k: profile[k] for k in ['id','model','thinking_level','service_tier']}))
write('writer-lease01.json', dict(issue='MSQ-92', holder='MeridianSquad Unreal', status='acquired',
    editor_pid=45548, authority='Controller OwnerStart01 sole production/editor writer dispatch'))
print(json.dumps(dict(native=context, baseline_files=len(rows), preserved=len(preserved))))
