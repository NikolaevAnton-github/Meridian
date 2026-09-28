"""Synchronous editor build with exact candidate hashes; editor must be closed."""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/LobbyColumnsPerf02'
name = sys.argv[1]
assert not (OUT / (name + '.json')).exists()
live = subprocess.check_output(['powershell', '-NoProfile', '-Command',
    "@(Get-Process UnrealEditor -ErrorAction SilentlyContinue).Count"], text=True).strip()
assert live == '0', 'Close Unreal Editor before a full build'
paths = ['Source/MeridianSquad/' + p for p in ['DemoColumnCladding.cpp', 'DemoColumnCladding.h',
         'LobbyFacingPool.cpp', 'LobbyFacingPool.h', 'CombatProjectileWorld.cpp', 'CombatProjectileWorld.h']]
command = ['D:/UE_5.8/Engine/Build/BatchFiles/Build.bat', 'MeridianSquadEditor', 'Win64',
           'Development', str(ROOT / 'MeridianSquad.uproject'), '-WaitMutex',
           '-NoHotReloadFromIDE', '-NoLiveCoding', '-MaxParallelActions=2']
start = time.monotonic()
with (OUT / (name + '.log')).open('w') as log:
    result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
report = dict(command=command, exit_code=result.returncode, elapsed_seconds=time.monotonic()-start,
              hashes={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
                      for p in paths + ['Binaries/Win64/UnrealEditor-MeridianSquad.dll']})
(OUT / (name + '.json')).write_text(json.dumps(report, indent=2))
print(json.dumps(dict(build=name, exit_code=result.returncode, seconds=report['elapsed_seconds'])))
raise SystemExit(result.returncode)
