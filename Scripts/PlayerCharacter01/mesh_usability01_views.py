"""Matched gray/wire closeups of keyed actual-surface deformation, using existing poses."""
import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'Assets/Source/PlayerCharacter01/MeshUsability01';OUT=ROOT/'Saved/PlayerCharacter01/MeshUsability01/Worker/Detail05'
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Datum16_Bind05_DeformationFinal.blend'))
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE');mesh=bpy.data.objects['Datum16_ExistingTopology_Bind05'];cam=scene.camera
probes=json.loads((OUT.parent/'DeformationBind05Final/probes.json').read_text())['probes']
scene.render.resolution_x=scene.render.resolution_y=1000;scene.display.shading.color_type='OBJECT'
records=[]
def bone(name):return rig.matrix_world@rig.pose.bones[name].head
scene.frame_set(1);bpy.context.view_layer.update()
rest_hands={s:(bone('hand_'+s)+bone('middle_03_'+s))/2 for s in ('l','r')}
for p in probes:
    scene.frame_set(p['frame']);bpy.context.view_layer.update()
    evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());pts=[mesh.matrix_world@v.co for v in evaluated.data.vertices]
    for o in scene.objects:
        if o.type=='MESH':o.hide_render=True
    name=p['name'];views=[]
    if name=='rest' or name[:2] in ('l_','r_') or name=='wrist_flex':
        for side in (name[0],) if name[:2] in ('l_','r_') else ('l','r'):
            views.append(('hand_'+side,rest_hands[side],(.2,-1,1),.31,side))
    if name in ('rest','arm_raise','cross_body','cross_body_right'):
        for side in ('l','r'):views.append(('shoulder_'+side,bone('upperarm_'+side),(1 if side=='l' else -1,-1,.25),.55,None))
    if name in ('rest','elbow_twist','elbow_twist_right'):
        for side in ('l','r'):views.append(('elbow_'+side,bone('lowerarm_'+side),(1 if side=='l' else -1,-1,.4),.48,None))
    if name in ('rest','deep_crouch'):
        views.append(('hips',bone('pelvis'),(1,-1,.2),.65,None))
        for side in ('l','r'):views.append(('knee_'+side,bone('calf_'+side),(1 if side=='l' else -1,-1,.3),.5,None))
    if name in ('rest','ankle_flex'):
        for side in ('l','r'):views.append(('ankle_'+side,bone('foot_'+side),(1 if side=='l' else -1,-1,.2),.4,None))
    for label,target,direction,size,hand in views:
        allowed=set(range(len(pts))) if not hand else {i for i,pt in enumerate(pts) if (pt-bone('hand_'+hand)).length<.25 and (pt.x>0)==(hand=='l')}
        faces=[list(f.vertices) for f in mesh.data.polygons if all(i in allowed for i in f.vertices)]
        data=bpy.data.meshes.new('EvaluatedSurface');data.from_pydata(pts,[],faces);data.update()
        display=bpy.data.objects.new('EvaluatedSurface',data);scene.collection.objects.link(display);display.color=(.55,.55,.55,1)
        for poly,original in zip(data.polygons,[f for f in mesh.data.polygons if all(i in allowed for i in f.vertices)]):poly.use_smooth=original.use_smooth
        curve=bpy.data.curves.new('OriginalPolygonEdges','CURVE');curve.dimensions='3D';curve.resolution_u=1;curve.bevel_resolution=0;curve.bevel_depth=size*.0005
        for edge in mesh.data.edges:
            if not all(i in allowed for i in edge.vertices):continue
            spline=curve.splines.new('POLY');spline.points.add(1)
            for pt,vi in zip(spline.points,edge.vertices):pt.co=(*pts[vi],1)
        wire=bpy.data.objects.new('OriginalPolygonEdges',curve);scene.collection.objects.link(wire);wire.color=(.01,.01,.01,1)
        direction=Vector(direction).normalized();cam.location=target+direction*5;cam.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size
        for enabled in (False,True):
            wire.hide_render=not enabled;filename=name+'-'+label+('-wire' if enabled else '-gray')+'.png'
            scene.render.filepath=str(OUT/filename);bpy.ops.render.render(write_still=True)
            records.append(dict(file=filename,probe=name,frame=p['frame'],region=label,wire=enabled,target=list(target),scale_m=size,display='Actual evaluated vertices and original polygon edges; temporary recalc smooth normals; hand crop hides other surface beyond 25cm wrist radius'))
        bpy.data.objects.remove(display,do_unlink=True);bpy.data.meshes.remove(data);bpy.data.objects.remove(wire,do_unlink=True);bpy.data.curves.remove(curve)
(OUT/'views.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(dict(images=len(records))))
