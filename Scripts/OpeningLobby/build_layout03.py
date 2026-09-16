"""Neutral blockout from immutable owner-approved LobbyScale-Review01 metres."""
import hashlib
import json
from pathlib import Path
import unreal as u
from layout02_verification import require_project

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'Saved/OpeningLobby/Layout03'
MAP = '/Game/Maps/L_OpeningLobby_Layout03'
MAT = '/Game/OpeningLobby/Layout03/Materials'
SCHEDULE = ROOT/'Assets/Concepts/OpeningLobby/ScaleReview01/schedule.json'

def build():
    require_project(u.Paths.get_project_file_path())
    assert hashlib.sha256((SCHEDULE.parent/'manifest.json').read_bytes()).hexdigest() == 'e7c113fd8b74ea2106d8af29391cdfece7a1f763db272fb9727da0568a65efb6'
    les = u.get_editor_subsystem(u.LevelEditorSubsystem)
    aes = u.get_editor_subsystem(u.EditorActorSubsystem)
    editor = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert not editor.get_game_world()
    assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    assert not u.EditorLoadingAndSavingUtils.get_dirty_content_packages()
    assert not u.EditorAssetLibrary.does_asset_exist(MAP), 'Never overwrite an existing revision.'
    s = json.loads(SCHEDULE.read_text())
    a, e, h = s['architecture']['candidate'], s['end_fields']['candidate'], s['human_elements']
    assert les.new_level(MAP)
    materials = {}
    for name, color, rough, glow in [
        ('Floor',(.32,.34,.33),.65,0), ('Strip',(.045,.05,.05),.65,0),
        ('Stone',(.15,.17,.17),.8,0), ('Wall',(.46,.48,.47),.85,0),
        ('Ceiling',(.38,.40,.39),.85,0), ('Metal',(.09,.11,.11),.65,0),
        ('Glazing',(.48,.65,.67),.65,.5)]:
        m = u.AssetToolsHelpers.get_asset_tools().create_asset('M_Layout03_'+name,MAT,u.Material,u.MaterialFactoryNew())
        assert m
        c = u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant3Vector,-350,0)
        c.set_editor_property('constant',u.LinearColor(*color,1))
        u.MaterialEditingLibrary.connect_material_property(c,'',u.MaterialProperty.MP_BASE_COLOR)
        r = u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant,-350,150)
        r.set_editor_property('r',rough)
        u.MaterialEditingLibrary.connect_material_property(r,'',u.MaterialProperty.MP_ROUGHNESS)
        if glow:
            g = u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant3Vector,-350,300)
            g.set_editor_property('constant',u.LinearColor(*(v*glow for v in color),1))
            u.MaterialEditingLibrary.connect_material_property(g,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
        u.MaterialEditingLibrary.recompile_material(m)
        assert u.EditorAssetLibrary.save_loaded_asset(m)
        materials[name] = m
    cube = u.load_asset('/Engine/BasicShapes/Cube.Cube')
    expected = {}

    def box(name,loc,size,material,folder='Architecture',blocking=True):
        # All design values remain metres until this single Unreal conversion.
        actor = aes.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*(v*100 for v in loc)))
        actor.set_actor_label(name)
        actor.set_folder_path('Layout03/'+folder)
        component = actor.static_mesh_component
        component.set_static_mesh(cube)
        component.set_material(0,materials[material])
        component.set_collision_profile_name('BlockAll' if blocking else 'NoCollision')
        actor.set_actor_scale3d(u.Vector(*size))
        expected[name] = dict(center_m=list(loc),size_m=list(size),blocking=blocking)
        return actor

    length,width,height = a['length'],a['width'],a['height']
    # 0.4 m shell thickness is only a placeholder outside scheduled interior faces.
    t = .4
    box('Floor',(0,0,-t/2),(length+2*t,width+2*t,t),'Floor')
    for sign in [-1,1]:
        box('SideWall_'+str(sign),(0,sign*(width/2+t/2),a['aisle_height']/2),(length+2*t,t,a['aisle_height']),'Wall')
        box('SideAisleCeiling_'+str(sign),(0,sign*(width/2-a['aisle_clear']/2),a['aisle_height']+t/2),(length,a['aisle_clear'],t),'Ceiling','Ceiling')
        y = sign*a['pier_y']
        box('LongLintel_'+str(sign),(0,y,a['lintel_underside']+a['lintel_depth']/2),(length,a['lintel_width'],a['lintel_depth']),'Stone')
        bottom = a['lintel_underside']+a['lintel_depth']
        box('UpperInfill_'+str(sign),(0,y,(bottom+height)/2),(length,a['lintel_width'],height-bottom),'Wall')
        for index,x in enumerate(a['pier_x']):
            box('Pier_%s_%s'%(index,sign),(x,y,a['shaft_height']/2),(a['pier_size'],a['pier_size'],a['shaft_height']),'Stone','Piers')
        box('FloorStrip_'+str(sign),(0,sign*a['floor_strip_y'],.001),(length,a['floor_strip_width'],.002),'Strip','Floor',False)
    box('CentralCeiling',(0,0,height+t/2),(length+2*t,2*(a['pier_y']+a['pier_size']/2),t),'Ceiling','Ceiling')
    for sign,name in [(-1,'Entrance'),(1,'Inner')]:
        x = sign*(length/2+t/2)
        box(name+'Boundary',(x,0,height/2),(t,2*(a['pier_y']+a['pier_size']/2),height),'Wall')
        for side in [-1,1]:
            box(name+'AisleEnd_'+str(side),(x,side*(width/2-a['aisle_clear']/2),a['aisle_height']/2),(t,a['aisle_clear'],a['aisle_height']),'Wall')
            # Visible facing is 3 cm inside the nominal end plane; no wall coplanarity.
            box(name+'EndBand_'+str(side),(sign*(length/2-.02),side*a['pier_y'],height/2),(.02,a['pier_size'],height),'Stone','EndFields',False)
    # Opaque, neutral glazing proxies sit immediately in front of closed boundaries.
    x = -length/2+.025
    w = e['entrance_field_width']
    box('EntranceUpperGlazing',(x,0,e['upper_sill']+e['upper_height']/2),(.04,w,e['upper_height']),'Glazing','Entrance',False)
    box('EntranceLowerField',(-length/2+.01,0,e['entry_field_height']/2),(.01,w,e['entry_field_height']),'Glazing','Entrance',False)
    for y in [-w/2,-w/4,0,w/4,w/2]:
        box('EntranceUpperMullion_'+str(y),(x+.04,y,e['upper_sill']+e['upper_height']/2),(.04,.04,e['upper_height']),'Metal','Entrance',False)
    for index in range(6):
        z = e['upper_sill']+index*e['upper_height']/5
        box('EntranceUpperTransom_'+str(index),(x+.04,0,z),(.04,w,.04),'Metal','Entrance',False)
    leaves = h['entrance_leaves']
    lw,lh = leaves['candidate_leaf_width'],leaves['candidate_leaf_height']
    for sign in [-1,1]:
        box('EntranceLeaf_'+str(sign),(-length/2+.035,sign*lw/2,lh/2),(.01,lw,lh),'Glazing','Entrance',False)
    for y in [-lw,0,lw]:
        box('EntranceLeafMullion_'+str(y),(x+.09,y,lh/2),(.035,.025,lh),'Metal','Entrance',False)
    box('EntranceLeafHead',(x+.09,0,lh),(.035,2*lw,.025),'Metal','Entrance',False)
    for y in [-w/2,w/2]:
        box('EntranceFieldEdge_'+str(y),(x+.04,y,e['entry_field_height']/2),(.04,.04,e['entry_field_height']),'Metal','Entrance',False)
    door = h['inner_door']
    # Technical proxy depths, not approved fabrication thicknesses. Leaf centers
    # are measured against the schedule's nominal end planes (+/-30 m).
    box('InnerDoorFrame',(length/2-.015,0,door['candidate_frame_height']/2),(.01,door['candidate_frame_width'],door['candidate_frame_height']),'Metal','Inner',False)
    box('InnerDoorLeaf',(length/2-.035,0,door['candidate_height']/2),(.01,door['candidate_width'],door['candidate_height']),'Strip','Inner',False)
    iw,ih,iz = e['inner_window_width'],e['inner_window_height'],e['inner_window_sill']
    box('InnerHighWindow',(length/2-.025,0,iz+ih/2),(.04,iw,ih),'Glazing','Inner',False)
    for y in [-iw/2,0,iw/2]:
        box('InnerWindowMullion_'+str(y),(length/2-.065,y,iz+ih/2),(.04,.04,ih),'Metal','Inner',False)
    for index in range(3):
        box('InnerWindowTransom_'+str(index),(length/2-.065,0,iz+index*ih/2),(.04,iw,.04),'Metal','Inner',False)
    d = h['detector']
    for sign in [-1,1]:
        box('DetectorPost_'+str(sign),(d['x'],d['y']+sign*(d['clear_width']+d['post_width'])/2,d['clear_height']/2),(d['depth'],d['post_width'],d['clear_height']),'Metal','Checkpoint')
    box('DetectorHeader',(d['x'],d['y'],d['clear_height']+d['header_depth']/2),(d['depth'],d['clear_width']+2*d['post_width'],d['header_depth']),'Metal','Checkpoint')
    station = h['station']
    box('StationBody',(station['x'],station['y'],station['body_height']/2),(station['depth_x'],station['width_y'],station['body_height']),'Stone','Checkpoint')
    box('StationWorktop',(station['x'],station['y'],station['worktop_height']-station['worktop_thickness']/2),(station['worktop_depth_x'],station['worktop_width_y'],station['worktop_thickness']),'Metal','Checkpoint')
    for x in [-25,-15,-5,5,15,25]:
        for y in [-10,0,10]:
            light = aes.spawn_actor_from_class(u.PointLight,u.Vector(x*100,y*100,650 if y else 1400))
            light.set_actor_label('NeutralFill_%s_%s'%(x,y))
            light.set_folder_path('Layout03/Lighting')
            c = light.point_light_component
            c.set_mobility(u.ComponentMobility.MOVABLE)
            c.set_editor_property('intensity_units',u.LightUnits.LUMENS)
            c.set_editor_property('intensity',45000. if y else 100000.)
            c.set_editor_property('attenuation_radius',1900. if y else 2600.)
            c.set_editor_property('source_radius',150.)
            c.set_editor_property('use_temperature',True)
            c.set_editor_property('temperature',6500.)
    pp = aes.spawn_actor_from_class(u.PostProcessVolume,u.Vector())
    pp.set_actor_label('Layout03NeutralExposure')
    pp.set_folder_path('Layout03/Lighting')
    pp.set_editor_property('unbound',True)
    settings = pp.get_editor_property('settings')
    for name,value in [('override_auto_exposure_method',True),('auto_exposure_method',u.AutoExposureMethod.AEM_MANUAL),
                       ('override_auto_exposure_bias',True),('auto_exposure_bias',-5.),
                       ('override_auto_exposure_apply_physical_camera_exposure',True),('auto_exposure_apply_physical_camera_exposure',False),
                       ('override_bloom_intensity',True),('bloom_intensity',0.),
                       ('override_motion_blur_amount',True),('motion_blur_amount',0.)]:
        settings.set_editor_property(name,value)
    pp.set_editor_property('settings',settings)
    start = aes.spawn_actor_from_class(u.PlayerStart,u.Vector(-2850,-105,100),u.Rotator(0,0,0))
    start.set_actor_label('Layout03EntranceStart')
    start.set_folder_path('Layout03/Gameplay')
    editor.get_editor_world().get_world_settings().set_editor_property('default_game_mode',u.load_class(None,'/Script/MeridianSquad.OpeningLobbyGameMode'))
    editor.set_level_viewport_camera_info(u.Vector(-1900,0,172),u.Rotator(0,0,0))
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'expected-geometry.json').write_text(json.dumps(expected,indent=2))
    assert les.save_current_level()
    assert les.load_level(MAP)
    return inspect_geometry()

