import importlib
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

@u.uclass()
class PhysicsControlLegPose01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str) -> str:
        try:
            import unreal91
            if operation == 'reload':
                importlib.reload(unreal91)
                return json.dumps(dict(reloaded=True))
            return json.dumps(unreal91.action(operation, argument))
        except Exception:
            return json.dumps(dict(error=traceback.format_exc()))

registration = Registration([PhysicsControlLegPose01Tools])
registration.register()
