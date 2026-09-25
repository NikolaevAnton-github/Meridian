"""Read actual vendor/candidate managed hierarchy and anchoring without mutation."""
import json
from pathlib import Path
import unreal as u
OUT=Path('D:/devgames/MeridianSquad/Saved/ReinforcedColumn01/Candidate01')
paths=dict(vendor='/Game/NextGenDestruction/GeometryCollections/Concrete/GC_ConcretePillar_Square_5m',
           candidate='/Game/ReinforcedColumn01/GC_RC01_BondedConcrete')
report={}
for key,path in paths.items():
    row=json.loads(u.NGDColumnAuthoring.inspect_collection(u.load_asset(path)))
    row['asset']=path
    report[key]=row
target=OUT/'managed-collection-comparison.json'
assert not target.exists()
target.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({key:{k:v for k,v in row.items() if k!='hierarchy'} for key,row in report.items()}))
