"""Editable closed modular solids using the existing local Blender/FBX conventions."""
import importlib.util
import itertools
import json
import math
import sys
from pathlib import Path
import bpy
import bmesh

ROOT = Path('D:/devgames/MeridianSquad')
sys.path.insert(0,str(ROOT/'Scripts/OpeningLobby'))
from reworka01_data import OUT,SRC,geometry

def union_mesh(name, boxes):
    axes = [sorted(set(b[i] for b in boxes for i in [axis*2,axis*2+1])) for axis in range(3)]
    occupied = set()
    for cell in itertools.product(*(range(len(a)-1) for a in axes)):
        center = [(axes[i][c]+axes[i][c+1])/2 for i,c in enumerate(cell)]
        if any(all(b[i*2]-1e-8<v<b[i*2+1]+1e-8 for i,v in enumerate(center)) for b in boxes):
            occupied.add(cell)
    vertices, faces, indices = [], [], {}
    for cell in occupied:
        for axis in range(3):
            others = [i for i in range(3) if i!=axis]
            for sign in [-1,1]:
                neighbor = list(cell); neighbor[axis]+=sign
                if tuple(neighbor) in occupied:
                    continue
                face = []
                for a,b in [(0,0),(1,0),(1,1),(0,1)]:
                    grid = list(cell);grid[axis]+=int(sign>0);grid[others[0]]+=a;grid[others[1]]+=b
                    xyz = tuple(axes[i][c] for i,c in enumerate(grid))
                    if xyz not in indices:
                        indices[xyz]=len(vertices);vertices.append(xyz)
                    face.append(indices[xyz])
                faces.append(face)
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces);mesh.update()
    bm = bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bmesh.ops.dissolve_limit(bm,angle_limit=.0001,verts=list(bm.verts),edges=list(bm.edges),use_dissolve_boundaries=False)
    bm.to_mesh(mesh);bm.free();mesh.update()
    return mesh

def build():
    assert not (SRC/'LobbyArchitectureReworkA01.blend').exists()
    SRC.mkdir(parents=True,exist_ok=True);(OUT/'FBX').mkdir(parents=True,exist_ok=True)
    data = geometry()
    (OUT/'geometry-contract.json').write_text(json.dumps(data,indent=2))
    scene = bpy.data.scenes.new('ReworkA01_ReusableKit')
    scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    bpy.context.window.scene=scene
    mats={}
    for name,color in [('Stone',(.15,.17,.17)),('Wall',(.46,.48,.47)),('Ceiling',(.38,.40,.39)),('Metal',(.09,.11,.11)),('Glazing',(.48,.65,.67))]:
        mat=bpy.data.materials.new('M_RA01_'+name);mat.diffuse_color=(*color,1);mats[name]=mat
    kit={};objects={}
    # Reuse the existing generic saved-asset geometry helpers, without executing
    # its benchmark task, fixed crate expectations, or output routine.
    spec=importlib.util.spec_from_file_location('existing_asset_geometry',ROOT/'Scripts/Benchmarks/OrchestrationAB/inspect_saved_asset.py')
    validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
    for index,(name,definition) in enumerate(data['modules'].items()):
        obj=bpy.data.objects.new('SM_RA01_'+name,union_mesh('RA01_'+name,definition['boxes_m']))
        scene.collection.objects.link(obj);objects[name]=obj
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
        obj.data.materials.append(mats[definition['material']])
        # Small manufacturing edge, subordinate to the metre-scale depth hierarchy.
        bevel=min(.002,min(definition['size_m'])/8)
        mod=obj.modifiers.new('Subordinate 2mm edge','BEVEL');mod.width=bevel;mod.segments=2
        bpy.ops.object.modifier_apply(modifier=mod.name)
        uv=obj.data.uv_layers.new(name='UV_Metres') if not obj.data.uv_layers else obj.data.uv_layers.active
        uv.name='UV_Metres'
        for face in obj.data.polygons:
            axis=max(range(3),key=lambda i:abs(face.normal[i]));coordinates=([1,2],[0,2],[0,1])[axis]
            for loop in face.loop_indices:
                co=obj.data.vertices[obj.data.loops[loop].vertex_index].co
                uv.data[loop].uv=(co[coordinates[0]],co[coordinates[1]])
        obj.data.calc_loop_triangles()
        bm=bmesh.new();bm.from_mesh(obj.data)
        nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free()
        actual=validator.bounds([v.co for v in obj.data.vertices])
        expected=[[-s/2 for s in definition['size_m']],[s/2 for s in definition['size_m']]]
        error=validator.bounds_error(actual,expected)
        row=dict(object=obj.name,dimensions_m=list(obj.dimensions),bounds_m=actual,bounds_error_m=error,
                 vertices=len(obj.data.vertices),triangles=len(obj.data.loop_triangles),nonmanifold_edges=nonmanifold,
                 signed_volume_m3=volume,connected_components=len(validator.components(obj.data)),
                 degenerate_faces=sum(p.area<=1e-12 for p in obj.data.polygons),
                 slots=[m.name for m in obj.data.materials],uv_layers=len(obj.data.uv_layers),
                 uv_mode='Dominant-axis metres; intentional shared tiling, neutral materials',
                 scale=list(obj.scale),rotation=list(obj.rotation_euler),pivot='Module bounding-box centre',
                 export='Saved/OpeningLobby/ArchitectureReworkA01/Worker/FBX/'+obj.name+'.fbx')
        assert nonmanifold==0 and volume>0 and error<.0001 and row['degenerate_faces']==0,(name,row)
        bpy.ops.export_scene.fbx(filepath=str(ROOT/row['export']),use_selection=True,object_types={'MESH'},global_scale=1,
            apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',use_space_transform=True,
            bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_triangles=True,bake_anim=False,add_leaf_bones=False)
        kit[name]=row
        obj.location=(index%6*12,index//6*24,definition['size_m'][2]/2)
    assembly=bpy.data.scenes.new('ReworkA01_RepresentativeAssembly')
    assembly.unit_settings.system='METRIC';assembly.unit_settings.scale_length=1
    for name,instance in data['instances'].items():
        obj=objects[instance['module']].copy();obj.name='RA01_'+name;obj.location=instance['center_m']
        assembly.collection.objects.link(obj)
    bpy.context.window.scene=assembly
    bpy.data.libraries.write(str(SRC/'LobbyArchitectureReworkA01.blend'),{scene,assembly},fake_user=True,compress=True)
    (OUT/'kit.json').write_text(json.dumps(dict(blender=bpy.app.version_string,assets=kit,passed=True,
        validator='Reused inspect_saved_asset.bounds/bounds_error/components; Architecture01 UV/export pattern',
        source='Assets/Source/OpeningLobby/ArchitectureReworkA01/LobbyArchitectureReworkA01.blend'),indent=2))
    print(json.dumps(dict(modules=len(kit),instances=len(data['instances']),source=str(SRC/'LobbyArchitectureReworkA01.blend'))))
