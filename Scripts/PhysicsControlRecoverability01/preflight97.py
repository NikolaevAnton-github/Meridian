"""Preserve the dispatched baseline and verify the actual native execution."""
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlRecoverability01/Worker'
OUT.mkdir(parents=True, exist_ok=True)

def write(name, value):
    p = OUT / name
    assert not p.exists(), p
    p.write_text(json.dumps(value, indent=2), encoding='utf-8')

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

checks = []
for e in json.loads((OUT.parent / 'Controller/preservation-before.json').read_text(encoding='utf-8-sig')):
    p = Path(e['Path'])
    checks.append(dict(path=p.relative_to(ROOT).as_posix(), sha256=digest(p), expected=e['Hash'].lower()))
assert all(e['sha256'] == e['expected'] for e in checks)
write('preservation-before01.json', checks)

native = None
session = next((Path(os.environ['CODEX_HOME']) / 'sessions').rglob('*.jsonl'))
with session.open(encoding='utf-8') as f:
    for line in f:
        row = json.loads(line)
        if row.get('type') == 'turn_context':
            native = {k: row['payload'].get(k) for k in ['model', 'effort', 'service_tier', 'collaboration_mode']}
            break
process = json.loads((OUT.parent / 'Controller/native-processes.json').read_text(encoding='utf-8-sig'))
assert native['model'] == 'gpt-6-astra' and native['effort'] == 'max'
assert native['service_tier'] in [None, 'default', 'standard']
assert '--disable fast_mode' in process['CommandLine'] and 'service_tier=' in process['CommandLine']
write('native-execution01.json', dict(context=native, process_id=process['ProcessId'], native_arguments=process['CommandLine']))

paths = [*ROOT.glob('Source/MeridianSquad/PhysicsControl*'), *ROOT.glob('Source/MeridianSquad/CombatPrototypeHUD*'),
         *ROOT.glob('Source/MeridianSquad/CombatProjectileWorld*'), *ROOT.glob('Source/MeridianSquad/OpeningLobbyCharacter*'),
         ROOT / 'Binaries/Win64/UnrealEditor-MeridianSquad.dll',
         ROOT / 'Content/Development/PhysicsControlRecovery01/PA_Manny_Recovery01.uasset']
dest = OUT / 'Baseline01'
assert not dest.exists()
rows = []
for p in paths:
    if not p.is_file():
        continue
    rel = p.relative_to(ROOT)
    copy = dest / rel
    copy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(p, copy)
    rows.append(dict(path=rel.as_posix(), sha256=digest(p), bytes=p.stat().st_size))
(dest / 'manifest.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
write('writer-lease01.json', dict(issue='MSQ-97', holder='MeridianSquad Unreal', status='acquired',
    authorization='Controller OwnerStart01 dispatch; sole production/editor writer', editor_pid=18416))
print(json.dumps(dict(native=native, baseline_files=len(rows), preserved=len(checks))))
