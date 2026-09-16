"""Candidate-scoped registration on official Epic MCP; no general Python runner."""
import importlib
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

@u.uclass()
class OpeningLobbyReworkA01Tools(u.ToolsetDefinition):
    """Build and verify only the owner-authorized ReworkA01 neutral candidate."""
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str = '') -> str:
        """inspect/create/import/assemble/audit/save_reopen; capture_prepare/camera/shoot/restore; verify/status."""
        import reworka01_unreal as work
        if operation in ['inspect','create','import','assemble','audit','save_reopen']:
            work=importlib.reload(work)
        try:
            return json.dumps(work.action(operation,argument))
        except Exception:
            error=traceback.format_exc();(work.OUT/('error-'+operation+'.txt')).write_text(error)
            return json.dumps(dict(error=error))

registration=Registration([OpeningLobbyReworkA01Tools])
registration.register()
