"""Bounded Layout03 editor operations exposed through official Epic MCP."""
import importlib
import json
import re
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration
from stage1_tools import state
from layout02_verification import ROOT, require_project

MAP = '/Game/Maps/L_OpeningLobby_Layout03'
OUT = ROOT/'Saved/OpeningLobby/Layout03'

@u.uclass()
class OpeningLobbyLayout03Tools(u.ToolsetDefinition):
    """Build and verify the approved neutral blockout only."""

    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str) -> str:
        """Operations: inspect, build, dimensions, correction01, correction_audit, verify, status, save_reopen."""
        s = state()
        require_project(s['project'])
        OUT.mkdir(parents=True,exist_ok=True)
        if operation == 'inspect':
            (OUT/'latest-state.json').write_text(json.dumps(s,indent=2))
            return json.dumps(s)
        if operation == 'build':
            assert not s['pie'] and not s['dirty_maps'] and not s['dirty_content'],s
            import build_layout03
            return json.dumps(importlib.reload(build_layout03).build())
        assert re.sub(r'UEDPIE_\d+_', '', s['level']).split('.')[0] == MAP,s
        if operation in ('verify','status'):
            import verify_lobby
            if operation == 'verify':
                assert verify_lobby._run is None or verify_lobby._run.done
                importlib.reload(verify_lobby)
                return verify_lobby.start(revision='Layout03')
            report = verify_lobby.status()
            return json.dumps({k:v for k,v in report.items() if k not in ('initial','events')})
        assert not s['pie'],s
        if operation in ('correction01','correction_audit'):
            import build_layout03
            module = importlib.reload(build_layout03)
            return json.dumps(module.correct_end_proxies() if operation == 'correction01' else module.correction_snapshot('after'))
        if operation == 'dimensions':
            import build_layout03
            return json.dumps(importlib.reload(build_layout03).inspect_geometry())
        if operation == 'save_reopen':
            assert not s['dirty_content'] and all(p == MAP for p in s['dirty_maps']),s
            les = u.get_editor_subsystem(u.LevelEditorSubsystem)
            assert les.save_current_level()
            assert les.load_level(MAP)
            s = state()
            world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
            s['game_mode'] = world.get_world_settings().get_editor_property('default_game_mode').get_path_name()
            s['temporarily_hidden'] = [a.get_actor_label() for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if a.is_temporarily_hidden_in_editor()]
            assert not s['pie'] and not s['dirty_maps'] and not s['dirty_content'] and not s['temporarily_hidden'],s
            assert s['game_mode'] == '/Script/MeridianSquad.OpeningLobbyGameMode',s
            (OUT/'reopened-state.json').write_text(json.dumps(s,indent=2))
            return json.dumps(s)
        raise ValueError(operation)

registration = Registration([OpeningLobbyLayout03Tools])
registration.register()
