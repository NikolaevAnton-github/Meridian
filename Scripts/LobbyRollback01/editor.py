"""Read-only actor/property exports and focused saved-map checks for MSQ-171."""
import importlib.util
import json
from pathlib import Path
import unreal as u

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/LobbyRollback01'
LOBBY = '/Game/Maps/L_OpeningLobby_PainterStone01'
TEMP = '/Game/Maps/L_RollbackBaseline01'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def capture(name):
    editor = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve() == ROOT
    assert not editor.get_game_world()
    dirty = [p.get_path_name() for p in list(u.EditorLoadingAndSavingUtils.get_dirty_map_packages())
             + list(u.EditorLoadingAndSavingUtils.get_dirty_content_packages())]
    assert not dirty, 'Never discard unsaved owner state.'
    inspect = module('rollback_inspect', 'Scripts/NextGenDestructionIntegration01/inspect_scene.py')
    scene = module('rollback_props', 'Scripts/LobbyPlaytestFix01/scene.py')
    actors = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
    props = [scene.prop_record(a) for a in actors if a.get_class().get_name() == 'BP_BreakableObject_C']
    path = OUT / (name + '.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(dict(world=editor.get_editor_world().get_path_name(), dirty=dirty,
                       actors=inspect.actors(), props=props), f, indent=2)
    export_path = OUT / (name + '.t3d')
    assert not export_path.exists()
    task = u.AssetExportTask()
    task.object = editor.get_editor_world()
    task.filename = str(export_path)
    task.automated = True
    task.prompt = False
    task.selected = False
    task.exporter = u.LevelExporterT3D()
    assert u.Exporter.run_asset_export_task(task), list(task.errors)
    print(json.dumps(dict(capture=name, actors=len(actors), props=len(props), export_bytes=export_path.stat().st_size)))


def verify(name):
    capture(name)
    data = json.loads((OUT / (name + '.json')).read_text())
    baseline = json.loads((OUT / 'Baseline/editor-loaded.json').read_text())
    assert len(data['actors']) == 143
    assert len(data['props']) == 14
    assert data['props'] == baseline['props'], 'Source configurations/transforms/materials must match.'
    forbidden = ('DemoColumn', 'LobbyFacing', 'DestructionFragment', 'ReinforcedColumn', 'LobbyColumns01', 'DestructionScaling01')
    assert not any(word in json.dumps(data) for word in forbidden)
    print('Saved lobby: 143 actors, 14 exact vendor specimens, no custom column references.')
