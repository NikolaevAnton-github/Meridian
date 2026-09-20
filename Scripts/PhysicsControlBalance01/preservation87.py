"""Verify existing preservation inventories without scanning unrelated caches."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/CombatSlice01/PhysicsControlBalance01/Worker'

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(4*1024*1024),b''):h.update(chunk)
    return h.hexdigest()

before=json.loads((OUT/'preservation-before.json').read_text())
intentional={'Source/MeridianSquad/PhysicsControlDummy.cpp','Source/MeridianSquad/PhysicsControlDummy.h'}
changed=[];preserved=[]
for row in before:
    path=ROOT/row['path']
    actual=digest(path) if path.exists() else None
    if actual!=row['sha256']:
        changed.append(dict(path=row['path'],before=row['sha256'],after=actual,
            expected_task_edit=row['path'] in intentional or row['path'].startswith('Content/Development/PhysicsControlBalance01/')))
    else:preserved.append(row['path'])
controller=[]
for row in json.loads((OUT.parent/'Controller/preservation-before.json').read_text(encoding='utf-8-sig')):
    path=Path(row['Path'])
    actual=digest(path)
    controller.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=actual,preserved=actual==row['Hash'].lower()))
provenance=json.loads((ROOT/'Assets/Source/PhysicsControlBalance01/MixamoGetUp01/provenance.json').read_text(encoding='utf-8-sig'))
sources=[dict(path=c['path'],sha256=digest(ROOT/c['path']),preserved=digest(ROOT/c['path'])==c['sha256']) for c in provenance['clips']]
task_bytes=sum(p.stat().st_size for base in [OUT,ROOT/'Content/Development/PhysicsControlBalance01'] for p in base.rglob('*') if p.is_file())
storage=json.loads((OUT/'storage-before.json').read_text())
result=dict(task='MSQ-87',unchanged_inventory_files=len(preserved),changes=changed,
    controller_protected_files=controller,original_mixamo_sources=sources,
    budget=dict(project_bytes_before=storage['bytes'],task_output_and_asset_bytes=task_bytes,
        conservative_before_plus_task_bytes=storage['bytes']+task_bytes,limit_bytes=storage['limit_bytes'],
        method='Existing whole-project baseline plus complete bounded task output/assets; intentionally double-counts any task files already present at baseline. No whole-project cache rescan.'),
    passed=all(c['expected_task_edit'] for c in changed) and all(c['preserved'] for c in controller+sources) and storage['bytes']+task_bytes<storage['limit_bytes'])
path=OUT/'preservation-after01.json';assert not path.exists()
path.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
