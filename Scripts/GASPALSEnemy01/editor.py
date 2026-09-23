"""Source inspection and isolated derived-asset authoring. Never save GASPALS sources."""
import json
from pathlib import Path
import unreal as u

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/CombatSlice01/GASPALSEnemy01'
OUT.mkdir(parents=True, exist_ok=True)
RIFLE = '/GASPALS/OverlaySystem/Overlays/Poses/Rifle/'


def state():
    assert ROOT.resolve() == Path('D:/devgames/MeridianSquad').resolve()
    sub = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    pie = u.EditorLevelLibrary.get_pie_worlds(False)
    world = sub.get_game_world() if pie else sub.get_editor_world()
    return dict(project=str(ROOT), engine=u.SystemLibrary.get_engine_version(),
                map=world.get_path_name() if world else None, pie=[w.get_path_name() for w in pie],
                dirty=[p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_content_packages()] +
                      [p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()])


def graph_dump(bp):
    graphs = []
    for graph in u.BlueprintEditorLibrary.list_graphs(bp):
        nodes = []
        for node in u.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes():
            try:
                nodes.append(dict(name=node.get_name(), title=node.get_node_title(),
                    pins=[dict(name=str(p.get_pin_name()), type=str(p.get_pin_type_display_string()), value=p.get_pin_value(),
                               links=[c.get_owning_node().get_name()+':'+str(c.get_pin_name()) for c in p.list_connected_pins()])
                          for p in node.list_all_pins()]))
            except Exception:
                nodes.append(dict(name=node.get_name()))
        graphs.append(dict(name=graph.get_name(), nodes=nodes))
    return graphs


