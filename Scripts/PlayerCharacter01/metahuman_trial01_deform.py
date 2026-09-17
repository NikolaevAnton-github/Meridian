"""Static skinning probes on the actual A-pose FBX, without a corrective rig."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'Assets/Source/PlayerCharacter01/MetaHumanTrial01'
OUT=ROOT/'Saved/PlayerCharacter01/MetaHumanTrial01/Worker/Deformation03'
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Solve02/Datum16_APose02_Inspection.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
mesh=next(o for o in bpy.data.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers))
scene=bpy.context.scene
cam=scene.camera
for o in bpy.data.objects:
    if o.type=='MESH':o.hide_render=o!=mesh
mesh.hide_set(False)
for b in rig.pose.bones:b.rotation_mode='QUATERNION'
results=[]

def update():bpy.context.view_layer.update()
def reset():
    for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
    update()
def rotate(name,axis,degrees):
    b=rig.pose.bones[name]
    origin=b.head.copy()
    b.matrix=Matrix.Translation(origin)@Matrix.Rotation(math.radians(degrees),4,Vector(axis).normalized())@Matrix.Translation(-origin)@b.matrix
    update()
def aim(name,end,direction):
    b=rig.pose.bones[name];origin=b.head.copy()
    current=(rig.pose.bones[end].head-origin).normalized()
    rotation=current.rotation_difference(Vector(direction).normalized()).to_matrix().to_4x4()
    b.matrix=Matrix.Translation(origin)@rotation@Matrix.Translation(-origin)@b.matrix
    update()
def curl(side,digit):
    sign=1 if side=='l' else -1
    pb=rig.pose.bones
    across=pb['pinky_01_'+side].head-pb['index_01_'+side].head
    length=pb['middle_03_'+side].head-pb['middle_01_'+side].head
    palm=sign*across.cross(length).normalized()
    along=pb[digit+'_03_'+side].head-pb[digit+'_01_'+side].head
    axis=along.cross(palm).normalized()
    for index,angle in [(1,35),(2,50),(3,25)]:rotate(f'{digit}_{index:02}_{side}',axis,angle)
def vertices():
    evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
    return [evaluated.matrix_world@v.co for v in evaluated.data.vertices]
def render(name,target,direction,scale):
    target=Vector(target);direction=Vector(direction).normalized()
    cam.location=target+direction*6
    cam.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=scale
    scene.render.filepath=str(OUT/(name+'.png'))
    bpy.ops.render.render(write_still=True)
def hand_view(name,side):
    pb=rig.pose.bones
    hand=rig.matrix_world@pb['hand_'+side].head
    tip=rig.matrix_world@pb['middle_03_'+side].head
    across=pb['pinky_01_'+side].head-pb['index_01_'+side].head
    along=pb['middle_03_'+side].head-pb['middle_01_'+side].head
    palm=(1 if side=='l' else -1)*across.cross(along).normalized()
    for suffix,direction in [('palm',palm),('dorsal',-palm),('oblique',-palm+along.normalized()*.5)]:
        render(name+'-'+suffix,(hand+tip)/2,direction,.32)

reset()
rest=vertices()
rest_feet=sum(rig.pose.bones['foot_'+s].head.z for s in ('l','r'))/2
probes=['rest','arm_raise','cross_body','elbow_twist','deep_crouch','ankle_flex']
probes += [side+'_'+digit for side in ('l','r') for digit in ('thumb','index','middle','ring','pinky')]
for frame,name in enumerate(probes,1):
    scene.frame_set(frame)
    reset()
    if name=='arm_raise':
        rotate('upperarm_l',(0,1,0),-115);rotate('upperarm_r',(0,1,0),115)
    elif name=='cross_body':
        aim('upperarm_l','lowerarm_l',(-.5,-1,.1))
        aim('lowerarm_l','hand_l',(-.9,-.1,.2))
    elif name=='elbow_twist':
        aim('lowerarm_l','hand_l',(0,-1,.2))
        axis=rig.pose.bones['hand_l'].head-rig.pose.bones['lowerarm_l'].head
        rotate('lowerarm_l',axis,80)
    elif name=='deep_crouch':
        for side in ('l','r'):
            rotate('thigh_'+side,(1,0,0),-105)
            rotate('calf_'+side,(1,0,0),140)
            rotate('foot_'+side,(1,0,0),-35)
        pelvis=rig.pose.bones['pelvis'];matrix=pelvis.matrix.copy()
        matrix.translation.z += rest_feet-sum(rig.pose.bones['foot_'+s].head.z for s in ('l','r'))/2
        pelvis.matrix=matrix;update()
    elif name=='ankle_flex':
        rotate('foot_l',(1,0,0),25);rotate('foot_r',(1,0,0),-20)
    elif name[0:2] in ('l_','r_'):curl(*name.split('_'))
    current=vertices()
    displacement=[(a-b).length for a,b in zip(current,rest)]
    row=dict(name=name,frame=frame,moved_vertices_over_0_1mm=sum(v>.0001 for v in displacement),
        maximum_displacement_m=max(displacement),bounds_m=dict(min=[min(v[i] for v in current) for i in range(3)],max=[max(v[i] for v in current) for i in range(3)]),
        pose_basis={b.name:dict(location=list(b.location),rotation_quaternion=list(b.rotation_quaternion),scale=list(b.scale)) for b in rig.pose.bones if not b.matrix_basis.is_identity})
    # Render reevaluates the scene frame. Persist this pose first so an earlier
    # frame's animation keys cannot reset it during render dependency updates.
    for b in rig.pose.bones:
        b.keyframe_insert('location',frame=frame)
        b.keyframe_insert('rotation_quaternion',frame=frame)
        b.keyframe_insert('scale',frame=frame)
    if name[0:2] in ('l_','r_'):
        side,digit=name.split('_')
        row['other_digit_max_displacement_m']={}
        for other in ('thumb','index','middle','ring','pinky'):
            groups={g.index for g in mesh.vertex_groups if g.name.startswith(other+'_') and g.name.endswith('_'+side)}
            ids=[v.index for v in mesh.data.vertices if any(g.group in groups and g.weight>.5 for g in v.groups)]
            row['other_digit_max_displacement_m'][other]=max((displacement[i] for i in ids),default=0)
        hand_view(name,side)
    else:
        render(name+'-front',(0,0,.85),(0,-1,0),2.1)
        render(name+'-side',(0,0,.85),(1,0,0),2.1)
        render(name+'-oblique',(0,0,.85),(1,-1,.3),2.1)
        if name in ('arm_raise','cross_body','elbow_twist'):render(name+'-joint',(0,0,1.38),(1,-1,.35),1.)
        if name=='deep_crouch':render(name+'-joint',(0,-.2,.55),(1,-1,.3),1.1)
        if name=='ankle_flex':render(name+'-joint',(0,0,.16),(1,-1,.1),.62)
        if name=='rest':
            hand_view('rest-l','l');hand_view('rest-r','r')
    results.append(row)
scene.frame_start=1;scene.frame_end=len(probes);scene.frame_set(1)
if rig.animation_data and rig.animation_data.action:rig.animation_data.action.name='MHTrial01_StaticSkinningProbes'
data=dict(input='Solve02/APose/MH_Datum16_Trial01_Body.fbx',mesh=mesh.name,bones=len(rig.data.bones),
    scope='Blender linear skinning of the actual exported mesh and weights. No Unreal post-process corrective rig, IK, physics, cloth, production pose authoring, or retarget acceptance.',
    probes=results)
(OUT/'probes.json').write_text(json.dumps(data,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Solve02/Datum16_APose03_Deformation.blend'))
print(json.dumps(dict(probes=len(results),output=str(OUT))))
