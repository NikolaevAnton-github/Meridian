"""Task-scoped Epic MCP inspection entrypoint; no gameplay mutations at preflight."""
import json
from pathlib import Path
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/CombatSlice01/GASPEnemyFoundation01/Worker'


@u.uclass()
class GASPEnemyFoundation01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str = '') -> str:
        """Run the retained focused input/capture harness with GASP movement observations."""
        from Scripts.GASPEnemyFoundation01 import unreal98
        return json.dumps(unreal98.action(operation, argument))

    @toolset_registry.tool_call
    @staticmethod
    def runtime(operation: str, argument: str = '') -> str:
        """Operate the isolated runtime pilot or read its physical state."""
        import importlib
        from Scripts.GASPEnemyFoundation01 import pilot98
        importlib.reload(pilot98)
        return json.dumps(pilot98.run(operation, argument))

    @toolset_registry.tool_call
    @staticmethod
    def assets(operation: str) -> str:
        """Inspect or author only the migrated MSQ-98 Blueprint/physics derivatives."""
        import importlib
        from Scripts.GASPEnemyFoundation01 import edit_assets98
        importlib.reload(edit_assets98)
        return json.dumps(edit_assets98.run(operation))

    @toolset_registry.tool_call
    @staticmethod
    def inspect() -> str:
        subsystem = u.get_editor_subsystem(u.UnrealEditorSubsystem)
        world = subsystem.get_editor_world()
        game_world = subsystem.get_game_world()
        pie_worlds = [w.get_path_name() for w in u.EditorLevelLibrary.get_pie_worlds(False)]
        dirty = [p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
        dirty += [p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
        result = dict(project=str(ROOT), engine=u.SystemLibrary.get_engine_version(),
            editor_level=world.get_path_name() if world else None,
            game_level=game_world.get_path_name() if game_world else None,
            pie_worlds=pie_worlds, dirty_packages=dirty)
        return json.dumps(result)


registration = Registration([GASPEnemyFoundation01Tools])
registration.register()
