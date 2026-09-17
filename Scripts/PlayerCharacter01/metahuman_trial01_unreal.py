"""Bounded Creator trial. Experimental packages only; no gameplay or lobby edits."""
import json
import time
import traceback
from pathlib import Path
import unreal as u

ROOT = Path(u.Paths.project_dir()).resolve()
OUT = ROOT / 'Saved/PlayerCharacter01/MetaHumanTrial01/Worker'
ASSETS = ROOT / 'Assets/Source/PlayerCharacter01/MetaHumanTrial01'
PACKAGE = '/Game/Development/PlayerCharacter01/MetaHumanTrial01'

def write(name, data):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / (name + '.json')).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    return data

def action(operation, argument=''):
    if operation == 'inspect':
        editor = u.get_editor_subsystem(u.UnrealEditorSubsystem)
        result = dict(project=str(ROOT), engine=u.SystemLibrary.get_engine_version(),
            world=editor.get_editor_world().get_path_name(),
            dirty_content=[p.get_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_content_packages()],
            dirty_maps=[p.get_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()],
            classes=[x for x in dir(u) if 'MetaHuman' in x or 'ConformTarget' in x])
        if hasattr(u, 'MetaHumanCharacterEditorSubsystem'):
            sub = u.get_editor_subsystem(u.MetaHumanCharacterEditorSubsystem)
            result['subsystem'] = str(sub)
            result['api'] = {x: getattr(sub, x).__doc__ for x in dir(sub) if any(k in x for k in ['conform','export','pose','rig','edit','create','initialize'])}
        return write('live-inspect', result)
    if operation == 'api':
        result = {}
        for name in argument.split(','):
            cls = getattr(u, name)
            result[name] = dict(doc=cls.__doc__, members=[x for x in dir(cls) if not x.startswith('_')])
        return write('api-' + argument.split(',')[0], result)
    assert str(ROOT).replace('\\', '/').lower() == 'd:/devgames/meridiansquad'
    if operation == 'inspect_apose02':
        import animation_audit01_unreal as audit
        mesh=u.load_asset(PACKAGE+'/Solve02/APose/MH_Datum16_Trial01_Body')
        comp=u.new_object(u.SkeletalMeshComponent)
        comp.set_skeletal_mesh_asset(mesh)
        skeleton=mesh.get_editor_property('skeleton')
        names=[str(comp.get_bone_name(i)) for i in range(comp.get_num_bones())]
        contract=json.loads((ROOT/'Assets/Source/PlayerCharacter01/AnimationAudit01/rig-contract.json').read_text())
        expected={b['name']:b for b in contract['bones']}
        bones=[dict(name=n,parent=str(comp.get_parent_bone(n)),
            component_bind=audit.serial(comp.get_socket_transform(n,u.RelativeTransformSpace.RTS_COMPONENT))) for n in names]
        dynamic=u.DynamicMesh()
        copied=u.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(mesh,dynamic,
            u.GeometryScriptCopyMeshFromAssetOptions(),u.GeometryScriptMeshReadLOD())
        counts={}; invalid=0; maximum=0; sums=[]
        for i in range(dynamic.get_vertex_count()):
            _,weights,valid=dynamic.get_vertex_bone_weights(i)
            invalid+=not valid
            positive=[w for w in weights if w.weight>0]
            maximum=max(maximum,len(positive));sums.append(sum(w.weight for w in positive))
            for w in positive:
                n=str(comp.get_bone_name(w.bone_index));counts[n]=counts.get(n,0)+1
        result=dict(asset=mesh.get_path_name(),skeleton=skeleton.get_path_name(),bone_count=len(names),bones=bones,
            missing_contract_bones=sorted(set(expected)-set(names)),additional_bones=sorted(set(names)-set(expected)),
            parent_mismatches=[dict(name=b['name'],expected=expected[b['name']]['parent'],actual=b['parent']) for b in bones if b['name'] in expected and expected[b['name']]['parent']!=b['parent']],
            mesh_properties=audit.props(mesh,['physics_asset','post_process_anim_blueprint','lod_info']),
            skeleton_properties=audit.props(skeleton,['compatible_skeletons','sockets']),
            weights=dict(copy_result=str(copied),vertices=dynamic.get_vertex_count(),invalid=invalid,
                maximum_influences=maximum,weight_sum_range=[min(sums),max(sums)],weighted_bones=len(counts),bone_vertex_counts=counts),
            state=audit.state())
        write('apose-native-inspection',result)
        return {k:v for k,v in result.items() if k not in ('bones','weights','mesh_properties')}
    if operation == 'compatibility_probe02':
        import animation_audit01_unreal as audit
        audit.OUT=OUT/'Compatibility'
        audit.OUT.mkdir(exist_ok=True)
        audit.preview_setup()
        comp=audit.PREVIEW['components']['character']
        mesh=u.load_asset(PACKAGE+'/Solve02/APose/MH_Datum16_Trial01_Body')
        comp.set_skeletal_mesh_asset(mesh)
        comp.set_anim_instance_class(u.AnimPreviewInstance)
        path='/Game/InfimaGames/TacticalFPSAnimations/Weapons/AssaultRifle/Animations/Character/TP/Combat/A_TFA_TP_AR_Reload'
        anim=u.load_asset(path)
        assert anim
        before={n:audit.serial(comp.get_socket_transform(n,u.RelativeTransformSpace.RTS_COMPONENT)) for n in ['hand_l','hand_r','ik_hand_gun'] if comp.does_socket_exist(n)}
        inst=comp.get_anim_instance()
        inst.set_animation_asset(anim,False,1.)
        inst.set_playing(False)
        inst.set_position(1.,False)
        after={n:audit.serial(comp.get_socket_transform(n,u.RelativeTransformSpace.RTS_COMPONENT)) for n in ['hand_l','hand_r','ik_hand_gun'] if comp.does_socket_exist(n)}
        return write('compatibility-probe02',dict(candidate=mesh.get_path_name(),source_clip=path,
            source_settings=audit.props(anim,['skeleton','additive_anim_type','ref_pose_type','ref_pose_seq','ref_frame_index']),
            instance=str(inst),requested_time=1.,position=comp.get_position(),
            instance_properties=audit.props(inst,['current_asset']),before=before,after=after,
            has_ik_hand_gun=comp.does_socket_exist('ik_hand_gun'),
            note='Bounded direct-assignment eligibility probe using the existing MSQ-52 preview helper. This is not a playback or retarget pass.'))
    if operation in ('compatibility_pie02','compatibility_sample02'):
        import animation_audit01_unreal as audit
        audit.OUT=OUT/'Compatibility'
        if operation=='compatibility_pie02':
            audit.action('pie_bind','')
            comp=audit.PREVIEW['components']['character']
            inst=comp.get_anim_instance()
            anim=u.load_asset('/Game/InfimaGames/TacticalFPSAnimations/Weapons/AssaultRifle/Animations/Character/TP/Combat/A_TFA_TP_AR_Reload')
            inst.set_animation_asset(anim,False,1.)
            inst.set_playing(False)
            inst.set_position(1.,False)
            return {'sample_time':1.,'asset':str(inst.get_animation_asset()),'candidate':str(comp.get_skeletal_mesh_asset())}
        return audit.preview_sample('candidate-pie-at-one-second')
    if operation == 'candidate_playback_setup02':
        import animation_audit01_unreal as audit
        audit.OUT=OUT/'Compatibility'
        # Reuse the existing disposable preview world. Only the source carrier uses
        # the contract mesh; the measured character remains the new fitted surface.
        sub=u.get_editor_subsystem(u.EditorActorSubsystem)
        carrier=sub.spawn_actor_from_class(u.SkeletalMeshActor,u.Vector(0,0,0),transient=False)
        carrier.set_actor_label('MSQ52_Audit_reference')
        carrier.skeletal_mesh_component.set_skeletal_mesh_asset(u.load_asset('/Game/InfimaGames/TacticalFPSAnimations/Common/Characters/Mannequins/Meshes/SKM_Manny_Simple'))
        carrier.skeletal_mesh_component.set_editor_property('visibility_based_anim_tick_option',u.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
        carrier.set_actor_hidden_in_game(True)
        audit.action('reserve_setup','')
        audit.action('attachments','')
        audit.action('exposure_setup','')
        return {'carrier':carrier.get_path_name(),'purpose':'Diagnostic source weapon attachment only. Candidate lacks ik_hand_gun; no integration repair is implied.'}
    if operation == 'candidate_playback_bind02':
        import animation_audit01_unreal as audit
        audit.OUT=OUT/'Compatibility'
        audit.action('pie_bind','')
        audit.action('attachments_live','')
        audit.action('camera_named','body')
        comp=audit.PREVIEW['components']['character']
        assert 'MetaHumanTrial01' in comp.get_skeletal_mesh_asset().get_path_name()
        for i in range(comp.get_num_materials()):comp.set_material(i,u.load_asset('/Engine/BasicShapes/BasicShapeMaterial'))
        original=audit.preview_pose
        def candidate_pose(argument):
            candidate=audit.PREVIEW['components']['character']
            audit.PREVIEW['components']['character']=audit.PREVIEW['components']['reference']
            try: pose=original(argument)
            finally: audit.PREVIEW['components']['character']=candidate
            inst=candidate.get_anim_instance()
            anim=u.load_asset(pose['paths']['character'])
            inst.set_animation_asset(anim,False,1.)
            inst.set_playing(False)
            inst.set_position(pose['time'],False)
            pose['paths']['reference']=pose['paths']['character']
            pose['candidate_mesh']=candidate.get_skeletal_mesh_asset().get_path_name()
            pose['weapon_carrier']='Hidden original contract rig; candidate has no ik_hand_gun. Contact results are diagnostic only.'
            return pose
        audit.preview_pose=candidate_pose
        return write('candidate-playback-binding',dict(candidate=comp.get_skeletal_mesh_asset().get_path_name(),
            reference=audit.PREVIEW['components']['reference'].get_skeletal_mesh_asset().get_path_name(),
            interpretation='Direct native animation evaluation on the fitted mesh; source weapon motion uses a separate hidden source carrier. No retarget correction, new socket, or compatible-skeleton edit.'))
    if operation == 'candidate_playback_start02':
        import animation_audit01_unreal as audit
        return audit.playback_start(argument)
    if operation == 'candidate_playback_status02':
        import animation_audit01_unreal as audit
        return audit.action('playback_status','')
    if operation == 'final_packages02':
        registry=u.AssetRegistryHelpers.get_asset_registry()
        registry.scan_paths_synchronous([PACKAGE],True)
        rows=[]
        for path in u.EditorAssetLibrary.list_assets(PACKAGE):
            obj=u.load_asset(path)
            assert obj,path
            package=obj.get_outermost().get_path_name()
            hard=[str(d) for d in registry.get_dependencies(package,u.AssetRegistryDependencyOptions(
                include_hard_package_references=True,include_soft_package_references=False,
                include_editor_only_package_references=True,include_game_package_references=True))]
            rows.append(dict(asset=obj.get_path_name(),class_name=obj.get_class().get_name(),hard_dependencies=hard,
                missing_game_dependencies=[d for d in hard if d.startswith('/Game/') and not u.EditorAssetLibrary.does_asset_exist(d)]))
        return write('final-packages',rows)
    if operation == 'shutdown':
        import animation_audit01_unreal as audit
        assert not globals().get('PLAYBACK',{}).get('active')
        assert not getattr(audit,'PLAYBACK',{}).get('active')
        character=u.load_asset(PACKAGE+'/MH_Datum16_Trial01')
        u.get_editor_subsystem(u.AssetEditorSubsystem).close_all_editors_for_asset(character)
        before=audit.state()
        assert all(p.startswith('/Temp/') for p in before['dirty_maps']),before
        assert all(p.startswith(PACKAGE) or p=='/Engine/BasicShapes/BasicShapeMaterial' for p in before['dirty_content']),before
        for p in before['dirty_content']:
            if p.startswith(PACKAGE):u.EditorAssetLibrary.save_asset(p)
        u.EditorLoadingAndSavingUtils.load_map('/Engine/Maps/Entry')
        after=audit.state()
        write('editor-shutdown',dict(before=before,after=after,reason='Restore the pre-trial closed-editor state. Discard only this trial transient preview map.'))
        u.SystemLibrary.quit_editor()
        return {'shutdown_requested':True}
    if operation == 'import_input':
        assert not u.EditorAssetLibrary.does_asset_exist(PACKAGE + '/SM_Datum16_BodyOnly01')
        task = u.AssetImportTask()
        task.filename = str(ASSETS / 'Datum16_BodyOnly01.fbx')
        task.destination_path = PACKAGE
        task.destination_name = 'SM_Datum16_BodyOnly01'
        task.automated = True
        task.save = True
        task.replace_existing = False
        options = u.FbxImportUI()
        options.import_mesh = True
        options.import_as_skeletal = False
        options.mesh_type_to_import = u.FBXImportType.FBXIT_STATIC_MESH
        options.automated_import_should_detect_type = False
        options.import_materials = False
        options.import_textures = False
        options.static_mesh_import_data.combine_meshes = True
        options.static_mesh_import_data.generate_lightmap_u_vs = False
        options.static_mesh_import_data.auto_generate_collision = False
        options.static_mesh_import_data.import_uniform_scale = 1.0
        task.options = options
        task.factory = u.FbxFactory()
        u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        paths = list(task.imported_object_paths)
        result = {'paths': paths}
        for p in paths:
            mesh = u.load_asset(p)
            if isinstance(mesh, u.StaticMesh):
                vertices, indices = u.MetaHumanCharacterEditorSubsystem.get_mesh_data_for_conforming(mesh)
                coords = [[v.x,v.y,v.z] for v in vertices]
                result.update(vertices=len(vertices), triangles=len(indices)//3,
                    bounds_cm={'min':[min(v[i] for v in coords) for i in range(3)], 'max':[max(v[i] for v in coords) for i in range(3)]})
                write('input-unreal-geometry', dict(vertices=coords, triangles=list(indices)))
        return write('import-input', result)
    if operation == 'create_character':
        assert not u.EditorAssetLibrary.does_asset_exist(PACKAGE + '/MH_Datum16_Trial01')
        start = time.monotonic()
        character = u.AssetToolsHelpers.get_asset_tools().create_asset('MH_Datum16_Trial01', PACKAGE,
            u.MetaHumanCharacter, u.MetaHumanCharacterFactoryNew())
        assert character
        u.EditorAssetLibrary.save_loaded_asset(character)
        write('character-created', dict(path=character.get_path_name(), seconds=time.monotonic()-start))
        sub = u.get_editor_subsystem(u.MetaHumanCharacterEditorSubsystem)
        edited = sub.try_add_object_to_edit(character)
        return write('character-edit', dict(path=character.get_path_name(), added_for_edit=edited,
            seconds=time.monotonic()-start))
    if operation == 'open_character':
        character = u.load_asset(PACKAGE + '/MH_Datum16_Trial01')
        result = u.get_editor_subsystem(u.AssetEditorSubsystem).open_editor_for_assets([character])
        return write('open-character', dict(result=result))
    if operation == 'schedule_solve02':
        handle = None
        def run(_delta):
            u.unregister_slate_post_tick_callback(handle)
            try: action('solve02')
            except Exception: write('solve02-exception', dict(error=traceback.format_exc()))
        handle = u.register_slate_post_tick_callback(run)
        return {'scheduled': 'solve02', 'transport': 'Deferred one Slate tick so the MCP HTTP callback returns before the blocking solver.'}
    if operation == 'export_source_pose02':
        character = u.load_asset(PACKAGE + '/MH_Datum16_Trial01')
        mesh = u.load_asset(PACKAGE + '/SM_Datum16_BodyOnly01')
        key = u.MetaHumanCharacterTargetMeshKey(body_mesh=mesh)
        dest = ASSETS / 'Solve02/SourcePose'
        dest.mkdir(parents=True, exist_ok=True)
        params = u.MetaHumanPosedDNAExportParams(project_path=PACKAGE + '/Solve02/SourcePose',
            external_path=str(dest), target_mesh_key=key, asset_name='Datum16_Solve02_Posed',
            overwrite_existing_assets=False)
        u.MetaHumanCharacterExportBlueprintLibrary.export_posed_dna(character, params)
        geometry = u.MetaHumanGeometryExportParams(project_path=PACKAGE + '/Solve02/SourcePose',
            head_skeletal_mesh=False, body_skeletal_mesh=True, full_body_skeletal_mesh=False,
            overwrite_existing_assets=False)
        u.MetaHumanCharacterExportBlueprintLibrary.export_geometry(character, geometry)
        assets = u.EditorAssetLibrary.list_assets(PACKAGE + '/Solve02/SourcePose')
        exported = []
        for path in assets:
            obj = u.load_asset(path)
            u.EditorAssetLibrary.save_loaded_asset(obj)
            if isinstance(obj, u.SkeletalMesh):
                task = u.AssetExportTask()
                task.object = obj
                task.filename = str(dest / (obj.get_name()+'.fbx'))
                task.automated = True
                task.prompt = False
                task.options = u.FbxExportOption()
                task.options.level_of_detail = False
                task.options.export_morph_targets = False
                task.options.ascii = False
                task.exporter = u.SkeletalMeshExporterFBX()
                exported.append(dict(asset=path, success=u.Exporter.run_asset_export_task(task), filename=task.filename))
        return write('export-sourcepose02', dict(assets=list(assets), exported=exported, files=[p.name for p in dest.iterdir()]))
    if operation == 'dna_capability':
        cls = u.load_class(None, '/Script/RigLogicModule.DNAConfigHolder')
        obj = u.new_object(cls)
        try: config = obj.get_editor_property('Config')
        except Exception as exc: config = str(exc)
        return write('dna-capability', dict(holder=str(obj), config=str(config),
            manager={n:getattr(u.InterchangeManager,n).__doc__ for n in dir(u.InterchangeManager) if 'import' in n},
            parameters=u.ImportAssetParameters.__doc__))
    if operation == 'select_dna02':
        character = u.load_asset(PACKAGE + '/MH_Datum16_Trial01')
        u.get_editor_subsystem(u.AssetEditorSubsystem).close_all_editors_for_asset(character)
        u.EditorAssetLibrary.sync_browser_to_objects([PACKAGE + '/Solve02/SourcePose/Datum16_Solve02_Posed'])
        return {'selected': PACKAGE + '/Solve02/SourcePose/Datum16_Solve02_Posed'}
    if operation == 'generate_posed_mesh02':
        # Default native holder config is retained; output axes and bind pose must be measured.
        source = ASSETS / 'Solve02/SourcePose/Datum16_Solve02_Posed.dna'
        temp = OUT / 'Datum16_Solve02_Posed.mhdna'
        temp.write_bytes(source.read_bytes())
        source_data = u.InterchangeManager.create_source_data(str(temp))
        holder = u.new_object(u.load_class(None, '/Script/RigLogicModule.DNAConfigHolder'), outer=source_data)
        source_data.set_context_object_by_tag('DNAConfig', holder)
        params = u.ImportAssetParameters(is_automated=True, replace_existing=False,
            destination_name='SK_Datum16_PosedDNA02', override_pipelines=[u.SoftObjectPath('/MetaHumanSDK/DefaultDNAPipeline.DefaultDNAPipeline')])
        result = u.InterchangeManager.get_interchange_manager_scripted().import_asset(
            PACKAGE + '/Solve02/GeneratedFromDNA', source_data, params)
        return write('generate-posedmesh02', dict(assets=[o.get_path_name() for o in result or []], source=str(source), temporary_input=str(temp)))
    if operation == 'export_apose02':
        character = u.load_asset(PACKAGE + '/MH_Datum16_Trial01')
        sub = u.get_editor_subsystem(u.MetaHumanCharacterEditorSubsystem)
        if not sub.is_object_added_for_editing(character):
            assert sub.try_add_object_to_edit(character)
        key = u.MetaHumanCharacterTargetMeshKey(body_mesh=u.load_asset(PACKAGE+'/SM_Datum16_BodyOnly01'))
        sub.commit_posed_state_as_a_pose(character, key)
        u.EditorAssetLibrary.save_loaded_asset(character)
        dest=ASSETS/'Solve02/APose'
        dest.mkdir(parents=True,exist_ok=True)
        dna_params=u.MetaHumanDNAExportParams(project_path=PACKAGE+'/Solve02/APose/DNA',
            external_path=str(dest), dna_head=False, dna_body=True, overwrite_existing_assets=False)
        u.MetaHumanCharacterExportBlueprintLibrary.export_dna(character,dna_params)
        geometry=u.MetaHumanGeometryExportParams(project_path=PACKAGE+'/Solve02/APose',
            head_skeletal_mesh=False, body_skeletal_mesh=True, full_body_skeletal_mesh=False, overwrite_existing_assets=False)
        u.MetaHumanCharacterExportBlueprintLibrary.export_geometry(character,geometry)
        return action('save_apose02')
    if operation in ('export_generated02','save_apose02'):
        apose=operation=='save_apose02'
        paths = u.EditorAssetLibrary.list_assets(PACKAGE + ('/Solve02/APose' if apose else '/Solve02/GeneratedFromDNA'))
        results = []
        dest = ASSETS / ('Solve02/APose' if apose else 'Solve02/SourcePose')
        for path in paths:
            obj = u.load_asset(path)
            saved = u.EditorAssetLibrary.save_loaded_asset(obj)
            entry = dict(path=path, type=obj.get_class().get_name(), saved=saved)
            if isinstance(obj, u.SkeletalMesh):
                task = u.AssetExportTask()
                task.object = obj
                task.filename = str(dest / (obj.get_name()+'.fbx'))
                task.automated = True
                task.prompt = False
                task.exporter = u.SkeletalMeshExporterFBX()
                task.options = u.FbxExportOption()
                task.options.level_of_detail = False
                task.options.export_morph_targets = False
                task.options.ascii = False
                entry['export_success'] = u.Exporter.run_asset_export_task(task)
                entry['export_file'] = task.filename
            results.append(entry)
        return write('export-apose02' if apose else 'export-generated02', results)
    if operation in ('solve01', 'solve02'):
        attempt = operation
        assert not (OUT / (attempt + '-start.json')).exists(), 'Retain every attempt; never rerun under the same identity'
        character = u.load_asset(PACKAGE + '/MH_Datum16_Trial01')
        mesh = u.load_asset(PACKAGE + '/SM_Datum16_BodyOnly01')
        sub = u.get_editor_subsystem(u.MetaHumanCharacterEditorSubsystem)
        assert sub.is_object_added_for_editing(character)
        vertices, indices = sub.get_mesh_data_for_conforming(mesh)
        target = u.ConformTargetMesh(target_parts_type=u.TargetPartsType.BODY_ONLY,
            body_vertices=vertices, body_vertex_indices=indices)
        settings = u.BodyConformSolveSettings(pipeline_name='body_only')
        params = u.ConformTargetParams(conform_target_mesh=target, auto_solve=True,
            estimate_body_joints_from_mesh=False, body_conform_solve_settings=settings)
        if attempt == 'solve02':
            params.image_size = u.IntPoint(1024, 1024)
            params.camera_view_info = u.MinimalViewInfo(location=u.Vector(0, 300, 100),
                rotation=u.Rotator(0, -90, 0), fov=45.0, aspect_ratio=1.0)
        key = u.MetaHumanCharacterTargetMeshKey(body_mesh=mesh)
        start = time.monotonic()
        write(attempt + '-start', dict(time=time.time(), character=character.get_path_name(), mesh=mesh.get_path_name(),
            vertices=len(vertices), triangles=len(indices)//3, pipeline='body_only', auto_solve=True,
            keypoints={}, settings=str(settings), image_size=str(params.image_size),
            source='Installed Creator Auto Solve body-only defaults'))
        ok = sub.conform_to_target_meshes(character, key, params)
        u.EditorAssetLibrary.save_loaded_asset(character)
        return write(attempt + '-result', dict(success=ok, seconds=time.monotonic()-start))
    raise ValueError(operation)
