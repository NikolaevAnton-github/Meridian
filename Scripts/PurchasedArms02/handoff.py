"""Exact task-scoped inventory and preservation checks; no staging or commits."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/PurchasedArms02/Worker'

def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    assets=json.loads((ROOT/'Assets/Source/PurchasedArms02/source-manifest.json').read_text())['files']
    files=[r['destination'] for r in assets if not r['existed']]
    for r in assets: assert sha(ROOT/r['destination'])==r['active_sha256'],r['destination']
    files += ['Source/MeridianSquad/OpeningLobbyCharacter.h','Source/MeridianSquad/OpeningLobbyCharacter.cpp',
        'Source/MeridianSquad/PurchasedArmsAnimInstance.h','Source/MeridianSquad/PurchasedArmsAnimInstance.cpp',
        'Source/MeridianSquad/OpeningLobbyGameMode.cpp','Config/DefaultInput.ini',
        'Docs/PurchasedArms02.md','Assets/Source/PurchasedArms02/source-manifest.json']
    scripts=sorted((ROOT/'Scripts/PurchasedArms02').glob('*.py'))
    for p in scripts: ast.parse(p.read_text(),filename=str(p))
    files += [p.relative_to(ROOT).as_posix() for p in scripts]
    rows=[{'path':p,'sha256':sha(ROOT/p),'bytes':(ROOT/p).stat().st_size} for p in sorted(files)]
    archive=json.loads((ROOT/'Assets/Archive/PurchasedArms01/manifest.json').read_text())['files']
    for r in archive: assert sha(ROOT/r['archived'])==r['sha256'],r['archived']
    map_path=ROOT/'Content/Maps/L_OpeningLobby_PainterStone01.umap'
    map_hash=sha(map_path)
    assert map_hash=='b28fa0f6e8bb80dcc71b4789df9c3e2375a3cf8b1da67021225584e4560fd92f'
    result={'task':'MSQ-62','files':rows,'map_sha256':map_hash,'verified_archive_files':len(archive),
        'binary_count':sum(p.endswith('.uasset') for p in files),'python_syntax_files':len(scripts),
        'note':'Worker inventory for controller review and scoped commit; no owner/task/controller files included.'}
    (OUT/'changed-files.json').write_text(json.dumps(result,indent=2))
    subprocess.run(['git','diff','--check','--',*[p for p in files if not p.endswith('.uasset')]],cwd=ROOT,check=True)
    (OUT/'git-status-handoff.txt').write_bytes(subprocess.check_output(['git','status','--short'],cwd=ROOT))
    print(json.dumps({k:v for k,v in result.items() if k!='files'}))

if __name__=='__main__': main()
