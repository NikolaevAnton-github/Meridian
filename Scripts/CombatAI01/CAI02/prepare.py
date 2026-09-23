"""One-time MSQ-104 preservation and actual native settings snapshot."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'Saved/CombatAI01/CAI-02/Worker/Candidate01'
C=ROOT/'Saved/CombatAI01/CAI-02/Controller'
OUT.mkdir(parents=True,exist_ok=True)
def write(name,data):
    with (OUT/name).open('x',encoding='utf-8') as f: json.dump(data,f,indent=2)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
profile=json.loads((C/'agent-configured.json').read_text(encoding='utf-8-sig'))
native=json.loads((C/'native-process.json').read_text(encoding='utf-8-sig'))
cmd=subprocess.check_output(['powershell','-NoProfile','-Command',
    f"Get-CimInstance Win32_Process -Filter 'ProcessId = {native['pid']}' | Select-Object ProcessId,CommandLine | ConvertTo-Json"],text=True)
process=json.loads(cmd)
args=process['CommandLine']
contexts=json.loads((C/'all-native-turn-contexts.json').read_text(encoding='utf-8-sig'))
checks=dict(profile=profile['model']=='gpt-6-astra' and profile['thinking_level']=='max' and profile['service_tier']=='default',
    model='gpt-6-astra' in args, max_reasoning='model_reasoning_effort=\\\"max\\\"' in args,
    standard='service_tier=\\\"default\\\"' in args, fast_off='--disable fast_mode' in args,
    context=bool(contexts) and contexts[-1]['model']=='gpt-6-astra' and contexts[-1]['effort']=='max')
write('execution-settings.json',dict(checks=checks,passed=all(checks.values()),pid=process['ProcessId'],
    contexts=contexts, note='Snapshot only; mutable controller monitor files are excluded from the frozen candidate.'))
assert all(checks.values()),checks
write('owner-preservation-before.json',json.loads((C/'preservation-before.json').read_text(encoding='utf-8-sig')))
rows=[]
for folder in ('CAI-00/Worker','CAI-01/Worker','CAI-T01/Worker','CAI-T01/Review'):
    for p in sorted((ROOT/'Saved/CombatAI01'/folder).rglob('*')):
        if p.is_file(): rows.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
write('historical-preservation-before.json',rows)
write('baseline.json',dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    verification='Native build, affected pure/source integration fixtures and read-only editor; no gameplay.'))
print(json.dumps(dict(settings=checks,historical_files=len(rows))))
