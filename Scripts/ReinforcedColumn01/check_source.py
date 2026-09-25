"""Check physical volume, finite coordinates, and limits of the authored source."""
import collections
import json
import math
import hashlib
import sys
import argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('name',nargs='?',default='source-check.json')
parser.add_argument('--source',default='Assets/Source/ReinforcedColumn01/column.json')
parser.add_argument('--evidence-root',default='Saved/ReinforcedColumn01/Candidate01')
options=parser.parse_args()
source_path=ROOT/options.source
source=json.loads(source_path.read_text())

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
failures=dict(nonpositive=[dict(index=i,**p) for i,p in enumerate(pieces) if p['volume_cm3']<=0],
              open_pieces=[dict(index=i,**p) for i,p in enumerate(pieces) if p['nonmanifold_edges']])
if any(failures.values()):
    fail_path=ROOT/options.evidence_root/(options.name+'.failures.json')
    assert not fail_path.exists()
    fail_path.write_text(json.dumps(failures,indent=2),encoding='utf-8')
    print(json.dumps({k:dict(count=len(v),examples=v[:2]) for k,v in failures.items()}),flush=True)
assert all(p['volume_cm3']>0 for p in pieces)
assert all(p['nonmanifold_edges']==0 for p in pieces)
assert all(math.isfinite(x) for m in [source['core'],source['steel']]+source['pieces'] for p in m['vertices'] for x in p)
total=core['volume_cm3']+sum(p['volume_cm3'] for p in pieces)
assert abs(total-240*240*1800)<50, total
record=dict(core=core,pieces=pieces,total_solid_cm3=total,expected_column_cm3=240*240*1800,body_limit=len(pieces),finite=True)
anchors=[inspect(m) for m in source.get('anchors',[])]
assert all(a['volume_cm3']>0 and a['nonmanifold_edges']==0 for a in anchors)
record['fixed_bond_anchors']=anchors
record['source_sha256']=hashlib.sha256(source_path.read_bytes()).hexdigest()
out=ROOT/options.evidence_root/options.name
assert not out.exists()
out.write_text(json.dumps(record,indent=2))
print(json.dumps({k:v for k,v in record.items() if k not in ['pieces','fixed_bond_anchors']}))
