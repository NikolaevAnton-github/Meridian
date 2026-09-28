import json
from pathlib import Path
import unreal as u

OUT=Path('D:/devgames/MeridianSquad/Saved/DemoTiledColumn01/Correction03')
DEST='/Game/Experiments/DemoTiledColumn01/Correction03/'
editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert editor.get_editor_world().get_path_name().split('.')[0]=='/Game/Maps/L_OpeningLobby_PainterStone01'
assert not editor.get_game_world()
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
old=[a for a in actors.get_all_level_actors() if a.get_actor_label()=='EXP_DemoTiledColumn01']
assert len(old)==1
old=old[0]
assert old.get_editor_property('DataAsset').get_path_name().startswith('/Game/Experiments/DemoTiledColumn01/Correction02/')
result=json.loads(u.NGDColumnAuthoring.bake_demo_column_scale())
assert 'error' not in result,result
(OUT/'baked.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
assert u.EditorAssetLibrary.save_directory(DEST,only_if_is_dirty=True,recursive=True)
data=u.EditorAssetLibrary.duplicate_asset('/Game/Experiments/DemoTiledColumn01/Correction02/DA_DemoTiledColumn02',DEST+'DA_DemoTiledColumn03')
assert data
data.set_editor_property('GeometryCollection',u.load_asset(DEST+'GC_DemoColumn03'))
assert u.EditorAssetLibrary.save_loaded_asset(data)
location=old.get_actor_location(); rotation=old.get_actor_rotation()
assert actors.destroy_actor(old)
actor=u.NGDTools.spawn_prop(editor.get_editor_world(),data,location,rotation,'EXP_DemoTiledColumn01_Correction03')
assert actor
actor.set_actor_scale3d(u.Vector(1,1,1))
for c in actor.get_components_by_class(u.StaticMeshComponent):
    if c.static_mesh and c.static_mesh.get_name()=='SM_ConcretePillar_Square_5m_REBAR':
        c.set_relative_scale3d(u.Vector(2.364,2.364,3.6))
actor.set_folder_path('Experiments/DemoTiledColumn01')
actor.tags=list(actor.tags)+['DemoTiledColumn01_Correction03']
actor.set_actor_label('EXP_DemoTiledColumn01')
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
result.update(actor=actor.get_path_name(),data_asset=data.get_path_name(),bounds=str(actor.get_actor_bounds(False)),scale=str(actor.get_actor_scale3d()))
(OUT/'placed.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
