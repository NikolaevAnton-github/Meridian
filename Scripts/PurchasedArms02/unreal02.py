import json
from pathlib import Path
import unreal as u
from stage1_tools import state
from editor_toolset.toolsets.blueprint import BlueprintTools as BP

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/PurchasedArms02/Worker'

def write(name, value):
    p = OUT / (name + '.json')
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2), encoding='utf-8')
    return value

def audit():
    registry = u.AssetRegistryHelpers.get_asset_registry()
    registry.scan_paths_synchronous(['/Game/InfimaGames/TacticalFPSAnimations'], True)
    names = ['Common/Core/Characters/BP_TFA_BaseCharacter',
        'Common/Core/Characters/ABP_TFA_FP_BaseCharacter',
        'Common/Core/Weapons/BP_TFA_BaseWeapon', 'Common/Core/Weapons/BP_TFA_BaseMagazine',
        'Weapons/AssaultRifle/Meshes/ABP_TFA_AR', 'Weapons/AssaultRifle/Meshes/ABP_TFA_AR_Magazine',
        'Common/Core/Configs/BP_TFA_BaseConfig']
    index = []
    for name in names:
        obj = u.load_asset('/Game/InfimaGames/TacticalFPSAnimations/' + name)
        folder = OUT / 'SourceGraphs' / obj.get_name()
        folder.mkdir(parents=True, exist_ok=True)
        for graph in BP.list_graphs(obj):
            file = graph.get_path_name().split(':')[-1].replace('/', '_').replace(':', '_') + '.dsl'
            target = folder / file
            assert not target.exists(), target
            try:
                target.write_text(BP.read_graph_dsl(graph), encoding='utf-8')
            except Exception as e:
                target.write_text(str(e), encoding='utf-8')
        cdo = u.get_default_object(obj.generated_class())
        values = {}
        for name in BP.list_variables(obj):
            try:
                values[name] = str(cdo.get_editor_property(name))
            except Exception as e:
                values[name] = str(e)
        write('SourceGraphs/' + obj.get_name() + '/defaults', values)
        index.append(dict(asset=obj.get_path_name(), graphs=len(BP.list_graphs(obj))))
    data = u.load_asset('/Game/InfimaGames/TacticalFPSAnimations/Weapons/AssaultRifle/Demo/Data/DA_TFA_AssaultRifle')
    cfg = u.load_asset('/Game/InfimaGames/TacticalFPSAnimations/Common/Core/Configs/BP_TFA_BaseConfig')
    write('SourceGraphs/rifle-config', {n: str(data.get_editor_property(n)) for n in BP.list_variables(cfg)})
    return write('source-audit-index', index)

