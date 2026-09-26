"""Source-only depth, support, UV and deformation checks; never runs gameplay."""
import hashlib
import json
import math
import random
import argparse
from pathlib import Path
import generate_progressive as g

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('--source',default='Assets/Source/ReinforcedColumn01/ReinforcedColumn02-Candidate01/column03.json')
parser.add_argument('--output',default='Saved/ReinforcedColumn02/Candidate01/progression03.json')
parser.add_argument('--deformation',choices=['progressive','spalling'],default='progressive')
options=parser.parse_args()
if options.deformation=='spalling':
    from shape_spalling import raw_transform as deformation
else:
    deformation=g.warp
SOURCE=ROOT/options.source
OUT=ROOT/options.output
assert not OUT.exists()
source=json.loads(SOURCE.read_text())
meshes=source['pieces']
bounds=[([min(v[k] for v in m['vertices']) for k in range(3)],
         [max(v[k] for v in m['vertices']) for k in range(3)]) for m in meshes]
# Every dynamic bounding box lies outside this square prism. Therefore no
# removable triangle or convex hull can cut its continuous structural spine.
spine_half=min(max(lo[0],-hi[0],lo[1],-hi[1]) for lo,hi in bounds)
anchor_extent=max(abs(p[k]) for m in source['anchors'] for p in m['vertices'] for k in [0,1])
print(json.dumps(dict(spine_half=spine_half,anchor_extent=anchor_extent)),flush=True)
assert spine_half>35
assert all(0<p[2]<280 for m in source['anchors'] for p in m['vertices'])
previous=json.loads((ROOT/'Assets/Source/ReinforcedColumn01/column.json').read_text())
assert source['steel']==previous['steel']
assert source['materials']==previous['materials']
assert sorted(i for group in source['clusters'] for i in group)==list(range(len(meshes)+len(source['anchors'])))
assert all(sum(i>=len(meshes) for i in group)==1 for group in source['clusters'])

core_bins={}
def crossings(m,axis,sign,lateral,height,z_shift=0,limit=110):
    other=1-axis
    ys=[]
    triangles=m['triangles']
    if m is source['core']:
        # The support probes all target the lower band. Index its projected
        # triangle bounds so checking every anchor remains practical as the
        # physical fracture surface becomes denser.
        if axis not in core_bins:
            bins={}
            for triangle in triangles:
                points=[m['vertices'][i] for i in triangle[:3]]
                low=max(0,min(p[2]+z_shift for p in points)); high=min(280,max(p[2]+z_shift for p in points))
                if high<low: continue
                for row in range(math.floor(low/8),math.floor(high/8)+1):
                    for col in range(math.floor(min(p[other] for p in points)/8),math.floor(max(p[other] for p in points)/8)+1):
                        bins.setdefault((col,row),[]).append(triangle)
            core_bins[axis]=bins
        triangles=core_bins[axis].get((math.floor(lateral/8),math.floor(height/8)),[])
    for ai,bi,ci,_ in triangles:
        a,b,c=[m['vertices'][i] for i in [ai,bi,ci]]
        az=a[2]+z_shift; bz=b[2]+z_shift; cz=c[2]+z_shift
        denom=(bz-cz)*(a[other]-c[other])+(c[other]-b[other])*(az-cz)
        if abs(denom)<1e-10: continue
        u=((bz-cz)*(lateral-c[other])+(c[other]-b[other])*(height-cz))/denom
        v=((cz-az)*(lateral-c[other])+(a[other]-c[other])*(height-cz))/denom
        if u>=-1e-7 and v>=-1e-7 and u+v<=1+1e-7:
            depth=120-sign*(u*a[axis]+v*b[axis]+(1-u-v)*c[axis])
            if -1e-3<=depth<limit: ys.append(depth)
    return sorted(set(round(v,4) for v in ys))

anchor_clearances=[]
anchor_check=OUT.with_name('anchor-'+OUT.name)
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
if anchor_check.exists():
    cached=json.loads(anchor_check.read_text())
    assert cached['source_sha256']==source_hash
    anchor_clearances=cached['clearances']
else:
    for m in source['anchors']:
        for p in set(tuple(p) for p in m['vertices']):
            hits=crossings(source['core'],0,1,p[1],p[2],900,240)
            assert len(hits)>=2 and len(hits)%2==0, hits
            clearance=max(min(120-p[0]-a,b-(120-p[0])) for a,b in zip(hits[::2],hits[1::2]))
            assert clearance>(.05 if options.deformation=='spalling' else 1.), (p,hits)
            anchor_clearances.append(clearance)
    anchor_check.write_text(json.dumps(dict(source_sha256=source_hash,clearances=anchor_clearances)),encoding='utf-8')
