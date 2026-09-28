"""Inventory the new render-only candidate without rebaselining source assets."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'Assets/Source/DestructionScaling01/Candidate01'
DEST=ROOT/'Content/OpeningLobby/DestructionScaling01/Candidate01'
SOURCE.mkdir(parents=True,exist_ok=True)
def fingerprint(path):
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size_bytes':path.stat().st_size}
inputs=[ROOT/'Content/OpeningLobby/LobbyColumns01/DA_Cladding01.uasset',ROOT/'Source/MeridianSquad/DestructionCompactAuthoring.cpp']
inputs.extend(ROOT/('Content/'+p.removeprefix('/Game/')+'.uasset')
    for p in json.loads((ROOT/'Saved/DestructionScaling01/compact-sources-01.json').read_text()))
report=json.loads((ROOT/'Saved/DestructionScaling01/compact-authoring-01.json').read_text())
provenance={'task':'MSQ-167','candidate':'Candidate01','inputs':[fingerprint(p) for p in inputs],
    'authoring':report,'method':'Append original mesh descriptions with authored tile transforms; preserve normals, tangents, all UV channels, colors and material assignments. No simplification. Original tile collision retained.',
    'acceptance':'Technical candidate; owner visual/play verdict pending.'}
source=SOURCE/'provenance.json'
assert not source.exists(),'Immutable candidate provenance already exists'
source.write_text(json.dumps(provenance,indent=2)+'\n')
paths=[source]+sorted(DEST.glob('*.uasset'))
evidence=[{'source':source.relative_to(ROOT).as_posix(),'note':'Derived render-only candidate. Exact triangle count preserved; original collision and assets unchanged. Owner verdict pending.'}]
artifacts=[]
for p in paths:
    item=fingerprint(p)
    item.update(role='unreal_asset' if p.suffix=='.uasset' else 'source_provenance',
        unreal_package='/Game/'+p.relative_to(ROOT/'Content').with_suffix('').as_posix() if p.suffix=='.uasset' else None,evidence=evidence)
    artifacts.append(item)
dependencies=[{'upstream':artifacts[0]['path'],'downstream':a['path'],'kind':'derived_render_geometry',
    'status':'declared','evidence':evidence} for a in artifacts[1:]]
manifest={'asset':'DestructionScaling01-CompactFacing-Candidate01','artifacts':artifacts,'dependencies':dependencies}
(ROOT/'Scripts/AssetRegistry/manifests/DestructionScaling01-CompactFacing-Candidate01.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'artifacts':len(artifacts),'bytes':sum(a['size_bytes'] for a in artifacts)}))
