"""Author only the isolated candidate; preserve the current placed checkpoint."""
import json
from pathlib import Path
import unreal as u

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/DemoColumnExperiment05'
DEST = '/Game/Experiments/DemoTiledColumn01/Correction05/'
editor = u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert editor.get_editor_world().get_path_name().split('.')[0] == '/Game/Maps/L_OpeningLobby_PainterStone01'
assert not editor.get_game_world()
assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not u.EditorLoadingAndSavingUtils.get_dirty_content_packages()
assert not u.EditorAssetLibrary.does_asset_exist(DEST + 'GC_DemoColumn05')
result = json.loads(u.NGDColumnAuthoring.build_demo_column_surface())
assert 'error' not in result, result
asset = u.load_asset(DEST + 'GC_DemoColumn05')
inspection = json.loads(u.NGDColumnAuthoring.inspect_collection(asset))
(OUT / 'collection-after.json').write_text(json.dumps(inspection, indent=2), encoding='utf-8')
assert not inspection['leaves_without_convex']
assert result['tiles'] == 1560 and result['surface_bones'] > 600
assert result['geometries'] < 6000, result
assert u.EditorAssetLibrary.save_directory(DEST, only_if_is_dirty=True, recursive=True)
data = u.EditorAssetLibrary.duplicate_asset(
    '/Game/Experiments/DemoTiledColumn01/Correction04/DA_DemoTiledColumn04', DEST + 'DA_DemoTiledColumn05')
assert data
data.set_editor_property('GeometryCollection', asset)
assert u.EditorAssetLibrary.save_loaded_asset(data)
(OUT / 'authored.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result))
