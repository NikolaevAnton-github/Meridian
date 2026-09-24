"""MSQ-119 guarded lifecycle and read-only state through official Epic MCP."""
import json
from pathlib import Path
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

ROOT=Path('D:/devgames/MeridianSquad')
OUT=ROOT/'Saved/CombatAI01/CAI-T02/Worker/Candidate01'
def state():
    project=Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
    assert project.resolve()==ROOT.resolve()
    world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
    return dict(project=str(project),engine=u.SystemLibrary.get_engine_version(),
        map=world.get_path_name() if world else None,
        pie=[w.get_path_name() for w in u.EditorLevelLibrary.get_pie_worlds(False)],
        dirty=[p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_content_packages()]+
              [p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()])
@u.uclass()
class CoverFireTools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str) -> str:
        current=state()
        assert operation in ('before','close','after','after02'), operation
        assert current['map']=='/Game/Maps/L_OpeningLobby_PainterStone01.L_OpeningLobby_PainterStone01'
        assert not current['pie'] and not current['dirty'], current
        with (OUT/('editor-'+operation+'.json')).open('x',encoding='utf-8') as f: json.dump(current,f,indent=2)
        if operation=='close': u.SystemLibrary.quit_editor()
        return json.dumps(current)
registration=Registration([CoverFireTools])
registration.register()
