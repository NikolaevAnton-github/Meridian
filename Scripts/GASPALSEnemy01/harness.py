"""Rifle commands added to the existing focused GASP recorder and observers."""
import json
from pathlib import Path
import unreal as u
from Scripts.GASPEnemyFoundation01 import unreal98

OUT = Path('D:/devgames/MeridianSquad/Saved/CombatSlice01/GASPALSEnemy01')


def sample(contacts=False):
    row = unreal98.sample(contacts)
    world, player, manager, fixtures = unreal98.unreal87.unreal85.actors()
    row['enemy_rifles'] = []
    for fixture in fixtures:
        state = json.loads(fixture.get_dummy_state(False))
        mesh = fixture.body
        rifle = fixture.rifle
        hand = mesh.get_socket_location('hand_l')
        grip = rifle.get_socket_location('HandIK_Left')
        barrel=rifle.get_right_vector()
        direction=u.Vector(*state['gasp']['aim_direction'])
        anim=mesh.get_anim_instance()
        import math
        row['enemy_rifles'].append(dict(name=fixture.get_name(),profile=fixture.reaction_profile,
            gasp=state['gasp'], left_grip_gap_cm=(hand-grip).length(),
            barrel_direction=[barrel.x,barrel.y,barrel.z],
            aim_error_degrees=math.degrees(math.acos(max(-1,min(1,u.MathLibrary.dot_vector_vector(barrel,direction))))),
            root_relative_aim=[anim.get_editor_property('AO').x,anim.get_editor_property('AO').y],
            rifle_transform=str(rifle.get_world_transform())))
    row['counts']['enemy_command_controllers'] = len(u.GameplayStatics.get_all_actors_of_class(world,u.GASPEnemyCommandController))
    return row


def tick(delta):
    runner = unreal98.unreal87.verify02.RUN
    world, player, manager, fixtures = unreal98.unreal87.unreal85.actors()
    now = json.loads(manager.get_combat_state())['firing_clock'] - runner['clock_start']
    for event in runner.get('rifle_events', []):
        if not event.get('done') and now >= event['t']:
            u.SystemLibrary.execute_console_command(world, 'msq.EnemyRifle '+event['command'])
            event['done'] = True
            runner['events'].append(dict(t=now,key='@rifle',value=event['command']))
    unreal98.tick(delta)


def action(operation, argument=''):
    unreal98.OUT = OUT
    if operation == 'verify':
        config = json.loads(argument)
        commands = [dict(t=e[0],command=e[2]) for e in config['events'] if e[1]=='@rifle']
        config['events'] = [e for e in config['events'] if e[1]!='@rifle']
        result = unreal98.action(operation,json.dumps(config))
        unreal98.unreal87.verify02.RUN['rifle_events'] = commands
    else:
        result = unreal98.action(operation,argument)
    if operation in ['verify','verify_status']:
        unreal98.unreal87.unreal85.sample = sample
    unreal98.unreal87.balance_tick_impl = tick
    return result
