"""Read-only asset inspection and disposable PIE verification for MSQ-61."""
import json
import importlib
import time
import types
from pathlib import Path
import unreal as u
from stage1_tools import state

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/PurchasedArms01/Worker'


def write(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / (name + '.json')).write_text(json.dumps(value, indent=2), encoding='utf-8')
    return value


def dependency_plan():
    s = state()
    assert not s['pie'] and not s['dirty_maps'] and not s['dirty_content'], s
    registry = u.AssetRegistryHelpers.get_asset_registry()
    registry.search_all_assets(True)
    hard = u.AssetRegistryDependencyOptions(False, True, False, False, False)
    soft = u.AssetRegistryDependencyOptions(True, False, False, False, False)
    selected = json.loads((ROOT / 'Assets/Source/PlayerCharacter01/AnimationAudit01/selected-sources.json').read_text())['files']
    candidates = {r['package'] for r in selected}
    candidates.update(str(a.package_name) for a in registry.get_assets_by_path('/Game/Development/PlayerCharacter01', recursive=True))
    # Explicit constructor roots: native private properties are not exposed to Python.
    base = '/Game/InfimaGames/TacticalFPSAnimations/'
    fp = base + 'Weapons/AssaultRifle/Animations/Character/FP/'
    seeds = {fp + 'Locomotion/A_TFA_FP_AR_' + motion + '_Loop_' + stance
        for motion in ['Idle', 'Walk_F', 'Walk_B', 'Walk_Strafe_L', 'Walk_Strafe_R'] for stance in ['Standing', 'Aimed']}
    seeds.update([fp + 'Poses/A_TFA_FP_AR_Idle_Pose_Standing', fp + 'Poses/A_TFA_FP_AR_Aim_Pose'])
    for suffix in ['', '_Aimed']:
        seeds.add(fp + 'Combat/A_TFA_FP_AR_Reload' + suffix)
        seeds.add(base + 'Weapons/AssaultRifle/Animations/Weapon/FP/A_TFA_FP_WEP_AR_Reload' + suffix)
    seeds.add(base + 'Common/Characters/Mannequins/Meshes/SKM_FP_Manny_Simple')
    seeds.update(base + 'Weapons/AssaultRifle/Meshes/' + n for n in ['SK_TFA_AR', 'SK_TFA_AR_Magazine', 'SM_TFA_AR_Handguard_Default', 'SM_TFA_AR_ATT_Sight_Rear', 'SM_TFA_AR_ATT_Sight_Front'])
    keep, queue, edges, missing = set(), list(seeds), {}, []
    while queue:
        p = queue.pop()
        if p in keep:
            continue
        keep.add(p)
        deps = [str(d) for d in registry.get_dependencies(p, hard)]
        edges[p] = deps
        for d in deps:
            if d.startswith('/Game/'):
                if not u.EditorAssetLibrary.does_asset_exist(d):
                    missing.append([p, d])
                queue.append(d)
    archive = candidates - keep
    external = []
    for p in sorted(archive):
        for options, kind in [(hard, 'hard'), (soft, 'soft')]:
            for r in registry.get_referencers(p, options):
                if str(r).startswith('/Game/') and str(r) not in archive and str(r) not in keep:
                    external.append(dict(package=p, referencer=str(r), kind=kind))
    soft_edges = {p: [str(d) for d in registry.get_dependencies(p, soft) if str(d).startswith('/Game/') and str(d) not in keep] for p in sorted(keep)}
    assert not missing, missing
    return write('dependency-plan', dict(seeds=sorted(seeds), keep=sorted(keep), archive=sorted(archive),
        external_referencers=external, hard_edges=edges, optional_soft_outside_closure=soft_edges))


