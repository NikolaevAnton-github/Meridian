"""Focused real-rifle input and collision observations; all state is PIE-local."""
import json
import time
import traceback
import unreal as u
from ed01_editor import ROOT, OUT, LAB, write

ACTIVE = None
TARGETS = {'A': (-1335, -120, 165), 'B': (-1185, -120, 105), 'untouched': (-1230, -120, 200)}

def xyz(v):
    return [v.x, v.y, v.z]

def trace(world, pawn, position):
    x, y, z = position
    hit = u.SystemLibrary.sphere_trace_single(world, u.Vector(x, 280, z), u.Vector(x, -200, z), .5,
        u.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [pawn], u.DrawDebugTrace.NONE)
    if not hit:
        return None
    h = hit.to_tuple()
    return {'blocking': h[0], 'distance': h[3], 'impact': xyz(h[5]),
            'actor': h[9].get_name() if h[9] else None, 'component': h[10].get_name() if h[10] else None}

class Sequence:
    def __init__(self, label):
        assert label in ('normal01', 'slow01', 'normal02', 'slow02', 'normal03', 'slow03', 'normal04', 'normal05', 'slow04', 'cost01', 'readable01', 'readable02', 'readable03')
        assert not (OUT / (label + '-complete.json')).exists()
        self.label = label
        self.world, self.pawn, self.pc, self.shell, self.projectile = actors()
        self.rifle = self.pawn.get_component_by_class(u.CombatRifleComponent)
        self.slow = label.startswith('slow')
        self.capture_exposure_bias = 1.0 if label == 'readable03' else 3.5
        self.started = time.perf_counter()
        self.hits, self.snapshots, self.events = [], [], []
        self.handle = None
        self.performance_settings = u.load_object(None, '/Script/UnrealEd.Default__EditorPerformanceSettings')
        self.throttle_before = self.performance_settings.get_editor_property('bThrottleCPUWhenNotForeground')
        self.performance_settings.set_editor_property('bThrottleCPUWhenNotForeground', False)
        self.gpu_before = u.SystemLibrary.get_console_variable_int_value('r.GPUCsvStatsEnabled')
        self.pc.set_ignore_move_input(True)
        self.pc.set_ignore_look_input(True)
        self.pawn.get_component_by_class(u.CharacterMovementComponent).stop_movement_immediately()
        self.pawn.set_actor_location(u.Vector(-1400, 210, 90.15) if label == 'readable01' else u.Vector(-1260, 290, 90.15), False, True)
        if label.startswith('readable'):
            camera = self.pawn.get_component_by_class(u.CameraComponent)
            settings = camera.get_editor_property('post_process_settings')
            settings.set_editor_property('override_auto_exposure_bias', True)
            settings.set_editor_property('auto_exposure_bias', self.capture_exposure_bias)
            camera.set_editor_property('post_process_settings', settings)
            camera.set_editor_property('post_process_blend_weight', 1)
        self.fixed_pose()
        self.disabled_enemy_components = []
        for actor in u.GameplayStatics.get_all_actors_of_class(self.world, u.Actor):
            component = actor.get_component_by_class(u.EnemyCombatComponent)
            if component:
                component.set_enabled(False)
                self.disabled_enemy_components.append(component.get_path_name())
        self.projectile.on_bullet_hit.add_callable(self.on_hit)
        if self.slow:
            assert self.projectile.is_physics_dummy_enabled()
            self.pawn.probe_key('Y', 1, True)
        u.SystemLibrary.execute_console_command(self.world, 'r.GPUCsvStatsEnabled 1')
        u.SystemLibrary.execute_console_command(self.world, 'csvprofile STARTFILE=../../EnvironmentDestruction01/ED-01/MSQ-141-Candidate01/' + label + '.csv')
        u.SystemLibrary.execute_console_command(self.world, 'csvprofile START')
        self.queue = [(0.3, lambda: self.pawn.probe_key('Y', 0, False)),
            (3, lambda: self.snapshot('intact', True)),
            (5, lambda: self.aim('A')), (5.3, lambda: self.key('LeftMouseButton', True)), (5.6, lambda: self.key('LeftMouseButton', False)),
            (7, self.fixed_pose), (8, lambda: self.snapshot('A-removed', True)),
            (9, lambda: self.aim('A')), (9.3, lambda: self.key('LeftMouseButton', True)), (9.6, lambda: self.key('LeftMouseButton', False)),
            (11, lambda: self.snapshot('A-core-shot')),
            (12, lambda: self.aim('B')), (12.3, lambda: self.key('LeftMouseButton', True)), (12.6, lambda: self.key('LeftMouseButton', False)),
            (14, self.fixed_pose), (16, lambda: self.snapshot('two-regions', True)),
            (21, lambda: self.snapshot('settled', True)),
            (22, lambda: self.key('F7', True)), (22.3, lambda: self.key('F7', False)), (23, lambda: self.snapshot('reset1')),
            (24, lambda: self.aim('A')), (24.3, lambda: self.key('LeftMouseButton', True)), (24.6, lambda: self.key('LeftMouseButton', False)),
            (27, lambda: self.snapshot('repeat1')), (28, lambda: self.key('F7', True)), (28.3, lambda: self.key('F7', False)),
            (29, lambda: self.snapshot('reset2')),
            (30, lambda: self.aim('A')), (30.3, lambda: self.key('LeftMouseButton', True)), (30.6, lambda: self.key('LeftMouseButton', False)),
            (33, lambda: self.snapshot('repeat2')), (34, lambda: self.key('F7', True)), (34.3, lambda: self.key('F7', False)),
            (35, self.fixed_pose), (36, lambda: self.snapshot('reset3', True)), (38, self.finish)]
        if label == 'cost01':
            self.queue = [(3, lambda: self.snapshot('intact')),
                (7, lambda: self.aim('A')), (7.3, lambda: self.key('LeftMouseButton', True)), (7.6, lambda: self.key('LeftMouseButton', False)),
                (9, self.fixed_pose), (10, lambda: self.snapshot('A-removed')), (16, lambda: self.snapshot('settled')),
                (17, lambda: self.key('F7', True)), (17.3, lambda: self.key('F7', False)), (18, lambda: self.snapshot('reset1')), (19, self.finish)]
        if self.slow:
            # Preserve the purchased weapon's busy/recovery gate under slow time.
            # Widely spaced presses exercise destruction without bypassing cadence.
            self.queue = [(0.3, lambda: self.pawn.probe_key('Y', 0, False)), (3, lambda: self.snapshot('intact', True)),
                (5, lambda: self.aim('A')), (5.3, lambda: self.key('LeftMouseButton', True)), (5.6, lambda: self.key('LeftMouseButton', False)),
                (8, self.fixed_pose), (10, lambda: self.snapshot('A-removed', True)),
                (17, lambda: self.aim('A')), (17.3, lambda: self.key('LeftMouseButton', True)), (17.6, lambda: self.key('LeftMouseButton', False)),
                (20, lambda: self.snapshot('A-core-shot')),
                (29, lambda: self.aim('B')), (29.3, lambda: self.key('LeftMouseButton', True)), (29.6, lambda: self.key('LeftMouseButton', False)),
                (32, self.fixed_pose), (38, lambda: self.snapshot('two-regions', True)), (45, lambda: self.snapshot('settled')),
                (46, lambda: self.key('F7', True)), (46.3, lambda: self.key('F7', False)), (48, lambda: self.snapshot('reset1', True)), (50, self.finish)]
        if label.startswith('readable'):
            self.queue = [(t, action) for t, action in self.queue if t < 23]
            self.queue += [(23, self.fixed_pose), (24, lambda: self.snapshot('reset1', True)), (25, self.finish)]
        self.handle = u.register_slate_post_tick_callback(self.tick)

    def key(self, name, pressed):
        accepted = self.pawn.probe_key(name, 1 if pressed else 0, pressed)
        self.events.append({'elapsed': time.perf_counter() - self.started, 'key': name, 'pressed': pressed, 'input_return': accepted})

    def fixed_pose(self):
        self.pc.set_control_rotation(u.MathLibrary.find_look_at_rotation(u.Vector(-1400, 210, 172.15), u.Vector(-1260, -120, 125))
            if self.label == 'readable01' else u.Rotator(pitch=-6, yaw=-90, roll=0))

    def aim(self, name):
        camera = self.pc.player_camera_manager.get_camera_location()
        self.pc.set_control_rotation(u.MathLibrary.find_look_at_rotation(camera, u.Vector(*TARGETS[name])))
        self.events.append({'elapsed': time.perf_counter() - self.started, 'aim': name, 'camera': xyz(camera), 'target': TARGETS[name]})

    def on_hit(self, shot_id, identity, shooter, victim, damage, position, self_hit):
        self.hits.append({'elapsed': time.perf_counter() - self.started, 'shot_id': shot_id,
            'shooter': str(identity), 'victim': victim.get_name() if victim else None, 'damage': damage,
            'position': xyz(position), 'self_hit': self_hit, 'shell': json.loads(self.shell.get_cladding_state())})

    def snapshot(self, label, screenshot=False):
        scales = {'world': u.GameplayStatics.get_global_time_dilation(self.world),
            'hero_custom': self.pawn.get_editor_property('custom_time_dilation'),
            'projectile': self.projectile.get_projectile_time_scale()}
        row = {'label': label, 'elapsed': time.perf_counter() - self.started,
               'world_seconds': u.GameplayStatics.get_time_seconds(self.world), 'scales': scales,
               'shell': json.loads(self.shell.get_cladding_state()), 'rifle': json.loads(self.rifle.get_rifle_state()),
               'projectile': json.loads(self.projectile.get_combat_state()),
               'traces': {k: trace(self.world, self.pawn, v) for k, v in TARGETS.items()},
               'camera': xyz(self.pc.player_camera_manager.get_camera_location()), 'viewport': list(self.pc.get_viewport_size())}
        components = self.shell.get_components_by_class(u.StaticMeshComponent)
        row['actual_mesh_components'] = sorted(c.get_name() for c in components)
        row['actual_simulating_components'] = [c.get_name() for c in components if c.is_simulating_physics()]
        row['tuning'] = {name: self.shell.get_editor_property(name) for name in ('break_threshold', 'release_speed_cm_s', 'release_clearance_cm')}
        if self.label.startswith('readable'):
            row['capture_camera_override'] = {'auto_exposure_bias': self.capture_exposure_bias, 'blend_weight': 1, 'scope': 'PIE camera only; scene lighting and quality unchanged'}
            row['control_rotation'] = str(self.pc.get_control_rotation())
        self.snapshots.append(row)
        if screenshot:
            path = OUT / (self.label + '-' + label + '.png')
            assert not path.exists()
            u.SystemLibrary.execute_console_command(self.world, 'HighResShot 1 filename=' + str(path).replace('\\', '/'))

    def tick(self, delta):
        try:
            elapsed = time.perf_counter() - self.started
            if self.queue and elapsed >= self.queue[0][0]:
                _, action = self.queue.pop(0)
                action()
        except Exception:
            self.finish(traceback.format_exc())

    def finish(self, error=None):
        global ACTIVE
        if self.handle is not None:
            u.unregister_slate_post_tick_callback(self.handle)
            self.handle = None
        self.pawn.probe_key('LeftMouseButton', 0, False)
        self.projectile.on_bullet_hit.remove_callable(self.on_hit)
        u.SystemLibrary.execute_console_command(self.world, 'csvprofile STOP')
        u.SystemLibrary.execute_console_command(self.world, 'r.GPUCsvStatsEnabled ' + str(self.gpu_before))
        self.performance_settings.set_editor_property('bThrottleCPUWhenNotForeground', self.throttle_before)
        cvars = {n: u.SystemLibrary.get_console_variable_float_value(n) for n in
            ('r.ScreenPercentage', 'sg.ResolutionQuality', 'r.AntiAliasingMethod', 'r.VSync', 't.MaxFPS',
             'sg.ViewDistanceQuality', 'sg.ShadowQuality', 'sg.GlobalIlluminationQuality', 'sg.ReflectionQuality',
             'sg.TextureQuality', 'sg.EffectsQuality', 'sg.FoliageQuality', 'r.TSR.History.ScreenPercentage')}
        write(self.label + '-complete', {'error': error, 'duration': time.perf_counter() - self.started,
            'events': self.events, 'hits': self.hits, 'snapshots': self.snapshots, 'quality_cvars': cvars,
            'gpu_csv_before_and_restored': self.gpu_before, 'disabled_enemy_components': self.disabled_enemy_components,
            'background_throttle_before_and_restored': self.throttle_before, 'background_throttle_during_capture': False,
            'notes': ['Existing enemy combat disabled only in PIE for this focused specimen sequence.',
                      'Raw capture includes screenshot/automation and editor overhead. No rendering quality setting changed.']})
        ACTIVE = None

