"""Bounded official-Epic-MCP assembly and saved-geometry audit for ReworkA01."""
import importlib
import json
import re
from pathlib import Path
import unreal as u
from stage1_tools import state
from layout02_verification import require_project
import reworka01_data as _data
importlib.reload(_data)
from reworka01_data import ROOT,OUT,SRC,MAP,BASE,ASSETS,D,S,A,geometry,replaced,imported_module

def guard(candidate=True, clean=False):
    s=state();require_project(s['project']);assert not s['pie'],s
    if candidate:
        assert s['level'].split('.')[0]==MAP,s
    assert all(p.startswith(ASSETS) for p in s['dirty_content']),s
    assert all(p==MAP for p in s['dirty_maps']),s
    if clean:
        assert not s['dirty_content'] and not s['dirty_maps'],s
    return s

def save():
    guard()
    for p in u.EditorLoadingAndSavingUtils.get_dirty_content_packages():
        assert p.get_path_name().startswith(ASSETS)
        assert u.EditorAssetLibrary.save_asset(p.get_path_name())
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()

def snapshot():
    rows={}
    for actor in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
        center,extent=actor.get_actor_bounds(False)
        row=dict(center=[center.x,center.y,center.z],extent=[extent.x,extent.y,extent.z],transform=str(actor.get_actor_transform()))
        c=actor.get_component_by_class(u.StaticMeshComponent)
        if c:
            scale=actor.get_actor_scale3d()
            row.update(mesh=c.static_mesh.get_path_name(),visible=c.is_visible(),profile=str(c.get_collision_profile_name()),
                collision=str(c.get_collision_enabled()),scale=[scale.x,scale.y,scale.z],
                materials=[c.get_material(i).get_path_name() for i in range(c.get_num_materials())])
        if isinstance(actor,u.PointLight):
            c=actor.point_light_component
            row['lighting']={k:str(c.get_editor_property(k)) for k in ['intensity','intensity_units','attenuation_radius','source_radius','use_temperature','temperature','mobility']}
        if isinstance(actor,u.PostProcessVolume):
            settings=actor.get_editor_property('settings')
            row['exposure']={k:str(settings.get_editor_property(k)) for k in ['auto_exposure_method','auto_exposure_bias','auto_exposure_apply_physical_camera_exposure','bloom_intensity','motion_blur_amount']}
        rows[actor.get_actor_label()]=row
    return rows

def create():
    guard(False,True)
    assert not u.EditorAssetLibrary.does_asset_exist(MAP)
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).new_level_from_template(MAP,BASE)
    (OUT/'baseline-actual.json').write_text(json.dumps(snapshot(),indent=2))
    # Materials are duplicated so any authorized candidate fixes have local scope.
    for name in ['Stone','Wall','Ceiling','Metal','Glazing','Floor','Strip']:
        old='/Game/OpeningLobby/Layout03/Materials/M_Layout03_'+name
        new=ASSETS+'/Materials/M_RA01_'+name
        assert not u.EditorAssetLibrary.does_asset_exist(new)
        assert u.EditorAssetLibrary.duplicate_asset(old,new)
    for actor in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
        c=actor.get_component_by_class(u.StaticMeshComponent)
        if not c:
            continue
        for i in range(c.get_num_materials()):
            old=c.get_material(i)
            assert old.get_name().startswith('M_Layout03_')
            c.set_material(i,u.load_asset(ASSETS+'/Materials/M_RA01_'+old.get_name().replace('M_Layout03_','')))
    save()
    return dict(map=MAP,state=state())

def import_assets():
    guard(clean=True)
    assert not u.EditorAssetLibrary.does_directory_exist(ASSETS+'/Meshes')
    kit=json.loads((OUT/'kit.json').read_text())['assets']
    tasks=[]
    for name,item in kit.items():
        task=u.AssetImportTask();task.filename=str(ROOT/item['export']);task.destination_path=ASSETS+'/Meshes'
        task.destination_name=item['object'];task.automated=True;task.save=True
        options=u.FbxImportUI();options.import_mesh=True;options.import_materials=False;options.import_textures=False
        options.import_as_skeletal=False;options.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH
        options.static_mesh_import_data.combine_meshes=True
        options.static_mesh_import_data.generate_lightmap_u_vs=False
        options.static_mesh_import_data.auto_generate_collision=False
        options.static_mesh_import_data.normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
        task.options=options;tasks.append(task)
    u.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    records=[]
    modules=geometry()['modules']
    for (name,item),task in zip(kit.items(),tasks):
        assert task.imported_object_paths,task.filename
        mesh=u.load_asset(task.imported_object_paths[0])
        body=mesh.get_editor_property('body_setup');assert body
        # Exact closed static geometry, including the concave jamb and collar.
        # No collision shells fill the deliberate recess or doorway.
        body.set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        mesh.set_material(0,u.load_asset(ASSETS+'/Materials/M_RA01_'+modules[name]['material']))
        assert u.EditorAssetLibrary.save_loaded_asset(mesh)
        records.append(dict(source=task.filename,assets=list(task.imported_object_paths),collision=str(body.get_editor_property('collision_trace_flag'))))
    (OUT/'imports.json').write_text(json.dumps(records,indent=2));save()
    return dict(imported=len(records))

