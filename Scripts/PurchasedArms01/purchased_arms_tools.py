"""MSQ-61 inspection and acceptance through the official Epic MCP registry."""
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration


@u.uclass()
class PurchasedArms01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str) -> str:
        import purchased_arms_unreal as work
        try:
            return json.dumps(work.action(operation, argument))
        except Exception:
            return json.dumps({'error': traceback.format_exc()})


registration = Registration([PurchasedArms01Tools])
registration.register()
