"""Narrow new task registration in the official Epic tool registry."""
import importlib
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

@u.uclass()
class OpeningLobbyPainterStone01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str = '') -> str:
        """Operate only on the new PainterStone01 assets and bounded source reads."""
        import painterstone01_unreal as work
        if not operation.startswith('capture_'):work=importlib.reload(work)
        try:return json.dumps(work.action(operation,argument))
        except Exception:
            error=traceback.format_exc()
            work.OUT.mkdir(parents=True,exist_ok=True)
            (work.OUT/('error-'+operation+'.txt')).write_text(error)
            return json.dumps(dict(error=error))

registration=Registration([OpeningLobbyPainterStone01Tools])
registration.register()
