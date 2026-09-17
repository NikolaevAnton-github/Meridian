"""Inspect the actual Creator FBX export and render matched neutral comparisons."""
import bpy
import json
import sys
import math
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'Assets/Source/PlayerCharacter01/MetaHumanTrial01'
OUT = ROOT / 'Saved/PlayerCharacter01/MetaHumanTrial01/Worker/Compare02'
DNA_MODE = 'dna02' in sys.argv
if DNA_MODE: OUT = OUT.parent / 'ComparePosedDNA02'
AXIS_MODE = 'axis02' in sys.argv
if AXIS_MODE:
    DNA_MODE=True
    OUT=OUT.parent/'ComparePosedDNA02_Aligned'
APOSE_MODE = 'apose02' in sys.argv
if APOSE_MODE: OUT=OUT.parent/'CompareAPose02'
OUT.mkdir(parents=True, exist_ok=True)

def bounds(objects):
    points = [o.matrix_world @ v.co for o in objects for v in o.data.vertices]
    return dict(min=[min(v[i] for v in points) for i in range(3)],
        max=[max(v[i] for v in points) for i in range(3)])

def main():
    bpy.ops.wm.open_mainfile(filepath=str(BASE / 'Datum16Trial01.blend'))
    source = bpy.data.objects['Datum16_BodyOnly01']
    before = set(bpy.data.objects)
    fbx = 'SK_Datum16_PosedDNA02.fbx' if DNA_MODE else 'MH_Datum16_Trial01_Body.fbx'
    folder='Solve02/APose' if APOSE_MODE else 'Solve02/SourcePose'
    bpy.ops.import_scene.fbx(filepath=str(BASE / folder / fbx),
        use_anim=False, use_image_search=False, use_custom_normals=True)
    added = set(bpy.data.objects)-before
    meshes = [o for o in added if o.type=='MESH']
    rigs = [o for o in added if o.type=='ARMATURE']
    raw_bounds=bounds(meshes)
    if AXIS_MODE:
        for o in meshes: o.data.transform(Matrix.Rotation(math.pi/2,4,'X'))
    data = dict(source_bounds=bounds([source]), fit_bounds=bounds(meshes),
        meshes=[dict(name=o.name, vertices=len(o.data.vertices), faces=len(o.data.polygons),
            groups=len(o.vertex_groups), uv_layers=[x.name for x in o.data.uv_layers],
            assigned_vertices=sum(bool(v.groups) for v in o.data.vertices),
            weight_sum_range=[min(sum(g.weight for g in v.groups) for v in o.data.vertices),
                max(sum(g.weight for g in v.groups) for v in o.data.vertices)],
            dimensions=list(o.dimensions), matrix=[list(r) for r in o.matrix_world]) for o in meshes],
        armatures=[dict(name=o.name, bones=len(o.data.bones),
            hierarchy=[dict(name=b.name,parent=b.parent.name if b.parent else None,
                head=list(b.head_local), tail=list(b.tail_local)) for b in o.data.bones]) for o in rigs])
    data['raw_export_bounds']=raw_bounds
    data['diagnostic_axis_correction']='Mesh data +90 degrees X; original exported rig unchanged. Diagnostic only; not a verified production import.' if AXIS_MODE else 'None'
    (OUT/'mesh-inspection.json').write_text(json.dumps(data,indent=2)+'\n')
    bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
    scene=bpy.context.scene
    scene.render.resolution_x=scene.render.resolution_y=900
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.display.shading.light='STUDIO'
    scene.display.shading.studio_light='paint.sl'
    scene.display.shading.color_type='SINGLE'
    scene.display.shading.single_color=(.55,.55,.55)
    scene.display.shading.background_type='WORLD'
    scene.world.color=(.18,.18,.18)
    scene.display.shading.show_shadows=True
    scene.display.shading.show_cavity=True
    scene.display.shading.cavity_type='BOTH'
    scene.display.render_aa='16'
    cam_data=bpy.data.cameras.new('ComparisonCamera')
    cam=bpy.data.objects.new('ComparisonCamera',cam_data)
    scene.collection.objects.link(cam)
    scene.camera=cam
    cam_data.type='ORTHO'
    cam_data.clip_start=.001
    cam_data.clip_end=100
    views=[('front',(0,0,.85),(0,-1,0),2.1),('back',(0,0,.85),(0,1,0),2.1),
           ('side',(0,0,.85),(1,0,0),2.1),('oblique',(0,0,.85),(1,-1,.3),2.1),
           ('hips',(0,0,.82),(0,-1,0),.67),('ankles',(0,0,.17),(1,-1,.2),.6),
           ('shoulders',(0,0,1.35),(0,-1,.2),1.0)]
    points=[source.matrix_world@v.co for v in source.data.vertices]
    for name, sign in [('left',1),('right',-1)]:
        hand=[p for p in points if sign*p.x>.75]
        target=tuple((min(p[i] for p in hand)+max(p[i] for p in hand))/2 for i in range(3))
        for side,d in [('dorsal',(0,0,1)),('palm',(0,0,-1)),('oblique',(sign,-1,.65))]:
            views.append((name+'_'+side,target,d,.39))
    for o in bpy.data.objects:
        if o.type=='MESH':o.hide_render=True
    for label,group in [('source',[source]),('fit',meshes)]:
        for o in group:o.hide_render=False
        for name,target,direction,scale in views:
            target=Vector(target);direction=Vector(direction).normalized()
            cam.location=target+direction*6
            cam.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
            cam_data.ortho_scale=scale
            scene.render.filepath=str(OUT/(label+'-'+name+'.png'))
            bpy.ops.render.render(write_still=True)
        for o in group:o.hide_render=True
    for o in meshes:o.hide_render=False
    (OUT/'views.json').write_text(json.dumps(views,indent=2)+'\n')
    blend_name = 'Datum16_PosedDNA02_Inspection.blend' if DNA_MODE else 'Datum16_Solve02_Inspection.blend'
    if AXIS_MODE: blend_name='Datum16_PosedDNA02_Aligned.blend'
    if APOSE_MODE: blend_name='Datum16_APose02_Inspection.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Solve02'/blend_name))
    print(json.dumps({k:v for k,v in data.items() if k!='armatures'}))

if __name__=='__main__':main()
