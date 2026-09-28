"""Replace only the restored center demo actor with the verified coarse variant."""
import json
import shutil
from pathlib import Path
import unreal as u

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/DemoColumnExperiment06'
editor = u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert not editor.get_game_world()
assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not u.EditorLoadingAndSavingUtils.get_dirty_content_packages()
assert (OUT / 'authored.json').exists()
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
old = [a for a in actors.get_all_level_actors() if a.get_actor_label() == 'EXP_DemoTiledColumn01']
assert len(old) == 1
old = old[0]
assert '/Correction04/' in old.get_editor_property('DataAsset').get_path_name()
backup = OUT / 'LobbyBefore06.umap'
assert not backup.exists()
shutil.copy2(ROOT / 'Content/Maps/L_OpeningLobby_PainterStone01.umap', backup)
data = u.load_asset('/Game/Experiments/DemoTiledColumn01/Correction06/DA_DemoTiledColumn06')
a = u.NGDTools.spawn_prop(editor.get_editor_world(), data, old.get_actor_location(), old.get_actor_rotation(), 'EXP_DemoTiledColumn01')
assert a and a.actor_has_tag('DemoColumnCoarse06')
assert actors.destroy_actor(old)
a.set_actor_label('EXP_DemoTiledColumn01')
a.set_folder_path('Experiments/DemoTiledColumn01')
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(OUT / 'placed.json').write_text(json.dumps(dict(actor=a.get_path_name(), data=data.get_path_name()), indent=2), encoding='utf-8')
print(a.get_path_name())