def inspect_geometry():
    require_project(u.Paths.get_project_file_path())
    assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().split('.')[0] == MAP
    expected = json.loads((OUT/'expected-geometry.json').read_text())
    actual,blocking,failures = {},{},[]
    for actor in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
        name = actor.get_actor_label()
        if name not in expected:
            continue
        center,extent = actor.get_actor_bounds(False)
        center = [center.x,center.y,center.z]
        extent = [extent.x,extent.y,extent.z]
        target = expected[name]
        errors = [abs(v/100-w) for v,w in zip(center,target['center_m'])]+[abs(2*v/100-w) for v,w in zip(extent,target['size_m'])]
        actual[name] = dict(center=center,extent=extent,max_error_m=max(errors))
        if target['blocking']:
            blocking[name] = actual[name]
        if max(errors) > .05:
            failures.append(name)
    missing = sorted(set(expected)-set(actual))
    result = dict(map=MAP,schedule_sha256=hashlib.sha256(SCHEDULE.read_bytes()).hexdigest(),saved_and_reopened=True,
                  actor_bounds=actual,blocking_bounds=blocking,failures=failures,missing=missing,passed=not failures and not missing,
                  placeholder_shell_thickness_m=.4)
    (OUT/'construction.json').write_text(json.dumps(result,indent=2))
    assert result['passed'],result
    return dict(map=MAP,measured_actors=len(actual),passed=True)


