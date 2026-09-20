"""Source intake and focused runtime checks for MSQ-87; no map edits."""
import json
import time
import traceback
from pathlib import Path
import unreal as u
import unreal85
import verify02
from stage1_tools import state

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlBalance01/Worker'
ASSETS = '/Game/Development/PhysicsControlBalance01'

def write(name, result):
    path = OUT / (name + '.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    assert not path.exists(), path
    path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result

def source_import():
    s = state()
    assert not s['pie'] and not s['dirty_maps'] and not s['dirty_content'], s
    tools = u.AssetToolsHelpers.get_asset_tools()
    result = []
    for name, last in [('Back', 250), ('Stomach', 258)]:
        task = u.AssetImportTask()
        task.filename = str(ROOT / f'Assets/Source/PhysicsControlBalance01/MixamoGetUp01/GetUp_From{name}_XBot.fbx')
        task.destination_path = ASSETS + '/Source/' + name
        task.destination_name = 'XBot_' + name
        task.automated = True
        task.save = True
        options = u.FbxImportUI()
        options.automated_import_should_detect_type = False
        options.mesh_type_to_import = u.FBXImportType.FBXIT_SKELETAL_MESH
        options.import_as_skeletal = True
        options.import_mesh = True
        options.import_animations = True
        options.import_materials = False
        options.import_textures = False
        options.create_physics_asset = False
        options.anim_sequence_import_data.set_editor_property('animation_length', u.FBXAnimationLengthImportType.FBXALIT_ANIMATED_KEY)
        options.anim_sequence_import_data.set_editor_property('use_default_sample_rate', False)
        options.anim_sequence_import_data.set_editor_property('custom_sample_rate', 30)
        task.options = options
        task.factory = u.FbxFactory()
        assert not u.EditorAssetLibrary.does_directory_exist(task.destination_path)
        tools.import_asset_tasks([task])
        assets = task.get_objects()
        result.append(dict(name=name, assets=[dict(path=a.get_path_name(), cls=a.get_class().get_name(),
            length=a.sequence_length if isinstance(a, u.AnimSequence) else None) for a in assets]))
    return write('source-import01', result)

def inspect_api():
    return {n: [x for x in dir(getattr(u, n)) if any(k in x for k in ['auto', 'retarget', 'skeletal', 'op', 'bone', 'transform'])]
        for n in ['IKRigController', 'IKRetargeterController', 'AnimPoseExtensions', 'AnimationLibrary']}

def inventory():
    result = []
    for path in u.EditorAssetLibrary.list_assets(ASSETS):
        a = u.load_asset(path)
        result.append(dict(path=path, cls=a.get_class().get_name(), length=a.sequence_length if isinstance(a,u.AnimSequence) else None))
    return result

def retarget():
    assert not state()['pie']
    tools = u.AssetToolsHelpers.get_asset_tools()
    src = u.load_asset(ASSETS + '/Source/Back/XBot_Back')
    dst = u.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple')
    rigs = []
    report = []
    for name, mesh in [('XBot',src),('Manny',dst)]:
        rig = tools.create_asset('IK_' + name, ASSETS, u.IKRigDefinition, u.IKRigDefinitionFactory())
        rc = u.IKRigController.get_controller(rig)
        assert rc.set_skeletal_mesh(mesh)
        assert rc.apply_auto_generated_retarget_definition(), name
        assert rc.apply_auto_fbik(), name
        rigs.append(rig)
        report.append(dict(name=name, chains=[str(c.chain_name) for c in rc.get_retarget_chains()]))
        u.EditorAssetLibrary.save_loaded_asset(rig)
    rt = tools.create_asset('RT_XBot_Manny', ASSETS, u.IKRetargeter, u.IKRetargetFactory())
    ctrl = u.IKRetargeterController.get_controller(rt)
    ctrl.set_ik_rig(u.RetargetSourceOrTarget.SOURCE, rigs[0])
    ctrl.set_ik_rig(u.RetargetSourceOrTarget.TARGET, rigs[1])
    ctrl.add_default_ops()
    ctrl.auto_align_all_bones(u.RetargetSourceOrTarget.TARGET)
    u.EditorAssetLibrary.save_loaded_asset(rt)
    for name, length in [('Back',8.3333333),('Stomach',8.6)]:
        candidates = [u.load_asset(p) for p in u.EditorAssetLibrary.list_assets(ASSETS+'/Source/'+name)]
        anims = [a for a in candidates if isinstance(a,u.AnimSequence) and abs(a.sequence_length-length)<.02]
        assert len(anims)==1, [(a.get_name(),a.sequence_length) for a in candidates if isinstance(a,u.AnimSequence)]
        inputs = u.IKRetargetBatchOperationInputs()
        inputs.assets_to_retarget = [u.EditorAssetLibrary.find_asset_data(anims[0].get_path_name())]
        inputs.source_mesh = src
        inputs.target_mesh = dst
        inputs.ik_retarget_asset = rt
        inputs.target_path = ASSETS
        inputs.prefix = 'Manny_'
        inputs.include_referenced_assets = False
        made = u.IKRetargetBatchOperation.run_batch_retarget(inputs)
        assert len(made)==1, made
        a = made[0].get_asset()
        target = ASSETS+'/A_GetUp_'+name
        assert u.EditorAssetLibrary.rename_asset(a.get_path_name(),target)
        u.EditorAssetLibrary.save_loaded_asset(a)
        report.append(dict(name=name,source=anims[0].get_path_name(),path=a.get_path_name(),length=a.sequence_length))
    return write('retarget01',report)

def motion_audit():
    report = []
    for name in ['Back','Stomach']:
        a=u.load_asset(ASSETS+'/A_GetUp_'+name)
        opts=u.AnimPoseEvaluationOptions()
        rows=[]
        for frame in range(round(a.sequence_length*30)+1):
            pose=u.AnimPoseExtensions.get_anim_pose_at_frame(a,frame,opts)
            bones={}
            for bone in ['root','pelvis','spine_05','head','thigh_l','calf_l','foot_l','foot_r','hand_l','hand_r']:
                t=u.AnimPoseExtensions.get_bone_pose(pose,bone,u.AnimPoseSpaces.WORLD)
                bones[bone]=dict(p=[t.translation.x,t.translation.y,t.translation.z],q=[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w])
            rows.append(dict(frame=frame,bones=bones))
        report.append(dict(name=name,length=a.sequence_length,rows=rows))
    write('motion-audit01',report)
    return [dict(name=x['name'],length=x['length'],frames=len(x['rows']),samples=[x['rows'][i] for i in [0,len(x['rows'])//2,len(x['rows'])-1]]) for x in report]

def view_audit():
    w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
    targets=[(-950,-320,z) for z in [20,100,180]]+[(x,y,30) for x,y in [(-1050,-320),(-850,-320),(-950,-420),(-950,-220)]]
    scored=[]
    for x in range(-1350,-550,100):
        for y in range(-720,121,100):
            distance=((x+950)**2+(y+320)**2)**.5
            if not 270<distance<520: continue
            for z in [170,240]:
                start=u.Vector(x,y,z)
                if u.SystemLibrary.sphere_overlap_actors(w,start,80,[u.ObjectTypeQuery.OBJECT_TYPE_QUERY1],u.Actor,[]): continue
                clear=[u.SystemLibrary.line_trace_single(w,start,u.Vector(*p),u.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],u.DrawDebugTrace.NONE) is None for p in targets]
                scored.append(dict(camera=[x,y,z],clear=sum(clear),total=len(clear),distance=distance))
    scored.sort(key=lambda r:(-r['clear'],abs(r['distance']-360)))
    write('view-audit02',scored)
    return scored[:12]

def overview_views():
    w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
    targets=[(-950+(i//3)*320,-320+(i%3)*320,z) for i in range(6) for z in [20,100,180]]
    scored=[]
    for x in [-1450,-1150,-850,-550,-350]:
        for y in [-900,-650,0,650,900]:
            for z in [350,650,900]:
                p=u.Vector(x,y,z)
                if u.SystemLibrary.sphere_overlap_actors(w,p,80,[u.ObjectTypeQuery.OBJECT_TYPE_QUERY1],u.Actor,[]):continue
                clear=[u.SystemLibrary.line_trace_single(w,p,u.Vector(*t),u.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],u.DrawDebugTrace.NONE) is None for t in targets]
                scored.append(dict(camera=[x,y,z],clear=sum(clear),fixtures=[sum(clear[i*3:i*3+3]) for i in range(6)]))
    scored.sort(key=lambda r:-r['clear'])
    write('overview-views01',scored)
    return scored[:8]

def action(operation, argument):
    if operation in ['performance','frame_rate','verify_status']:
        return unreal85.action(operation,argument)
    if operation == 'sample': return unreal85.sample(True)
    if operation == 'close':
        s=state()
        assert not s['pie'] and not s['dirty_maps'] and not s['dirty_content'],s
        write('close-'+argument,s)
        u.SystemLibrary.quit_editor()
        return s
    if operation == 'verify':
        config=json.loads(argument)
        extra=[e for e in config['events'] if e[1] in ['@impulse','@push','@environment']]
        config['events']=[e for e in config['events'] if e not in extra]
        unreal85.OUT=OUT
        result=unreal85.action('verify',json.dumps(config))
        if config.get('flying'):
            p=unreal85.actors()[1]
            p.character_movement.set_movement_mode(u.MovementMode.MOVE_FLYING)
            p.character_movement.stop_movement_immediately()
            p.set_actor_location(u.Vector(*config['location']),False,False)
        if config.get('platform'):
            assert unreal85.selected(unreal85.actors()[3]).probe_balance_environment('platform')
        if config.get('inspection_view'):
            p=unreal85.actors()[1]
            p.mesh.set_visibility(False,True)
            for a in p.get_attached_actors(reset_array=True,recursively_include_attached_actors=True): a.set_actor_hidden_in_game(True)
        verify02.RUN['extra']=extra
        verify02.RUN['extra_index']=0
        u.unregister_slate_post_tick_callback(verify02.RUN['handle'])
        verify02.tick=balance_tick
        verify02.RUN['handle']=u.register_slate_post_tick_callback(balance_tick)
        return result
    if operation == 'state': return write('state-' + argument, state())
    if operation == 'handoff':
        s=state()
        assert not s['pie'] and not s['dirty_maps'] and not s['dirty_content'],s
        w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
        s['transient_probe_actors']=[a.get_name() for a in u.GameplayStatics.get_all_actors_of_class(w,u.Actor) if a.actor_has_tag('MSQ87_TransientProbe')]
        assert not s['transient_probe_actors'],s
        return write('handoff-'+argument,s)
    if operation == 'import': return source_import()
    if operation == 'api': return inspect_api()
    if operation == 'inventory': return inventory()
    if operation == 'retarget': return retarget()
    if operation == 'motion_audit': return motion_audit()
    if operation == 'views': return view_audit()
    if operation == 'overview_views': return overview_views()
    if operation == 'save_sources':
        s=state()
        assert not s['pie'] and not s['dirty_maps'] and all(p.startswith(ASSETS) for p in s['dirty_content']),s
        u.EditorAssetLibrary.save_directory(ASSETS,only_if_is_dirty=True,recursive=True)
        return state()
    raise ValueError(operation)

def balance_tick(delta):
    try:
        balance_tick_impl(delta)
    except Exception:
        verify02.RUN['error']=traceback.format_exc()
        verify02.finish()

def balance_tick_impl(delta):
    r=verify02.RUN
    w,p,m,ds=unreal85.actors()
    d=unreal85.selected(ds)
    now=json.loads(m.get_combat_state())['firing_clock']-r['clock_start']
    while r['extra_index']<len(r['extra']) and now>=r['extra'][r['extra_index']][0]:
        _,key,value=r['extra'][r['extra_index']]
        if key=='@impulse':
            bone=value[3]
            d.apply_external_disturbance(u.Vector(*value[:3]),d.get_physical_body_location(bone),bone)
        elif key=='@environment':
            assert d.probe_balance_environment(value),value
            if value=='ceiling' and r['config'].get('inspection_view'):
                mat=u.load_asset('/Engine/EngineDebugMaterials/WireframeMaterial')
                assert mat
                for a in u.GameplayStatics.get_all_actors_of_class(w,u.StaticMeshActor):
                    if a.actor_has_tag('MSQ87_TransientProbe'): a.static_mesh_component.set_material(0,mat)
        elif key=='@push':
            # Use the actual anatomical front so a directional fall is reproducible
            # without overriding the physical pose or selecting a get-up animation.
            chest=d.get_physical_body_location('spine_05')-d.get_physical_body_location('pelvis')
            side=d.get_physical_body_location('clavicle_l')-d.get_physical_body_location('clavicle_r')
            direction=u.MathLibrary.cross_vector_vector(chest,side)
            direction.z=0
            direction=u.MathLibrary.normal(direction)
            d.apply_external_disturbance(direction*float(value),d.get_physical_body_location('spine_05'),'spine_05')
        r['events'].append(dict(t=now,wall=time.monotonic()-r['wall'],key=key,value=value))
        r['extra_index']+=1
    balance=json.loads(d.get_dummy_state(False))['balance']
    if r['config'].get('joint_diagnostics'):
        label = 'standing' if now < .8 else ('recovery' if balance['state']=='GETTING UP' and balance['state_seconds']>5.4 else '')
        if label and not r.get('joints_'+label):
            write(r['config']['name']+'-joints-'+label,json.loads(d.get_dummy_state(True)))
            r['joints_'+label]=True
    if r['config'].get('look_at'):
        camera=u.GameplayStatics.get_player_camera_manager(w,0)
        u.GameplayStatics.get_player_controller(w,0).set_control_rotation(u.MathLibrary.find_look_at_rotation(camera.get_camera_location(),u.Vector(*r['config']['look_at'])))
    if r['config'].get('follow_fall') and r.get('removed_support'):
        p.set_actor_location(d.get_physical_body_location('pelvis')+u.Vector(-350,150,100),False,False)
    if r['config'].get('remove_support') and not r.get('removed_support') and balance['state']=='GETTING UP' and balance['state_seconds']>=1:
        assert d.probe_balance_environment('remove_floor')
        r['removed_support']=True
        r['events'].append(dict(t=now,world=u.GameplayStatics.get_time_seconds(w),key='remove_actual_floor'))
    if r['config'].get('interrupt_and_kill') and balance['state']=='GETTING UP' and balance['state_seconds']>=1.5:
        stage=r.get('interrupt_stage',0)
        if stage==0 or (stage==1 and balance['interruptions']>=1):
            p.probe_key('LeftMouseButton',1,True)
            r['release_at']=now+.06
            r['interrupt_stage']=stage+1
            r['events'].append(dict(t=now,key='actual_recovery_rifle_press',stage=stage))
    if r.get('release_at') is not None and now>=r['release_at']:
        p.probe_key('LeftMouseButton',0,False);r['release_at']=None
    if r['config'].get('slow_getup'):
        if 'slow_start' not in r and balance['state']=='GETTING UP' and balance['state_seconds']>=1:
            m.set_physics_preview_scale(.25)
            r['slow_start']=now
            r['events'].append(dict(t=now,world=u.GameplayStatics.get_time_seconds(w),key='recovery_slow_start'))
        elif 'slow_start' in r and not r.get('slow_ended') and now-r['slow_start']>=4:
            m.set_physics_preview_scale(1)
            r['slow_ended']=True
            r['events'].append(dict(t=now,world=u.GameplayStatics.get_time_seconds(w),key='recovery_slow_end'))
    unreal85.tick(delta)
