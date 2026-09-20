"""Focused recovery observations using the existing Epic/native-input harness."""
import json
import time
from pathlib import Path
import unreal as u
import unreal91
import unreal89
import unreal87

OUT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())) / 'Saved/CombatSlice01/PhysicsControlRecoverability01/Worker'

def recovery_tick(delta):
    r=unreal87.verify02.RUN
    w,p,m,ds=unreal87.unreal85.actors()
    d=unreal87.unreal85.selected(ds)
    now=json.loads(m.get_combat_state())['firing_clock']-r['clock_start']
    for event in r.get('recovery_extra',[]):
        if event.get('done') or now<event['t'] or d is None:continue
        if event['key']=='@sweep_leg':
            value=event['value']
            bone=value.get('bone','calf_l') if isinstance(value,dict) else 'calf_l'
            strength=value['strength'] if isinstance(value,dict) else value
            direction=d.get_physical_body_location(bone.replace('_l','_r'))-d.get_physical_body_location(bone)
            direction.z=0
            impulse=u.MathLibrary.normal(direction)*strength
            d.apply_external_disturbance(impulse,d.get_physical_body_location(bone),bone)
            event['applied_to']=bone
            event['impulse']=[impulse.x,impulse.y,impulse.z]
        elif event['key']=='@tune':
            for key,value in event['value'].items():d.set_editor_property(key,value)
        event['done']=True
        r['events'].append(dict(t=now,wall=time.monotonic()-r['wall'],**{k:v for k,v in event.items() if k not in ['t','done']}))
    if d is None:
        unreal87.unreal85.tick(delta)
    else:
        unreal91.legs_tick(delta)
        current=json.loads(d.get_dummy_state(False))
        if current['balance']['state']=='STANDING' and current['step']['completed'] and current['balance']['since_disturbance']>.5:
            key=f"{current['epoch']}-{current['step']['completed']}-{current['balance']['get_ups']}"
            if key not in r.setdefault('recovery_snapshots',[]):
                r['recovery_snapshots'].append(key)
                unreal89.write(r['config']['name']+'-recovery-pose-'+key,dict(runtime=json.loads(d.get_dummy_state(True)),
                    skeleton={str(d.body.get_bone_name(i)):unreal91.transform(d.body.get_socket_transform(d.body.get_bone_name(i)))
                              for i in range(d.body.get_num_bones())},skin=json.loads(u.PhysicsControlRecoveryLibrary.audit_skin(d.body))))

def action(operation, argument):
    unreal91.OUT = unreal89.OUT = unreal87.OUT = OUT
    unreal87.balance_tick_impl=recovery_tick
    if operation=='verify':
        config=json.loads(argument)
        extra=[dict(t=e[0],key=e[1],value=e[2]) for e in config['events'] if e[1] in ['@sweep_leg','@tune']]
        config['events']=[e for e in config['events'] if e[1] not in ['@sweep_leg','@tune']]
        result=unreal91.action(operation,json.dumps(config))
        unreal87.verify02.RUN['recovery_extra']=extra
        return result
    if operation == 'audit_asset':
        asset = u.load_asset('/Game/Development/PhysicsControlRecovery01/PA_Manny_Recovery01')
        report = json.loads(u.PhysicsControlRecoveryLibrary.audit_asset(asset))
        unreal89.write(argument, report)
        return report
    return unreal91.action(operation, argument)
