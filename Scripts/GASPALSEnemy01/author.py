"""Selective GASPALS derivatives and the archived, canonical Mover AnimBP adapter."""
import hashlib
import json
from pathlib import Path
import unreal as u

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/CombatSlice01/GASPALSEnemy01'
PREFIX = '/GASPALSEnemy01/'
RIFLE = '/GASPALS/OverlaySystem/Overlays/Poses/Rifle/'
SKEL = '/GASPEnemyFoundation01/Characters/UEFN_Mannequin/Meshes/SK_UEFN_Mannequin'
POSES = [f'Pose_Rifle_Stand_{stance}_{motion}' for stance in ['Relax','Ready','Aim'] for motion in ['Idle','Move']]
POSES += [f'Pose_Rifle_Crouch_{stance}' for stance in ['Relax','Ready','Aim']]
POSES += ['AO_Rifle_Stand_Sweep','AO_Rifle_Crouch_Sweep']


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def import_poses():
    skeleton = u.load_asset(SKEL)
    result = []
    for name in POSES:
        source = u.load_asset(RIFLE + name)
        target = PREFIX + 'Animations/' + name
        dest = u.load_asset(target) if u.EditorAssetLibrary.does_asset_exist(target) else u.EditorAssetLibrary.duplicate_asset(source.get_path_name(), target)
        assert dest and u.GASPALSAnimationLibrary.assign_skeleton(dest, skeleton), name
        assert u.EditorAssetLibrary.save_loaded_asset(dest, only_if_is_dirty=False)
        source_file = Path('D:/devgames/GASPALS_UE58/Plugins/GASPALS/Content/OverlaySystem/Overlays/Poses/Rifle') / (name+'.uasset')
        target_file = ROOT / 'Plugins/GASPALSEnemy01/Content/Animations' / (name+'.uasset')
        result.append(dict(source=source.get_path_name(), destination=dest.get_path_name(), source_file=str(source_file),
                           source_sha256=digest(source_file), destination_file=str(target_file), destination_sha256=digest(target_file)))
    (OUT / 'pose-import.json').write_text(json.dumps(result, indent=2))
    return result


def import_prop():
    registry = u.AssetRegistryHelpers.get_asset_registry()
    options = u.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True)
    queue = ['/GASPALS/OverlaySystem/Props/Meshes/M4A1']
    packages = set()
    while queue:
        package = queue.pop()
        if package in packages or not package.startswith('/GASPALS/'):
            continue
        packages.add(package)
        queue.extend(str(p) for p in registry.get_dependencies(package, options))
    assert len(packages) < 40, packages
    source_root = Path('D:/devgames/GASPALS_UE58/Plugins/GASPALS/Content')
    rows = []
    for package in sorted(packages):
        relative = package.removeprefix('/GASPALS/') + '.uasset'
        src = source_root / relative
        rows.append(dict(source_package=package, destination_package=package.replace('/GASPALS/','/GASPALSEnemy01/'),
                         source_file=str(src), relative=relative, source_sha256=digest(src), bytes=src.stat().st_size))
    (OUT / 'prop-import-plan.json').write_text(json.dumps(rows, indent=2))
    sources, derivatives = [], []
    for row in rows:
        assert not u.EditorAssetLibrary.does_asset_exist(row['destination_package'])
        sources.append(u.load_asset(row['source_package']))
        derivatives.append(u.EditorAssetLibrary.duplicate_asset(row['source_package'],row['destination_package']))
    assert u.GASPALSAnimationLibrary.remap_imported_references(sources,derivatives)
    for obj in derivatives:
        assert u.EditorAssetLibrary.save_loaded_asset(obj,only_if_is_dirty=False)
    for row in rows:
        target = ROOT / 'Plugins/GASPALSEnemy01/Content' / row['relative']
        assert target.is_file(), target
        assert digest(Path(row['source_file'])) == row['source_sha256']
        row['destination_sha256'] = digest(target)
        row['destination_file'] = str(target)
    (OUT / 'prop-import.json').write_text(json.dumps(rows, indent=2))
    registry.scan_paths_synchronous(['/GASPALSEnemy01'], True)
    return dict(packages=len(rows), bytes=sum(r['bytes'] for r in rows))


def connect(a, b):
    assert a and b and a.try_create_connection(b), (str(a),str(b))


