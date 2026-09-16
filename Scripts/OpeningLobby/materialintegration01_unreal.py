"""Guarded material overrides and complete reflected-property evidence."""
import json
import re
from pathlib import Path
import unreal as u
from stage1_tools import state
from architecture01_lightstudy import props
from architecture01_reflection import settings

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/OpeningLobby/MaterialIntegration01/WorkerFresh01'
SOURCE = '/Game/Maps/L_OpeningLobby_FunctionalBuild01'
MAP = '/Game/Maps/L_OpeningLobby_MaterialIntegration01'
ASSETS = '/Game/OpeningLobby/MaterialIntegration01'
MATERIALS = ASSETS + '/Materials/M_MI01_'

def write(name, data):
    path = OUT / (name + '.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')
    return data

def guard(candidate=True, clean=False, pie=False):
    s = state()
    project = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve()
    assert project == ROOT, s
    assert s['level'].replace('UEDPIE_0_', '').split('.')[0] == (MAP if candidate else SOURCE), s
    assert s['pie'] == pie, s
    assert all(p.startswith(ASSETS + '/') for p in s['dirty_content']), s
    assert all(p == MAP for p in s['dirty_maps']), s
    if clean:
        assert not s['dirty_maps'] and not s['dirty_content'], s
    return s

def actors():
    return u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()

def snapshot(name, candidate=True):
    s = guard(candidate, clean=True)
    schemas, rows, inventory = {}, {}, []
    for a in actors():
        row = props(a, schemas)
        row.update(label=a.get_actor_label(), transform=re.sub(r'0x[0-9A-Fa-f]+', 'POINTER', str(a.get_actor_transform())), hidden=a.is_temporarily_hidden_in_editor())
        row['components'] = {c.get_name(): props(c, schemas) for c in a.get_components_by_class(u.ActorComponent)}
        rows[a.get_name()] = row
        for c in a.get_components_by_class(u.MeshComponent):
            mesh = c.get_editor_property('static_mesh') if isinstance(c, u.StaticMeshComponent) else None
            inventory.append(dict(actor=a.get_name(), label=a.get_actor_label(), component=c.get_name(), mesh=mesh.get_path_name() if mesh else None,
                materials=[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())],
                overrides=[m.get_path_name() if m else None for m in c.get_editor_property('override_materials')],
                visible=c.get_editor_property('visible'), hidden_in_game=c.get_editor_property('hidden_in_game'),
                actor_hidden=a.get_editor_property('hidden'), collision=str(c.get_collision_enabled()),
                location=str(a.get_actor_location()), bounds=str(a.get_actor_bounds(False))))
    world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
    data = dict(actors=rows, world=props(world, schemas), world_settings=props(world.get_world_settings(), schemas), renderer=settings())
    # Compact large evidence, with all properties retained.
    folder = OUT / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'all-properties.json').write_text(json.dumps(data, separators=(',', ':')))
    (folder / 'property-schemas.json').write_text(json.dumps(schemas, separators=(',', ':')))
    write(name + '/inventory', inventory)
    write(name + '/state', s)
    return dict(actors=len(rows), components=sum(len(r['components']) for r in rows.values()), mesh_components=len(inventory), classes=len(schemas), state=s)

def native_materials():
    lib = u.MaterialEditingLibrary
    schemas, records = {}, {}
    for name in ['Stone', 'Wall', 'Floor', 'Strip', 'Metal', 'Ceiling']:
        m = u.load_asset(MATERIALS + name)
        assert m and m.get_editor_property('blend_mode') == u.BlendMode.BLEND_OPAQUE
        nodes = {}
        def visit(node):
            if node is None or node.get_path_name() in nodes:
                return
            nodes[node.get_path_name()] = props(node, schemas)
            for child in lib.get_inputs_for_material_expression(m, node):
                visit(child)
        inputs = {}
        for key in ['MP_BASE_COLOR', 'MP_ROUGHNESS', 'MP_NORMAL', 'MP_METALLIC', 'MP_WORLD_POSITION_OFFSET']:
            node = lib.get_material_property_input_node(m, getattr(u.MaterialProperty, key))
            inputs[key] = node.get_path_name() if node else None
            visit(node)
        stats = lib.get_statistics(m)
        records[name] = dict(asset=props(m, schemas), inputs=inputs, connected_nodes=nodes,
            statistics={k:getattr(stats,k) for k in ['num_pixel_shader_instructions','num_vertex_shader_instructions','num_samplers']})
        records[name]['textures'] = {t.get_path_name(): props(t, schemas) for t in lib.get_used_textures(m)}
    write('native-materials', records)
    write('native-material-schemas', schemas)
    return {k:dict(nodes=len(v['connected_nodes']), statistics=v['statistics']) for k,v in records.items()}

