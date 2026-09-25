"""Check physical volume, finite coordinates, and limits of the authored source."""
import collections
import json
import math
import hashlib
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
source=json.loads((ROOT/'Assets/Source/ReinforcedColumn01/column.json').read_text())

def inspect(m):
    edges=collections.Counter()
    volume=0.
    for a,b,c,mat in m['triangles']:
        v=[tuple(round(x,4) for x in m['vertices'][i]) for i in [a,b,c]]
        for p,q in zip(v,v[1:]+v[:1]): edges[tuple(sorted([p,q]))]+=1
        p,q,r=v
        volume+=(p[0]*(q[1]*r[2]-q[2]*r[1])+p[1]*(q[2]*r[0]-q[0]*r[2])+p[2]*(q[0]*r[1]-q[1]*r[0]))/6
    return dict(volume_cm3=volume,nonmanifold_edges=sum(n!=2 for n in edges.values()),
        minimum=[min(p[i] for p in m['vertices']) for i in range(3)],maximum=[max(p[i] for p in m['vertices']) for i in range(3)])

pieces=[inspect(m) for m in source['pieces']]
core=inspect(source['core'])
assert all(p['volume_cm3']>0 for p in pieces)
assert all(p['nonmanifold_edges']==0 for p in pieces)
assert all(math.isfinite(x) for m in [source['core'],source['steel']]+source['pieces'] for p in m['vertices'] for x in p)
total=core['volume_cm3']+sum(p['volume_cm3'] for p in pieces)
assert abs(total-240*240*1800)<50, total
record=dict(core=core,pieces=pieces,total_solid_cm3=total,expected_column_cm3=240*240*1800,body_limit=len(pieces),finite=True)
anchors=[inspect(m) for m in source.get('anchors',[])]
assert all(a['volume_cm3']>0 and a['nonmanifold_edges']==0 for a in anchors)
record['fixed_bond_anchors']=anchors
record['source_sha256']=hashlib.sha256((ROOT/'Assets/Source/ReinforcedColumn01/column.json').read_bytes()).hexdigest()
out=ROOT/'Saved/ReinforcedColumn01/Candidate01'/(sys.argv[1] if len(sys.argv)>1 else 'source-check.json')
assert not out.exists()
out.write_text(json.dumps(record,indent=2))
print(json.dumps({k:v for k,v in record.items() if k not in ['pieces','fixed_bond_anchors']}))
