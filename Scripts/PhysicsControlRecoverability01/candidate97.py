"""Freeze task source, build and tooling without modifying any prior candidate."""
import hashlib
import json
import shutil
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/CombatSlice01/PhysicsControlRecoverability01/Worker'
dest=OUT/sys.argv[1]
assert not dest.exists(),dest
paths=[*ROOT.glob('Source/MeridianSquad/PhysicsControl*'),*ROOT.glob('Source/MeridianSquad/DummyRecovery*'),
       *ROOT.glob('Source/MeridianSquad/CombatRifle*'),*ROOT.glob('Source/MeridianSquad/CombatProjectileWorld*'),
       *ROOT.glob('Source/MeridianSquad/CombatPrototypeHUD*'),
       ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll',ROOT/'Content/Development/PhysicsControlRecovery01/PA_Manny_Recovery01.uasset',
       *ROOT.glob('Scripts/PhysicsControlRecoverability01/*.py'),*ROOT.glob('Scripts/PhysicsControlRecoverability01/*.json'),
       ROOT/'Docs/PhysicsControlRecoverability01.md']
rows=[]
for path in paths:
    if not path.is_file():continue
    copy=dest/path.relative_to(ROOT);copy.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,copy)
    rows.append(dict(path=path.relative_to(ROOT).as_posix(),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
(dest/'manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(dict(candidate=sys.argv[1],files=len(rows))))
