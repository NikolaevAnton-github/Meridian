"""Registration only for bounded UpperVoid01 operations."""
import json,traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration
@u.uclass()
class OpeningLobbyUpperVoid01SoftTools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation:str,argument:str)->str:
        import uppervoid01_soft_unreal as work
        try:return json.dumps(work.action(operation,argument))
        except Exception:
            error=traceback.format_exc();work.write('error-'+operation,dict(error=error))
            return json.dumps(dict(error=error))
registration=Registration([OpeningLobbyUpperVoid01SoftTools])
registration.register()
