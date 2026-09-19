"""Immutable task candidate, no Git mutation or asset copies."""
import hashlib
import json
import shutil
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlVariants01/Worker'

def capture(name):
    dest=OUT/name
    assert not dest.exists()
    paths=[*ROOT.glob('Source/MeridianSquad/PhysicsControlDummy*'),
           *[ROOT/'Source/MeridianSquad'/s for s in ['CombatProjectileWorld.h','CombatProjectileWorld.cpp','CombatRifleComponent.h','CombatRifleComponent.cpp','CombatTimingProbes.cpp','CombatPrototypeHUD.cpp']],
           ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll']
    rows=[]
    for p in paths:
        target=dest/p.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,target)
        rows.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (dest/'manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    print(json.dumps(dict(candidate=name,files=len(rows))))

if __name__=='__main__': capture(sys.argv[1])