def telemetry():
    s = state()
    if not s['pie']:
        return s
    world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    pawn = u.GameplayStatics.get_player_pawn(world, 0)
    def vector(v):
        return [v.x, v.y, v.z]
    s['components'] = {}
    for c in pawn.get_components_by_class(u.MeshComponent):
        row = dict(class_name=c.get_class().get_name(), visible=c.is_visible(),
            parent=c.get_attach_parent().get_name() if c.get_attach_parent() else None, socket=str(c.get_attach_socket_name()),
            world=vector(c.get_world_location()), relative=vector(c.get_editor_property('relative_location')))
        for key in ['cast_shadow', 'cast_dynamic_shadow', 'cast_static_shadow', 'cast_hidden_shadow', 'cast_contact_shadow', 'first_person_primitive_type']:
            value = c.get_editor_property(key)
            row[key] = str(value) if key == 'first_person_primitive_type' else value
        if isinstance(c, u.SkeletalMeshComponent):
            row['mesh'] = c.get_skeletal_mesh_asset().get_path_name() if c.get_skeletal_mesh_asset() else None
            row['anim_class'] = c.get_anim_instance().get_class().get_path_name() if c.get_anim_instance() else None
            if c.get_anim_instance() and hasattr(c.get_anim_instance(), 'get_evaluation_state'):
                row['evaluation'] = json.loads(c.get_anim_instance().get_evaluation_state())
            row['bones'] = {}
            for b in ['hand_l', 'hand_r', 'ik_hand_gun', 'root', 'magazine', 'magazine_reserve', 'SOCKET_Magazine', 'SOCKET_Magazine_Reserve', 'SOCKET_Sight_Rear']:
                if c.does_socket_exist(b):
                    t = c.get_socket_transform(b, u.RelativeTransformSpace.RTS_WORLD)
                    row['bones'][b] = dict(location=vector(t.translation), rotation=[t.rotation.x, t.rotation.y, t.rotation.z, t.rotation.w])
        s['components'][c.get_name()] = row
    from analyze import relative, distance
    cs = s['components']
    shown = 'ReserveMagazine' if cs['ReserveMagazine']['visible'] else 'MainMagazine'
    s['displayed_magazine'] = shown
    s['seated_magazine_gap_cm'] = distance(relative(cs[shown]['world'], cs['PurchasedRifle']['bones']['root']),
        [.0072924322, 12.2653608322, -7.0208334923])
    return s


