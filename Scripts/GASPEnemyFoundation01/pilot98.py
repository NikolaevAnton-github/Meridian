"""Isolated fixture commands; existing project harness remains the evidence runner."""
import json
from pathlib import Path
import unreal as u

OUT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())) / 'Saved/CombatSlice01/GASPEnemyFoundation01/Worker'


def actors():
    world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    assert world, 'Requires PIE.'
    fixtures = u.GameplayStatics.get_all_actors_of_class(world, u.GASPEnemyFixture)
    return world, fixtures


def run(operation, argument=''):
    if operation == 'editor_state':
        import unreal68
        subsystem = u.get_editor_subsystem(u.UnrealEditorSubsystem)
        game_world = subsystem.get_game_world()
        world = game_world if game_world else subsystem.get_editor_world()
        settings = u.get_default_object(u.load_class(None, '/Script/UnrealEd.EditorPerformanceSettings'))
        result = dict(project=u.Paths.convert_relative_path_to_full(u.Paths.project_dir()),
            engine=u.SystemLibrary.get_engine_version(), active_level=world.get_path_name(),
            pie_worlds=[w.get_path_name() for w in u.EditorLevelLibrary.get_pie_worlds(False)],
            dirty_packages=[p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_content_packages()] +
                [p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()],
            background_throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground'),
            max_fps=u.SystemLibrary.get_console_variable_float_value('t.MaxFPS'),
            harness_performance_override_pending=unreal68._performance_before is not None,
            fixture_count=len(u.GameplayStatics.get_all_actors_of_class(world, u.PhysicsControlDummy)),
            foundation_count=len(u.GameplayStatics.get_all_actors_with_tag(world, 'MSQ98_GASPEnemy')),
            existing_play_session_preserved=bool(game_world))
        assert not result['harness_performance_override_pending']
        if argument:
            with (OUT / (argument + '.json')).open('x', encoding='utf-8') as stream:
                json.dump(result, stream, indent=2)
        return result
    world, fixtures = actors()
    if operation == 'performance':
        settings = u.get_default_object(u.load_class(None, '/Script/UnrealEd.EditorPerformanceSettings'))
        old = settings.get_editor_property('bThrottleCPUWhenNotForeground')
        settings.set_editor_property('bThrottleCPUWhenNotForeground', False)
        u.SystemLibrary.execute_console_command(world, 't.MaxFPS 30')
        return {'previous_background_throttle': old, 'max_fps': 30}
    if operation == 'spawn':
        manager = u.GameplayStatics.get_actor_of_class(world, u.CombatProjectileWorld)
        manager.set_physics_dummy_enabled(False)
        assert not u.GameplayStatics.get_all_actors_of_class(world, u.GASPEnemyFixture)
        transform = u.Transform(location=u.Vector(-950, 0, 0), rotation=u.Rotator(pitch=0, yaw=180, roll=0))
        statics = u.get_default_object(u.GameplayStatics)
        fixture = statics.call_method('BeginDeferredActorSpawnFromClass', (world, u.GASPEnemyFixture.static_class(), transform,
            u.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, None))
        statics.call_method('FinishSpawningActor', (fixture, transform))
        return {'spawned': fixture.get_path_name()}
    if operation == 'destroy':
        for fixture in fixtures:
            fixture.destroy_actor()
        return {'destroyed': len(fixtures)}
    if operation == 'command':
        data = json.loads(argument)
        for fixture in fixtures:
            fixture.set_movement_command(u.Vector(*data.get('direction', [0,0,0])), data.get('walk', True))
        return {'commanded': len(fixtures)}
    if operation == 'components':
        fixture = fixtures[0]
        pawn = fixture.get_movement_pawn()
        mesh = fixture.body
        pc = pawn.get_component_by_class(u.PhysicsControlComponent)
        result = {'mesh_transform': str(mesh.get_world_transform()), 'collision_profile': str(mesh.get_collision_profile_name()),
                  'applied_profile': str(pawn.get_editor_property('AppliedPhysicsProfile')),
                  'control_data': {str(n): str(pc.get_control_data(n)) for n in pc.get_all_control_names()},
                  'modifier_api': [n for n in dir(pc) if 'modifier' in n and ('get_' in n)]}
        anim = mesh.get_anim_instance()
        result['animation'] = {str(name): str(anim.get_editor_property(name)) for name in ['MSQRecoveryActive']}
        result['animation_class'] = anim.get_class().get_path_name()
        result['tick'] = pc.is_component_tick_enabled()
        result['skeletal_pelvis'] = str(mesh.get_socket_location('pelvis'))
        result['actor_rotation'] = str(pawn.get_actor_rotation())
        result['rotator_test'] = str(u.Rotator(0,180,0))
        result['scale'] = str(pawn.get_actor_scale3d())
        result['visible'] = mesh.is_visible()
        result['mesh_component_count'] = len(pawn.get_components_by_class(u.SkeletalMeshComponent))
        asset = u.load_asset('/GASPEnemyFoundation01/Characters/UEFN_Mannequin/Rigs/PCA_SandboxCharacter')
        result['profiles'] = str(asset.get_editor_property('my_profiles'))
        (OUT / (argument + '.json')).write_text(json.dumps(result, indent=2), encoding='utf-8')
        return {k:v for k,v in result.items() if k not in ['control_data','profiles']}
    if operation == 'view':
        pawn = u.GameplayStatics.get_player_pawn(world, 0)
        pawn.set_actor_location(u.Vector(-500, 0, 110), False, True)
        u.GameplayStatics.get_player_controller(world, 0).set_control_rotation(u.Rotator(pitch=-10,yaw=180,roll=0))
        return {'view': 'pilot front'}
    if operation == 'impulse':
        values = json.loads(argument)
        bone = values.get('bone', 'pelvis')
        fixtures[0].apply_external_disturbance(u.Vector(*values['impulse']), fixtures[0].get_physical_body_location(bone), bone)
        return {'impulse': values}
    if operation == 'profile_refresh':
        pawn = fixtures[0].get_movement_pawn()
        pawn.call_method('SetPhysicsProfile', ('PhysicalAnimation',))
        return {'refreshed': True}
    if operation == 'reset':
        for fixture in fixtures:
            fixture.reset_dummy()
    if operation == 'snapshot' or operation == 'reset':
        rows = [json.loads(fixture.get_dummy_state(True)) for fixture in fixtures]
        if argument:
            (OUT / (argument + '.json')).write_text(json.dumps(rows, indent=2), encoding='utf-8')
        return rows
    raise ValueError(operation)
