"""Create derived resources without mutating the accepted central specimen."""
import json
from pathlib import Path
import unreal as u

ROOT=Path('D:/devgames/MeridianSquad')
OUT=ROOT/'Saved/LobbyColumns01'
DEST='/Game/OpeningLobby/LobbyColumns01/'
editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert not editor.get_game_world()
assert editor.get_editor_world().get_path_name().split('.')[0]=='/Game/Maps/L_OpeningLobby_PainterStone01'
assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
meshes=json.loads(u.NGDColumnAuthoring.build_lobby_column_meshes(str(OUT/'source.json')))
(OUT/'meshes-authored.json').write_text(json.dumps(meshes,indent=2))
assert 'error' not in meshes,meshes
structure=json.loads(u.NGDColumnAuthoring.build_lobby_column_structure())
(OUT/'structure-authored.json').write_text(json.dumps(structure,indent=2))
assert 'error' not in structure,structure
gc=u.load_asset(DEST+'GC_LobbyColumn01')
inspection=json.loads(u.NGDColumnAuthoring.inspect_collection(gc))
(OUT/'collection.json').write_text(json.dumps(inspection,indent=2))
assert not inspection['leaves_without_convex']
assert structure['unchanged_lower_leaves']==486 and structure['cut_sources']==42
assert structure['tiles']==768
data=u.EditorAssetLibrary.duplicate_asset('/Game/Experiments/DemoTiledColumn01/Correction08/DA_DemoTiledColumn08',DEST+'DA_LobbyColumn01')
assert data
data.set_editor_property('GeometryCollection',gc)
assert u.EditorAssetLibrary.save_directory(DEST,only_if_is_dirty=True,recursive=True)
print(json.dumps(dict(meshes=meshes,structure=structure,convex_complete=True)))
