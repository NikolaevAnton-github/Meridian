"""Record effective runtime settings without copying session content or credentials."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT/'Saved/ReinforcedColumn01/Candidate01'
config_path = ROOT/'Saved/ContextBudget02/runs/01a0d970-05c3-7590-9f6d-c2785f0dccd3/native-config.json'
config = json.loads(config_path.read_text())
session_root = ROOT/'Saved/Multica/workspaces/meridiansqu-6f91832bf07d/msq-154-c2785f0dccd3/codex-home/sessions'
contexts = []
for path in session_root.rglob('*.jsonl'):
    for line in path.open(encoding='utf-8'):
        if '"turn_context"' not in line[:150]:
            continue
        record = json.loads(line)
        if record.get('type') == 'turn_context':
            contexts.append({k:record['payload'].get(k) for k in ['model','effort','service_tier','cwd']})
raw = subprocess.check_output(['powershell','-NoProfile','-Command',
    "Get-CimInstance Win32_Process -Filter \"Name = 'codex.exe'\" | Select-Object ProcessId,CommandLine | ConvertTo-Json"], text=True)
native = []
for row in json.loads(raw):
    command = row['CommandLine'] or ''
    if 'model_reasoning_effort' not in command:
        continue
    normalized = command.replace('\\', '').replace('"', '')
    native.append(dict(pid=row['ProcessId'], model=re.search(r'model=([^ ]+)',normalized).group(1),
                       effort=re.search(r'model_reasoning_effort=([^ ]+)',normalized).group(1),
                       tier=re.search(r'service_tier=([^ ]+)',normalized).group(1),
                       fast_disabled='--disable fast_mode' in normalized))
assert config['model_reasoning_effort']=='max' and config['service_tier']=='default'
assert contexts and all(c['model']=='gpt-6-astra' and c['effort']=='max' for c in contexts)
assert native and all(n['model']=='gpt-6-astra' and n['effort']=='max' and n['tier']=='default' and n['fast_disabled'] for n in native)
record = dict(config_path=str(config_path.relative_to(ROOT)),config_sha256=hashlib.sha256(config_path.read_bytes()).hexdigest(),
              configured={k:config[k] for k in ['role','model_reasoning_effort','service_tier']}, actual_contexts=contexts,native_arguments=native)
path=OUT/'native-settings.json'
assert not path.exists()
path.write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record))
