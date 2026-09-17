"""Measure source-space digit separation without deriving labels from skin weights."""
import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Assets/Source/PlayerCharacter01/MeshUsability01/Datum16_Bind01.blend'))
o=bpy.data.objects['Revision02_Untouched'];pts=[o.matrix_world@v.co for v in o.data.vertices]
adj=[[] for _ in pts]
for e in o.data.edges:
    a,b=e.vertices;adj[a].append(b);adj[b].append(a)
result={}
for threshold in [.435,.445,.45,.455,.46,.47]:
    remaining={i for i,p in enumerate(pts) if p.x>threshold};comps=[]
    while remaining:
        stack=[remaining.pop()];ids=[]
        while stack:
            i=stack.pop();ids.append(i)
            for j in adj[i]:
                if j in remaining:remaining.remove(j);stack.append(j)
        if len(ids)>8:comps.append(dict(n=len(ids),min=[min(pts[i][a] for i in ids) for a in range(3)],max=[max(pts[i][a] for i in ids) for a in range(3)],mean=[sum(pts[i][a] for i in ids)/len(ids) for a in range(3)]))
    result[str(threshold)]=comps
(ROOT/'Saved/PlayerCharacter01/MeshUsability01/Worker/hand-source-components.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
