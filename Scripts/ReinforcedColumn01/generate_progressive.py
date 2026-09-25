"""MSQ-156 closed 3D Voronoi concrete with three staggered removable depths.

The same canonical tessellated face is shared by both solids. An invertible
coordinate flow bends fracture faces and their rims while retaining the exact
outer planes, 1.8 cm stone layer and upper architecture. No runtime simulation.
"""
import collections
import hashlib
import json
import math
import random
import argparse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Assets/Source/ReinforcedColumn01/ReinforcedColumn02-Candidate01'
EVIDENCE=ROOT/'Saved/ReinforcedColumn02/Candidate01'
RNG=random.Random(15601)
SKIN=1.8
EDGE_SPACING=4.5
FACET_SAMPLES=[]
RIM_SAMPLES=[]

def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def mul(a,s): return tuple(x*s for x in a)
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def length(a): return math.sqrt(dot(a,a))
def unit(a): return mul(a,1/max(length(a),1e-20))
def mean(p): return tuple(sum(v[k] for v in p)/len(p) for k in range(3))
def key(p): return tuple(round(v,5) for v in p)
def rotated(p,side):
    x,y,z=p
    for _ in range(side): x,y=-y,x
    return (x,y,z)

def ordered(points,n):
    # Keep double precision throughout clipping. Rounding intermediate plane
    # intersections creates spurious sliver caps at later bisectors.
    points=list({tuple(round(v,9) for v in p):p for p in points}.values())
    if len(points)<3: return []
    center=mean(points)
    a=unit(cross(n,(0,0,1) if abs(unit(n)[2])<.9 else (0,1,0)))
    b=cross(unit(n),a)
    points.sort(key=lambda p:math.atan2(dot(sub(p,center),b),dot(sub(p,center),a)))
    return points

def clean_polygon(poly):
    poly=list(dict.fromkeys(key(p) for p in poly))
    changed=True
    while changed and len(poly)>=3:
        changed=False
        for i,p in enumerate(poly):
            a=poly[i-1]; b=poly[(i+1)%len(poly)]
            if length(cross(sub(p,a),sub(b,a))) < 1e-5*max(length(sub(b,a)),1.):
                poly.pop(i);changed=True;break
    return poly

def cut_polygon(poly,n,d):
    inside=[]; hits=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        da=dot(a,n)-d; db=dot(b,n)-d
        if da<=1e-7: inside.append(a)
        if (da < -1e-7 and db > 1e-7) or (db < -1e-7 and da > 1e-7):
            p=add(a,mul(sub(b,a),da/(da-db)))
            inside.append(p); hits.append(p)
        elif abs(da)<=1e-7: hits.append(a)
    return inside,hits

def box(x0,x1,y0,y1,z0,z1):
    points=[(x,y,z) for x in [x0,x1] for y in [y0,y1] for z in [z0,z1]]
    return [(tag,ordered([p for p in points if abs(dot(p,n)-d)<1e-7],n)) for tag,n,d in
            [(-1,(-1,0,0),-x0),(-2,(1,0,0),x1),(-3,(0,-1,0),-y0),
             (-4,(0,1,0),y1),(-5,(0,0,-1),-z0),(-6,(0,0,1),z1)]]

def cut_solid(faces,n,d,tag):
    result=[]; hits=[]
    for oldtag,poly in faces:
        new,edge=cut_polygon(poly,n,d)
        if len(new)>=3: result.append((oldtag,new))
        hits.extend(edge)
    cap=ordered(hits,n)
    if len(cap)>=3: result.append((tag,cap))
    return result

def warp(p):
    # Each step is monotone in the moved coordinate; its offset depends only
    # on the other two coordinates. Composing the steps remains invertible.
    # In contrast to fading the entire vector at the skin, tangential motion
    # continues through it: both the stone rim and the concrete beneath bend.
    result=list(p)
    for k in range(3):
        center=140. if k==2 else 0.
        limit=140. if k==2 else 120-SKIN
        value=result[k]-center
        if abs(value)>=limit-1e-8: continue
        a,b=result[(k+1)%3],result[(k+2)%3]
        shift=1.4*math.sin(a*.061+b*.047+k*1.9)
        shift+=4.5*math.sin(a*.173-b*.139+k*2.3)
        shift+=1.8*math.sin(a*.417+b*.329+k*1.7)
        shift+=.45*math.sin(a*1.07-b*.89+k*2.7)
        result[k]=center+limit*math.tanh(math.atanh(value/limit)+shift/limit)
    return key(result)

