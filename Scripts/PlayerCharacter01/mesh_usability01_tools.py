"""Isolated MSQ-54 operations registered with official Epic MCP."""
import importlib
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

@u.uclass()
class MeshUsability01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str) -> str:
        import mesh_usability01_unreal as work
        importlib.reload(work)
        try: return json.dumps(work.action(operation, argument))
        except Exception:
            error=traceback.format_exc()
            work.write('error-'+operation,dict(error=error))
            return json.dumps(dict(error=error))

registration=Registration([MeshUsability01Tools])
registration.register()
