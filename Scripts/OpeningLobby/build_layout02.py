"""Bounded prototype interpretation of the approved LobbyArt-Review02 images."""
import json
from pathlib import Path
import unreal as u
from layout02_verification import require_project

MAP = '/Game/Maps/L_OpeningLobby_Layout02'
MAT = '/Game/OpeningLobby/Layout02/Materials'

def build():
    require_project(u.Paths.get_project_file_path())
    les = u.get_editor_subsystem(u.LevelEditorSubsystem)
    aes = u.get_editor_subsystem(u.EditorActorSubsystem)
    editor = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert not editor.get_game_world()
    assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    assert not u.EditorLoadingAndSavingUtils.get_dirty_content_packages()
    assert not u.EditorAssetLibrary.does_asset_exist(MAP), 'Never overwrite an existing revision.'
    assert les.new_level(MAP)
    materials = {}
    for name,color,rough,metal,glow in [
        ('Floor',(.13,.19,.165),.18,0,0),
        ('BlackStrip',(.012,.018,.017),.24,0,0),
        ('Stone',(.04,.065,.053),.44,0,0),
        ('Wall',(.06,.085,.07),.48,0,0),
        ('Ceiling',(.045,.065,.058),.75,0,0),
        ('Metal',(.04,.06,.06),.28,.8,0),
        ('Glazing',(.24,.40,.41),.16,.15,.65),
        ('Light',(.5,.85,.85),.3,0,4),
    ]:
        m = u.AssetToolsHelpers.get_asset_tools().create_asset('M_Layout02_'+name,MAT,u.Material,u.MaterialFactoryNew())
        assert m
        e = u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant3Vector,-350,0)
        e.set_editor_property('constant',u.LinearColor(*color,1))
        u.MaterialEditingLibrary.connect_material_property(e,'',u.MaterialProperty.MP_BASE_COLOR)
        for prop,val,y in [(u.MaterialProperty.MP_ROUGHNESS,rough,130),(u.MaterialProperty.MP_METALLIC,metal,230)]:
            c = u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant,-350,y)
            c.set_editor_property('r',val)
            u.MaterialEditingLibrary.connect_material_property(c,'',prop)
        if glow:
            c = u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant3Vector,-350,330)
            c.set_editor_property('constant',u.LinearColor(*(v*glow for v in color),1))
            u.MaterialEditingLibrary.connect_material_property(c,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
        if name == 'Glazing':
            c = u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant,-350,430)
            c.set_editor_property('r',.05)
            u.MaterialEditingLibrary.connect_material_property(c,'',u.MaterialProperty.MP_SPECULAR)
        u.MaterialEditingLibrary.recompile_material(m)
        assert u.EditorAssetLibrary.save_loaded_asset(m)
        materials[name] = m
    cube = u.load_asset('/Engine/BasicShapes/Cube.Cube')
    bounds = {}
    def box(name,loc,size,material,folder='Architecture',blocking=True):
        a = aes.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*loc))
        a.set_actor_label(name)
        a.set_folder_path('Layout02/'+folder)
        c = a.static_mesh_component
        c.set_static_mesh(cube)
        c.set_material(0,materials[material])
        c.set_collision_profile_name('BlockAll' if blocking else 'NoCollision')
        a.set_actor_scale3d(u.Vector(*(v/100 for v in size)))
        if blocking:
            center,extent = a.get_actor_bounds(False)
            bounds[name] = dict(center=[center.x,center.y,center.z],extent=[extent.x,extent.y,extent.z])
        return a
    box('Floor',(0,0,-25),(3040,1240,50),'Floor')
    for y in [-620,620]:
        box('SideWall_'+str(y),(0,y,450),(3040,40,900),'Wall')
    box('EntranceBoundary',(-1520,0,450),(40,1240,900),'Wall')
    box('InnerBoundary',(1520,0,450),(40,1240,900),'Wall')
    box('HighCentralCeiling',(0,0,920),(3040,800,40),'Ceiling','Ceiling')
    for y in [-500,500]:
        box('SideAisleCeiling_'+str(y),(0,y,480),(3000,200,40),'Ceiling','Ceiling')
    for y in [-340,340]:
        box('HeavyLongLintel_'+str(y),(0,y,490),(3000,120,140),'Stone')
        box('UpperClerestoryWall_'+str(y),(0,y,730),(3000,120,340),'Wall')
        for x in [-1050,-630,-210,210,630,1050]:
            box('Pier_%s_%s'%(x,y),(x,y,210),(120,120,420),'Stone','Piers')
            for z in [140,280]:
                box('PierJoint_%s_%s_%s'%(x,y,z),(x,y,z),(120.3,120.3,.7),'BlackStrip','Dressing',False)
    for y in [-110,110]:
        box('ParallelBlackStrip_'+str(y),(0,y,.12),(3000,32,.24),'BlackStrip','Dressing',False)
    # Flush joints provide scale without raised obstacles or a texture pipeline.
    for x in range(-1440,1500,120):
        box('FloorJointX_'+str(x),(x,0,.13),(.4,1200,.26),'BlackStrip','Dressing',False)
    for y in range(-600,601,120):
        box('FloorJointY_'+str(y),(0,y,.13),(3000,.4,.26),'BlackStrip','Dressing',False)
    # Entrance: one tall narrow mullioned field, with entry glazing below.
    box('EntranceUpperGlazing',(-1496,0,580),(6,260,620),'Glazing','Entrance',False)
    box('EntryGlazing',(-1495,0,132),(8,260,264),'Glazing','Entrance',False)
    for y in [-135,-65,0,65,135]:
        box('EntryMullion_'+str(y),(-1488,y,445),(12,5,890),'Metal','Entrance',False)
    for z in [5,265,400,535,670,805,890]:
        box('EntryTransom_'+str(z),(-1488,0,z),(12,280,6 if z!=265 else 20),'Metal','Entrance',False)
    for y in [-18,18]:
        box('EntryHandle_'+str(y),(-1478,y,108),(7,3,42),'Metal','Entrance',False)
    # One opaque human-scale door; no destination is assigned.
    box('InnerDoorFrame',(1492,0,116),(16,122,232),'Metal','InnerEnd',False)
    box('InnerOpaqueDoor',(1482,0,110),(6,104,218),'BlackStrip','InnerEnd',False)
    box('InnerDoorHandle',(1477,-34,110),(5,3,38),'Metal','InnerEnd',False)
    box('InnerHighWindow',(1494,0,725),(8,120,310),'Glazing','InnerEnd',False)
    for y in [-62,0,62]:
        box('InnerWindowMullion_'+str(y),(1487,y,725),(12,4,316),'Metal','InnerEnd',False)
    for z in [570,725,880]:
        box('InnerWindowTransom_'+str(z),(1487,0,z),(12,128,4),'Metal','InnerEnd',False)
    # Looking toward -X, +Y is left: station left of the detector.
    for y in [-170,-40]:
        box('DetectorPost_'+str(y),(-1230,y,114),(55,16,228),'Metal','Security')
    box('DetectorHeader',(-1230,-105,235),(55,146,14),'Metal','Security')
    box('ScreeningStation',(-1230,95,48),(85,220,96),'Metal','Security')
    box('ScreeningCounter',(-1230,95,99),(95,230,6),'BlackStrip','Dressing',False)
    for y in [20,105,185]:
        box('StationMonitor_'+str(y),(-1242,y,118),(12,32,30),'Metal','Dressing',False)
    box('DetectorStatus',(-1199,-105,235),(2,16,3),'Light','Dressing',False)
    # Restrained continuous side-aisle lines, with bounded movable fill lights.
    for y in [-591,591]:
        box('SideLinearLight_'+str(y),(0,y,420),(2940,8,5),'Light','Dressing',False)
    for x in [-1260,-630,0,630,1260]:
        for y in [-495,495,0]:
            light = aes.spawn_actor_from_class(u.PointLight,u.Vector(x,y,390 if y else 720))
            light.set_actor_label('Layout02Fill_%s_%s'%(x,y))
            light.set_folder_path('Layout02/Lighting')
            c = light.point_light_component
            c.set_editor_property('intensity_units',u.LightUnits.LUMENS)
            c.set_editor_property('intensity',6000. if y else 4500.)
            c.set_editor_property('attenuation_radius',1050.)
            c.set_editor_property('source_radius',50.)
            c.set_editor_property('use_temperature',True)
            c.set_editor_property('temperature',6200.)
            c.set_mobility(u.ComponentMobility.MOVABLE)
    pp = aes.spawn_actor_from_class(u.PostProcessVolume,u.Vector())
    pp.set_actor_label('Layout02StableExposure')
    pp.set_folder_path('Layout02/Lighting')
    pp.set_editor_property('unbound',True)
    settings = pp.get_editor_property('settings')
    for name,value in [('override_auto_exposure_method',True),('auto_exposure_method',u.AutoExposureMethod.AEM_MANUAL),
                       ('override_auto_exposure_bias',True),('auto_exposure_bias',-4.3),
                       ('override_auto_exposure_apply_physical_camera_exposure',True),('auto_exposure_apply_physical_camera_exposure',False),
                       ('override_bloom_intensity',True),('bloom_intensity',.12),
                       ('override_motion_blur_amount',True),('motion_blur_amount',0.)]:
        settings.set_editor_property(name,value)
    pp.set_editor_property('settings',settings)
    start = aes.spawn_actor_from_class(u.PlayerStart,u.Vector(-1400,-105,100),u.Rotator(0,0,0))
    start.set_actor_label('Layout02EntranceStart')
    start.set_folder_path('Layout02/Gameplay')
    editor.get_editor_world().get_world_settings().set_editor_property('default_game_mode',u.load_class(None,'/Script/MeridianSquad.OpeningLobbyGameMode'))
    editor.set_level_viewport_camera_info(u.Vector(-1120,0,172),u.Rotator(0,0,0))
    assert les.save_current_level()
    result = dict(map=MAP,estimate_not_image_measurement=True,dimensions_cm=dict(room=[3000,1200,900],pier=[120,120,420],bay_pitch=420,central_clear_width=560,side_aisle_clear_width=200,side_aisle_height=460,lintel_height=140,door=[104,218],detector_clear_width=114,detector_clear_height=228),actor_count=len(aes.get_all_level_actors()),blocking_bounds=bounds)
    out = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_saved_dir()))/'OpeningLobby/Layout02'
    out.mkdir(parents=True,exist_ok=True)
    (out/'construction.json').write_text(json.dumps(result,indent=2))
    return {k:v for k,v in result.items() if k!='blocking_bounds'}

