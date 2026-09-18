"""Continuous evaluated recovery samples; never pause PIE or take high-res shots."""
import json
import time
from pathlib import Path
import unreal as u
ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/PurchasedArms02/Worker'
RUN = None

def start(name):
    global RUN
    assert RUN is None or RUN['done']
    world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    pawn = u.GameplayStatics.get_player_pawn(world, 0)
    assert pawn
    path = OUT / (name + '.json')
    assert not path.exists()
    RUN = dict(name=name, rows=[], done=False, phase=0, world=world, pawn=pawn,
        start=u.GameplayStatics.get_time_seconds(world), wall=time.monotonic())
    RUN['handle'] = u.register_slate_post_tick_callback(tick)
    return {'started': name}

def status():
    return {k: RUN[k] for k in ['name', 'done', 'phase']} | {'samples': len(RUN['rows'])}

def tick(delta):
    r = RUN
    p = r['pawn']
    try:
        now = u.GameplayStatics.get_time_seconds(r['world']) - r['start']
        if r['phase'] == 0:
            p.probe_key('W', 1, True)
            if 'aim' in r['name']:
                p.probe_key('RightMouseButton', 1, True)
            r['phase'] = 1
        if r['phase'] == 1 and now >= 2:
            p.probe_key('R', 1, True)
            r['phase'] = 2
        if r['phase'] == 2 and now >= 2.08:
            p.probe_key('R', 0, False)
            r['phase'] = 3
        state = json.loads(p.get_probe_state())
        camera = u.GameplayStatics.get_player_camera_manager(r['world'], 0)
        transform = u.Transform(camera.get_camera_location(), camera.get_camera_rotation())
        mesh = p.get_component_by_class(u.SkeletalMeshComponent)
        state.update(t=now, wall=time.monotonic()-r['wall'], delta=delta,
            speed=p.get_velocity().length(), position=str(p.get_actor_location()),
            bones={n: str(transform.inverse_transform_location(mesh.get_socket_location(n))) for n in ['ik_hand_gun','hand_r','hand_l']})
        r['rows'].append(state)
        if now >= 10:
            for key in ['W','R','RightMouseButton']:
                p.probe_key(key, 0, False)
            r['done'] = True
            u.unregister_slate_post_tick_callback(r['handle'])
            (OUT / (r['name'] + '.json')).write_text(json.dumps(r['rows'], indent=2), encoding='utf-8')
    except Exception:
        import traceback
        r['done'] = True
        u.unregister_slate_post_tick_callback(r['handle'])
        (OUT / (r['name'] + '-error.txt')).write_text(traceback.format_exc())
