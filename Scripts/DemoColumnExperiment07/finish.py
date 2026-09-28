"""Restore the editor view and verify only the intended demo actor was replaced."""
import json
import re
from pathlib import Path
import unreal as u

OUT = Path('D:/devgames/MeridianSquad/Saved/DemoColumnExperiment07')
editor = u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert not editor.get_game_world()
before = json.loads((OUT / 'editor-before.json').read_text(encoding='utf-8-sig'))
actors = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
rows = [dict(path=a.get_path_name(), label=a.get_actor_label(), transform=str(a.get_actor_transform())) for a in actors]


def unchanged(rows):
    return {r['path']: (r['label'], r['transform'].split('{', 1)[1])
            for r in rows if r['label'] != 'EXP_DemoTiledColumn01'}


assert unchanged(rows) == unchanged(before['actors'])
demo = [a for a in actors if a.get_actor_label() == 'EXP_DemoTiledColumn01']
assert len(demo) == 1 and demo[0].actor_has_tag('DemoColumnRefined07')
assert '/Correction07/' in demo[0].get_editor_property('DataAsset').get_path_name()
assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not u.EditorLoadingAndSavingUtils.get_dirty_content_packages()
location = [float(n) for n in re.findall(r': ([-+]?\d+(?:\.\d+)?)', before['camera'][0])]
rotation = [float(n) for n in re.findall(r': ([-+]?\d+(?:\.\d+)?)', before['camera'][1])]
editor.set_level_viewport_camera_info(u.Vector(*location), u.Rotator(*rotation))
u.get_default_object(u.load_class(None, '/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground', True)
result = dict(actor_count=len(rows), unrelated_actors_unchanged=True, actor=demo[0].get_path_name(),
              data=demo[0].get_editor_property('DataAsset').get_path_name(), dirty_packages=0,
              restored_camera=before['camera'], background_throttle=True)
(OUT / 'editor-final.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result))
