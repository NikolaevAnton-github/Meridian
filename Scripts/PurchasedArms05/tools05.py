"""Bounded airborne-action checks; transport remains the official Epic MCP."""
import importlib
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration


@u.uclass()
class PurchasedArms05Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str) -> str:
        try:
            import unreal05
            if operation == 'reload':
                importlib.reload(unreal05)
                return json.dumps({'reloaded': True})
            return json.dumps(unreal05.action(operation, argument))
        except Exception:
            return json.dumps({'error': traceback.format_exc()})


registration = Registration([PurchasedArms05Tools])
registration.register()
