"""Save exact candidate source/DLL identities without changing Git state."""
import hashlib
import json
import shutil
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlDummy01/Worker'

def capture(name):
    dest = OUT / name
    assert not dest.exists()
    files = [*ROOT.glob('Source/MeridianSquad/PhysicsControlDummy*'),
             *[ROOT / 'Source/MeridianSquad' / x for x in ['CombatProjectileWorld.h','CombatProjectileWorld.cpp','CombatRifleComponent.h','CombatRifleComponent.cpp','MeridianSquad.Build.cs']],
             ROOT / 'MeridianSquad.uproject', ROOT / 'Binaries/Win64/UnrealEditor-MeridianSquad.dll']
    rows=[]
    for p in files:
        target=dest/p.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,target)
        rows.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (dest/'manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    print(json.dumps(dict(candidate=name,files=len(rows))))

if __name__=='__main__': capture(sys.argv[1])
