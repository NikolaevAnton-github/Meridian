"""Leave the matching ordinary editor available; no Play or asset writes."""
from pathlib import Path
from datetime import datetime, timezone
import json, subprocess, hashlib
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'Saved/CombatAI01/CAI-T03/Worker/Candidate01'
guard=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',"$rows=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'UnrealEditor*' -or $_.Name -in @('cl.exe','UnrealBuildTool.exe','blender.exe') } | Select-Object ProcessId,Name); ConvertTo-Json -InputObject $rows"],text=True))
assert not guard,guard
args=['D:/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe',str(ROOT/'MeridianSquad.uproject'),
      '-abslog='+str(OUT/'editor.log'),'-ExecCmds=py D:/devgames/MeridianSquad/Scripts/CombatAI01/CAIT03/bootstrap.py']
# A breakaway process is not owned by this task's process job. Retain its PID and
# ordinary editor log so the controller can inspect the handoff after this turn.
proc=subprocess.Popen(args,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS | subprocess.CREATE_BREAKAWAY_FROM_JOB)
with (OUT/'editor-process.json').open('x',encoding='utf-8') as f:
    json.dump(dict(pid=proc.pid,arguments=args,started_utc=datetime.now(timezone.utc).isoformat(),
        breakaway=True,stop='Close this ordinary editor normally; preserve any later owner edits.',
        dll_sha256=hashlib.sha256((ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll').read_bytes()).hexdigest()),f,indent=2)
print(json.dumps(dict(pid=proc.pid,breakaway=True)))