def correction_snapshot(stage):
    """Actual geometry/collision inventory and unchanged lighting/gameplay anchors."""
    from stage1_tools import state
    s = state()
    require_project(s['project'])
    assert not s['pie'] and s['level'].split('.')[0] == MAP,s
    result = dict(state=s,actors={})
    for actor in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
        name = actor.get_actor_label()
        c,e = actor.get_actor_bounds(False)
        row = dict(center=[c.x,c.y,c.z],extent=[e.x,e.y,e.z],
                   transform=str(actor.get_actor_transform()),hidden=actor.is_temporarily_hidden_in_editor())
        components = actor.get_components_by_class(u.PrimitiveComponent)
        row['collision'] = [dict(profile=str(comp.get_collision_profile_name()),enabled=str(comp.get_collision_enabled()),
                                 responses=[str(comp.get_collision_response_to_channel(channel)) for channel in
                                            [u.CollisionChannel.ECC_WORLD_STATIC,u.CollisionChannel.ECC_WORLD_DYNAMIC,u.CollisionChannel.ECC_PAWN]],
                                 material=[str(comp.get_material(i)) for i in range(comp.get_num_materials())]) for comp in components]
        if isinstance(actor,u.PointLight):
            comp = actor.point_light_component
            row['lighting'] = {key:str(comp.get_editor_property(key)) for key in ['intensity','intensity_units','attenuation_radius','source_radius','use_temperature','temperature','mobility']}
        if isinstance(actor,u.PostProcessVolume):
            pp = actor.get_editor_property('settings')
            row['exposure'] = {key:str(pp.get_editor_property(key)) for key in ['auto_exposure_method','auto_exposure_bias','auto_exposure_apply_physical_camera_exposure','bloom_intensity','motion_blur_amount']}
            row['unbound'] = actor.get_editor_property('unbound')
        result['actors'][name] = row
    world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
    result['game_mode'] = world.get_world_settings().get_editor_property('default_game_mode').get_path_name()
    (OUT/'Correction01'/(stage+'-actual.json')).write_text(json.dumps(result,indent=2))
    return dict(stage=stage,actors=len(result['actors']),state=s)


