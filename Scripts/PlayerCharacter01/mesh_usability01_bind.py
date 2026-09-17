"""Topology-preserving T-pose fit, donor skin transfer, and inverse bind to exact A-pose."""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Matrix, Vector, Quaternion
from mathutils.kdtree import KDTree
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'Assets/Source/PlayerCharacter01/MeshUsability01'
VARIANT=next((v for v in sys.argv if v in ('Bind01','Bind02','Bind03','Bind04','Bind05')),'Bind01')
OUT=ROOT/'Saved/PlayerCharacter01/MeshUsability01/Worker'/VARIANT
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Donor/MSQ52_Manny161.blend'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
donor=next(o for o in bpy.context.scene.objects if o.type=='MESH')
corrections=[]
if VARIANT!='Bind01':
    expected=json.loads((ROOT/'Assets/Source/PlayerCharacter01/AnimationAudit01/rig-contract.json').read_text())
    actual=json.loads((OUT.parent/'inspect-Datum16_Bind01.json').read_text())
    expected={b['name']:b for b in expected['bones']};actual={b['name']:b for b in actual['bones']}
    reflect=Matrix.Diagonal((1,-1,1,1))
    def matrix(row):
        t=row['component_bind'];q=t['rotation_xyzw']
        return reflect@Matrix.LocRotScale(Vector(t['translation']),Quaternion((q[3],*q[:3])),Vector(t['scale']))@reflect
    new={b.name:matrix(expected[b.name])@matrix(actual[b.name]).inverted()@b.matrix_local for b in rig.data.bones}
    bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    for b in rig.data.edit_bones:
        b.matrix=new[b.name];corrections.append(b.name)
    bpy.ops.object.mode_set(mode='OBJECT')
def update():bpy.context.view_layer.update()
def aim(name,end,direction):
    b=rig.pose.bones[name];origin=b.head.copy()
    rot=(rig.pose.bones[end].head-origin).rotation_difference(Vector(direction)).to_matrix().to_4x4()
    b.matrix=Matrix.Translation(origin)@rot@Matrix.Translation(-origin)@b.matrix;update()
for side,sign in [('l',1),('r',-1)]:
    aim('upperarm_'+side,'lowerarm_'+side,(sign,0,0))
    aim('lowerarm_'+side,'hand_'+side,(sign,0,0))
    pb=rig.pose.bones
    along=(pb['middle_03_'+side].head-pb['middle_01_'+side].head).normalized() if VARIANT=='Bind01' else (pb['middle_01_'+side].head-pb['hand_'+side].head).normalized()
    across=(pb['pinky_01_'+side].head-pb['index_01_'+side].head).normalized()
    across=(across-along*across.dot(along)).normalized()
    src=Matrix((along,across,along.cross(across))).transposed()
    dst=Matrix((Vector((sign,0,0)),Vector((0,1,0)),Vector((0,0,sign)))).transposed()
    b=pb['hand_'+side];origin=b.head.copy()
    b.matrix=Matrix.Translation(origin)@(dst@src.inverted()).to_4x4()@Matrix.Translation(-origin)@b.matrix;update()
    for digit in ['index','middle','ring','pinky']:
        for n in [1,2]:aim(f'{digit}_{n:02}_{side}',f'{digit}_{n+1:02}_{side}',(sign,0,0))
