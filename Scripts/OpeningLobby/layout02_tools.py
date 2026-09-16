"""Dedicated Layout02 actions registered in the official Epic tool registry."""
import base64
import importlib
import json
import runpy
import re
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration
from stage1_tools import state
from layout02_verification import ROOT, require_project

OUT = ROOT / 'Saved/OpeningLobby/Layout02'
MAP = '/Game/Maps/L_OpeningLobby_Layout02'
_overview = None

@u.uclass()
class OpeningLobbyLayout02Tools(u.ToolsetDefinition):
    """Build, inspect, capture and verify only the approved lobby revision."""

    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str) -> str:
        """Allowed operations: inspect, build, refine, verify, views, status, overview, restore, capture_overview, save_reopen."""
        global _overview
        s = state()
        require_project(s['project'])
        OUT.mkdir(parents=True, exist_ok=True)
        les = u.get_editor_subsystem(u.LevelEditorSubsystem)
        editor = u.get_editor_subsystem(u.UnrealEditorSubsystem)
        if operation == 'inspect':
            (OUT/'latest-state.json').write_text(json.dumps(s,indent=2))
            return json.dumps(s)
        if operation == 'build':
            assert not s['pie'] and not s['dirty_maps'] and not s['dirty_content'], s
            return json.dumps(runpy.run_path(str(ROOT/'Scripts/OpeningLobby/build_layout02.py'))['build']())
        assert re.sub(r'UEDPIE_\d+_', '', s['level']).split('.')[0] == MAP, s
        if operation in ('verify','views','status'):
            import verify_lobby
            if operation in ('verify','views'):
                assert verify_lobby._run is None or verify_lobby._run.done
                importlib.reload(verify_lobby)
                return verify_lobby.start(views=operation == 'views',revision='Layout02')
            return json.dumps(verify_lobby.status())
        assert not s['pie'], s
        if operation == 'refine':
            assert all(p.startswith('/Game/OpeningLobby/Layout02/') for p in s['dirty_content']),s
            assert all(p == MAP for p in s['dirty_maps']),s
            return runpy.run_path(str(ROOT/'Scripts/OpeningLobby/build_layout02.py'))['refine_appearance']()
        elif operation == 'overview':
            assert _overview is None
            actors = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
            roof = [a for a in actors if str(a.get_folder_path()) == 'Layout02/Ceiling' or a.get_actor_label().startswith(('HeavyLongLintel_','UpperClerestoryWall_'))]
            _overview = ([(a,a.is_temporarily_hidden_in_editor()) for a in roof],editor.get_level_viewport_camera_info(),les.editor_get_game_view())
            for a in roof:
                a.set_is_temporarily_hidden_in_editor(True)
            les.editor_set_game_view(True)
            editor.set_level_viewport_camera_info(u.Vector(0,0,2600),u.Rotator(pitch=-90,yaw=90,roll=0))
        elif operation == 'capture_overview':
            assert _overview is not None
            capture = u.ToolsetRegistry.execute_tool('EditorToolset.EditorAppToolset','CaptureViewport',json.dumps(dict(captureTransform=None,annotations=None,bShowUI=False)))
            assert capture.is_complete and not capture.error
            value = json.loads(capture.value)['returnValue']
            (OUT/'overview.png').write_bytes(base64.b64decode(value['image'].pop('data')))
            (OUT/'overview-camera.json').write_text(json.dumps(value,indent=2))
        elif operation == 'restore':
            assert _overview is not None
            actors,camera,game_view = _overview
            for a,hidden in actors:
                a.set_is_temporarily_hidden_in_editor(hidden)
            editor.set_level_viewport_camera_info(*camera)
            les.editor_set_game_view(game_view)
            _overview = None
        elif operation == 'save_reopen':
            assert _overview is None
            assert not s['dirty_content'], s
            assert les.save_current_level()
            assert les.load_level(MAP)
            s = state()
            world = editor.get_editor_world()
            s['game_mode'] = world.get_world_settings().get_editor_property('default_game_mode').get_path_name()
            s['temporarily_hidden'] = [a.get_actor_label() for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if a.is_temporarily_hidden_in_editor()]
            assert not s['pie'] and not s['dirty_maps'] and not s['dirty_content'] and not s['temporarily_hidden'],s
            assert s['game_mode'] == '/Script/MeridianSquad.OpeningLobbyGameMode',s
            (OUT/'reopened-state.json').write_text(json.dumps(s,indent=2))
            return json.dumps(s)
        else:
            raise ValueError(operation)
        return operation + ' complete'

registration = Registration([OpeningLobbyLayout02Tools])
registration.register()
