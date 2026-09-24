"""Focused compile, asset wiring and actual source-function evaluation. No actor/world playback."""
from pathlib import Path
import json,math
import unreal as u
from Scripts.GASPALSLocomotion01.editor import ROOT,OUT,state,graphs,defaults

CHAR='/GASPALS/Blueprints/CBP_SandboxCharacter'
CHILD='/Game/Development/GASPALSLocomotion01/Candidate01/BP_GASPALSEnemy_Candidate01'
ANIM='/GASPALS/Blueprints/ABP_SandboxCharacter'
RIFLE='/GASPALS/OverlaySystem/Overlays/Poses/Rifle/ABP_Overlay_Rifle'
MASC='/GASPALS/OverlaySystem/Overlays/Bases/Masculine/ABP_OverlayBase_Masculine'

def source_speeds(cdo):
    movement=cdo.character_movement
    props=['Gait']
    saved={p:cdo.get_editor_property(p) for p in props}
    saved_movement={p:movement.get_editor_property(p) for p in ['velocity','use_controller_desired_rotation','orient_rotation_to_movement']}
    # Unreal struct wrappers can reference the underlying CDO storage.
    velocity=saved_movement['velocity']
    saved_movement['velocity']=u.Vector(velocity.x,velocity.y,velocity.z)
    result=[]
    try:
        movement.set_editor_property('use_controller_desired_rotation',True)
        movement.set_editor_property('orient_rotation_to_movement',False)
        for gait in range(3):
            cdo.set_editor_property('Gait',type(saved['Gait']).cast(gait))
            for angle in [0,90,180]:
                movement.set_editor_property('velocity',u.Vector(100*math.cos(math.radians(angle)),100*math.sin(math.radians(angle)),0))
                result.append(dict(gait=gait,angle=angle,standing=cdo.call_method('CalculateMaxSpeed'),
                    crouched=cdo.call_method('CalculateMaxCrouchSpeed')))
    finally:
        for p,v in saved.items(): cdo.set_editor_property(p,v)
        for p,v in saved_movement.items(): movement.set_editor_property(p,v)
    return result

