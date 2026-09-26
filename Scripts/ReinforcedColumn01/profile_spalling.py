"""Revision 11: normalize coarse core facets to a rough concrete envelope.

A sampled radial profile drives one continuous monotone map for core and debris.
Average core radius stays near revision10; the cladding and body partition stay.
"""
import ast
import functools
import json
import math

import generate_progressive as g
import shape_spalling as shape
from rough_spalling import smooth_core_concrete
from varied_spalling import ROOT, SOURCE, LIMIT

NX=120
NZ=140
ATLAS=[]


def build_atlas(core):
    rows=[[] for _ in range(NZ+1)]
    for a,b,c,material in core['triangles']:
        points=[(core['vertices'][i][0],core['vertices'][i][1],core['vertices'][i][2]+900) for i in (a,b,c)]
        low,high=min(p[2] for p in points),max(p[2] for p in points)
        if high<=0 or low>=280 or high-low<1e-8:
            continue
        for row in range(max(0,math.floor(low/2)),min(NZ,math.ceil(high/2))+1):
            z=min(279.999,max(.001,row*2.))
            if not low<=z<=high:
                continue
            hits=[]
            for p,q in zip(points,points[1:]+points[:1]):
                if (p[2]<=z<q[2]) or (q[2]<=z<p[2]):
                    t=(z-p[2])/(q[2]-p[2])
                    hits.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
            if len(hits)==2:
                a,b=hits
                ex,ey=b[0]-a[0],b[1]-a[1]
                rows[row].append((a[0],a[1],ex,ey,a[0]*ey-a[1]*ex))
    atlas=[[] for _ in range(4)]
    for side in range(4):
        for row,segments in enumerate(rows):
            radii=[]
            for col in range(NX+1):
                t=-1+2*col/NX
                dx,dy,_=g.rotated((t,1.,0),side)
                radius=0.
                for ax,ay,ex,ey,numerator in segments:
                    denominator=dx*ey-dy*ex
                    if abs(denominator)<1e-9:
                        continue
                    s=(ax*dy-ay*dx)/denominator
                    if -.00001<=s<=1.00001:
                        r=numerator/denominator
                        if 0<r<LIMIT and r>radius:
                            radius=r
                assert radius>10,(side,row,col,radius)
                radii.append(radius)
            atlas[side].append(radii)
        print('Core profile face',side,flush=True)
    return atlas


def profile(x,y,z):
    radius=max(abs(x),abs(y))
    if abs(y)>=abs(x):
        side=0 if y>=0 else 2
        t=x/radius if y>=0 else -x/radius
    else:
        side=1 if x<0 else 3
        t=y/radius if x<0 else -y/radius
    col=(t+1)*NX/2;row=max(0.,min(float(NZ),z/2))
    i=min(NX-1,max(0,math.floor(col)));j=min(NZ-1,math.floor(row))
    u,v=col-i,row-j
    face=ATLAS[side]
    return ((face[j][i]*(1-u)+face[j][i+1]*u)*(1-v)
            +(face[j+1][i]*(1-u)+face[j+1][i+1]*u)*v)


@functools.lru_cache(maxsize=1100000)
def transform(p):
    x,y,z=p
    radius=max(abs(x),abs(y))
    if radius>=LIMIT-1e-6 or radius<1e-8 or z>280.00001:
        return p
    old=profile(x,y,z)
    qx,qy=x*LIMIT/radius,y*LIMIT/radius
    target=(86.+10.*shape.noise(qx+17,qy-31,z+29,34.)
            +6.*shape.noise(qx-13,qy+7,z-19,13.)
            +2.*shape.noise(qx+37,qy-11,z+5,5.5))
    target=max(73.,min(99.,target))
    target=old+min(1.,max(0.,(280-z)/12.))*(target-old)
    mapped=radius*target/old if radius<=old else target+(radius-old)*(LIMIT-target)/(LIMIT-old)
    return round(x*mapped/radius,5),round(y*mapped/radius,5),z


def core_uv(mesh):
    # A continuous cylindrical projection avoids stretched per-Voronoi-face
    # texture islands on the newly normalized exterior concrete envelope.
    concrete={i for t in mesh['triangles'] if t[3]==2 for i in t[:3]}
    for i in concrete:
        x,y,z=mesh['vertices'][i]
        mesh['uvs'][i]=[math.atan2(x,y)*108/1000,(z+900)/1000]
    duplicates={}
    for triangle in mesh['triangles']:
        if triangle[3]!=2:
            continue
        us=[mesh['uvs'][i][0] for i in triangle[:3]]
        if max(us)-min(us)<math.pi*108/1000:
            continue
        for k,i in enumerate(triangle[:3]):
            if mesh['uvs'][i][0]>=0:
                continue
            if i not in duplicates:
                duplicates[i]=len(mesh['vertices'])
                for field in ('vertices','normals','uvs'):
                    mesh[field].append(list(mesh[field][i]))
                mesh['uvs'][-1][0]+=2*math.pi*108/1000
            triangle[k]=duplicates[i]


