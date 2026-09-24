"""Focused correction experiments in one transient PIE world; no asset saves."""
from pathlib import Path
import json
import unreal as u
from Scripts.CombatAI01.GASPALSAudit01 import editor as capture
from Scripts.GASPALSLocomotion01.editor import state

OUT = Path('D:/devgames/MeridianSquad/Saved/GASPALSAIFix01')
OUT.mkdir(exist_ok=True)

def actors():
    worlds=u.EditorLevelLibrary.get_pie_worlds(False)
    assert len(worlds)==1
    world=worlds[0]
    enemies=u.GameplayStatics.get_all_actors_of_class(world,u.GASPALSLocomotionFixture)
    assert len(enemies)==1
    enemy=enemies[0]
    character=next(a for a in u.GameplayStatics.get_all_actors_of_class(world,u.Character) if a.get_owner()==enemy)
    return world,enemy,character,u.GameplayStatics.get_player_pawn(world,0)

def run(operation,argument=''):
    current=state()
    assert Path(current['project']).resolve()==Path('D:/devgames/MeridianSquad').resolve()
    capture.OUT=OUT
    if operation=='quit':
        assert not current['pie'] and not current['dirty'],current
        u.SystemLibrary.quit_editor()
        return {'quit_requested':True}
    if operation=='state':
        path=OUT/('editor-state-'+argument+'.json')
        with path.open('x',encoding='utf-8') as f: json.dump(current,f,indent=2)
        return current
    if operation=='sample':
        # Retain the audit schema, but record the actual launch socket where it
        # exists. Earlier audit captures intentionally remain unchanged.
        label,duration=json.loads(argument)
        world,enemy,character,player=actors()
        path=OUT/('samples-'+label+'.json'); assert not path.exists()
        start=u.GameplayStatics.get_time_seconds(world)
        rows=[]; token={}; next_time=[start]
        def tick(_delta):
            now=u.GameplayStatics.get_time_seconds(world)
            if now>=next_time[0]:
                next_time[0]=now+.1
                data=json.loads(enemy.get_dummy_state(False)); c=data.pop('enemy_combat')
                data['combat']={k:v for k,v in c.items() if k not in ['decision_events','tuning_at_status_request']}
                rifle=character.get_editor_property('OverlaySkeletalMesh')
                socket=rifle.does_socket_exist('Muzzle')
                data['barrel']=capture.vector(rifle.get_right_vector())
                data['muzzle']=capture.vector(rifle.get_socket_location('Muzzle') if socket else rifle.get_world_transform().transform_location(u.Vector(0,62,9)))
                data['muzzle_source']='Muzzle socket' if socket else 'local fallback'
                data['head']=capture.vector(character.mesh.get_socket_location('head'))
                rows.append(data)
            if now-start>=duration:
                with path.open('x',encoding='utf-8') as f: json.dump({'start':start,'end':now,'samples':rows},f,indent=2)
                u.unregister_slate_post_tick_callback(token['handle'])
        token['handle']=u.register_slate_post_tick_callback(tick)
        return {'started':start,'duration':duration,'file':str(path)}
    if operation=='setup':
        world,enemy,character,player=actors()
        # Clear pre-test knowledge without changing the production tuning.
        combat=enemy.get_component_by_class(u.EnemyCombatComponent)
        combat.set_enabled(False)
        character.set_actor_location(u.Vector(-1148.834,-937.882,90.163),False,True)
        character.set_actor_rotation(u.Rotator(0,0,0),True)
        player.set_actor_location(u.Vector(450.869,-907.046,90.15),False,True)
        combat.set_enabled(True)
        return {'world_time':u.GameplayStatics.get_time_seconds(world),'enemy':capture.vector(character.get_actor_location()),'player':capture.vector(player.get_actor_location())}
    if operation=='hit':
        world,enemy,character,player=actors()
        bone=argument or 'spine_03'
        point=character.mesh.get_socket_location(bone)
        enemy.apply_external_disturbance(u.Vector(120,0,0),point,bone)
        return {'world_time':u.GameplayStatics.get_time_seconds(world),'bone':bone,'impulse':[120,0,0],'gasp':json.loads(enemy.get_dummy_state(False))['gasp']}
    if operation=='reset':
        world,enemy,character,player=actors()
        enemy.reset_dummy()
        data=json.loads(enemy.get_dummy_state(False))
        result={'world_time':u.GameplayStatics.get_time_seconds(world),'ready':data['ready'],'gasp':data['gasp']}
        if argument:
            with (OUT/('reset-'+argument+'.json')).open('x',encoding='utf-8') as f: json.dump(result,f,indent=2)
        return result
    if operation=='world':
        world,enemy,character,player=actors()
        manager=u.GameplayStatics.get_all_actors_of_class(world,u.CombatProjectileWorld)[0]
        result=json.loads(manager.get_combat_state())
        if argument:
            with (OUT/('world-'+argument+'.json')).open('x',encoding='utf-8') as f: json.dump(result,f,indent=2)
        return result
    if operation=='physical_response':
        world,enemy,character,player=actors()
        mesh=character.mesh; bone='spine_03'
        rows=[]; token={}; start=u.GameplayStatics.get_time_seconds(world)
        path=OUT/('physical-response-'+argument+'.json'); assert not path.exists()
        def read():
            return {'time':u.GameplayStatics.get_time_seconds(world),
                'velocity':capture.vector(mesh.get_physics_linear_velocity(bone)),
                'bone':capture.vector(mesh.get_socket_location(bone)),
                'feet':capture.vector(character.get_actor_location()),
                'simulating':mesh.is_simulating_physics(bone),
                'gasp':json.loads(enemy.get_dummy_state(False))['gasp']}
        rows.append(read())
        enemy.apply_external_disturbance(u.Vector(120,0,0),mesh.get_socket_location(bone),bone)
        def tick(_delta):
            rows.append(read())
            if u.GameplayStatics.get_time_seconds(world)-start>=1:
                with path.open('x',encoding='utf-8') as f: json.dump(rows,f,indent=2)
                u.unregister_slate_post_tick_callback(token['handle'])
        token['handle']=u.register_slate_post_tick_callback(tick)
        return {'started':start,'file':str(path)}
    if operation=='tick_groups':
        world,enemy,character,player=actors()
        rows=[]
        for actor in [enemy,character,character.get_controller()]:
            for obj,field in [(actor,'primary_actor_tick')]+[(c,'primary_component_tick') for c in actor.get_components_by_class(u.ActorComponent)]:
                tick=obj.get_editor_property(field)
                rows.append({'name':obj.get_path_name(),'group':str(tick.get_editor_property('tick_group')),'end':str(tick.get_editor_property('end_tick_group'))})
        with (OUT/('tick-groups-'+argument+'.json')).open('x',encoding='utf-8') as f: json.dump(rows,f,indent=2)
        return rows
    if operation=='pose':
        world,enemy,character,player=actors()
        enemy.get_component_by_class(u.EnemyCombatComponent).set_enabled(False)
        enemy.stop_movement_command()
        enemy.set_crouch_command(argument.startswith('crouch'))
        enemy.set_rifle_aim_target(player.get_actor_location()+u.Vector(0,0,82))
        enemy.set_rifle_stance(u.GASPALSRifleStance.READY if argument.endswith('ready') else u.GASPALSRifleStance.AIM)
        return {'requested_pose':argument}
    if operation=='watch_lean':
        world,enemy,character,player=actors()
        token={}; start=u.GameplayStatics.get_time_seconds(world)
        def tick(_delta):
            g=json.loads(enemy.get_dummy_state(False))['gasp']
            if abs(g['lean_degrees'])>=31 and g['source_aim_weight']>=.99:
                run('anatomy',argument)
                u.unregister_slate_post_tick_callback(token['handle'])
            elif u.GameplayStatics.get_time_seconds(world)-start>15:
                with (OUT/('anatomy-'+argument+'.json')).open('x',encoding='utf-8') as f: json.dump({'timeout':True},f)
                u.unregister_slate_post_tick_callback(token['handle'])
        token['handle']=u.register_slate_post_tick_callback(tick)
        return {'started':start}
    if operation=='anatomy':
        world,enemy,character,player=actors()
        feet=character.get_actor_location()-u.Vector(0,0,character.capsule_component.get_scaled_capsule_half_height())
        rifle=character.get_editor_property('OverlaySkeletalMesh')
        result={'feet':capture.vector(feet),'mesh_scale':capture.vector(character.mesh.get_world_transform().get_editor_property('scale3d')),'barrel':capture.vector(rifle.get_right_vector()),'gasp':json.loads(enemy.get_dummy_state(False))['gasp'],
            'bones':{b:capture.vector(character.mesh.get_socket_location(b)-feet) for b in ['head','spine_05','spine_01','hand_r']},
            'muzzle':capture.vector((rifle.get_socket_location('Muzzle') if rifle.does_socket_exist('Muzzle') else rifle.get_world_transform().transform_location(u.Vector(0,62,9)))-feet),
            'muzzle_socket_present':rifle.does_socket_exist('Muzzle')}
        with (OUT/('anatomy-'+argument+'.json')).open('x',encoding='utf-8') as f: json.dump(result,f,indent=2)
        return result
    if operation=='aimed_run':
        world,enemy,character,player=actors()
        result=capture.run('manual_move','[1,0,false,1.5]')
        enemy.set_rifle_aim_target(player.get_actor_location()+u.Vector(0,0,82))
        enemy.set_rifle_stance(u.GASPALSRifleStance.AIM)
        return result
    if operation=='reload_occlusion':
        world,enemy,character,player=actors()
        combat=enemy.get_component_by_class(u.EnemyCombatComponent)
        start=u.GameplayStatics.get_time_seconds(world)
        original=player.get_actor_location()
        path=OUT/('reload-occlusion-'+argument+'.json')
        assert not path.exists()
        events=[]; token={}; triggered=[False]
        def tick(_delta):
            now=u.GameplayStatics.get_time_seconds(world)
            c=json.loads(combat.get_combat_state())
            if not triggered[0] and c['state']=='Reload':
                triggered[0]=True
                events.append({'event':'hide','combat':{k:v for k,v in c.items() if k not in ['decision_events','tuning_at_status_request','senses']}})
                player.set_actor_location(u.Vector(-2850,-105,90.15),False,True)
            if triggered[0] and c['reloads']>events[0]['combat']['reloads']:
                events.append({'event':'complete','combat':{k:v for k,v in c.items() if k not in ['decision_events','tuning_at_status_request','senses']}})
                player.set_actor_location(original,False,True)
                with path.open('x',encoding='utf-8') as f: json.dump(events,f,indent=2)
                u.unregister_slate_post_tick_callback(token['handle'])
            elif now-start>12:
                player.set_actor_location(original,False,True)
                with path.open('x',encoding='utf-8') as f: json.dump({'timeout':True,'events':events},f,indent=2)
                u.unregister_slate_post_tick_callback(token['handle'])
        token['handle']=u.register_slate_post_tick_callback(tick)
        return {'started':start,'file':str(path)}
    return capture.run(operation,argument)