pose={b.name:[list(r) for r in b.matrix] for b in rig.pose.bones}
evalmesh=donor.evaluated_get(bpy.context.evaluated_depsgraph_get())
points=[v.co.copy() for v in evalmesh.data.vertices]
kd=KDTree(len(points))
for i,p in enumerate(points):kd.insert(p,i)
kd.balance()
before=set(bpy.data.objects)
sourcepath=ROOT/'Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16UndersuitInput01/OwnerExports/Revision02/tactical+jumpsuit+3d+model.fbx'
bpy.ops.import_scene.fbx(filepath=str(sourcepath),use_anim=False,use_image_search=False,use_custom_normals=True)
original=next(o for o in set(bpy.data.objects)-before if o.type=='MESH')
original.name='Revision02_Untouched'
original.hide_render=True;original.hide_set(True)
fit=original.copy();fit.data=original.data.copy();bpy.context.collection.objects.link(fit)
fit.name='Datum16_ExistingTopology_'+VARIANT;fit.hide_render=False;fit.hide_set(False)
fit.matrix_world=donor.matrix_world.copy()
scale=180.5439/.939941403577345
sourcepoints=[original.matrix_world@a.co for a in original.data.vertices]
digit_labels={};digit_fit=[]
centers={'index':(.003,.752,.4939),'middle':(.0204,.754,.49976),'ring':(.037,.756,.49487),'pinky':(.0522,.757,.4812)}
for a,v in zip(original.data.vertices,fit.data.vertices):
    p=original.matrix_world@a.co
    p*=scale
    # Narrow the stance to the unchanged contract leg centers; blend above hips.
    if p.z<100:
        influence=min(1.,max(0.,(100-p.z)/40))
        p.x*=1-.28*influence
    # Translate sleeve/hand centerline to the contract T-pose shoulder plane.
    influence=min(1.,max(0.,(abs(p.x)-25)/12))
    p.z+=influence*1.6
    if VARIANT!='Bind01' and abs(sourcepoints[v.index].x)>.385:
        raw=sourcepoints[v.index];sign=1 if raw.x>0 else -1;side='l' if sign==1 else 'r';x=abs(raw.x)
        wrist=rig.pose.bones['hand_'+side].head
        blend=min(1.,max(0.,(x-.385)/.025))
        h=Vector((sign*((x-.395)*170+abs(wrist.x)),(raw.y-.025)*155+wrist.y,(raw.z-.757)*155+wrist.z))
        digit=min(centers,key=lambda d:abs(raw.y-centers[d][0]))
        if VARIANT=='Bind05':digit='index' if raw.y<.0132 else 'middle' if raw.y<.029 else 'ring' if raw.y<.044 else 'pinky'
        if raw.z<.744 and raw.y<.012 and x>.418 and (VARIANT not in ('Bind04','Bind05') or x<.453):digit='thumb'
        if digit!='thumb':
            cy,cz,tip=centers[digit]
            start=rig.pose.bones[digit+'_01_'+side].head
            end=rig.pose.bones[digit+'_03_'+side].head+Vector((sign*2.,0,0))
            alpha=(x-.445)/(tip-.445)
            target=start.lerp(end,alpha)+Vector((0,(raw.y-cy)*155,(raw.z-cz)*155))
            weight=min(1.,max(0.,(x-.427)/.028))
            h=h.lerp(target,weight)
            if x>.447:digit_labels[v.index]=digit+'_'+side
        else:
            # Thumb gets its own correspondence; avoid nearest index/palm leakage.
            start=rig.pose.bones['thumb_01_'+side].head
            end=rig.pose.bones['thumb_03_'+side].head
            axis=(end-start).normalized();end=end+axis*2.
            alpha=(x-.417)/(.4475-.417)
            target=start.lerp(end,alpha)+Vector((0,(raw.y+.009)*140,(raw.z-.735)*140))
            h=h.lerp(target,min(1.,max(0.,(x-.415)/.018)))
            if x>.430 and raw.z<.742:digit_labels[v.index]='thumb_'+side
        p=p.lerp(h,blend)
    v.co=p
fit.data.update()
fit.parent=rig;fit.matrix_parent_inverse=Matrix.Identity(4)
fit.matrix_world=donor.matrix_world.copy()
for group in list(fit.vertex_groups):fit.vertex_groups.remove(group)
groups={g.name:fit.vertex_groups.new(name=g.name) for g in donor.vertex_groups}
distances=[];weights=[]
for v in fit.data.vertices:
    neighbors=kd.find_n(v.co,4)
    accum={}
    total=sum(1/max(d,.05)**2 for _,_,d in neighbors)
    for _,idx,d in neighbors:
        factor=(1/max(d,.05)**2)/total
        for g in donor.data.vertices[idx].groups:
            name=donor.vertex_groups[g.group].name
            accum[name]=accum.get(name,0)+g.weight*factor
    if VARIANT!='Bind01' and v.index in digit_labels:
        digit,side=digit_labels[v.index].split('_')
        # Interpolate only consecutive joints of the geometrically identified digit.
        joints=[rig.pose.bones[f'{digit}_{n:02}_{side}'].head for n in (1,2,3)]
        length=(joints[2]-joints[0]).length;along=(joints[2]-joints[0]).normalized()
        value=(v.co-joints[0]).dot(along)
        mid=(joints[1]-joints[0]).dot(along)
        if value<mid:
            alpha=max(0.,min(1.,value/mid));accum={f'{digit}_01_{side}':1-alpha,f'{digit}_02_{side}':alpha}
        else:
            alpha=max(0.,min(1.,(value-mid)/(length-mid)));accum={f'{digit}_02_{side}':1-alpha,f'{digit}_03_{side}':alpha}
    elif VARIANT!='Bind01' and abs(sourcepoints[v.index].x)>.40:
        # Proximal hand uses its own hand bone; digit blend begins at anatomical roots.
        side='l' if sourcepoints[v.index].x>0 else 'r'
        accum={'hand_'+side:1.}
    items=sorted(((n,w) for n,w in accum.items() if w>1e-5),key=lambda q:-q[1])[:8]
    s=sum(w for _,w in items)
    items=[(n,w/s) for n,w in items]
    for n,w in items:groups[n].add([v.index],w,'REPLACE')
    weights.append(items);distances.append(neighbors[0][2])
