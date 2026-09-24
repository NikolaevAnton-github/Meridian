"""Record final live readiness after checks without changing editor state."""
import json, unreal as u, toolset_registry
from toolset_registry.registration import Registration
from Scripts.CombatAI01.CAIT03.editor_tools import state, OUT
@u.uclass()
class MobileLeanReadyTools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def read_state() -> str:
        current=state()
        assert current['map']=='/Game/Maps/L_OpeningLobby_PainterStone01.L_OpeningLobby_PainterStone01'
        assert not current['pie'] and not current['dirty'],current
        with (OUT/'editor-ready.json').open('x',encoding='utf-8') as f:json.dump(current,f,indent=2)
        return json.dumps(current)
registration=Registration([MobileLeanReadyTools]);registration.register()
