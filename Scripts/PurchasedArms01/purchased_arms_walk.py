"""Task-local configuration for the unchanged lobby input/collision verifier."""
import json
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_run_name = globals().get('_run_name', 'Acceptance03')
_scope = globals().get('_scope', 'full')
OUT = ROOT / 'Saved/PurchasedArms01/Worker' / _run_name
MAP = '/Game/Maps/L_OpeningLobby_PainterStone01'
_module = None


def configuration(root):
    OUT.mkdir(parents=True, exist_ok=True)
    plan = [('wait', 'spawn', 1), ('mouse', 'mouse_yaw', 30, 0),
        ('mouse', 'mouse_pitch', 0, 20), ('look', 'restore_look', 0, 0),
        ('move', 'clear_entrance', -2700, -105), ('move', 'wall_approach', -2700, 0),
        ('hold', 'entrance_wall_collision', 'D', 2.2), ('move', 'lane_align', -2700, 465),
        ('move', 'lane_inbound', -1900, 465), ('move', 'axis_align', -1900, 0),
        ('move', 'elevator_approach', 2850, 0), ('move', 'walk_back', 0, 0),
        ('capture', 'idle', .6), ('aim', 'aim_press', True), ('aim', 'aim_release', False),
        ('reload', 'reload_hip', 0, False, False), ('aim', 'aim_before_reload', True),
        ('reload', 'reload_aimed', 1, True, False), ('reload', 'reload_queue_aim', 0, True, False),
        ('reload', 'reload_moving_aimed', 1, False, True), ('aim', 'final_release', False),
        ('unsupported', 'unsupported_keys'), ('move', 'return_to_test_origin', 0, 0),
        ('capture', 'recovered', .6)]
    if _scope == 'actions':
        plan = [('wait', 'settle_existing_walkthrough', .6), ('move', 'actions_origin', 0, 0)] + plan[12:-2] + [
            ('move', 'return_before_hip_moving', 0, 0), ('reload', 'reload_hip_moving', 0, False, True),
            ('move', 'return_to_test_origin', 0, 0), ('capture', 'recovered', .6)]
    elif _scope == 'views':
        plan = plan[:4] + [('move', 'clear_entrance', -2700, -105),
            ('move', 'lane_align', -2700, 465), ('move', 'lane_inbound', -1900, 465),
            ('move', 'axis_align', -1900, 0), ('move', 'view_origin', 0, 0),
            ('capture', 'idle', .6), ('move', 'walk_back', -180, 0),
            ('move', 'return_to_view_origin', 0, 0), ('capture', 'recovered', .6)]
    elif _scope == 'correction':
        plan = plan[:4] + [('move', 'clear_entrance', -2700, -105),
            ('move', 'lane_align', -2700, 465), ('move', 'lane_inbound', -1900, 465),
            ('move', 'axis_align', -1900, 0), ('move', 'view_origin', 0, 0),
            ('steer', 'diagonal_turn_and_moving_aim'), ('look', 'restore_after_steer', 0, 0),
            ('move', 'return_after_steer', 0, 0)] + plan[12:-2] + [
            ('move', 'return_before_hip_moving', 0, 0), ('reload', 'reload_hip_moving', 0, False, True),
            ('move', 'return_to_test_origin', 0, 0), ('capture', 'recovered', .6)]
    (OUT / 'route-contract.json').write_text(json.dumps(dict(map=MAP, plan=plan,
        verifier='Unchanged Scripts/OpeningLobby/verify_lobby.py with task-local configuration and scoped action extension'), indent=2))
    return dict(map=MAP, out=OUT, plan=plan, view_plan=plan, refresh_held_input=True,
        collision_surfaces={'entrance_wall_collision':560}, contact_tolerance_cm=3)


def start(run_name='Acceptance03', scope='full'):
    global _module, _run_name, _scope
    assert run_name.replace('-', '').isalnum() and scope in ['full', 'actions', 'views', 'correction']
    _run_name, _scope = run_name, scope
    assert _module is None or _module._run is None or _module._run.done
    path = ROOT / 'Scripts/OpeningLobby/verify_lobby.py'
    source = path.read_text()
    selector = "'layout03_verification' if revision == 'Layout03' else 'layout02_verification'"
    assert source.count(selector) == 1
    source = source.replace(selector, "'purchased_arms_walk'")
    _module = types.ModuleType('purchased_arms_existing_verifier')
    exec(compile(source, str(path), 'exec'), _module.__dict__)
    module = _module
    result = module.start(revision='Layout03')
    # The verifier reloads this configuration module while constructing its run.
    _module = module
    return result


def status():
    result = _module.status() if _module else {'done':True,'passed':False,'error':'Not started'}
    return {k:v for k,v in result.items() if k not in ['initial','events']}
