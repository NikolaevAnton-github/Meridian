"""Focused asset and runtime evidence, using the existing input/capture harness."""
import importlib
import json
import time
import traceback
from pathlib import Path
import unreal as u
from stage1_tools import state
import unreal68
import verify02

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/CombatSlice01/EnemyPrototype01/Worker'
BASE = '/Game/InfimaGames/TacticalFPSAnimations/'
MESH = BASE + 'Common/Characters/Mannequins/Meshes/SKM_Manny_Simple'

def write(name, data):
    path = OUT / (name + '.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    assert not path.exists(), path
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')
    return data

def action(operation, argument):
    if operation in ['performance', 'frame_rate', 'verify_status']:
        return unreal68.action(operation, argument)
    if operation == 'probe':
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        manager = u.GameplayStatics.get_actor_of_class(world, u.CombatProjectileWorld)
        return write('collision-probe-' + argument, json.loads(manager.probe_enemy(argument.startswith('cover'))))
    if operation == 'sample':
        return sample()
    if operation == 'capture':
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        assert world
        folder = OUT / 'GameViews'
        folder.mkdir(exist_ok=True)
        assert argument.replace('-','').replace('_','').isalnum()
        path = folder / (argument + '.png')
        assert not path.exists()
        u.SystemLibrary.execute_console_command(world, 'Shot filename=' + str(path).replace('\\','/') + ' nosuffix')
        return write('GameViews/' + argument, sample())
    if operation == 'verify':
        assert verify02.RUN is None or verify02.RUN['done']
        importlib.reload(verify02)
        verify02.OUT = OUT
        verify02.sample = sample
        verify02.tick = tick
        return verify02.start(argument)
    if operation == 'handoff':
        current = state()
        assert not current['pie'] and not current['dirty_maps'] and not current['dirty_content'], current
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
        actors = u.GameplayStatics.get_all_actors_of_class(world, u.EnemyPrototypeCharacter)
        assert not actors
        return write('handoff-' + argument, dict(state=current, enemy_actor_leaks=[]))
    if operation == 'dependency_plan':
        registry = u.AssetRegistryHelpers.get_asset_registry()
        options = u.AssetRegistryDependencyOptions(include_hard_package_references=True, include_soft_package_references=False,
            include_editor_only_package_references=False, include_game_package_references=True)
        seeds = ['/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple'] + [
            '/Game/Development/EnemyPrototype01/' + n for n in ['A_EnemyTemplate_Idle','A_EnemyTemplate_Fire','A_EnemyTemplate_Hit','A_Enemy_Left','A_Enemy_Right']]
        queue, seen, rows = list(seeds), set(), []
        while queue:
            p = queue.pop()
            if p in seen or not p.startswith('/Game/'): continue
            seen.add(p)
            deps = [str(d) for d in registry.get_dependencies(p, options)]
            rows.append(dict(package=p, loaded=u.load_asset(p) is not None, hard_dependencies=deps))
            queue.extend(deps)
        return write('dependency-plan-' + argument, dict(seeds=seeds, closure=sorted(seen), assets=rows))
    if operation in ['state', 'close']:
        result = write(operation + '-' + argument, state())
        if operation == 'close':
            assert not result['pie'] and not result['dirty_maps'] and not result['dirty_content'], result
            u.SystemLibrary.quit_editor()
        return result
    if operation == 'audit':
        assert not state()['pie']
        registry = u.AssetRegistryHelpers.get_asset_registry()
        registry.scan_paths_synchronous(['/Game/InfimaGames', '/Game/Characters'], force_rescan=True)
        manifest = json.loads((OUT / ('staged-sources-template.json' if argument == 'template' else 'staged-sources.json')).read_text())
        rows = []
        for entry in manifest['files']:
            p = entry['package']
            obj = u.load_asset(p)
            row = dict(package=p, loaded=bool(obj), type=obj.get_class().get_name() if obj else None)
            if isinstance(obj, u.AnimSequence):
                row.update(skeleton=obj.get_editor_property('skeleton').get_path_name(), length=obj.get_play_length(),
                           additive=str(obj.get_editor_property('additive_anim_type')),
                           root_motion=obj.get_editor_property('enable_root_motion'),
                           base=str(obj.get_editor_property('ref_pose_seq')))
                row['poses'] = []
                for t in [0, obj.get_play_length()*.5]:
                    pose = obj.get_anim_pose_at_time(t, u.AnimPoseEvaluationOptions())
                    row['poses'].append(dict(time=t, bones={b: str(u.AnimPoseExtensions.get_bone_pose(pose,b,u.AnimPoseSpaces.WORLD))
                        for b in ['root','pelvis','head','hand_l','hand_r','foot_l','foot_r','ik_hand_gun']}))
            if isinstance(obj, u.SkeletalMesh):
                comp = u.new_object(u.SkeletalMeshComponent)
                comp.set_skeletal_mesh_asset(obj)
                row.update(skeleton=obj.get_editor_property('skeleton').get_path_name(),
                           physics=str(obj.get_editor_property('physics_asset')), bounds=str(obj.get_bounds()),
                           bones=[dict(name=str(comp.get_bone_name(i)), parent=str(comp.get_parent_bone(comp.get_bone_name(i)))) for i in range(comp.get_num_bones())])
            rows.append(row)
        return write('asset-audit-' + argument, dict(state=state(), assets=rows))
    if operation == 'export':
        source = MESH if argument == '01' else '/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple'
        mesh = u.load_asset(source)
        path = ROOT / ('Assets/Source/EnemyPrototype01/SKM_Manny_Simple_Export' + argument + '.fbx')
        path.parent.mkdir(parents=True, exist_ok=True)
        assert not path.exists()
        task = u.AssetExportTask()
        task.object = mesh
        task.filename = str(path)
        task.automated = True
        task.prompt = False
        task.replace_identical = False
        task.options = u.FbxExportOption()
        task.options.set_editor_property('level_of_detail', False)
        assert u.Exporter.run_asset_export_task(task), task.errors
        return write('source-export-' + argument, dict(source=source, destination=str(path), bytes=path.stat().st_size))
    if operation == 'adapt':
        current = state()
        assert not current['pie'] and not current['dirty_maps'] and all(p.startswith('/Game/Development/EnemyPrototype01/') for p in current['dirty_content']), current
        prefix = '/Game/Development/EnemyPrototype01/'
        selected = {
            'A_EnemyTemplate_Idle': '/Game/Characters/Mannequins/Anims/Rifle/MF_Rifle_Idle_ADS',
            'A_EnemyTemplate_Fire': '/Game/Characters/Mannequins/Anims/Rifle/MM_Rifle_Fire',
            'A_EnemyTemplate_Hit': '/Game/Characters/Mannequins/Anims/Rifle/HitReact/MM_HitReact_Front_Lgt_01',
            'A_Enemy_Left': '/Game/Characters/Mannequins/Anims/Rifle/Walk/MF_Rifle_Walk_Left',
            'A_Enemy_Right': '/Game/Characters/Mannequins/Anims/Rifle/Walk/MF_Rifle_Walk_Right',
        }
        rows = []
        for name, source in selected.items():
            destination = prefix + name
            assert not u.EditorAssetLibrary.does_asset_exist(destination)
            obj = u.EditorAssetLibrary.duplicate_asset(source, destination)
            assert obj
            obj.set_editor_property('additive_anim_type', u.AdditiveAnimationType.AAT_NONE)
            obj.set_editor_property('enable_root_motion', False)
            obj.set_editor_property('force_root_lock', True)
            assert u.EditorAssetLibrary.save_asset(destination)
            pose = obj.get_anim_pose_at_time(0, u.AnimPoseEvaluationOptions())
            rows.append(dict(source=source, destination=destination, head=str(u.AnimPoseExtensions.get_bone_pose(pose,'head',u.AnimPoseSpaces.WORLD))))
        return write('animation-adaptation-' + argument, rows)
    raise ValueError(operation)

def sample():
    row = unreal68.sample()
    world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    enemy = u.GameplayStatics.get_actor_of_class(world, u.EnemyPrototypeCharacter)
    row['enemy'] = json.loads(enemy.get_enemy_state()) if enemy else None
    if enemy:
        row['enemy']['bones'] = {b: verify02.vec(enemy.mesh.get_socket_location(b)) for b in ['head','pelvis','hand_l','hand_r','foot_l','foot_r']}
    return row

def tick(delta):
    """The retained verify02 recorder/input seam with MSQ-69 fixture events."""
    r = verify02.RUN
    try:
        now = u.GameplayStatics.get_time_seconds(r['world']) - r['start']
        enemy = u.GameplayStatics.get_actor_of_class(r['world'], u.EnemyPrototypeCharacter)
        while r['index'] < len(r['config']['events']) and now >= r['config']['events'][r['index']][0]:
            _, key, value = r['config']['events'][r['index']]
            if key == '@move': enemy.set_preview_moving(bool(value))
            elif key == '@fire_pose': enemy.preview_fire()
            elif key == '@track': r['track'] = value
            else:
                r['pawn'].probe_key(key, abs(value), value > 0)
                if value > 0 and not key.startswith('Mouse'): r['held'].add(key)
                else: r['held'].discard(key)
            r['events'].append(dict(t=now, key=key, value=value))
            r['index'] += 1
        if r.get('track') and (enemy.health > 0 or r['track'] == 'pelvis'):
            pc = u.GameplayStatics.get_player_controller(r['world'], 0)
            camera = u.GameplayStatics.get_player_camera_manager(r['world'], 0)
            aim = enemy.mesh.get_socket_location(r['track'])
            pc.set_control_rotation(u.MathLibrary.find_look_at_rotation(camera.get_camera_location(), aim))
        for key in r['held']:
            if key == 'RightMouseButton': r['pawn'].probe_key(key, 1, True)
        row = sample()
        row.update(t=now, wall=time.monotonic()-r['wall'], delta=delta, held=sorted(r['held']))
        r['rows'].append(row)
        if now >= r['config']['duration']: verify02.finish()
    except Exception:
        r['error'] = traceback.format_exc()
        verify02.finish()
