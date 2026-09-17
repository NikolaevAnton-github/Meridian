"""MSQ-52 read-only asset audit and disposable preview fixtures."""
import json
import time
from pathlib import Path
import unreal as u

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/PlayerCharacter01/AnimationAudit01/Worker'
SOURCE = ROOT / 'Assets/Source/PlayerCharacter01/AnimationAudit01'


def serial(value):
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, u.Object):
        return value.get_path_name()
    if isinstance(value, u.Transform):
        return dict(translation=serial(value.translation), rotation_xyzw=serial(value.rotation), scale=serial(value.scale3d))
    if isinstance(value, u.Vector):
        return [value.x, value.y, value.z]
    if isinstance(value, u.Quat):
        return [value.x, value.y, value.z, value.w]
    if isinstance(value, (u.Array, list, tuple)):
        return [serial(v) for v in value]
    return str(value)


def props(obj, names):
    result = {}
    for name in names:
        try:
            result[name] = serial(obj.get_editor_property(name))
        except Exception as e:
            result[name] = {'unavailable': str(e)}
    return result


def inspect_assets():
    manifest = json.loads((SOURCE / 'selected-sources.json').read_text())
    registry = u.AssetRegistryHelpers.get_asset_registry()
    rows, rigs, dependencies, blends = [], {}, [], {}
    hard = u.AssetRegistryDependencyOptions(include_hard_package_references=True, include_soft_package_references=False,
        include_editor_only_package_references=True, include_game_package_references=True)
    soft = u.AssetRegistryDependencyOptions(include_hard_package_references=False, include_soft_package_references=True,
        include_editor_only_package_references=True, include_game_package_references=True)
    for entry in manifest['files']:
        p = entry['package']
        deps = {}
        for kind, options in [('hard',hard), ('soft',soft)]:
            deps[kind] = [str(d) for d in registry.get_dependencies(p, options)]
        deps['package'] = p
        deps['missing_hard'] = [d for d in deps['hard'] if d.startswith('/Game/') and not u.EditorAssetLibrary.does_asset_exist(d)]
        deps['missing_soft'] = [d for d in deps['soft'] if d.startswith('/Game/') and not u.EditorAssetLibrary.does_asset_exist(d)]
        dependencies.append(deps)
        data = registry.get_asset_by_object_path(p + '.' + p.rsplit('/',1)[1])
        cls = str(data.asset_class_path.asset_name)
        if cls not in ['AnimSequence', 'BlendSpace', 'BlendSpace1D', 'Skeleton', 'SkeletalMesh']:
            continue
        obj = u.load_asset(p)
        row = dict(package=p, type=cls, loaded=obj is not None)
        if not obj:
            rows.append(row)
            continue
        if isinstance(obj, u.AnimSequence):
            row.update(props(obj, ['skeleton', 'sequence_length', 'rate_scale', 'enable_root_motion',
                'force_root_lock', 'root_motion_root_lock', 'additive_anim_type', 'ref_pose_type',
                'ref_pose_seq', 'ref_frame_index', 'retarget_source', 'interpolation']))
            row['tracks'] = [str(b) for b in u.AnimationLibrary.get_animation_track_names(obj)]
            row['notify_tracks'] = [str(b) for b in u.AnimationLibrary.get_animation_notify_track_names(obj)]
            row['notifies'] = []
            for e in u.AnimationLibrary.get_animation_notify_events(obj):
                n = props(e, ['notify_name','notify','notify_state_class'])
                n['time'] = u.AnimationLibrary.get_anim_notify_event_trigger_time(e)
                n['duration'] = u.AnimationLibrary.get_anim_notify_event_duration(e)
                row['notifies'].append(n)
            row['sampled_component_positions'] = []
            for t in [0., obj.get_play_length() * .25, obj.get_play_length() * .5, obj.get_play_length() * .75]:
                pose = obj.get_anim_pose_at_time(t, u.AnimPoseEvaluationOptions())
                names = {str(n) for n in u.AnimPoseExtensions.get_bone_names(pose)}
                bones = ['root','pelvis','head','hand_l','hand_r','foot_l','foot_r','ball_l','ball_r','ik_hand_gun','magazine','trigger']
                row['sampled_component_positions'].append(dict(time=t, bones={b:serial(u.AnimPoseExtensions.get_bone_pose(pose,b,u.AnimPoseSpaces.WORLD).translation) for b in bones if b in names}))
        elif isinstance(obj, u.SkeletalMesh):
            row.update(props(obj,['skeleton','physics_asset','post_process_anim_blueprint','asset_import_data']))
            comp = u.new_object(u.SkeletalMeshComponent)
            comp.set_skeletal_mesh_asset(obj)
            row['bones'] = [dict(index=i, name=str(comp.get_bone_name(i)), parent=str(comp.get_parent_bone(comp.get_bone_name(i))),
                                local_bind=serial(comp.get_ref_pose_transform(i))) for i in range(comp.get_num_bones())]
            row['sockets'] = [str(n) for n in comp.get_all_socket_names() if str(n) not in [b['name'] for b in row['bones']]]
            row['bounds'] = str(obj.get_bounds())
            try:
                row['import_filenames'] = list(obj.get_editor_property('asset_import_data').extract_filenames())
            except Exception as e:
                row['import_filenames'] = str(e)
        elif isinstance(obj, u.Skeleton):
            pose = obj.get_reference_pose()
            names = u.AnimPoseExtensions.get_bone_names(pose)
            rig = dict(package=p, bones=[dict(name=str(n), local_bind=serial(u.AnimPoseExtensions.get_bone_pose(pose,n)),
                       component_bind=serial(u.AnimPoseExtensions.get_bone_pose(pose,n,u.AnimPoseSpaces.WORLD))) for n in names],
                       properties=props(obj,['compatible_skeletons','preview_skeletal_mesh','sockets','virtual_bones','slot_groups']))
            rigs[obj.get_name()] = rig
        else:
            blends[p] = props(obj,['sample_data','blend_parameters','skeleton'])
        rows.append(row)
    write('assets',rows)
    write('dependencies',dependencies)
    write('rigs',rigs)
    write('blendspaces',blends)
    return dict(assets=len(rows),rigs=list(rigs),blends=len(blends),missing_hard=[x for x in dependencies if x['missing_hard']])


