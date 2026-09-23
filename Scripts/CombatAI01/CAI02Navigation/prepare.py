"""One-time MSQ-104 navigation correction preservation/settings snapshot."""
from pathlib import Path
import hashlib
import json
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT/'Saved/CombatAI01/CAI-02/Worker/Candidate02'
PREVIOUS = OUT.parent/'Candidate01'
CONTROLLER = ROOT/'Saved/CombatAI01/CAI-02/Controller'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(name, data):
    with (OUT/name).open('x', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2)


OUT.mkdir(parents=True, exist_ok=True)
assert not (OUT/'execution-settings.json').exists(), 'Do not replace correction evidence'
profile = read(CONTROLLER/'agent-configured.json')
native = read(CONTROLLER/'native-process.json')
process = json.loads(subprocess.check_output(['powershell', '-NoProfile', '-Command',
    f"Get-CimInstance Win32_Process -Filter 'ProcessId = {native['pid']}' | Select-Object ProcessId,CommandLine | ConvertTo-Json"], text=True))
args = process['CommandLine']
contexts = []
for path in sorted({row['file'] for row in read(CONTROLLER/'all-native-turn-contexts.json')}):
    with Path(path).open(encoding='utf-8') as stream:
        for line in stream:
            row = json.loads(line)
            if row.get('type') == 'turn_context':
                payload = row['payload']
                contexts.append(dict(timestamp=row['timestamp'], model=payload.get('model'),
                    effort=payload.get('effort'), service_tier=payload.get('service_tier')))
contexts.sort(key=lambda row: row['timestamp'])
checks = dict(profile=profile['model']=='gpt-6-astra' and profile['thinking_level']=='max' and profile['service_tier']=='default',
    model='gpt-6-astra' in args, max_reasoning='model_reasoning_effort=\\\"max\\\"' in args,
    standard='service_tier=\\\"default\\\"' in args, fast_off='--disable fast_mode' in args,
    context=bool(contexts) and contexts[-1]['model']=='gpt-6-astra' and contexts[-1]['effort']=='max')
write('execution-settings.json', dict(checks=checks, passed=all(checks.values()), pid=process['ProcessId'],
    captured_utc=datetime.now(timezone.utc).isoformat(), contexts=contexts,
    native_arguments_sha256=hashlib.sha256(args.encode()).hexdigest(),
    note='Direct live native process and turn-context read; no profile changes. Null turn service tier is resolved by explicit native default and fast-disabled arguments.'))
assert all(checks.values()), checks

rows = [dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(path))
    for path in sorted(PREVIOUS.rglob('*')) if path.is_file()]
for name in ('Docs/CombatAI01-CAI02.md',):
    rows.append(dict(path=name, sha256=sha(ROOT/name)))
for path in sorted((ROOT/'Scripts/CombatAI01/CAI02').iterdir()):
    if path.suffix in ('.cpp', '.py'):
        rows.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(path)))
write('candidate01-preservation-before.json', rows)
write('historical-preservation-before.json', read(PREVIOUS/'historical-preservation-before.json'))
write('owner-preservation-before.json', read(PREVIOUS/'owner-preservation-before.json'))
write('baseline.json', dict(head=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
    prior_manifest_sha256=sha(PREVIOUS/'candidate-manifest.json'), prior_archive_sha256=sha(PREVIOUS/'CAI02-Candidate01-frozen.zip'),
    prior_dll_sha256=read(PREVIOUS/'freeze-result.json')['dll_sha256'],
    scope='Bounded existing home-region navigation correction after Candidate01 freeze; native/pure/source only.'))
print(json.dumps(dict(settings=checks, preserved_candidate01_files=len(rows)), indent=2))
