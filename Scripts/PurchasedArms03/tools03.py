"""Heading diagnosis using the existing graph, input and evaluated-pose tools."""
import importlib
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration


@u.uclass()
class PurchasedArms03Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str) -> str:
        try:
            import unreal03
            if operation == 'reload':
                importlib.reload(unreal03)
                return json.dumps({'reloaded': True})
            return json.dumps(unreal03.action(operation, argument))
        except Exception:
            return json.dumps({'error': traceback.format_exc()})


registration = Registration([PurchasedArms03Tools])
registration.register()
