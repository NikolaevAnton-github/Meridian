"""Add only leg geometry observations to the established MSQ-89 recorder."""
import json
from pathlib import Path
import unreal as u
import unreal89
import unreal87

OUT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())) / 'Saved/CombatSlice01/PhysicsControlLegPose01/Worker'
unreal89.OUT = unreal87.OUT = OUT

def transform(t):
    return dict(p=[t.translation.x, t.translation.y, t.translation.z],
                q=[t.rotation.x, t.rotation.y, t.rotation.z, t.rotation.w])

def legs_tick(delta):
    r = unreal87.verify02.RUN
    d = unreal87.unreal85.selected(unreal87.unreal85.actors()[3])
    current = json.loads(d.get_dummy_state(False))
    if r['config'].get('infeasible_stance') and current['step']['phase'] == 'SWING' and not r.get('infeasible_done'):
        assert d.probe_balance_environment('step_infeasible_stance')
        r['infeasible_done'] = True
        r['events'].append(dict(t=json.loads(unreal87.unreal85.actors()[2].get_combat_state())['firing_clock']-r['clock_start'],
                                key='infeasible_stance_target',height_offset_cm=40))
    key = f"{current['epoch']}-{current['step']['completed']}-{current['balance']['get_ups']}"
    if current['balance']['state'] == 'STANDING' and current['balance']['instability'] == 0 and key not in r.setdefault('leg_snapshots', []):
        r['leg_snapshots'].append(key)
        unreal89.write(r['config']['name']+'-pose-'+key, dict(runtime=json.loads(d.get_dummy_state(True)),
            skeleton={str(d.body.get_bone_name(i)): transform(d.body.get_socket_transform(d.body.get_bone_name(i)))
                      for i in range(d.body.get_num_bones())},
            skin=json.loads(u.PhysicsControlRecoveryLibrary.audit_skin(d.body))))
    # Add the measured visible bone origins before the original recorder serializes its last row.
    original_sample = unreal87.unreal85.sample
    def sample(contacts=False):
        row = original_sample(contacts)
        row['leg_bones'] = {bone: transform(d.body.get_socket_transform(bone)) for bone in
            ['pelvis', 'thigh_l', 'calf_l', 'foot_l', 'ball_l', 'thigh_r', 'calf_r', 'foot_r', 'ball_r']}
        return row
    unreal87.unreal85.sample = sample
    try:
        unreal89.focused_tick(delta)
    finally:
        unreal87.unreal85.sample = original_sample

unreal87.balance_tick_impl = legs_tick

def action(operation, argument):
    unreal89.OUT = unreal87.OUT = OUT
    return unreal89.action(operation, argument)
