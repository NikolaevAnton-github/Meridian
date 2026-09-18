"""Small MSQ-63 additions to the MSQ-62 evaluated-pose verifier."""
import importlib
import json
from pathlib import Path
import unreal as u
from editor_toolset.toolsets.blueprint import BlueprintTools as BP
from stage1_tools import state
import verify02

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/PurchasedArms03/Worker'
BASE = '/Game/InfimaGames/TacticalFPSAnimations/'
ANIM = BASE + 'Common/Core/Characters/ABP_TFA_FP_BaseCharacter'
ORIGINAL_SAMPLE = verify02.sample
SHOTS = set()


def write(name, value):
    path = OUT / (name + '.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')
    return value


def audit():
    bp = u.load_asset(ANIM)
    rows = []
    for graph in BP.list_graphs(bp):
        for node in u.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes():
            if node.get_class().get_name() not in ['AnimGraphNode_ModifyBone', 'AnimGraphNode_Fabrik']:
                continue
            data = node.get_editor_property('node')
            names = (['bone_to_modify', 'translation_mode', 'rotation_mode', 'scale_mode',
                      'translation_space', 'rotation_space', 'scale_space']
                     if node.get_class().get_name() == 'AnimGraphNode_ModifyBone' else
                     ['effector_transform_space', 'effector_target', 'tip_bone', 'root_bone'])
            props = {key: str(data.get_editor_property(key)) for key in names}
            info = BP.get_node_infos([node])[0]
            props['inputs'] = [{'name': pin.name, 'links': [q.node.get_name() for q in pin.connected_pins]}
                               for pin in info.input_pins]
            rows.append({'node': node.get_name(), **props})
    config = u.load_asset(BASE + 'Weapons/AssaultRifle/Demo/Data/DA_TFA_AssaultRifle')
    return {'nodes': rows, 'config': {name: verify02.transform(config.get_editor_property(name))
            for name in ['OffsetAimDownSights', 'OffsetCantedAim', 'OffsetCrouch']}, 'state': state()}


def sample():
    row = ORIGINAL_SAMPLE()
    world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    pawn = u.GameplayStatics.get_player_pawn(world, 0)
    pc = pawn.get_controller()
    control = pc.get_control_rotation()
    row['control'] = [control.pitch, control.yaw, control.roll]
    row['mesh_world'] = verify02.transform(pawn.mesh.get_world_transform())
    row['offsets'] = {name: verify02.transform(pawn.get_editor_property(name)) for name in
        ['TargetAimDownSightsOffset', 'CurrentAimDownSightsOffset', 'CurrentRecoil']}
    # Preserve all existing evaluated transforms and add an attachment-relative IK check.
    gun = pawn.mesh.get_socket_transform('ik_hand_gun', u.RelativeTransformSpace.RTS_WORLD)
    row['hands_relative_gun'] = {name: verify02.transform(pawn.mesh.get_socket_transform(
        name, u.RelativeTransformSpace.RTS_WORLD).make_relative(gun)) for name in ['hand_l', 'hand_r']}
    run = verify02.RUN
    if run and not run['done']:
        now = row['world_time'] - run['start']
        config = run['config']
        # Closed-loop mouse input keeps the test independent of viewport/FOV sensitivity.
        # Only the existing native input probe changes the player's view.
        targets = config.get('headings', [[0, 0, 0]])
        target = targets[0]
        for next_target in targets[1:]:
            if now < next_target[0]:
                break
            target = next_target
        errors = [((target[1] - control.yaw + 180) % 360) - 180,
                  ((target[2] - control.pitch + 180) % 360) - 180]
        gain = .07 * 2.5 * row['view_fov'] * .011110
        for key, error in zip(['MouseX', 'MouseY'], errors):
            delta = max(-1.5, min(1.5, error * .5))
            if abs(delta) > .00005:
                pawn.probe_key(key, delta / gain, True)
        row['heading_target'] = target
        row['heading_error'] = errors
        for stamp, label in config.get('shots', []):
            if now >= stamp and label not in SHOTS:
                path = OUT / 'Views' / (config['name'] + '-' + label + '.png')
                path.parent.mkdir(parents=True, exist_ok=True)
                assert not path.exists(), path
                u.SystemLibrary.execute_console_command(world, 'HighResShot 1 filename="' + str(path) + '"')
                SHOTS.add(label)
                row['screenshot_requested'] = label
    return row


def action(operation, argument):
    global ORIGINAL_SAMPLE, SHOTS
    if operation == 'close':
        current = state()
        assert not current['pie'] and not current['dirty_maps'] and not current['dirty_content'], current
        write('editor-before-cold-restart', current)
        u.SystemLibrary.quit_editor()
        return {'close_requested': True}
    if operation == 'cold_load':
        current = state()
        assert not current['pie'] and not current['dirty_maps'] and not current['dirty_content'], current
        bp = u.load_asset(ANIM)
        graph = next(g for g in BP.list_graphs(bp) if g.get_name() == 'AnimGraph')
        nodes = u.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes()
        ads = next(n for n in nodes if n.get_name() == 'AnimGraphNode_ModifyBone_2')
        space = ads.get_editor_property('node').get_editor_property('translation_space')
        assert space == u.BoneControlSpace.BCS_COMPONENT_SPACE
        translation = next(p for p in BP.get_node_infos([ads])[0].input_pins if p.name == 'Translation')
        rotate = translation.connected_pins[0].node
        info = BP.get_node_infos([rotate])[0]
        assert info.type_id == 'Math|Vector|RotateVector'
        rotation = next(p for p in info.input_pins if p.name == 'B')
        assert rotation.value == '0,90,0', rotation.value
        assert next(p for p in info.input_pins if p.name == 'A').connected_pins[0].node.get_name() == 'K2Node_VariableGet_4'
        return write('cold-load', {'state': current, 'generated_class': bp.generated_class().get_path_name(),
            'blueprint_status': str(bp.get_editor_property('status')), 'translation_space': str(space),
            'conversion_node': rotate.get_name(), 'conversion_rotation': rotation.value})
    if operation == 'fix':
        import fix03
        importlib.reload(fix03)
        return fix03.run()
    if operation == 'reload_audit':
        current = state()
        assert not current['pie'] and not current['dirty_maps']
        assert set(current['dirty_content']) <= {ANIM}, current
        initial = json.loads((OUT / 'editor-state-initial.json').read_text())
        assert not initial['dirty_content'] and not (OUT / 'fix.json').exists()
        bp = u.load_asset(ANIM)
        result = u.EditorLoadingAndSavingUtils.reload_packages(
            [bp.get_outer()], u.ReloadPackagesInteractionMode.ASSUME_POSITIVE)
        return write('audit-package-reload' + argument, {'result': str(result), 'state': state()})
    if operation == 'state':
        return write('editor-state-' + argument, state())
    if operation == 'audit':
        return write('graph-audit-' + argument, audit())
    if operation == 'sample':
        return write('sample-' + argument, sample())
    if operation == 'verify':
        assert verify02.RUN is None or verify02.RUN['done']
        importlib.reload(verify02)
        ORIGINAL_SAMPLE = verify02.sample
        verify02.sample = sample
        verify02.OUT = OUT
        SHOTS = set()
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
    raise ValueError(operation)
