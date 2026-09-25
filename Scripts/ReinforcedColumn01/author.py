"""MSQ-154 derived assets and guarded integration of one existing lobby column."""
import importlib.util
import json
from pathlib import Path
import unreal as u

ROOT=Path('D:/devgames/MeridianSquad')
OUT=ROOT/'Saved/ReinforcedColumn01/Candidate01'
DEST='/Game/ReinforcedColumn01/'
LOBBY='/Game/Maps/L_OpeningLobby_PainterStone01'

def write(name,data):
    path=OUT/name
    assert not path.exists(), str(path)
    path.write_text(json.dumps(data,indent=2),encoding='utf-8')

def duplicate(src,name):
    return u.load_asset(DEST+name) or u.EditorAssetLibrary.duplicate_asset(src,DEST+name)

def materials():
    master=duplicate('/Game/OpeningLobby/MaterialsComplete01/SlabLayout01/M_Slabs01','M_RC01_Cladding')
    u.MaterialEditingLibrary.set_material_usage(master,u.MaterialUsage.MATUSAGE_GEOMETRY_COLLECTIONS)
    u.MaterialEditingLibrary.recompile_material(master)
    inst=duplicate('/Game/OpeningLobby/MaterialsComplete01/SlabLayout01/MI_Slabs_035','MI_RC01_Cladding')
    u.MaterialEditingLibrary.set_material_instance_parent(inst,master)
    edge=u.load_asset(DEST+'M_RC01_StoneEdge')
    if not edge:
        edge=u.AssetToolsHelpers.get_asset_tools().create_asset('M_RC01_StoneEdge',DEST.rstrip('/'),u.Material,u.MaterialFactoryNew())
        col=u.MaterialEditingLibrary.create_material_expression(edge,u.MaterialExpressionConstant3Vector)
        col.set_editor_property('constant',u.LinearColor(.065,.11,.085,1))
        u.MaterialEditingLibrary.connect_material_property(col,'',u.MaterialProperty.MP_BASE_COLOR)
        rough=u.MaterialEditingLibrary.create_material_expression(edge,u.MaterialExpressionConstant)
        rough.set_editor_property('r',.86)
        u.MaterialEditingLibrary.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
        u.MaterialEditingLibrary.set_material_usage(edge,u.MaterialUsage.MATUSAGE_GEOMETRY_COLLECTIONS)
        u.MaterialEditingLibrary.recompile_material(edge)
    for obj in [master,inst,edge]: assert u.EditorAssetLibrary.save_loaded_asset(obj)

def build(evidence='asset-build.json'):
    assert not (OUT/evidence).exists(), 'Choose a new immutable evidence filename.'
    ed=u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert not ed.get_game_world()
    assert ed.get_editor_world(), 'Wait for the editor world to finish loading.'
    assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    assert not u.EditorLoadingAndSavingUtils.get_dirty_content_packages()
    level=ed.get_editor_world().get_path_name().split('.')[0]
    assert level==LOBBY
    # A GC transform-count change cannot reuse the live old render proxy.
    # Use an unsaved empty world during authoring, then reopen the retained map.
    u.EditorLoadingAndSavingUtils.new_blank_map(False)
    materials()
    result=json.loads(u.NGDColumnAuthoring.build_column(str(ROOT/'Assets/Source/ReinforcedColumn01/column.json')))
    assert 'error' not in result, result
    write(evidence,result)
    vendor=u.load_asset('/Game/NextGenDestruction/GeometryCollections/Concrete/GC_ConcretePillar_Square_5m')
    if not (OUT/'vendor-collection-layout.json').exists():
        write('vendor-collection-layout.json',json.loads(u.NGDColumnAuthoring.inspect_collection(vendor)))
    data=duplicate('/Game/NextGenDestruction/Blueprints/DataAssets/Destructible/DA_Pillar_Large_Concrete_Square','DA_RC01_Column')
    for name,value in [('GeometryCollection',u.load_asset(DEST+'GC_RC01_BondedConcrete')),
                       ('OptionalStaticMesh',u.load_asset(DEST+'SM_RC01_Rebar')),
                       ('HasKinematicPieces',True),('DamageRadius',.22)]:
        data.set_editor_property(name,value)
    assert u.EditorAssetLibrary.save_directory(DEST,only_if_is_dirty=True,recursive=True)
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(level)
    print(json.dumps({k:v for k,v in result.items() if k!='hierarchy'}))

def integrate():
    ed=u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert not ed.get_game_world()
    assert ed.get_editor_world().get_path_name()==LOBBY+'.L_OpeningLobby_PainterStone01'
    actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
    target=next(a for a in actors if a.get_name()=='StaticMeshActor_35')
    assert target.get_actor_label()=='FB01_newNcolumnNN12p6NN2p4'
    assert target.static_mesh_component.static_mesh.get_path_name() in ['/Game/OpeningLobby/FunctionalBuild01/Meshes/SM_FB01_TallColumn.SM_FB01_TallColumn', DEST+'SM_RC01_SupportedColumn.SM_RC01_SupportedColumn']
    assert not any(a.get_actor_label()=='RC01_ReinforcedColumn' for a in actors)
    target.modify()
    target.static_mesh_component.set_static_mesh(u.load_asset(DEST+'SM_RC01_SupportedColumn'))
    prop=u.NGDTools.spawn_prop(ed.get_editor_world(),u.load_asset(DEST+'DA_RC01_Column'),u.Vector(-1260,-240,0),u.Rotator(), 'RC01_ReinforcedColumn')
    assert prop and prop.get_component_by_class(u.NGDPropComponent)
    prop.set_folder_path('ReinforcedColumn01')
    prop.tags=list(prop.tags)+['ReinforcedColumn01']
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    write('integration.json',dict(actor=target.get_path_name(),transform=str(target.get_actor_transform()),bounds=str(target.get_actor_bounds(False)),prop=prop.get_path_name(),min_damage_radius=prop.get_editor_property('MinDamageRadius'),kinematic=prop.get_editor_property('HasKinematicPieces'),material_overrides=[str(m) for m in target.static_mesh_component.get_editor_property('override_materials')]))
    print('Integrated one column and saved the lobby.')
