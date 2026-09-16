"""Task-local inventory using established no-junction walk and hash helpers."""
import json
import sys
from pathlib import Path
from functionalbuild01_preflight import walk, digest

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/OpeningLobby/MaterialIntegration01/WorkerFresh01'

def allowed(path):
    return (path.startswith(('Saved/OpeningLobby/MaterialIntegration01/WorkerFresh01/', 'Content/OpeningLobby/MaterialIntegration01/', 'Assets/Source/OpeningLobby/MaterialIntegration01/', 'Scripts/OpeningLobby/materialintegration01_'))
            or path in ('Docs/OpeningLobbyMaterialIntegration01.md', 'Content/Maps/L_OpeningLobby_MaterialIntegration01.umap'))

def entry(p):
    return dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=digest(p))

def scan():
    OUT.mkdir(parents=True, exist_ok=True)
    dest=OUT/'protected-before.json'
    assert not dest.exists()
    paths=[ROOT/'AGENTS.md', ROOT/'.codex/config.toml', ROOT/'MeridianSquad.uproject', ROOT/'.gitattributes']
    for folder in ['Assets','Content','Config','Scripts','Docs','.agents','Source']:
        paths.extend(p for p in walk(ROOT/folder) if '__pycache__' not in str(p) and not allowed(p.relative_to(ROOT).as_posix()))
    for folder in ['Saved/OpeningLobby/MaterialIntegration01/Worker', 'Saved/OpeningLobby/MaterialIntegration01/Controller/ReuseAttempt01']:
        paths.extend(p for p in walk(ROOT/folder) if '__pycache__' not in str(p))
    data=dict(project_bytes=sum(p.stat().st_size for p in walk(ROOT)), entries=[entry(p) for p in paths])
    data['lobby_bytes']=sum(p.stat().st_size for folder in ['Saved/OpeningLobby','Assets/Concepts/OpeningLobby','Assets/Source/OpeningLobby','Content/OpeningLobby'] for p in walk(ROOT/folder))
    dest.write_text(json.dumps(data,indent=2))
    print(json.dumps(dict(protected=len(data['entries']),project_GB=data['project_bytes']/1e9,lobby_GB=data['lobby_bytes']/1e9)))

if __name__=='__main__':
    if sys.argv[1]=='scan':scan()