def action(operation, argument):
    if operation == 'capsule_fix':
        import capsule_fix
        return capsule_fix.run()
    if operation == 'contract':
        assert not state()['pie']
        bp = u.load_asset('/Game/InfimaGames/TacticalFPSAnimations/Common/Core/Characters/BP_TFA_BaseCharacter')
        rows = []
        for graph in BP.list_graphs(bp):
            for node in u.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes():
                title = str(node.get_node_title())
                if title in ['Event BeginPlay','Event Tick'] or node.get_class().get_name() == 'K2Node_EnhancedInputAction':
                    info = BP.get_node_infos([node])[0]
                    rows.append({'graph':graph.get_name(),'title':title,'outputs':{p.name:len(p.connected_pins) for p in info.output_pins}})
        mapping = u.load_asset('/Game/InfimaGames/TacticalFPSAnimations/Common/Core/Inputs/IMC_TFA_Default')
        cdo = u.get_default_object(bp.generated_class())
        return write('final-graph-contract', {'events':rows,'parent':str(BP.get_parent(bp)),
            'mapping_actions':[m.action.get_name() for m in mapping.get_editor_property('default_key_mappings').get_editor_property('mappings')],
            'config':str(cdo.get_editor_property('WeaponConfig')),'fp_mesh':str(cdo.mesh.skeletal_mesh_asset),
            'anim_class':str(cdo.mesh.anim_class),'aimed_fov':cdo.get_editor_property('AimedFOV'),
            'capsule':[cdo.capsule_component.get_unscaled_capsule_radius(),cdo.capsule_component.get_unscaled_capsule_half_height()],
            'state':state()})
    if operation == 'refine':
        import refine02
        return refine02.run()
    if operation == 'walk':
        import walk02
        return walk02.start()
    if operation == 'walk_status':
        import walk02
        return walk02.status()
    if operation == 'cold_load':
        plan = closure()
        assert not plan['missing'] and not plan['forbidden'], plan
        packages = json.loads((OUT/'dependency-closure.json').read_text())['keep']
        failed = [p for p in packages if not u.load_asset(p)]
        return write('cold-load-final', {'packages':len(packages),'failed':failed})
    if operation == 'adapt':
        import adapt
        return adapt.run()
    if operation == 'cleanup':
        import cleanup02
        return cleanup02.run()
    if operation == 'adapt_state':
        bp = u.load_asset('/Game/InfimaGames/TacticalFPSAnimations/Common/Core/Characters/BP_TFA_BaseCharacter')
        return write('adaptation01-state', {'parent': str(BP.get_parent(bp)), 'state': state()})
    if operation == 'key':
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        pawn = u.GameplayStatics.get_player_pawn(world, 0)
        key, amount, pressed = argument.split(':')
        return {'handled': pawn.probe_key(key, float(amount), pressed == 'true')}
    if operation == 'metadata':
        return metadata()
    if operation == 'closure':
        return closure()
    if operation in ['verify', 'verify_status', 'sample']:
        import verify02
        if operation == 'verify':
            import importlib
            importlib.reload(verify02)
        if operation == 'verify':
            return verify02.start(argument)
        if operation == 'verify_status':
            return verify02.status()
        return write('sample-' + (argument or 'latest'), verify02.sample())
    if operation == 'close':
        s = state()
        allowed = {r['package'] for r in json.loads((OUT / 'staging-manifest.json').read_text())['files'] if not r['existed']}
        assert not s['pie'] and not s['dirty_maps'], s
        assert set(s['dirty_content']) <= allowed, s
        write('editor-before-close-' + (argument or 'latest'), s)
        u.SystemLibrary.quit_editor()
        return {'close_requested': True, 'discarded_audit_cache_only': s['dirty_content']}
    if operation == 'state':
        return write('editor-state-' + (argument or 'latest'), state())
    if operation == 'audit':
        return audit()
    if operation == 'nodes':
        return audit_nodes()
    if operation == 'baseline':
        import recovery02
        return recovery02.start(argument)
    if operation == 'baseline_status':
        import recovery02
        return recovery02.status()
    if operation == 'performance':
        obj = u.get_default_object(u.load_class(None, '/Script/UnrealEd.EditorPerformanceSettings'))
        path = OUT / 'performance-before.json'
        if not path.exists():
            write('performance-before', {'throttle': obj.get_editor_property('bThrottleCPUWhenNotForeground')})
        obj.set_editor_property('bThrottleCPUWhenNotForeground', json.loads(path.read_text())['throttle'] if argument == 'restore' else False)
        return {'throttle': obj.get_editor_property('bThrottleCPUWhenNotForeground')}
    raise ValueError(operation)