rays=[]
for axis,sign in [(1,1),(0,-1),(1,-1),(0,1)]:
    other=1-axis
    for lateral in [-60.,0.,60.]:
        for z in [45.,100.,155.,210.,260.]:
            cells=[]
            for i,(lo,hi) in enumerate(bounds):
                if not lo[other]<=lateral<=hi[other] or not lo[2]<=z<=hi[2]: continue
                if (lo[axis] if sign>0 else -hi[axis])<0: continue
                hits=crossings(meshes[i],axis,sign,lateral,z)
                assert len(hits)%2==0, (i,hits)
                # A curved closed fragment can intersect the same ray more
                # than once. Preserve real intervals, not its convex envelope.
                for front,back in zip(hits[::2],hits[1::2]):
                    if back-front>.001: cells.append(dict(piece=i,front=front,back=back))
            cells.sort(key=lambda c:c['front'])
            core_hits=crossings(source['core'],axis,sign,lateral,z,900)
            core_depth=min(core_hits)
            # Only the removable run in front of the first structural mass is
            # reachable from this ray; farther lobes can be reached from a side.
            cells=[c for c in cells if c['front']<core_depth-.005]
            assert cells and abs(cells[0]['front'])<.002
            assert abs(cells[-1]['back']-core_depth)<.005
            assert all(abs(a['back']-b['front'])<.005 for a,b in zip(cells,cells[1:]))
            assert len({c['piece'] for c in cells})>=2, cells
            rays.append(dict(axis=axis,sign=sign,lateral=lateral,height=z,cells=cells,core_depth=core_depth))

rng=random.Random(1);jacobians=[];h=.00001 if options.deformation=='spalling' else .03
for _ in range(2000):
    p=(rng.uniform(-118,118),rng.uniform(-118,118),rng.uniform(1,279));a=deformation(p)
    columns=[g.mul(g.sub(deformation(g.add(p,v)),a),1/h) for v in [(h,0,0),(0,h,0),(0,0,h)]]
    jacobians.append(g.dot(columns[0],g.cross(columns[1],columns[2])))
assert min(jacobians)>(.001 if options.deformation=='spalling' else .5), min(jacobians)
for m in [source['core']]+meshes+source['anchors']:
    assert len(m['vertices'])==len(m['normals'])==len(m['uvs'])
    assert all(.99<g.length(n)<1.01 for n in m['normals'])
    assert all(math.isfinite(v) for uv in m['uvs'] for v in uv)
report=dict(source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),rays=rays,
            min_removable_intervals=min(len(r['cells']) for r in rays),max_removable_intervals=max(len(r['cells']) for r in rays),
            min_distinct_removable_pieces=min(len({c['piece'] for c in r['cells']}) for r in rays),
            max_distinct_removable_pieces=max(len({c['piece'] for c in r['cells']}) for r in rays),
            min_core_depth_cm=min(r['core_depth'] for r in rays),max_core_depth_cm=max(r['core_depth'] for r in rays),
            guaranteed_central_spine_width_cm=2*spine_half,anchor_outer_extent_cm=anchor_extent,
            anchor_corners_inside_core=len(anchor_clearances),min_anchor_x_clearance_cm=min(anchor_clearances),
            steel_exact=True,original_materials_exact=True,complete_cluster_partition=True,
            deformation_samples=2000,min_deformation_jacobian=min(jacobians),normal_uv_integrity=True,
            gameplay_tested=False)
if options.deformation=='spalling':
    # Probe the actual core triangles at unchanged longitudinal rod positions.
    # Each test distinguishes full cover, a rod crossing the rough surface,
    # and a fully exposed rod. This is geometric evidence, not a visual score.
    bars=[]
    for axis,sign in [(1,1),(0,-1),(1,-1),(0,1)]:
        for lateral in [-110.8+221.6*i/7 for i in range(1,7)]:
            for z in range(20,261,5):
                hits=crossings(source['core'],axis,sign,lateral,z,900,240)
                depth=min(hits)
                state='covered' if depth<7.66 else 'crossing' if depth<10.74 else 'exposed'
                bars.append(dict(axis=axis,sign=sign,lateral=lateral,height=z,core_depth=depth,state=state))
    counts={state:sum(p['state']==state for p in bars) for state in ['covered','crossing','exposed']}
    assert counts['covered']>len(bars)*.15 and counts['exposed']>len(bars)*.15, counts
    report.update(deformation='spalling',rod_samples=bars,rod_coverage_counts=counts,
                  minimum_required_anchor_clearance_cm=.05)
OUT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['rays','rod_samples']}))
