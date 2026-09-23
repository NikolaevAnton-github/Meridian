"""MSQ-102 read-only inventory and guarded native-build lifecycle via Epic MCP."""
import json
from pathlib import Path
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/CombatAI01/CAI-00/Worker/Candidate01'


def state():
    assert ROOT.resolve() == Path('D:/devgames/MeridianSquad').resolve()
    world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
    return dict(project=str(ROOT), engine=u.SystemLibrary.get_engine_version(),
                map=world.get_path_name() if world else None,
                pie=[w.get_path_name() for w in u.EditorLevelLibrary.get_pie_worlds(False)],
                dirty=[p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_content_packages()] +
                      [p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()])


@u.uclass()
class CombatAI00Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str) -> str:
        current = state()
        OUT.mkdir(parents=True, exist_ok=True)
        if operation in ('before', 'after', 'close'):
            assert current['map'] == '/Game/Maps/L_OpeningLobby_PainterStone01.L_OpeningLobby_PainterStone01'
            if operation == 'close':
                assert not current['pie'] and not current['dirty'], current
            (OUT / ('editor-' + operation + '.json')).write_text(json.dumps(current, indent=2))
            if operation == 'close':
                u.SystemLibrary.quit_editor()
            return json.dumps(current)
        if operation == 'audio':
            assets = [dict(path=str(a.package_name), kind=str(a.asset_class_path.asset_name))
                      for a in u.AssetRegistryHelpers.get_asset_registry().get_assets_by_path('/Game', recursive=True)
                      if str(a.asset_class_path.asset_name) in ('SoundWave', 'SoundCue', 'MetaSoundSource')]
            (OUT / 'audio-inventory.json').write_text(json.dumps(assets, indent=2))
            return json.dumps(assets)
        raise ValueError(operation)


registration = Registration([CombatAI00Tools])
registration.register()
