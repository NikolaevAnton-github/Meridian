"""Unoccluded hand views of retained Deformation03 frames; no new poses."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/PlayerCharacter01/MetaHumanTrial01/Worker/Deformation03/Hands04'
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Assets/Source/PlayerCharacter01/MetaHumanTrial01/Solve02/Datum16_APose03_Deformation.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
mesh=next(o for o in bpy.data.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers))
scene=bpy.context.scene;cam=scene.camera
scene.frame_set(1);bpy.context.view_layer.update()
fixed_views={}
for side in ('l','r'):
    pb=rig.pose.bones
    hand=rig.matrix_world@pb['hand_'+side].head
    tip=rig.matrix_world@pb['middle_03_'+side].head
    across=pb['pinky_01_'+side].head-pb['index_01_'+side].head
    along=pb['middle_03_'+side].head-pb['middle_01_'+side].head
    fixed_views[side]=dict(target=(hand+tip)/2,palm=(1 if side=='l' else -1)*across.cross(along).normalized(),along=along.normalized())
records=[]
data=json.loads((OUT.parent/'probes.json').read_text())
requests=[('rest_l',1,'l'),('rest_r',1,'r')]+[(p['name'],p['frame'],p['name'][0]) for p in data['probes'] if p['name'][:2] in ('l_','r_')]
for name,frame,side in requests:
    scene.frame_set(frame);bpy.context.view_layer.update()
    pb=rig.pose.bones
    hand=rig.matrix_world@pb['hand_'+side].head
    tip=rig.matrix_world@pb['middle_03_'+side].head
    evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
    coordinates=[evaluated.matrix_world@v.co for v in evaluated.data.vertices]
    ids={i for i,p in enumerate(coordinates) if (p-hand).length<.25}
    remap={old:new for new,old in enumerate(sorted(ids))}
    polygons=[[remap[i] for i in face.vertices] for face in evaluated.data.polygons if all(i in ids for i in face.vertices)]
    crop=bpy.data.meshes.new('HandViewSnapshot')
    crop.from_pydata([coordinates[i] for i in sorted(ids)],[],polygons);crop.update()
    for p in crop.polygons:p.use_smooth=True
    obj=bpy.data.objects.new('HandViewSnapshot',crop);scene.collection.objects.link(obj)
    for o in bpy.data.objects:
        if o.type=='MESH':o.hide_render=o!=obj
    palm=fixed_views[side]['palm'];along=fixed_views[side]['along']
    for suffix,direction in [('palm',palm),('dorsal',-palm),('oblique',-palm+along*.5)]:
        direction=direction.normalized();target=fixed_views[side]['target']
        cam.location=target+direction*6
        cam.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
        cam.data.ortho_scale=.32
        scene.render.filepath=str(OUT/(name+'-'+suffix+'.png'))
        bpy.ops.render.render(write_still=True)
    records.append(dict(name=name,frame=frame,side=side,vertices=len(crop.vertices),faces=len(crop.polygons)))
    bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(crop)
(OUT/'views.json').write_text(json.dumps(dict(method='Exact evaluated skin surface cropped to a 25 cm radius around the tested wrist; body and opposite hand omitted only from these views. Cameras fixed from rest-hand landmarks so middle-finger flex cannot move the view.',views=records),indent=2)+'\n')
