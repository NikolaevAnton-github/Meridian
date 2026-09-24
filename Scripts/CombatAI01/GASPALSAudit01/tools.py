"""Audit tool on the existing official Epic MCP registry."""
import importlib
import json
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

@u.uclass()
class GASPALSAIAuditTools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str = '') -> str:
        from Scripts.CombatAI01.GASPALSAudit01 import editor
        importlib.reload(editor)
        return json.dumps(editor.run(operation, argument))

registration = Registration([GASPALSAIAuditTools])
registration.register()
