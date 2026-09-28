"""Bounded in-editor evidence using the real rifle input and projectile path.

Execute this module in a persistent globals dictionary, then call run().
Evidence belongs in Saved; this helper does not modify saved map/assets.
"""
import json
import time
import traceback
from pathlib import Path
import unreal as u

OUT = Path('D:/devgames/MeridianSquad/Saved/DemoColumnExperiment06')


def objects():
    world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    assert world
    pawn = u.GameplayStatics.get_player_pawn(world, 0)
    actor = next(a for a in u.GameplayStatics.get_all_actors_of_class(world, u.Actor)
                 if a.actor_has_tag('DemoColumnCoarse06'))
    return world, pawn, actor


def state():
    world, pawn, actor = objects()
    gc = actor.get_component_by_class(u.GeometryCollectionComponent)
    return dict(cladding=json.loads(actor.get_component_by_class(u.DemoColumnCladding).get_state()),
                prop=json.loads(actor.get_component_by_class(u.NGDPropComponent).get_state()),
                rifle=json.loads(pawn.get_component_by_class(u.CombatRifleComponent).get_rifle_state()),
                game_time=u.GameplayStatics.get_time_seconds(world),
                global_dilation=u.GameplayStatics.get_global_time_dilation(world),
                player_dilation=pawn.custom_time_dilation,
                pieces=[dict(p=[t.translation.x, t.translation.y, t.translation.z],
                             s=[t.scale3d.x, t.scale3d.y, t.scale3d.z])
                        for t in gc.get_current_transforms()])


def run(name, events, duration):
    path = OUT / (name + '.json')
    assert not path.exists(), path
    world, pawn, actor = objects()
    report = dict(events=events, before=state(), samples=[], frame_ms=[])
    started = time.monotonic()
    index = 0
    last_sample = -1
    handle = None
    in_tick = False

    def tick(delta):
        nonlocal index, handle, last_sample, in_tick
        if in_tick:
            return
        in_tick = True
        try:
            elapsed = time.monotonic() - started
            world, pawn, actor = objects()
            report['frame_ms'].append([elapsed, delta * 1000])
            while index < len(events) and elapsed >= events[index][0]:
                _, op, *args = events[index]
                if op == 'position':
                    pawn.set_actor_location(u.Vector(*args[0]), False, True)
                elif op == 'aim':
                    assert u.NGDTools.aim_player(world, u.Vector(*args[0]))
                elif op == 'fire':
                    assert u.NGDTools.rifle_input(world, args[0])
                elif op == 'reload':
                    pawn.get_component_by_class(u.CombatRifleComponent).request_reload(False)
                elif op == 'key':
                    pawn.probe_key(args[0], 1. if args[1] else 0., args[1])
                elif op == 'capture':
                    u.AutomationLibrary.take_high_res_screenshot(1280, 720, str(OUT / (args[0] + '.png')))
                elif op == 'trace':
                    report.setdefault('traces', []).append(dict(time=elapsed, result=json.loads(
                        u.NGDTools.sweep(world, u.Vector(*args[0]), u.Vector(*args[1]), .25))))
                elif op == 'sample':
                    report.setdefault('marked', []).append(dict(label=args[0], elapsed=elapsed, **state()))
                else:
                    raise ValueError(op)
                index += 1
            if elapsed - last_sample >= .5:
                report['samples'].append(dict(elapsed=elapsed, **state()))
                last_sample = elapsed
            if elapsed >= duration:
                u.NGDTools.rifle_input(world, False)
                report['after'] = state()
                path.write_text(json.dumps(report), encoding='utf-8')
                u.unregister_slate_post_tick_callback(handle)
        except Exception:
            u.NGDTools.rifle_input(world, False)
            report['error'] = traceback.format_exc()
            path.write_text(json.dumps(report), encoding='utf-8')
            u.unregister_slate_post_tick_callback(handle)
        finally:
            in_tick = False

    handle = u.register_slate_post_tick_callback(tick)
    print(json.dumps(dict(scheduled=name, duration=duration)))
