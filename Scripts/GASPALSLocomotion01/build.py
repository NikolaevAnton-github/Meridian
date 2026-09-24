"""One guarded native Development Editor build, with bounded file logs."""
from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/GASPALSLocomotion01/Worker'
label=sys.argv[1]
guard=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',
    "$active=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'UnrealEditor*' -or $_.Name -eq 'UnrealBuildTool.exe' -or ($_.Name -eq 'dotnet.exe' -and $_.CommandLine -like '*UnrealBuildTool*') -or $_.Name -in @('cl.exe','MSBuild.exe','blender.exe') } | Select-Object ProcessId,Name); [pscustomobject]@{active=$active; free_physical_kib=(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory} | ConvertTo-Json -Depth 4"],text=True))
assert not guard['active'],guard
args=['D:/UE_5.8/Engine/Build/BatchFiles/Build.bat','MeridianSquadEditor','Win64','Development',str(ROOT/'MeridianSquad.uproject'),'-WaitMutex','-NoHotReloadFromIDE','-MaxParallelActions=4']
started=time.monotonic()
with (OUT/('build-'+label+'.log')).open('xb') as log:
    result=subprocess.run(args,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
record=dict(args=args,guard=guard,exit_code=result.returncode,seconds=time.monotonic()-started,
            ended_utc=datetime.now(timezone.utc).isoformat())
(OUT/('build-'+label+'.json')).write_text(json.dumps(record,indent=2))
print(json.dumps(record))
sys.exit(result.returncode)
