"""Bounded sprint-jump audit using existing source and input utilities."""
import importlib
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration


@u.uclass()
class PurchasedArms04Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str) -> str:
        try:
            import unreal04
            if operation == 'reload':
                importlib.reload(unreal04)
                return json.dumps({'reloaded': True})
            return json.dumps(unreal04.action(operation, argument))
        except Exception:
            return json.dumps({'error': traceback.format_exc()})


registration = Registration([PurchasedArms04Tools])
registration.register()
