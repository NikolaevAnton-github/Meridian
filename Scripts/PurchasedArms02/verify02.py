"""Task-scoped continuous checks through the existing native input probe."""
import json
import time
import traceback
from pathlib import Path
import unreal as u

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/PurchasedArms02/Worker'
RUN = None

def vec(v):
    return [v.x,v.y,v.z]

def transform(t):
    return {'p':vec(t.translation),'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'scale':vec(t.scale3d)}

def sample():
    w = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    p = u.GameplayStatics.get_player_pawn(w,0)
    result = json.loads(p.get_probe_state())
    camera = u.GameplayStatics.get_player_camera_manager(w,0)
    ct = u.Transform(camera.get_camera_location(), camera.get_camera_rotation())
    mesh = p.mesh
    parts = []
    actors = [p, *p.get_attached_actors(reset_array=True, recursively_include_attached_actors=True)]
    for a in actors:
        for c in a.get_components_by_class(u.PrimitiveComponent):
            if isinstance(c,u.CapsuleComponent): continue
            item = {'actor':a.get_name(),'component':c.get_name(),'visible':c.is_visible(),
                'actor_hidden':a.get_editor_property('hidden'),
                'actor_socket':str(a.root_component.get_attach_socket_name()),
                'class':c.get_class().get_name(),'first_person':str(c.get_editor_property('first_person_primitive_type')),
                'shadow_flags':[c.get_editor_property(n) for n in ['cast_shadow','cast_dynamic_shadow','cast_static_shadow','cast_hidden_shadow','cast_contact_shadow']],
                'parent':c.get_attach_parent().get_name() if c.get_attach_parent() else None, 'socket':str(c.get_attach_socket_name()),
                'camera': transform(c.get_world_transform().make_relative(ct))}
            if isinstance(c,u.SkeletalMeshComponent):
                inst = c.get_anim_instance()
                if inst and hasattr(inst,'get_evaluation_state'):
                    item['evaluation'] = json.loads(inst.get_evaluation_state())
                    if 'BaseMagazine' in a.get_name():
                        item['ammo_display'] = inst.get_editor_property('AmmoCount')
                item['bones'] = {n:transform(c.get_socket_transform(n,u.RelativeTransformSpace.RTS_WORLD).make_relative(ct))
                    for n in ['head','ik_hand_gun','hand_l','hand_r','SOCKET_Magazine','SOCKET_Magazine_Reserve','SOCKET_Muzzle'] if c.does_socket_exist(n)}
            parts.append(item)
    physics=[]
    for a in u.GameplayStatics.get_all_actors_of_class(w,u.Actor):
        if 'BP_TFA_Physics' not in a.get_class().get_name(): continue
        physics.append({'actor':a.get_name(),'parts':[{'name':c.get_name(),'shadow':c.get_editor_property('cast_shadow'),
            'space':str(c.get_editor_property('first_person_primitive_type'))} for c in a.get_components_by_class(u.PrimitiveComponent)]})
    result.update(world_time=u.GameplayStatics.get_time_seconds(w), paused=u.GameplayStatics.is_game_paused(w),
        velocity=vec(p.get_velocity()), location=vec(p.get_actor_location()), camera=transform(ct), parts=parts,
        simulated_velocity=vec(p.get_editor_property('SimulatedVelocity')),physics=physics,
        camera_animation=not p.get_editor_property('bAnimateCamera'),source_head_lock=p.get_editor_property('bAnimateCamera'),canted=p.get_editor_property('bIsCantedAiming'),
        source_camera=transform(p.get_editor_property('CameraFP').get_world_transform()),
        view_fov=camera.get_fov_angle(),
        source_stance=str(p.get_editor_property('CurrentStance')),
        crouch_target=transform(p.get_editor_property('TargetCrouchOffset')))
    return result

def start(spec):
    global RUN
    assert RUN is None or RUN['done']
    config = json.loads(spec)
    assert not (OUT / (config['name'] + '.json')).exists()
    w = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    p = u.GameplayStatics.get_player_pawn(w,0)
    if config.get('fixture') == 'platform':
        assert p.probe_fixture('platform')
    if config.get('audio'):
        (OUT/'Audio').mkdir(exist_ok=True)
        u.AudioMixerLibrary.start_recording_output(w,config['duration'])
    RUN = dict(config=config, done=False, rows=[], events=[], error=None, world=w, pawn=p,
        start=u.GameplayStatics.get_time_seconds(w), wall=time.monotonic(), index=0, held=set())
    RUN['handle'] = u.register_slate_post_tick_callback(tick)
    return status()

def status():
    if not RUN:
        return {'done':True,'error':'not started'}
    return dict(name=RUN['config']['name'], done=RUN['done'], samples=len(RUN['rows']),
        event=RUN['index'], error=RUN['error'], t=RUN['rows'][-1]['t'] if RUN['rows'] else 0)

def finish():
    r = RUN
    for key in r['held']:
        r['pawn'].probe_key(key,0,False)
    r['done'] = True
    u.unregister_slate_post_tick_callback(r['handle'])
    if r['config'].get('audio'):
        u.AudioMixerLibrary.stop_recording_output(r['world'],u.AudioRecordingExportType.WAV_FILE,
            r['config']['name'],str(OUT/'Audio'))
    (OUT / (r['config']['name'] + '.json')).write_text(json.dumps({k:r[k] for k in ['config','error','rows','events']}, separators=(',',':')),encoding='utf-8')

def tick(delta):
    r = RUN
    try:
        now = u.GameplayStatics.get_time_seconds(r['world']) - r['start']
        events = r['config']['events']
        while r['index'] < len(events) and now >= events[r['index']][0]:
            _,key,value = events[r['index']]
            if key == '@ceiling':
                assert r['pawn'].probe_fixture('ceiling')
            else:
                r['pawn'].probe_key(key,abs(value),value>0)
                if value>0 and not key.startswith('Mouse'): r['held'].add(key)
                else: r['held'].discard(key)
            r['events'].append({'t':now,'key':key,'value':value})
            r['index'] += 1
        row = sample()
        row.update(t=now,wall=time.monotonic()-r['wall'],delta=delta,held=sorted(r['held']))
        r['rows'].append(row)
        if now >= r['config']['duration']:
            finish()
    except Exception:
        r['error'] = traceback.format_exc()
        finish()
