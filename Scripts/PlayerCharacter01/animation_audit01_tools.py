"""Bounded animation audit operations registered with official Epic MCP."""
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration


@u.uclass()
class PlayerAnimationAudit01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str) -> str:
        import animation_audit01_unreal as work
        try:
            return json.dumps(work.action(operation, argument))
        except Exception:
            error = traceback.format_exc()
            work.write('error-' + operation, {'error': error})
            return json.dumps({'error': error})


registration = Registration([PlayerAnimationAudit01Tools])
registration.register()