def empty(): return dict(vertices=[],triangles=[],normals=[],uvs=[])

def surface(poly,material,normal=None,rough=True):
    """One closed-interface side, with smooth normals and one continuous UV basis."""
    poly=list(dict.fromkeys(key(p) for p in poly))
    if len(poly)<3: return empty()
    n=normal or unit(cross(sub(poly[1],poly[0]),sub(poly[2],poly[0])))
    center=mean(poly)
    positions=[]; tris=[]; lookup={}
    def vertex(p):
        p=key(p)
        if p not in lookup:
            lookup[p]=len(positions); positions.append(p)
        return lookup[p]
    # Every incident face uses the same boundary samples. Interior longest-edge
    # refinement avoids the old coarse fan and never adds unmatched rim points.
    center_id=vertex(center)
    for a,b in zip(poly,poly[1:]+poly[:1]):
        divisions=max(1,math.ceil(length(sub(b,a))/EDGE_SPACING)) if rough else 1
        lo,hi=sorted((a,b))
        edge=[vertex(add(lo,mul(sub(hi,lo),i/divisions))) for i in range(divisions+1)]
        if a!=lo: edge.reverse()
        for i,j in zip(edge,edge[1:]):
            if length(cross(sub(positions[i],center),sub(positions[j],center)))>1e-8:
                tris.append([center_id,i,j,material])
        if rough and material==2 and length(sub(b,a))>15 and all(abs(max(abs(p[0]),abs(p[1]))-(120-SKIN))<1e-4 for p in [a,b]):
            RIM_SAMPLES.append([positions[i] for i in edge])
    if rough:
        for iteration in range(16):
            split={}
            for a,b,c,_ in tris:
                for i,j in [(a,b),(b,c),(c,a)]:
                    pair=tuple(sorted((i,j)))
                    if pair not in split and length(sub(positions[i],positions[j]))>EDGE_SPACING+1e-5:
                        split[pair]=vertex(mul(add(positions[i],positions[j]),.5))
            if not split: break
            refined=[]
            for a,b,c,m in tris:
                ids=[a,b,c]
                mids=[split.get(tuple(sorted((ids[i],ids[(i+1)%3])))) for i in range(3)]
                count=sum(i is not None for i in mids)
                if count==0: parts=[(a,b,c)]
                elif count==3:
                    ab,bc,ca=mids
                    parts=[(a,ab,ca),(ab,b,bc),(ca,bc,c),(ab,bc,ca)]
                else:
                    # Rotate to put the sole split or sole unsplit edge first.
                    pivot=next(i for i,v in enumerate(mids) if (v is not None)==(count==1))
                    a,b,c=ids[pivot:]+ids[:pivot]
                    ab,bc,ca=mids[pivot:]+mids[:pivot]
                    parts=[(a,ab,c),(ab,b,c)] if count==1 else [(a,b,ca),(b,bc,ca),(ca,bc,c)]
                refined.extend([*t,m] for t in parts)
            tris=refined
        else: raise AssertionError('Fracture refinement did not converge.')
    if not tris: return empty()
    used=sorted({i for t in tris for i in t[:3]}); remap={old:new for new,old in enumerate(used)}
    positions=[positions[i] for i in used]
    tris=[[remap[a],remap[b],remap[c],m] for a,b,c,m in tris]
    warped=[warp(p) if rough else key(p) for p in positions]
    area=sum(length(cross(sub(positions[b],positions[a]),sub(positions[c],positions[a])))/2 for a,b,c,_ in tris)
    if rough and material==2 and area>=150:
        FACET_SAMPLES.append(dict(area_cm2=area,normal=n,positions=positions))
    normals=[(0.,0.,0.) for _ in positions]
    for a,b,c,_ in tris:
        face=cross(sub(warped[b],warped[a]),sub(warped[c],warped[a]))
        for i in [a,b,c]: normals[i]=add(normals[i],face)
    # Vendor instance multiplies UVs by 20; measured interior area/UV ratio is
    # about 1200 cm/UV including relief. A 1000 cm planar base approaches that
    # density once warped, rather than the previous per-triangle 5 cm repeat.
    u=unit(cross((0,0,1) if abs(n[2])<.9 else (0,1,0),n)); v=cross(n,u)
    return dict(vertices=warped,triangles=tris,normals=[key(unit(p)) for p in normals],
                uvs=[(round(dot(p,u)/1000,7),round(dot(p,v)/1000,7)) for p in positions])

