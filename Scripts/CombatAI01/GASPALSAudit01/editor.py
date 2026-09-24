"""Direct AI audit: reads and transient PIE experiments; no production asset edits."""
import json
import math
from pathlib import Path
import unreal as u

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/GASPALSAIAudit01'
OUT.mkdir(parents=True, exist_ok=True)

def vector(v):
    return [v.x, v.y, v.z]

def reflected(obj):
    return json.loads(u.GASPALSLocomotionLibrary.inspect_properties(obj)) if obj else {}

def snapshot(detail=False):
    assert Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve() == ROOT.resolve()
    worlds = u.EditorLevelLibrary.get_pie_worlds(False)
    result = {'pie': [w.get_path_name() for w in worlds], 'enemies': []}
    if not worlds:
        return result
    world = worlds[0]
    result['world_time'] = u.GameplayStatics.get_time_seconds(world)
    player = u.GameplayStatics.get_player_pawn(world, 0)
    result['player'] = {'position': vector(player.get_actor_location()), 'rotation': str(player.get_actor_rotation())} if player else None
    for enemy in u.GameplayStatics.get_all_actors_of_class(world, u.GASPALSLocomotionFixture):
        combat = enemy.get_component_by_class(u.EnemyCombatComponent)
        state = json.loads(combat.get_combat_state())
        props = reflected(enemy)
        character = next(a for a in u.GameplayStatics.get_all_actors_of_class(world, u.Character) if a.get_owner() == enemy)
        body = character.mesh
        rifle = character.get_editor_property('OverlaySkeletalMesh')
        animation = body.get_anim_instance()
        row = {'name': enemy.get_name(), 'combat': state, 'fixture': props,
               'character': reflected(character), 'movement': reflected(character.character_movement),
               'animation': reflected(animation), 'character_position': vector(character.get_actor_location()),
               'body_transform': str(body.get_world_transform()),
               'spine': vector(body.get_socket_location('spine_05')),
               'head': vector(body.get_socket_location('head')),
               'rifle_transform': str(rifle.get_world_transform()),
               'barrel': vector(rifle.get_right_vector()),
               'muzzle': vector(rifle.get_socket_location('Muzzle')) if rifle.does_socket_exist('Muzzle') else vector(rifle.get_world_transform().transform_location(u.Vector(0, 62, 9)))}
        if detail:
            row['body'] = reflected(body)
            row['rifle'] = reflected(rifle)
            row['components'] = [{'name': c.get_name(), 'class': c.get_class().get_name(), 'tick': c.is_component_tick_enabled()} for c in character.get_components_by_class(u.ActorComponent)]
        result['enemies'].append(row)
    return result

def compact(data):
    rows = []
    for e in data.get('enemies', []):
        c = e['combat']
        rows.append({'name': e['name'], 'state': c.get('state'), 'reason': c.get('reason'),
                     'shots': c.get('shots'), 'feet': c.get('feet'), 'visible': c.get('visible'),
                     'barrel': e['barrel'], 'muzzle': e['muzzle'],
                     'velocity': e['movement'].get('Velocity')})
    return {'world_time': data.get('world_time'), 'enemies': rows}

