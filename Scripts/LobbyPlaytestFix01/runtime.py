"""Bounded live PIE input traces. Collect the completion file before ending a run."""
import json
import time
import traceback
import unreal as u
from scene import OUT, write

FIRE_KEY = next(m.key for m in u.load_asset('/Game/InfimaGames/TacticalFPSAnimations/Common/Core/Inputs/IMC_TFA_Default').get_editor_property('default_key_mappings').mappings if m.action.get_name() == 'IA_TFA_Fire')

def objects():
    w = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    assert w and 'L_OpeningLobby_PainterStone01' in w.get_path_name()
    p = u.GameplayStatics.get_player_pawn(w, 0)
    return w, p, p.get_component_by_class(u.CombatRifleComponent), u.GameplayStatics.get_actor_of_class(w, u.CombatProjectileWorld)

def state():
    w, p, r, sim = objects()
    rifle = json.loads(r.get_rifle_state())
    combat = json.loads(sim.get_combat_state())
    anim = p.get_component_by_class(u.SkeletalMeshComponent).get_anim_instance()
    montage = anim.get_current_active_montage()
    view, rotation = u.GameplayStatics.get_player_controller(w, 0).get_player_view_point()
    return dict(rifle=rifle, combat={k: v for k, v in combat.items() if not isinstance(v, (list, dict))},
                flags={k: bool(p.get_editor_property(k)) for k in ['bIsBusy', 'bIsRunning', 'bIsSprinting']},
                montage=montage.get_path_name() if montage else None,
                location=str(p.get_actor_location()), eyes=str(p.get_actor_eyes_view_point()),
                view=[view.x,view.y,view.z], global_dilation=u.GameplayStatics.get_global_time_dilation(w),
                player_dilation=p.custom_time_dilation,
                key_down=u.GameplayStatics.get_player_controller(w, 0).is_input_key_down(FIRE_KEY),
                props=[json.loads(c.get_state()) for a in u.GameplayStatics.get_all_actors_of_class(w, u.Actor)
                       for c in [a.get_component_by_class(u.NGDPropComponent)] if c])

def run(name, events, duration):
    """Events use elapsed real seconds; all input traverses PlayerController/EnhancedInput."""
    path = OUT / (name + '.json')
    assert not path.exists()
    w, p, r, sim = objects()
    report = dict(method='PlayerController InputKey -> EnhancedInput -> rifle -> finite projectile sweep', events=events, before=state(), samples=[])
    started = time.monotonic()
    index = 0
    handle = None
    def tick(delta):
        nonlocal index, handle
        try:
            elapsed = time.monotonic() - started
            while index < len(events) and elapsed >= events[index][0]:
                event = events[index]
                operation, args = event[1], event[2:]
                if operation == 'fire':
                    u.NGDTools.rifle_input(w, args[0])
                elif operation == 'key':
                    p.probe_key(args[0], 1.0 if args[1] else 0.0, args[1])
                elif operation == 'aim':
                    u.NGDTools.aim_player(w, u.Vector(*args[0]))
                elif operation == 'fps':
                    u.SystemLibrary.execute_console_command(w, 't.MaxFPS ' + str(args[0]))
                elif operation == 'ammo':
                    assert r.probe_ammo(*args)
                elif operation == 'position':
                    p.set_actor_location(u.Vector(*args[0]), False, True)
                else:
                    raise ValueError(operation)
                index += 1
            report['samples'].append(dict(elapsed=elapsed, **state()))
            if elapsed >= duration:
                u.NGDTools.rifle_input(w, False)
                report['after'] = state()
                write(name + '.json', report)
                u.unregister_slate_post_tick_callback(handle)
        except Exception:
            u.NGDTools.rifle_input(w, False)
            u.SystemLibrary.execute_console_command(w, 't.MaxFPS 60')
            report['error'] = traceback.format_exc()
            write(name + '.json', report)
            u.unregister_slate_post_tick_callback(handle)
    handle = u.register_slate_post_tick_callback(tick)
    print(json.dumps(dict(scheduled=name, duration=duration)))