def actors():
    world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    assert world and 'L_OpeningLobby_DestructionLab01' in world.get_path_name()
    pawn = u.GameplayStatics.get_player_pawn(world, 0)
    pc = u.GameplayStatics.get_player_controller(world, 0)
    shell = u.GameplayStatics.get_all_actors_of_class(world, u.DestructibleCladding)[0]
    projectile = u.GameplayStatics.get_all_actors_of_class(world, u.CombatProjectileWorld)[0]
    return world, pawn, pc, shell, projectile

def run(operation, argument):
    global ACTIVE
    world, pawn, pc, shell, projectile = actors()
    if operation == 'runtime-geometry-coordinates':
        result = {}
        for path in ['/Game/OpeningLobby/FunctionalBuild01/Meshes/SM_FB01_TallColumn',
                     '/Game/Development/EnvironmentDestruction01/MSQ141Candidate01/SM_ED01_ColumnBacking']:
            dm = u.DynamicMesh()
            u.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(u.load_asset(path), dm, u.GeometryScriptCopyMeshFromAssetOptions(), u.GeometryScriptMeshReadLOD())
            vertices = u.GeometryScript_MeshQueries.get_all_vertex_positions(dm, False)[1].convert_vector_list_to_array()
            result[path] = {'vertices': [xyz(v) for v in vertices], 'triangles': dm.get_triangle_count()}
        result['copy_options'] = u.GeometryScriptCopyMeshFromAssetOptions.__doc__
        result['weld_doc'] = u.GeometryScript_MeshRepair.weld_mesh_edges.__doc__
        return write('geometry-coordinates', result)
    if operation == 'runtime-hit-api':
        hit = u.SystemLibrary.sphere_trace_single(world, u.Vector(-1335, 280, 165), u.Vector(-1335, -200, 165), .5,
            u.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [pawn], u.DrawDebugTrace.NONE)
        return {'hit': str(hit), 'methods': [n for n in dir(hit) if not n.startswith('_')]}
    if operation == 'runtime-input-state':
        anim = pawn.mesh.get_anim_instance()
        montage = anim.get_current_active_montage()
        return {'flags': {name: pawn.get_editor_property(name) for name in ('bIsBusy', 'bIsRunning', 'bIsSprinting')},
            'montage': montage.get_name() if montage else None, 'position': anim.montage_get_position(montage) if montage else None,
            'rifle': json.loads(pawn.get_component_by_class(u.CombatRifleComponent).get_rifle_state())}
    if operation == 'runtime-readable-setup':
        pc.set_ignore_move_input(True)
        pc.set_ignore_look_input(True)
        pawn.get_component_by_class(u.CharacterMovementComponent).stop_movement_immediately()
        pawn.set_actor_location(u.Vector(-1400, 210, 90.15), False, True)
        pc.set_control_rotation(u.MathLibrary.find_look_at_rotation(u.Vector(-1400, 210, 172.15), u.Vector(-1260, -120, 125)))
        camera = pawn.get_component_by_class(u.CameraComponent)
        settings = camera.get_editor_property('post_process_settings')
        settings.set_editor_property('override_auto_exposure_bias', True)
        settings.set_editor_property('auto_exposure_bias', 3.5)
        camera.set_editor_property('post_process_settings', settings)
        camera.set_editor_property('post_process_blend_weight', 1)
        for a in u.GameplayStatics.get_all_actors_of_class(world, u.Actor):
            combat = a.get_component_by_class(u.EnemyCombatComponent)
            if combat:
                combat.set_enabled(False)
        return {'camera': camera.get_name(), 'exposure_bias': settings.get_editor_property('auto_exposure_bias'),
                'scope': 'Transient player camera override in PIE only; normal lighting/quality retained.'}
    if operation == 'runtime-readable-shot':
        target = u.Vector(*TARGETS[argument])
        pc.set_control_rotation(u.MathLibrary.find_look_at_rotation(pc.player_camera_manager.get_camera_location(), target))
        pawn.probe_key('LeftMouseButton', 1, True)
        return {'pressed_at': argument}
    if operation == 'runtime-readable-pose':
        pawn.probe_key('LeftMouseButton', 0, False)
        pc.set_control_rotation(u.MathLibrary.find_look_at_rotation(u.Vector(-1400, 210, 172.15), u.Vector(-1260, -120, 125)))
        return {'pose_restored': True}
    if operation == 'runtime-readable-capture':
        path = OUT / (argument + '.png')
        assert not path.exists()
        u.SystemLibrary.execute_console_command(world, 'HighResShot 1 filename=' + str(path).replace('\\', '/'))
        return write(argument, {'camera': xyz(pc.player_camera_manager.get_camera_location()),
            'rotation': str(pc.get_control_rotation()), 'exposure_bias': 3.5, 'shell': json.loads(shell.get_cladding_state()),
            'rifle': json.loads(pawn.get_component_by_class(u.CombatRifleComponent).get_rifle_state()),
            'traces': {k: trace(world, pawn, v) for k, v in TARGETS.items()}, 'scope': 'PIE-only camera exposure override; unretouched native screenshot'})
    if operation == 'runtime-collision-inspect':
        core = next(a for a in u.GameplayStatics.get_all_actors_of_class(world, u.StaticMeshActor) if a.get_name() == 'StaticMeshActor_35')
        sm = core.static_mesh_component.static_mesh
        dm = u.DynamicMesh()
        u.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(sm, dm, u.GeometryScriptCopyMeshFromAssetOptions(), u.GeometryScriptMeshReadLOD())
        vertices = u.GeometryScript_MeshQueries.get_all_vertex_positions(dm, False)[1]
        return write('collision-diagnostic', {'core_mesh': sm.get_path_name(), 'body': str(sm.get_editor_property('body_setup').get_editor_property('collision_trace_flag')),
            'vertex_methods': dir(vertices), 'dm_methods': [n for n in dir(u.GeometryScript_ListUtilityFunctions) if 'vector' in n] if hasattr(u, 'GeometryScript_ListUtilityFunctions') else [],
            'shell_component': str(shell.get_components_by_class(u.StaticMeshComponent)[0].get_world_transform()),
            'shell_body': str(shell.get_components_by_class(u.StaticMeshComponent)[0].static_mesh.get_editor_property('body_setup')),
            'core_only_trace': str(u.SystemLibrary.sphere_trace_single(world, u.Vector(-1335, 280, 165), u.Vector(-1335, -200, 165), .5,
            u.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [pawn, shell], u.DrawDebugTrace.NONE).to_tuple())})
    if operation == 'runtime-sequence':
        assert ACTIVE is None
        ACTIVE = Sequence(argument)
        return {'started': argument, 'duration_seconds': 50 if argument.startswith('slow') else (19 if argument == 'cost01' else (25 if argument.startswith('readable') else 38))}
    if operation == 'runtime-cancel':
        if ACTIVE:
            ACTIVE.finish('Cancelled by foreground host')
        return {'active': ACTIVE is not None}
    if operation == 'runtime-inspect':
        return write('runtime-inspect', {'shell': json.loads(shell.get_cladding_state()),
            'rifle': json.loads(pawn.get_component_by_class(u.CombatRifleComponent).get_rifle_state()),
            'projectiles': json.loads(projectile.get_combat_state()),
            'trace_doc': u.SystemLibrary.sphere_trace_single.__doc__, 'hit_doc': u.HitResult.__doc__,
            'screenshot_doc': u.AutomationLibrary.take_high_res_screenshot.__doc__})
    raise ValueError(operation)