def assemble():
    guard(clean=True)
    aes=u.get_editor_subsystem(u.EditorActorSubsystem)
    old={a.get_actor_label():a for a in aes.get_all_level_actors()}
    assert not any(n.startswith('RA01_') for n in old)
    data=geometry()
    removed=[]
    for name,a in old.items():
        if replaced(name):
            assert aes.destroy_actor(a);removed.append(name)
    for name,item in data['instances'].items():
        module=item['module'];mesh=u.load_asset(ASSETS+'/Meshes/SM_RA01_'+imported_module(module));assert mesh,module
        actor=aes.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*(v*100 for v in item['center_m'])))
        actor.set_actor_label('RA01_'+name);actor.set_folder_path('ArchitectureReworkA01/'+('Entrance' if name.startswith(('Portal','Door','Datum','Lower','UpperGlazing','UpperMullion','UpperTransom')) else 'TerminalAndColonnade'))
        c=actor.static_mesh_component;c.set_static_mesh(mesh)
        c.set_collision_profile_name('BlockAll' if item['blocking'] else 'NoCollision')
        c.set_mobility(u.ComponentMobility.STATIC)
        c.set_material(0,u.load_asset(ASSETS+'/Materials/M_RA01_'+data['modules'][module]['material']))
    (OUT/'replacement-record.json').write_text(json.dumps(dict(removed_candidate_proxies=removed,added=list(data['instances']),
        reason='Owner-approved A depth/upper-wall/terminal-soffit deltas; historical files untouched'),indent=2))
    save()
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
    return audit()

def profiles():
    s=state();require_project(s['project']);assert 'L_OpeningLobby_ArchitectureReworkA01' in s['level']
    editor=u.get_editor_subsystem(u.UnrealEditorSubsystem);world=editor.get_game_world() or editor.get_editor_world()
    probes=[]
    def trace(name,start,end,axis,target):
        hit=u.SystemLibrary.line_trace_single(world,u.Vector(*start),u.Vector(*end),u.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],u.DrawDebugTrace.NONE,True)
        values=hit.to_tuple();location=values[4];xyz=[location.x,location.y,location.z]
        probes.append(dict(name=name,blocking_hit=values[0],start_cm=start,end_cm=end,impact_cm=xyz,
            actor=values[9].get_actor_label() if values[9] else None,expected_cm=target,
            error_cm=abs(xyz[axis]-target),passed=values[0] and abs(xyz[axis]-target)<.1))
    for sign in [-1,1]:
        for z in [400,1600]:
            for y,target in [(275,-2900),(350,-2840),(445,-2840)]:
                trace('jamb_%s_y%s_z%s'%(sign,y,z),[-2700,sign*y,z],[-3100,sign*y,z],0,target)
        for y,target in [(510,-2960),(680,-2880)]:
            trace('terminal_%s_y%s'%(sign,y),[-2700,sign*y,400],[-3100,sign*y,400],0,target)
        for x,y,target in [(-2550,1000,920),(-2860,1000,840),(-2240,1000,840),(-2550,820,840),(-2550,1180,840)]:
            trace('soffit_%s_x%s_y%s'%(sign,x,y),[x,sign*y,200],[x,sign*y,1200],2,target)
    report=dict(map=MAP,passed=all(r['passed'] for r in probes),probes=probes,
        method='Complex traces against actual imported saved geometry; no proxy bounds substitution',
        handedness='Opposite native jamb hand assigned in UE to compensate FBX Y reflection')
    (OUT/'imported-profile-probes.json').write_text(json.dumps(report,indent=2))
    return report

