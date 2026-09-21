"""Bounded task asset operations, invoked through the official Epic toolset."""
import json
import hashlib
import shutil
from pathlib import Path
import unreal as u

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/CombatSlice01/GASPEnemyFoundation01/Worker'
PREFIX = '/GASPEnemyFoundation01/'


def graph(bp, name):
    return u.BlueprintGraphEditor.get_graph_editor(u.BlueprintEditorLibrary.find_graph(bp, name))


def inspect_assets():
    base = u.load_asset(PREFIX + 'Blueprints/SandboxCharacter_Mover')
    ragdoll = u.load_asset(PREFIX + 'Blueprints/SandboxCharacter_Mover_Ragdoll')
    anim = u.load_asset(PREFIX + 'Blueprints/SandboxCharacter_Mover_ABP')
    sub = u.get_engine_subsystem(u.SubobjectDataSubsystem)
    result = {'components': [], 'animation_nodes': [], 'methods': {}}
    for bp in [base, ragdoll]:
        for handle in sub.k2_gather_subobject_data_for_blueprint(bp):
            data = u.SubobjectDataBlueprintFunctionLibrary.get_data(handle)
            obj = u.SubobjectDataBlueprintFunctionLibrary.get_object(data)
            row = {'blueprint': bp.get_name(), 'object': obj.get_path_name() if obj else None}
            if obj:
                row['class'] = obj.get_class().get_name()
                for prop in ['skeletal_mesh_asset','physics_asset_override','anim_class','control_asset','relative_location','relative_rotation','capsule_half_height']:
                    try:
                        row[prop] = str(obj.get_editor_property(prop))
                    except Exception:
                        pass
            result['components'].append(row)
    ed = graph(anim, 'AnimGraph')
    result['animation_nodes'] = [x for x in ed.list_available_nodes([]) if any(s in x.lower() for s in ['snapshot', 'blendposesbybool', 'blendposesby'])]
    result['methods']['get_struct_type'] = u.BlueprintEditorLibrary.get_struct_type.__doc__
    result['methods']['add_member_variable'] = u.BlueprintEditorLibrary.add_member_variable.__doc__
    with (OUT / 'asset-editor-audit01.json').open('w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    return result


def node(ed, name):
    return next(n for n in ed.list_all_nodes() if n.get_name() == name)


def connect(a, b):
    assert a.try_create_connection(b), (str(a.get_pin_name()), str(b.get_pin_name()))


def self_node(ed):
    names = ed.list_available_nodes([])
    choices = [x for x in names if 'referencetoself' in x.lower() or x.lower().endswith('|self')]
    assert choices, [x for x in names if 'self' in x.lower()]
    return ed.create_node_from_name(choices[0], u.Vector2D(-400, -300), [])


def bridge_call(ed, method):
    call = ed.add_call_function_node('/Script/MeridianSquad.GASPEnemyFoundationLibrary.' + method)
    selfref = self_node(ed)
    connect(selfref.find_output_pin('self'), call.find_input_pin('Foundation'))
    return call


def gate(ed, source, method):
    targets = list(source.list_connected_pins())
    assert targets, 'Expected connected entry to gate.'
    source.break_pin_links()
    branch = ed.add_branch_node()
    call = bridge_call(ed, method)
    connect(source, branch.find_execute_pin())
    connect(call.find_output_pin('ReturnValue'), branch.find_input_pin('Condition'))
    for target in targets:
        connect(branch.find_output_pin('then'), target)
    ed.add_comment_to_nodes('MSQ-98: one physical authority; native recovery gates sample writes.', [branch, call])


def archive(bp):
    relative = bp.get_path_name().split('.')[0].removeprefix(PREFIX) + '.uasset'
    src = ROOT / 'Plugins/GASPEnemyFoundation01/Content' / relative
    dest = OUT / 'MigratedBeforeAuthoring01' / relative
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def save(bp):
    from toolset_registry.helpers import compile_blueprint
    compile_blueprint(bp, False)
    assert u.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)