def verify_start(argument):
    """Extend the existing actual-input route verifier with this task's action checks."""
    import purchased_arms_walk as walk
    assert walk._module is None or walk._module._run is None or walk._module._run.done
    importlib.reload(walk)
    name, scope = (argument or 'Acceptance03:full').split(':')
    walk.start(name, scope)
    run = walk._module._run
    walk._module.state = telemetry
    previous_update = run.update
    run.captured = set()
    run.capture_pause = None
    run.capture_resume_at = None
    def capture_once(name, s):
        if name in run.captured:
            return
        run.captured.add(name)
        if 'fade' in name:
            # Freeze an already evaluated frame while HighResShot stalls rendering, then resume
            # on its completion. This prevents a capture stall from skipping the 0.15 s interval.
            assert u.GameplayStatics.set_game_paused(run.world, True)
            run.capture_pause = run.out / (name + '.png')
            run.capture_resume_at = None
        u.SystemLibrary.execute_console_command(run.world, 'HighResShot 1 filename="' + str(run.out / (name + '.png')) + '"')
        (run.out / (name + '.json')).write_text(json.dumps(s, indent=2))
    def update(self):
        if self.capture_pause:
            if self.capture_pause.exists():
                if self.capture_resume_at is None:
                    self.capture_resume_at = time.monotonic() + .15
                elif time.monotonic() >= self.capture_resume_at:
                    # Allow ordinary paused engine frames to consume the capture's large delta.
                    u.GameplayStatics.set_game_paused(self.world, False)
                    self.capture_pause = None
            return
        s = telemetry()
        self.validate_identity(s)
        step = self.plan[self.index]
        kind, name = step[:2]
        for key, c in s['components'].items():
            if key.startswith('CameraProxy'):
                continue
            assert not any(c[k] for k in ['cast_shadow', 'cast_dynamic_shadow', 'cast_static_shadow', 'cast_hidden_shadow', 'cast_contact_shadow']), c
        arms, rifle = (s['components'][n] for n in ['CharacterMesh0', 'PurchasedRifle'])
        assert abs(arms['evaluation']['action_time'] - rifle['evaluation']['action_time']) < .00001
        assert abs(arms['evaluation']['time'] - rifle['evaluation']['time']) < .00001
        if s['reload_time'] >= 3.466667:
            assert s['seated_magazine_gap_cm'] < .05, ('Visible magazine left the seated position', s)
            assert s['components']['MainMagazine']['visible'] != s['components']['ReserveMagazine']['visible']
        if kind == 'move' and name == 'walk_back' and abs(s['velocity'][0]) > 300:
            capture_once('movement', s)
        if kind not in ['aim', 'reload', 'unsupported', 'steer']:
            return previous_update()
        now = time.monotonic()
        age = now - self.step_started
        assert age < 30, (name, s)
        if now - self.last_sample > (.005 if s['reloading'] and s['reload_time'] > 3.4 else .05):
            self.samples.append(dict(t=now-self.started, step=name, **s))
            self.last_sample = now
        if kind == 'aim':
            wanted = step[2]
            if self.settled is None:
                self.settled = now
                self.aim_start_clock = s['animation_time']
            self.keys(['RightMouseButton'] if wanted else [])
            if s['animation_time'] - self.aim_start_clock > .35:
                assert s['aim_requested'] == wanted and abs(s['aim_alpha'] - int(wanted)) < .001
                capture_once(name, s)
                self.advance('Aim press/release evaluated through normal input')
                if wanted:
                    self.keys(['RightMouseButton'])
        elif kind == 'reload':
            aimed, toggle, moving = step[2:]
            if self.settled is None:
                self.action_start_count = s['reload_starts']
                self.action_complete_count = s['reload_completions']
                self.settled = now
                self.reload_toggled = False
                self.repeated_at = set()
                self.action_started = False
                self.action_max_time = 0
                self.action_start_clock = s['animation_time']
                self.keys((['RightMouseButton'] if aimed else []) + ['R'] + (['W'] if moving else []))
                return
            t = s['reload_time']
            if s['reloading']:
                self.action_started = True
                assert s['reload_starts'] == self.action_start_count + 1
                assert abs(s['reload_aim_alpha'] - aimed) < .001
                assert t >= self.action_max_time
                self.action_max_time = t
                if toggle and t > 1.1:
                    self.reload_toggled = True
                held = (['RightMouseButton'] if bool(aimed) != self.reload_toggled else []) + (['W'] if moving else [])
                # Two repeated presses must not restart or enqueue another reload.
                for stamp in [.7, 1.6]:
                    if t >= stamp and stamp not in self.repeated_at:
                        held.append('R')
                        self.repeated_at.add(stamp)
                self.keys(held)
                main, reserve = s['components']['MainMagazine']['visible'], s['components']['ReserveMagazine']['visible']
                assert main == (t < 2.520381) and reserve == (t >= .455137), (t, main, reserve)
                for threshold, suffix in [(.2, 'start'), (.8, 'reserve'), (1.8, 'transfer'), (2.7, 'seated'),
                        (3.47, 'before-fade'), (3.55, 'mid-fade'), (3.63, 'late-fade')]:
                    if t >= threshold:
                        capture_once(name + '-' + suffix, s)
            elif self.action_started and s['reload_completions'] == self.action_complete_count + 1:
                assert s['reload_starts'] == self.action_start_count + 1
                assert s['components']['MainMagazine']['visible'] and not s['components']['ReserveMagazine']['visible']
                expected_aim = bool(aimed) != bool(toggle)
                self.keys(['RightMouseButton'] if expected_aim else [])
                if abs(s['aim_alpha'] - int(expected_aim)) < .001:
                    capture_once(name + '-complete', s)
                    self.advance(dict(max_sample_time=self.action_max_time, reloads_started=s['reload_starts'], completed=s['reload_completions'], aim_after=expected_aim))
                    if expected_aim:
                        self.keys(['RightMouseButton'])
            else:
                # HighResShot can tick Slate while the game world is suspended for capture.
                assert s['animation_time'] - self.action_start_clock < .8, 'Reload did not start/complete'
                # Simulated input is frame scoped; keep the press present until a game tick consumes it.
                self.keys((['RightMouseButton'] if aimed else []) + ['R'] + (['W'] if moving else []))
        elif kind == 'steer':
            if self.settled is None:
                self.settled = now
                self.steer_clock = s['animation_time']
                self.steer_yaw = s['rotation'][1]
                self.steer_turned = False
                self.steer_diagonal = False
                self.steer_aimed = False
            elapsed = s['animation_time'] - self.steer_clock
            if elapsed < .4:
                self.keys(['W', 'D'])
                self.steer_diagonal |= s['move_blend'][0] > .25 and s['move_blend'][1] > .25
            elif elapsed < .9:
                self.keys(['W', 'RightMouseButton'])
                if not self.steer_turned:
                    self.pawn.probe_key('MouseX', 30., True)
                    self.steer_turned = True
                self.steer_aimed |= s['aim_alpha'] > .99 and sum(v*v for v in s['velocity'][:2]) > 10000
            else:
                self.keys(['W'])
                if elapsed > 1.3:
                    assert self.steer_diagonal and self.steer_aimed and abs(s['rotation'][1] - self.steer_yaw) > 1
                    assert s['aim_alpha'] == 0
                    self.advance(dict(diagonal_evaluated=True, aimed_while_walking=True, released_while_walking=True, yaw_change=s['rotation'][1]-self.steer_yaw))
        elif kind == 'unsupported':
            keys = ['LeftMouseButton', 'SpaceBar', 'LeftShift', 'LeftControl', 'C', 'F', 'E', 'Q', 'G', 'One', 'Two', 'Three', 'MouseScrollUp', 'MouseScrollDown']
            if self.settled is None:
                self.settled = now
                self.unsupported_before = s
                self.actor_count = len(u.GameplayStatics.get_all_actors_of_class(self.world, u.Actor))
            self.keys(keys if age < .5 else [])
            if age > 1:
                assert not s['reloading'] and not s['aim_requested'] and s['walking']
                assert s['reload_starts'] == self.unsupported_before['reload_starts']
                assert s['location'] == self.unsupported_before['location']
                assert len(u.GameplayStatics.get_all_actors_of_class(self.world, u.Actor)) == self.actor_count
                self.advance(dict(keys=keys, actor_count_unchanged=True, movement_unchanged=True, action_counts_unchanged=True))
    run.update = types.MethodType(update, run)
    original_finish = run.finish
    def finish(self, error=None):
        if self.capture_pause:
            u.GameplayStatics.set_game_paused(self.world, False)
            self.capture_pause = None
        return original_finish(error)
    run.finish = types.MethodType(finish, run)
    return dict(started=True, plan_steps=len(run.plan))