def details():
    rows = json.loads((OUT/'assets.json').read_text())
    result = dict(blends={}, meshes={}, animation_api={})
    for row in rows:
        if row['type'].startswith('BlendSpace'):
            obj=u.load_asset(row['package'])
            result['blends'][row['package']] = dict(
                samples=[props(s,['animation','sample_value','rate_scale']) for s in obj.get_editor_property('sample_data')],
                parameters=[props(s,['display_name','min','max','grid_num']) for s in obj.get_editor_property('blend_parameters')])
        if row['type']=='SkeletalMesh' and ('Mannequins' in row['package'] or 'AssaultRifle' in row['package']):
            obj=u.load_asset(row['package'])
            comp=u.new_object(u.SkeletalMeshComponent)
            comp.set_skeletal_mesh_asset(obj)
            bones={str(comp.get_bone_name(i)) for i in range(comp.get_num_bones())}
            result['meshes'][row['package']]=dict(sockets=[dict(name=str(n),bone=str(comp.get_socket_bone_name(n)),
                component_transform=serial(comp.get_socket_transform(n,u.RelativeTransformSpace.RTS_COMPONENT)))
                for n in comp.get_all_socket_names() if str(n) not in bones],
                import_data=props(obj.get_editor_property('asset_import_data'),['import_translation','import_rotation','import_uniform_scale','convert_scene','convert_scene_unit','force_front_x_axis','use_t0_as_ref_pose','update_skeleton_reference_pose']))
    for name in ['AnimSingleNodeInstance','EditorLevelLibrary','EditorLoadingAndSavingUtils','SkeletalMeshComponent','LevelSequenceEditorBlueprintLibrary']:
        result['animation_api'][name]=dict(members=dir(getattr(u,name,None)))
    return write('details',result)


