"""Reuse unchanged body numerical/render helpers with isolated revision paths."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import body_intake01 as body
revision=sys.argv[sys.argv.index('--')+1]
assert revision in ('Revision01','Revision02')
body.OUT=body.ROOT/'Saved/PlayerCharacter01/MeshUsability01/Worker'/revision
body.SOURCE=body.PACKAGE/'OwnerExports'/revision/'tactical+jumpsuit+3d+model.fbx'
body.EXPECTED={'Revision01':'fc6340b6f36c529f15dac48ef06dca37aa72a07134b873e9e564f0addc6fa196',
               'Revision02':'aade1a13585f8639610e42a12cc350619ff4279e33325968f416bb4e8b8e8467'}[revision]
# The old main hardcodes Revision01's byte size. Substitute only that asserted
# identity in an isolated function namespace; numerical and rendering code stays unchanged.
if '--render-only' in sys.argv:
    import bpy
    import json
    assert body.helper.sha(body.SOURCE)==body.EXPECTED
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(body.SOURCE),use_custom_normals=True,use_image_search=False,use_anim=False)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    box=body.helper.bounds([o.matrix_world@v.co for o in meshes for v in o.data.vertices])
    body.render(meshes,box)
else:
    import inspect
    code=inspect.getsource(body.main).replace('SOURCE.stat().st_size == 933904',f'SOURCE.stat().st_size == {body.SOURCE.stat().st_size}')
    exec(compile(code,__file__,'exec'),body.__dict__)
    body.main()
