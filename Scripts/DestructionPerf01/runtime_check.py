"""Focused real-key PIE smoke: cancel a fuse, hold F7 once, then restore with F6."""
import json
import time
import traceback
from pathlib import Path
import unreal as u


def run(name='input-smoke'):
    assert name.replace('-', '').replace('_', '').isalnum()
    out = Path('D:/devgames/MeridianSquad/Saved/DestructionPerf01') / (name + '.json')
    assert not out.exists(), 'Keep prior evidence; use a new output name for another check.'
    world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    assert world
    pawn = u.GameplayStatics.get_player_pawn(world, 0)
    fixture = u.GameplayStatics.get_actor_of_class(world, u.DestructionPerfFixture)
    thrower = pawn.get_component_by_class(u.PrototypeGrenadeComponent)
    assert fixture and thrower
    initial = json.loads(thrower.get_state())
    started = time.monotonic()
    stage = 0
    report = {'initial': initial, 'events': []}

    def snapshot(name):
        row = {'name': name, 'elapsed': time.monotonic() - started,
               'fixture': json.loads(fixture.get_state()), 'grenade': json.loads(thrower.get_state())}
        report['events'].append(row)
        return row

    def key(name, pressed):
        pawn.probe_key(name, 1 if pressed else 0, pressed)

    def tick(delta):
        nonlocal stage
        try:
            elapsed = time.monotonic() - started
            if stage == 0 and elapsed > 1:
                key('F7', True); stage = 1
            elif stage == 1 and elapsed > 1.4:
                key('F7', False); key('F6', True); stage = 2
            elif stage == 2 and elapsed > 1.6:
                key('F6', False); stage = 3
            elif stage == 3 and elapsed > 4:
                row = snapshot('cancelled_fuse')
                assert row['grenade']['explosions'] == initial['explosions']
                assert row['grenade']['live_grenades'] == 0 and not row['fixture']['spent']
                key('F7', True); stage = 4
            elif stage == 4 and elapsed > 9:
                key('F7', False)
                row = snapshot('held_once')
                assert row['grenade']['explosions'] == initial['explosions'] + 1
                assert row['fixture']['recording'] and row['fixture']['detonated']
                stage = 5
            elif stage == 5 and elapsed > 23:
                row = snapshot('saved')
                assert not row['fixture']['recording'] and row['fixture']['output']
                key('F6', True); stage = 6
            elif stage == 6 and elapsed > 23.3:
                key('F6', False); stage = 7
            elif stage == 7 and elapsed > 26:
                row = snapshot('restored')
                assert not row['fixture']['spent'] and row['grenade']['live_grenades'] == 0
                props = [json.loads(c.get_state()) for a in u.GameplayStatics.get_all_actors_of_class(world, u.Actor)
                         for c in [a.get_component_by_class(u.NGDPropComponent)] if c]
                report['props_after_reset'] = props
                assert len(props) == 26 and all(p['ready'] and p['break_events'] == 0 and not p['root_broken'] for p in props)
                report['passed'] = True
                out.write_text(json.dumps(report, indent=2))
                u.unregister_slate_post_tick_callback(handle)
        except Exception:
            key('F7', False); key('F6', False)
            report['error'] = traceback.format_exc()
            out.write_text(json.dumps(report, indent=2))
            u.unregister_slate_post_tick_callback(handle)
    handle = u.register_slate_post_tick_callback(tick)
    return {'scheduled': str(out)}
