"""Read the exported UV coordinates; a layer name alone is insufficient evidence."""
import bpy
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Assets/Source/PlayerCharacter01/MetaHumanTrial01/Solve02/Datum16_APose02_Inspection.blend'))
mesh=next(o.data for o in bpy.data.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers))
layers=[]
for layer in mesh.uv_layers:
    uv=[tuple(loop.uv) for loop in layer.data]
    areas=[]
    for poly in mesh.polygons:
        points=[uv[i] for i in poly.loop_indices]
        areas.append(abs(sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points))))/2)
    layers.append(dict(name=layer.name,loops=len(uv),distinct_coordinates=len(set(uv)),
        minimum=[min(p[i] for p in uv) for i in (0,1)],maximum=[max(p[i] for p in uv) for i in (0,1)],
        faces=len(areas),zero_area_faces=sum(a<1e-12 for a in areas),sum_absolute_face_area=sum(areas)))
out=ROOT/'Saved/PlayerCharacter01/MetaHumanTrial01/Worker/apose-uv-inspection.json'
out.write_text(json.dumps(dict(mesh=mesh.name,layers=layers,scope='Coordinate presence and per-face area only; no texture bake, packing/overlap acceptance, or original garment UV transfer.'),indent=2)+'\n')
print(out.read_text())
