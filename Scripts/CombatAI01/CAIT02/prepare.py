"""Preserve MSQ-119 inputs and verify the existing executor, without administration."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'Saved/CombatAI01/CAI-T02/Worker/Candidate01'
OUT.mkdir(parents=True, exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n, x):
    with (OUT/n).open('x', encoding='utf-8') as f: json.dump(x, f, indent=2)
def rows(paths): return [dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p)) for p in sorted(set(paths))]
profile = json.loads(subprocess.check_output(['multica','agent','get','d3ed0aae-f7e4-40d2-9568-9aa9b11fdf51','--output','json'], text=True))
native = json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',
    "Get-CimInstance Win32_Process -Filter 'ProcessId = 39708' | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json"], text=True))
args = native['CommandLine']
session = next((ROOT/'Saved/Multica/workspaces/meridiansqu-6f91832bf07d/msq-119-ded3be75ca14/codex-home/sessions').rglob('*.jsonl'))
contexts=[]
for line in session.read_text(encoding='utf-8').splitlines():
    r=json.loads(line)
    if r.get('type')=='turn_context':
        p=r['payload']; contexts.append(dict(model=p.get('model'), effort=p.get('effort'), service_tier=p.get('service_tier')))
checks=dict(configured=profile['model']=='gpt-6-astra' and profile['thinking_level']=='max' and profile['service_tier']=='default',
    native=native['Name']=='codex.exe' and 'gpt-6-astra' in args and 'model_reasoning_effort=\\\"max\\\"' in args,
    standard='service_tier=\\\"default\\\"' in args and '--disable fast_mode' in args,
    turn=bool(contexts) and contexts[-1]['model']=='gpt-6-astra' and contexts[-1]['effort']=='max')
write('execution-settings.json',dict(checks=checks,passed=all(checks.values()),pid=native['ProcessId'],contexts=contexts,
    captured_utc=datetime.now(timezone.utc).isoformat(),native_arguments_sha256=hashlib.sha256(args.encode()).hexdigest()))
assert all(checks.values()),checks
protected=[ROOT/p for p in ['AGENTS.md','Config/DefaultEngine.ini','MeridianSquad.uproject','Content/Maps/L_OpeningLobby_PainterStone01.umap',
    'Docs/ProjectState.md','Docs/Tasks/CombatAI01.md','Docs/Tasks/CombatAI01/CAI-T02.md','Docs/Approvals/CombatAI01-CoverFire01-OwnerStart01.json']]
write('owner-preservation-before.json',rows(protected))
history=[p for family in ['CAI-00','CAI-01','CAI-T01','CAI-02'] for p in (ROOT/'Saved/CombatAI01'/family/'Worker').rglob('*') if p.is_file()]
write('historical-preservation-before.json',rows(history))
write('source-before.json',rows(p for p in (ROOT/'Source/MeridianSquad').glob('*') if p.is_file()))
write('baseline.json',dict(head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    dll_sha256=sha(ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll'),
    prerequisite_manifest_sha256=sha(ROOT/'Saved/CombatAI01/CAI-02/Worker/Candidate03/candidate-manifest.json')))
print(json.dumps(dict(settings=checks,historical_files=len(history))))
