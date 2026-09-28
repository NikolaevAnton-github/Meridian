import json
from pathlib import Path
import unreal as u
OUT=Path('D:/devgames/MeridianSquad/Saved/DemoTiledColumn01/Correction02')
DEST='/Game/Experiments/DemoTiledColumn01/Correction02/'
editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert editor.get_editor_world().get_path_name().split('.')[0]=='/Game/Maps/L_OpeningLobby_PainterStone01'
assert not editor.get_game_world()
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
old=[a for a in actors.get_all_level_actors() if a.get_actor_label()=='EXP_DemoTiledColumn01']
assert len(old)==1
old=old[0]
assert old.get_editor_property('DataAsset').get_path_name()=='/Game/Experiments/DemoTiledColumn01/DA_DemoTiledColumn01.DA_DemoTiledColumn01'
edge=u.load_asset(DEST+'M_StoneEdge02') or u.EditorAssetLibrary.duplicate_asset('/Game/ReinforcedColumn01/M_RC01_StoneEdge',DEST+'M_StoneEdge02')
assert edge
u.MaterialEditingLibrary.set_material_usage(edge,u.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES)
u.MaterialEditingLibrary.recompile_material(edge)
assert u.EditorAssetLibrary.save_loaded_asset(edge)
for i in range(72):
    mesh=u.load_asset(DEST+f'SM_Tile02_{i:03}')
    assert mesh
    for slot in (1,2,3): mesh.set_material(slot,edge)
    assert u.EditorAssetLibrary.save_loaded_asset(mesh)
data=u.load_asset(DEST+'DA_DemoTiledColumn02')
assert data.get_editor_property('GeometryCollection').get_path_name()=='/Game/NextGenDestruction/GeometryCollections/Concrete/GC_ConcretePillar_Square_5m.GC_ConcretePillar_Square_5m'
location=old.get_actor_location(); rotation=old.get_actor_rotation()
assert actors.destroy_actor(old)
actor=u.NGDTools.spawn_prop(editor.get_editor_world(),data,location,rotation,'EXP_DemoTiledColumn01_Correction02')
assert actor
actor.set_actor_scale3d(u.Vector(2.364,2.364,3.6))
actor.set_folder_path('Experiments/DemoTiledColumn01')
actor.tags=list(actor.tags)+['DemoTiledColumn01_Correction02']
actor.set_actor_label('EXP_DemoTiledColumn01')
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
result=json.loads((OUT/'created.json').read_text(encoding='utf-8'))
result.update(actor=actor.get_path_name(),label=actor.get_actor_label(),data_asset=data.get_path_name(),
    size_cm=[240,240,1800],runtime_tested=False)
(OUT/'placed.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
