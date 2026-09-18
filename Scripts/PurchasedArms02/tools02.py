"""Bounded source audit and PIE checks through official Epic MCP."""
import importlib
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

@u.uclass()
class PurchasedArms02Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str) -> str:
        try:
            import unreal02
            if operation == 'reload':
                importlib.reload(unreal02)
                return json.dumps({'reloaded': True})
            return json.dumps(unreal02.action(operation, argument))
        except Exception:
            return json.dumps({'error': traceback.format_exc()})

registration = Registration([PurchasedArms02Tools])
registration.register()
