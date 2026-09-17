"""Bounded MSQ-54 operations on the official Epic MCP tool registry."""
import importlib
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

@u.uclass()
class MetaHumanTrial01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str) -> str:
        import metahuman_trial01_unreal as work
        importlib.reload(work)
        try:
            return json.dumps(work.action(operation, argument))
        except Exception:
            error = traceback.format_exc()
            work.write('error-' + operation, {'error': error})
            return json.dumps({'error': error})

registration = Registration([MetaHumanTrial01Tools])
registration.register()
