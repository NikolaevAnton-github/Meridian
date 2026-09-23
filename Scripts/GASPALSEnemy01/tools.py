"""Bounded editor entrypoints for the direct GASPALS enemy integration."""
import importlib
import json
from pathlib import Path
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration


@u.uclass()
class GASPALSEnemyTools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str = '') -> str:
        from Scripts.GASPALSEnemy01 import editor
        importlib.reload(editor)
        try:
            return json.dumps(editor.run(operation, argument))
        except Exception:
            import traceback
            error = traceback.format_exc()
            (editor.OUT / 'last-editor-error.txt').write_text(error)
            return json.dumps({'error': error})


registration = Registration([GASPALSEnemyTools])
registration.register()
