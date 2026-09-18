"""Focused MSQ-68 operations registered on the official Epic MCP server."""
import json
import sys
import traceback
import importlib
import time
from pathlib import Path
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/CombatSlice01/CombatFoundation01/Worker'
for folder in ['OpeningLobby', 'PurchasedArms02', 'CombatFoundation01']:
    sys.path.insert(0, str(ROOT / 'Scripts' / folder))
from stage1_tools import state
import verify02
_performance_before = None
_aim_key = u.Key()
_aim_key.set_editor_property('key_name', 'RightMouseButton')

def write(name, value):
    destination = OUT / (name + '.json')
    destination.parent.mkdir(parents=True, exist_ok=True)
    assert not destination.exists(), destination
    destination.write_text(json.dumps(value, indent=2), encoding='utf-8')
    return value

def action(operation, argument):
    global _performance_before
    if operation.startswith('timing_'):
        import timing82
        if operation == 'timing_reload':
            importlib.reload(timing82)
            return {'reloaded': 'timing82'}
        return timing82.action(operation.removeprefix('timing_'), argument)
    if operation == 'performance':
        obj = u.get_default_object(u.load_class(None, '/Script/UnrealEd.EditorPerformanceSettings'))
        if argument == 'restore':
            assert _performance_before is not None
            obj.set_editor_property('bThrottleCPUWhenNotForeground', _performance_before['throttle'])
            u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),
                                                   't.MaxFPS ' + str(_performance_before['fps']))
            _performance_before = None
        else:
            assert _performance_before is None
            _performance_before = {'throttle': obj.get_editor_property('bThrottleCPUWhenNotForeground'),
                                   'fps': u.SystemLibrary.get_console_variable_float_value('t.MaxFPS')}
            obj.set_editor_property('bThrottleCPUWhenNotForeground', False)
        return {'throttle': obj.get_editor_property('bThrottleCPUWhenNotForeground'),
                'fps': u.SystemLibrary.get_console_variable_float_value('t.MaxFPS')}
    if operation == 'frame_rate':
        assert _performance_before is not None
        limit = float(argument)
        assert 30 <= limit <= 120
        u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),
                                               't.MaxFPS ' + str(limit))
        return {'fps': u.SystemLibrary.get_console_variable_float_value('t.MaxFPS')}
    if operation == 'adapt':
        import adapt68
        return adapt68.run()
    if operation == 'save_magazine':
        from adapt68 import ASSET
        current = state()
        assert not current['pie'] and not current['dirty_maps'] and set(current['dirty_content']) <= {ASSET}, current
        assert u.EditorAssetLibrary.save_asset(ASSET, only_if_is_dirty=False)
        return state()
    if operation == 'sample':
        return sample()
    if operation == 'setup_probe':
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        rows = []
        for target in u.GameplayStatics.get_all_actors_of_class(world, u.CombatTarget):
            point = target.get_actor_location()
            overlaps = u.SystemLibrary.box_overlap_actors(world, point, u.Vector(8, 36, 49),
                [u.ObjectTypeQuery.OBJECT_TYPE_QUERY1], u.Actor, [target])
            rows.append({'target': target.get_name(), 'position': verify02.vec(point),
                         'static_overlaps': [a.get_name() for a in (overlaps or [])]})
        return write('target-setup-' + argument, rows)
    if operation == 'verify':
        assert verify02.RUN is None or verify02.RUN['done']
        importlib.reload(verify02)
        verify02.OUT = OUT
        verify02.sample = sample
        verify02.tick = tick
        return verify02.start(argument)
    if operation == 'verify_status':
        return verify02.status()
    if operation in ['ballistics', 'corrections']:
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        simulation = u.GameplayStatics.get_actor_of_class(world, u.CombatProjectileWorld)
        report = simulation.probe_ballistics() if operation == 'ballistics' else simulation.probe_corrections()
        return write(operation + '-' + argument, json.loads(report))
    if operation == 'target_audit':
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        target = u.GameplayStatics.get_actor_of_class(world, u.CombatTarget)
        material = target.get_component_by_class(u.StaticMeshComponent).get_material(0)
        return write('target-material-' + argument, {'material': material.get_path_name(),
                     'vector_parameters': [str(n) for n in u.MaterialEditingLibrary.get_vector_parameter_names(material)]})
    if operation == 'state':
        return write('editor-state-' + argument, state())
    if operation == 'handoff':
        current = state()
        assert not current['pie'] and not current['dirty_maps'] and not current['dirty_content'], current
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
        leaked = [a.get_name() for a in u.GameplayStatics.get_all_actors_of_class(world, u.Actor)
                  if isinstance(a, (u.CombatTarget, u.CombatProjectileWorld)) or a.actor_has_tag('CombatProbeCover')]
        assert not leaked, leaked
        assert verify02.RUN is None or verify02.RUN['done']
        verify02.RUN = None
        return write('handoff-' + argument, {'state': current, 'editor_gameplay_actor_leaks': leaked})
    if operation == 'close':
        current = state()
        assert not current['pie'] and not current['dirty_maps'] and not current['dirty_content'], current
        write('editor-before-close-' + argument, current)
        u.SystemLibrary.quit_editor()
        return {'close_requested': True}
    if operation == 'audit':
        from editor_toolset.toolsets.blueprint import BlueprintTools as BP
        base = '/Game/InfimaGames/TacticalFPSAnimations/'
        data = u.load_asset(base + 'Weapons/AssaultRifle/Demo/Data/DA_TFA_AssaultRifle')
        config = u.load_asset(base + 'Common/Core/Configs/BP_TFA_BaseConfig')
        values = {name: str(data.get_editor_property(name)) for name in BP.list_variables(config)}
        montages = []
        for key in values:
            if key.startswith('FP_') and any(s in key for s in ['Reload', 'Fire', 'MagCheck']):
                obj = data.get_editor_property(key)
                if not isinstance(obj, u.AnimMontage):
                    continue
                montages.append({'key': key, 'asset': obj.get_path_name(), 'length': obj.get_play_length()})
        return write('live-source-audit', {'state': state(), 'config': values, 'montages': montages})
    raise ValueError(operation)