def run(operation, argument=''):
    if operation == 'manual_move':
        x, y, walk, duration = json.loads(argument)
        world = u.EditorLevelLibrary.get_pie_worlds(False)[0]
        enemy = u.GameplayStatics.get_all_actors_of_class(world, u.GASPALSLocomotionFixture)[0]
        combat = enemy.get_component_by_class(u.EnemyCombatComponent)
        was_enabled = combat.get_editor_property('bEnabled')
        combat.set_enabled(False)
        enemy.set_movement_command(u.Vector(x, y, 0), walk)
        started = u.GameplayStatics.get_time_seconds(world)
        token = {}
        def stop(_delta):
            if u.GameplayStatics.get_time_seconds(world) - started >= duration:
                enemy.stop_movement_command()
                u.unregister_slate_post_tick_callback(token['handle'])
        token['handle'] = u.register_slate_post_tick_callback(stop)
        return {'was_enabled': was_enabled, 'started': started, 'duration': duration}
    if operation == 'resume_combat':
        world = u.EditorLevelLibrary.get_pie_worlds(False)[0]
        for enemy in u.GameplayStatics.get_all_actors_of_class(world, u.GASPALSLocomotionFixture):
            enemy.get_component_by_class(u.EnemyCombatComponent).set_enabled(True)
        return {'resumed': True}
    if operation == 'sample':
        label, duration = json.loads(argument)
        path = OUT / ('samples-' + label + '.json')
        assert not path.exists()
        worlds = u.EditorLevelLibrary.get_pie_worlds(False)
        assert len(worlds) == 1
        world = worlds[0]
        started = u.GameplayStatics.get_time_seconds(world)
        samples = []
        token = {}
        next_time = [started]
        def tick(_delta):
            now = u.GameplayStatics.get_time_seconds(world)
            if now >= next_time[0]:
                next_time[0] = now + .1
                for enemy in u.GameplayStatics.get_all_actors_of_class(world, u.GASPALSLocomotionFixture):
                    data = json.loads(enemy.get_dummy_state(False))
                    c = data.pop('enemy_combat')
                    data['combat'] = {k:v for k,v in c.items() if k not in ['decision_events', 'tuning_at_status_request']}
                    character = next(a for a in u.GameplayStatics.get_all_actors_of_class(world, u.Character) if a.get_owner() == enemy)
                    rifle = character.get_editor_property('OverlaySkeletalMesh')
                    data['barrel'] = vector(rifle.get_right_vector())
                    data['muzzle'] = vector(rifle.get_world_transform().transform_location(u.Vector(0,62,9)))
                    data['head'] = vector(character.mesh.get_socket_location('head'))
                    samples.append(data)
            if now - started >= duration:
                path.write_text(json.dumps({'start': started, 'end': now, 'samples': samples}, indent=2), encoding='utf-8')
                u.unregister_slate_post_tick_callback(token['handle'])
        token['handle'] = u.register_slate_post_tick_callback(tick)
        return {'started': started, 'duration': duration, 'file': str(path)}
    if operation == 'place_player':
        world = u.EditorLevelLibrary.get_pie_worlds(False)[0]
        player = u.GameplayStatics.get_player_pawn(world, 0)
        before = vector(player.get_actor_location())
        x, y, z = json.loads(argument)
        moved = player.set_actor_location(u.Vector(x, y, z), False, True)
        return {'before': before, 'after': vector(player.get_actor_location()), 'result': str(moved)}
    if operation == 'throttle':
        settings = u.get_default_object(u.load_class(None, '/Script/UnrealEd.EditorPerformanceSettings'))
        before = settings.get_editor_property('bThrottleCPUWhenNotForeground')
        settings.set_editor_property('bThrottleCPUWhenNotForeground', argument == 'true')
        return {'before': before, 'after': settings.get_editor_property('bThrottleCPUWhenNotForeground')}
    if operation == 'sight':
        world = u.EditorLevelLibrary.get_pie_worlds(False)[0]
        enemy = u.GameplayStatics.get_all_actors_of_class(world, u.GASPALSLocomotionFixture)[0]
        character = next(a for a in u.GameplayStatics.get_all_actors_of_class(world, u.Character) if a.get_owner() == enemy)
        player = u.GameplayStatics.get_player_pawn(world, 0)
        camera = u.GameplayStatics.get_player_camera_manager(world, 0)
        head = character.mesh.get_socket_location('head')
        end = camera.get_camera_location()
        hit = u.SystemLibrary.line_trace_single(world, head, end, u.TraceTypeQuery.TRACE_TYPE_QUERY1, True,
            [enemy, character, player], u.DrawDebugTrace.NONE, True)
        return {'origin': vector(head), 'end': vector(end), 'facing': vector(character.get_actor_forward_vector()), 'hit': str(hit),
                'hit_details': str(hit.to_tuple()) if hit is not None else None,
                'trace_doc': u.SystemLibrary.line_trace_single.__doc__}
    if operation == 'visible_positions':
        world = u.EditorLevelLibrary.get_pie_worlds(False)[0]
        enemy = u.GameplayStatics.get_all_actors_of_class(world, u.GASPALSLocomotionFixture)[0]
        character = next(a for a in u.GameplayStatics.get_all_actors_of_class(world, u.Character) if a.get_owner() == enemy)
        player = u.GameplayStatics.get_player_pawn(world, 0)
        head = character.mesh.get_socket_location('head')
        center = character.get_actor_location()
        result = []
        for distance in [650, 1000, 1600]:
            for angle in [-85, -65, -45, 0, 45, 65, 85]:
                theta = math.radians(character.get_actor_rotation().yaw + angle)
                p = u.Vector(center.x + distance*math.cos(theta), center.y + distance*math.sin(theta), 172.15)
                if abs(p.y)>1100 or abs(p.x)>2900:
                    continue
                hit = u.SystemLibrary.line_trace_single(world, head, p, u.TraceTypeQuery.TRACE_TYPE_QUERY1, True,
                    [enemy, character, player], u.DrawDebugTrace.NONE, True)
                if hit is None:
                    result.append([p.x,p.y,90.15])
        return {'visible_positions': result}
    if operation == 'snapshot':
        data = snapshot(True)
        path = OUT / ('snapshot-' + argument + '.json')
        assert not path.exists(), 'Audit evidence is append-only; use a new label'
        path.write_text(json.dumps(data, indent=2), encoding='utf-8')
        return {'file': str(path), **compact(data)}
    if operation == 'api':
        return {'transform': [n for n in dir(u.Transform) if 'transform' in n],
                'fixture': [n for n in dir(u.GASPALSLocomotionFixture) if 'state' in n or 'command' in n]}
    raise ValueError(operation)
