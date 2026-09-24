"""Register the scoped ED-01 editor tool with Epic MCP."""
import importlib
import sys
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

sys.path.insert(0, 'D:/devgames/MeridianSquad/Scripts/EnvironmentDestruction01')

@u.uclass()
class ED01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def run(operation: str, argument: str = '') -> str:
        import ed01_editor
        return importlib.reload(ed01_editor).run(operation, argument)

registration = Registration([ED01Tools])
registration.register()
