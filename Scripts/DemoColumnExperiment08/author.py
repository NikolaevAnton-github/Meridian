"""Further refine large Correction07 pieces and author matching ceramic shards."""
import json
from pathlib import Path
import unreal as u

OUT = Path('D:/devgames/MeridianSquad/Saved/DemoColumnExperiment08')
DEST = '/Game/Experiments/DemoTiledColumn01/Correction08/'
editor = u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert editor.get_editor_world().get_path_name().split('.')[0] == '/Game/Maps/L_OpeningLobby_PainterStone01'
assert not editor.get_game_world()
assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not u.EditorLoadingAndSavingUtils.get_dirty_content_packages()
assert not u.EditorAssetLibrary.does_asset_exist(DEST + 'GC_DemoColumn08')
result = json.loads(u.NGDColumnAuthoring.build_demo_column_refinement08())
assert 'error' not in result, result
shards = json.loads(u.NGDColumnAuthoring.build_demo_column_tile_fractures08())
assert 'error' not in shards, shards
(OUT / 'shards-authored.json').write_text(json.dumps(shards, indent=2), encoding='utf-8')
asset = u.load_asset(DEST + 'GC_DemoColumn08')
inspection = json.loads(u.NGDColumnAuthoring.inspect_collection(asset))
(OUT / 'collection.json').write_text(json.dumps(inspection, indent=2), encoding='utf-8')
assert not inspection['leaves_without_convex']
assert inspection['anchored_count'] == result['protected_core_bones']
assert result['tiles'] == 1560 and result['original_leaves'] == 874
assert 874 < result['geometries'] < 1200
assert result['protected_core_bones'] == 167
assert result['support_links'] > result['tiles']
assert u.EditorAssetLibrary.save_directory(DEST, only_if_is_dirty=True, recursive=True)
data = u.EditorAssetLibrary.duplicate_asset('/Game/Experiments/DemoTiledColumn01/Correction07/DA_DemoTiledColumn07', DEST + 'DA_DemoTiledColumn08')
assert data
data.set_editor_property('GeometryCollection', asset)
assert u.EditorAssetLibrary.save_loaded_asset(data)
(OUT / 'authored.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result))
