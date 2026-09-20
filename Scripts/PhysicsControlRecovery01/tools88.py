"""Bounded MSQ-88 operations registered with official Epic MCP."""
import importlib
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

@u.uclass()
class PhysicsControlRecovery01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str) -> str:
        try:
            import unreal88
            if operation == 'reload':
                importlib.reload(unreal88)
                return json.dumps({'reloaded': True})
            return json.dumps(unreal88.action(operation, argument))
        except Exception:
            return json.dumps({'error': traceback.format_exc()})

registration = Registration([PhysicsControlRecovery01Tools])
registration.register()
