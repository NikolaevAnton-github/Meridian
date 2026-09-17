"""Measure topology identity, native round trip, and source-labeled digit leakage."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'Assets/Source/PlayerCharacter01/MeshUsability01';OUT=ROOT/'Saved/PlayerCharacter01/MeshUsability01/Worker'
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Datum16_Bind05_DeformationFinal.blend'))
scene=bpy.context.scene;mesh=bpy.data.objects['Datum16_ExistingTopology_Bind05'];original=bpy.data.objects['Revision02_Untouched']
scene.frame_set(1);bpy.context.view_layer.update()
def points():return [mesh.matrix_world@v.co for v in mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices]
rest=points();source=[original.matrix_world@v.co for v in original.data.vertices]
assert len(mesh.data.vertices)==len(original.data.vertices)
assert [tuple(p.vertices) for p in mesh.data.polygons]==[tuple(p.vertices) for p in original.data.polygons]
assert [tuple(e.vertices) for e in mesh.data.edges]==[tuple(e.vertices) for e in original.data.edges]
native=json.loads((OUT/'native-geometry-Bind05.json').read_text());nativepoints=[Vector((x,-y,z)) for x,y,z in native['vertices']]
local=[p*100 for p in rest]
def nearest(a,b):
    kd=KDTree(len(b))
    for i,p in enumerate(b):kd.insert(p,i)
    kd.balance();d=sorted(kd.find(p)[2] for p in a)
    return dict(max_cm=max(d),p95_cm=d[int(len(d)*.95)],median_cm=d[len(d)//2])
labels={}
for i,p in enumerate(source):
    side='l' if p.x>0 else 'r';x=abs(p.x)
    if x>.455:
        digit='index' if p.y<.0132 else 'middle' if p.y<.029 else 'ring' if p.y<.044 else 'pinky'
        labels[i]=side+'_'+digit
    elif .435<x<.450 and p.z<.742 and p.y<0:labels[i]=side+'_thumb'
probes=json.loads((OUT/'DeformationBind05Final/probes.json').read_text())['probes'];rows=[]
for probe in probes:
    scene.frame_set(probe['frame']);bpy.context.view_layer.update();posed=points()
    d=[(a-b).length*100 for a,b in zip(posed,rest)]
    edge_ratios=[]
    for e in mesh.data.edges:
        a,b=e.vertices;base=(rest[a]-rest[b]).length
        if base>1e-7:edge_ratios.append((posed[a]-posed[b]).length/base)
    row=dict(name=probe['name'],maximum_displacement_cm=max(d),edges_stretched_over_2x=sum(v>2 for v in edge_ratios),edges_compressed_below_half=sum(v<.5 for v in edge_ratios),max_edge_stretch=max(edge_ratios),
        caveat='Edge strain is a deformation diagnostic, not attribution to topology; small pre-existing edges amplify ratios.')
    if probe['name'][:2] in ('l_','r_'):
        row['source_defined_digit_displacement_cm']={label:max(d[i] for i,x in labels.items() if x==label) for label in sorted(set(labels.values()))}
    rows.append(row)
result=dict(topology=dict(vertices=len(mesh.data.vertices),edges=len(mesh.data.edges),polygons=len(mesh.data.polygons),exact_original_vertex_order_edge_and_polygon_indices=True),native=dict(vertices=len(nativepoints),triangles=native['triangles'],blender_to_native=nearest(local,nativepoints),native_to_blender=nearest(nativepoints,local)),
    digit_label_definition='Distal source-space components beyond |X|0.455; Y bands 0.0132/0.029/0.044. Thumb |X|0.435-0.450, Z<0.742,Y<0. Labels independent of skin groups.',digit_counts={label:sum(x==label for x in labels.values()) for label in sorted(set(labels.values()))},probes=rows)
(OUT/'surface-verification-Bind05.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='probes'}))