def main():
    global ATLAS
    paths=[SOURCE/(name+'11.json') for name in ('column','collision','design')]
    assert not any(p.exists() for p in paths)
    source=json.loads((SOURCE/'column10.json').read_text())
    collision=json.loads((SOURCE/'collision10.json').read_text())
    design=json.loads((SOURCE/'design10.json').read_text())
    ATLAS=build_atlas(source['core'])
    shape.transform=transform
    for ordinal,(mesh,offset) in enumerate([(source['core'],900)]+[(m,0) for m in source['pieces']]):
        old_vertices,old_normals=mesh['vertices'],mesh['normals']
        shape.transform_mesh(mesh,offset)
        for i,(a,b) in enumerate(zip(old_vertices,mesh['vertices'])):
            if a==b:
                mesh['normals'][i]=old_normals[i]
        if ordinal%80==0:
            print('Profiled geometry',ordinal,flush=True)
    smooth_core_concrete(source['core'])
    core_uv(source['core'])
    for leaf in collision['leaves'][:644]:
        for i,p in enumerate(leaf):
            leaf[i]=transform(tuple(p))
    tree=ast.parse((ROOT/'Scripts/ReinforcedColumn01/check_progression.py').read_text())
    context=dict(math=math,source=source,core_bins={})
    module=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='crossings'],type_ignores=[])
    exec(compile(module,'core-intersection','exec'),context)
    crossings=context['crossings'];records=[]
    for i,old_anchor in enumerate(source['anchors']):
        center=transform(g.mean(sorted(set(tuple(p) for p in old_anchor['vertices']))))
        for attempt in range(25):
            x,y,z=center[0]*(.96**attempt),center[1]*(.96**attempt),center[2]
            anchor=g.empty()
            for _,poly in g.box(x-.4,x+.4,y-.4,y+.4,z-.4,z+.4):
                g.append(anchor,g.surface(poly,2,rough=False))
            clearances=[]
            for p in set(tuple(p) for p in anchor['vertices']):
                hits=crossings(source['core'],0,1,p[1],p[2],900,240)
                if len(hits)<2 or len(hits)%2:
                    break
                clearance=max(min(120-p[0]-a,b-(120-p[0])) for a,b in zip(hits[::2],hits[1::2]))
                if clearance<=.15:
                    break
                clearances.append(clearance)
            else:
                break
        else:
            raise AssertionError(('Anchor placement',i))
        source['anchors'][i]=anchor
        collision['leaves'][644+i]=sorted(set(tuple(p) for p in anchor['vertices']))
        records.append(dict(anchor=i,center=[x,y,z],inward_steps=attempt,min_x_clearance_cm=min(clearances)))
    for row in design['piece_meta']:
        row['seed']=transform(tuple(row['seed']))
    silhouettes=[]
    for i,piece in enumerate(source['pieces']):
        axis=0 if design['piece_meta'][i]['side']%2==0 else 1
        p=piece['vertices']
        width=max(v[axis] for v in p)-min(v[axis] for v in p)
        height=max(v[2] for v in p)-min(v[2] for v in p)
        silhouettes.append(dict(piece=i,width_cm=width,height_cm=height,aspect=max(width,height)/min(width,height)))
    design.update(revision='11',source_revision='10',previous_revision='10',
        geometry_operation=design['geometry_operation']+'; normalize coarse radial core profile to 86 cm plus irregular concrete relief',
        core_profile_grid=[4,NZ+1,NX+1],target_core_radius_cm='clamp(86 + 10*N34 + 6*N13 + 2*N5.5,73,99)',
        anchors_rebuilt=records,silhouettes=silhouettes,core_uv='Continuous cylindrical concrete projection; rear seam unwrapped per triangle')
    for path,data in zip(paths,(source,collision,design)):
        path.write_text(json.dumps(data,indent=2) if path==paths[2] else json.dumps(data,separators=(',',':')),encoding='utf-8')
    (SOURCE/'profile11.json').write_text(json.dumps(ATLAS,separators=(',',':')),encoding='utf-8')
    print(json.dumps(dict(revision='11',bodies=len(source['pieces']),anchors=len(source['anchors']),
        min_anchor_x_clearance_cm=min(r['min_x_clearance_cm'] for r in records),
        widths_cm=[min(r['width_cm'] for r in silhouettes),max(r['width_cm'] for r in silhouettes)],
        heights_cm=[min(r['height_cm'] for r in silhouettes),max(r['height_cm'] for r in silhouettes)],
        compact=sum(r['aspect']<1.5 for r in silhouettes),elongated=sum(r['aspect']>2 for r in silhouettes))),flush=True)


if __name__=='__main__':
    main()
