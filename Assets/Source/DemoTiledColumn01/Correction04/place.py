import json
from pathlib import Path
import unreal as u

OUT=Path('D:/devgames/MeridianSquad/Saved/DemoTiledColumn01/Correction04')
DEST='/Game/Experiments/DemoTiledColumn01/Correction04/'
editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert editor.get_editor_world().get_path_name().split('.')[0]=='/Game/Maps/L_OpeningLobby_PainterStone01'
assert not editor.get_game_world()
assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
old=[a for a in actors.get_all_level_actors() if a.get_actor_label()=='EXP_DemoTiledColumn01']
assert len(old)==1
old=old[0]
assert old.get_editor_property('DataAsset').get_path_name().startswith('/Game/Experiments/DemoTiledColumn01/Correction03/')
result=json.loads(u.NGDColumnAuthoring.build_demo_column_cladding(str(OUT/'cladding.json')))
assert 'error' not in result,result
(OUT/'created.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
assert u.EditorAssetLibrary.save_directory(DEST,only_if_is_dirty=True,recursive=True)
data=u.EditorAssetLibrary.duplicate_asset('/Game/Experiments/DemoTiledColumn01/Correction03/DA_DemoTiledColumn03',DEST+'DA_DemoTiledColumn04')
assert data
assert u.EditorAssetLibrary.save_loaded_asset(data)
actor=u.NGDTools.spawn_prop(editor.get_editor_world(),data,old.get_actor_location(),old.get_actor_rotation(),'EXP_DemoTiledColumn01_Correction04')
assert actor and actor.actor_has_tag('DemoColumnCladding04')
actor.set_folder_path('Experiments/DemoTiledColumn01')
assert actors.destroy_actor(old)
actor.set_actor_label('EXP_DemoTiledColumn01')
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
result.update(actor=actor.get_path_name(),data_asset=data.get_path_name(),bounds=str(actor.get_actor_bounds(False)),scale=str(actor.get_actor_scale3d()))
(OUT/'placed.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
