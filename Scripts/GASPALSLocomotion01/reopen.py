"""Open the ordinary retained-lobby editor with task tools; never launches Play."""
from pathlib import Path
from datetime import datetime, timezone
import json, subprocess, sys, hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/GASPALSLocomotion01/Worker'
label=sys.argv[1]
guard=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',
    "$rows=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'UnrealEditor*' -or $_.Name -in @('cl.exe','UnrealBuildTool.exe','blender.exe') } | Select-Object ProcessId,Name); ConvertTo-Json -InputObject $rows"],text=True))
assert not guard,guard
args=['D:/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe',str(ROOT/'MeridianSquad.uproject'),
      '/Game/Maps/L_OpeningLobby_PainterStone01','-abslog='+str(OUT/('editor-'+label+'.log')),
      '-ExecCmds=py D:/devgames/MeridianSquad/Scripts/GASPALSLocomotion01/bootstrap.py']
proc=subprocess.Popen(args,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.DETACHED_PROCESS|subprocess.CREATE_BREAKAWAY_FROM_JOB)
with (OUT/('editor-process-'+label+'.json')).open('x') as f:
    json.dump(dict(pid=proc.pid,args=args,started_utc=datetime.now(timezone.utc).isoformat(),
        dll_sha256=hashlib.sha256((ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll').read_bytes()).hexdigest()),f,indent=2)
print(json.dumps(dict(pid=proc.pid)))
