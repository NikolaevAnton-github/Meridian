"""Deterministic editable meshes for the existing 240 cm lobby column.

No external packages. Voronoi cells carry an actual 1.8 cm stone edge and concrete
backing. The persistent core is their complementary rough surface, not a box.
"""
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'Assets/Source/ReinforcedColumn01'
RNG = random.Random(15401)
WIDTH, HEIGHT, HALF, SKIN = 240., 280., 120., 1.8

def mesh():
    return dict(vertices=[], triangles=[])

def sub(a,b): return [x-y for x,y in zip(a,b)]
def cross(a,b): return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
def dot(a,b): return sum(x*y for x,y in zip(a,b))

def tri(m, a,b,c, material, normal=None):
    if normal and dot(cross(sub(b,a),sub(c,a)),normal)<0: b,c=c,b
    if dot(cross(sub(b,a),sub(c,a)),cross(sub(b,a),sub(c,a)))<1e-10: return
    n=len(m['vertices'])
    m['vertices'].extend([list(a),list(b),list(c)])
    m['triangles'].append([n,n+1,n+2,material])

def quad(m,a,b,c,d,material,normal=None):
    tri(m,a,b,c,material,normal)
    tri(m,a,c,d,material,normal)

def clip(poly,nx,ny,d):
    out=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        da=nx*a[0]+ny*a[1]-d
        db=nx*b[0]+ny*b[1]-d
        if da<=1e-7: out.append(a)
        if (da<0)!=(db<0):
            t=da/(da-db)
            out.append([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])])
    return out

def map_point(side,p,depth=0):
    t,z=p
    # Radial inset gives matching mitred corner volumes on all four sides.
    x=t-HALF
    if abs(x)>80:
        x=math.copysign(80+(abs(x)-80)*(1-depth/40),x)
    y=HALF-depth
    for _ in range(side): x,y=-y,x
    return [x,y,z]

core, steel, pieces, anchors = mesh(),mesh(),[],[]
piece_meta=[]
for side in range(4):
    seeds=[[30*(x+.5)+RNG.uniform(-9,9),HEIGHT/9*(z+.5)+RNG.uniform(-9,9)] for x in range(8) for z in range(9)]
    cells=[]
    for i,p in enumerate(seeds):
        poly=[[0,0],[WIDTH,0],[WIDTH,HEIGHT],[0,HEIGHT]]
        for q in seeds:
            if p==q: continue
            poly=clip(poly,q[0]-p[0],q[1]-p[1],(dot(q,q)-dot(p,p))/2)
            if not poly: break
        poly=[[round(x,5),round(y,5)] for x,y in poly]
        shallow=RNG.random()<.16 and all(40<x<WIDTH-40 and .01<y<HEIGHT-.01 for x,y in poly)
        cells.append((p,poly,shallow))
    depths={}
    for _,poly,_ in cells:
        for x,z in poly:
            key=(x,z)
            if key not in depths: depths[key]=12. if min(x,WIDTH-x)<40.01 or min(z,HEIGHT-z)<.01 else RNG.uniform(8.,17.)
    for _,poly,shallow in cells:
        if shallow:
            for p in poly: depths[tuple(p)]=SKIN
    outward=map_point(side,[120,0],0)
    outward[2]=0
    tangent=sub(map_point(side,[121,0]),map_point(side,[120,0]))
    for p,poly,shallow in cells:
        chunk=mesh()
        center_depth=SKIN if shallow else RNG.uniform(18.,29.)
        oc=map_point(side,p)
        ic=map_point(side,p,center_depth)
        # Keep the back fan's projected centre inside its polygon, including corners.
        inner_points=[map_point(side,q,depths[tuple(q)]) for q in poly]
        if side%2==0: ic[0]=sum(q[0] for q in inner_points)/len(poly)
        else: ic[1]=sum(q[1] for q in inner_points)/len(poly)
        ic[2]=sum(q[2] for q in inner_points)/len(poly)
        for a,b in zip(poly,poly[1:]+poly[:1]):
            oa,ob=map_point(side,a),map_point(side,b)
            ia,ib=map_point(side,a,depths[tuple(a)]),map_point(side,b,depths[tuple(b)])
            sa,sb=map_point(side,a,SKIN),map_point(side,b,SKIN)
            tri(chunk,oc,oa,ob,0,outward)
            tri(chunk,ic,ib,ia,1 if shallow else 2,[-v for v in outward])
            # The side normal follows the cell edge in its unfolded face.
            edge=[b[1]-a[1],a[0]-b[0]]
            n=[tangent[0]*edge[0],tangent[1]*edge[0],edge[1]]
            # Adjacent cells must choose the same diagonal on nonplanar walls.
            if tuple(a)<tuple(b):
                quad(chunk,oa,sa,sb,ob,1,n)
                quad(chunk,sa,ia,ib,sb,2,n)
            else:
                quad(chunk,ob,sb,sa,oa,1,n)
                quad(chunk,sb,ib,ia,sa,2,n)
            tri(core,ic,ia,ib,2,outward)
            if abs(a[1])<.01 and abs(b[1])<.01:
                tri(core,[0,0,0],ib,ia,2,[0,0,-1])
            if abs(a[1]-HEIGHT)<.01 and abs(b[1]-HEIGHT)<.01:
                quad(core,ia,ib,ob,oa,2,[0,0,-1])
        pieces.append(chunk)
        # A small fixed bond face lives inside the permanent core. Its coplanar
        # contact keeps an untouched shard supported after neighbouring loss.
        q0=inner_points[0]
        q1=inner_points[1]
        face=[ic,q0,q1]
        center=[sum(q[j] for q in face)/3 for j in range(3)]
        contact=[[center[j]+.35*(q[j]-center[j]) for j in range(3)] for q in face]
        apex=[center[j]-outward[j]/120*2 for j in range(3)]
        av=contact+[apex]
        centroid=[sum(q[j] for q in av)/4 for j in range(3)]
        anchor=mesh()
        for indices in [(0,1,2),(0,3,1),(1,3,2),(2,3,0)]:
            aa,bb,cc=[av[k] for k in indices]
            normal=sub([sum(q[j] for q in [aa,bb,cc])/3 for j in range(3)],centroid)
            tri(anchor,aa,bb,cc,2,normal)
        anchors.append(anchor)
        piece_meta.append(dict(side=side, center=p, depth_cm=center_depth, shallow=shallow))
    # Original outer dimensions and world-position material above the affected band.
    quad(core,map_point(side,[0,HEIGHT]),map_point(side,[WIDTH,HEIGHT]),map_point(side,[WIDTH,1800]),map_point(side,[0,1800]),0,outward)
