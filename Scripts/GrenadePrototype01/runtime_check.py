"""Short real-input smoke check. Does not edit or save the level."""
import json
import time
import traceback
from pathlib import Path
import unreal as u

OUT = Path('D:/devgames/MeridianSquad/Saved/GrenadePrototype01')


def run(name='throw01', park_at=None):
    world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    assert world
    pawn = u.GameplayStatics.get_player_pawn(world, 0)
    thrower = pawn.get_component_by_class(u.PrototypeGrenadeComponent)
    klass = u.load_class(None, '/Game/NextGenDestruction/Blueprints/Actors/BP_Grenade.BP_Grenade_C')
    field_class = u.load_class(None, '/Game/NextGenDestruction/Blueprints/Actors/BP_DestructionField.BP_DestructionField_C')
    report = {'samples': [], 'break_events': []}
    def prop_states():
        return [json.loads(c.get_state()) for a in u.GameplayStatics.get_all_actors_of_class(world, u.Actor)
                for c in [a.get_component_by_class(u.NGDPropComponent)] if c]
    report['props_before'] = prop_states()
    started = time.monotonic()
    stage = 0
    parked = False
    last = -1
    callbacks = []
    for actor in u.GameplayStatics.get_all_actors_of_class(world, u.Actor):
        for component in actor.get_components_by_class(u.GeometryCollectionComponent):
            component.set_notify_breaks(True)
            def make_callback(label):
                def on_break(event):
                    report['break_events'].append({'actor': label, 'elapsed': time.monotonic()-started})
                return on_break
            on_break = make_callback(actor.get_name())
            callbacks.append(on_break)
            component.on_chaos_break_event.add_callable(on_break)

    def tick(delta):
        nonlocal stage, last, parked
        try:
            elapsed = time.monotonic() - started
            if stage == 0 and elapsed > 1:
                pawn.probe_key('G', 1, True)
                stage = 1
            if stage == 1 and elapsed > 6:
                pawn.probe_key('G', 0, False)
                stage = 2
            if park_at is not None and not parked and elapsed > 2.4:
                grenades = u.GameplayStatics.get_all_actors_of_class(world, klass)
                if grenades:
                    grenade = grenades[-1]
                    movement = grenade.get_component_by_class(u.ProjectileMovementComponent)
                    movement.stop_movement_immediately()
                    movement.deactivate()
                    grenade.set_actor_location(u.Vector(*park_at), False, True)
                    report['blast_fixture'] = {'position': park_at, 'after_free_flight_seconds': elapsed}
                    parked = True
            if elapsed - last > .08:
                last = elapsed
                anim = pawn.get_component_by_class(u.SkeletalMeshComponent).get_anim_instance()
                montage = anim.get_current_active_montage()
                grenades = u.GameplayStatics.get_all_actors_of_class(world, klass)
                report['samples'].append({'elapsed': elapsed, 'state': json.loads(thrower.get_state()),
                    'busy': pawn.get_editor_property('bIsBusy'),
                    'montage': montage.get_name() if montage else None,
                    'montage_position': anim.montage_get_position(montage) if montage else None,
                    'fields': [{'position': str(a.get_actor_location()), 'scale': str(a.get_actor_scale3d())}
                               for a in u.GameplayStatics.get_all_actors_of_class(world, field_class)],
                    'grenades': [{'name': a.get_name(), 'location': str(a.get_actor_location()),
                                  'velocity': str(a.get_velocity())} for a in grenades]})
            if elapsed > 7:
                pawn.probe_key('G', 0, False)
                report['after'] = json.loads(thrower.get_state())
                report['props_after'] = prop_states()
                (OUT / (name + '.json')).write_text(json.dumps(report, indent=2))
                u.unregister_slate_post_tick_callback(handle)
        except Exception:
            pawn.probe_key('G', 0, False)
            report['error'] = traceback.format_exc()
            (OUT / (name + '.json')).write_text(json.dumps(report, indent=2))
            u.unregister_slate_post_tick_callback(handle)
    handle = u.register_slate_post_tick_callback(tick)
    return {'scheduled': name}
