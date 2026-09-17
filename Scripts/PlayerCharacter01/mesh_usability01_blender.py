"""Inspect donor and preserve original layers for topology-preserving binding."""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Matrix, Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import shoulder_intake01 as helper
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'Assets/Source/PlayerCharacter01/MeshUsability01'
OUT=ROOT/'Saved/PlayerCharacter01/MeshUsability01/Worker'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(BASE/'Donor/MSQ52_Manny161.fbx'),use_anim=False,use_image_search=False,automatic_bone_orientation=False,ignore_leaf_bones=False)
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
data=dict(blender=bpy.app.version_string,rig=dict(name=rig.name,matrix=[list(r) for r in rig.matrix_world],bones=[dict(name=b.name,parent=b.parent.name if b.parent else None,head=list(b.head_local),tail=list(b.tail_local),matrix=[list(r) for r in b.matrix_local]) for b in rig.data.bones]),
    meshes=[dict(name=o.name,vertices=len(o.data.vertices),faces=len(o.data.polygons),matrix=[list(r) for r in o.matrix_world],bounds=helper.bounds([o.matrix_world@v.co for v in o.data.vertices]),groups=len(o.vertex_groups)) for o in meshes])
(OUT/'donor-blender.json').write_text(json.dumps(data,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Donor/MSQ52_Manny161.blend'))
print(json.dumps(dict(bones=len(rig.data.bones),meshes=data['meshes'],rig_matrix=data['rig']['matrix'])))
