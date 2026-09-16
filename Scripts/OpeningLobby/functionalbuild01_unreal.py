"""Scoped neutral assembly using the existing saved-scene and import patterns."""
import json
import re
from pathlib import Path
import unreal as u
from stage1_tools import state
from layout02_verification import require_project
from reworka01_unreal import snapshot
ROOT=Path('D:/devgames/MeridianSquad')
OUT=ROOT/'Saved/OpeningLobby/FunctionalBuild01/Worker'
MAP='/Game/Maps/L_OpeningLobby_FunctionalBuild01'
BASE='/Game/Maps/L_OpeningLobby_ArchitectureReworkA01'
ASSETS='/Game/OpeningLobby/FunctionalBuild01'
from functionalbuild01_data import geometry,replaced,D

def save():
    guard()
    for p in u.EditorLoadingAndSavingUtils.get_dirty_content_packages():
        assert p.get_path_name().startswith(ASSETS)
        assert u.EditorAssetLibrary.save_asset(p.get_path_name())
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()

def create():
    guard(False,True);assert not u.EditorAssetLibrary.does_asset_exist(MAP)
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).new_level_from_template(MAP,BASE)
    save();return state()

def import_assets():
    guard(clean=True);assert not u.EditorAssetLibrary.does_directory_exist(ASSETS+'/Meshes')
    kit=json.loads((OUT/'kit.json').read_text())['assets'];tasks=[]
    for name,item in kit.items():
        task=u.AssetImportTask();task.filename=str(ROOT/item['export']);task.destination_path=ASSETS+'/Meshes'
        task.destination_name=item['object'];task.automated=True;task.save=True
        options=u.FbxImportUI();options.import_mesh=True;options.import_materials=False;options.import_textures=False
        options.import_as_skeletal=False;options.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH
        options.static_mesh_import_data.combine_meshes=True;options.static_mesh_import_data.generate_lightmap_u_vs=False
        options.static_mesh_import_data.auto_generate_collision=False
        options.static_mesh_import_data.normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
        task.options=options;tasks.append(task)
    u.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    records=[];modules=geometry()['modules']
    for (name,item),task in zip(kit.items(),tasks):
        assert task.imported_object_paths,task.filename
        mesh=u.load_asset(task.imported_object_paths[0]);body=mesh.get_editor_property('body_setup');assert body
        body.set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        mesh.set_material(0,u.load_asset('/Game/OpeningLobby/ArchitectureReworkA01/Materials/M_RA01_'+modules[name]['material']))
        assert u.EditorAssetLibrary.save_loaded_asset(mesh)
        records.append({'module':name,'assets':list(task.imported_object_paths),'collision':str(body.get_editor_property('collision_trace_flag'))})
    (OUT/'imports.json').write_text(json.dumps(records,indent=2));save();return {'imported':len(records)}

def assemble():
    guard(clean=True);aes=u.get_editor_subsystem(u.EditorActorSubsystem)
    actors={a.get_actor_label():a for a in aes.get_all_level_actors()};assert not any(n.startswith('FB01_') for n in actors)
    removed=[]
    for name,a in actors.items():
        if replaced(name):assert aes.destroy_actor(a);removed.append(name)
    data=geometry()
    for name,item in data['instances'].items():
        mesh=u.load_asset(ASSETS+'/Meshes/SM_FB01_'+item['module']);assert mesh
        actor=aes.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*(v*100 for v in item['center_m'])))
        actor.set_actor_label('FB01_'+name);actor.set_folder_path('FunctionalBuild01')
        c=actor.static_mesh_component;c.set_static_mesh(mesh);c.set_collision_profile_name('BlockAll');c.set_mobility(u.ComponentMobility.STATIC)
    (OUT/'replacement-record.json').write_text(json.dumps({'removed':removed,'added':list(data['instances']),'unchanged_context_reused':True},indent=2))
    save();assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
    return audit()

