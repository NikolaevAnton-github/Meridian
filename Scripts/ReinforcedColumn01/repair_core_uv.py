"""Planar concrete caps and steep ledges, cylindrical side-wall mapping."""
import json
from pathlib import Path
import unreal as u

CORE='/Game/ReinforcedColumn01/SM_RC01_SupportedColumn'


def build(report_path, source_revision='11'):
    report_path=Path(report_path)
    assert not report_path.exists()
    assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    core=u.load_asset(CORE)
    before=json.loads(u.NGDColumnAuthoring.inspect_mesh(core))
    collider=core.get_editor_property('complex_collision_mesh')
    mesh=u.DynamicMesh()
    _,outcome=u.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(
        core,mesh,u.GeometryScriptCopyMeshFromAssetOptions(apply_build_settings=False),
        u.GeometryScriptMeshReadLOD(lod_type=u.GeometryScriptLODType.SOURCE_MODEL))
    assert outcome==u.GeometryScriptOutcomePins.SUCCESS
    queries=u.GeometryScript_MeshQueries;uvs=u.GeometryScript_UVs
    elements={};changed=0;ledges=0
    for triangle_id in range(queries.get_num_triangle_i_ds(mesh)):
        valid,a,b,c=queries.get_triangle_positions(mesh,triangle_id)
        if not valid:
            continue
        cap=(max(a.z,b.z,c.z)-min(a.z,b.z,c.z)<=.0001
             and min(abs(a.z+620),abs(a.z+900))<=.001)
        p=(b.x-a.x,b.y-a.y,b.z-a.z);q=(c.x-a.x,c.y-a.y,c.z-a.z)
        normal=(p[1]*q[2]-p[2]*q[1],p[2]*q[0]-p[0]*q[2],p[0]*q[1]-p[1]*q[0])
        length=sum(v*v for v in normal)**.5
        ledge=(int(source_revision)>=13 and length>1e-10
               and max(a.z,b.z,c.z)<=-619.999 and abs(normal[2])/length>.65)
        if not cap and not ledge:
            continue
        ledges+=int(ledge and not cap)
        ids,valid=queries.get_triangle_indices(mesh,triangle_id)
        assert valid
        uv_ids=[]
        for vertex_id,p in zip((ids.x,ids.y,ids.z),(a,b,c)):
            if vertex_id not in elements:
                _,element_id,valid=uvs.add_uv_element_to_mesh(mesh,0,u.Vector2D(p.x/1000,p.y/1000),True)
                assert valid
                elements[vertex_id]=element_id
            uv_ids.append(elements[vertex_id])
        _,valid=uvs.set_mesh_triangle_uv_element_i_ds(mesh,0,triangle_id,u.IntVector(*uv_ids),True)
        assert valid
        changed+=1
    assert changed>0 and mesh.get_triangle_count()==before['source_triangles']
    u.GeometryScript_Normals.compute_tangents(mesh,u.GeometryScriptTangentsOptions(uv_layer=0))
    options=u.GeometryScriptCopyMeshToAssetOptions(enable_recompute_normals=False,
        enable_recompute_tangents=False,enable_remove_degenerates=False,
        apply_nanite_settings=False,replace_materials=False,use_original_vertex_order=True)
    _,outcome=u.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(mesh,core,options,u.GeometryScriptMeshWriteLOD())
    assert outcome==u.GeometryScriptOutcomePins.SUCCESS
    assert core.get_editor_property('complex_collision_mesh')==collider
    assert u.EditorAssetLibrary.save_loaded_asset(core)
    after=json.loads(u.NGDColumnAuthoring.inspect_mesh(core))
    assert after['source_triangles']==before['source_triangles']
    assert after['invalid_normals']==0 and after['invalid_tangents']==0
    record=dict(asset=CORE,source_revision=source_revision,operation='Planar XY UVs on concrete caps and steep lower-band ledges; cylindrical side UVs retained',
        cap_triangles=changed-ledges,steep_ledge_triangles=ledges,new_uv_elements=len(elements),before=before,after=after,
        geometry_positions_edited=False,collision_proxy_preserved=True)
    report_path.write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps(record))
