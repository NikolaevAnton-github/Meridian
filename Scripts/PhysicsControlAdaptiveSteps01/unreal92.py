"""Reuse predecessor actions, actual input, skin audits and per-frame observations."""
import json
import time
from pathlib import Path
import unreal as u
import unreal97
import unreal87

OUT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())) / 'Saved/CombatSlice01/PhysicsControlAdaptiveSteps01/Worker'

def action(operation, argument):
    unreal97.OUT = OUT
    result = unreal97.action(operation, argument)
    unreal87.balance_tick_impl = adaptive_tick
    if operation == 'verify':
        r = unreal87.verify02.RUN
        r['capture_start_monotonic'] = r['wall']
    return result

def adaptive_tick(delta):
    r = unreal87.verify02.RUN
    if r['config'].get('block_landing') and not r.get('landing_blocked'):
        w,p,m,ds = unreal87.unreal85.actors()
        d = unreal87.unreal85.selected(ds)
        if d:
            before = json.loads(d.get_dummy_state(False))
            if before['step']['phase'] == 'SWING':
                assert d.probe_balance_environment('step_target_block')
                r['landing_blocked'] = True
                r['events'].append(dict(t=json.loads(m.get_combat_state())['firing_clock']-r['clock_start'],
                    wall=time.monotonic()-r['wall'], key='block_landing', target=before['step']['destination']))
    unreal97.recovery_tick(delta)
    if r.get('done'):
        path = OUT / (r['config']['name'] + '-clock.json')
        with path.open('x', encoding='utf-8') as stream:
            json.dump(dict(recording_monotonic_start=r['capture_start_monotonic']), stream, indent=2)
