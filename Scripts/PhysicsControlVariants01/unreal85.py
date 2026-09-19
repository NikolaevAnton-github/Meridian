"""Focused MSQ-85 evidence; native input and capture are the retained MSQ-84 tools."""
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
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlVariants01/Worker'

def write(name, value):
    p = OUT / (name + '.json')
    p.parent.mkdir(parents=True, exist_ok=True)
    assert not p.exists(), p
    p.write_text(json.dumps(value, indent=2), encoding='utf-8')
    return value

def actors():
    w = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    p = u.GameplayStatics.get_player_pawn(w, 0)
    m = u.GameplayStatics.get_actor_of_class(w, u.CombatProjectileWorld)
    ds = sorted(u.GameplayStatics.get_all_actors_of_class(w, u.PhysicsControlDummy), key=lambda d: d.get_name())
    return w, p, m, ds

def profile(d):
    return d.reaction_profile if hasattr(d, 'reaction_profile') else 0

def selected(ds):
    r = verify02.RUN
    number = r.get('profile', r['config'].get('profile', 1)) if r else 1
    return next((d for d in ds if profile(d) == number), ds[0] if ds else None)

def sample(contacts=False):
    w, p, m, ds = actors()
    d = selected(ds)
    pc = u.GameplayStatics.get_player_camera_manager(w, 0)
    rifle = p.get_component_by_class(u.CombatRifleComponent)
    assembly = [p, *p.get_attached_actors(reset_array=True, recursively_include_attached_actors=True)]
    anim = []
    for a in assembly:
        for mesh in a.get_components_by_class(u.SkeletalMeshComponent):
            inst = mesh.get_anim_instance()
            montage = inst.get_current_active_montage() if inst else None
            anim.append(dict(actor=a.get_name(), custom_dilation=a.custom_time_dilation, mesh=mesh.get_name(),
                rate=mesh.global_anim_rate_scale, montage=montage.get_name() if montage else None,
                position=inst.montage_get_position(montage) if montage else None))
    result = dict(world_time=u.GameplayStatics.get_time_seconds(w), world_delta=u.GameplayStatics.get_world_delta_seconds(w),
        global_dilation=u.GameplayStatics.get_global_time_dilation(w), player_dilation=p.custom_time_dilation,
        manager_dilation=m.custom_time_dilation, player_location=verify02.vec(p.get_actor_location()),
        player_velocity=verify02.vec(p.get_velocity()), camera=verify02.vec(pc.get_camera_location()),
        rifle=json.loads(rifle.get_rifle_state()), combat=json.loads(m.get_combat_state()),
        dummy=json.loads(d.get_dummy_state(contacts)) if d else None, animations=anim,
        fixtures=[dict(name=x.get_name(),profile=profile(x),health=x.health,hits=x.physical_hits,deaths=x.deaths,
            location=verify02.vec(x.get_actor_location())) for x in ds],
        counts={name:len(u.GameplayStatics.get_all_actors_of_class(w,cls)) for name,cls in
            [('dummy',u.PhysicsControlDummy),('legacy',u.EnemyPrototypeCharacter),('manager',u.CombatProjectileWorld),('controller',u.PlayerController)]})
    return result

def action(operation, argument):
    if operation in ['performance','frame_rate','verify_status']: return unreal68.action(operation, argument)
    if operation in ['state','handoff','close']:
        result = state()
        if operation != 'state':
            assert not result['pie'] and not result['dirty_maps'] and not result['dirty_content'], result
            w = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
            result['leaks'] = [a.get_name() for cls in [u.PhysicsControlDummy,u.CombatProjectileWorld,u.EnemyPrototypeCharacter]
                               for a in u.GameplayStatics.get_all_actors_of_class(w,cls)]
            assert not result['leaks']
        write(operation + '-' + argument, result)
        if operation == 'close': u.SystemLibrary.quit_editor()
        return result
    if operation == 'sample': return write('sample-' + argument, sample(True)) if argument else sample(True)
    if operation == 'timing':
        config = json.loads(argument)
        return write(config.pop('name'), json.loads(actors()[2].probe_timing(json.dumps(config))))
    if operation == 'verify':
        assert verify02.RUN is None or verify02.RUN['done']
        importlib.reload(verify02)
        verify02.OUT = OUT
        verify02.sample = sample
        verify02.tick = tick
        result = verify02.start(argument)
        r = verify02.RUN
        r['clock_start'] = json.loads(actors()[2].get_combat_state())['firing_clock']
        r['last_contacts'] = None
        return result
    if operation == 'probe': return write('probe-' + argument, json.loads(actors()[2].probe_physics_dummy()))
    if operation == 'overrides': return write('overrides-' + argument, json.loads(actors()[2].probe_physics_preview_overrides()))
    raise ValueError(operation)

