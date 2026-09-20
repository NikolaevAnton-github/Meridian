"""Extend the existing focused recorder only with stepping observations/actions."""
import json
import time
from pathlib import Path
import unreal as u
import unreal87
from stage1_tools import state

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlStepping01/Worker'
unreal87.OUT = OUT
_original_tick = getattr(unreal87, '_msq89_original_tick', unreal87.balance_tick_impl)
unreal87._msq89_original_tick = _original_tick

def write(name, value):
    path = OUT / (name + '.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')
    return value

def focused_tick(delta):
    r = unreal87.verify02.RUN
    w, p, m, ds = unreal87.unreal85.actors()
    d = unreal87.unreal85.selected(ds)
    if d is None:
        unreal87.unreal85.tick(delta)
        return
    now = json.loads(m.get_combat_state())['firing_clock'] - r['clock_start']
    for event in r.get('step_extra', []):
        if event.get('done') or now < event['t']:
            continue
        assert event['key'] == '@lateral'
        up = d.get_physical_body_location('spine_05') - d.get_physical_body_location('pelvis')
        left = d.get_physical_body_location('clavicle_l') - d.get_physical_body_location('clavicle_r')
        front = u.MathLibrary.cross_vector_vector(up, left)
        side = u.MathLibrary.normal(u.Vector(-front.y, front.x, 0))
        impulse = side * event['value']
        d.apply_external_disturbance(impulse, d.get_physical_body_location('spine_05'), 'spine_05')
        event['done'] = True
        r['events'].append(dict(t=now,wall=time.monotonic()-r['wall'],key='body_relative_lateral',impulse=[impulse.x,impulse.y,impulse.z]))
    before = json.loads(d.get_dummy_state(False)) if d else None
    if before and before['step']['phase'] == 'SWING':
        mode = r['config'].get('during_step')
        if mode and not r.get('during_step_done'):
            r['during_step_done'] = True
            if mode == 'hit':
                d.apply_external_disturbance(u.Vector(0,-1300,0), d.get_physical_body_location('spine_05'), 'spine_05')
            elif mode == 'leg':
                bone = before['step']['support_foot'].replace('foot', 'calf')
                d.apply_external_disturbance(u.Vector(-700,0,0), d.get_physical_body_location(bone), bone)
            elif mode == 'kill':
                p.probe_key('LeftMouseButton',1,True)
                r['release_at'] = now + .4
            elif mode == 'reset':
                p.probe_key('F6',1,True)
                p.probe_key('F6',0,False)
            elif mode == 'slow':
                m.set_physics_preview_scale(.25)
            elif mode == 'remove_floor':
                assert d.probe_balance_environment('remove_floor')
            else:
                raise ValueError(mode)
            r['events'].append(dict(t=now,wall=time.monotonic()-r['wall'],key='during_step_'+mode,step=before['step']))
    _original_tick(delta)
    if r.get('done') or not r['config'].get('capture_skin') or not d:
        return
    current = json.loads(d.get_dummy_state(False))
    b, s = current['balance'], current['step']
    if b['state'] == 'STANDING':
        label = 'getup' if b['get_ups'] else 'stepped' if s['completed'] else 'reset'
        if not r.get('skin_'+label):
            result = json.loads(u.PhysicsControlRecoveryLibrary.audit_skin(d.body))
            result['runtime'] = current
            write(r['config']['name']+'-skin-'+label, result)
            r['skin_'+label] = True

unreal87.balance_tick_impl = focused_tick

def action(operation, argument):
    if operation == 'verify':
        config = json.loads(argument)
        custom = [dict(t=e[0],key=e[1],value=e[2]) for e in config['events'] if e[1] == '@lateral']
        config['events'] = [e for e in config['events'] if e[1] != '@lateral']
        result = unreal87.action(operation, json.dumps(config))
        unreal87.verify02.RUN['step_extra'] = custom
        d = unreal87.unreal85.selected(unreal87.unreal85.actors()[3])
        if config.get('turned'):
            assert d.probe_balance_environment('turn90')
        for key, value in config.get('tuning', {}).items():
            d.set_editor_property(key, value)
        if config.get('reset_tuning'):
            d.reset_dummy()
            write(config['name']+'-tuning', dict(tuning=config['tuning'], runtime=json.loads(d.get_dummy_state(True))))
        return result
    if operation == 'inspect_skeleton':
        d = unreal87.unreal85.selected(unreal87.unreal85.actors()[3])
        return write(argument, dict(runtime=json.loads(d.get_dummy_state(True)),
            bones=[dict(name=str(d.body.get_bone_name(i)), transform=str(d.body.get_socket_transform(d.body.get_bone_name(i))))
                   for i in range(d.body.get_num_bones())]))
    return unreal87.action(operation, argument)