def preview_setup():
    global PREVIEW
    before=state()
    assert all(p.startswith('/Temp/Untitled') for p in before['dirty_maps']), before
    assert all(p == '/Engine/BasicShapes/BasicShapeMaterial' for p in before['dirty_content']), before
    assert 'MeridianSquad' in before['project']
    world=u.EditorLoadingAndSavingUtils.new_blank_map(False)
    sub=u.get_editor_subsystem(u.EditorActorSubsystem)
    light=sub.spawn_actor_from_class(u.DirectionalLight,u.Vector(0,0,300),u.Rotator(pitch=-35,yaw=-130,roll=0),transient=False)
    light.light_component.set_editor_property('intensity',50000.)
    sky=sub.spawn_actor_from_class(u.SkyLight,u.Vector(0,0,200),transient=False)
    sky.light_component.set_editor_property('intensity',1.)
    base='/Game/InfimaGames/TacticalFPSAnimations/'
    mesh_paths=dict(character=base+'Common/Characters/Mannequins/Meshes/SKM_Manny_Simple',
                    weapon=base+'Weapons/AssaultRifle/Meshes/SK_TFA_AR',
                    magazine=base+'Weapons/AssaultRifle/Meshes/SK_TFA_AR_Magazine')
    PREVIEW=dict(actors={},components={},before=before)
    for name,path in mesh_paths.items():
        actor=sub.spawn_actor_from_class(u.SkeletalMeshActor,u.Vector(0,0,0),transient=False)
        actor.set_actor_label('MSQ52_Audit_'+name)
        comp=actor.skeletal_mesh_component
        comp.set_skeletal_mesh_asset(u.load_asset(path))
        comp.set_anim_instance_class(u.AnimPreviewInstance)
        comp.set_update_animation_in_editor(True)
        comp.set_editor_property('visibility_based_anim_tick_option',u.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
        PREVIEW['actors'][name]=actor
        PREVIEW['components'][name]=comp
    u.EditorLevelLibrary.set_level_viewport_camera_info(u.Vector(140,220,175),u.Rotator(pitch=-14,yaw=-122,roll=0))
    return write('preview-setup',dict(state=state(),instances={n:str(c.get_anim_instance()) for n,c in PREVIEW['components'].items()},
        instance_api=str(u.AnimPreviewInstance.set_animation_asset.__doc__)))


def preview_pose(argument):
    view,variant,seconds=argument.split(':')
    seconds=float(seconds)
    base='/Game/InfimaGames/TacticalFPSAnimations/'
    c=PREVIEW['components']['character']
    mesh=base+'Common/Characters/Mannequins/Meshes/'+('SKM_FP_Manny_Simple' if view=='FP' else 'SKM_Manny_Simple')
    c.set_skeletal_mesh_asset(u.load_asset(mesh))
    c.set_anim_instance_class(u.AnimPreviewInstance)
    paths=dict(character=base+f'Weapons/AssaultRifle/Animations/Character/{view}/Combat/A_TFA_{view}_AR_{variant}',
               weapon=base+f'Weapons/AssaultRifle/Animations/Weapon/{view}/A_TFA_{view}_WEP_AR_{variant}')
    for n,p in paths.items():
        comp=PREVIEW['components'][n]
        inst=comp.get_anim_instance()
        anim=u.load_asset(p)
        assert anim,p
        inst.set_animation_asset(anim,False,1.)
        inst.set_playing(False)
        inst.set_position(seconds,False)
    rules=[u.AttachmentRule.SNAP_TO_TARGET]*3
    PREVIEW['actors']['weapon'].attach_to_component(c,'ik_hand_gun',*rules,False)
    PREVIEW['actors']['magazine'].attach_to_component(PREVIEW['components']['weapon'],'SOCKET_Magazine',*rules,False)
    if 'reserve' in PREVIEW['actors']:
        PREVIEW['actors']['reserve'].attach_to_component(PREVIEW['components']['weapon'],'SOCKET_Magazine_Reserve',*rules,False)
        show,hide={('FP',False):(.455137,2.520381),('FP',True):(.860815,.433333),
                   ('TP',False):(.256150,1.944525),('TP',True):(.572721,.350720)}[(view,'Empty' in variant)]
        PREVIEW['actors']['magazine'].set_actor_hidden_in_game(seconds>=hide)
        PREVIEW['actors']['reserve'].set_actor_hidden_in_game(seconds<show)
    PREVIEW['pose']=dict(view=view,variant=variant,time=seconds,paths=paths)
    return PREVIEW['pose']


def preview_sample(argument):
    data=dict(pose=PREVIEW.get('pose'),components={})
    for n,c in PREVIEW['components'].items():
        data['components'][n]=dict(transform=serial(c.get_world_transform()),
            bones={str(b):serial(c.get_socket_transform(b,u.RelativeTransformSpace.RTS_WORLD))
                   for b in c.get_all_socket_names()})
    return write(argument or 'preview-sample',data)


def playback_start(argument):
    global PLAYBACK, PLAYBACK_HANDLE
    assert not globals().get('PLAYBACK',{}).get('active'), 'Playback already running'
    if argument.startswith('Local:'):
        key=argument.split(':',1)[1]
        row=next(r for r in json.loads((OUT/'assets.json').read_text()) if r['package'].endswith('/'+key))
        c=PREVIEW['components']['character']
        c.set_skeletal_mesh_asset(u.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple'))
        c.set_anim_instance_class(u.AnimPreviewInstance)
        c.get_anim_instance().set_animation_asset(u.load_asset(row['package']),False,1.)
        PREVIEW['pose']=dict(view='Local',variant=key,time=0,paths=dict(character=row['package']))
        PREVIEW['actors']['weapon'].set_actor_hidden_in_game(True)
        PREVIEW['actors']['magazine'].set_actor_hidden_in_game(True)
        for a in PREVIEW.get('attachments',[]):a.set_actor_hidden_in_game(True)
        u.EditorLevelLibrary.set_level_viewport_camera_info(u.Vector(185,250,145),u.Rotator(pitch=-12,yaw=-127,roll=0))
    else:
        preview_pose(argument+':0')
        PREVIEW['actors']['weapon'].set_actor_hidden_in_game(False)
        PREVIEW['actors']['magazine'].set_actor_hidden_in_game(False)
        for a in PREVIEW.get('attachments',[]):a.set_actor_hidden_in_game(False)
    duration=max(u.load_asset(p).get_play_length() for p in PREVIEW['pose']['paths'].values())
    revision='Contact04-' if 'reserve' in PREVIEW['actors'] and not argument.startswith('Local:') else ''
    PLAYBACK=dict(active=True,key=revision+argument.replace(':','-'),duration=duration,start=time.monotonic(),
                  paths=PREVIEW['pose']['paths'],samples=[],last_sample=-1.)
    PLAYBACK['visibility_probe']='Source montage interval emulation, no demo notify execution or dropped-magazine physics' if revision else 'Single main magazine; no visibility emulation'
    for name in PREVIEW['pose']['paths']:
        inst=PREVIEW['components'][name].get_anim_instance()
        inst.set_position(0.,False)
        inst.set_playing(True)
    def tick(delta):
        global PLAYBACK_HANDLE
        elapsed=time.monotonic()-PLAYBACK['start']
        if revision:
            view=PREVIEW['pose']['view']
            empty='Empty' in PREVIEW['pose']['variant']
            show,hide=({('FP',False):(.455137,2.520381),('FP',True):(.860815,.433333),
                       ('TP',False):(.256150,1.944525),('TP',True):(.572721,.350720)})[(view,empty)]
            t=PREVIEW['components']['weapon'].get_position()
            PREVIEW['actors']['magazine'].set_actor_hidden_in_game(t>=hide)
            PREVIEW['actors']['reserve'].set_actor_hidden_in_game(t<show)
        if elapsed-PLAYBACK['last_sample']>=1/30:
            row=dict(elapsed=elapsed,components={})
            for n,c in PREVIEW['components'].items():
                wanted=(['root','pelvis','head','upperarm_l','lowerarm_l','hand_l','hand_r','index_03_r','middle_03_l',
                         'index_03_l','thumb_03_l','thumb_03_r','foot_l','foot_r','ball_l','ball_r','ik_hand_gun']
                        if n=='character' else ['Root','Grip','Trigger','Magazine','Magazine_Reserve','Charging_Handle','Bolt','Bullet_Chambered'])
                row['components'][n]=dict(time=c.get_position(),bones={b:serial(c.get_socket_transform(b,u.RelativeTransformSpace.RTS_WORLD)) for b in wanted if c.does_socket_exist(b)})
            if revision:
                row['visibility']=dict(main=not PREVIEW['actors']['magazine'].get_editor_property('hidden'),reserve=not PREVIEW['actors']['reserve'].get_editor_property('hidden'))
            PLAYBACK['samples'].append(row)
            PLAYBACK['last_sample']=elapsed
        if elapsed>=duration+.3 and PREVIEW['components']['character'].get_position()>=duration-.01:
            for c in PREVIEW['components'].values():
                c.get_anim_instance().set_playing(False)
            PLAYBACK['active']=False
            write('Playback/'+PLAYBACK['key'],PLAYBACK)
            u.unregister_slate_post_tick_callback(PLAYBACK_HANDLE)
    (OUT/'Playback').mkdir(exist_ok=True)
    def guarded_tick(delta):
        try:
            tick(delta)
        except Exception:
            import traceback
            PLAYBACK['error']=traceback.format_exc()
            PLAYBACK['active']=False
            for c in PREVIEW['components'].values():c.get_anim_instance().set_playing(False)
            write('Playback/'+PLAYBACK['key'],PLAYBACK)
            u.unregister_slate_post_tick_callback(PLAYBACK_HANDLE)
    PLAYBACK_HANDLE=u.register_slate_post_tick_callback(guarded_tick)
    return dict(key=PLAYBACK['key'],duration=duration)


def skin_weights():
    paths=['/Game/InfimaGames/TacticalFPSAnimations/Common/Characters/Mannequins/Meshes/SKM_Manny_Simple',
           '/Game/InfimaGames/TacticalFPSAnimations/Common/Characters/Mannequins/Meshes/SKM_FP_Manny_Simple',
           '/Game/InfimaGames/TacticalFPSAnimations/Weapons/AssaultRifle/Meshes/SK_TFA_AR',
           '/Game/InfimaGames/TacticalFPSAnimations/Weapons/AssaultRifle/Meshes/SK_TFA_AR_Magazine']
    output={}
    for p in paths:
        mesh=u.load_asset(p)
        dynamic=u.DynamicMesh()
        result=u.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(mesh,dynamic,u.GeometryScriptCopyMeshFromAssetOptions(),u.GeometryScriptMeshReadLOD())
        output[p]=dict(copy_result=str(result),api=dict(weights=str(u.GeometryScript_BoneWeights.get_vertex_bone_weights.__doc__),
                bones=str(u.GeometryScript_BoneWeights.get_all_bones_info.__doc__)),methods=[n for n in dir(dynamic) if 'vertex' in n or 'vertice' in n])
        comp=u.new_object(u.SkeletalMeshComponent)
        comp.set_skeletal_mesh_asset(mesh)
        counts={}
        max_influences=0
        invalid=0
        for i in range(dynamic.get_vertex_count()):
            _,weights,valid=dynamic.get_vertex_bone_weights(i)
            if not valid:invalid+=1
            influences=[w for w in weights if w.weight>0]
            max_influences=max(max_influences,len(influences))
            for w in influences:
                name=str(comp.get_bone_name(w.bone_index))
                counts[name]=counts.get(name,0)+1
        output[p]=dict(copy_result=str(result),lod=0,vertices=dynamic.get_vertex_count(),
                       weighted_bone_vertex_counts=counts,weighted_bones=len(counts),max_influences=max_influences,invalid_vertices=invalid)
    return write('skin-weights',output)


def rig_details():
    rigs=json.loads((OUT/'rigs.json').read_text())
    result={}
    for key in ['SKEL_TFA_Mannequin','SK_Mannequin','SKEL_TFA_AR','SKEL_TFA_AR_Magazine']:
        obj=u.load_asset(rigs[key]['package'])
        pose=obj.get_reference_pose()
        result[key]=dict(sockets={str(n):dict(local=serial(u.AnimPoseExtensions.get_socket_pose(pose,n,u.AnimPoseSpaces.LOCAL)),
                                            component=serial(u.AnimPoseExtensions.get_socket_pose(pose,n,u.AnimPoseSpaces.WORLD)))
                                  for n in u.AnimPoseExtensions.get_socket_names(pose)})
    p='/Game/InfimaGames/TacticalFPSAnimations/Weapons/AssaultRifle/Animations/Weapon/Common/A_TFA_AR_Magazine_FireDepletion'
    anim=u.load_asset(p)
    result['depletion']=dict(package=p,length=anim.get_play_length(),samples=[])
    for fraction in [0.,.25,.5,.75,1.]:
        pose=anim.get_anim_pose_at_time(fraction*anim.get_play_length(),u.AnimPoseEvaluationOptions())
        result['depletion']['samples'].append(dict(time=fraction*anim.get_play_length(),
            bones={str(b):serial(u.AnimPoseExtensions.get_bone_pose(pose,b,u.AnimPoseSpaces.WORLD)) for b in u.AnimPoseExtensions.get_bone_names(pose)}))
    return write('rig-details',result)


def write(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / (name + '.json')).write_text(json.dumps(value, indent=2), encoding='utf-8')
    return value


def state():
    return dict(project=u.Paths.get_project_file_path(), engine=u.SystemLibrary.get_engine_version(),
                world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name(),
                dirty_maps=[p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()],
                dirty_content=[p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_content_packages()])


def action(operation, argument):
    if operation == 'reload':
        import importlib, sys
        importlib.reload(sys.modules[__name__])
        return {'reloaded': True}
    if operation == 'api':
        names = ['Skeleton.get_reference_pose', 'AnimPoseExtensions.get_bone_names',
                 'AnimPoseExtensions.get_bone_pose', 'AnimPoseExtensions.get_ref_bone_pose',
                 'AnimPoseExtensions.get_anim_pose_at_time', 'AnimSequence.get_anim_pose_at_time',
                 'AnimPoseEvaluationOptions', 'AnimationLibrary.get_raw_track_data',
                 'AnimationLibrary.get_animation_notify_events', 'SkeletalMeshComponent.get_ref_pose_transform',
                 'SkeletalMesh.get_bone_parent', 'AnimNotifyEvent', 'AssetRegistryDependencyOptions',
                 'AnimPose', 'AnimPoseSpaces', 'SkeletalMeshComponent.set_position',
                 'DebugSkelMeshComponent', 'AnimPreviewInstance', 'Actor.add_component_by_class',
                 'AnimSequenceFactory', 'AnimationDataController', 'EditorLoadingAndSavingUtils.new_blank_map',
                 'GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh','GeometryScript_BoneWeights',
                 'GeometryScriptCopyMeshFromAssetOptions','GeometryScriptMeshReadLOD','DynamicMesh']
        data = {}
        for n in names:
            o = u
            for part in n.split('.'):
                o = getattr(o, part, None)
            data[n] = dict(doc=str(o.__doc__), members=dir(o))
        return write('api', data)
    if operation == 'state':
        return write(argument or 'editor-state', state())
    if operation == 'inspect':
        return inspect_assets()
    if operation == 'details':
        return details()
    if operation == 'preview_setup':
        return preview_setup()
    if operation == 'preview_pose':
        return preview_pose(argument)
    if operation == 'preview_sample':
        return preview_sample(argument)
    if operation == 'preview_camera':
        u.EditorLevelLibrary.set_level_viewport_camera_info(u.Vector(210,260,175),u.Rotator(pitch=-10,yaw=-130,roll=0))
        for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
            if isinstance(a,u.DirectionalLight):
                a.set_actor_rotation(u.Rotator(pitch=-45,yaw=-50,roll=0),False)
                a.light_component.set_editor_property('intensity',10000.)
        u.EditorLevelLibrary.editor_invalidate_viewports()
        return {'camera':True}
    if operation == 'preview_light':
        sub=u.get_editor_subsystem(u.EditorActorSubsystem)
        for a in sub.get_all_level_actors():
            if isinstance(a,u.DirectionalLight):
                a.set_actor_rotation(u.Rotator(pitch=-35,yaw=-130,roll=0),False)
                a.light_component.set_editor_property('intensity',50000.)
        c=PREVIEW['components']['character']
        for i in range(c.get_num_materials()):
            c.set_material(i,u.load_asset('/Engine/BasicShapes/BasicShapeMaterial'))
        floor=sub.spawn_actor_from_class(u.StaticMeshActor,u.Vector(0,0,-5),transient=True)
        floor.static_mesh_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'))
        floor.set_actor_scale3d(u.Vector(5,5,.05))
        u.EditorLevelLibrary.set_level_viewport_camera_info(u.Vector(140,220,175),u.Rotator(pitch=-14,yaw=-122,roll=0))
        return {'lit':True}
    if operation == 'preview_play':
        for n,c in PREVIEW['components'].items():
            if n!='magazine':
                c.set_update_animation_in_editor(True)
                c.set_component_tick_enabled(True)
                c.get_anim_instance().set_playing(argument=='true')
        return {n:dict(properties=props(c,['animation_mode','update_animation_in_editor','pause_anims','no_skeleton_update','primary_component_tick']),
                position=c.get_position()) for n,c in PREVIEW['components'].items()}
    if operation == 'pie_bind':
        world=u.EditorLevelLibrary.get_game_world()
        actors=u.GameplayStatics.get_all_actors_of_class(world,u.SkeletalMeshActor)
        found={}
        for actor in actors:
            label=actor.get_actor_label()
            if label.startswith('MSQ52_Audit_'):
                n=label.removeprefix('MSQ52_Audit_')
                PREVIEW['actors'][n]=actor
                PREVIEW['components'][n]=actor.skeletal_mesh_component
                actor.skeletal_mesh_component.set_anim_instance_class(u.AnimPreviewInstance)
                found[n]=actor.get_path_name()
        PREVIEW['attachments']=[a for a in u.GameplayStatics.get_all_actors_of_class(world,u.StaticMeshActor)
                                if a.get_actor_label().startswith('MSQ52_Part_')]
        return write('pie-bind',found)
    if operation == 'pie_light':
        world=u.EditorLevelLibrary.get_game_world()
        for a in u.GameplayStatics.get_all_actors_of_class(world,u.DirectionalLight):
            a.light_component.set_editor_property('intensity',float(argument or 5))
        u.EditorLevelLibrary.set_level_viewport_camera_info(u.Vector(95,125,162),u.Rotator(pitch=-10,yaw=-127,roll=0))
        return {'intensity':argument}
    if operation == 'playback_start':
        return playback_start(argument)
    if operation == 'playback_abort':
        u.unregister_slate_post_tick_callback(PLAYBACK_HANDLE)
        PLAYBACK['active']=False
        for c in PREVIEW['components'].values():c.get_anim_instance().set_playing(False)
        return write('failed-playback-'+PLAYBACK['key'],PLAYBACK)
    if operation == 'skin_weights':
        return skin_weights()
    if operation == 'rig_details':
        return rig_details()
    if operation == 'socket_contract':
        rows=json.loads((OUT/'assets.json').read_text())
        result={}
        for row in rows:
            if row['type']!='SkeletalMesh' or '/InfimaGames/' not in row['package'] or '/Environment/' in row['package']:continue
            mesh=u.load_asset(row['package'])
            result[row['package']]={}
            for name in row['sockets']:
                socket=mesh.find_socket(name)
                result[row['package']][name]=props(socket,['socket_name','bone_name','relative_location','relative_rotation','relative_scale']) if socket else {'unavailable':True}
        return write('socket-contract',result)
    if operation == 'restore':
        assert not globals().get('PLAYBACK',{}).get('active')
        u.EditorLoadingAndSavingUtils.load_map('/Game/Maps/L_OpeningLobby_PainterStone01')
        return write('editor-restored',state())
    if operation == 'shutdown':
        current=state()
        assert not current['dirty_maps'] and all(p=='/Engine/BasicShapes/BasicShapeMaterial' for p in current['dirty_content'])
        write('editor-shutdown',dict(state=current,reason='Editor was closed before the audit; release staged asset handles without saving original assets.'))
        u.SystemLibrary.quit_editor()
        return {'shutdown_requested':True}
    if operation == 'final_dependencies':
        registry=u.AssetRegistryHelpers.get_asset_registry()
        registry.scan_paths_synchronous(['/Game/InfimaGames/TacticalFPSAnimations','/Game/Characters/Mannequins'],True)
        manifest=json.loads((SOURCE/'selected-sources.json').read_text())
        rows=[]
        for entry in manifest['files']:
            p=entry['package']
            row=dict(package=p)
            for kind in ['hard','soft']:
                opt=u.AssetRegistryDependencyOptions(include_hard_package_references=kind=='hard',include_soft_package_references=kind=='soft',include_editor_only_package_references=True,include_game_package_references=True)
                row[kind]=[str(d) for d in registry.get_dependencies(p,opt)]
                row['missing_'+kind]=[d for d in row[kind] if d.startswith('/Game/') and not (ROOT/'Content'/(d.removeprefix('/Game/')+'.uasset')).exists()]
            rows.append(row)
        write('final-dependencies',rows)
        return {'checked':len(rows),'missing_hard':[x for x in rows if x['missing_hard']],'missing_soft_count':sum(len(x['missing_soft']) for x in rows)}
    if operation == 'cold_load':
        rows=[]
        for entry in json.loads((SOURCE/'selected-sources.json').read_text())['files']:
            obj=u.load_asset(entry['package'])
            rows.append(dict(package=entry['package'],loaded=obj is not None,class_name=obj.get_class().get_name() if obj else None))
        write('cold-load',rows)
        return {'assets':len(rows),'failed':[r for r in rows if not r['loaded']],'state':state()}
    if operation == 'camera_named':
        poses={'fp_baseline':(u.Vector(0,0,170),u.Rotator(pitch=0,yaw=90,roll=0)),
               'fp_source':(u.Vector(0,.663123,162.5751),u.Rotator(pitch=0,yaw=90,roll=0)),
               'contact':(u.Vector(65,92,150),u.Rotator(pitch=-5,yaw=-132,roll=0)),
               'body':(u.Vector(185,250,145),u.Rotator(pitch=-12,yaw=-127,roll=0))}
        u.EditorLevelLibrary.set_level_viewport_camera_info(*poses[argument])
        return {'camera':argument,'fov':90}
    if operation == 'playback_status':
        return dict(active=PLAYBACK['active'],key=PLAYBACK['key'],error=PLAYBACK.get('error'),samples=len(PLAYBACK['samples']),
                    latest=PLAYBACK['samples'][-1] if PLAYBACK['samples'] else None)
    if operation == 'attachments':
        sub=u.get_editor_subsystem(u.EditorActorSubsystem)
        actors=sub.get_all_level_actors()
        weapon=next(a for a in actors if a.get_actor_label()=='MSQ52_Audit_weapon')
        PREVIEW['attachments']=[]
        meshroot='/Game/InfimaGames/TacticalFPSAnimations/Weapons/AssaultRifle/Meshes/'
        for mesh,socket in [('SM_TFA_AR_Handguard_Default','SOCKET_Handguard'),('SM_TFA_AR_ATT_Sight_Rear','SOCKET_Sight_Rear')]:
            actor=sub.spawn_actor_from_class(u.StaticMeshActor,u.Vector(0,0,0),transient=False)
            actor.set_actor_label('MSQ52_Part_'+mesh)
            actor.static_mesh_component.set_static_mesh(u.load_asset(meshroot+mesh))
            actor.attach_to_component(weapon.skeletal_mesh_component,socket,*([u.AttachmentRule.SNAP_TO_TARGET]*3),False)
            PREVIEW['attachments'].append(actor)
        return [a.get_path_name() for a in PREVIEW['attachments']]
    if operation == 'attachments_live':
        result=[]
        for a in PREVIEW['attachments']:
            a.static_mesh_component.set_mobility(u.ComponentMobility.MOVABLE)
            socket='SOCKET_Handguard' if 'Handguard' in a.get_actor_label() else 'SOCKET_Sight_Rear'
            result.append(a.attach_to_component(PREVIEW['components']['weapon'],socket,*([u.AttachmentRule.SNAP_TO_TARGET]*3),False))
        return result
    if operation == 'reserve_setup':
        sub=u.get_editor_subsystem(u.EditorActorSubsystem)
        actor=sub.spawn_actor_from_class(u.SkeletalMeshActor,u.Vector(0,0,0),transient=False)
        actor.set_actor_label('MSQ52_Audit_reserve')
        actor.skeletal_mesh_component.set_skeletal_mesh_asset(u.load_asset('/Game/InfimaGames/TacticalFPSAnimations/Weapons/AssaultRifle/Meshes/SK_TFA_AR_Magazine'))
        actor.skeletal_mesh_component.set_anim_instance_class(u.AnimPreviewInstance)
        return actor.get_path_name()
    if operation == 'exposure_setup':
        sub=u.get_editor_subsystem(u.EditorActorSubsystem)
        volume=sub.spawn_actor_from_class(u.PostProcessVolume,u.Vector(0,0,0),transient=False)
        volume.set_editor_property('unbound',True)
        settings=volume.get_editor_property('settings')
        for name,value in [('override_auto_exposure_method',True),('auto_exposure_method',u.AutoExposureMethod.AEM_MANUAL),
                           ('override_auto_exposure_bias',True),('auto_exposure_bias',0.),
                           ('override_auto_exposure_apply_physical_camera_exposure',True),('auto_exposure_apply_physical_camera_exposure',False),
                           ('override_bloom_intensity',True),('bloom_intensity',0.)]:
            settings.set_editor_property(name,value)
        volume.set_editor_property('settings',settings)
        for a in sub.get_all_level_actors():
            if isinstance(a,u.DirectionalLight):a.light_component.set_editor_property('intensity',5.)
        return {'manual_exposure':True}
    if operation == 'montages':
        rows=[]
        for r in json.loads((OUT/'montage-audit-copies.json').read_text()):
            p='/Game/'+Path(r['copy']).relative_to('Content').with_suffix('').as_posix()
            obj=u.load_asset(p)
            row=dict(package=p,loaded=obj is not None)
            if obj:
                row.update(props(obj,['sequence_length','slot_anim_tracks','composite_sections','blend_in','blend_out']))
                row['notifies']=[]
                for e in u.AnimationLibrary.get_animation_notify_events(obj):
                    n=props(e,['notify_name','notify','notify_state_class'])
                    n['time']=u.AnimationLibrary.get_anim_notify_event_trigger_time(e)
                    n['duration']=u.AnimationLibrary.get_anim_notify_event_duration(e)
                    row['notifies'].append(n)
                row['slots']=[props(s,['slot_name','anim_track']) for s in obj.get_editor_property('slot_anim_tracks')]
            rows.append(row)
        return write('montage-timing',rows)
    if operation == 'capabilities':
        classes = ['AnimationLibrary', 'AnimSequence', 'Skeleton', 'SkeletalMesh',
                   'SkeletalMeshComponent', 'AnimPoseExtensions', 'AnimPoseEvaluationOptions',
                   'AnimationBlueprintLibrary', 'SkeletalMeshEditorSubsystem']
        return write('capabilities', {n: dict(doc=str(getattr(u, n, None).__doc__),
                members=dir(getattr(u, n, None))) for n in classes})
    if operation == 'scan':
        registry = u.AssetRegistryHelpers.get_asset_registry()
        registry.scan_paths_synchronous(['/Game/InfimaGames/TacticalFPSAnimations', '/Game/Characters/Mannequins'], True)
        return write('registry', [dict(path=str(a.package_name), type=str(a.asset_class_path))
            for p in ['/Game/InfimaGames/TacticalFPSAnimations', '/Game/Characters/Mannequins']
            for a in registry.get_assets_by_path(p, recursive=True)])
    raise ValueError(operation)