def profiles():
    guard(clean=True);world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world();probes=[]
    def trace(name,start,end,axis,target,expected_actor=None):
        hit=u.SystemLibrary.line_trace_single(world,u.Vector(*start),u.Vector(*end),u.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],u.DrawDebugTrace.NONE,True)
        values=hit.to_tuple();p=values[4];xyz=[p.x,p.y,p.z];actor=values[9].get_actor_label() if values[9] else None
        passed=bool(values[0]) and abs(xyz[axis]-target)<.2 and (expected_actor is None or actor==expected_actor)
        probes.append({'name':name,'start_cm':start,'end_cm':end,'axis':axis,'expected_cm':target,'impact_cm':xyz,'actor':actor,'passed':passed})
    for sign in [-1,1]:
        for z in [50,150,230]:
            trace('entrance_leaf_'+str(sign)+'_'+str(z),[-1900,sign*1000,z],[-2100,sign*1000,z],0,-2004)
            trace('inner_leaf_'+str(sign)+'_'+str(z),[2610,0,z],[2610,sign*650,z],1,sign*584)
        for offset in [-66,66]:
            trace('entrance_frame_'+str(sign)+'_'+str(offset),[-1900,sign*1000+offset,120],[-2100,sign*1000+offset,120],0,-1980)
            trace('inner_frame_'+str(sign)+'_'+str(offset),[2610+offset,0,120],[2610+offset,sign*650,120],1,sign*560)
        trace('entrance_door_head_'+str(sign),[-1900,sign*1000,246],[-2100,sign*1000,246],0,-1980)
        trace('inner_door_head_'+str(sign),[2610,0,246],[2610,sign*650,246],1,sign*560)
        trace('entrance_blind_wall_'+str(sign),[-2600,0,150],[-2600,sign*650,150],1,sign*560)
        trace('inner_blind_cap_'+str(sign),[1800,sign*1000,150],[2200,sign*1000,150],0,1980)
        trace('room_band_roof_'+str(sign),[-2500,sign*680,700],[-2500,sign*680,1000],2,804)
        trace('room_aisle_roof_'+str(sign),[-2500,sign*1000,700],[-2500,sign*1000,1000],2,884)
        trace('inner_band_roof_'+str(sign),[2500,sign*680,700],[2500,sign*680,1000],2,804)
        trace('inner_aisle_roof_'+str(sign),[2500,sign*1000,700],[2500,sign*1000,1000],2,884)
        # The lower roof step closes directly against the retained beam side.
        trace('roof_step_beam_contact_'+str(sign),[-2050,sign*900,860],[-2050,sign*750,860],1,sign*800)
        for x in [-1260,1260]:
            trace('column_face_'+str(x)+'_'+str(sign),[x-250,sign*240,1700],[x,sign*240,1700],0,x-120)
            trace('column_top_'+str(x)+'_'+str(sign),[x,sign*240,1850],[x,sign*240,1750],2,1840,'CentralCeiling')
        trace('lane_left_'+str(sign),[-2460,sign*465,120],[-2460,sign*600,120],1,sign*540)
        trace('lane_right_'+str(sign),[-2460,sign*465,120],[-2460,sign*300,120],1,sign*390)
        trace('lane_head_'+str(sign),[-2460,sign*465,172],[-2460,sign*465,300],2,240)
        trace('elevator_jamb_'+str(sign),[2800,sign*200,200],[3100,sign*200,200],0,2940)
        trace('elevator_leaf_'+str(sign),[2800,sign*90,200],[3100,sign*90,200],0,3000)
    trace('elevator_head',[2800,0,440],[3100,0,440],0,2940)
    for y in [-250,0,250]:
        for z in [1200,1500,1720]:trace('opaque_'+str(y)+'_'+str(z),[2800,y,z],[3100,y,z],0,3000,'FB01_InnerOpaqueWall')
    report={'passed':all(p['passed'] for p in probes),'probes':probes,'method':'Complex collision traces against reopened imported geometry'}
    (OUT/'imported-profile-probes.json').write_text(json.dumps(report,indent=2));return report

