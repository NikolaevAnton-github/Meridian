"""Refine only the large Correction06 pieces and rebuild facing support."""
import json
from pathlib import Path
import unreal as u

OUT = Path('D:/devgames/MeridianSquad/Saved/DemoColumnExperiment07')
DEST = '/Game/Experiments/DemoTiledColumn01/Correction07/'
editor = u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert editor.get_editor_world().get_path_name().split('.')[0] == '/Game/Maps/L_OpeningLobby_PainterStone01'
assert not editor.get_game_world()
assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not u.EditorLoadingAndSavingUtils.get_dirty_content_packages()
assert not u.EditorAssetLibrary.does_asset_exist(DEST + 'GC_DemoColumn07')
result = json.loads(u.NGDColumnAuthoring.build_demo_column_refinement())
assert 'error' not in result, result
asset = u.load_asset(DEST + 'GC_DemoColumn07')
inspection = json.loads(u.NGDColumnAuthoring.inspect_collection(asset))
(OUT / 'collection.json').write_text(json.dumps(inspection, indent=2), encoding='utf-8')
assert not inspection['leaves_without_convex']
assert inspection['anchored_count'] == result['protected_core_bones']
assert result['tiles'] == 1560 and result['original_leaves'] == 730
assert 730 < result['geometries'] < 950
assert result['protected_core_bones'] == 167
assert result['support_links'] > result['tiles']
assert u.EditorAssetLibrary.save_directory(DEST, only_if_is_dirty=True, recursive=True)
data = u.EditorAssetLibrary.duplicate_asset('/Game/Experiments/DemoTiledColumn01/Correction06/DA_DemoTiledColumn06', DEST + 'DA_DemoTiledColumn07')
assert data
data.set_editor_property('GeometryCollection', asset)
assert u.EditorAssetLibrary.save_loaded_asset(data)
(OUT / 'authored.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result))
