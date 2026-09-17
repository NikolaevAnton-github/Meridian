"""Locate the few source-degenerate faces without modifying the source."""
import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Saved/PlayerCharacter01/MeshUsability01/Worker'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Assets/Source/PlayerCharacter01/MeshUsability01/Datum16_Bind05.blend'))
o=bpy.data.objects['Revision02_Untouched'];m=o.data;m.calc_loop_triangles()
g=json.loads((OUT/'Revision02/geometry.json').read_text())['meshes'][0];rows=[]
for index in g['degenerate_faces']:
    p=m.polygons[index];co=sum((o.matrix_world@m.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
    region='boots_ankles' if co.z<.9399414*.145 else 'hands_cuffs' if abs(co.x)>.38 else 'head_collar' if co.z>.9399414*.84 else 'torso_trousers'
    rows.append(dict(face=index,vertices=list(p.vertices),center_source_world=list(co),region=region,area=p.area))
(OUT/'source-degenerate-locations.json').write_text(json.dumps(dict(faces=rows,degenerate_triangles=g['degenerate_loop_triangles']),indent=2)+'\n')
print(json.dumps(rows))