def correct_end_proxies():
    """Single bounded correction; refuses dirty state or an already applied revision."""
    from stage1_tools import state
    s = state()
    require_project(s['project'])
    assert not s['pie'] and s['level'].split('.')[0] == MAP,s
    assert not s['dirty_maps'] and not s['dirty_content'],s
    assert (OUT/'Review01Preserved/L_OpeningLobby_Layout03.umap').is_file()
    assert not (OUT/'Correction01/before-actual.json').exists(), 'Correction already started; inspect evidence before retry.'
    correction_snapshot('before')
    expected = json.loads((OUT/'expected-geometry.json').read_text())
    changes = {name:(sign*29.98,.02) for sign,end in [(-1,'Entrance'),(1,'Inner')] for name in [end+'EndBand_-1',end+'EndBand_1']}
    changes.update(EntranceLowerField=(-29.99,.01),InnerDoorFrame=(29.985,.01),InnerDoorLeaf=(29.965,.01))
    changes.update({f'EntranceLeaf_{sign}':(-29.965,.01) for sign in [-1,1]})
    actors = {a.get_actor_label():a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()}
    for name in changes:
        assert str(actors[name].static_mesh_component.get_collision_profile_name()) == 'NoCollision',name
        assert not expected[name]['blocking']
    for name,(x,depth) in changes.items():
        actor = actors[name]
        pos,scale = actor.get_actor_location(),actor.get_actor_scale3d()
        pos.x,scale.x = x*100,depth
        actor.set_actor_location(pos,False,False)
        actor.set_actor_scale3d(scale)
        expected[name]['center_m'][0],expected[name]['size_m'][0] = x,depth
    (OUT/'expected-geometry.json').write_text(json.dumps(expected,indent=2))
    return dict(changed=changes,requires_save_reopen=True)
