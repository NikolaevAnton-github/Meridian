import json, math, random
from pathlib import Path

OUT=Path('D:/devgames/MeridianSquad/Saved/DemoTiledColumn01')
rng=random.Random(260926)
sx=240/104
sz=3.6
pieces=[]

def mesh_for(poly, face, mode, sample):
    vertices=[]; triangles=[]
    def point(q, depth):
        a,z=q
        if face==0: return [depth/sx,a/sx,z/sz]
        if face==1: return [-depth/sx,-a/sx,z/sz]
        if face==2: return [-a/sx,depth/sx,z/sz]
        return [a/sx,-depth/sx,z/sz]
    def prism(front, back, frontmat, sidemat):
        base=len(vertices); n=len(poly)
        vertices.extend(point(p, front) for p in poly)
        vertices.extend(point(p, back[i] if isinstance(back,list) else back) for i,p in enumerate(poly))
        # The polygon is counterclockwise in the a,z plane; side frame is right-handed.
        for i in range(1,n-1):
            triangles.append([base,base+i,base+i+1,frontmat])
            triangles.append([base+n,base+n+i+1,base+n+i,sidemat])
        for i in range(n):
            j=(i+1)%n
            triangles.extend([[base+i,base+n+i,base+n+j,sidemat],[base+i,base+n+j,base+j,sidemat]])
    prism(120,118.2,2,3)
    if mode in (1,2,3):
        depth=.7 if mode==1 else 2.65
        prism(118.2,[118.2-depth*rng.uniform(.65,1) for _ in poly],1,1)
    return dict(vertices=vertices,triangles=triangles,mode=mode,sample=sample)

for face in range(4):
    for row in range(8):
        z0=row*240+.25; z1=min(1800,(row+1)*240)-.25
        for col in range(2):
            a0=-120+col*120+.25; a1=a0+119.5
            ac=(a0+a1)/2+rng.uniform(-13,13)
            zc=(z0+z1)/2+rng.uniform(-.12,.12)*(z1-z0)
            ring=[(a0,z0),((a0+a1)/2,z0),(a1,z0),(a1,(z0+z1)/2),
                  (a1,z1),((a0+a1)/2,z1),(a0,z1),(a0,(z0+z1)/2)]
            for i in range(8):
                poly=[(ac,zc),ring[i],ring[(i+1)%8]]
                # Shift tiny fracture seams inward; slab joints remain the existing 5 mm pattern.
                ca=sum(p[0] for p in poly)/3; cz=sum(p[1] for p in poly)/3
                poly=[(ca+(a-ca)*.9998,cz+(z-cz)*.9998) for a,z in poly]
                if face==0: sample=[50,ca/sx,cz/sz]
                elif face==1: sample=[-50,-ca/sx,cz/sz]
                elif face==2: sample=[-ca/sx,50,cz/sz]
                else: sample=[ca/sx,-50,cz/sz]
                mode=(i+row+col+face)%4
                pieces.append(mesh_for(poly,face,mode,sample))

(OUT/'tiles.json').write_text(json.dumps(dict(pieces=pieces)),encoding='utf-8')
print(json.dumps(dict(tile_fragments=len(pieces),outer_size_cm=[240,240,1800],actor_scale=[sx,sx,sz])))