def correct_handedness():
    guard(clean=True)
    aes=u.get_editor_subsystem(u.EditorActorSubsystem);actors={a.get_actor_label():a for a in aes.get_all_level_actors()}
    assert not (OUT/'handedness-correction.json').exists()
    changes=[]
    for sign in [-1,1]:
        name='PortalJamb_'+str(sign);actor=actors['RA01_'+name];component=actor.static_mesh_component
        old=component.static_mesh.get_path_name();new=ASSETS+'/Meshes/SM_RA01_'+imported_module(name)
        assert old!=new+'.'+new.split('/')[-1]
        component.set_static_mesh(u.load_asset(new))
        changes.append(dict(actor='RA01_'+name,before=old,after=component.static_mesh.get_path_name()))
    save();assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
    (OUT/'handedness-correction.json').write_text(json.dumps(dict(changes=changes,reason='Measured FBX Y reflection put reveals on outer sides; assigned opposite native hands at unit positive scale.'),indent=2))
    return audit()

def audit():
    guard(clean=True)
    data=geometry();rows=snapshot();baseline=json.loads((OUT/'baseline-actual.json').read_text());errors=[];checks=[]
    def check(name,passed,actual=None):
        checks.append(dict(name=name,passed=bool(passed),actual=actual))
        if not passed:errors.append(name)
    # Existing measured-geometry pattern; candidate targets come from the exact
    # common design used by the drawings, not edited historical verifier defaults.
    for name,item in data['instances'].items():
        row=rows.get('RA01_'+name)
        if not row:
            check(name+' present',False);continue
        error=max([abs(v/100-w) for v,w in zip(row['center'],item['center_m'])]+[abs(2*v/100-w) for v,w in zip(row['extent'],item['size_m'])])
        row['error_m']=error
        check(name+' measured geometry',error<.001,error)
        check(name+' collision',row['profile']==('BlockAll' if item['blocking'] else 'NoCollision'),row['profile'])
        check(name+' visible/local/unit scale',row['visible'] and row['mesh'].startswith(ASSETS) and row['scale']==[1,1,1])
        check(name+' handed module assignment',row['mesh'].split('.')[-1]=='SM_RA01_'+imported_module(item['module']))
    for name,old in baseline.items():
        if replaced(name):
            check(name+' removed duplicate',name not in rows);continue
        now=rows.get(name)
        def comparable(value):
            return re.sub(r'0x[0-9A-Fa-f]+','ADDRESS',value) if isinstance(value,str) else value
        check(name+' preserved context',now is not None and all(comparable(now[k])==comparable(old[k]) for k in old if k!='materials'))
    # Record measurable authored deltas and primary span from actual saved bounds.
    def span(names,axis):
        rs=[rows[n] for n in names]
        return [min(r['center'][axis]-r['extent'][axis] for r in rs)/100,max(r['center'][axis]+r['extent'][axis] for r in rs)/100]
    dimensions={}
    for sign in [-1,1]:
        dimensions['beam_union_'+str(sign)]=[span(['RA01_EndPier_'+str(sign),'RA01_Beam_'+str(sign)],0),span(['RA01_Beam_'+str(sign)],2)]
        check('beam primary span '+str(sign),all(abs(v-w)<.001 for v,w in zip(dimensions['beam_union_'+str(sign)][0],[-30,30])))
        upper=span(['RA01_UpperWall_'+str(sign)],1)
        inner=upper[0] if sign>0 else -upper[1]
        dimensions['upper_inner_abs_y_'+str(sign)]=inner
        check('A 0.6m upper setback '+str(sign),abs(inner-6.2)<.001,inner)
        gap=span(['RA01_FirstPier_'+str(sign)],0)[0]-span(['RA01_EndPier_'+str(sign)],0)[1]
        dimensions['terminal_gap_'+str(sign)]=gap
        check('A terminal 6.6m gap '+str(sign),abs(gap-6.6)<.001,gap)
    check('six free pier pairs',sum(n.startswith('Pier_') for n in rows)+sum(n.startswith('RA01_FirstPier_') for n in rows)==12)
    world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
    gamemode=world.get_world_settings().get_editor_property('default_game_mode').get_path_name()
    check('gameplay class',gamemode=='/Script/MeridianSquad.OpeningLobbyGameMode',gamemode)
    kit=json.loads((OUT/'kit.json').read_text())['assets'];meshes={};smes=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
    for name,item in kit.items():
        mesh=u.load_asset(ASSETS+'/Meshes/'+item['object']);bounds=mesh.get_bounds()
        size=[bounds.box_extent.x*2/100,bounds.box_extent.y*2/100,bounds.box_extent.z*2/100]
        body=mesh.get_editor_property('body_setup')
        imp=mesh.get_editor_property('asset_import_data')
        build=smes.get_lod_build_settings(mesh,0)
        record=dict(dimensions_m=size,pivot_origin_cm=[bounds.origin.x,bounds.origin.y,bounds.origin.z],
            max_error_m=max(abs(a-b) for a,b in zip(size,data['modules'][name]['size_m'])),
            uv_channels=smes.get_num_uv_channels(mesh,0),material_slots=len(mesh.static_materials),
            lod_count=mesh.get_num_lods(),collision=str(body.get_editor_property('collision_trace_flag')),
            import_source=list(imp.extract_filenames()),import_data_class=imp.get_class().get_name(),
            build_settings={k:str(build.get_editor_property(k)) for k in ['recompute_normals','recompute_tangents','generate_lightmap_u_vs','build_scale3d']},
            materials=[m.material_interface.get_path_name() for m in mesh.static_materials])
        meshes[name]=record
        check(name+' imported normals/tangents retained',not build.recompute_normals and not build.recompute_tangents)
        check(name+' source/import properties',record['max_error_m']<.001 and record['uv_channels']>0 and record['material_slots']==1 and all(abs(v)<.01 for v in record['pivot_origin_cm']) and 'USE_COMPLEX_AS_SIMPLE' in record['collision'],record)
    blocking={n:r for n,r in rows.items() if r.get('profile')=='BlockAll'}
    profile=profiles()
    check('actual imported A sections and soffit closure',profile['passed'])
    report=dict(map=MAP,state=state(),saved_and_reopened=True,actor_bounds=rows,blocking_bounds=blocking,
        checks=checks,dimensions=dimensions,failures=errors,passed=not errors,game_mode=gamemode,design_sha256=data['design_sha256'])
    (OUT/'construction.json').write_text(json.dumps(report,indent=2))
    (OUT/'asset-audit.json').write_text(json.dumps(dict(meshes=meshes,passed=not errors),indent=2))
    assert not errors,errors
    return dict(passed=True,checks=len(checks),actors=len(rows),meshes=len(meshes),game_mode=gamemode)

