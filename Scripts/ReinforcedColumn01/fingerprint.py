"""Freeze candidate file identities after checks and handoff are complete."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/ReinforcedColumn01/Candidate01'
paths=[]
for directory in ['Content/ReinforcedColumn01','Assets/Source/ReinforcedColumn01','Scripts/ReinforcedColumn01']:
    paths += [p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
paths += [ROOT/p for p in ['Content/Maps/L_OpeningLobby_PainterStone01.umap','Source/MeridianSquad/NGDColumnAuthoring.h','Source/MeridianSquad/NGDColumnAuthoring.cpp','Source/MeridianSquad/NGDPropComponent.cpp','Source/MeridianSquad/MeridianSquad.Build.cs','Docs/ReinforcedColumn01.md','Docs/Tasks/ReinforcedColumn01.md','Binaries/Win64/UnrealEditor-MeridianSquad.dll']]
for name in ['verification.json','review-reopened.json','review-impact.json','review-burst.json','review-layers.json','review-reset.json','review-after-reset-shot.json','review-cavity-collision.json','review-detail-state.json','review-intact.png','review-damaged-layers.png','review-detail.png','review-reset.png','review-editor-intact.png','asset-build07.json','Build08.json','source-check02.json','native-settings.json','storage.json']:
    paths.append(OUT/name)
paths += [OUT/name for name in ['verification02.json','Build09.json','managed-collection-comparison.json','core-seams01.json','inspector-only-diff.json']]
record=dict(candidate='MSQ-154-Candidate01',build='Build09',runtime_evidence_build='Build08',asset_build='asset-build07',files={p.relative_to(ROOT).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(paths)})
path=OUT/(sys.argv[1] if len(sys.argv)>1 else 'candidate-fingerprints.json')
assert not path.exists()
path.write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(dict(candidate=record['candidate'],files=len(paths),map_sha256=record['files']['Content/Maps/L_OpeningLobby_PainterStone01.umap']['sha256'])))
