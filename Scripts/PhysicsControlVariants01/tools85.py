"""Task-scoped operations on the retained Epic MCP transport."""
import importlib
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

@u.uclass()
class PhysicsControlVariants01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str) -> str:
        try:
            import unreal85
            if operation == 'reload':
                importlib.reload(unreal85)
                return json.dumps({'reloaded': True})
            return json.dumps(unreal85.action(operation, argument))
        except Exception:
            return json.dumps({'error': traceback.format_exc()})

registration = Registration([PhysicsControlVariants01Tools])
registration.register()
