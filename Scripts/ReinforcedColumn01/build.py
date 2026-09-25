"""One foreground Development Editor build with immutable task evidence."""
import hashlib
import json
import subprocess
import sys
import time
import argparse
from pathlib import Path

ROOT = Path('D:/devgames/MeridianSquad')
parser = argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('--evidence-root', default='Saved/ReinforcedColumn01/Candidate01')
options = parser.parse_args()
OUT = ROOT / options.evidence_root
OUT.mkdir(parents=True, exist_ok=True)
name = options.name
assert name.replace('-', '').isalnum()
log = OUT / (name + '.log')
assert not log.exists()
args = ['D:/UE_5.8/Engine/Build/BatchFiles/Build.bat', 'MeridianSquadEditor', 'Win64', 'Development',
        str(ROOT/'MeridianSquad.uproject'), '-WaitMutex', '-NoHotReloadFromIDE', '-NoLiveCoding', '-MaxParallelActions=2']
started = time.time()
with log.open('w', encoding='utf-8') as stream:
    result = subprocess.run(args, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
files = [ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll']
files += [p for p in (ROOT/'Source/MeridianSquad').glob('*') if p.name in ['CombatRifleComponent.h','CombatRifleComponent.cpp','CombatProjectileWorld.cpp','NGDPropComponent.h','NGDPropComponent.cpp','CombatTimingProbes.cpp','NGDColumnAuthoring.h','NGDColumnAuthoring.cpp','MeridianSquad.Build.cs']]
record = dict(command=args, exit_code=result.returncode, elapsed=time.time()-started,
              files={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
log.with_suffix('.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
print(json.dumps(record))
sys.exit(result.returncode)
