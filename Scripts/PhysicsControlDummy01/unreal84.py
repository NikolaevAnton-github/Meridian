"""Focused physical contacts and clock evidence using verify02's native input driver."""
import importlib
import json
import time
import traceback
from pathlib import Path
import unreal as u
import unreal68
import verify02
from stage1_tools import state

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlDummy01/Worker'

def write(name, data):
    path = OUT / (name + '.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    assert not path.exists(), path
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')
    return data

def actors():
    w = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    return w, u.GameplayStatics.get_player_pawn(w, 0), u.GameplayStatics.get_actor_of_class(w, u.CombatProjectileWorld), u.GameplayStatics.get_actor_of_class(w, u.PhysicsControlDummy)

def sample(contacts=False):
    w, p, manager, dummy = actors()
    enemy = u.GameplayStatics.get_actor_of_class(w, u.EnemyPrototypeCharacter)
    rifle = p.get_component_by_class(u.CombatRifleComponent)
    pc = u.GameplayStatics.get_player_camera_manager(w, 0)
    result = dict(world_time=u.GameplayStatics.get_time_seconds(w), world_delta=u.GameplayStatics.get_world_delta_seconds(w),
        global_dilation=u.GameplayStatics.get_global_time_dilation(w), player_dilation=p.custom_time_dilation,
        manager_dilation=manager.custom_time_dilation, player_location=verify02.vec(p.get_actor_location()),
        player_velocity=verify02.vec(p.get_velocity()), camera=verify02.vec(pc.get_camera_location()),
        rifle=json.loads(rifle.get_rifle_state()), combat=json.loads(manager.get_combat_state()),
        dummy=json.loads(dummy.get_dummy_state(contacts)) if dummy else None,
        enemy=json.loads(enemy.get_enemy_state()) if enemy else None)
    if dummy:
        result['dummy']['control_tick_enabled'] = dummy.physics_control.is_component_tick_enabled()
        result['dummy']['actor_tick_enabled'] = dummy.is_actor_tick_enabled()
    return result

def action(operation, argument):
    if operation in ['performance','frame_rate','verify_status']:
        return unreal68.action(operation, argument)
    if operation == 'sample':
        result = sample(True)
        return write('sample-' + argument, result) if argument else result
    if operation == 'verify':
        assert verify02.RUN is None or verify02.RUN['done']
        importlib.reload(verify02)
        verify02.OUT = OUT
        verify02.sample = sample
        verify02.tick = tick
        result = verify02.start(argument)
        verify02.RUN['clock_start'] = json.loads(actors()[2].get_combat_state())['firing_clock']
        verify02.RUN['last_contacts'] = None
        if verify02.RUN['config'].get('freefall_clock'):
            w,p,manager,dummy = actors()
            assert manager.prepare_physics_dummy_freefall_probe()
            p.character_movement.set_movement_mode(u.MovementMode.MOVE_FLYING)
            p.character_movement.stop_movement_immediately()
            p.set_actor_location(u.Vector(29200,33000,1092),False,False)
        return result
    if operation == 'probe':
        w,p,manager,dummy = actors()
        before = p.get_component_by_class(u.CombatRifleComponent).get_rifle_state()
        result = json.loads(manager.probe_enemy(False, True) if argument.startswith('baseline') else manager.probe_physics_dummy())
        result['player_rifle_unchanged'] = before == p.get_component_by_class(u.CombatRifleComponent).get_rifle_state()
        return write('probe-' + argument, result)
    if operation in ['state','handoff','close']:
        result = state()
        if operation != 'state':
            assert not result['pie'] and not result['dirty_maps'] and not result['dirty_content'], result
            w = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
            result['dummy_leaks'] = [a.get_name() for a in u.GameplayStatics.get_all_actors_of_class(w,u.PhysicsControlDummy)]
            assert not result['dummy_leaks']
        write(operation + '-' + argument, result)
        if operation == 'close': u.SystemLibrary.quit_editor()
        return result
    raise ValueError(operation)

def tick(delta):
    r = verify02.RUN
    try:
        w,p,manager,dummy = actors()
        clock = json.loads(manager.get_combat_state())['firing_clock']
        now = clock - r['clock_start']
        while r['index'] < len(r['config']['events']) and now >= r['config']['events'][r['index']][0]:
            _,key,value = r['config']['events'][r['index']]
            if key == '@track':
                r['track'] = value
                r['fixed_view'] = None
            elif key == '@health': dummy.set_editor_property('health', value)
            elif key == '@drive_strength':
                dummy.set_editor_property('limb_angular_strength', value)
                manager.reset_targets()
            elif key == '@scale': manager.set_physics_preview_scale(value)
            elif key == '@shoot_when_asleep': r['sleep_fire'] = bool(value)
            elif key == '@speed': p.get_component_by_class(u.CombatRifleComponent).set_editor_property('bullet_speed', value)
            elif key == '@view':
                r['track'] = None
                r['fixed_view'] = value
            elif key == '@console': u.SystemLibrary.execute_console_command(w,value)
            elif key == '@enabled': manager.set_physics_dummy_enabled(bool(value))
            else:
                p.probe_key(key, abs(value), value > 0)
                if value > 0 and not key.startswith('Mouse'): r['held'].add(key)
                else: r['held'].discard(key)
            r['events'].append(dict(t=now,wall=time.monotonic()-r['wall'],key=key,value=value))
            r['index'] += 1
        if r.get('track') and dummy:
            camera = u.GameplayStatics.get_player_camera_manager(w,0)
            aim = dummy.get_physical_body_location(r['track'])
            u.GameplayStatics.get_player_controller(w,0).set_control_rotation(u.MathLibrary.find_look_at_rotation(camera.get_camera_location(),aim))
        elif r.get('fixed_view'):
            value = r['fixed_view']
            u.GameplayStatics.get_player_controller(w,0).set_control_rotation(u.Rotator(value[0],value[1],0))
        if r['config'].get('cost_only'):
            r['rows'].append(dict(t=now,wall=time.monotonic()-r['wall'],delta=delta,
                world_delta=u.GameplayStatics.get_world_delta_seconds(w),dummy_enabled=dummy is not None))
            if now >= r['config']['duration']: verify02.finish()
            return
        row = sample(False)
        if r.get('sleep_release') is not None and now >= r['sleep_release']:
            p.probe_key('LeftMouseButton', 0, False)
            r['sleep_release'] = None
        if r.get('sleep_fire') and row['dummy'] and row['dummy']['deaths'] and not any(b['awake'] for b in row['dummy']['bodies'].values()):
            p.probe_key('LeftMouseButton', 1, True)
            r['events'].append(dict(t=now, wall=time.monotonic()-r['wall'], key='actual_asleep_rifle_press',value=1))
            r['sleep_release'] = now + .07
            r['sleep_fire'] = False
        if row['dummy']:
            stamp = (row['dummy']['epoch'],row['dummy']['physical_hits'])
            if stamp != r['last_contacts']:
                row['dummy']['contacts'] = json.loads(dummy.get_dummy_state(True))['contacts']
                r['last_contacts'] = stamp
        row.update(t=now,wall=time.monotonic()-r['wall'],delta=delta,held=sorted(r['held']))
        r['rows'].append(row)
        if now >= r['config']['duration']: verify02.finish()
    except Exception:
        r['error'] = traceback.format_exc()
        verify02.finish()