mod=fit.modifiers.new('ExactMSQ52_LinearSkin','ARMATURE');mod.object=rig
mod.use_deform_preserve_volume=False
# Preserve the fitted T surface and all original polygon connectivity.
tcopy=fit.copy();tcopy.data=fit.data.copy();bpy.context.collection.objects.link(tcopy)
tcopy.name='Revision02_FittedT_Unbound'+VARIANT[-2:];tcopy.modifiers.clear();tcopy.hide_render=True;tcopy.hide_set(True)
transforms={b.name:b.matrix@b.bone.matrix_local.inverted() for b in rig.pose.bones}
determinants=[]
for v,items in zip(fit.data.vertices,weights):
    blended=Matrix([[0]*4 for _ in range(4)])
    for name,w in items:blended+=transforms[name]*w
    determinants.append(blended.determinant())
    if VARIANT in ('Bind03','Bind04','Bind05') and abs(sourcepoints[v.index].x)>.385:
        # Retained bounded inverse alternative from Bind03. The later measured
        # cause of the spikes was thumb/index misclassification, not singularity.
        v.co=sum((transforms[name].inverted()@v.co*w for name,w in items),Vector())
    else:v.co=blended.inverted()@v.co
fit.data.update();update()
actual=fit.evaluated_get(bpy.context.evaluated_depsgraph_get())
residual=max((a.co-b.co).length for a,b in zip(actual.data.vertices,tcopy.data.vertices))
for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
update()
donor.hide_render=True;donor.hide_set(True)
fit.data.materials.clear()
mat=bpy.data.materials.new('NeutralDiagnostic');mat.diffuse_color=(.55,.55,.55,1)
fit.data.materials.append(mat)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1.
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=scene.render.resolution_y=1000
scene.render.resolution_percentage=100;scene.display.shading.light='STUDIO';scene.display.shading.studio_light='paint.sl'
scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.55,.55,.55)
scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.world.color=(.18,.18,.18)
camera=bpy.data.objects.new('DiagnosticCamera',bpy.data.cameras.new('DiagnosticCamera'));scene.collection.objects.link(camera);scene.camera=camera
camera.data.type='ORTHO';camera.data.clip_start=.001;camera.data.clip_end=100
for name,target,direction,size in [('front',(0,0,.9),(0,-1,0),2.05),('back',(0,0,.9),(0,1,0),2.05),('oblique',(0,0,.9),(1,-1,.25),2.05)]:
    target=Vector(target);direction=Vector(direction).normalized()
    camera.location=target+direction*5;camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=size
    scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/('Datum16_'+VARIANT+'.blend')))
bpy.ops.object.select_all(action='DESELECT');fit.select_set(True);rig.hide_set(False);rig.select_set(True);bpy.context.view_layer.objects.active=rig
export=dict(filepath=str(BASE/('Datum16_'+VARIANT+'.fbx')),use_selection=True,object_types={'MESH','ARMATURE'},add_leaf_bones=False,bake_anim=False,use_armature_deform_only=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',use_mesh_modifiers=True,mesh_smooth_type='FACE')
bpy.ops.export_scene.fbx(**export)
report=dict(vertices=len(fit.data.vertices),polygons=len(fit.data.polygons),scale_source_to_cm=scale,fit_notes=['Leg stance X narrowed up to 28%, blended to zero at Z100cm','Sleeve/hand Z +1.6cm blended across X25-37cm'],donor_pose_matrices=pose,
    transfer='Inverse-distance 4 nearest evaluated donor vertices; normalized top 8 influences; initial baseline before regional correction',
    distance_cm=dict(median=sorted(distances)[len(distances)//2],p95=sorted(distances)[int(.95*len(distances))],max=max(distances)),
    inverse_bind_reconstruction_max_cm=residual,weight_sums=[min(sum(w for _,w in x) for x in weights),max(sum(w for _,w in x) for x in weights)],
    export={k:sorted(v) if isinstance(v,set) else v for k,v in export.items()},rest_matrices_unchanged=not corrections,contract_rest_correction_bones=corrections,geometric_digit_labels=digit_labels,
    blend_determinant_min=min(determinants),near_singular_vertices=sum(abs(d)<.05 for d in determinants),hand_inverse_method='weighted inverse rigid transforms' if VARIANT in ('Bind03','Bind04','Bind05') else 'inverse blended matrix')
(OUT/'bind.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('donor_pose_matrices','export')}))
