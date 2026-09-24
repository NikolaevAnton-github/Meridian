"""Capture MSQ-120 inputs/settings; no profile or issue administration."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, zipfile
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'Saved/CombatAI01/CAI-T03/Worker/Candidate01'
OUT.mkdir(parents=True,exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):
    with (OUT/n).open('x',encoding='utf-8') as f: json.dump(v,f,indent=2)
def rows(ps): return [dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(set(ps))]
profile=json.loads(subprocess.check_output(['multica','agent','get','d3ed0aae-f7e4-40d2-9568-9aa9b11fdf51','--output','json'],text=True,encoding='utf-8'))
native=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process -Filter 'ProcessId=30416' | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json"],text=True))
args=native['CommandLine']
sessions=ROOT/'Saved/Multica/workspaces/meridiansqu-6f91832bf07d/msq-120-282f0ff3c188/codex-home/sessions'
contexts=[]
for p in sessions.rglob('*.jsonl'):
    for line in p.read_text(encoding='utf-8').splitlines():
        r=json.loads(line)
        if r.get('type')=='turn_context': contexts.append({k:r['payload'].get(k) for k in ('model','effort','service_tier')})
checks=dict(configured=profile['model']=='gpt-6-astra' and profile['thinking_level']=='max' and profile['service_tier']=='default',
    native='gpt-6-astra' in args and 'model_reasoning_effort=\\\"max\\\"' in args,
    standard='service_tier=\\\"default\\\"' in args and '--disable fast_mode' in args,
    turn=bool(contexts) and contexts[-1]['model']=='gpt-6-astra' and contexts[-1]['effort']=='max')
write('execution-settings.json',dict(checks=checks,passed=all(checks.values()),native=native,contexts=contexts,
    configured={k:profile[k] for k in ('model','thinking_level','service_tier','custom_args')},captured_utc=datetime.now(timezone.utc).isoformat()))
assert all(checks.values()),checks
protected=[ROOT/p for p in ('AGENTS.md','Config/DefaultEngine.ini','MeridianSquad.uproject','Content/Maps/L_OpeningLobby_PainterStone01.umap','Docs/ProjectState.md','Docs/Tasks/CombatAI01.md','Docs/Tasks/CombatAI01/CAI-T03.md','Docs/Approvals/CombatAI01-MobileLean01-OwnerStart01.json')]
write('owner-preservation-before.json',rows(protected))
history=[p for family in ('CAI-00','CAI-01','CAI-T01','CAI-02','CAI-T02') for p in (ROOT/'Saved/CombatAI01'/family/'Worker').rglob('*') if p.is_file()]
write('historical-preservation-before.json',rows(history))
source=[p for p in (ROOT/'Source/MeridianSquad').glob('*') if p.is_file()]
assets=[p for folder in ('Plugins/GASPEnemyFoundation01/Content/Blueprints','Plugins/GASPALSEnemy01/Content') for p in (ROOT/folder).rglob('*.uasset')]
write('source-before.json',rows(source)); write('assets-before.json',rows(assets))
with zipfile.ZipFile(OUT/'preserved-inputs.zip','x',zipfile.ZIP_DEFLATED) as z:
    for p in source+assets+protected: z.write(p,p.relative_to(ROOT).as_posix())
write('baseline.json',dict(head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),dll_sha256=sha(ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll'),
    prerequisite_manifest_sha256=sha(ROOT/'Saved/CombatAI01/CAI-T02/Worker/Candidate02/candidate-manifest.json')))
print(json.dumps(dict(settings=checks,source=len(source),assets=len(assets),historical_files=len(history))))
