"""Fresh 2.4 metre UV sample only; no lobby geometry is imported or changed."""
import bpy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'Assets/Source/OpeningLobby/PainterStone01'
OUT=ROOT/'Saved/OpeningLobby/PainterStone01/Worker/Exports'
SRC.mkdir(parents=True,exist_ok=True)
OUT.mkdir(parents=True,exist_ok=True)
assert not (SRC/'StoneSample.blend').exists()
assert bpy.data.filepath == '', 'Only a fresh background factory scene is allowed'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
scene.unit_settings.scale_length=1.0
mesh=bpy.data.meshes.new('StoneSample_240cm_UV')
mesh.from_pydata([(-1.2,0,-1.2),(1.2,0,-1.2),(1.2,0,1.2),(-1.2,0,1.2)],[],[(0,1,2,3)])
mesh.update()
uv=mesh.uv_layers.new(name='StoneTile_0_1')
for loop,coords in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=coords
obj=bpy.data.objects.new('StoneSample_240cm',mesh)
scene.collection.objects.link(obj)
mat=bpy.data.materials.new('PainterStone01')
mesh.materials.append(mat)
obj.select_set(True)
bpy.context.view_layer.objects.active=obj
bpy.ops.wm.save_as_mainfile(filepath=str(SRC/'StoneSample.blend'))
bpy.ops.export_scene.fbx(filepath=str(OUT/'StoneSample_240cm.fbx'),use_selection=True,
    object_types={'MESH'},apply_unit_scale=True,axis_forward='-Z',axis_up='Y',bake_anim=False,
    add_leaf_bones=False,path_mode='AUTO')
(SRC/'mesh.json').write_text(json.dumps(dict(blender=bpy.app.version_string,physical_coverage_cm=[240,240],
    vertices_m=[list(v.co) for v in mesh.vertices],uvs=[list(v.uv) for v in uv.data],
    material='PainterStone01',source='StoneSample.blend',fbx='Saved/OpeningLobby/PainterStone01/Worker/Exports/StoneSample_240cm.fbx'),indent=2))
print('PAINTERSTONE_MESH_OK '+bpy.app.version_string)
