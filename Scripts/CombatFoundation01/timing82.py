"""Bounded MSQ-82 extensions to the existing Epic transport and input probes."""
import json
from pathlib import Path
import unreal as u
import unreal68
from stage1_tools import state

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/CombatSlice01/CombatTiming01/Worker'

def write(name, value):
    destination = OUT / (name + '.json')
    destination.parent.mkdir(parents=True, exist_ok=True)
    assert not destination.exists(), destination
    destination.write_text(json.dumps(value, indent=2), encoding='utf-8')
    return value

def action(operation, argument):
    if operation == 'state':
        return write('editor-state-' + argument, state())
    if operation == 'close':
        current = state()
        assert not current['pie'] and not current['dirty_maps'] and not current['dirty_content'], current
        write('editor-before-close-' + argument, current)
        u.SystemLibrary.quit_editor()
        return {'close_requested': True}
    if operation == 'probe':
        configuration = json.loads(argument)
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        simulation = u.GameplayStatics.get_actor_of_class(world, u.CombatProjectileWorld)
        result = json.loads(simulation.probe_timing(argument))
        directory = 'Correction02/' if configuration.get('correction') == 2 else 'Correction01/' if configuration.get('correction') else ''
        return write(directory + 'controlled-' + configuration['name'], result)
    if operation in ['ballistics', 'corrections']:
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        simulation = u.GameplayStatics.get_actor_of_class(world, u.CombatProjectileWorld)
        result = simulation.probe_ballistics() if operation == 'ballistics' else simulation.probe_corrections()
        return write(operation + '-' + argument, json.loads(result))
    if operation == 'frame_rate':
        assert unreal68._performance_before is not None
        limit = float(argument)
        assert 10 <= limit <= 144
        u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),
                                               't.MaxFPS ' + str(limit))
        return {'fps': u.SystemLibrary.get_console_variable_float_value('t.MaxFPS')}
    if operation == 'verify':
        # Reuse native input, per-frame sampling, and completion/cleanup.
        before = unreal68.OUT
        try:
            correction = json.loads(argument).get('correction')
            unreal68.OUT = OUT / ('Correction02' if correction == 2 else 'Correction01') if correction else OUT
            unreal68.OUT.mkdir(parents=True, exist_ok=True)
            return unreal68.action('verify', argument)
        finally:
            unreal68.OUT = before
    if operation == 'handoff':
        current = state()
        assert not current['pie'] and not current['dirty_maps'] and not current['dirty_content'], current
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
        leaked = [a.get_name() for a in u.GameplayStatics.get_all_actors_of_class(world, u.Actor)
                  if isinstance(a, (u.CombatTarget, u.CombatProjectileWorld)) or a.actor_has_tag('CombatProbeCover')]
        assert not leaked, leaked
        current['editor_gameplay_actor_leaks'] = leaked
        current['fps_limit'] = u.SystemLibrary.get_console_variable_float_value('t.MaxFPS')
        settings = u.get_default_object(u.load_class(None, '/Script/UnrealEd.EditorPerformanceSettings'))
        current['throttle_when_background'] = settings.get_editor_property('bThrottleCPUWhenNotForeground')
        return write('handoff-' + argument, current)
    raise ValueError(operation)
