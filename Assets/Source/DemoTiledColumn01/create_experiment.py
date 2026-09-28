import json
from pathlib import Path
import unreal as u

ROOT=Path('D:/devgames/MeridianSquad')
OUT=ROOT/'Saved/DemoTiledColumn01'
DEST='/Game/Experiments/DemoTiledColumn01/'
MAP='/Game/Maps/L_OpeningLobby_PainterStone01'
editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert editor.get_editor_world().get_path_name().split('.')[0]==MAP
assert not editor.get_game_world()
assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not u.EditorLoadingAndSavingUtils.get_dirty_content_packages()
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assert not any(a.get_actor_label()=='EXP_DemoTiledColumn01' for a in actors.get_all_level_actors())

def duplicate(source,name):
    assert not u.EditorAssetLibrary.does_asset_exist(DEST+name), name
    asset=u.EditorAssetLibrary.duplicate_asset(source,DEST+name)
    assert asset,name
    return asset

stone=duplicate('/Game/ReinforcedColumn01/MI_RC01_Cladding','MI_DemoTiledColumn01')
u.MaterialEditingLibrary.set_material_instance_vector_parameter_value(stone,'OriginCm',u.LinearColor(-120,-120,0,1))
u.MaterialEditingLibrary.set_material_instance_vector_parameter_value(stone,'ExtentCm',u.LinearColor(240,240,1800,1))
u.EditorAssetLibrary.save_loaded_asset(stone)
collection=duplicate('/Game/NextGenDestruction/GeometryCollections/Concrete/GC_ConcretePillar_Square_5m','GC_DemoTiledColumn01')
collection.set_editor_property('materials',list(collection.get_editor_property('materials'))+[stone,u.load_asset('/Game/ReinforcedColumn01/M_RC01_StoneEdge')])
result=json.loads(u.NGDColumnAuthoring.add_demo_column_tiles(collection,str(OUT/'tiles.json')))
assert 'error' not in result,result
(OUT/'created.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
assert u.EditorAssetLibrary.save_loaded_asset(collection)

data=duplicate('/Game/NextGenDestruction/Blueprints/DataAssets/Destructible/DA_Pillar_Large_Concrete_Square','DA_DemoTiledColumn01')
data.set_editor_property('GeometryCollection',collection)
data.set_editor_property('DamageRadius',.65)
assert u.EditorAssetLibrary.save_loaded_asset(data)
actor=u.NGDTools.spawn_prop(editor.get_editor_world(),data,u.Vector(0,0,0),u.Rotator(),'EXP_DemoTiledColumn01')
assert actor
actor.set_actor_scale3d(u.Vector(240/104,240/104,3.6))
actor.set_folder_path('Experiments/DemoTiledColumn01')
actor.tags=list(actor.tags)+['DemoTiledColumn01']
gc=actor.get_component_by_class(u.GeometryCollectionComponent)
gc.set_editor_property('max_cluster_level',10)
gc.set_editor_property('max_simulated_level',10)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
actors.set_selected_level_actors([actor])
u.get_editor_subsystem(u.UnrealEditorSubsystem).set_level_viewport_camera_info(u.Vector(700,-850,380),u.Rotator(10,130,0))
result.update(actor=actor.get_path_name(),location_cm=[0,0,0],size_cm=[240,240,1800],data_asset=data.get_path_name())
(OUT/'placed.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
