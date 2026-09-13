"""Create the original Stage 1 blockout through the focused Epic MCP tool."""
import json
from pathlib import Path
import unreal as u

MAP = '/Game/Maps/L_OpeningLobby'
MAT = '/Game/OpeningLobby/Materials/'

def build():
    les = u.get_editor_subsystem(u.LevelEditorSubsystem)
    aes = u.get_editor_subsystem(u.EditorActorSubsystem)
    assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    assert not u.EditorAssetLibrary.does_asset_exist(MAP), 'Do not overwrite an existing lobby; review first.'
    assert les.new_level(MAP)
    world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
    materials = {}
    for name, color, rough, metal, glow in [
        ('Floor', (.15,.17,.16), .3, 0, 0),
        ('FloorBorder', (.035,.047,.044), .33, 0, 0),
        ('Stone', (.23,.30,.265), .58, 0, 0),
        ('Wall', (.36,.40,.36), .75, 0, 0),
        ('Ceiling', (.14,.17,.155), .8, 0, 0),
        ('Metal', (.20,.23,.22), .28, .85, 0),
        ('DarkGlass', (.025,.075,.08), .15, .35, 0),
        ('Light', (.65,.8,.72), .4, 0, 5),
    ]:
        path = MAT + 'M_Lobby_' + name
        m = u.AssetToolsHelpers.get_asset_tools().create_asset('M_Lobby_' + name, MAT.rstrip('/'), u.Material, u.MaterialFactoryNew())
        assert m, path
        e = u.MaterialEditingLibrary.create_material_expression(m, u.MaterialExpressionConstant3Vector, -350, 0)
        e.set_editor_property('constant', u.LinearColor(*color,1))
        u.MaterialEditingLibrary.connect_material_property(e, '', u.MaterialProperty.MP_BASE_COLOR)
        for prop, val, y in [(u.MaterialProperty.MP_ROUGHNESS,rough,130),(u.MaterialProperty.MP_METALLIC,metal,230)]:
            c = u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant,-350,y)
            c.set_editor_property('r',val)
            u.MaterialEditingLibrary.connect_material_property(c,'',prop)
        if glow:
            c = u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant3Vector,-350,330)
            c.set_editor_property('constant',u.LinearColor(*(v*glow for v in color),1))
            u.MaterialEditingLibrary.connect_material_property(c,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
        u.MaterialEditingLibrary.recompile_material(m)
        assert u.EditorAssetLibrary.save_loaded_asset(m)
        materials[name] = m

    cube = u.load_asset('/Engine/BasicShapes/Cube.Cube')
    counts = {}
    def box(name, loc, size, material, folder='Architecture'):
        actor = aes.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*loc))
        actor.set_actor_label(name)
        actor.set_folder_path('OpeningLobby/' + folder)
        c = actor.static_mesh_component
        c.set_static_mesh(cube)
        c.set_material(0,materials[material])
        c.set_collision_profile_name('BlockAll')
        actor.set_actor_scale3d(u.Vector(*(v/100 for v in size)))
        counts[folder] = counts.get(folder,0)+1
        return actor

    # Interior clear dimensions: x +/-1800, y +/-1100, z 0..800 cm.
    box('Floor_Structure',(0,0,-25),(3640,2240,50),'Floor')
    box('Wall_West',(0,-1120,400),(3640,40,800),'Wall')
    box('Wall_East',(0,1120,400),(3640,40,800),'Wall')
    box('Entrance_Boundary',(-1820,0,400),(40,2240,800),'Wall')
    box('Elevator_Boundary',(1820,0,400),(40,2240,800),'Wall')
    box('Ceiling_Slab',(0,0,820),(3640,2240,40),'Ceiling','Ceiling')
    # Narrow raised inlays remain well below the capsule step threshold.
    for y in [-650,-360,360,650]:
        box('Floor_Long_Inlay_'+str(y),(0,y,.3),(3600,8,.6),'FloorBorder','FloorPattern')
    for x in [-1500,-1150,-450,250,950,1500]:
        box('Floor_Cross_Inlay_'+str(x),(x,0,.3),(8,2200,.6),'FloorBorder','FloorPattern')
    for x in [-1100,-400,300,1000]:
        for y in [-500,500]:
            prefix = 'Column_%s_%s' % (x,y)
            box(prefix+'_Base',(x,y,15),(150,150,30),'FloorBorder','Columns')
            box(prefix+'_Shaft',(x,y,395),(100,100,730),'Stone','Columns')
            box(prefix+'_Capital',(x,y,775),(170,170,50),'Stone','Columns')
        box('Ceiling_Bay_'+str(x),(x,0,765),(90,2200,70),'Stone','Ceiling')
    for y in [-500,500]:
        box('Ceiling_Long_'+str(y),(0,y,765),(3600,120,70),'Stone','Ceiling')
    for y in [-1090,1090]:
        box('Wall_Plinth_'+str(y),(0,y,35),(3600,20,70),'FloorBorder')
        box('Wall_Cornice_'+str(y),(0,y,620),(3600,30,45),'Stone')
        for x in [-1450,-750,-50,650,1350]:
            box('Wall_Panel_%s_%s'%(x,y),(x,y,335),(600,12,470),'Stone')
    # Entrance portals are a visible closed boundary, not a story explanation.
    for y in [-260,0,260]:
        box('Entrance_Glass_'+str(y),(-1792,y,230),(12,235,440),'DarkGlass','Entrance')
        box('Entrance_Mullion_'+str(y),(-1775,y-125,235),(28,14,470),'Metal','Entrance')
    box('Entrance_Header',(-1775,0,470),(35,810,35),'Metal','Entrance')
    for y in [-325,325]:
        box('Security_Pedestal_'+str(y),(-1370,y,55),(180,95,110),'Metal','Security')
        box('Security_Top_'+str(y),(-1370,y,115),(195,110,10),'FloorBorder','Security')
    box('Reception_Desk',(-1450,850,60),(260,160,120),'Stone','Security')
    box('Reception_Counter',(-1450,850,125),(280,175,10),'FloorBorder','Security')
    for y in [-430,0,430]:
        box('Elevator_Frame_'+str(y),(1770,y,190),(60,310,380),'FloorBorder','Elevators')
        box('Elevator_Door_'+str(y),(1735,y,172),(16,250,340),'Metal','Elevators')
        box('Elevator_Seam_'+str(y),(1725,y,170),(4,4,338),'FloorBorder','Elevators')
        box('Elevator_Lintel_'+str(y),(1720,y,370),(25,320,35),'Stone','Elevators')
        box('Elevator_Indicator_'+str(y),(1703,y,405),(6,50,10),'Light','Elevators')
    # A low, walkable plinth supports a real step-off gravity check in the side aisle.
    box('Side_Inspection_Step',(1050,-870,12),(240,180,24),'Stone','Architecture')
    for x in [-1400,-750,0,750,1400]:
        for y in [-830,0,830]:
            box('Ceiling_Luminaire_%s_%s'%(x,y),(x,y,789),(180,65,12),'Light','Ceiling')
            light = aes.spawn_actor_from_class(u.PointLight,u.Vector(x,y,660))
            light.set_actor_label('Lobby_Light_%s_%s'%(x,y))
            light.set_folder_path('OpeningLobby/Lighting')
            c = light.point_light_component
            c.set_editor_property('intensity_units',u.LightUnits.LUMENS)
            c.set_editor_property('intensity',14000.)
            c.set_editor_property('attenuation_radius',1350.)
            c.set_editor_property('source_radius',35.)
            c.set_editor_property('use_temperature',True)
            c.set_editor_property('temperature',4700.)
            c.set_mobility(u.ComponentMobility.MOVABLE)
    pp = aes.spawn_actor_from_class(u.PostProcessVolume,u.Vector())
    pp.set_actor_label('Lobby_StableExposure')
    pp.set_folder_path('OpeningLobby/Lighting')
    pp.set_editor_property('unbound',True)
    settings = pp.get_editor_property('settings')
    for name, value in [('override_auto_exposure_method',True),('auto_exposure_method',u.AutoExposureMethod.AEM_MANUAL),
                        ('override_auto_exposure_bias',True),('auto_exposure_bias',-4.0),
                        ('override_auto_exposure_apply_physical_camera_exposure',True),('auto_exposure_apply_physical_camera_exposure',False),
                        ('override_bloom_intensity',True),('bloom_intensity',.15),
                        ('override_motion_blur_amount',True),('motion_blur_amount',0.)]:
        settings.set_editor_property(name,value)
    pp.set_editor_property('settings',settings)
    start = aes.spawn_actor_from_class(u.PlayerStart,u.Vector(-1630,0,100),u.Rotator(0,0,0))
    start.set_actor_label('Lobby_Entrance_PlayerStart')
    start.set_folder_path('OpeningLobby/Gameplay')
    world.get_world_settings().set_editor_property('default_game_mode',u.load_class(None,'/Script/MeridianSquad.OpeningLobbyGameMode'))
    u.get_editor_subsystem(u.UnrealEditorSubsystem).set_level_viewport_camera_info(u.Vector(-1600,0,172),u.Rotator(0,0,0))
    assert les.save_current_level()
    result = dict(map=MAP, dimensions_cm=[3600,2200,800], actor_count=len(aes.get_all_level_actors()), geometry_groups=counts, material_families=list(materials))
    out = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_saved_dir())) / 'OpeningLobby/Stage1'
    (out/'construction.json').write_text(json.dumps(result,indent=2))
    return result
