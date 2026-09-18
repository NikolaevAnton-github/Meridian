"""Focused source/input/pose adapters over the existing verification driver."""
import importlib
import json
import time
from pathlib import Path
import unreal as u
from editor_toolset.toolsets.blueprint import BlueprintTools as BP
from stage1_tools import state
import verify02

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/PurchasedArms05/Worker'
BASE = '/Game/InfimaGames/TacticalFPSAnimations/'
ORIGINAL_SAMPLE = verify02.sample


def write(name, value):
    path = OUT / (name + '.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')
    return value


def sample():
    row = ORIGINAL_SAMPLE()
    world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    pawn = u.GameplayStatics.get_player_pawn(world, 0)
    movement = pawn.character_movement
    anim = pawn.mesh.get_anim_instance()
    row.update(jump_z_velocity=movement.jump_z_velocity, max_walk_speed=movement.max_walk_speed,
               animation_jump_base=anim.get_editor_property('bUseOrdinaryJumpBase'),
               capture_wall_monotonic=time.monotonic())
    row['aim_offset'] = verify02.transform(pawn.get_editor_property('CurrentAimDownSightsOffset'))
    row['aim_target'] = verify02.transform(pawn.get_editor_property('TargetAimDownSightsOffset'))
    for name in ['AimingAlpha', 'bIsAiming', 'bIsRunning', 'bIsSprinting']:
        try:
            row['anim_' + name] = anim.get_editor_property(name)
        except Exception:
            pass
    # Deliver through PlayerController input immediately after a confirmed physical
    # takeoff sample. Zero means the first sample, one means the following frame.
    run = verify02.RUN
    if row['falling'] and row['jump_starts']:
        count = run.setdefault('air_frames', {}).get(row['jump_starts'], 0)
        run['air_frames'][row['jump_starts']] = count + 1
        for trigger in run['config'].get('air_inputs', []):
            if trigger.get('jump', 1) == row['jump_starts'] and trigger['frame'] == count:
                for key, value in trigger['keys']:
                    pawn.probe_key(key, abs(value), value > 0)
                    if value > 0:
                        run['held'].add(key)
                    else:
                        run['held'].discard(key)
                    run['events'].append({'t': row['world_time'] - run['start'], 'key': key, 'value': value,
                        'after_air_frame': count, 'frame': row['frame'], 'falling': True,
                        'vertical_velocity': row['velocity'][2], 'ammo_before': row['ammo']})
    return row


def audit():
    bp = u.load_asset(BASE + 'Common/Core/Characters/BP_TFA_BaseCharacter')
    graphs = []
    for graph in BP.list_graphs(bp):
        if graph.get_name() not in ['EventGraph', 'PlayJump', 'CGraph_PlaySyncedAnimation',
            'CGraph_TacticalSprint', 'PlayFire', 'Fire', 'Aim', 'AimIn', 'AimOut', 'PlayAnimation',
            'CGraph_Aiming', 'CGraph_Firing']:
            continue
        def pin(p):
            return {'name': p.name, 'value': p.value, 'type': p.type_id,
                    'links': [{'node': q.node.get_name(), 'pin': q.index_id} for q in p.connected_pins]}
        graphs.append({'path': graph.get_path_name(), 'nodes': [
            {'name': info.node.get_name(), 'title': str(info.node.get_node_title()), 'type': info.type_id,
             'inputs': [pin(p) for p in info.input_pins], 'outputs': [pin(p) for p in info.output_pins]}
            for info in BP.get_node_infos(u.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes())]})
    mapping = u.load_asset(BASE + 'Common/Core/Inputs/IMC_TFA_Default')
    mappings = []
    for m in mapping.get_editor_property('mappings'):
        if any(x in m.action.get_name() for x in ['Sprint', 'Run', 'Aim', 'Fire']):
            mappings.append({'action': m.action.get_path_name(), 'key': str(m.key),
                             'triggers': [str(t) for t in m.triggers],
                             'action_triggers': [str(t) for t in m.action.triggers]})
    jump = u.load_asset(BASE + 'Weapons/AssaultRifle/Animations/Character/FP/Locomotion/AM_TFA_FP_AR_Jump_Full')
    return {'graphs': graphs, 'all_graphs': [g.get_name() for g in BP.list_graphs(bp)],
            'variables': list(BP.list_variables(bp)), 'mappings': mappings,
            'jump': {'length': jump.get_play_length(), 'notifies': [
                {'event': str(n), 'time': u.AnimationLibrary.get_anim_notify_event_trigger_time(n),
                 'duration': u.AnimationLibrary.get_anim_notify_event_duration(n)}
                for n in u.AnimationLibrary.get_animation_notify_events(jump)]},
            'state': state()}


def action(operation, argument):
    global ORIGINAL_SAMPLE
    if operation == 'contract':
        import sys
        sys.path.insert(0, str(ROOT / 'Scripts/PurchasedArms04'))
        import correction04
        assert argument in ['', 'Correction01', 'Correction02']
        correction04.OUT = OUT / (argument or 'Correction01')
        return correction04.action('correction_contract', argument)
    if operation == 'state':
        return write('editor-state-' + argument, state())
    if operation == 'audit':
        result = audit()
        write('source-audit-' + argument, result)
        return {'graphs': len(result['graphs']), 'all_graphs': result['all_graphs'], 'state': result['state']}
    if operation == 'verify':
        assert verify02.RUN is None or verify02.RUN['done']
        importlib.reload(verify02)
        ORIGINAL_SAMPLE = verify02.sample
        verify02.sample = sample
        verify02.OUT = OUT
        return verify02.start(argument)
    if operation == 'verify_status':
        return verify02.status()
    if operation == 'performance':
        obj = u.get_default_object(u.load_class(None, '/Script/UnrealEd.EditorPerformanceSettings'))
        path = OUT / 'performance-before.json'
        if not path.exists():
            write('performance-before', {'throttle': obj.get_editor_property('bThrottleCPUWhenNotForeground')})
        value = json.loads(path.read_text())['throttle'] if argument == 'restore' else False
        obj.set_editor_property('bThrottleCPUWhenNotForeground', value)
        return {'throttle': value}
    if operation == 'close':
        current = state()
        assert not current['pie'] and not current['dirty_maps'] and not current['dirty_content'], current
        write('editor-before-close-' + argument, current)
        u.SystemLibrary.quit_editor()
        return {'close_requested': True}
    raise ValueError(operation)