def refine_appearance():
    """Apply the reviewed prototype palette to existing Layout02 assets only."""
    require_project(u.Paths.get_project_file_path())
    editor = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert not editor.get_game_world()
    assert editor.get_editor_world().get_path_name().split('.')[0] == MAP
    for name,color,roughness in [('Floor',(.13,.19,.165),.18),('Stone',(.04,.065,.053),.44),('Wall',(.06,.085,.07),.48)]:
        m = u.load_asset(MAT+'/M_Layout02_'+name)
        # Expressions created by this script have fixed, dedicated object classes.
        for expression in u.MaterialEditingLibrary.get_material_expressions(m):
            if isinstance(expression,u.MaterialExpressionConstant3Vector):
                expression.set_editor_property('constant',u.LinearColor(*color,1))
            elif isinstance(expression,u.MaterialExpressionConstant) and u.MaterialEditingLibrary.get_material_expression_node_position(expression)[1] == 130:
                expression.set_editor_property('r',roughness)
        u.MaterialEditingLibrary.recompile_material(m)
        assert u.EditorAssetLibrary.save_loaded_asset(m)
    glazing = u.load_asset(MAT+'/M_Layout02_Glazing')
    specular = [e for e in u.MaterialEditingLibrary.get_material_expressions(glazing) if isinstance(e,u.MaterialExpressionConstant) and u.MaterialEditingLibrary.get_material_expression_node_position(e)[1] == 430]
    c = specular[0] if specular else u.MaterialEditingLibrary.create_material_expression(glazing,u.MaterialExpressionConstant,-350,430)
    c.set_editor_property('r',.05)
    u.MaterialEditingLibrary.connect_material_property(c,'',u.MaterialProperty.MP_SPECULAR)
    u.MaterialEditingLibrary.recompile_material(glazing)
    assert u.EditorAssetLibrary.save_loaded_asset(glazing)
    for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
        if a.get_actor_label().startswith('Layout02Fill_'):
            a.point_light_component.set_editor_property('intensity',6000. if abs(a.get_actor_location().y)>1 else 4500.)
        if a.get_actor_label() == 'Layout02StableExposure':
            settings = a.get_editor_property('settings')
            settings.set_editor_property('auto_exposure_bias',-4.3)
            a.set_editor_property('settings',settings)
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    return 'Layout02 palette and lighting refined; geometry unchanged'
