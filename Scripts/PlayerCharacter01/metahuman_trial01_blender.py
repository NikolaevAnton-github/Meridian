"""Prepare a preserved T-pose body-only input for the bounded Creator experiment."""
import bpy
import bmesh
import hashlib
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/PlayerCharacter01/MetaHumanTrial01/Worker'
DEST = ROOT / 'Assets/Source/PlayerCharacter01/MetaHumanTrial01'
SOURCE = ROOT / 'Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16UndersuitInput01/OwnerExports/tactical+jumpsuit+3d+model.fbx'

def bbox(obj):
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    lo = [min(v[i] for v in pts) for i in range(3)]
    hi = [max(v[i] for v in pts) for i in range(3)]
    return dict(min=lo, max=hi, size=[hi[i]-lo[i] for i in range(3)])

def main():
    assert bpy.app.background and not bpy.context.preferences.filepaths.use_scripts_auto_execute
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == 'fc6340b6f36c529f15dac48ef06dca37aa72a07134b873e9e564f0addc6fa196'
    DEST.mkdir(parents=True, exist_ok=True)
    assert not (DEST / 'Datum16Trial01.blend').exists()
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0
    bpy.ops.import_scene.fbx(filepath=str(SOURCE), use_custom_normals=True, use_image_search=False,
        use_anim=False, global_scale=1.0, bake_space_transform=False)
    source = bpy.context.selected_objects[0]
    source.name = 'Original_Untouched_DeclaredUnits'
    initial = bbox(source)
    factor = 1.805439 / initial['size'][2]
    full = source.copy()
    full.data = source.data.copy()
    bpy.context.collection.objects.link(full)
    full.name = 'Datum16_Full_Experimental180_54cm'
    full.scale *= factor
    bpy.ops.object.select_all(action='DESELECT')
    full.select_set(True)
    bpy.context.view_layer.objects.active = full
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    source.hide_set(True)
    source.hide_render = True
    body = full.copy()
    body.data = full.data.copy()
    bpy.context.collection.objects.link(body)
    body.name = 'Datum16_BodyOnly01'
    bm = bmesh.new()
    bm.from_mesh(body.data)
    bm.verts.ensure_lookup_table()
    unvisited = set(bm.verts)
    components = []
    while unvisited:
        first = unvisited.pop()
        comp, queue = {first}, [first]
        while queue:
            v = queue.pop()
            for edge in v.link_edges:
                q = edge.other_vert(v)
                if q in unvisited:
                    unvisited.remove(q)
                    comp.add(q)
                    queue.append(q)
        components.append(comp)
    hood = [c for c in components if max(v.co.z for v in c) > 1.79]
    assert len(hood) == 1 and min(v.co.z for v in hood[0]) > 1.4
    removed = len(hood[0])
    bmesh.ops.delete(bm, geom=list(hood[0]), context='VERTS')
    bm.to_mesh(body.data)
    bm.free()
    full.hide_set(True)
    full.hide_render = True
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    export_settings = dict(use_selection=True, object_types={'MESH'}, use_mesh_modifiers=True,
        add_leaf_bones=False, bake_anim=False, axis_forward='-Y', axis_up='Z',
        apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE', global_scale=1.0)
    bpy.ops.export_scene.fbx(filepath=str(DEST / 'Datum16_BodyOnly01.fbx'), **export_settings)
    bpy.ops.wm.save_as_mainfile(filepath=str(DEST / 'Datum16Trial01.blend'))
    info = dict(blender=bpy.app.version_string, original=str(SOURCE.relative_to(ROOT)),
        initial_bounds_m=initial, uniform_scale=factor, experimental_full_bounds_m=bbox(full),
        body_bounds_m=bbox(body), source_vertices=len(source.data.vertices), body_vertices=len(body.data.vertices),
        hood_vertices_excluded=removed, topology_repair='None; first solve retains garment defects and islands.',
        axes='Blender +Z up, front -Y; source X positive is character-left.',
        scale_authority='Temporary 180.5439 cm diagnostic source-mesh height from MSQ52. Not approved stature.',
        preserved_gameplay=dict(camera_cm=170, capsule_radius_cm=34, capsule_half_height_cm=88, fov_deg=90),
        export=dict(export_settings, object_types=['MESH']),
        native_layers=[source.name, full.name, body.name])
    (DEST / 'input-settings.json').write_text(json.dumps(info, indent=2)+'\n')
    (OUT / 'input-preparation.json').write_text(json.dumps(info, indent=2)+'\n')
    print(json.dumps(info))

if __name__ == '__main__': main()