def tick(delta):
    r = verify02.RUN
    try:
        w,p,m,ds = actors()
        d = selected(ds)
        rifle = p.get_component_by_class(u.CombatRifleComponent)
        now = json.loads(m.get_combat_state())['firing_clock'] - r['clock_start']
        while r['index'] < len(r['config']['events']) and now >= r['config']['events'][r['index']][0]:
            _,key,value = r['config']['events'][r['index']]
            if key == '@track': r['track'] = value; r['fixed_view'] = None
            elif key == '@profile': r['profile'] = value; d = selected(ds)
            elif key == '@scale': m.set_physics_preview_scale(value)
            elif key == '@enabled': m.set_physics_dummy_enabled(bool(value))
            elif key == '@view': r['track'] = None; r['fixed_view'] = value
            elif key == '@console': u.SystemLibrary.execute_console_command(w,value)
            elif key == '@speed': rifle.set_editor_property('bullet_speed',value)
            elif key == '@ammo': assert rifle.probe_ammo(*value)
            elif key == '@reload': assert rifle.request_reload(bool(value))
            elif key == '@cancel': rifle.cancel_reload()
            elif key == '@duplicate': rifle.probe_duplicate_notify()
            elif key == '@sleep_fire': r['sleep_fire'] = bool(value)
            else:
                p.probe_key(key,abs(value),value>0)
                if value>0 and not key.startswith('Mouse'): r['held'].add(key)
                else: r['held'].discard(key)
            r['events'].append(dict(t=now,wall=time.monotonic()-r['wall'],key=key,value=value))
            r['index'] += 1
        if r.get('track') and d:
            camera=u.GameplayStatics.get_player_camera_manager(w,0)
            aim=d.get_physical_body_location(r['track'])
            u.GameplayStatics.get_player_controller(w,0).set_control_rotation(u.MathLibrary.find_look_at_rotation(camera.get_camera_location(),aim))
        elif r.get('fixed_view'):
            u.GameplayStatics.get_player_controller(w,0).set_control_rotation(u.Rotator(*r['fixed_view'],0))
        for key in r['held']:
            if key == 'RightMouseButton': p.probe_key(key,1,True)
        if r['config'].get('cost_only'):
            r['rows'].append(dict(t=now,wall=time.monotonic()-r['wall'],delta=delta,enabled=len(ds)))
            if now >= r['config']['duration']: verify02.finish()
            return
        row = sample(False)
        if r.get('sleep_release') is not None and now >= r['sleep_release']:
            p.probe_key('LeftMouseButton',0,False); r['sleep_release']=None
        if r.get('sleep_fire') and row['dummy'] and row['dummy']['deaths'] and not any(b['awake'] for b in row['dummy']['bodies'].values()):
            p.probe_key('LeftMouseButton',1,True)
            r['events'].append(dict(t=now,wall=time.monotonic()-r['wall'],key='actual_asleep_rifle_press',value=1))
            r['sleep_release']=now+.07; r['sleep_fire']=False
        if row['dummy']:
            stamp=(row['dummy']['name'],row['dummy']['epoch'],row['dummy']['physical_hits'])
            if stamp != r['last_contacts']:
                row['dummy']['contacts']=json.loads(selected(actors()[3]).get_dummy_state(True))['contacts']
                r['last_contacts']=stamp
        row.update(t=now,wall=time.monotonic()-r['wall'],delta=delta,held=sorted(r['held']))
        r['rows'].append(row)
        if now >= r['config']['duration']: verify02.finish()
    except Exception:
        r['error']=traceback.format_exc()
        verify02.finish()