def author_graph():
    # Chooser context types reference this original class. Preserve the exact
    # prior package, then add one bounded adapter while keeping its class identity.
    destination = '/GASPEnemyFoundation01/Blueprints/SandboxCharacter_Mover_ABP'
    package_file = ROOT/'Plugins/GASPEnemyFoundation01/Content/Blueprints/SandboxCharacter_Mover_ABP.uasset'
    before_file = ROOT/'Assets/Source/GASPALSEnemy01/Before/SandboxCharacter_Mover_ABP.uasset'
    before_file.parent.mkdir(parents=True,exist_ok=True)
    if not before_file.exists():
        import shutil
        shutil.copy2(package_file,before_file)
        (OUT/'modified-package-before.json').write_text(json.dumps(dict(package=destination,source=str(package_file),archive=str(before_file),sha256=digest(before_file)),indent=2))
    bp = u.load_asset(destination)
    if u.BlueprintEditorLibrary.get_blueprint_parent_class(bp) == u.GASPALSRifleAnimInstance.static_class():
        ed = u.BlueprintGraphEditor.get_graph_editor(u.BlueprintEditorLibrary.find_graph(bp,'AnimGraph'))
        source_names = set(json.loads((OUT/'original-animgraph-nodes.json').read_text()))
        added = [n for n in ed.list_all_nodes() if n.get_name() not in source_names]
        ed.remove_nodes(added)
        cache = next(n for n in ed.list_all_nodes() if n.get_name()=='AnimGraphNode_SaveCachedPose_0')
        upstream = next(n for n in ed.list_all_nodes() if n.get_name()=='AnimGraphNode_LinkedAnimLayer_4')
        cache.find_input_pin('Pose').break_pin_links()
        connect(upstream.find_output_pin('Pose'),cache.find_input_pin('Pose'))
    else:
        ed = u.BlueprintGraphEditor.get_graph_editor(u.BlueprintEditorLibrary.find_graph(bp,'AnimGraph'))
        (OUT/'original-animgraph-nodes.json').write_text(json.dumps([n.get_name() for n in ed.list_all_nodes()]))
    assert bp
    u.BlueprintEditorLibrary.reparent_blueprint(bp, u.GASPALSRifleAnimInstance.static_class())
    u.BlueprintEditorLibrary.compile_blueprint(bp)
    ed = u.BlueprintGraphEditor.get_graph_editor(u.BlueprintEditorLibrary.find_graph(bp, 'AnimGraph'))
    pos = 0
    created = []

    def create(name):
        nonlocal pos
        pos += 1
        node = ed.create_node_from_name(name, u.Vector2D(-2000+(pos%4)*300,1200+(pos//4)*220), [])
        assert node, name
        created.append(node)
        return node

    def variable(name):
        node = ed.add_get_member_variable_node(name)
        created.append(node)
        return node.find_output_pin(name)

    def sequence(name, time=False):
        node = create('Animation|Sequences|SequenceEvaluator')
        data = node.get_editor_property('node')
        data.set_editor_property('sequence', u.load_asset(PREFIX+'Animations/'+name))
        node.set_editor_property('node', data)
        if time:
            connect(variable('RiflePitchTime'), node.find_input_pin('ExplicitTime'))
        else:
            node.find_input_pin('ExplicitTime').set_pin_value('0.0')
        return node.find_output_pin('Pose')

    def blend(a,b,alpha):
        node = create('Animation|Blends|TwoWayBlend')
        connect(a,node.find_input_pin('A'))
        connect(b,node.find_input_pin('B'))
        connect(variable(alpha),node.find_input_pin('Alpha'))
        return node.find_output_pin('Pose')

    def stance(poses):
        return blend(blend(poses[0],poses[1],'RifleReadyAlpha'),poses[2],'RifleAimAlpha')

    stand = stance([blend(sequence(f'Pose_Rifle_Stand_{s}_Idle'), sequence(f'Pose_Rifle_Stand_{s}_Move'),'RifleMoveAlpha') for s in ['Relax','Ready','Aim']])
    crouch = stance([sequence(f'Pose_Rifle_Crouch_{s}') for s in ['Relax','Ready','Aim']])
    upper = blend(stand,crouch,'RifleCrouchAlpha')
    aim = blend(sequence('AO_Rifle_Stand_Sweep',True),sequence('AO_Rifle_Crouch_Sweep',True),'RifleCrouchAlpha')
    additive = create('Animation|Blends|ApplyMeshSpaceAdditive')
    connect(upper,additive.find_input_pin('Base'))
    connect(aim,additive.find_input_pin('Additive'))
    connect(variable('RifleAimAlpha'),additive.find_input_pin('Alpha'))
    layered = create('Animation|Blends|Layeredblendperbone')
    data = layered.get_editor_property('node')
    branch = u.BranchFilter()
    branch.set_editor_property('bone_name','spine_01')
    branch.set_editor_property('blend_depth',3)
    layer = u.InputBlendPose()
    layer.set_editor_property('branch_filters',[branch])
    data.set_editor_property('layer_setup', [layer])
    data.set_editor_property('mesh_space_rotation_blend', True)
    layered.set_editor_property('node',data)
    cache = next(n for n in ed.list_all_nodes() if n.get_name()=='AnimGraphNode_SaveCachedPose_0')
    source = cache.find_input_pin('Pose')
    previous = list(source.list_connected_pins())
    assert len(previous)==1
    source.break_pin_links()
    connect(previous[0],layered.find_input_pin('BasePose'))
    connect(additive.find_output_pin('Pose'),layered.find_input_pin('BlendPoses_0'))
    connect(variable('RifleAlpha'),layered.find_input_pin('BlendWeights_0'))
    # Keep the left wrist at the imported prop's authored foregrip in right-hand
    # space. The animated elbow supplies the pole, preserving the pose silhouette.
    ik = create('Animation|SkeletalControls|TwoBoneIK')
    data = ik.get_editor_property('node')
    hand = u.BoneReference()
    hand.set_editor_property('bone_name','hand_l')
    right = u.BoneReference()
    right.set_editor_property('bone_name','hand_r')
    effector = u.BoneSocketTarget()
    effector.set_editor_property('bone_reference',right)
    joint = u.BoneSocketTarget()
    joint.set_editor_property('bone_reference',hand)
    data.set_editor_property('ik_bone',hand)
    data.set_editor_property('effector_target',effector)
    data.set_editor_property('effector_location_space',u.BoneControlSpace.BCS_BONE_SPACE)
    data.set_editor_property('joint_target',joint)
    data.set_editor_property('joint_target_location_space',u.BoneControlSpace.BCS_PARENT_BONE_SPACE)
    data.set_editor_property('allow_stretching',False)
    ik.set_editor_property('node',data)
    import math
    angle=math.radians(75)
    sx,sy,sz=9.28313467,17.92407448,2.66232269
    grip=(-7.60517584+math.cos(angle)*sx-math.sin(angle)*sy,
          1.43000278+math.sin(angle)*sx+math.cos(angle)*sy,-.04438320+sz)
    ik.find_input_pin('EffectorLocation').set_pin_value(','.join(str(x) for x in grip))
    ik.find_input_pin('JointTargetLocation').set_pin_value('0,0,0')
    connect(variable('RifleAlpha'),ik.find_input_pin('Alpha'))
    to_component=create('Animation|ConvertSpaces|LocalToComponent')
    to_local=create('Animation|ConvertSpaces|ComponentToLocal')
    correction=create('Animation|SkeletalControls|Transform(Modify)Bone')
    data=correction.get_editor_property('node')
    spine=u.BoneReference()
    spine.set_editor_property('bone_name','spine_01')
    data.set_editor_property('bone_to_modify',spine)
    data.set_editor_property('rotation_mode',u.BoneModificationMode.BMM_ADDITIVE)
    data.set_editor_property('rotation_space',u.BoneControlSpace.BCS_COMPONENT_SPACE)
    correction.set_editor_property('node',data)
    call=ed.add_call_function_node('/Script/MeridianSquad.GASPALSRifleAnimInstance.GetRifleAimCorrection')
    created.append(call)
    connect(variable('AO'),call.find_input_pin('RootRelativeAim'))
    connect(call.find_output_pin('ReturnValue'),correction.find_input_pin('Rotation'))
    connect(variable('RifleAlpha'),correction.find_input_pin('Alpha'))
    connect(layered.find_output_pin('Pose'),to_component.find_input_pin('LocalPose'))
    connect(to_component.find_output_pin('ComponentPose'),correction.find_input_pin('ComponentPose'))
    connect(correction.find_output_pin('Pose'),ik.find_input_pin('ComponentPose'))
    connect(ik.find_output_pin('Pose'),to_local.find_input_pin('ComponentPose'))
    connect(to_local.find_output_pin('Pose'),source)
    ed.add_comment_to_nodes('GASPALS rifle poses adapted to Mover; physical recovery snapshot and ragdoll/get-up stay downstream.',created)
    from toolset_registry.helpers import compile_blueprint
    compile_blueprint(bp,False)
    assert u.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    return dict(asset=bp.get_path_name(),nodes=len(created),errors=str(ed.list_nodes_with_errors()))


def run(operation):
    assert not u.EditorLevelLibrary.get_pie_worlds(False)
    if operation == 'import_poses': return import_poses()
    if operation == 'import_prop': return import_prop()
    if operation == 'author_graph': return author_graph()
    raise ValueError(operation)
