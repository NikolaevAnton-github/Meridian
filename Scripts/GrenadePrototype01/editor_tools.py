"""Focused direct grenade implementation helpers; all temporary tests use PIE."""
import hashlib
import json
import shutil
import re
import traceback
from pathlib import Path

import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/GrenadePrototype01'
OUT.mkdir(parents=True, exist_ok=True)


def inventory():
    return {a.get_name(): {'class': a.get_class().get_path_name(),
                          'label': a.get_actor_label(), 'transform': re.sub(r'0x[0-9A-Fa-f]+', 'address', str(a.get_actor_transform()))}
            for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()}


def state():
    editor = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    return {'project': u.Paths.get_project_file_path(),
            'level': editor.get_editor_world().get_path_name(),
            'pie': editor.get_game_world() is not None,
            'dirty_maps': [p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()],
            'dirty_content': [p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_content_packages()]}


def action(operation, argument):
    if operation == 'state':
        return state()
    if operation == 'preserve':
        s = state()
        assert not s['pie'] and 'L_OpeningLobby_PainterStone01' in s['level'], s
        path = ROOT / 'Content/Maps/L_OpeningLobby_PainterStone01.umap'
        before = OUT / 'owner-map-before-save.umap'
        assert not before.exists()
        shutil.copy2(path, before)
        actors = inventory()
        (OUT / 'owner-actors.json').write_text(json.dumps(actors, indent=2))
        (OUT / 'editor-before.json').write_text(json.dumps(s, indent=2))
        packages = list(u.EditorLoadingAndSavingUtils.get_dirty_content_packages())
        for package in packages:
            relative = 'Content/' + package.get_path_name().removeprefix('/Game/') + '.uasset'
            source = ROOT / relative
            assert source.is_file(), source
            snapshot = OUT / 'PreSave' / relative
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, snapshot)
        if packages:
            assert u.EditorLoadingAndSavingUtils.save_packages(packages, only_dirty=True)
        if s['dirty_maps']:
            assert s['dirty_maps'] == ['/Game/Maps/L_OpeningLobby_PainterStone01'], s
            assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
        assert inventory() == actors
        shutil.copy2(path, OUT / 'owner-map-saved.umap')
        return {'actors': len(actors), 'state': state(), 'map_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    if operation == 'close':
        s = state()
        assert not s['pie'] and not s['dirty_maps'] and not s['dirty_content'], s
        u.SystemLibrary.quit_editor()
        return {'closing': True}
    if operation == 'preserved':
        assert not state()['pie'], 'Compare the editor inventory outside PIE only.'
        before = json.loads((OUT / 'owner-actors-normalized.json').read_text())
        after = inventory()
        return {'same': before == after, 'before': len(before), 'after': len(after), 'state': state()}
    if operation == 'runtime':
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        assert world
        pawn = u.GameplayStatics.get_player_pawn(world, 0)
        grenades = u.GameplayStatics.get_all_actors_of_class(world, u.load_class(None, '/Game/NextGenDestruction/Blueprints/Actors/BP_Grenade.BP_Grenade_C'))
        return {'pawn': pawn.get_path_name(), 'grenades': [{'name': a.get_name(), 'position': str(a.get_actor_location()),
            'parts': [{'name': c.get_name(), 'class': c.get_class().get_name(), 'physics': c.is_simulating_physics(),
                       'collision': str(c.get_collision_enabled()), 'velocity': str(c.get_component_velocity())}
                      for c in a.get_components_by_class(u.PrimitiveComponent)]} for a in grenades],
                'component': pawn.get_editor_property('grenade_thrower').get_state() if hasattr(pawn, 'grenade_thrower') else None}
    raise ValueError(operation)


@u.uclass()
class GrenadePrototypeTools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str) -> str:
        try:
            return json.dumps(action(operation, argument))
        except Exception:
            return json.dumps({'error': traceback.format_exc()})


registration = Registration([GrenadePrototypeTools])
registration.register()
