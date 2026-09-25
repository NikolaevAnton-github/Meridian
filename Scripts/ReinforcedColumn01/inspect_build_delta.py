"""Bound the read-only inspector addition and prove the tested asset bytes persist."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/ReinforcedColumn01/Candidate01'
old=OUT/'BeforeInspection/Source/MeridianSquad/NGDColumnAuthoring.cpp'
new=ROOT/'Source/MeridianSquad/NGDColumnAuthoring.cpp'
prior=old.read_text()
current=new.read_text()
marker='FString UNGDColumnAuthoring::InspectCollection'
builder='FString UNGDColumnAuthoring::BuildColumn'
assert prior.split(marker)[0]==current.split(marker)[0]
assert prior.split(builder)[1]==current.split(builder)[1]
manifest=json.loads((OUT/'candidate-fingerprints.json').read_text())['files']
paths=[p for p in manifest if p.startswith('Content/') or p.startswith('Assets/Source/') or p=='Source/MeridianSquad/NGDPropComponent.cpp']
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==manifest[p]['sha256'] for p in paths)
report=dict(passed=True,earlier_runtime_build='Build08',current_inspector_build='Build09',
    changed_native_function='UNGDColumnAuthoring::InspectCollection (read-only)',
    authoring_build_function_unchanged=True,material_mesh_helpers_unchanged=True,
    tested_map_assets_sources_and_runtime_adapter_unchanged=paths)
target=OUT/'inspector-only-diff.json'
assert not target.exists()
target.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(dict(passed=True,unchanged_files=len(paths))))
