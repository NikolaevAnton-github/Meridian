"""Temporary Correction01 registration in the official Epic MCP registry."""
import importlib,json,traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration
@u.uclass()
class OpeningLobbyMaterialsCorrection01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation:str,argument:str='')->str:
        import materialscomplete01_correction_unreal as work
        if not operation.startswith('capture_'):work=importlib.reload(work)
        try:return json.dumps(work.action(operation,argument))
        except Exception:
            error=traceback.format_exc()
            work.write('error-'+operation,dict(error=error))
            return json.dumps(dict(error=error))
registration=Registration([OpeningLobbyMaterialsCorrection01Tools])
registration.register()
