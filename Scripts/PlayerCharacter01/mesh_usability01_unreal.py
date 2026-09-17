"""Bounded exact-rig export/import and candidate playback adapters."""
import json
from pathlib import Path
import unreal as u
import animation_audit01_unreal as audit
ROOT=Path(u.Paths.project_dir()).resolve()
OUT=ROOT/'Saved/PlayerCharacter01/MeshUsability01/Worker'
SOURCE=ROOT/'Assets/Source/PlayerCharacter01/MeshUsability01'
BASE='/Game/Development/PlayerCharacter01/MeshUsability01'
DONOR=BASE+'/Donor/SKM_Manny'

def write(name,value):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    return value

def action(operation,argument=''):
    if operation=='inspect':
        return write(argument or 'editor-initial',audit.state())
    if operation=='playback_setup':
        audit.OUT=OUT/'Compatibility05';audit.OUT.mkdir(exist_ok=True)
        audit.preview_setup()
        comp=audit.PREVIEW['components']['character']
        comp.set_skeletal_mesh_asset(u.load_asset(BASE+'/Datum16_Bind05'))
        comp.set_anim_instance_class(u.AnimPreviewInstance)
        for i in range(comp.get_num_materials()):comp.set_material(i,u.load_asset('/Engine/BasicShapes/BasicShapeMaterial'))
        for op in ['reserve_setup','attachments','exposure_setup']:audit.action(op,'')
        return write('playback-setup',dict(candidate=comp.get_skeletal_mesh_asset().get_path_name(),state=audit.state()))
    if operation=='playback_bind':
        import inspect
        audit.OUT=OUT/'Compatibility05'
        audit.action('pie_bind','');audit.action('attachments_live','');audit.action('camera_named','contact')
        c=audit.PREVIEW['components']['character']
        assert c.get_skeletal_mesh_asset().get_path_name()==BASE+'/Datum16_Bind05.Datum16_Bind05'
        # Keep the existing timing, additive-base and attachment implementation;
        # replace only its unconditional mannequin substitution with an assertion.
        code=inspect.getsource(audit.preview_pose)
        code=code.replace('c.set_skeletal_mesh_asset(u.load_asset(mesh))',"assert 'MeshUsability01/Datum16_Bind05.' in c.get_skeletal_mesh_asset().get_path_name()")
        exec(compile(code,inspect.getfile(audit),'exec'),audit.__dict__)
        return write('playback-binding',dict(candidate=c.get_skeletal_mesh_asset().get_path_name(),attachment='Candidate ik_hand_gun at identity',hidden_donor=False))
    if operation in ('playback_start','playback_status','playback_abort','camera_named','restore'):
        audit.OUT=OUT/'Compatibility05'
        return audit.action(operation,argument)
    if operation=='pose':
        result=audit.preview_pose(argument)
        return result
    if operation=='sample':
        return audit.preview_sample(argument)
    if operation=='native_geometry':
        mesh=u.load_asset(BASE+'/Datum16_Bind05');dynamic=u.DynamicMesh()
        u.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(mesh,dynamic,u.GeometryScriptCopyMeshFromAssetOptions(),u.GeometryScriptMeshReadLOD())
        pts=[]
        for i in range(dynamic.get_vertex_count()):
            pos,valid=dynamic.get_vertex_position(i)
            assert valid
            pts.append(audit.serial(pos))
        write('native-geometry-Bind05',dict(vertices=pts,triangles=dynamic.get_triangle_count(),api=str(dynamic.get_vertex_position.__doc__)))
        return dict(vertices=len(pts),triangles=dynamic.get_triangle_count())
    if operation=='packages':
        registry=u.AssetRegistryHelpers.get_asset_registry();rows=[]
        for p in u.EditorAssetLibrary.list_assets(BASE):
            obj=u.load_asset(p);assert obj,p
            deps=[str(d) for d in registry.get_dependencies(obj.get_outermost().get_path_name(),u.AssetRegistryDependencyOptions(include_hard_package_references=True,include_soft_package_references=False,include_editor_only_package_references=True,include_game_package_references=True))]
            rows.append(dict(asset=p,dependencies=deps,missing=[d for d in deps if d.startswith('/Game/') and not u.EditorAssetLibrary.does_asset_exist(d)]))
        return write('packages',rows)
    if operation=='shutdown':
        state=audit.state()
        assert not state['dirty_maps'] and all(p=='/Engine/BasicShapes/BasicShapeMaterial' for p in state['dirty_content']),state
        write('editor-shutdown',state)
        u.SystemLibrary.quit_editor()
        return state
    if operation=='import_candidate':
        name=argument or 'Datum16_Bind01'
        assert name in ('Datum16_Bind01','Datum16_Bind02','Datum16_Bind03','Datum16_Bind04','Datum16_Bind05')
        assert not u.EditorAssetLibrary.does_asset_exist(BASE+'/'+name)
        task=u.AssetImportTask();task.filename=str(SOURCE/(name+'.fbx'))
        task.destination_path=BASE;task.destination_name=name;task.automated=True;task.save=True;task.replace_existing=False
        options=u.FbxImportUI();options.import_mesh=True;options.import_as_skeletal=True
        options.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH
        options.automated_import_should_detect_type=False;options.import_animations=False
        options.import_materials=False;options.import_textures=False;options.create_physics_asset=False
        data=options.skeletal_mesh_import_data
        data.import_uniform_scale=1.;data.convert_scene=True;data.convert_scene_unit=False;data.force_front_x_axis=False
        data.set_editor_property('use_t0_as_ref_pose',False)
        data.set_editor_property('update_skeleton_reference_pose',False)
        task.options=options
        u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        return write('import-'+name,dict(paths=list(task.imported_object_paths),state=audit.state()))
    if operation=='inspect_candidate':
        name=argument or 'Datum16_Bind01';mesh=u.load_asset(BASE+'/'+name);assert mesh
        skeleton=mesh.get_editor_property('skeleton');pose=skeleton.get_reference_pose()
        names=[str(n) for n in u.AnimPoseExtensions.get_bone_names(pose)]
        comp=u.new_object(u.SkeletalMeshComponent);comp.set_skeletal_mesh_asset(mesh)
        bones=[dict(name=n,parent=str(comp.get_parent_bone(n)),local_bind=audit.serial(u.AnimPoseExtensions.get_bone_pose(pose,n,u.AnimPoseSpaces.LOCAL)),component_bind=audit.serial(u.AnimPoseExtensions.get_bone_pose(pose,n,u.AnimPoseSpaces.WORLD))) for n in names]
        dynamic=u.DynamicMesh()
        copied=u.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(mesh,dynamic,u.GeometryScriptCopyMeshFromAssetOptions(),u.GeometryScriptMeshReadLOD())
        counts={};sums=[];maximum=0;invalid=0
        for i in range(dynamic.get_vertex_count()):
            _,weights,valid=dynamic.get_vertex_bone_weights(i);invalid+=not valid
            positive=[w for w in weights if w.weight>0];sums.append(sum(w.weight for w in positive));maximum=max(maximum,len(positive))
            for w in positive:
                n=str(comp.get_bone_name(w.bone_index));counts[n]=counts.get(n,0)+1
        result=dict(asset=mesh.get_path_name(),skeleton=skeleton.get_path_name(),bone_count=len(names),bones=bones,
            weights=dict(vertices=dynamic.get_vertex_count(),invalid=invalid,maximum_influences=maximum,sum_range=[min(sums),max(sums)],bone_vertex_counts=counts),
            bounds=audit.serial(mesh.get_bounds()),materials=[str(x.material_interface) for x in mesh.get_editor_property('materials')])
        write('inspect-'+name,result)
        return {k:v for k,v in result.items() if k!='bones'}
    if operation=='export_donor':
        state=audit.state()
        assert 'MeridianSquad.uproject' in state['project'] and not state['dirty_maps'] and not state['dirty_content'],state
        u.AssetRegistryHelpers.get_asset_registry().scan_paths_synchronous([BASE+'/Donor'],True)
        mesh=u.load_asset(DONOR)
        assert mesh,DONOR
        comp=u.new_object(u.SkeletalMeshComponent)
        comp.set_skeletal_mesh_asset(mesh)
        names=[str(comp.get_bone_name(i)) for i in range(comp.get_num_bones())]
        assert len(names)==161,names
        dest=SOURCE/'Donor/MSQ52_Manny161.fbx'
        dest.parent.mkdir(parents=True,exist_ok=True)
        assert not dest.exists()
        task=u.AssetExportTask()
        task.object=mesh; task.filename=str(dest); task.automated=True; task.prompt=False
        task.exporter=u.SkeletalMeshExporterFBX(); task.options=u.FbxExportOption()
        task.options.ascii=False; task.options.level_of_detail=False; task.options.export_morph_targets=False
        ok=u.Exporter.run_asset_export_task(task)
        return write('donor-export',dict(success=ok,asset=DONOR,bones=names,filename=str(dest),state=audit.state()))
    raise ValueError(operation)
