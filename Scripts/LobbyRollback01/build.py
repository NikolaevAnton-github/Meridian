"""One foreground full Development Editor build; no hot reload/live coding."""
import json
import subprocess
import sys
import time
from audit import ROOT, OUT, sha, write

name = sys.argv[1]
assert name.replace('-', '').isalnum()
log = OUT / (name + '.log')
assert not log.exists()
args = ['D:/UE_5.8/Engine/Build/BatchFiles/Build.bat', 'MeridianSquadEditor', 'Win64', 'Development',
        str(ROOT / 'MeridianSquad.uproject'), '-WaitMutex', '-NoHotReloadFromIDE', '-NoLiveCoding', '-MaxParallelActions=2']
started = time.time()
with log.open('x', encoding='utf-8') as stream:
    result = subprocess.run(args, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
files = [p for p in (ROOT / 'Source/MeridianSquad').glob('*') if p.is_file()]
files.append(ROOT / 'Binaries/Win64/UnrealEditor-MeridianSquad.dll')
record = dict(command=args, exit_code=result.returncode, elapsed=time.time() - started,
              files={p.relative_to(ROOT).as_posix(): sha(p) for p in files if p.exists()})
write(name + '.json', record)
print(json.dumps({k:v for k,v in record.items() if k != 'files'}))
print('DLL SHA-256: ' + record['files'].get('Binaries/Win64/UnrealEditor-MeridianSquad.dll', 'missing'))
sys.exit(result.returncode)
