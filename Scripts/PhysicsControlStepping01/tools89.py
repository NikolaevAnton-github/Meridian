"""Bounded MSQ-89 operations registered in the official Epic tool registry."""
import importlib
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

@u.uclass()
class PhysicsControlStepping01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str) -> str:
        try:
            import unreal89
            if operation == 'reload':
                importlib.reload(unreal89)
                return json.dumps({'reloaded': True})
            return json.dumps(unreal89.action(operation, argument))
        except Exception:
            return json.dumps({'error': traceback.format_exc()})

registration = Registration([PhysicsControlStepping01Tools])
registration.register()
