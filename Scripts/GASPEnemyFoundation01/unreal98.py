"""GASP commands layered onto the retained MSQ-92 focused observer."""
import json
import sys
import time
from pathlib import Path
import unreal as u

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/CombatSlice01/GASPEnemyFoundation01/Worker'
for folder in ['OpeningLobby','PurchasedArms02','CombatFoundation01','PhysicsControlDummy01',
               'PhysicsControlVariants01','PhysicsControlBalance01','PhysicsControlStepping01',
               'PhysicsControlLegPose01','PhysicsControlRecoverability01','PhysicsControlAdaptiveSteps01']:
    sys.path.insert(0, str(ROOT / 'Scripts' / folder))
import unreal92
import unreal87
from Scripts.GASPEnemyFoundation01 import pilot98


def sample(contacts=False):
    row = unreal87.unreal85._gasp98_original_sample(contacts)
    world, player, manager, fixtures = unreal87.unreal85.actors()
    foundations = u.GameplayStatics.get_all_actors_with_tag(world, 'MSQ98_GASPEnemy')
    row['counts']['gasp_foundation'] = len(foundations)
    row['counts']['orphan_foundation'] = sum(p.get_owner() not in fixtures for p in foundations)
    row['fixture_classes'] = sorted(set(p.get_class().get_name() for p in fixtures))
    return row


def tick(delta):
    r = unreal87.verify02.RUN
    world, player, manager, fixtures = unreal87.unreal85.actors()
    now = json.loads(manager.get_combat_state())['firing_clock'] - r['clock_start']
    for event in r.get('gasp_events', []):
        if event.get('done') or now < event['t']:
            continue
        fixture = unreal87.unreal85.selected(fixtures)
        assert isinstance(fixture, u.GASPEnemyFixture)
        value = event['value']
        if event['key'] == '@move':
            fixture.set_movement_command(u.Vector(*value['direction']), value.get('walk', True))
        elif event['key'] == '@pilot_reset':
            fixture.reset_dummy()
        elif event['key'] == '@arm_trunk':
            hand = fixture.get_physical_body_location('hand_l')
            chest = fixture.get_physical_body_location('spine_03')
            fixture.apply_external_disturbance(u.MathLibrary.normal(chest-hand)*float(value), hand, 'hand_l')
        event['done'] = True
        r['events'].append(dict(t=now, wall=time.monotonic()-r['wall'], key=event['key'], value=value))
    unreal92.adaptive_tick(delta)


def action(operation, argument=''):
    unreal92.OUT = OUT
    if operation == 'prepare':
        config = json.loads(argument)
        return pilot98.run('spawn') if config.get('pilot', True) else {'rollout': True}
    if operation == 'verify':
        if not hasattr(unreal87.unreal85, '_gasp98_original_sample'):
            unreal87.unreal85._gasp98_original_sample = unreal87.unreal85.sample
        unreal87.unreal85.sample = sample
        config = json.loads(argument)
        custom = ['@move','@pilot_reset','@arm_trunk']
        events = [dict(t=e[0], key=e[1], value=e[2]) for e in config['events'] if e[1] in custom]
        config['events'] = [e for e in config['events'] if e[1] not in custom]
        result = unreal92.action(operation, json.dumps(config))
        unreal87.verify02.RUN['gasp_events'] = events
        unreal87.balance_tick_impl = tick
        return result
    result = unreal92.action(operation, argument)
    # The predecessor restores its observer on every status poll; retain the
    # command layer for the entire recording, including after that poll.
    unreal87.balance_tick_impl = tick
    return result