quad(core,[-120,-120,1800],[120,-120,1800],[120,120,1800],[-120,120,1800],0,[0,0,1])
# Preserve the selected existing actor's original 900 cm pivot and transform.
for p in core['vertices']: p[2]-=900.

def tube(points,radii,sides=8):
    rings=[]
    for i,p in enumerate(points):
        direction=sub(points[min(i+1,len(points)-1)],points[max(0,i-1)])
        length=math.sqrt(dot(direction,direction))
        direction=[x/length for x in direction]
        basis=cross(direction,[0,0,1] if abs(direction[2])<.9 else [0,1,0])
        length=math.sqrt(dot(basis,basis))
        basis=[x/length for x in basis]
        other=cross(direction,basis)
        r=radii[i] if isinstance(radii,list) else radii
        rings.append([[p[j]+r*(math.cos(k*2*math.pi/sides)*basis[j]+math.sin(k*2*math.pi/sides)*other[j]) for j in range(3)] for k in range(sides)])
    for i in range(len(rings)-1):
        for k in range(sides):
            kn=(k+1)%sides
            radial=sub(rings[i][k],points[i])
            quad(steel,rings[i][k],rings[i+1][k],rings[i+1][kn],rings[i][kn],3,radial)
    for i,sgn in [(0,-1),(-1,1)]:
        n=sub(points[1],points[0]) if i==0 else sub(points[-1],points[-2])
        for k in range(sides): tri(steel,points[i],rings[i][k],rings[i][(k+1)%sides],3,[sgn*x for x in n])

bars=set()
for i in range(8):
    t=round(-110.8+221.6*i/7,5)
    bars.update([(t,-110.8),(t,110.8),(-110.8,t),(110.8,t)])
for x,y in sorted(bars):
    pts=[]; radii=[]
    for z in range(-40,341,4):
        for dz,r in [(0,1.4),(.6,1.54),(1.2,1.4)]:
            pts.append([x,y,z+dz]); radii.append(r)
    tube(pts,radii)
for z in range(10,311,20):
    pts=[]
    for sx,sy,start in [(1,1,0),(-1,1,90),(-1,-1,180),(1,-1,270)]:
        for i in range(7):
            a=math.radians(start+i*15)
            pts.append([sx*108.6+4.2*math.cos(a),sy*108.6+4.2*math.sin(a),float(z)])
    pts.append(pts[0]); tube(pts,.6)
    # Closed perimeter ties plus internal cross-links at alternating levels.
    for t in [-47.4857,47.4857]:
        tube([[-110.8,t,z],[110.8,t,z],[107.8,t-3.,z]],.6)
        tube([[t,-110.8,z],[t,110.8,z],[t-3.,107.8,z]],.6)

source=dict(schema=1, seed=15401, units='centimetres', materials=[
    '/Game/ReinforcedColumn01/MI_RC01_Cladding',
    '/Game/ReinforcedColumn01/M_RC01_StoneEdge',
    '/Game/NextGenDestruction/Materials/Instances/MI_ConcreteInner_5m',
    '/Game/NextGenDestruction/Materials/Instances/MI_Steel_Rebar_5mDirty'],
    core=core,steel=steel,pieces=pieces,anchors=anchors)
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'column.json').write_text(json.dumps(source,separators=(',',':')),encoding='utf-8')
record=dict(actor='StaticMeshActor_35',label='FB01_newNcolumnNN12p6NN2p4',location=[-1260,-240,900],outer_cm=[240,240,1800],affected_height_cm=[0,280],stone_thickness_cm=SKIN,
    longitudinal_bars=len(bars),longitudinal_diameter_cm=2.8,longitudinal_axis_offset_cm=110.8,longitudinal_spacing_cm=221.6/7,
    tie_diameter_cm=1.2,tie_spacing_cm=20,minimum_cover_to_tie_cm=118.2-113.4,bar_embed_below_cm=40,bar_embed_above_band_cm=61.2,
    pieces=len(pieces),fixed_bond_anchors=len(anchors),shallow_pieces=sum(p['shallow'] for p in piece_meta),piece_meta=piece_meta,
    core_triangles=len(core['triangles']),steel_triangles=len(steel['triangles']))
(OUT/'design.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k!='piece_meta'}))