def sample():
    world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    pawn = u.GameplayStatics.get_player_pawn(world, 0)
    rifle = pawn.get_component_by_class(u.CombatRifleComponent)
    simulation = u.GameplayStatics.get_actor_of_class(world, u.CombatProjectileWorld)
    camera = u.GameplayStatics.get_player_camera_manager(world, 0)
    magazines = []
    for actor in pawn.get_attached_actors(reset_array=True, recursively_include_attached_actors=True):
        if 'BaseMagazine' in actor.get_class().get_name():
            for mesh in actor.get_components_by_class(u.SkeletalMeshComponent):
                inst = mesh.get_anim_instance()
                magazines.append({'socket': str(actor.root_component.get_attach_socket_name()),
                                  'visible': mesh.is_visible(), 'ammo': inst.get_editor_property('AmmoCount'),
                                  'expected': inst.get_combat_magazine_rounds()})
    result = json.loads(pawn.get_probe_state())
    assembly = [pawn, *pawn.get_attached_actors(reset_array=True, recursively_include_attached_actors=True)]
    niagara_count = sum(len(a.get_components_by_class(u.NiagaraComponent)) for a in assembly)
    result.update(rifle=json.loads(rifle.get_rifle_state()), ballistics=json.loads(simulation.get_combat_state()),
                  world_time=u.GameplayStatics.get_time_seconds(world), location=verify02.vec(pawn.get_actor_location()),
                  velocity=verify02.vec(pawn.get_velocity()), camera=verify02.vec(camera.get_camera_location()),
                  view_fov=camera.get_fov_angle(), magazines=magazines, niagara_components=niagara_count,
                  capture_wall_monotonic=time.monotonic())
    pc = u.GameplayStatics.get_player_controller(world, 0)
    result.update(aim_key_down=pc.is_input_key_down(_aim_key),
                  frame_rate_limit=u.SystemLibrary.get_console_variable_float_value('t.MaxFPS'))
    if verify02.RUN and verify02.RUN['config'].get('pose_detail'):
        camera_transform = u.Transform(camera.get_camera_location(), camera.get_camera_rotation())
        result['pose'] = {
            'offsets': {name: verify02.transform(pawn.get_editor_property(name)) for name in
                        ['TargetAimDownSightsOffset', 'CurrentAimDownSightsOffset', 'TargetRecoil', 'CurrentRecoil']},
            'gun_camera': verify02.transform(pawn.mesh.get_socket_transform('ik_hand_gun',
                u.RelativeTransformSpace.RTS_WORLD).make_relative(camera_transform)),
            'evaluation': json.loads(pawn.mesh.get_anim_instance().get_evaluation_state())}
    return result

def tick(delta):
    r = verify02.RUN
    try:
        now = u.GameplayStatics.get_time_seconds(r['world']) - r['start']
        rifle = r['pawn'].get_component_by_class(u.CombatRifleComponent)
        simulation = u.GameplayStatics.get_actor_of_class(r['world'], u.CombatProjectileWorld)
        events = r['config']['events']
        # Explicit reproduction of the retired Smoke01 driver order, never the default.
        legacy_aim_refresh = r['config'].get('legacy_aim_refresh_before_events', False)
        if legacy_aim_refresh and 'RightMouseButton' in r['held']:
            r['pawn'].probe_key('RightMouseButton', 1, True)
        while r['index'] < len(events) and now >= events[r['index']][0]:
            _, key, value = events[r['index']]
            if key == '@ammo':
                assert rifle.probe_ammo(*value)
            elif key == '@scale':
                simulation.set_projectile_time_scale(value)
            elif key == '@speed':
                rifle.set_editor_property('bullet_speed', value)
            elif key == '@cancel':
                rifle.cancel_reload()
            elif key == '@duplicate':
                rifle.probe_duplicate_notify()
            elif key == '@clear':
                simulation.reset_targets()
            elif key == '@reload':
                rifle.request_reload(bool(value))
            elif key == '@capacity':
                simulation.set_editor_property('max_projectiles', value)
            elif key == '@cover':
                assert simulation.probe_cover(value)
            elif key == '@hitch':
                assert 0 <= value <= .6
                time.sleep(value)
            else:
                r['pawn'].probe_key(key, abs(value), value > 0)
                if value > 0 and not key.startswith('Mouse'):
                    r['held'].add(key)
                else:
                    r['held'].discard(key)
            r['events'].append({'t': now, 'key': key, 'value': value})
            r['index'] += 1
        for key in r['held']:
            if key == 'RightMouseButton' and not legacy_aim_refresh:
                r['pawn'].probe_key(key, 1, True)
        row = sample()
        row.update(t=now, wall=time.monotonic() - r['wall'], delta=delta, held=sorted(r['held']))
        r['rows'].append(row)
        if now >= r['config']['duration']:
            verify02.finish()
    except Exception:
        r['error'] = traceback.format_exc()
        verify02.finish()
