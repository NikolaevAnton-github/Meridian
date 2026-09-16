"""Bounded Architecture01 actions registered in official Epic MCP."""
import importlib
import json
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

@u.uclass()
class OpeningLobbyArchitecture01Tools(u.ToolsetDefinition):
    """Author and verify only the dedicated Architecture01 candidate."""
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str = '') -> str:
        """inspect, import, materials, preview, complete, audit, save_reopen, capture_prepare/camera/shoot/restore, verify/status."""
        import architecture01_unreal as work
        if operation not in ('status','capture_camera','capture_shoot','capture_restore'):
            work=importlib.reload(work)
        try:
            return json.dumps(work.action(operation,argument))
        except Exception:
            import traceback
            message=traceback.format_exc()
            (work.OUT/('error-'+operation+'.txt')).write_text(message)
            return json.dumps(dict(error=message))

registration=Registration([OpeningLobbyArchitecture01Tools])
registration.register()
