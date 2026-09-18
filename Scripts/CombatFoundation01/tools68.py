"""Stable registration; reload implementation without replacing reflected classes."""
import importlib
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

@u.uclass()
class CombatFoundation01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str) -> str:
        try:
            import unreal68
            if operation == 'reload':
                importlib.reload(unreal68)
                return json.dumps({'reloaded': True})
            return json.dumps(unreal68.action(operation, argument))
        except Exception:
            return json.dumps({'error': traceback.format_exc()})

registration = Registration([CombatFoundation01Tools])
registration.register()
