"""Editable native union kit; reuses ReworkA01 mesh and asset validators."""
import importlib.util
import json
import sys
from pathlib import Path
import bpy
import bmesh
ROOT=Path('D:/devgames/MeridianSquad')
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'Scripts/OpeningLobby'))
from functionalbuild01_data import OUT,SRC,geometry
from reworka01_kit import union_mesh

def build():
    assert not (SRC/'LobbyFunctionalBuild01.blend').exists() or ('--refine-elevator' in sys.argv and (OUT/'InitialDiagnostics/LobbyFunctionalBuild01.blend').exists())
    data=geometry();(OUT/'FBX').mkdir(exist_ok=True)
    scene=bpy.data.scenes.new('FunctionalBuild01_ReusableKit')
    scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    bpy.context.window.scene=scene
    mats={}
    for name,color in [('Stone',(.15,.17,.17)),('Wall',(.46,.48,.47)),('Metal',(.09,.11,.11))]:
        m=bpy.data.materials.new('M_FB01_'+name);m.diffuse_color=(*color,1);mats[name]=m
    spec=importlib.util.spec_from_file_location('existing_geometry_validator',ROOT/'Scripts/Benchmarks/OrchestrationAB/inspect_saved_asset.py')
    validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
    kit={};objects={}
    for index,(name,definition) in enumerate(data['modules'].items()):
        mesh=union_mesh('FB01_'+name,definition['boxes_m'])
        if name=='ElevatorLeaves':
            # Keep the two closed leaves as separate solids in one reusable mesh.
            # A 2mm edge makes their centre joint readable without a through gap.
            vertices=[];faces=[]
            for box in definition['boxes_m']:
                part=union_mesh('LeafPart',[box]);offset=len(vertices)
                vertices.extend([tuple(v.co) for v in part.vertices])
                faces.extend([[i+offset for i in face.vertices] for face in part.polygons])
                bpy.data.meshes.remove(part)
            bpy.data.meshes.remove(mesh);mesh=bpy.data.meshes.new('FB01_'+name)
            mesh.from_pydata(vertices,[],faces);mesh.update()
        obj=bpy.data.objects.new('SM_FB01_'+name,mesh)
        scene.collection.objects.link(obj);objects[name]=obj
        obj.data.materials.append(mats[definition['material']])
        if name=='ElevatorLeaves':
            bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
            bevel=obj.modifiers.new('Closed leaf meeting edge 2mm','BEVEL');bevel.width=.002;bevel.segments=1
            bpy.ops.object.modifier_apply(modifier=bevel.name)
        uv=obj.data.uv_layers.new(name='UV_Metres')
        for face in obj.data.polygons:
            axis=max(range(3),key=lambda i:abs(face.normal[i]));coords=([1,2],[0,2],[0,1])[axis]
            for loop in face.loop_indices:
                co=obj.data.vertices[obj.data.loops[loop].vertex_index].co
                uv.data[loop].uv=(co[coords[0]],co[coords[1]])
        obj.data.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(obj.data)
        nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free()
        bounds=validator.bounds([v.co for v in obj.data.vertices]);error=validator.bounds_error(bounds,[[-s/2 for s in definition['size_m']],[s/2 for s in definition['size_m']]])
        row={'object':obj.name,'dimensions_m':list(obj.dimensions),'bounds_m':bounds,'bounds_error_m':error,
             'nonmanifold_edges':nonmanifold,'signed_volume_m3':volume,'triangles':len(obj.data.loop_triangles),
             'degenerate_faces':sum(p.area<=1e-12 for p in obj.data.polygons),'connected_components':len(validator.components(obj.data)),
             'uv_layers':len(obj.data.uv_layers),'slots':[m.name for m in obj.data.materials],
             'scale':list(obj.scale),'rotation':list(obj.rotation_euler),'pivot':'Bounds centre',
             'export':'Saved/OpeningLobby/FunctionalBuild01/Worker/FBX/'+obj.name+'.fbx'}
        assert nonmanifold==0 and volume>0 and error<.0001 and row['degenerate_faces']==0,(name,row)
        # Source stays in drawing coordinates. Export a temporary mesh with Y
        # reflected and normals repaired to cancel the measured UE FBX reflection.
        export=obj.copy();export.data=obj.data.copy();export.name=obj.name+'_Export';scene.collection.objects.link(export)
        for v in export.data.vertices:v.co.y=-v.co.y
        bm=bmesh.new();bm.from_mesh(export.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(export.data);bm.free()
        bpy.ops.object.select_all(action='DESELECT');export.select_set(True);bpy.context.view_layer.objects.active=export
        bpy.ops.export_scene.fbx(filepath=str(ROOT/row['export']),use_selection=True,object_types={'MESH'},global_scale=1,
            apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',use_space_transform=True,
            bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_triangles=True,bake_anim=False,add_leaf_bones=False)
        mesh=export.data;bpy.data.objects.remove(export,do_unlink=True);bpy.data.meshes.remove(mesh)
        row['export_y_reflection_compensated']=True;kit[name]=row
        obj.location=(index%5*25,index//5*30,definition['size_m'][2]/2)
    assembly=bpy.data.scenes.new('FunctionalBuild01_Assembly')
    assembly.unit_settings.system='METRIC';assembly.unit_settings.scale_length=1
    for name,item in data['instances'].items():
        obj=objects[item['module']].copy();obj.name='FB01_'+name;obj.location=item['center_m'];assembly.collection.objects.link(obj)
    bpy.context.window.scene=assembly
    bpy.data.libraries.write(str(SRC/'LobbyFunctionalBuild01.blend'),{scene,assembly},fake_user=True,compress=True)
    (OUT/'kit.json').write_text(json.dumps({'blender':bpy.app.version_string,'assets':kit,'passed':True,'source':'Assets/Source/OpeningLobby/FunctionalBuild01/LobbyFunctionalBuild01.blend'},indent=2))
    print(json.dumps({'modules':len(kit),'instances':len(data['instances']),'passed':True}))

if __name__=='__main__':build()
