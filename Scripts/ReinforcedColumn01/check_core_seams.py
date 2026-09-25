"""Distinguish collinear tessellation junctions from open core boundaries."""
import collections
import hashlib
import json
import math
import argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('--source',default='Assets/Source/ReinforcedColumn01/column.json')
parser.add_argument('--output',default='Saved/ReinforcedColumn01/Candidate01/core-seams01.json')
options=parser.parse_args()
source=ROOT/options.source
core=json.loads(source.read_text())['core']
edges=collections.defaultdict(list)
for ai,bi,ci,_ in core['triangles']:
    vertices=[tuple(round(v,4) for v in core['vertices'][i]) for i in [ai,bi,ci]]
    for a,b in zip(vertices,vertices[1:]+vertices[:1]):
        edges[tuple(sorted([a,b]))].append((a,b))
boundary=[ab for occurrences in edges.values() if len(occurrences)!=2 for ab in occurrences]
points=set(p for ab in boundary for p in ab)
segments=collections.defaultdict(list)
tolerance_cm=.0005
for a,b in boundary:
    direction=[b[i]-a[i] for i in range(3)]
    length2=sum(x*x for x in direction)
    splits={0.:a,1.:b}
    for p in points:
        t=sum((p[i]-a[i])*direction[i] for i in range(3))/length2
        if not 1e-9<t<1-1e-9: continue
        projection=[a[i]+t*direction[i] for i in range(3)]
        if math.dist(projection,p)<=tolerance_cm: splits[t]=p
    ordered=[p for _,p in sorted(splits.items())]
    for x,y in zip(ordered,ordered[1:]):
        key=tuple(sorted([x,y]))
        segments[key].append(1 if (x,y)==key else -1)
unmatched=[dict(a=k[0],b=k[1],orientations=v) for k,v in segments.items() if len(v)!=2 or sum(v)!=0]
interior_orientation_failures=sum(len(v)==2 and v[0]==v[1] for v in edges.values())
report=dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),initial_unpaired_edges=len(boundary),
    method='Split unmatched edges at existing collinear boundary endpoints; require two opposite orientations per resulting segment.',
    tolerance_cm=tolerance_cm,paired_subsegments=len(segments),unmatched_subsegments=unmatched,
    interior_orientation_failures=interior_orientation_failures,passed=not unmatched and not interior_orientation_failures)
out=ROOT/options.output
assert not out.exists()
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
assert report['passed']
