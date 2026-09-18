"""Focused jump evidence; native input and evaluated poses reuse MSQ-62."""
import importlib
import json
import time
from pathlib import Path
import unreal as u
from editor_toolset.toolsets.blueprint import BlueprintTools as BP
from stage1_tools import state
import verify02

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/PurchasedArms04/Worker'
BASE = '/Game/InfimaGames/TacticalFPSAnimations/'
ORIGINAL_SAMPLE = verify02.sample


def write(name, value):
    target = OUT / (name + '.json')
    target.parent.mkdir(parents=True, exist_ok=True)
    assert not target.exists(), target
    target.write_text(json.dumps(value, indent=2), encoding='utf-8')
    return value


def sample():
    row = ORIGINAL_SAMPLE()
    world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    pawn = u.GameplayStatics.get_player_pawn(world, 0)
    movement = pawn.character_movement
    row.update(jump_z_velocity=movement.jump_z_velocity, max_walk_speed=movement.max_walk_speed,
               air_control=movement.air_control, gravity_scale=movement.gravity_scale)
    anim = pawn.mesh.get_anim_instance()
    row['animation_jump_base'] = anim.get_editor_property('bUseOrdinaryJumpBase')
    row['capture_wall_monotonic'] = time.monotonic()
    return row


def audit():
    bp = u.load_asset(BASE + 'Common/Core/Characters/BP_TFA_BaseCharacter')
    graphs = []
    for graph in BP.list_graphs(bp):
        if graph.get_name() not in ['EventGraph', 'PlayJump', 'CGraph_PlaySyncedAnimation', 'CGraph_TacticalSprint']:
            continue
        def pin(p):
            return {'name': p.name, 'value': p.value, 'type': p.type_id,
                    'links': [{'node': q.node.get_name(), 'pin': q.index_id} for q in p.connected_pins]}
        graphs.append({'path': graph.get_path_name(), 'nodes': [
            {'name': info.node.get_name(), 'type': info.type_id,
             'inputs': [pin(p) for p in info.input_pins], 'outputs': [pin(p) for p in info.output_pins]}
            for info in BP.get_node_infos(u.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes())]})
    return {'graphs': graphs, 'state': state()}


def action(operation, argument):
    global ORIGINAL_SAMPLE
    if operation in ['correction_audit', 'correction_fix', 'correction_contract']:
        import correction04
        importlib.reload(correction04)
        return correction04.action(operation, argument)
    if operation == 'state':
        return write('editor-state-' + argument, state())
    if operation == 'audit':
        return write('source-audit-' + argument, audit())
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
