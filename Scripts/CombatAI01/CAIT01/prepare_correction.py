"""Record correction-only preservation, native settings and initial Epic MCP state."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
OUT = ROOT / 'Saved/CombatAI01/CAI-T01/Worker/Candidate02'
CONTROLLER = ROOT / 'Saved/CombatAI01/CAI-T01/Controller'
OUT.mkdir(parents=True, exist_ok=True)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    with (OUT / name).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2)


preserved = []
for directory in ('Worker/Candidate01', 'Review'):
    for path in sorted((OUT.parents[1] / directory).rglob('*')):
        if path.is_file():
            preserved.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=digest(path)))
for path in [ROOT/'Docs/CombatAI01-Tactical01.md', ROOT/'Docs/CombatAI01-Tactical01Review.md']:
    preserved.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=digest(path)))
write('historical-preservation-before.json', preserved)
write('owner-preservation-baseline.json', json.loads((CONTROLLER/'preservation-before.json').read_text(encoding='utf-8-sig')))

profile = json.loads((CONTROLLER/'correction01-agent-configured.json').read_text(encoding='utf-8-sig'))
native = json.loads((CONTROLLER/'correction01-native-process.json').read_text(encoding='utf-8-sig'))
command = subprocess.run(['powershell', '-NoProfile', '-Command',
    f"Get-CimInstance Win32_Process -Filter 'ProcessId = {int(native['pid'])}' | Select-Object ProcessId, ParentProcessId, CommandLine | ConvertTo-Json"],
    capture_output=True, text=True, check=True)
process = json.loads(command.stdout)
args = process['CommandLine']
checks = dict(model='gpt-6-astra' in args, effort='model_reasoning_effort=\\\"max\\\"' in args,
    tier='service_tier=\\\"default\\\"' in args, fast_disabled='--disable fast_mode' in args,
    configured=profile['model']=='gpt-6-astra' and profile['thinking_level']=='max' and profile['service_tier']=='default')
contexts = []
session_root = ROOT/'Saved/Multica/workspaces/meridiansqu-6f91832bf07d/msq-118-1efcb0a368d6/codex-home/sessions'
for path in session_root.rglob('*.jsonl'):
    for line in path.read_text(encoding='utf-8').splitlines():
        row = json.loads(line)
        if row.get('type') == 'turn_context':
            p = row['payload']
            contexts.append(dict(timestamp=row.get('timestamp'), model=p.get('model'), effort=p.get('effort')))
contexts.sort(key=lambda c: c['timestamp'])
checks['native_context'] = bool(contexts) and contexts[-1]['model']=='gpt-6-astra' and contexts[-1]['effort']=='max'
write('execution-settings.json', dict(profile=dict(model=profile['model'], effort=profile['thinking_level'], tier=profile['service_tier']),
    native_pid=process['ProcessId'], native_settings=native['settings'], context=contexts[-1:] ,checks=checks, passed=all(checks.values()),
    note='One-time snapshot; no mutable controller monitor included. Actual command line checked without storing credentials or full arguments.'))
assert all(checks.values()), checks

from Scripts import check_unreal_mcp as probe
probe.OUTPUT = OUT/'InitialEpicProbe'
try:
    probe.check()
    connection = dict(connected=True)
except Exception as error:
    connection = dict(connected=False, error=str(error))
processes = subprocess.run(['powershell', '-NoProfile', '-Command',
    "@(Get-CimInstance Win32_Process -Filter \"Name = 'UnrealEditor.exe'\" | Select-Object ProcessId, ExecutablePath, CommandLine) | ConvertTo-Json"],
    capture_output=True, text=True, check=True)
connection['editor_processes'] = json.loads(processes.stdout) if processes.stdout.strip() else []
write('editor-initial-availability.json', connection)
print(json.dumps(dict(preservation_files=len(preserved), settings=checks, editor=connection), indent=2))
