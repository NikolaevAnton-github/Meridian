"""Bounded MSQ-87 operations using the official Epic MCP registry."""
import importlib
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

@u.uclass()
class PhysicsControlBalance01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str) -> str:
        try:
            import unreal87
            if operation == 'reload':
                importlib.reload(unreal87)
                return json.dumps({'reloaded': True})
            return json.dumps(unreal87.action(operation, argument))
        except Exception:
            return json.dumps({'error': traceback.format_exc()})

registration = Registration([PhysicsControlBalance01Tools])
registration.register()