def action(operation, argument):
    if operation == 'inspect':
        s = state()
        assert 'MeridianSquad' in s['project']
        w = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
        gm = w.get_world_settings().get_editor_property('default_game_mode')
        s['game_mode_override'] = gm.get_path_name() if gm else None
        return write('editor-state-' + (argument or 'initial'), s)
    if operation == 'close':
        s = state()
        assert not s['pie'] and not s['dirty_maps'] and not s['dirty_content'], s
        u.SystemLibrary.execute_console_command(None, 'QUIT_EDITOR')
        return {'close_requested': True}
    if operation == 'plan':
        return dependency_plan()
    if operation == 'telemetry':
        return write('telemetry-' + (argument or 'latest'), telemetry())
    if operation == 'key':
        name, amount, pressed = argument.split(':')
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        pawn = u.GameplayStatics.get_player_pawn(world, 0)
        assert pawn and pawn.get_class() == u.OpeningLobbyCharacter.static_class()
        return dict(handled=pawn.probe_key(name, float(amount), pressed == 'true'))
    if operation == 'capture':
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        assert world and argument.replace('-', '').replace('_', '').isalnum()
        u.SystemLibrary.execute_console_command(world, 'HighResShot 1 filename="' + str(OUT / (argument + '.png')) + '"')
        return write(argument, telemetry())
    if operation == 'reload_tools':
        import purchased_arms_unreal
        importlib.reload(purchased_arms_unreal)
        return {'reloaded': True}
    if operation == 'performance':
        obj = u.get_default_object(u.load_class(None, '/Script/UnrealEd.EditorPerformanceSettings'))
        if argument == 'restore':
            obj.set_editor_property('bThrottleCPUWhenNotForeground', json.loads((OUT / 'performance-before.json').read_text())['throttle'])
        else:
            if not (OUT / 'performance-before.json').exists():
                write('performance-before', dict(throttle=obj.get_editor_property('bThrottleCPUWhenNotForeground')))
            obj.set_editor_property('bThrottleCPUWhenNotForeground', False)
        return {'throttle': obj.get_editor_property('bThrottleCPUWhenNotForeground')}
    if operation == 'fit_data':
        path = '/Game/InfimaGames/TacticalFPSAnimations/Weapons/AssaultRifle/Meshes/'
        result = {}
        for name in ['SM_TFA_AR_Handguard_Default', 'SM_TFA_AR_ATT_Sight_Front', 'SM_TFA_AR_ATT_Sight_Rear']:
            mesh = u.load_asset(path + name)
            sockets = [mesh.find_socket(n) for n in ['SOCKET_Sight_Front', 'SOCKET_Muzzle', 'SOCKET_Laser', 'SOCKET_Grip']]
            result[name] = dict(sockets=[dict(name=str(s.socket_name), location=str(s.relative_location), rotation=str(s.relative_rotation)) for s in sockets if s], bounds=str(mesh.get_bounding_box()))
        return write('fit-data', result)
    if operation == 'verify_start':
        return verify_start(argument)
    if operation == 'verify_status':
        import purchased_arms_walk as walk
        return walk.status()
    if operation == 'cold_load':
        plan = json.loads((OUT / 'dependency-plan.json').read_text())
        registry = u.AssetRegistryHelpers.get_asset_registry()
        options = u.AssetRegistryDependencyOptions(False, True, False, False, False)
        rows = []
        for p in plan['keep']:
            obj = u.load_asset(p)
            deps = [str(d) for d in registry.get_dependencies(p, options)]
            rows.append(dict(package=p, loaded=obj is not None, missing_hard=[d for d in deps if d.startswith('/Game/') and not u.EditorAssetLibrary.does_asset_exist(d)]))
        active_archived = [p for p in plan['archive'] if u.EditorAssetLibrary.does_asset_exist(p)]
        return write('cold-load', dict(assets=rows, active_archived=active_archived,
            passed=all(r['loaded'] and not r['missing_hard'] for r in rows) and not active_archived, state=state()))
    if operation == 'obstacle':
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        pawn = u.GameplayStatics.get_player_pawn(world, 0)
        p = pawn.get_actor_location()
        rows = []
        for actor in u.GameplayStatics.get_all_actors_of_class(world, u.StaticMeshActor):
            c, e = actor.get_actor_bounds(False)
            if abs(c.z - p.z) <= e.z + 100 and abs(c.x - p.x) < e.x + 600 and abs(c.y - p.y) < e.y + 800:
                rows.append(dict(label=actor.get_actor_label(), centre=[c.x,c.y,c.z], extent=[e.x,e.y,e.z], collision=str(actor.static_mesh_component.get_collision_enabled())))
        return write('route-obstacles', rows)
    raise ValueError(operation)
