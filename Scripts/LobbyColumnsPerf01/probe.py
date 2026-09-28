"""Focused PIE checks for pristine cladding sleep, wake, rifle damage and F6."""
import json
import time
import traceback
from pathlib import Path

import unreal as u

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/LobbyColumnsPerf01'
TARGET = 'Pier_2_-1'


def world():
    result = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    assert result
    return result


def columns():
    return [a for a in u.GameplayStatics.get_all_actors_of_class(world(), u.Actor)
            if a.actor_has_tag('LobbyColumns01')]


def target():
    return next(a for a in columns()
                if str(a.get_component_by_class(u.NGDPropComponent).object_id) == TARGET)


def state(actor):
    location = actor.get_actor_location()
    return dict(prop=json.loads(actor.get_component_by_class(u.NGDPropComponent).get_state()),
                cladding=json.loads(actor.get_component_by_class(u.DemoColumnCladding).get_state()),
                location=[location.x, location.y, location.z])


def sample(name):
    rows = [state(a) for a in columns()]
    (OUT / (name + '.json')).write_text(json.dumps(rows, indent=2))
    print(json.dumps(dict(sample=name, columns=len(rows),
                         idle=sum(r['cladding']['idle'] for r in rows),
                         full_updates=[r['cladding']['full_updates'] for r in rows])))
    return rows


def capture(name):
    u.SystemLibrary.execute_console_command(world(), 'CsvProfile STARTFILE=LobbyColumnsPerf01-' + name + '.csv')
    u.SystemLibrary.execute_console_command(world(), 'CsvProfile FRAMES=400')


def transitions(name='transitions01'):
    """Move an untouched column, externally fracture its root, then reset via F6."""
    path = OUT / (name + '.json')
    assert not path.exists()
    actor = target()
    origin = actor.get_actor_location()
    report = dict(before=state(actor), samples={})
    started = time.monotonic()
    stage = 0
    handle = None

    def tick(delta):
        nonlocal stage, handle
        elapsed = time.monotonic() - started
        try:
            if stage == 0 and elapsed >= 1:
                actor.set_actor_location(origin + u.Vector(50, 0, 0), False, True)
                stage = 1
            elif stage == 1 and elapsed >= 2:
                report['samples']['moved'] = state(actor)
                actor.set_actor_location(origin, False, True)
                stage = 2
            elif stage == 2 and elapsed >= 3:
                report['samples']['restored'] = state(actor)
                gc = actor.get_component_by_class(u.GeometryCollectionComponent)
                gc.apply_external_strain(gc.get_root_index(), origin, 1000., 0, 1., 1.e9)
                stage = 3
            elif stage == 3 and elapsed >= 5:
                report['samples']['external_fracture'] = state(actor)
                u.GameplayStatics.get_player_pawn(world(), 0).probe_key('F6', 1., True)
                stage = 4
            elif stage == 4 and elapsed >= 5.5:
                u.GameplayStatics.get_player_pawn(world(), 0).probe_key('F6', 0., False)
                stage = 5
            elif stage == 5 and elapsed >= 8:
                report['samples']['reset'] = state(target())
                report['columns_after_reset'] = [state(a) for a in columns()]
                path.write_text(json.dumps(report, indent=2))
                u.unregister_slate_post_tick_callback(handle)
        except Exception:
            report['error'] = traceback.format_exc()
            path.write_text(json.dumps(report, indent=2))
            u.GameplayStatics.get_player_pawn(world(), 0).probe_key('F6', 0., False)
            u.unregister_slate_post_tick_callback(handle)

    handle = u.register_slate_post_tick_callback(tick)
    print(json.dumps(dict(scheduled=name, duration=8)))


def rifle(name='rifle01'):
    # Reuse the accepted real-rifle fixture, including its reset-safe actor lookup.
    lobby = {}
    exec((ROOT / 'Scripts/LobbyColumns01/play_probe.py').read_text(), lobby)
    lobby['probe']['OUT'] = OUT
    lobby['run'](name, TARGET, [-420, -160, 90.15],
                 [[-455, -560, 22], [-385, -560, 810]])
