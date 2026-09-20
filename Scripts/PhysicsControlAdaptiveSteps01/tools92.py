import importlib
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

@u.uclass()
class PhysicsControlAdaptiveSteps01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str) -> str:
        try:
            import unreal92
            if operation == 'reload':
                importlib.reload(unreal92)
                return json.dumps(dict(reloaded=True))
            return json.dumps(unreal92.action(operation, argument))
        except Exception:
            return json.dumps(dict(error=traceback.format_exc()))

registration = Registration([PhysicsControlAdaptiveSteps01Tools])
registration.register()