def audit_nodes():
    result = []
    for row in json.loads((OUT / 'source-audit-index.json').read_text()):
        obj = u.load_asset(row['asset'])
        graphs = []
        for graph in BP.list_graphs(obj):
            editor = u.BlueprintGraphEditor.get_graph_editor(graph)
            def pin(p):
                return dict(name=p.name, value=p.value, type=p.type_id,
                    id=p.pin_id.index_id, direction=str(p.pin_id.direction),
                    links=[dict(node=q.node.get_name(), id=q.index_id, direction=str(q.direction)) for q in p.connected_pins])
            nodes = []
            for info in BP.get_node_infos(editor.list_all_nodes()):
                nodes.append(dict(name=info.node.get_name(), type=info.type_id, class_name=info.node.get_class().get_name(),
                    inputs=[pin(p) for p in info.input_pins], outputs=[pin(p) for p in info.output_pins]))
            graphs.append(dict(path=graph.get_path_name(), nodes=nodes))
        write('SourceGraphs/' + obj.get_name() + '/nodes', graphs)
        result.append(dict(asset=obj.get_name(), nodes=sum(len(g['nodes']) for g in graphs)))
    return result

def metadata():
    from editor_toolset.toolsets.object import ObjectTools
    base = '/Game/InfimaGames/TacticalFPSAnimations/'
    rows = {}
    for suffix in ['Reload_MagCheck', 'Inspecting', 'Fire', 'Run', 'Sprint']:
        obj = u.load_asset(base + 'Common/Core/Inputs/IA_TFA_' + suffix)
        rows[suffix] = []
        for trigger in obj.get_editor_property('triggers'):
            names = list(json.loads(ObjectTools.list_properties(trigger)))
            rows[suffix].append(json.loads(ObjectTools.get_properties(trigger, names)))
    montage = u.load_asset(base + 'Weapons/AssaultRifle/Animations/Character/FP/Locomotion/AM_TFA_FP_AR_Jump_Full')
    rows['jump'] = {'length': montage.sequence_length, 'sections': [str(n) for n in dir(montage) if 'section' in n]}
    cfg = u.load_asset(base + 'Common/Core/Configs/BP_TFA_BaseConfig')
    data = u.load_asset(base + 'Weapons/AssaultRifle/Demo/Data/DA_TFA_AssaultRifle')
    rows['actions'] = {}
    for n in BP.list_variables(cfg):
        if not n.startswith('FP_'): continue
        value = data.get_editor_property(n)
        if isinstance(value, u.AnimMontage):
            rows['actions'][n] = {'name':value.get_name(),'length':value.sequence_length}
        elif isinstance(value,u.Array) and value and isinstance(value[0],u.AnimMontage):
            rows['actions'][n] = [{'name':v.get_name(),'length':v.sequence_length} for v in value]
    return write('input-metadata', rows)

def closure():
    assert not state()['pie'], 'Dependency/load checks require the editor world, outside PIE.'
    registry = u.AssetRegistryHelpers.get_asset_registry()
    hard = u.AssetRegistryDependencyOptions(False,True,False,False,False)
    base = '/Game/InfimaGames/TacticalFPSAnimations/'
    seeds = [base+s for s in ['Common/Core/Characters/BP_TFA_BaseCharacter',
        'Common/Core/Characters/ABP_TFA_FP_BaseCharacter',
        'Common/Characters/Mannequins/Meshes/SKM_FP_Manny_Simple',
        'Common/Core/Inputs/IMC_TFA_Default',
        'Weapons/AssaultRifle/Animations/Character/FP/Locomotion/AM_TFA_FP_AR_Jump_Full']]
    queue = list(seeds)
    edges = {}
    missing = []
    while queue:
        package = queue.pop()
        if package in edges: continue
        if not registry.get_assets_by_package_name(package): missing.append(package)
        deps = [str(d) for d in registry.get_dependencies(package,hard)]
        edges[package] = deps
        queue.extend(d for d in deps if d.startswith('/Game/'))
    forbidden = [p for p in edges if any(s in p for s in ['/Core/UI/','/Environment/','/Demo/Maps/'])]
    result = dict(seeds=seeds, keep=sorted(edges), edges=edges, missing=missing, forbidden=forbidden)
    write('dependency-closure',result)
    return {'count':len(edges),'missing':missing,'forbidden':forbidden}