def action(operation, argument=''):
    OUT.mkdir(parents=True, exist_ok=True)
    if operation == 'inspect':
        result = snapshot('Source', False) if not (OUT / 'Source/all-properties.json').exists() else dict(state=guard(False, True), source_snapshot_already_recorded=True)
        import hashlib
        source_file = ROOT / 'Content/Maps/L_OpeningLobby_FunctionalBuild01.umap'
        result['source_sha256'] = hashlib.sha256(source_file.read_bytes()).hexdigest()
        return write('preflight', result)
    if operation == 'state':
        return state()
    if operation == 'runtime_diagnostic':
        worlds = u.EditorLevelLibrary.get_pie_worlds(True)
        records = []
        for world in worlds:
            pc = u.GameplayStatics.get_player_controller(world,0)
            pawn = u.GameplayStatics.get_player_pawn(world,0)
            manager = u.GameplayStatics.get_player_camera_manager(world,0)
            records.append(dict(world=world.get_path_name(), paused=u.GameplayStatics.is_game_paused(world),
                                seconds=u.GameplayStatics.get_time_seconds(world), pc=str(pc), pawn=str(pawn),
                                local=pc.is_local_controller() if pc else None,
                                manager_location=str(manager.get_camera_location()) if manager else None,
                                view_target=str(pc.get_view_target()) if pc else None))
        return dict(worlds=records, selected_gameworld=str(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()))
    if operation == 'runtime_unthrottle':
        current = u.SystemLibrary.get_console_variable_int_value('Slate.bAllowThrottling')
        assert current == 1 and not (OUT / 'slate-throttle-before.json').exists()
        write('slate-throttle-before', dict(value=current, reason='PIE world time remained zero; EditorEngine.cpp gates world ticks and drawing on Slate throttle'))
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        u.SystemLibrary.execute_console_command(world, 'Slate.bAllowThrottling 0')
        return dict(before=current, now=u.SystemLibrary.get_console_variable_int_value('Slate.bAllowThrottling'))
    if operation == 'runtime_restore':
        guard(True,clean=True)
        before=json.loads((OUT / 'slate-throttle-before.json').read_text())['value']
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
        u.SystemLibrary.execute_console_command(world, 'Slate.bAllowThrottling '+str(before))
        current=u.SystemLibrary.get_console_variable_int_value('Slate.bAllowThrottling')
        assert current==before
        return write('slate-throttle-restored',dict(value=current,matched=True))
    if operation == 'capabilities':
        return dict(material_property=dir(u.MaterialProperty), material_library=[n for n in dir(u.MaterialEditingLibrary) if any(k in n for k in ['input','expression','texture','statistic'])])
    if operation == 'graph_capabilities':
        schema = {}
        for name in ['MaterialExpressionCustom', 'MaterialExpressionTextureObject', 'MaterialExpressionWorldPosition',
                     'MaterialExpressionVertexNormalWS', 'MaterialExpressionScalarParameter', 'CustomInput', 'Texture2D', 'Material']:
            cls = getattr(u, name)
            try:
                schema[name] = json.loads(u.ToolsetLibrary.list_struct_properties(cls.static_class()))
            except Exception:
                schema[name] = str(cls.__doc__)
        write('graph-capabilities', schema)
        return dict(classes={k:list(v) if isinstance(v,dict) else v[:500] for k,v in schema.items()},
                    libraries=[n for n in dir(u.MaterialEditingLibrary) if any(k in n for k in ['input','expression','texture','statistic'])])
    if operation == 'graph_pins':
        m = u.load_asset(ASSETS + '/Materials/M_MI01_Stone')
        return {n.get_name():dict(inputs=list(u.MaterialEditingLibrary.get_material_expression_input_names(n)),
                                 outputs=list(u.MaterialEditingLibrary.get_material_expression_output_names(n)))
                for n in u.MaterialEditingLibrary.get_material_expressions(m)}
    if operation == 'graph_connections':
        m = u.load_asset(ASSETS + '/Materials/M_MI01_Stone')
        lib = u.MaterialEditingLibrary
        return dict(outputs={k:str(lib.get_material_property_input_node(m, getattr(u.MaterialProperty, 'MP_'+k)))
                             for k in ['BASE_COLOR','NORMAL','METALLIC','ROUGHNESS','SPECULAR']},
                    nodes={n.get_name():[str(c) for c in lib.get_inputs_for_material_expression(m,n)] for n in lib.get_material_expressions(m)},
                    editordata=props(m.get_editor_property('editor_only_data'), {}))
    if operation == 'create':
        guard(False, clean=True)
        assert not u.EditorAssetLibrary.does_asset_exist(MAP)
        assert (OUT / 'assembly-contract.md').exists() and (OUT / 'material-mapping.json').exists()
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).new_level_from_template(MAP, SOURCE)
        return write('created', dict(method='LevelEditorSubsystem.new_level_from_template',
                                    source=SOURCE, candidate=MAP, snapshot=snapshot('Template', True)))
    if operation in ['author_material', 'audit_materials', 'repair_unused']:
        import importlib
        import materialintegration01_materials as materials
        materials = importlib.reload(materials)
        if operation == 'repair_unused':
            return materials.repair_unused()
        return materials.create(argument) if operation == 'author_material' else materials.audit()
    if operation == 'bind':
        guard(True, clean=True)
        assert argument in ['Pilot', 'All']
        mapping = json.loads((OUT / 'material-mapping.json').read_text())
        lookup = {(a.get_name(),c.get_name()):c for a in actors() for c in a.get_components_by_class(u.MeshComponent)}
        changes = []
        for row in mapping:
            c = lookup[(row['actor'],row['component'])]
            actual = c.get_material(row['slot']).get_path_name()
            assert actual in [row['old'], row['new']], (row, actual)
            if row['protected_reason'] or (argument == 'Pilot' and not row['pilot']):
                assert actual == row['old']
                continue
            material = u.load_asset(row['new'])
            assert material
            c.set_material(row['slot'], material)
            changes.append(row)
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
        return write('bindings-' + argument, dict(changed=len(changes), rows=changes, state=guard(True,True)))
    if operation.startswith('capture_'):
        import materialintegration01_capture as capture
        if operation == 'capture_prepare':
            import importlib
            capture = importlib.reload(capture)
        return capture.run(operation[len('capture_'):], argument)
    raise ValueError(operation)
