"""Bounded registration for the approved FunctionalBuild01 candidate."""
import importlib
import json
import traceback
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

@u.uclass()
class OpeningLobbyFunctionalBuild01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str = '') -> str:
        """Candidate inspect/create/import/assemble/audit; captures and real PIE verification."""
        import functionalbuild01_unreal as work
        if operation in ['inspect','create','import','assemble','audit','save_reopen','final_state','refine_elevator','verify','verify_elevator']:
            work=importlib.reload(work)
        try:return json.dumps(work.action(operation,argument))
        except Exception:
            error=traceback.format_exc();(work.OUT/('error-'+operation+'.txt')).write_text(error)
            return json.dumps({'error':error})

registration=Registration([OpeningLobbyFunctionalBuild01Tools])
registration.register()
