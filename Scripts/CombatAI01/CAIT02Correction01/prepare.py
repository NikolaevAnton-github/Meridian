"""Capture bounded correction inputs without modifying Candidate01 or review evidence."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'Saved/CombatAI01/CAI-T02/Worker/Candidate02'
OUT.mkdir(parents=True, exist_ok=True)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name, value):
    with (OUT / name).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2)
def rows(paths):
    return [dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(set(paths))]

controller = ROOT / 'Saved/CombatAI01/CAI-T02/Controller'
profile_path = controller / 'correction01-agent-configured.json'
profile = json.loads(profile_path.read_text(encoding='utf-8-sig'))
process = json.loads(subprocess.check_output(['powershell', '-NoProfile', '-Command',
    "Get-CimInstance Win32_Process -Filter 'ProcessId=37948' | Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json"], text=True))
session_root = ROOT / 'Saved/Multica/workspaces/meridiansqu-6f91832bf07d/msq-119-3a6b73dde3f8/codex-home/sessions'
session = next(session_root.rglob('*01a0d0c6-65dd-75a1-bd74-7a6b7d87879a.jsonl'))
contexts = []
for line in session.read_text(encoding='utf-8').splitlines():
    entry = json.loads(line)
    if entry.get('type') == 'turn_context':
        p = entry['payload']
        contexts.append(dict(timestamp=entry['timestamp'], model=p.get('model'), effort=p.get('effort'), service_tier=p.get('service_tier')))
args = process['CommandLine']
settings = dict(configured=profile['model']=='gpt-6-astra' and profile['thinking_level']=='max' and profile['service_tier']=='default',
    native=process['Name']=='codex.exe' and 'gpt-6-astra' in args and 'model_reasoning_effort=\\\"max\\\"' in args,
    standard='service_tier=\\\"default\\\"' in args and '--disable fast_mode' in args,
    turn=bool(contexts) and contexts[-1]['model']=='gpt-6-astra' and contexts[-1]['effort']=='max')
write('execution-settings.json', dict(captured_utc=datetime.now(timezone.utc).isoformat(), profile_source=profile_path.relative_to(ROOT).as_posix(),
    configured={k:profile[k] for k in ('model','thinking_level','service_tier')}, native_process=process, turn_contexts=contexts,
    checks=settings, passed=all(settings.values()), note='Turn context tier is null; native arguments explicitly select default and disable fast mode. No profile changed.'))
assert all(settings.values()), settings
source = rows(p for p in (ROOT/'Source/MeridianSquad').iterdir() if p.is_file())
write('source-before.json', source)
protected = [ROOT/p for p in ('Config/DefaultEngine.ini','MeridianSquad.uproject','Content/Maps/L_OpeningLobby_PainterStone01.umap',
    'Docs/CombatAI01-CoverFire01.md','Docs/CombatAI01-CoverFire01Review.md')]
write('owner-preservation-before.json', rows(protected))
history = [p for family in ('CAI-00','CAI-01','CAI-T01','CAI-02') for p in (ROOT/'Saved/CombatAI01'/family/'Worker').rglob('*') if p.is_file()]
history += [p for directory in (ROOT/'Saved/CombatAI01/CAI-T02/Worker/Candidate01', ROOT/'Saved/CombatAI01/CAI-T02/Review', ROOT/'Scripts/CombatAI01/CAIT02') for p in directory.rglob('*') if p.is_file()]
write('historical-preservation-before.json', rows(history))
candidate = ROOT/'Saved/CombatAI01/CAI-T02/Worker/Candidate01/candidate-manifest.json'
manifest = json.loads(candidate.read_text(encoding='utf-8-sig'))
mismatches = [r['path'] for r in manifest['files'] if sha(ROOT/r['path']) != r['sha256']]
write('baseline.json', dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    candidate01_manifest_sha256=sha(candidate), candidate01_entries=len(manifest['files']), mismatches=mismatches,
    dll_sha256=sha(ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll')))
assert not mismatches, mismatches
print(json.dumps(dict(settings=settings, candidate01_entries=len(manifest['files']), history_files=len(history))))
