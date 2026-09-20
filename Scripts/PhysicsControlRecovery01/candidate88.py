"""Freeze task-scoped candidates without changing older records or Git state."""
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'Saved/CombatSlice01/PhysicsControlRecovery01/Worker' / sys.argv[1]
assert not DEST.exists()
paths = [*ROOT.glob('Source/MeridianSquad/PhysicsControl*'),
         *ROOT.glob('Source/MeridianSquad/DummyRecovery*'),
         ROOT / 'Source/MeridianSquad/MeridianSquad.Build.cs',
         ROOT / 'Binaries/Win64/UnrealEditor-MeridianSquad.dll',
         *ROOT.glob('Content/Development/PhysicsControlRecovery01/**/*.uasset'),
         *ROOT.glob('Scripts/PhysicsControlRecovery01/*.py'),
         *ROOT.glob('Scripts/PhysicsControlRecovery01/*.json'),
         ROOT / 'Scripts/AssetRegistry/manifests/PhysicsControlRecovery01.json',
         ROOT / 'Docs/PhysicsControlRecovery01.md']
rows = []
for path in paths:
    if not path.is_file():
        continue
    dest = DEST / path.relative_to(ROOT)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, dest)
    rows.append(dict(path=path.relative_to(ROOT).as_posix(), bytes=path.stat().st_size,
                     sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
(DEST / 'manifest.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
print(json.dumps(dict(candidate=sys.argv[1], files=len(rows))))
