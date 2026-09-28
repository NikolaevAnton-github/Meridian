"""Full production build with source and module identities, saved outside Git."""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'Saved/DestructionScaling01'
name = sys.argv[1]
assert not (OUT/(name+'.json')).exists()
assert subprocess.check_output(['powershell','-NoProfile','-Command',
    '@(Get-Process UnrealEditor -ErrorAction SilentlyContinue).Count'],text=True).strip() == '0'
command = ['D:/UE_5.8/Engine/Build/BatchFiles/Build.bat','MeridianSquadEditor','Win64','Development',
    str(ROOT/'MeridianSquad.uproject'),'-WaitMutex','-NoHotReloadFromIDE','-NoLiveCoding','-MaxParallelActions=2']
started=time.monotonic()
with (OUT/(name+'.log')).open('w') as log:
    result=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
files = sorted((ROOT/'Source/MeridianSquad').glob('*.h'))+sorted((ROOT/'Source/MeridianSquad').glob('*.cpp'))
files.append(ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll')
report=dict(command=command,exit_code=result.returncode,seconds=time.monotonic()-started,
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.exists()})
(OUT/(name+'.json')).write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='hashes'}))
raise SystemExit(result.returncode)