def audit():
    guard(clean=True);data=geometry();rows=snapshot();baseline=json.loads((OUT/'baseline-actual.json').read_text());checks=[]
    def check(name,passed,actual=None):checks.append({'name':name,'passed':bool(passed),'actual':actual})
    for name,item in data['instances'].items():
        row=rows.get('FB01_'+name);check(name+' present',row is not None)
        if row is None:continue
        error=max([abs(v/100-w) for v,w in zip(row['center'],item['center_m'])]+[abs(2*v/100-w) for v,w in zip(row['extent'],item['size_m'])])
        check(name+' measured bounds',error<.001,error)
        check(name+' local visible static collision',row['profile']=='BlockAll' and row['visible'] and row['scale']==[1,1,1] and row['mesh'].startswith(ASSETS),row)
    for name,old in baseline.items():
        if replaced(name):check(name+' obsolete removed',name not in rows);continue
        now=rows.get(name)
        def comparable(v):return re.sub(r'0x[0-9A-Fa-f]+','ADDRESS',v) if isinstance(v,str) else v
        check(name+' preserved',now is not None and all(comparable(now[k])==comparable(old[k]) for k in old))
    smes=u.get_editor_subsystem(u.StaticMeshEditorSubsystem);meshes={}
    for name,item in data['modules'].items():
        mesh=u.load_asset(ASSETS+'/Meshes/SM_FB01_'+name);b=mesh.get_bounds();settings=smes.get_lod_build_settings(mesh,0)
        size=[b.box_extent.x*2/100,b.box_extent.y*2/100,b.box_extent.z*2/100]
        body=mesh.get_editor_property('body_setup')
        record={'dimensions_m':size,'pivot_cm':[b.origin.x,b.origin.y,b.origin.z],'uv_channels':smes.get_num_uv_channels(mesh,0),
                'material_slots':len(mesh.static_materials),'collision':str(body.get_editor_property('collision_trace_flag')),
                'recompute_normals':settings.recompute_normals,'recompute_tangents':settings.recompute_tangents,
                'import_sources':list(mesh.get_editor_property('asset_import_data').extract_filenames())}
        meshes[name]=record
        check(name+' import audit',max(abs(a-b) for a,b in zip(size,item['size_m']))<.001 and record['uv_channels']>0 and record['material_slots']==1 and max(abs(v) for v in record['pivot_cm'])<.1 and not settings.recompute_normals and not settings.recompute_tangents and 'USE_COMPLEX_AS_SIMPLE' in record['collision'],record)
    profile=profiles();check('actual imported profiles',profile['passed'])
    world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world();mode=world.get_world_settings().get_editor_property('default_game_mode').get_path_name()
    check('GameMode',mode=='/Script/MeridianSquad.OpeningLobbyGameMode',mode)
    failures=[c['name'] for c in checks if not c['passed']]
    report={'map':MAP,'state':state(),'saved_and_reopened':True,'actor_bounds':rows,'checks':checks,'failures':failures,'passed':not failures,'game_mode':mode}
    (OUT/'construction.json').write_text(json.dumps(report,indent=2));(OUT/'asset-audit.json').write_text(json.dumps({'meshes':meshes,'passed':not failures},indent=2))
    return {'passed':not failures,'checks':len(checks),'actors':len(rows),'meshes':len(meshes),'failed':failures}

def guard(candidate=True,clean=False):
    s=state();require_project(s['project']);assert not s['pie'],s
    if candidate:assert s['level'].split('.')[0]==MAP,s
    assert all(p.startswith(ASSETS) for p in s['dirty_content']),s
    assert all(p==MAP for p in s['dirty_maps']),s
    if clean:assert not s['dirty_content'] and not s['dirty_maps'],s
    return s

