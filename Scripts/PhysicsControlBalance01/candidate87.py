"""Freeze native/asset evidence without altering Git or previous candidates."""
import hashlib
import json
import shutil
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'Saved/CombatSlice01/PhysicsControlBalance01/Worker'/sys.argv[1]
assert not DEST.exists()
paths=[*ROOT.glob('Source/MeridianSquad/PhysicsControl*'),
       ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll',
       *ROOT.glob('Content/Development/PhysicsControlBalance01/**/*.uasset'),
       *ROOT.glob('Scripts/PhysicsControlBalance01/*.py'),
       ROOT/'Scripts/PhysicsControlBalance01/cases87.json',
       ROOT/'Docs/PhysicsControlBalance01.md']
rows=[]
for p in paths:
    dest=DEST/p.relative_to(ROOT)
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(p,dest)
    rows.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(DEST/'manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(dict(candidate=sys.argv[1],files=len(rows))))