def author_control():
    base = u.load_asset(PREFIX + 'Blueprints/SandboxCharacter_Mover')
    ragdoll = u.load_asset(PREFIX + 'Blueprints/SandboxCharacter_Mover_Ragdoll')
    for bp in [base, ragdoll]:
        archive(bp)
    ed = graph(base, 'Get_MoveInput')
    entry = ed.find_graph_entry_pin()
    entry.break_pin_links()
    result = ed.add_return_node()
    call = bridge_call(ed, 'CommandedMovement')
    outputs = [p for p in result.list_all_pins() if str(p.get_pin_type_display_string()) == 'Vector']
    assert len(outputs) == 1, [(str(p.get_pin_name()), str(p.get_pin_type_display_string())) for p in result.list_all_pins()]
    outputs[0].break_pin_links()
    connect(entry, result.find_execute_pin())
    connect(call.find_output_pin('ReturnValue'), outputs[0])
    ed = graph(base, 'Get_Gait')
    entry = ed.find_graph_entry_pin()
    entry.break_pin_links()
    branch = ed.add_branch_node()
    call = bridge_call(ed, 'CommandedWalk')
    connect(entry, branch.find_execute_pin())
    connect(call.find_output_pin('ReturnValue'), branch.find_input_pin('Condition'))
    for output, value in [('then', 'NewEnumerator0'), ('else', 'NewEnumerator1')]:
        result = ed.add_return_node()
        connect(branch.find_output_pin(output), result.find_execute_pin())
        pins = [p for p in result.list_all_pins() if 'E_Gait' in str(p.get_pin_type_display_string())]
        assert len(pins) == 1
        pins[0].break_pin_links()
        assert pins[0].set_pin_value(value)
    for name in ['SetupInput', 'SetupCamera']:
        graph(base, name).find_graph_entry_pin().break_pin_links()
    # Sample input events remain unbound; the inherited function interfaces persist.
    save(base)
    gate(graph(ragdoll, 'SetPhysicsProfile'), graph(ragdoll, 'SetPhysicsProfile').find_graph_entry_pin(), 'AllowSamplePhysics')
    gate(graph(ragdoll, 'Ragdoll_UpdatePhysicsStrengthsFromCurves'), graph(ragdoll, 'Ragdoll_UpdatePhysicsStrengthsFromCurves').find_graph_entry_pin(), 'AllowSamplePhysics')
    ed = graph(ragdoll, 'EventGraph')
    node(ed, 'K2Node_CustomEvent_8')  # On_RagdollMode_Exit; preserve capsule restoration before gate.
    gate(ed, node(ed, 'K2Node_CallFunction_13').find_then_pin(), 'AllowSampleGetUp')
    disabled = []
    for n in ed.list_all_nodes():
        if n.get_node_title().replace(' ', '').replace('\n', '').startswith('NPC_GetupCheck'):
            n.find_then_pin().break_pin_links()
            disabled.append(n.get_name())
    assert disabled, 'Expected sample autonomous get-up entry.'
    save(ragdoll)
    return {'saved': [base.get_path_name(), ragdoll.get_path_name()], 'disabled_auto_getup': disabled}


def author_animation():
    bp = u.load_asset(PREFIX + 'Blueprints/SandboxCharacter_Mover_ABP')
    archive(bp)
    assert 'MSQRecoveryActive' not in u.BlueprintEditorLibrary.list_member_variable_names(bp, False)
    assert u.BlueprintEditorLibrary.add_member_variable(bp, 'MSQRecoveryActive', u.BlueprintEditorLibrary.get_basic_type_by_name('bool'))
    u.BlueprintEditorLibrary.compile_blueprint(bp)
    ed = graph(bp, 'AnimGraph')
    history = node(ed, 'AnimGraphNode_PoseSearchHistoryCollector_0')
    source = history.find_input_pin('Source')
    previous = list(source.list_connected_pins())
    assert len(previous) == 1
    blend = ed.create_node_from_name('Animation|Blends|BlendPosesbybool', u.Vector2D(650, 0), [])
    snapshot = ed.create_node_from_name('Animation|Poses|PoseSnapshot', u.Vector2D(400, 100), [])
    active = ed.add_get_member_variable_node('MSQRecoveryActive')
    # Named snapshots avoid duplicating the full skeletal pose in reflected Blueprint variables.
    snapshot.find_input_pin('SnapshotName').set_pin_value('MSQ98Recovery')
    pins = {str(p.get_pin_name()): p for p in blend.list_all_pins()}
    expected = ['bActiveValue', 'BlendPose_0', 'BlendPose_1', 'BlendTime_0', 'BlendTime_1', 'Pose']
    assert all(x in pins for x in expected), list(pins)
    connect(active.find_output_pin('MSQRecoveryActive'), pins['bActiveValue'])
    connect(snapshot.find_output_pin('Pose'), pins['BlendPose_0'])
    connect(previous[0], pins['BlendPose_1'])
    pins['BlendTime_0'].set_pin_value('0.0')
    pins['BlendTime_1'].set_pin_value('0.15')
    source.break_pin_links()
    connect(pins['Pose'], source)
    save(bp)
    return {'saved': bp.get_path_name(), 'recovery_snapshot_before_pose_history': True}