def action(operation,argument=''):
    if operation=='capture_refine_views':
        import functionalbuild01_capture as capture
        capture._capture.VIEWS.update({'inner-door-positive-90':(2610,80,90,5),'inner-door-negative-90':(2610,-80,-90,5),'elevator-detail-90':(2500,0,0,6),'column-contact-90':(-2100,0,0,45)})
        return {'updated':'Supplementary framing includes full thresholds and ceiling contacts; matched sheet poses unchanged'}
    if operation=='refine_elevator':
        guard(clean=True)
        mesh=u.load_asset(ASSETS+'/Meshes/SM_FB01_ElevatorLeaves');assert mesh
        task=u.AssetImportTask();task.filename=str(OUT/'FBX/SM_FB01_ElevatorLeaves.fbx');task.destination_path=ASSETS+'/Meshes'
        task.destination_name='SM_FB01_ElevatorLeaves';task.automated=True;task.save=True;task.replace_existing=True;task.replace_existing_settings=True
        options=u.FbxImportUI();options.import_mesh=True;options.import_materials=False;options.import_textures=False
        options.import_as_skeletal=False;options.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH
        options.static_mesh_import_data.combine_meshes=True;options.static_mesh_import_data.generate_lightmap_u_vs=False
        options.static_mesh_import_data.auto_generate_collision=False
        options.static_mesh_import_data.normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
        task.options=options;u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        mesh=u.load_asset(ASSETS+'/Meshes/SM_FB01_ElevatorLeaves')
        mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        mesh.set_material(0,u.load_asset('/Game/OpeningLobby/ArchitectureReworkA01/Materials/M_RA01_Metal'))
        assert u.EditorAssetLibrary.save_loaded_asset(mesh);save()
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
        return audit()
    if operation=='final_state':
        s=guard(clean=True)
        import functionalbuild01_capture as capture
        import functionalbuild01_walk as walk
        assert capture._capture._settings is None and walk.status()['done'] and walk.status()['passed']
        throttle=u.get_default_object(u.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).get_editor_property('bThrottleCPUWhenNotForeground')
        assert throttle==json.loads((OUT/'capture-settings-before.json').read_text())['throttle']
        s.update(capture_overrides_restored=True,throttle_restored=True,active_verifier_done=True,game_mode='/Script/MeridianSquad.OpeningLobbyGameMode')
        (OUT/'final-state.json').write_text(json.dumps(s,indent=2));return s
    if operation.startswith('capture_'):
        import functionalbuild01_capture as capture
        return getattr(capture,operation[len('capture_'):])(argument)
    if operation in ['verify','verify_elevator','status']:
        import importlib
        import functionalbuild01_walk as walk
        if operation!='status':walk=importlib.reload(walk)
        return walk.start('elevator' if operation=='verify_elevator' else 'full') if operation!='status' else walk.status()
    if operation=='runtime_settings':
        s=state();assert s['pie'] and 'L_OpeningLobby_FunctionalBuild01' in s['level']
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world();pawn=u.GameplayStatics.get_player_pawn(world,0)
        camera=pawn.get_component_by_class(u.CameraComponent);movement=pawn.get_component_by_class(u.CharacterMovementComponent)
        report={'state':s,'max_walk_speed':movement.max_walk_speed,'camera_fov':camera.field_of_view}
        assert movement.max_walk_speed==360 and camera.field_of_view==90 and s['capsule_radius']==34 and s['capsule_half_height']==88
        (OUT/'runtime-settings.json').write_text(json.dumps(report,indent=2));return report
    if operation=='create':return create()
    if operation=='import':return import_assets()
    if operation=='assemble':return assemble()
    if operation=='audit':return audit()
    if operation=='save_reopen':
        save();assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP);return audit()
    if operation=='inspect':
        s=guard(False,True);OUT.mkdir(parents=True,exist_ok=True)
        (OUT/'editor-preflight.json').write_text(json.dumps(s,indent=2));return s
    if operation=='baseline':
        guard(False,True);assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(BASE)
        rows=snapshot();(OUT/'baseline-actual.json').write_text(json.dumps(rows,indent=2))
        return {'state':state(),'actors':len(rows)}
    raise ValueError(operation)
