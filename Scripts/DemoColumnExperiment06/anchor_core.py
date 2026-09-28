"""Apply explicit core anchors to the pre-anchor Correction06 candidate."""
import json
from pathlib import Path
import unreal as u

out = Path('D:/devgames/MeridianSquad/Saved/DemoColumnExperiment06')
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
result = json.loads(u.NGDColumnAuthoring.anchor_demo_column_core())
assert 'error' not in result, result
assert result['anchored_count'] == 167
assert result['geometries'] == 730 and not result['leaves_without_convex']
assert u.EditorAssetLibrary.save_directory('/Game/Experiments/DemoTiledColumn01/Correction06/', only_if_is_dirty=True, recursive=True)
assert not (out / 'collection-before-depth-core.json').exists()
(out / 'collection-before-depth-core.json').write_bytes((out / 'collection.json').read_bytes())
(out / 'collection.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
(out / 'depth-core.json').write_text(json.dumps(dict(anchored=167, geometries=730)), encoding='utf-8')