def _run(operation, argument=''):
    current = state()
    if operation == 'aim_diagnosis':
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        rows=[]
        for fixture in u.GameplayStatics.get_all_actors_of_class(world,u.GASPEnemyFixture):
            body=fixture.body
            anim=body.get_anim_instance()
            barrel=fixture.rifle.get_right_vector()
            direction=u.Vector(*json.loads(fixture.get_dummy_state(False))['gasp']['aim_direction'])
            rows.append(dict(profile=fixture.reaction_profile,aim=str(direction),barrel=str(barrel),
                dot=u.MathLibrary.dot_vector_vector(barrel,direction),
                mesh=str(body.get_world_transform()),root=str(body.get_socket_transform('root')),
                properties={name:str(anim.get_editor_property(name)) for name in ['AO','RootTransform','RifleAimAlpha']}))
        (OUT/('aim-diagnosis-'+argument+'.json')).write_text(json.dumps(rows,indent=2))
        return rows
    if operation == 'inspect_rifle_pose':
        import math
        result={}
        prop=u.load_asset('/GASPALSEnemy01/OverlaySystem/Props/Meshes/M4A1')
        result['bounds']=str(prop.get_bounds())
        result['barrel_calibration']=[]
        options=u.AnimPoseEvaluationOptions()
        options.evaluation_type=u.AnimDataEvalType.COMPRESSED
        for name in ['Pose_Rifle_Stand_Aim_Idle','Pose_Rifle_Stand_Aim_Move','Pose_Rifle_Crouch_Aim','AO_Rifle_Stand_Sweep','AO_Rifle_Crouch_Sweep']:
            clip=u.load_asset('/GASPALSEnemy01/Animations/'+name)
            pose=u.AnimPoseExtensions.get_anim_pose_at_frame(clip,0,u.AnimPoseEvaluationOptions())
            result[name]={bone:str(u.AnimPoseExtensions.get_bone_pose(pose,bone,u.AnimPoseSpaces.WORLD)) for bone in ['root','pelvis','spine_01','spine_05','hand_l','hand_r','ik_hand_gun','ik_hand_l']}
            for frame in ([5,10,15,20,25] if name.startswith('AO_') else [0]):
                pose=u.AnimPoseExtensions.get_anim_pose_at_frame(clip,frame,options)
                hand=u.AnimPoseExtensions.get_bone_pose(pose,'hand_r',u.AnimPoseSpaces.WORLD)
                local=u.Vector(-math.sin(math.radians(75)),math.cos(math.radians(75)),0)
                direction=u.MathLibrary.transform_direction(hand,local)
                result['barrel_calibration'].append(dict(name=name,frame=frame,yaw=math.degrees(math.atan2(direction.y,direction.x)),pitch=math.degrees(math.asin(direction.z))))
        (OUT/'rifle-pose-audit.json').write_text(json.dumps(result,indent=2))
        return result
    if operation == 'conversion_nodes':
        bp=u.load_asset('/GASPEnemyFoundation01/Blueprints/SandboxCharacter_Mover_ABP')
        ed=u.BlueprintGraphEditor.get_graph_editor(u.BlueprintEditorLibrary.find_graph(bp,'AnimGraph'))
        return dict(modes=[x for x in dir(u.BoneModificationMode) if x.isupper()])
    if operation == 'dependencies':
        registry=u.AssetRegistryHelpers.get_asset_registry()
        registry.scan_paths_synchronous(['/GASPALSEnemy01'],True)
        options=u.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True)
        packages=[str(a.package_name) for a in registry.get_assets_by_path('/GASPALSEnemy01',recursive=True)]
        packages.append('/GASPEnemyFoundation01/Blueprints/SandboxCharacter_Mover_ABP')
        rows={p:[str(d) for d in registry.get_dependencies(p,options)] for p in sorted(set(packages))}
        external={p:[d for d in deps if d.startswith('/GASPALS/')] for p,deps in rows.items()}
        result=dict(state=current,packages=rows,external={p:d for p,d in external.items() if d})
        (OUT/'dependency-closure.json').write_text(json.dumps(result,indent=2))
        return dict(packages=len(rows),external=result['external'],state=current)
    if operation == 'clean_pose_authoring_references':
        assert not current['pie']
        mesh=u.load_asset('/GASPEnemyFoundation01/Characters/UEFN_Mannequin/Meshes/SKM_UEFN_Mannequin')
        rows=[]
        registry=u.AssetRegistryHelpers.get_asset_registry()
        for data in registry.get_assets_by_path('/GASPALSEnemy01/Animations',recursive=True):
            pose=data.get_asset()
            pose.set_preview_skeletal_mesh(mesh)
            before=str(pose.get_editor_property('asset_user_data'))
            pose.set_editor_property('asset_user_data',[])
            u.AssetToolsHelpers.get_asset_tools().rename_referencing_soft_object_paths(
                [pose.get_outer()],
                {u.SoftObjectPath('/GASPALS/Characters/UEFN_Mannequin/Meshes/SKM_UEFN_Mannequin.SKM_UEFN_Mannequin'):
                 u.SoftObjectPath(mesh.get_path_name())})
            assert u.EditorAssetLibrary.save_loaded_asset(pose,only_if_is_dirty=False)
            rows.append(dict(pose=pose.get_path_name(),removed_authoring_metadata=before))
        (OUT/'pose-authoring-reference-cleanup.json').write_text(json.dumps(rows,indent=2))
        return dict(poses=len(rows))
    if operation == 'skeleton_compare':
        result = json.loads(u.GASPALSAnimationLibrary.compare_skeletons(
            u.load_asset('/GASPALS/Characters/UEFN_Mannequin/Meshes/SK_UEFN_Mannequin'),
            u.load_asset('/GASPEnemyFoundation01/Characters/UEFN_Mannequin/Meshes/SK_UEFN_Mannequin')))
        (OUT/'skeleton-compare.json').write_text(json.dumps(result,indent=2))
        return result
    if operation == 'diagnose_graph':
        result={}
        for name in ['reparent_blueprint','compile_blueprint']:
            result[name]=str(getattr(u.BlueprintEditorLibrary,name).__doc__)
        bp=u.load_asset('/GASPALSEnemy01/Blueprints/ABP_GASPALS_Enemy')
        result['parent']=str(u.BlueprintEditorLibrary.get_blueprint_parent_class(bp))
        result['graphs']=graph_dump(bp)
        (OUT/'graph-author-diagnostic.json').write_text(json.dumps(result,indent=2))
        return {k:v for k,v in result.items() if k!='graphs'}
    if operation.startswith('harness_'):
        import importlib
        from Scripts.GASPALSEnemy01 import harness
        if operation == 'harness_prepare':
            importlib.reload(harness)
        return harness.action(operation.removeprefix('harness_'),argument)
    if operation.startswith('runtime_'):
        from Scripts.GASPEnemyFoundation01 import pilot98
        return pilot98.run(operation.removeprefix('runtime_'), argument)
    if operation == 'console':
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        assert world and argument.startswith('msq.EnemyRifle ')
        u.SystemLibrary.execute_console_command(world,argument)
        return dict(command=argument)
    if operation in ['import_poses','import_prop','author_graph']:
        import importlib
        from Scripts.GASPALSEnemy01 import author
        importlib.reload(author)
        return author.run(operation)
    if operation == 'state':
        (OUT / 'editor-state.json').write_text(json.dumps(current, indent=2))
        return current
    if operation == 'handoff':
        assert not current['pie'] and not current['dirty'], current
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
        current['transient_fixtures']=[a.get_path_name() for a in u.GameplayStatics.get_all_actors_of_class(world,u.GASPEnemyFixture)]
        current['transient_controllers']=[a.get_path_name() for a in u.GameplayStatics.get_all_actors_of_class(world,u.GASPEnemyCommandController)]
        current['source_registry_assets']=len(u.AssetRegistryHelpers.get_asset_registry().get_assets_by_path('/GASPALS',recursive=True))
        current['command_line']=u.SystemLibrary.get_command_line()
        from Scripts.GASPEnemyFoundation01 import pilot98
        current['performance']=pilot98.run('editor_state')
        assert not current['transient_fixtures'] and not current['transient_controllers'] and current['source_registry_assets']==0
        (OUT/'final-editor-state.json').write_text(json.dumps(current,indent=2))
        return current
    if operation == 'close':
        assert not current['pie'] and all(p.startswith('/GASPALSEnemy01/') for p in current['dirty']), current
        for package in current['dirty']:
            assert u.EditorAssetLibrary.save_asset(package)
        u.SystemLibrary.quit_editor()
        return current
    if operation == 'audit':
        registry = u.AssetRegistryHelpers.get_asset_registry()
        registry.scan_paths_synchronous(['/GASPALS'], True)
        result = dict(state=current, sequences=[], graphs={})
        for data in registry.get_assets_by_path(RIFLE.rstrip('/'), recursive=True):
            obj = data.get_asset()
            if isinstance(obj, u.AnimSequence):
                row = dict(path=obj.get_path_name(), skeleton=str(obj.get_editor_property('skeleton')),
                           length=obj.get_play_length(), curves=str(u.AnimationLibrary.get_animation_curve_names(obj, u.RawCurveTrackTypes.RCT_FLOAT)))
                for prop in ['additive_anim_type', 'ref_pose_type', 'ref_pose_seq', 'ref_frame_index']:
                    row[prop] = str(obj.get_editor_property(prop))
                result['sequences'].append(row)
        for path in [RIFLE+'ABP_Overlay_Rifle', '/GASPALS/OverlaySystem/Overlays/ABP_OverlayPose_Base',
                     '/GASPEnemyFoundation01/Blueprints/SandboxCharacter_Mover_ABP',
                     '/GASPEnemyFoundation01/Blueprints/SandboxCharacter_Mover']:
            bp = u.load_asset(path)
            if bp:
                result['graphs'][path] = graph_dump(bp)
        prop = u.load_asset('/GASPALS/OverlaySystem/Overlays/Poses/Rifle/DA_Overlay_Rifle')
        result['rifle_data'] = str(prop)
        result['apis'] = {name: str(getattr(u.AnimationLibrary, name).__doc__) for name in dir(u.AnimationLibrary)
                          if 'bone' in name or 'skeleton' in name or 'curve' in name}
        (OUT / 'source-audit.json').write_text(json.dumps(result, indent=2))
        return {k:v for k,v in result.items() if k not in ['graphs','apis']}
    if operation == 'inspect_route':
        assert not current['pie']
        source = u.load_asset(RIFLE+'Pose_Rifle_Stand_Aim_Idle')
        target = '/GASPALSEnemy01/Animations/Pose_Rifle_Stand_Aim_Idle'
        pose = u.load_asset(target) if u.EditorAssetLibrary.does_asset_exist(target) else u.EditorAssetLibrary.duplicate_asset(source.get_path_name(), target)
        skel = u.load_asset('/GASPEnemyFoundation01/Characters/UEFN_Mannequin/Meshes/SK_UEFN_Mannequin')
        # The native authoring seam assigns only a checked same-hierarchy skeleton.
        if hasattr(u, 'GASPALSAnimationLibrary'):
            assert u.GASPALSAnimationLibrary.assign_skeleton(pose, skel)
            assert u.EditorAssetLibrary.save_loaded_asset(pose)
        result = dict(derived=pose.get_path_name(), skeleton=str(pose.get_editor_property('skeleton')), graphs={}, properties={})
        for path in ['/GASPALS/OverlaySystem/Overlays/Poses/ABP_OverlayPose_Base', '/GASPALS/OverlaySystem/ABP_LayerBlending']:
            bp = u.load_asset(path)
            result['graphs'][path] = graph_dump(bp)
        bp = u.load_asset('/GASPALS/OverlaySystem/Blueprints/Data/PDA_OverlayPose')
        data = u.load_asset(RIFLE+'DA_Overlay_Rifle')
        for name in u.BlueprintEditorLibrary.list_member_variable_names(bp, True):
            try:
                result['properties'][name] = str(data.get_editor_property(name))
            except Exception:
                pass
        bp = u.load_asset('/GASPEnemyFoundation01/Blueprints/SandboxCharacter_Mover_ABP')
        ed = u.BlueprintGraphEditor.get_graph_editor(u.BlueprintEditorLibrary.find_graph(bp,'AnimGraph'))
        result['available_nodes'] = [x for x in ed.list_available_nodes([]) if any(s in x.lower() for s in ['blend','sequence','snapshot','bone'])]
        result['graph_api'] = {name:str(getattr(ed,name).__doc__) for name in dir(ed) if not name.startswith('_')}
        node = next(n for n in ed.list_all_nodes() if 'BlendListByInt' in n.get_name())
        result['node_api'] = {name:str(getattr(node,name).__doc__) for name in dir(node) if not name.startswith('_')}
        (OUT / 'route-audit.json').write_text(json.dumps(result, indent=2))
        return {k:v for k,v in result.items() if k not in ['graphs','available_nodes','graph_api','node_api']}
    raise ValueError(operation)


def run(operation, argument=''):
    try:
        return _run(operation, argument)
    except Exception:
        import traceback
        error=traceback.format_exc()
        (OUT/'last-editor-error.txt').write_text(error)
        return {'error':error}
