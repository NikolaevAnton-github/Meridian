"""MSQ-141 guarded native editor authoring and focused runtime evidence."""
import json
from pathlib import Path
import unreal as u

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/EnvironmentDestruction01/ED-01/MSQ-141-Candidate01'
LAB = '/Game/Maps/L_OpeningLobby_DestructionLab01'

def write(name, data):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / (name + '.json')).open('x', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    return data

def state():
    project = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
    assert project.resolve() == ROOT.resolve()
    subsystem = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    world = subsystem.get_editor_world()
    return {'project': str(project), 'engine': u.SystemLibrary.get_engine_version(),
            'map': world.get_package().get_path_name(),
            'pie': bool(subsystem.get_game_world()),
            'background_cpu_throttle': u.load_object(None, '/Script/UnrealEd.Default__EditorPerformanceSettings').get_editor_property('bThrottleCPUWhenNotForeground'),
            'gpu_csv_enabled': u.SystemLibrary.get_console_variable_int_value('r.GPUCsvStatsEnabled'),
            'python_remote_execution': u.load_object(None, '/Script/PythonScriptPlugin.Default__PythonScriptPluginSettings').get_editor_property('bRemoteExecution'),
            'dirty': [p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_content_packages()] +
                     [p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()]}

def guard():
    current = state()
    assert current['map'] == LAB and not current['pie'] and not current['dirty'], current
    return current

def run(operation, argument=''):
    if operation == 'final-audit':
        current = guard()
        import ed00_editor
        final_actors = ed00_editor.actors()
        before = json.loads((ROOT / 'Saved/EnvironmentDestruction01/ED-00/MSQ-140-Candidate01/lab-loaded.json').read_text())['actors']
        prior = {a['name']: a for a in before}
        final = {a['name']: a for a in final_actors}
        changed = [name for name in prior if final.get(name) != prior[name]]
        added = [name for name in final if name not in prior]
        result = {'editor': current, 'changed_actors_vs_ed00': changed, 'added_actors': added, 'actors': final_actors}
        write('scene-final-audit', result)
        assert changed == ['StaticMeshActor_35'] and added == ['DestructibleCladding_0'], (changed, added)
        return json.dumps({k: v for k, v in result.items() if k != 'actors'})
    if operation == 'geometry-diagnose':
        guard()
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
        all_actors = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
        shell = next(a for a in all_actors if isinstance(a, u.DestructibleCladding))
        core = next(a for a in all_actors if a.get_name() == 'StaticMeshActor_35')
        rows = []
        for start, end in [(u.Vector(-1335, 280, 165), u.Vector(-1335, -200, 165)), (u.Vector(-1335, -200, 165), u.Vector(-1335, 280, 165))]:
            for ignore in [[], [shell], [core]]:
                hit = u.SystemLibrary.sphere_trace_single(world, start, end, .5, u.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ignore, u.DrawDebugTrace.NONE)
                rows.append({'start_y': start.y, 'ignored': [a.get_name() for a in ignore], 'hit': str(hit.to_tuple()) if hit else None})
        meshes = {}
        for component in [core.static_mesh_component, shell.get_components_by_class(u.StaticMeshComponent)[9]]:
            mesh = component.static_mesh
            dm = u.DynamicMesh()
            u.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh, dm, u.GeometryScriptCopyMeshFromAssetOptions(), u.GeometryScriptMeshReadLOD())
            body = mesh.get_editor_property('body_setup')
            meshes[mesh.get_name()] = {'bounds': str(mesh.get_bounding_box()), 'triangle_count': dm.get_triangle_count(),
                'positions': str(u.GeometryScript_MeshQueries.get_triangle_positions(dm, 0)),
                'normal': str(u.GeometryScript_MeshQueries.get_triangle_face_normal(dm, 0)),
                'hulls': len(body.get_editor_property('agg_geom').get_editor_property('convex_elems')),
                'collision': str(body.get_editor_property('collision_trace_flag'))}
        native = u.DynamicMesh()
        u.GeometryScript_Primitives.append_box(native, u.GeometryScriptPrimitiveOptions(), u.Transform())
        meshes['native_box'] = {'positions': str(u.GeometryScript_MeshQueries.get_triangle_positions(native, 0)), 'normal': str(u.GeometryScript_MeshQueries.get_triangle_face_normal(native, 0))}
        return json.dumps(write('geometry-diagnose03', {'traces': rows, 'meshes': meshes}))
    if operation == 'validate-geometry':
        guard()
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
        actors = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
        shell = next(a for a in actors if isinstance(a, u.DestructibleCladding))
        rows = []
        for x, z in [(-1335, 165), (-1185, 105), (-1230, 200), (-1335, 400)]:
            for ignore in [[], [shell]]:
                h = u.SystemLibrary.sphere_trace_single(world, u.Vector(x, 280, z), u.Vector(x, -200, z), .5,
                    u.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ignore, u.DrawDebugTrace.NONE).to_tuple()
                rows.append({'x': x, 'z': z, 'core_only': bool(ignore), 'actor': h[9].get_name(),
                    'component': h[10].get_name(), 'impact': [h[5].x, h[5].y, h[5].z]})
        return json.dumps(write('geometry-validation-' + argument, rows))
    if operation.startswith('runtime-'):
        import importlib
        import ed01_runtime
        if not getattr(ed01_runtime, 'ACTIVE', None):
            importlib.reload(ed01_runtime)
        return json.dumps(ed01_runtime.run(operation, argument))
    if operation in ('author-assets', 'place'):
        import importlib
        import ed01_author
        author = importlib.reload(ed01_author)
        return json.dumps(author.author() if operation == 'author-assets' else author.place())
    if operation == 'api-docs':
        requested = json.loads(argument)
        result = {name: getattr(getattr(u, name.split('.')[0]), name.split('.')[1]).__doc__
                  if '.' in name else getattr(u, name).__doc__ for name in requested}
        return json.dumps(result)
    if operation == 'api':
        guard()
        names = ['GeometryCollectionLibrary', 'GeometryCollectionFactory', 'GeometryScript_AssetUtils',
                 'GeometryScript_MeshAssetFunctions', 'GeometryScript_Primitives', 'GeometryScript_MeshBoolean',
                 'GeometryScript_MeshBasicEditFunctions', 'GeometryScript_Collision', 'GeometryScript_Normals']
        api = {name: [n for n in dir(getattr(u, name)) if not n.startswith('_')]
               for name in names if hasattr(u, name)}
        api['classes'] = [n for n in dir(u) if n.startswith('GeometryScript')]
        write('geometry-api', api)
        return json.dumps(api)
    if operation == 'inspect':
        current = guard()
        import ed00_editor
        current['source_actor'] = next(a for a in ed00_editor.actors() if a['name'] == 'StaticMeshActor_35')
        current['geometry_api'] = [n for n in dir(u) if any(p in n for p in ('GeometryCollection', 'GeometryScript', 'DynamicMesh'))]
        mesh = u.load_asset('/Game/OpeningLobby/FunctionalBuild01/Meshes/SM_FB01_TallColumn')
        current['mesh_bounds'] = str(mesh.get_bounding_box())
        result = write('source-before', current)
        return json.dumps(result)
    if operation == 'state':
        return json.dumps(write('editor-state-' + argument, state()))
    if operation == 'quit':
        guard()
        u.SystemLibrary.quit_editor()
        return json.dumps({'quit_requested': True})
    raise ValueError(operation)
