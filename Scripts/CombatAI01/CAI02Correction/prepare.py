"""Capture the correction baseline without changing previous candidate evidence."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'Saved/CombatAI01/CAI-02/Worker/Candidate03'
BASE = OUT.parent / 'Candidate02'
CONTROLLER = OUT.parents[1] / 'Controller'
OUT.mkdir(parents=True, exist_ok=True)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(name, data):
    with (OUT / name).open('x', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2)

assert not (OUT / 'baseline.json').exists(), 'Preserve the original correction baseline'
profile = read(CONTROLLER / 'correction01-agent-configured.json')
# This exact native PID was identified through this run's shell ancestry.
process = json.loads(subprocess.check_output(['powershell', '-NoProfile', '-Command',
    "Get-CimInstance Win32_Process -Filter 'ProcessId = 39784' | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json"], text=True))
args = process['CommandLine']
session = ROOT / 'Saved/Multica/workspaces/meridiansqu-6f91832bf07d/msq-104-21454b5f8f91/codex-home/sessions/2026/09/24/rollout-2026-09-24T01-12-29-01a0d053-d39d-76a0-b842-98945890d53b.jsonl'
contexts = []
for line in session.read_text(encoding='utf-8').splitlines():
    row = json.loads(line)
    if row.get('type') == 'turn_context':
        p = row['payload']
        contexts.append(dict(timestamp=row['timestamp'], model=p.get('model'), effort=p.get('effort'), service_tier=p.get('service_tier')))
checks = dict(profile=profile['model'] == 'gpt-6-astra' and profile['thinking_level'] == 'max' and profile['service_tier'] == 'default',
    native_process=process['Name'] == 'codex.exe', model='gpt-6-astra' in args,
    max_reasoning='model_reasoning_effort=\\\"max\\\"' in args,
    standard='service_tier=\\\"default\\\"' in args, fast_off='--disable fast_mode' in args,
    context=bool(contexts) and contexts[-1]['model'] == 'gpt-6-astra' and contexts[-1]['effort'] == 'max')
write('execution-settings.json', dict(checks=checks, passed=all(checks.values()), pid=process['ProcessId'],
    captured_utc=datetime.now(timezone.utc).isoformat(), contexts=contexts,
    native_arguments_sha256=hashlib.sha256(args.encode()).hexdigest(),
    note='Actual process and local turn context. Explicit native default and fast-disabled arguments resolve a null context tier. No profile changes.'))
assert all(checks.values()), checks
prior = read(BASE / 'candidate-manifest.json')
assert all(sha(ROOT / r['path']) == r['sha256'] for r in prior['files']), 'Candidate02 drift before correction'
folders = [OUT.parent / n for n in ('Candidate01', 'Candidate02')]
folders += [OUT.parents[1] / 'Review', ROOT / 'Scripts/CombatAI01/CAI02', ROOT / 'Scripts/CombatAI01/CAI02Navigation']
paths = {p for folder in folders for p in folder.rglob('*') if p.is_file()}
paths |= {ROOT / ('Docs/' + n) for n in ('CombatAI01-CAI02.md', 'CombatAI01-CAI02Navigation01.md', 'CombatAI01-CAI02Review.md')}
write('previous-preservation-before.json', [dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p)) for p in sorted(paths)])
write('historical-preservation-before.json', read(BASE / 'historical-preservation-before.json'))
protected = [ROOT / r['path'] for r in read(BASE / 'owner-preservation-before.json')]
protected += [ROOT / n for n in ('AGENTS.md', 'Docs/ProjectState.md', 'Docs/Tasks/CombatAI01.md', 'Docs/Tasks/CombatAI01/CAI-02.md', 'Docs/CombatAI01-CAI02Acceptance.md', 'Docs/Approvals/CombatAI01-CAI02-OwnerStart01.json')]
write('owner-preservation-before.json', [dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p)) for p in sorted(set(protected))])
write('source-before.json', [dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p)) for p in sorted((ROOT / 'Source/MeridianSquad').glob('*')) if p.is_file()])
write('baseline.json', dict(head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    prior_manifest_sha256=sha(BASE / 'candidate-manifest.json'), prior_archive_sha256=sha(BASE / 'CAI02-Candidate02-frozen.zip'),
    prior_dll_sha256=sha(ROOT / 'Binaries/Win64/UnrealEditor-MeridianSquad.dll'),
    scope='CAI02-R1/R2 and directly affected transitions only; build/pure/source, owner-only gameplay.'))
print(json.dumps(dict(settings=checks, prior_candidate_matches=True, previous_files=len(paths)), indent=2))
