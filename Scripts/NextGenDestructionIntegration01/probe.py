"""Bounded PIE observations using the real player, input bindings and finite projectile world."""
import json
import time
import traceback
from pathlib import Path
import unreal as u

OUT = Path('D:/devgames/MeridianSquad/Saved/NextGenDestructionIntegration01/NGD-01/Candidate01')

def world():
    w = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    assert w and 'L_OpeningLobby_PainterStone01' in w.get_path_name()
    return w

def state():
    w = world()
    p = u.GameplayStatics.get_player_pawn(w, 0)
    rifle = p.get_component_by_class(u.CombatRifleComponent)
    projectiles = u.GameplayStatics.get_actor_of_class(w, u.CombatProjectileWorld)
    props = [a.get_component_by_class(u.NGDPropComponent) for a in u.GameplayStatics.get_all_actors_of_class(w, u.Actor)]
    targets = u.GameplayStatics.get_all_actors_of_class(w, u.CombatTarget)
    subsystem = u.find_object(w, 'NGDWorldSubsystem_0')
    changes = []
    if subsystem:
        for key, c in subsystem.latest_changes.items():
            changes.append(dict(id=str(key), revision=c.collision_revision, generation=c.reset_generation,
                                reason=str(c.reason), bounds=str(c.changed_bounds)))
    return dict(world=w.get_path_name(), player=p.get_path_name(), location=str(p.get_actor_location()),
                eyes=str(p.get_actor_eyes_view_point()), rifle=json.loads(rifle.get_rifle_state()),
                projectiles=json.loads(projectiles.get_combat_state()),
                props=[json.loads(c.get_state()) for c in props if c],
                changes=changes,
                witnesses=[dict(name=a.get_name(), health=a.health, hits=a.hits, location=str(a.get_actor_location())) for a in targets if a.actor_has_tag('NGD01Witness')])

def fragment_contacts(center):
    w = world()
    rows = []
    for dx in range(-160, 161, 20):
        for dy in range(-160, 161, 20):
            if abs(dx) < 65 and abs(dy) < 65:
                continue
            x, y = center[0] + dx, center[1] + dy
            h = json.loads(u.NGDTools.sweep(w, u.Vector(x, y, 85), u.Vector(x, y, 3), 5))
            if h['actor'].startswith('BP_BreakableObject'):
                rows.append(dict(x=x, y=y, hit=h))
    return rows

def snapshot(name):
    path = OUT / (name + '.json')
    assert not path.exists()
    value = state()
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')
    print(json.dumps(dict(file=name, shots=value['rifle']['shots'], hits=value['projectiles']['hits'], props=value['props'], witnesses=value['witnesses'])))
    return value

def witness(location=(-840, 1000, 95)):
    assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    editor = u.get_editor_subsystem(u.EditorActorSubsystem)
    assert not any(a.actor_has_tag('NGD01Witness') for a in editor.get_all_level_actors())
    a = editor.spawn_actor_from_class(u.CombatTarget, u.Vector(*location), u.Rotator(0, 90, 0))
    a.tags = ['NGD01Witness']
    a.set_actor_label('NGD01Witness_RemoveBeforeSave')
    a.set_folder_path('NGD01_DemoProps')
    print(a.get_path_name())

def shot(name, target, scan_center=None):
    """Schedule real input edges on separate editor ticks; collect completion before handoff."""
    w = world()
    path = OUT / (name + '.json')
    assert not path.exists()
    before = state()
    assert not before['rifle']['automatic'], 'This bounded probe expects the default semi-auto mode.'
    assert before['rifle']['magazine'] > 0 and not before['rifle']['reloading']
    started = time.monotonic()
    flags = {'aim': False, 'press': False, 'release': False, 'fragments': None}
    handle = None
    def tick(delta):
        nonlocal handle
        try:
            elapsed = time.monotonic() - started
            if elapsed >= .15 and not flags['aim']:
                assert u.NGDTools.aim_player(w, u.Vector(*target))
                flags['aim'] = True
                flags['aim_time'] = elapsed
                return
            if flags['aim'] and elapsed >= flags['aim_time'] + .15 and not flags['press']:
                flags['press'] = True
                flags['press_time'] = elapsed
                u.NGDTools.rifle_input(w, True)
                return
            if flags['press'] and elapsed >= flags['press_time'] + .15 and not flags['release']:
                flags['release'] = True
                u.NGDTools.rifle_input(w, False)
                return
            if scan_center and elapsed >= flags.get('press_time', 0) + .55 and flags['fragments'] is None:
                flags['fragments'] = fragment_contacts(scan_center)
            if elapsed >= 1.7:
                after = state()
                report = dict(before=before, after=after, target=target, elapsed=elapsed, fragments=flags['fragments'],
                              method='PlayerController mouse input -> EnhancedInput -> CombatRifleComponent -> finite CombatProjectileWorld sweep -> vendor BulletImpact')
                path.write_text(json.dumps(report, indent=2), encoding='utf-8')
                u.unregister_slate_post_tick_callback(handle)
        except Exception:
            u.NGDTools.rifle_input(w, False)
            path.write_text(json.dumps(dict(error=traceback.format_exc())), encoding='utf-8')
            u.unregister_slate_post_tick_callback(handle)
    handle = u.register_slate_post_tick_callback(tick)
    print('Scheduled bounded shot: ' + name)

def reset_during_field(name, target):
    """Reset during the vendor field lifetime, then observe for stale damage/callbacks."""
    w = world()
    path = OUT / (name + '.json')
    assert not path.exists()
    before = state()
    started = time.monotonic()
    flags = {'aim': False, 'pressed': False, 'reset': False}
    report = {'before': before, 'target': target}
    handle = None
    def finish():
        u.NGDTools.rifle_input(w, False)
        path.write_text(json.dumps(report, indent=2), encoding='utf-8')
        u.unregister_slate_post_tick_callback(handle)
    def tick(delta):
        try:
            elapsed = time.monotonic() - started
            if elapsed >= .15 and not flags['aim']:
                assert u.NGDTools.aim_player(w, u.Vector(*target))
                flags['aim'] = True
                flags['aim_time'] = elapsed
                return
            if flags['aim'] and not flags['pressed'] and elapsed >= flags['aim_time'] + .15:
                flags['pressed'] = True
                u.NGDTools.rifle_input(w, True)
                return
            current = state()
            if not flags['reset'] and any(p['live_fields'] for p in current['props']):
                report['with_live_field'] = current
                u.NGDTools.rifle_input(w, False)
                u.GameplayStatics.get_actor_of_class(w, u.CombatProjectileWorld).reset_targets()
                report['immediate_reset'] = state()
                flags['reset'] = True
                flags['reset_at'] = elapsed
                return
            if flags['reset'] and elapsed > flags['reset_at'] + 1.5:
                report['after'] = current
                report['passed'] = all(p['break_events'] == 0 and p['delivered_hits'] == 0 and p['live_fields'] == 0 and not p['root_broken'] for p in current['props'])
                finish()
            elif elapsed > 5:
                report['error'] = 'No live vendor field observed within the bounded shot.'
                report['after'] = current
                finish()
        except Exception:
            report['error'] = traceback.format_exc()
            finish()
    handle = u.register_slate_post_tick_callback(tick)
    print('Scheduled live-field reset: ' + name)
