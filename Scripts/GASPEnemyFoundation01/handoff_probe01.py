"""Lightweight handoff observations using the retained native-input/capture harness.

Full body/skin audits lower the frame rate and can mask a short transition defect.
Keep per-frame pose and cached animation targets; retain full state at transitions.
"""
import json
import unreal as u
from Scripts.GASPEnemyFoundation01 import unreal98


def vec(value):
    return [value.x, value.y, value.z]


def start(config):
    base = unreal98.unreal87.unreal85
    base.OUT = unreal98.OUT
    original_sample = base.sample
    last_key = None
    full = None
    pending = list(config.get('handoff_events', []))

    def sample(contacts=False):
        nonlocal last_key, full
        world, player, manager, fixtures = base.actors()
        fixture = base.selected(fixtures)
        pawn = fixture.get_movement_pawn()
        mesh = fixture.body
        controls = pawn.get_component_by_class(u.PhysicsControlComponent)
        mover = pawn.get_component_by_class(u.MoverComponent)
        now = json.loads(manager.get_combat_state())['firing_clock'] - base.verify02.RUN['clock_start']
        for event in pending[:]:
            if now < event[0]:
                continue
            _, key, value = event
            if key == 'move':
                fixture.set_movement_command(u.Vector(*value), True)
            elif key == 'impulse':
                bone = value.get('bone', 'spine_03')
                fixture.apply_external_disturbance(u.Vector(*value['impulse']), fixture.get_physical_body_location(bone), bone)
            elif key == 'rifle_after_getup':
                state = json.loads(fixture.get_dummy_state(False))
                if state['gasp']['authority'] != 'Locomotion' or not state['balance']['get_ups']:
                    continue
                player.probe_key('LeftMouseButton', 1, True)
                base.verify02.RUN['held'].add('LeftMouseButton')
                pending.append([now + float(value), 'rifle_release', 0])
            elif key == 'rifle_release':
                player.probe_key('LeftMouseButton', 0, False)
                base.verify02.RUN['held'].discard('LeftMouseButton')
            else:
                raise ValueError(key)
            base.verify02.RUN['events'].append(dict(t=now, key=key, value=value))
            pending.remove(event)
        key = (str(fixture.authority), str(fixture.balance_state), fixture.physical_hits, fixture.deaths)
        changed = key != last_key
        if changed:
            full = json.loads(fixture.get_dummy_state(True))
            last_key = key
        bones = ['pelvis', 'spine_05', 'head', 'hand_l', 'foot_l', 'foot_r']
        if config.get('heading_probe'):
            bones += ['hand_r', 'upperarm_l', 'upperarm_r', 'clavicle_l', 'clavicle_r']
        physical = {bone: vec(fixture.get_physical_body_location(bone)) for bone in bones}
        visual = {bone: vec(mesh.get_socket_location(bone)) for bone in bones}
        targets = {bone: vec(controls.get_cached_bone_position(mesh, bone)) for bone in bones}
        result = dict(world_time=u.GameplayStatics.get_time_seconds(world),
            world_delta=u.GameplayStatics.get_world_delta_seconds(world),
            global_dilation=u.GameplayStatics.get_global_time_dilation(world),
            physical=physical, visual=visual, targets=targets,
            chest_spin=vec(mesh.get_physics_angular_velocity_in_radians('spine_05')),
            authority=str(fixture.authority), balance=str(fixture.balance_state),
            mover_mode=str(mover.get_movement_mode_name()),
            capsule=vec(pawn.get_actor_location()), heading=vec(pawn.get_actor_forward_vector()),
            pose_override=mesh.get_anim_instance().get_editor_property('MSQRecoveryActive'),
            applied_profile=str(pawn.get_editor_property('AppliedPhysicsProfile')),
            dummy=dict(name=fixture.get_name(), epoch=full['epoch'], physical_hits=fixture.physical_hits,
                deaths=fixture.deaths, health=fixture.health),
            full_state=full if changed else None)
        if config.get('heading_probe'):
            result['orientation_pre'] = vec(pawn.get_editor_property('MoverDefaultInputs_PreSim').orientation_intent)
            result['orientation_post'] = vec(pawn.get_editor_property('MoverDefaultInputs_PostSim').orientation_intent)
            result['move_input'] = vec(pawn.get_editor_property('MoverDefaultInputs_PreSim').move_input)
            result['mesh_rotation'] = str(mesh.get_world_rotation())
            result['bone_rotations'] = {bone: str(mesh.get_socket_rotation(bone)) for bone in ['pelvis', 'spine_05', 'upperarm_l', 'upperarm_r']}
        return result

    result = base.action('verify', json.dumps(config))
    base.sample = sample
    run = base.verify02.RUN
    u.unregister_slate_post_tick_callback(run['handle'])

    def tick(delta):
        base.tick(delta)
        if run['done']:
            base.sample = original_sample

    run['handle'] = u.register_slate_post_tick_callback(tick)
    if config.get('flying'):
        player = base.actors()[1]
        player.character_movement.set_movement_mode(u.MovementMode.MOVE_FLYING)
        player.character_movement.stop_movement_immediately()
        player.set_actor_location(u.Vector(*config['location']), False, False)
    return result