def run(label):
    from toolset_registry.helpers import compile_blueprint
    before=state()
    assert not before['pie'] and not before['dirty'],before
    result=dict(before=before,assertions=[])
    def check(condition,name):
        result['assertions'].append(dict(name=name,passed=bool(condition)))
        assert condition,name
    bps={p:u.load_asset(p) for p in [CHAR,CHILD,ANIM,RIFLE,MASC,
        '/GASPALS/OverlaySystem/Overlays/Poses/ABP_OverlayPose_Base',
        '/GASPALS/OverlaySystem/Overlays/Bases/ABP_OverlayBase_Base',
        '/GASPALS/OverlaySystem/ABP_LayerBlending','/GASPALS/Blueprints/PreCMCTick']}
    result['compiled']=[]
    for p,bp in bps.items():
        check(bp is not None,'load '+p)
        # The earlier authoring/compile pass is reusable in this editor session.
        # Compile only a dirty/unknown Blueprint, then inspect its actual status/errors.
        initial_status=str(bp.get_editor_property('status'))
        if 'UP_TO_DATE' not in initial_status and 'UPTODATE' not in initial_status:
            compile_blueprint(bp,False)
        result['compiled'].append(dict(path=p,status=str(bp.get_editor_property('status')),
            parent=u.BlueprintEditorLibrary.get_blueprint_parent_class(bp).get_path_name()))
        errors=[]
        for g in u.BlueprintEditorLibrary.list_graphs(bp):
            errors.extend(u.BlueprintGraphEditor.get_graph_editor(g).list_nodes_with_errors())
        check(not errors,'compile '+p)
    source=u.get_default_object(bps[CHAR].generated_class())
    child=u.get_default_object(bps[CHILD].generated_class())
    check(u.BlueprintEditorLibrary.get_blueprint_parent_class(bps[CHILD])==bps[CHAR].generated_class(),'source character identity inherited')
    check(child.get_editor_property('OverlayBase').name=='MASCULINE','Masculine selected')
    check(child.get_editor_property('OverlayPose').name=='RIFLE','Rifle selected')
    result['source_defaults']=defaults(source)
    result['child_defaults']=defaults(child)
    result['source_movement_defaults']=defaults(source.character_movement)
    result['child_movement_defaults']=defaults(child.character_movement)
    check(result['source_movement_defaults']==result['child_movement_defaults'],'exact source CMC defaults')
    for prop in ['WalkSpeeds','RunSpeeds','SprintSpeeds','CrouchSpeeds','StrafeSpeedMapCurve','MovementStickMode']:
        check(source.get_editor_property(prop)==child.get_editor_property(prop),'source value '+prop)
    result['source_speed_function_results']=source_speeds(source)
    result['child_speed_function_results']=source_speeds(child)
    check(result['source_speed_function_results']==result['child_speed_function_results'],'actual source and child speed functions agree')
    curve=child.get_editor_property('StrafeSpeedMapCurve')
    result['curve_samples']={str(a):curve.get_float_value(a) for a in [0,45,90,135,180]}
    result['rifle_defaults']=defaults(u.get_default_object(bps[RIFLE].generated_class()))
    result['masculine_defaults']=defaults(u.get_default_object(bps[MASC].generated_class()))
    result['source_rifle_states']=json.loads(u.GASPALSLocomotionLibrary.inspect_animation_states(u.get_default_object(bps[RIFLE].generated_class())))
    check(result['source_rifle_states'].get('Aiming',-1)>=0,'source Aiming state exists for actual fire gate')
    check(result['rifle_defaults']['bCanAim']=='True','source rifle can aim')
    mesh=child.mesh.skeletal_mesh_asset
    result['mesh']=mesh.get_path_name()
    result['physics_asset']=mesh.get_editor_property('physics_asset').get_path_name()
    result['source_anim_class']=child.mesh.anim_class.get_path_name()
    check(child.mesh.anim_class==bps[ANIM].generated_class(),'canonical source AnimBP drives the child')
    for name in ['DA_OverlayBase_Masculine','Pose_Masculine_Stand_Idle','Pose_Masculine_Stand_Move','Pose_Masculine_Crouch','Poses_Masculine']:
        check(u.load_asset('/GASPALS/OverlaySystem/Overlays/Bases/Masculine/'+name) is not None,'Masculine dependency '+name)
    registry=u.AssetRegistryHelpers.get_asset_registry()
    opts=u.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True)
    queue=[CHILD,ANIM,RIFLE,MASC]
    packages={}
    missing=[]
    while queue:
        package=queue.pop()
        if package in packages or package.startswith('/Script/'):continue
        if not (package.startswith('/GASPALS/') or package==CHILD): continue
        deps=[str(x) for x in registry.get_dependencies(package,opts)]
        packages[package]=deps
        for d in deps:
            if d.startswith('/Script/'): continue
            if not u.EditorAssetLibrary.does_asset_exist(d): missing.append(dict(owner=package,dependency=d))
            else: queue.append(d)
    result['dependency_packages']=packages
    result['missing_dependencies']=missing
    check(not missing,'source hard/soft dependency closure resolves locally')
    result['plugin_base']=u.PluginBlueprintLibrary.get_plugin_base_dir('GASPALS')
    check('MeridianSquad' in result['plugin_base'],'source plugin is mounted from target project')
    result['after']=state()
    check(not result['after']['pie'],'no Play or simulation')
    path=OUT/('asset-checks-'+label+'.json')
    path.write_text(json.dumps(result,indent=2))
    return dict(assertions=len(result['assertions']),passed=True,compiled=len(bps),closure_packages=len(packages),
        speeds=result['child_speed_function_results'],after=result['after'])
