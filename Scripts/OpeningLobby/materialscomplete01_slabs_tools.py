"""Registration only for the authorized bounded slab operation."""
import importlib,json,traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration
@u.uclass()
class OpeningLobbyMaterialsSlabs01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation:str,argument:str)->str:
        import materialscomplete01_slabs_unreal as work
        if not operation.startswith('capture_'):work=importlib.reload(work)
        try:return json.dumps(work.action(operation,argument))
        except Exception:
            error=traceback.format_exc();work.write('error-'+operation,dict(error=error))
            return json.dumps(dict(error=error))
registration=Registration([OpeningLobbyMaterialsSlabs01Tools])
registration.register()
