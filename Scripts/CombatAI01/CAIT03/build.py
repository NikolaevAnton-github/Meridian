"""Guard and collect one foreground Development Editor build; never launch gameplay."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'Saved/CombatAI01/CAI-T03/Worker/Candidate01'
tag=1
while (OUT/f'build-guard{tag:02}.json').exists(): tag+=1
state=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',
    "$active = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'UnrealEditor*' -or $_.Name -eq 'UnrealBuildTool.exe' -or ($_.Name -eq 'dotnet.exe' -and $_.CommandLine -like '*UnrealBuildTool*') -or $_.Name -in @('cl.exe','MSBuild.exe','blender.exe') } | Select-Object ProcessId,Name); [pscustomobject]@{ captured_utc=[DateTime]::UtcNow.ToString('o'); active=$active; free_physical_kib=(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory } | ConvertTo-Json -Depth 4"],text=True))
with (OUT/f'build-guard{tag:02}.json').open('x',encoding='utf-8') as stream: json.dump(state,stream,indent=2)
assert not state['active'], 'Preserve any newly active owner editor/workload; no lifecycle changes are authorized here'
args=['D:/UE_5.8/Engine/Build/BatchFiles/Build.bat','MeridianSquadEditor','Win64','Development',
      str(ROOT/'MeridianSquad.uproject'),'-WaitMutex','-NoHotReloadFromIDE','-NoLiveCoding','-MaxParallelActions=2',
      '-Log='+str(OUT/f'build{tag:02}.log')]
started=datetime.now(timezone.utc).isoformat()
result=subprocess.run(args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
with (OUT/f'build-stdout{tag:02}.log').open('xb') as stream: stream.write(result.stdout)
dll=ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll'
report=dict(started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),exit_code=result.returncode,
    mode='Development Editor',arguments=args,no_editor_at_start=True,
    dll_sha256=hashlib.sha256(dll.read_bytes()).hexdigest())
with (OUT/f'build-result{tag:02}.json').open('x',encoding='utf-8') as stream: json.dump(report,stream,indent=2)
print(json.dumps(report,indent=2))
print(result.stdout.decode('utf-8',errors='replace')[-4500:])
raise SystemExit(result.returncode)
