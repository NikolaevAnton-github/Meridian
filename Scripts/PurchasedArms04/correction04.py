"""Narrow transition-rule correction for the idle-authored additive jump."""
import hashlib
import json
from pathlib import Path
import unreal as u
from editor_toolset.toolsets.blueprint import BlueprintTools as BP
from stage1_tools import state

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/PurchasedArms04/Worker/Correction01'
BASE = '/Game/InfimaGames/TacticalFPSAnimations/'
ANIM = BASE + 'Common/Core/Characters/ABP_TFA_FP_BaseCharacter'


def write(name, value):
    path = OUT / (name + '.json')
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')
    return value


def pin(p):
    return {'name': p.name, 'type': p.type_id, 'value': p.value,
            'links': [{'node': q.node.get_name(), 'index': q.index_id} for q in p.connected_pins]}


def relevant(graph):
    return any(name in graph.get_path_name() for name in ['SM_LocomotionStanding', 'SM_RunningTransitions'])


def audit():
    bp = u.load_asset(ANIM)
    graphs = []
    for graph in BP.list_graphs(bp):
        if not relevant(graph):
            continue
        nodes = []
        for info in BP.get_node_infos(u.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes()):
            item = {'name': info.node.get_name(), 'type': info.type_id,
                    'inputs': [pin(p) for p in info.input_pins], 'outputs': [pin(p) for p in info.output_pins]}
            if info.node.get_class().get_name() in ['AnimGraphNode_SequencePlayer', 'AnimGraphNode_BlendSpacePlayer']:
                data = info.node.get_editor_property('node')
                prop = 'sequence' if 'Sequence' in info.node.get_class().get_name() else 'blend_space'
                item[prop] = str(data.get_editor_property(prop))
            nodes.append(item)
        graphs.append({'path': graph.get_path_name(), 'nodes': nodes})
    graph = next(g for g in BP.list_graphs(bp) if '.SM_LocomotionStanding.AnimStateTransitionNode_0.' in g.get_path_name())
    # Epic's Python type cache assumes a direct Blueprint outer. Transition
    # graphs have state-node outers, so use its native graph-editor API here.
    getter_types = [str(t) for t in u.BlueprintGraphEditor.get_graph_editor(graph).list_available_nodes([])
                    if 'useordinaryjumpbase' in str(t).lower()]
    seq = u.load_asset(BASE + 'Weapons/AssaultRifle/Animations/Character/FP/Locomotion/A_TFA_FP_AR_Jump_Full')
    metadata = {name: str(seq.get_editor_property(name)) for name in ['additive_anim_type', 'ref_pose_seq']}
    return {'graphs': graphs, 'getter_types': getter_types, 'jump_sequence': metadata, 'state': state()}


def fix():
    current = state()
    assert not current['pie'] and not current['dirty_maps'] and not current['dirty_content'], current
    asset_path = ROOT / ('Content/' + ANIM.removeprefix('/Game/') + '.uasset')
    backup = OUT / 'Rollback' / asset_path.relative_to(ROOT)
    assert backup.read_bytes() == asset_path.read_bytes(), 'Starting asset must match the preserved candidate.'
    before = audit()
    bp = u.load_asset(ANIM)
    changes = []
    for graph in BP.list_graphs(bp):
        path = graph.get_path_name()
        if not relevant(graph) or '.AnimStateTransitionNode_' not in path:
            continue
        infos = BP.get_node_infos(u.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes())
        result = next(n for n in infos if n.node.get_class().get_name() == 'AnimGraphNode_TransitionResult')
        condition = next(p for p in result.input_pins if p.name == 'bCanEnterTransition')
        assert len(condition.connected_pins) == 1
        original = condition.connected_pins[0]
        # Stand -> fast requires not jumping; fast -> Stand also permits jumping.
        # Keep the run-transition layer in its reference-pose Run state through
        # the entire jump. Run End can only begin after the jump has no weight.
        standing = 'SM_LocomotionStanding' in path
        block = (standing and any(f'.AnimStateTransitionNode_{i}.' in path for i in [0, 2])) or (
            not standing and '.AnimStateTransitionNode_17.' in path)
        getter_type = next(t for t in before['getter_types'] if 'Get' in t)
        editor = u.BlueprintGraphEditor.get_graph_editor(graph)
        def create(type_id, x, y):
            node = editor.create_node_from_name(type_id, u.Vector2D(x, y), [], None)
            assert node, type_id
            return node
        getter = create(getter_type, -450, 200)
        get_pin = next(p.pin_id for p in BP.get_node_infos([getter])[0].output_pins if p.name == 'bUseOrdinaryJumpBase')
        operator = create('Math|Boolean|' + ('ANDBoolean' if block else 'ORBoolean'), -150, 0)
        info = BP.get_node_infos([operator])[0]
        op_a = next(p.pin_id for p in info.input_pins if p.name == 'A')
        op_b = next(p.pin_id for p in info.input_pins if p.name == 'B')
        op_result = next(p.pin_id for p in info.output_pins if p.name == 'ReturnValue')
        added = [getter, operator]
        if block:
            inverse = create('Math|Boolean|NOTBoolean', -300, 200)
            info = BP.get_node_infos([inverse])[0]
            BP.connect_pins(get_pin, next(p.pin_id for p in info.input_pins if p.name == 'A'))
            get_pin = next(p.pin_id for p in info.output_pins if p.name == 'ReturnValue')
            added.append(inverse)
        BP.break_pins(original, condition.pin_id)
        BP.connect_pins(original, op_a)
        BP.connect_pins(get_pin, op_b)
        BP.connect_pins(op_result, condition.pin_id)
        BP.arrange_nodes(added)
        changes.append({'graph': path, 'rule': 'original AND NOT jump' if block else 'original OR jump',
                        'new_nodes': [n.get_name() for n in added]})
    assert len(changes) == 7, changes
    BP.compile_blueprint(bp, warnings_as_errors=True)
    assert u.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
    return write('graph-fix', {'changes': changes, 'after': audit(),
        'before_sha256': hashlib.sha256(backup.read_bytes()).hexdigest(),
        'after_sha256': hashlib.sha256(asset_path.read_bytes()).hexdigest(), 'compile_warnings_as_errors': True})


def action(operation, argument):
    if operation == 'correction_audit':
        return write('graph-audit-' + argument, audit())
    if operation == 'correction_fix':
        return fix()
    if operation == 'correction_contract':
        data = audit()
        checks = [g for g in data['graphs'] if any('UseOrdinaryJumpBase' in n['type'] for n in g['nodes'])]
        assert len(checks) == 7
        bp = u.load_asset(ANIM)
        graph = next(g for g in BP.list_graphs(bp) if g.get_name() == 'AnimGraph')
        ads = next(n for n in u.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes()
                   if n.get_name() == 'AnimGraphNode_ModifyBone_2')
        assert ads.get_editor_property('node').get_editor_property('translation_space') == u.BoneControlSpace.BCS_COMPONENT_SPACE
        source_pin = next(p for p in BP.get_node_infos([ads])[0].input_pins if p.name == 'Translation').connected_pins[0]
        conversion = BP.get_node_infos([source_pin.node])[0]
        assert conversion.type_id == 'Math|Vector|RotateVector'
        assert next(p.value for p in conversion.input_pins if p.name == 'B') == '0,90,0'
        return write('cold-contract', {'guarded_transitions': len(checks), 'ads_component_space_and_basis_preserved': True,
                                      'blueprint_status': str(bp.get_editor_property('status')), 'state': state()})
    raise ValueError(operation)