def physics_audit():
    mesh = u.load_asset(PREFIX + 'Characters/UEFN_Mannequin/Meshes/SKM_UEFN_Mannequin')
    asset = mesh.get_editor_property('physics_asset')
    result = json.loads(u.PhysicsControlRecoveryLibrary.audit_asset(asset))
    (OUT / 'gasp-physics-before01.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return {'mesh': mesh.get_path_name(), 'asset': asset.get_path_name(), 'bodies': result['bodies']}


def author_physics():
    mesh = u.load_asset(PREFIX + 'Characters/UEFN_Mannequin/Meshes/SKM_UEFN_Mannequin')
    source = mesh.get_editor_property('physics_asset')
    destination = PREFIX + 'Characters/UEFN_Mannequin/Rigs/PA_MSQ98_Recovery'
    assert not u.EditorAssetLibrary.does_asset_exist(destination)
    asset = u.EditorAssetLibrary.duplicate_asset(source.get_path_name(), destination)
    assert asset
    actors = u.get_editor_subsystem(u.EditorActorSubsystem)
    fixture = actors.spawn_actor_from_class(u.SkeletalMeshActor, u.Vector(0,0,0), transient=True)
    component = fixture.skeletal_mesh_component
    component.set_skeletal_mesh_asset(mesh)
    try:
        skin = json.loads(u.PhysicsControlRecoveryLibrary.audit_skin(component))
        (OUT / 'gasp-neutral-skin01.json').write_text(json.dumps(skin), encoding='utf-8')
        assert u.PhysicsControlRecoveryLibrary.configure_gasp_asset(asset, component)
    finally:
        actors.destroy_actor(fixture)
    assert u.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False)
    result = json.loads(u.PhysicsControlRecoveryLibrary.audit_asset(asset))
    (OUT / 'gasp-physics-derived01.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    base = u.load_asset(PREFIX + 'Blueprints/SandboxCharacter_Mover')
    archive(base)
    sub = u.get_engine_subsystem(u.SubobjectDataSubsystem)
    objects = set()
    for handle in sub.k2_gather_subobject_data_for_blueprint(base):
        data = u.SubobjectDataBlueprintFunctionLibrary.get_data(handle)
        obj = u.SubobjectDataBlueprintFunctionLibrary.get_object(data)
        if isinstance(obj, u.SkeletalMeshComponent) and obj not in objects:
            objects.add(obj)
            obj.set_editor_property('physics_asset_override', asset)
    assert len(objects) == 1
    save(base)
    return {'physics_asset': asset.get_path_name(), 'measured_vertices': len(skin['foot_vertices']),
            'foot_bodies': [b for b in result['bodies'] if b['bone'].startswith('foot')]}


def run(operation):
    assert Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve() == ROOT
    assert not u.EditorLevelLibrary.get_pie_worlds(False), 'Stop PIE before asset authoring.'
    if operation == 'inspect':
        return inspect_assets()
    if operation == 'author_control':
        return author_control()
    if operation == 'author_animation':
        return author_animation()
    if operation == 'physics_audit':
        return physics_audit()
    if operation == 'author_physics':
        return author_physics()
    if operation == 'author_recovery_anchor':
        bp = u.load_asset(PREFIX + 'Blueprints/SandboxCharacter_Mover_Ragdoll')
        ed = graph(bp, 'Get_RagdollTransform')
        result = node(ed, 'K2Node_FunctionResult_1').find_input_pin('ReturnValue')
        previous = list(result.list_connected_pins())
        assert len(previous) == 1
        call = bridge_call(ed, 'RagdollAnchor')
        connect(previous[0], call.find_input_pin('SampleAnchor'))
        result.break_pin_links()
        connect(call.find_output_pin('ReturnValue'), result)
        save(bp)
        return {'saved': bp.get_path_name(), 'physical_upright_anchor': True}
    if operation == 'author_profile_limits':
        bp = u.load_asset(PREFIX + 'Blueprints/SandboxCharacter_Mover_Ragdoll')
        ed = graph(bp, 'SetPhysicsProfile')
        source = node(ed, 'K2Node_CallFunction_15').find_then_pin()
        targets = list(source.list_connected_pins())
        call = bridge_call(ed, 'EnforceSampleLimits')
        source.break_pin_links()
        connect(source, call.find_execute_pin())
        for target in targets:
            connect(call.find_then_pin(), target)
        save(bp)
        return {'saved': bp.get_path_name(), 'source_profiles_bounded_before_simulation': True}
    if operation == 'author_getup_limits':
        bp = u.load_asset(PREFIX + 'Blueprints/SandboxCharacter_Mover_Ragdoll')
        ed = graph(bp, 'EventGraph')
        source = node(ed, 'K2Node_CallFunction_5').find_then_pin()
        targets = list(source.list_connected_pins())
        call = bridge_call(ed, 'EnforceSampleLimits')
        source.break_pin_links()
        connect(source, call.find_execute_pin())
        for target in targets:
            connect(call.find_then_pin(), target)
        save(bp)
        return {'saved': bp.get_path_name(), 'getup_control_data_bounded_before_simulation': True}
    if operation == 'remove_optional_mixer_extensions':
        saved = []
        for name in ['SandboxCharacter_Mover_ABP', 'SandboxCharacter_CMC_ABP']:
            bp = u.load_asset(PREFIX + 'Blueprints/' + name)
            archive(bp)
            save(bp)
            saved.append(bp.get_path_name())
        return {'recompiled_without_optional_mixer': saved}
    raise ValueError(operation)
