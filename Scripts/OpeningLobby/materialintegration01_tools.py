"""Narrow official Epic MCP entrypoint for the opaque material candidate."""
import importlib
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

@u.uclass()
class OpeningLobbyMaterialIntegration01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str = '') -> str:
        """Inspect, bind, capture and verify only the MaterialIntegration01 task."""
        import materialintegration01_unreal as work
        if not operation.startswith('capture') and not operation.startswith('walk'):
            work = importlib.reload(work)
        try:
            return json.dumps(work.action(operation, argument))
        except Exception:
            error = traceback.format_exc()
            work.OUT.mkdir(parents=True, exist_ok=True)
            (work.OUT / ('error-' + operation + '.txt')).write_text(error)
            return json.dumps({'error': error})

registration = Registration([OpeningLobbyMaterialIntegration01Tools])
registration.register()
