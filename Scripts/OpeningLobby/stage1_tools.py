"""Focused Stage 1 tools registered with the installed Epic ToolsetRegistry.

Bootstrap once in the editor Python console:
    import sys; sys.path.append('D:/devgames/MeridianSquad/Scripts/OpeningLobby')
    import stage1_tools
"""
import json
import base64
import runpy
from pathlib import Path
import unreal
import toolset_registry
from toolset_registry.registration import Registration

ROOT = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
OUT = ROOT / 'Saved/OpeningLobby/Stage1'
_overview_saved = None

def state():
    subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    game = subsystem.get_game_world()
    world = game or subsystem.get_editor_world()
    result = dict(project=unreal.Paths.get_project_file_path(), engine=unreal.SystemLibrary.get_engine_version(),
                  level=world.get_path_name(),
                  dirty_content=[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],
                  dirty_maps=[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()])
    result['pie'] = game is not None
    if game:
        pawn = unreal.GameplayStatics.get_player_pawn(game, 0)
        pc = unreal.GameplayStatics.get_player_controller(game, 0)
        result['pawn'] = pawn.get_path_name() if pawn else None
        if pawn:
            p, v, r = pawn.get_actor_location(), pawn.get_velocity(), pc.get_control_rotation()
            result.update(pawn_class=pawn.get_class().get_path_name(), possessed=pawn.get_controller() == pc,
                          location=[p.x,p.y,p.z], velocity=[v.x,v.y,v.z], rotation=[r.pitch,r.yaw,r.roll])
            if hasattr(pawn, 'get_probe_state'):
                result.update(json.loads(pawn.get_probe_state()))
    return result

@unreal.uclass()
class OpeningLobbyStage1Tools(unreal.ToolsetDefinition):
    """Bounded lobby construction and reproducible PIE verification for MSQ-5."""

    @toolset_registry.tool_call
    @staticmethod
    def inspect() -> str:
        """Record project, dirty packages, and current possessed pawn/floor state."""
        result = state()
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / 'latest-state.json').write_text(json.dumps(result, indent=2))
        return json.dumps(result)

    @toolset_registry.tool_call
    @staticmethod
    def preserve_dirty_materials() -> str:
        """Copy the four pre-existing unsaved benchmark materials without overwriting originals."""
        assert not state()['pie']
        assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
        saved = []
        for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages():
            source = package.get_path_name()
            assert source.startswith('/Game/Development/Benchmark/Bench'), source
            dest = '/Game/Development/PreservedBeforeLobby/' + source.rsplit('/', 1)[1]
            assert not unreal.EditorAssetLibrary.does_asset_exist(dest), dest
            copy = unreal.EditorAssetLibrary.duplicate_asset(source, dest)
            assert copy and unreal.EditorAssetLibrary.save_loaded_asset(copy, only_if_is_dirty=False)
            saved.append(dict(source=source, preserved=dest))
        (OUT / 'preserved-dirty-materials.json').write_text(json.dumps(saved, indent=2))
        return json.dumps(saved)

    @toolset_registry.tool_call
    @staticmethod
    def close_for_build() -> str:
        """Close this editor after verifying all dirty content has a saved preservation copy."""
        current = state()
        assert not current['pie'] and not current['dirty_maps']
        preserved = json.loads((OUT / 'preserved-dirty-materials.json').read_text())
        assert set(current['dirty_content']) <= {x['source'] for x in preserved}
        for item in preserved:
            assert unreal.EditorAssetLibrary.does_asset_exist(item['preserved'])
        # Copies preserve the unsaved versions; original on-disk benchmark bytes stay intact.
        unreal.SystemLibrary.execute_console_command(None, 'QUIT_EDITOR')
        return 'Editor close requested; preservation copies recorded.'

    @toolset_registry.tool_call
    @staticmethod
    def build_lobby() -> str:
        """Build and save only the dedicated lobby using the checked-in construction script."""
        assert not state()['pie']
        return json.dumps(runpy.run_path(str(ROOT / 'Scripts/OpeningLobby/build_lobby.py'))['build']())

    @toolset_registry.tool_call
    @staticmethod
    def begin_verification() -> str:
        """Start the tick-driven real-input route, collision and gravity test in an existing PIE session."""
        import verify_lobby
        import importlib
        assert verify_lobby._run is None or verify_lobby._run.done
        importlib.reload(verify_lobby)
        return verify_lobby.start()

    @toolset_registry.tool_call
    @staticmethod
    def verification_status() -> str:
        """Read the foreground caller's active PIE verification result."""
        import verify_lobby
        return json.dumps(verify_lobby.status())

    @toolset_registry.tool_call
    @staticmethod
    def begin_view_capture() -> str:
        """Walk to the elevator and look back for a useful eye-level destination image, then return."""
        import verify_lobby
        import importlib
        assert verify_lobby._run is None or verify_lobby._run.done
        importlib.reload(verify_lobby)
        return verify_lobby.start(views=True)

    @toolset_registry.tool_call
    @staticmethod
    def capture_view(name: str) -> str:
        """Save a viewport screenshot under the bounded Stage 1 evidence directory."""
        assert name in ['entrance', 'center', 'elevator', 'overview']
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if not world:
            capture = unreal.ToolsetRegistry.execute_tool('EditorToolset.EditorAppToolset', 'CaptureViewport',
                json.dumps(dict(captureTransform=None, annotations=None, bShowUI=False)))
            assert capture.is_complete and not capture.error
            data = json.loads(capture.value)['returnValue']['image']['data']
            (OUT / (name + '.png')).write_bytes(base64.b64decode(data))
            return str(OUT / (name + '.png'))
        unreal.SystemLibrary.execute_console_command(world, 'HighResShot 1 filename="' + str(OUT / (name + '.png')) + '"')
        return str(OUT / (name + '.png'))

    @toolset_registry.tool_call
    @staticmethod
    def overview_plan(enable: bool) -> str:
        """Temporarily hide the ceiling for a top-down evidence view; restore all visibility afterward."""
        global _overview_saved
        assert not state()['pie']
        les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        if enable:
            assert _overview_saved is None
            actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
            ceiling = [a for a in actors if str(a.get_folder_path()) == 'OpeningLobby/Ceiling']
            _overview_saved = ([(a,a.is_temporarily_hidden_in_editor()) for a in ceiling],
                               editor.get_level_viewport_camera_info(),les.editor_get_game_view())
            for actor in ceiling:
                actor.set_is_temporarily_hidden_in_editor(True)
            les.editor_set_game_view(True)
            editor.set_level_viewport_camera_info(unreal.Vector(0,0,3400),unreal.Rotator(pitch=-90,yaw=0,roll=0))
        else:
            assert _overview_saved is not None
            actors,camera,game_view = _overview_saved
            for actor,hidden in actors:
                actor.set_is_temporarily_hidden_in_editor(hidden)
            editor.set_level_viewport_camera_info(*camera)
            les.editor_set_game_view(game_view)
            _overview_saved = None
        return 'Overview enabled' if enable else 'Original ceiling visibility and camera restored'

registration = Registration([OpeningLobbyStage1Tools])
registration.register()