def append(target,part,reverse=False,z_shift=0):
    start=len(target['vertices'])
    target['vertices'].extend([(p[0],p[1],round(p[2]+z_shift,5)) for p in part['vertices']])
    target['normals'].extend([mul(n,-1) if reverse else n for n in part['normals']])
    target['uvs'].extend(part['uvs'])
    target['triangles'].extend([[start+a,start+(c if reverse else b),start+(b if reverse else c),m] for a,b,c,m in part['triangles']])

def split_material(poly,external):
    regions=[poly]
    for n in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]:
        next_regions=[]
        for p in regions:
            distances=[dot(v,n)-(120-SKIN) for v in p]
            if min(distances)>-1e-5 or max(distances)<1e-5:
                next_regions.append(p)
                continue
            inside,_=cut_polygon(p,n,120-SKIN)
            outside,_=cut_polygon(p,mul(n,-1),-(120-SKIN))
            for q in [inside,outside]:
                if len(set(key(v) for v in q))>=3: next_regions.append(q)
        regions=next_regions
    return [(p,0 if external else 1 if max(abs(mean(p)[0]),abs(mean(p)[1]))>120-SKIN+1e-6 else 2) for p in regions]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--revision',default='01')
    revision=parser.parse_args().revision
    assert revision.isdigit()
    source_path=OUT/('column'+revision+'.json')
    assert not source_path.exists(), 'Candidate source is immutable; choose a new revision.'
    seeds=[]; meta=[]
    # Staggering in all three dimensions avoids aligned, terminal 2D pockets.
    for side in range(4):
        for layer,(nx,nz,depth,extent) in enumerate([(8,9,4.5,116),(7,7,18.,100),(6,6,34.,84)]):
            for ix in range(nx):
                for iz in range(nz):
                    t=-extent+2*extent*(ix+.5)/nx+RNG.uniform(-.29,.29)*(2*extent/nx)
                    z=280*(iz+.5)/nz+RNG.uniform(-.31,.31)*(280/nz)
                    d=depth+RNG.uniform(-1.5,1.5) if layer==0 else depth+RNG.uniform(-3,3)
                    # Some paired seeds make genuine shallow stone chips. Their
                    # bisector is the 1.8 cm skin boundary, with concrete behind.
                    chip=layer==0 and (ix*13+iz*7+side)%19==0
                    if chip: d=3.2
                    seeds.append(rotated((t,120-d,z),side))
                    meta.append(dict(side=side,layer=layer,grid=[ix,iz],shallow=False))
                    if chip:
                        seeds.append(rotated((t,119.6,z),side))
                        meta.append(dict(side=side,layer=0,grid=[ix,iz],shallow=True))
    dynamic_count=len(seeds)
    for x in [-56.,0.,56.]:
        for y in [-56.,0.,56.]:
            for z in [24.,81.,140.,199.,256.]:
                seeds.append((x+RNG.uniform(-4,4),y+RNG.uniform(-4,4),z+RNG.uniform(-4,4)))
    cells=[]
    for i,seed in enumerate(seeds):
        faces=box(-120,120,-120,120,0,280)
        neighbours=sorted((dot(sub(other,seed),sub(other,seed)),j) for j,other in enumerate(seeds) if j!=i)
        for distance,j in neighbours:
            maxradius=max(dot(sub(p,seed),sub(p,seed)) for _,poly in faces for p in poly)
            if distance>4*maxradius+1e-3: break
            n=sub(seeds[j],seed)
            faces=cut_solid(faces,n,.5*(dot(seeds[j],seeds[j])-dot(seed,seed)),j)
        assert faces, i
        cells.append(faces)
        if i%100==0: print('Clipped',i,'/',len(seeds),flush=True)
    pieces=[empty() for _ in range(dynamic_count)]; core=empty()
    for i,faces in enumerate(cells):
        for neighbour,poly in faces:
            if neighbour>=0 and (neighbour<i or i>=dynamic_count and neighbour>=dynamic_count): continue
            if neighbour==-6 and i>=dynamic_count: continue
            poly=clean_polygon(poly)
            if len(poly)<3: continue
            # Snap a canonical face once, so the two contacting solids have
            # precisely the same positions, tessellation and surface relief.
            n=unit(cross(sub(poly[1],poly[0]),sub(poly[2],poly[0])))
            for region,material in split_material(poly,neighbour in [-1,-2,-3,-4]):
                part=surface(region,material,n)
                append(pieces[i] if i<dynamic_count else core,part,z_shift=0 if i<dynamic_count else -900)
                if neighbour>=0:
                    append(pieces[neighbour] if neighbour<dynamic_count else core,part,True,0 if neighbour<dynamic_count else -900)
                elif neighbour==-6:
                    append(core,part,True,-900)
    for tag,poly in box(-120,120,-120,120,280,1800):
        if tag!=-5: append(core,surface(poly,0,rough=False),z_shift=-900)
    groups=collections.defaultdict(list)
    for i,row in enumerate(meta):
        ix,iz=row['grid']; groups[(row['side'],row['layer'],ix//2,iz//3)].append(i)
    anchors=[]; clusters=[]; used=collections.Counter()
    for members in groups.values():
        center=mean([seeds[i] for i in members])
        fixed=min(range(dynamic_count,len(seeds)),key=lambda j:dot(sub(seeds[j],center),sub(seeds[j],center)))
        ordinal=used[fixed]; used[fixed]+=1
        x,y,z=add(seeds[fixed],(((ordinal%3)-1)*2.,((ordinal//3)%3-1)*2.,(ordinal//9)*2.))
        anchor=empty()
        for _,poly in box(x-.4,x+.4,y-.4,y+.4,z-.4,z+.4): append(anchor,surface(poly,2,rough=False))
        clusters.append(members+[dynamic_count+len(anchors)]); anchors.append(anchor)
    # Exact previous cage geometry and material preserve cover and embedded ends.
    previous=json.loads((ROOT/'Assets/Source/ReinforcedColumn01/column.json').read_text())
    previews=[]
    for name,depth in [('Shallow',15),('Deep',45)]:
        removed=[]
        for i,row in enumerate(meta):
            x,y,z=seeds[i]
            # A bounded front-face scar, deliberately exposed in the editor.
            if y>120-depth and (x/65)**2+((z-132)/88)**2<1: removed.append(i)
        previews.append(dict(name='SM_RC02_Preview_'+name,pieces=[i for i in range(dynamic_count) if i not in set(removed)],removed=removed))
    source=dict(schema=2,seed=15601,units='centimetres',materials=previous['materials'],core=core,steel=previous['steel'],
                pieces=pieces,anchors=anchors,clusters=clusters,previews=previews)
    record=dict(actor='StaticMeshActor_35',label='FB01_newNcolumnNN12p6NN2p4',location=[-1260,-240,900],
                outer_cm=[240,240,1800],affected_height_cm=[0,280],stone_thickness_cm=SKIN,
                dynamic_bodies=dynamic_count,anchors=len(anchors),local_clusters=len(clusters),fixed_voronoi_cells=len(seeds)-dynamic_count,
                seed_layers_cm=[4.5,18,34],roughness_max_displacement_per_axis_cm=8.15,fracture_edge_spacing_cm=EDGE_SPACING,
                warp='monotone coordinate flow, including tangential motion through the stone rim',uv_base_repeat_cm=1000,texture_repeat_cm=50,
                shallow_chips=sum(row['shallow'] for row in meta),core_triangles=len(core['triangles']),
                fragment_triangles=sum(len(p['triangles']) for p in pieces),steel_preserved=True,
                piece_meta=[dict(**row,seed=seeds[i],cluster=next(j for j,g in enumerate(clusters) if i in g)) for i,row in enumerate(meta)],
                previews=[{k:v for k,v in p.items() if k!='pieces'} for p in previews])
    assert dynamic_count+len(anchors)<900
    assert record['fragment_triangles']<1800000, record['fragment_triangles']
    OUT.mkdir(parents=True,exist_ok=True)
    source_path.write_text(json.dumps(source,separators=(',',':')),encoding='utf-8')
    (OUT/('design'+revision+'.json')).write_text(json.dumps(record,indent=2),encoding='utf-8')
    (EVIDENCE/('surface-samples'+revision+'.json')).write_text(json.dumps(dict(facets=FACET_SAMPLES,rims=RIM_SAMPLES),separators=(',',':')),encoding='utf-8')
    print(json.dumps({k:v for k,v in record.items() if k not in ['piece_meta','previews']}))
    print('Source bytes:',source_path.stat().st_size)

if __name__=='__main__': main()