def action(operation,argument=''):
    if operation=='inspect':return state()
    if operation=='final_state':
        s=guard(clean=True)
        import reworka01_capture as capture
        import reworka01_walk as walk
        assert capture._settings is None and walk.status()['done']
        throttle=u.get_default_object(u.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).get_editor_property('bThrottleCPUWhenNotForeground')
        expected=json.loads((OUT/'capture-settings-before.json').read_text())['throttle'];assert throttle==expected
        s.update(capture_overrides_restored=True,throttle_restored=True,game_mode='/Script/MeridianSquad.OpeningLobbyGameMode',
                 active_verifier_done=True,source_native_saved=str(SRC/'LobbyArchitectureReworkA01.blend'))
        (OUT/'final-state.json').write_text(json.dumps(s,indent=2));return s
    if operation=='runtime_settings':
        s=state();assert s['pie'] and 'L_OpeningLobby_ArchitectureReworkA01' in s['level']
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world();pawn=u.GameplayStatics.get_player_pawn(world,0)
        camera=pawn.get_component_by_class(u.CameraComponent)
        movement=pawn.get_component_by_class(u.CharacterMovementComponent)
        report=dict(state=s,max_walk_speed=movement.max_walk_speed,camera_fov=camera.field_of_view,
            throttle=u.get_default_object(u.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).get_editor_property('bThrottleCPUWhenNotForeground'))
        assert report['max_walk_speed']==360 and report['camera_fov']==90 and s['capsule_radius']==34 and s['capsule_half_height']==88
        (OUT/'runtime-settings.json').write_text(json.dumps(report,indent=2));return report
    if operation=='profile_probe':
        return profiles()
    if operation=='correct_handedness':return correct_handedness()
    if operation=='create':return create()
    if operation=='import':return import_assets()
    if operation=='assemble':return assemble()
    if operation=='audit':return audit()
    if operation=='save_reopen':
        save();assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP);return audit()
    if operation.startswith('capture_'):
        import reworka01_capture as capture
        return getattr(capture,operation[len('capture_'):])(argument)
    if operation in ['verify','status']:
        import reworka01_walk as walk
        walk=importlib.reload(walk)
        return walk.start(argument or 'full') if operation=='verify' else walk.status()
    raise ValueError(operation)
