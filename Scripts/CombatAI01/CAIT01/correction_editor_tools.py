"""Register guarded state/close tools for the temporary Candidate02 load check."""
import json
import os
import sys
from pathlib import Path
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT/'Saved/CombatAI01/CAI-T01/Worker/Candidate02'
sys.path.insert(0, str(ROOT))
from Scripts.CombatAI01.CAI00.editor_tools import state


@u.uclass()
class TacticalCorrectionTools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str) -> str:
        assert operation in ('state', 'close')
        current = state()
        current['pid'] = os.getpid()
        assert current['map']=='/Game/Maps/L_OpeningLobby_PainterStone01.L_OpeningLobby_PainterStone01'
        assert not current['pie'] and not current['dirty'], current
        launch = json.loads((OUT/'editor-launch.json').read_text(encoding='utf-8-sig'))
        assert current['pid']==launch['pid'], 'Only this correction run owns this diagnostic editor'
        with (OUT/f'editor-{operation}.json').open('x', encoding='utf-8') as stream:
            json.dump(current, stream, indent=2)
        if operation=='close':
            u.SystemLibrary.quit_editor()
        return json.dumps(current)


registration = Registration([TacticalCorrectionTools])
registration.register()
