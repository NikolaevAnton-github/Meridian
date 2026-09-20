import importlib
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

@u.uclass()
class PhysicsControlRecoverability01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str) -> str:
        try:
            import unreal97
            if operation == 'reload':
                importlib.reload(unreal97)
                return json.dumps(dict(reloaded=True))
            return json.dumps(unreal97.action(operation, argument))
        except Exception:
            return json.dumps(dict(error=traceback.format_exc()))

registration = Registration([PhysicsControlRecoverability01Tools])
registration.register()
