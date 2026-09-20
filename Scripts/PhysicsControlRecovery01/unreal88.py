"""Reuse the retained recorder; add only geometry and snapshot acceptance operations."""
import json
from pathlib import Path
import unreal as u
import unreal87
from stage1_tools import state

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlRecovery01/Worker'
unreal87.OUT = OUT
_original_tick = getattr(unreal87, '_msq88_original_tick', unreal87.balance_tick_impl)
unreal87._msq88_original_tick = _original_tick

def write(name, result):
    path = OUT / (name + '.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    assert not path.exists(), path
    path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result

def focused_tick(delta):
    _original_tick(delta)
    r = unreal87.verify02.RUN
    if not r or r.get('done') or not r['config'].get('capture_skin'):
        return
    d = unreal87.unreal85.selected(unreal87.unreal85.actors()[3])
    b = json.loads(d.get_dummy_state(False))['balance']
    if b['state'] == 'STANDING':
        label = 'reset' if b['get_ups'] == 0 else 'recovered'
        if not r.get('skin_' + label):
            result = json.loads(u.PhysicsControlRecoveryLibrary.audit_skin(d.body))
            result['runtime'] = json.loads(d.get_dummy_state(True))
            write(r['config']['name'] + '-skin-' + label, result)
            r['skin_' + label] = True

unreal87.balance_tick_impl = focused_tick

def action(operation, argument):
    if operation == 'collision_api':
        return [name for name in dir(u.CollisionChannel) if name.isupper()]
    if operation == 'verify':
        config = json.loads(argument)
        result = unreal87.action(operation, argument)
        if config.get('capture_collision'):
            d = unreal87.unreal85.selected(unreal87.unreal85.actors()[3])
            channels = ['WORLD_STATIC', 'WORLD_DYNAMIC', 'PAWN', 'PHYSICS_BODY', 'VISIBILITY']
            write(config['name']+'-collision', dict(
                object_type=str(d.body.get_collision_object_type()),
                collision_enabled=str(d.body.get_collision_enabled()),
                responses={name: str(d.body.get_collision_response_to_channel(getattr(u.CollisionChannel, 'ECC_'+name))) for name in channels},
                asset=d.body.get_editor_property('physics_asset_override').get_path_name(),
                note='Live component filter; native SetCollisionResponseToChannel propagates into body shape filters. Per-pair exclusions are audited separately.'))
        if config.get('seed_front'):
            d = unreal87.unreal85.selected(unreal87.unreal85.actors()[3])
            before = json.loads(d.get_dummy_state(True))
            # Controlled front-rest fixture after two directional falls rolled over.
            # Rotate the entire existing physical ragdoll, then let Chaos settle it.
            # This never selects an animation or supplies the get-up's first pose.
            d.apply_external_disturbance(u.Vector(6000,0,0), d.get_physical_body_location('spine_05'), 'spine_05')
            d.body.set_all_physics_linear_velocity(u.Vector(0,0,0), False)
            d.body.set_all_physics_angular_velocity_in_radians(u.Vector(0,0,0), False)
            transform = d.body.get_world_transform()
            pelvis = d.get_physical_body_location('pelvis')
            up = d.get_physical_body_location('spine_05') - pelvis
            left = d.get_physical_body_location('clavicle_l') - d.get_physical_body_location('clavicle_r')
            front = u.MathLibrary.normal(u.MathLibrary.cross_vector_vector(up, left))
            axis = u.MathLibrary.cross_vector_vector(front, u.Vector(0,0,-1))
            q = [axis.x, axis.y, axis.z, 1-front.z]
            length = sum(v*v for v in q)**.5
            delta_rotation = u.Quat(*(v/length for v in q))
            rotation = u.MathLibrary.compose_rotators(transform.rotation.rotator(), delta_rotation.rotator())
            transform.rotation = rotation.quaternion()
            offset = u.MathLibrary.transform_location(u.Transform(rotation=delta_rotation.rotator()), pelvis-transform.translation)
            transform.translation = u.Vector(-970,-320,24) - offset
            d.body.set_world_transform(transform,False,True)
            write(config['name']+'-seed', dict(method='Rigid rotation/translation of live ragdoll; physical settling follows; no source-animation pose seed', before=before, after=json.loads(d.get_dummy_state(True))))
        return result
    if operation == 'derive_asset':
        s = state()
        assert not s['pie'] and not s['dirty_maps'] and not s['dirty_content'], s
        source = '/Game/Characters/Mannequins/Rigs/PA_Mannequin'
        dest = '/Game/Development/PhysicsControlRecovery01/PA_Manny_Recovery01'
        assert not u.EditorAssetLibrary.does_asset_exist(dest)
        asset = u.EditorAssetLibrary.duplicate_asset(source, dest)
        assert asset and u.PhysicsControlRecoveryLibrary.configure_asset(asset)
        assert u.EditorAssetLibrary.save_loaded_asset(asset)
        result = json.loads(u.PhysicsControlRecoveryLibrary.audit_asset(asset))
        write(argument, result)
        return dict(asset=result['asset'], bodies=len(result['bodies']), exclusions=len(result['excluded_pairs']))
    if operation == 'audit_asset':
        asset = u.load_asset('/Game/Characters/Mannequins/Rigs/PA_Mannequin')
        result = json.loads(u.PhysicsControlRecoveryLibrary.audit_asset(asset))
        write(argument, result)
        return dict(asset=result['asset'], bodies=len(result['bodies']), exclusions=len(result['excluded_pairs']))
    if operation == 'audit_skin':
        d = unreal87.unreal85.selected(unreal87.unreal85.actors()[3])
        result = json.loads(u.PhysicsControlRecoveryLibrary.audit_skin(d.body))
        write(argument, result)
        return dict(bones=result['skeleton_bones'], vertices=len(result['foot_vertices']))
    return unreal87.action(operation, argument)
