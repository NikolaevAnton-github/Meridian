import json, random, math
from pathlib import Path

OUT=Path('D:/devgames/MeridianSquad/Saved/DemoTiledColumn01/Correction02')
SX=2.364; SZ=3.6
meshes=[]; layouts={}; tiles=[]
for height,rows in [(240,4),(120,2)]:
    for variant in range(4):
        rng=random.Random(9260200+height+variant)
        grid=[]
        for r in range(rows+1):
            line=[]
            for c in range(4):
                y=.25 if c==0 else 119.75 if c==3 else c*40+rng.uniform(-5,5)
                z=.25 if r==0 else height-.25 if r==rows else r*60+rng.uniform(-8,8)
                line.append((y,z))
            grid.append(line)
        layout=[]
        for r in range(rows):
            for c in range(3):
                poly=[grid[r][c],grid[r][c+1],grid[r+1][c+1],grid[r+1][c]]
                cy=sum(p[0] for p in poly)/4; cz=sum(p[1] for p in poly)/4
                poly=[(cy+(y-cy)*.99998,cz+(z-cz)*.99998) for y,z in poly]
                vertices=[[x/SX,(y-cy)/SX,(z-cz)/SZ] for x in [.9,-.9] for y,z in poly]
                uvs=[[y/240,z/240] for x in range(2) for y,z in poly]
                triangles=[[0,1,2,0],[0,2,3,0],[4,6,5,1],[4,7,6,1]]
                for i in range(4):
                    j=(i+1)%4
                    triangles.extend([[i,i+4,j+4,1],[i,j+4,j,1]])
                layout.append((len(meshes),cy,cz))
                meshes.append(dict(vertices=vertices,triangles=triangles,uvs=uvs))
        layouts[height,variant]=layout

def rotated(x,y,z,face):
    return [[x,y,z],[-y,x,z],[-x,-y,z],[y,-x,z]][face]

for face in range(4):
    for row in range(8):
        for col in range(2):
            height=120 if row==7 else 240
            variant=(face+row+col)%4
            for mesh,cy,cz in layouts[height,variant]:
                y=(-120+120*col+cy)/SX; z=(240*row+cz)/SZ
                tiles.append(dict(mesh=mesh,position=rotated(119.1/SX,y,z,face),yaw=90*face,
                    sample=rotated(50,y,z,face),bonded=((len(tiles)+row+face)%3==0)))

dest='/Game/Experiments/DemoTiledColumn01/Correction02/'
source=dict(meshes=meshes,tiles=tiles,materials=[dest+'M_StoneUV02','/Game/ReinforcedColumn01/M_RC01_StoneEdge',
    '/Game/ReinforcedColumn01/M_RC01_StoneEdge','/Game/ReinforcedColumn01/M_RC01_StoneEdge'])
(OUT/'cladding.json').write_text(json.dumps(source),encoding='utf-8')
print(json.dumps(dict(mesh_variants=len(meshes),tiles=len(tiles),size_cm=[240,240,1800])))
