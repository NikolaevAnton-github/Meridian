"""Derive the 840 cm boundary tiles and static upper/floor geometry from sources."""
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/LobbyColumns01'
spec = importlib.util.spec_from_file_location('facing04', ROOT/'Assets/Source/DemoTiledColumn01/Correction04/generate.py')
facing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(facing)
source = json.loads((ROOT/'Assets/Source/DemoTiledColumn01/Correction04/cladding.json').read_text())
layout = json.loads((ROOT/'Assets/Source/LobbyColumns01/layout.json').read_text())
DEST = '/Game/OpeningLobby/LobbyColumns01/'
CONCRETE = '/Game/NextGenDestruction/Materials/Instances/MI_ConcreteInner_5m'
meshes, tiles = [], []

def blank():
    return dict(vertices=[], triangles=[], uvs=[])

def append(target, mesh, translation=(0, 0, 0), yaw=0):
    start = len(target['vertices'])
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    target['vertices'] += [[c*x-s*y+translation[0], s*x+c*y+translation[1], z+translation[2]] for x,y,z in mesh['vertices']]
    target['triangles'] += [[a+start,b+start,c+start,m] for a,b,c,m in mesh['triangles']]
    target['uvs'] += mesh['uvs']

def box(target, lo, hi, material=0, top_material=None):
    x,y,z=lo; X,Y,Z=hi
    vertices=[[x,y,z],[X,y,z],[X,Y,z],[x,Y,z],[x,y,Z],[X,y,Z],[X,Y,Z],[x,Y,Z]]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    for face,(a,b,c,d) in enumerate(faces):
        points=[vertices[v] for v in (a,b,c,d)]
        uv=[[p[0]/240,p[1]/240] if face<2 else [p[0 if face in (2,4) else 1]/240,p[2]/240] for p in points]
        append(target,dict(vertices=points,uvs=uv,triangles=[[0,1,2,top_material if face==1 and top_material is not None else material],[0,2,3,top_material if face==1 and top_material is not None else material]]))

def record(name, geometry, materials, convex=False):
    meshes.append(dict(name=name,geometry=geometry,materials=materials,convex=convex))
    return DEST+name

def trimmed(poly, original):
    geometry,dy,dz=facing.make_mesh(poly,'height_boundary')
    # Keep the accepted tile's texture coordinates after recentering the crop.
    offset=[original['uvs'][0][i]-original['vertices'][0][i+1]/240 for i in range(2)]
    for uv in geometry['uvs']:
        uv[0]+=offset[0]; uv[1]+=offset[1]
    return geometry,dy,dz

upper=blank()
box(upper,[-118.2,-118.2,840],[118.2,118.2,1800],3)
for index,tile in enumerate(source['tiles']):
    original=source['meshes'][tile['mesh']]
    polygon=[(v[1],v[2]) for v in original['vertices'] if v[0]>0]
    bottom=min(v[1] for v in polygon)+tile['position'][2]
    top=max(v[1] for v in polygon)+tile['position'][2]
    cutoff=840-tile['position'][2]
    if bottom >= 840:
        append(upper,original,tile['position'],tile['yaw'])
        continue
    if top <= 840:
        tiles.append(dict(index=index))
        continue
    lower_poly=facing.clip(polygon,0,1,cutoff)
    geometry,dy,dz=trimmed(lower_poly,original)
    path=record(f'Tiles/SM_Boundary_{index:04}',geometry,source['materials'],True)
    entry=dict(index=index,mesh=path,offset=[0,dy,dz],area=geometry['area_cm2'],shards=[])
    if original['area_cm2']>=450:
        _,center=facing.area_centroid(polygon)
        angle=.31+(tile['mesh']%7)*.12
        for first,second in ((1,1),(1,-1),(-1,1),(-1,-1)):
            poly=lower_poly
            for sign,theta in ((first,angle),(second,angle+math.pi*.5)):
                ny,nz=sign*math.cos(theta),sign*math.sin(theta)
                poly=facing.clip(poly,ny,nz,ny*center[0]+nz*center[1]) if poly else []
            if len(poly)<3 or facing.area_centroid(poly)[0]<.01: continue
            shard,sy,sz=trimmed(poly,original)
            shard_path=record(f'Tiles/SM_Boundary_{index:04}_Shard{len(entry["shards"])}',shard,source['materials'],True)
            entry['shards'].append(dict(mesh=shard_path,offset=[0,sy-dy,sz-dz],area=shard['area_cm2']))
    tiles.append(entry)
    top_poly=facing.clip(polygon,0,-1,-cutoff)
    top_mesh,uy,uz=trimmed(top_poly,original)
    rot=facing.rotate(0,uy,uz,tile['yaw']//90)
    append(upper,top_mesh,[tile['position'][i]+rot[i] for i in range(3)],tile['yaw'])
record('SM_ColumnUpper01',upper,source['materials'][:3]+[CONCRETE])

columns=layout['columns']
assert len(columns)==16
holes=[(a['location'][0]-120,a['location'][1]-120,a['location'][0]+120,a['location'][1]+120) for a in columns]
# Derive a single floor mesh in the existing Cube's local frame, preserving the
# actor and material's world-space mapping. Column seats expose structural
# concrete at the slab datum instead of retaining the decorative finish.
xs=sorted({-3040,3040,*[x for h in holes for x in (h[0],h[2])]})
ys=sorted({-1240,1240,*[y for h in holes for y in (h[1],h[3])]})
floor=blank()
for x,X in zip(xs,xs[1:]):
    for y,Y in zip(ys,ys[1:]):
        hole=any(a<(x+X)/2<c and b<(y+Y)/2<d for a,b,c,d in holes)
        box(floor,[x/60.8,y/24.8,-50],[X/60.8,Y/24.8,50],1,1 if hole else 0)
floor_material='/Game/OpeningLobby/PainterFloor01/Materials/M_PainterFloor01_Floor'
record('SM_FloorWithColumnSeats01',floor,[floor_material,CONCRETE,CONCRETE,CONCRETE])
for sign in (-1,1):
    strip=blank(); center=sign*220
    intervals=sorted((a,c) for a,b,c,d in holes if b<center<d)
    cursor=-3000
    for lo,hi in intervals+[(3000,3000)]:
        if lo>cursor: box(strip,[cursor/60,-50,-50],[lo/60,50,50])
        cursor=max(cursor,hi)
    record(f'SM_FloorStrip_{"N" if sign<0 else "P"}01',strip,['/Game/OpeningLobby/PainterFloor01/Materials/M_PainterFloor01_Strip']*4)

result=dict(meshes=meshes,tiles=tiles,columns=columns,height_cm=840,embed_cm=30)
(OUT/'source.json').write_text(json.dumps(result),encoding='utf-8')
print(json.dumps(dict(meshes=len(meshes),lower_tiles=len(tiles),boundary_tiles=sum('mesh' in t for t in tiles),columns=len(columns))))
