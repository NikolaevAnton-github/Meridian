"""Read saved native modules and FBX using existing geometry helpers; no resave."""
import contextlib
import importlib.util
import io
import json
import math
import bpy
import bmesh
from reworka01_data import ROOT,SRC,OUT,geometry

def run():
    spec=importlib.util.spec_from_file_location('reused_geometry_checks',ROOT/'Scripts/Benchmarks/OrchestrationAB/inspect_saved_asset.py')
    validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
    definitions=geometry()['modules'];kit=json.loads((OUT/'kit.json').read_text())['assets'];rows=[]
    previous=bpy.context.window.scene
    scene=bpy.data.scenes.new('ReworkA01_ReadOnlySourceAudit');bpy.context.window.scene=scene

    def inspect(obj,name,kind):
        mesh=obj.data;mesh.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(mesh)
        volume=bm.calc_volume(signed=True);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
        points=[list(v.co) for v in mesh.vertices]
        expected=[[-v/2 for v in definitions[name]['size_m']],[v/2 for v in definitions[name]['size_m']]]
        row=dict(name=name,kind=kind,bounds_error_m=validator.bounds_error(validator.bounds(points),expected),
            nonmanifold_edges=nonmanifold,signed_volume_m3=volume,finite_vertices=all(math.isfinite(v) for p in points for v in p),
            material_slots=len(mesh.materials),uv_layers=len(mesh.uv_layers),triangles=len(mesh.loop_triangles),
            nonunit_normals=sum(abs(p.normal.length-1)>1e-5 for p in mesh.polygons),
            degenerate_faces=sum(p.area<=1e-12 for p in mesh.polygons),scale=list(obj.scale),rotation=list(obj.rotation_euler),
            connected_components=len(validator.components(mesh)))
        row['passed']=row['bounds_error_m']<.0001 and nonmanifold==0 and volume>0 and row['finite_vertices'] and row['nonunit_normals']==0 and row['degenerate_faces']==0 and row['material_slots']==1 and row['uv_layers']>0 and max(abs(v-1) for v in obj.scale)<1e-5 and max(abs(v) for v in obj.rotation_euler)<1e-5
        rows.append(row)

    with bpy.data.libraries.load(str(SRC/'LobbyArchitectureReworkA01.blend'),link=False) as (available,loaded):
        loaded.objects=[n for n in available.objects if n.startswith('SM_RA01_')]
    assert len(loaded.objects)==23
    for obj in loaded.objects:
        # Blender appends a numeric suffix when the current production object
        # is already in memory; the saved semantic module name precedes it.
        name=obj.name.split('.')[0].replace('SM_RA01_','')
        scene.collection.objects.link(obj);inspect(obj,name,'saved_blend')
        bpy.data.objects.remove(obj,do_unlink=True)
    for name,item in kit.items():
        with contextlib.redirect_stdout(io.StringIO()):
            bpy.ops.import_scene.fbx(filepath=str(ROOT/item['export']),use_custom_normals=True)
        imported=list(bpy.context.selected_objects);meshes=[o for o in imported if o.type=='MESH'];assert len(meshes)==1
        inspect(meshes[0],name,'reimported_fbx')
        for obj in imported:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.context.window.scene=previous;bpy.data.scenes.remove(scene)
    report=dict(passed=all(r['passed'] for r in rows),checks=rows,source=str(SRC/'LobbyArchitectureReworkA01.blend'),
        validator_reuse='inspect_saved_asset.bounds/bounds_error/components; existing Architecture01 FBX conventions',
        uv_scope='Metre tiling UVs intentionally share space; unique bake-atlas overlap gate is inapplicable to this neutral untextured kit.')
    (OUT/'saved-source-audit.json').write_text(json.dumps(report,indent=2))
    assert report['passed'],[r for r in rows if not r['passed']]
    print(json.dumps(dict(passed=True,saved_native_modules=23,reimported_fbx_modules=23)))
