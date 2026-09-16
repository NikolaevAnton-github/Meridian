"""GlassReview01: two bounded native optical recipes through official Epic MCP."""
import json
import re
from pathlib import Path
from contextlib import contextmanager

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'Saved/OpeningLobby/Stage2/Architecture01'
OUT=BASE/'GlassReview01'
SOURCE='/Game/Maps/L_OpeningLobby_Architecture01_LightStudy01'
MAP='/Game/Maps/L_OpeningLobby_Architecture01_GlassReview01'
ASSETS='/Game/OpeningLobby/Architecture01/GlassReview01'
ORIGINAL='/Game/OpeningLobby/Architecture01/Materials/M_A01_Glass.M_A01_Glass'
ROLES={n:('Leaf' if 'EntranceLeaf' in n else 'Fixed') for n in [
    'A01_EntranceUpperGlazing','A01_InnerHighWindow','A01_EntranceSidelight_-1',
    'A01_EntranceSidelight_1','A01_EntranceOverlight','A01_EntranceLeaf_-1','A01_EntranceLeaf_1']}
# Linear RGB, a single neutral green-grey family. Diffuse albedo is the Simple
# Volume scattering albedo, not an opaque base-color replacement. F0 stays .04.
VARIANTS={
    'A':{'Fixed':dict(albedo=[.55,.55,.55],transmission=[.84,.89,.87],roughness=.38),
         'Leaf':dict(albedo=[.08,.08,.08],transmission=[.72,.79,.76],roughness=.12)},
    # Adapted before its first execution after A's mauve scattering cast.
    'B':{'Fixed':dict(albedo=[.55,.55,.55],transmission=[.90,.90,.90],roughness=.32),
         'Leaf':dict(albedo=[.06,.06,.06],transmission=[.68,.74,.71],roughness=.09)}}

def write(name,data):
    p=OUT/(name+'.json');p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,indent=2));return data

def guard(candidate=True,clean=False,pie=False):
    import architecture01_unreal as w
    s=w.state();w.require_project(s['project'])
    assert s['level'].replace('UEDPIE_0_','').split('.')[0]==(MAP if candidate else SOURCE),s
    assert s['pie']==pie,s
    assert all(p.startswith(ASSETS+'/') for p in s['dirty_content']),s
    assert all(p==MAP for p in s['dirty_maps']),s
    if clean:assert not s['dirty_content'] and not s['dirty_maps'],s
    return s

@contextmanager
def config(folder,candidate=True):
    import architecture01_unreal as w
    import architecture01_capture as c
    old=(w.MAP,w.OUT,c.MAP,c.OUT,c.guard)
    w.MAP=c.MAP=MAP if candidate else SOURCE
    w.OUT=c.OUT=folder;folder.mkdir(parents=True,exist_ok=True)
    c.guard=lambda *args,**kw:guard(candidate,clean=True)
    try:yield c
    finally:w.MAP,w.OUT,c.MAP,c.OUT,c.guard=old

def snapshot(name,candidate=True):
    import unreal as u
    import architecture01_unreal as w
    from architecture01_lightstudy import props
    from architecture01_reflection import settings
    guard(candidate,True)
    folder=OUT/name;folder.mkdir(exist_ok=True)
    (folder/'expected-geometry.json').write_bytes((BASE/'expected-geometry.json').read_bytes())
    with config(folder,candidate):audit=w.audit()
    schemas={};rows={}
    for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
        row=props(a,schemas)
        row.update(name=a.get_name(),transform=re.sub(r'0x[0-9A-Fa-f]+','POINTER',str(a.get_actor_transform())),hidden=a.is_temporarily_hidden_in_editor())
        row['components']={c.get_name():props(c,schemas) for c in a.get_components_by_class(u.ActorComponent)}
        rows[a.get_actor_label()]=row
    world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
    data=dict(actors=rows,world_settings=props(world.get_world_settings(),schemas),cvars=settings())
    (folder/'all-properties.json').write_text(json.dumps(data,separators=(',',':')))
    (folder/'property-schemas.json').write_text(json.dumps(schemas,separators=(',',':')))
    return dict(audit=audit,actors=len(rows),state=guard(candidate,True))

def targets():
    import unreal as u
    selected={}
    for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
        c=a.get_component_by_class(u.StaticMeshComponent)
        if c and any(c.get_material(i).get_path_name()==ORIGINAL or c.get_material(i).get_path_name().startswith(ASSETS+'/') for i in range(c.get_num_materials())):
            assert a.get_actor_label() in ROLES and c.get_num_materials()==1
            selected[a.get_actor_label()]=a
    assert set(selected)==set(ROLES)
    return selected

def settings_read():
    import unreal as u
    obj=u.get_default_object(u.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
    perf=u.get_default_object(u.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
    return dict(play={n:re.sub(r'0x[0-9A-Fa-f]+','POINTER',str(obj.get_editor_property(n))) for n in ['NewWindowWidth','NewWindowHeight','CenterNewWindow','NewWindowPosition']},throttle=perf.get_editor_property('bThrottleCPUWhenNotForeground'))

def execute(command):
    import unreal as u
    import architecture01_unreal as w
    import architecture01_capture as c
    from architecture01_reflection import settings
    if command=='preflight':
        guard(False,True);assert not u.EditorAssetLibrary.does_asset_exist(MAP)
        assert not (OUT/'Source').exists()
        return write('preflight',dict(snapshot=snapshot('Source',False),renderer=settings(),roles=ROLES,variants=VARIANTS,capture_settings=settings_read()))
    if command=='create':
        guard(False,True);assert (OUT/'Source/all-properties.json').exists()
        assert not u.EditorAssetLibrary.does_asset_exist(MAP)
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).new_level_from_template(MAP,SOURCE)
        return write('created',dict(source=SOURCE,map=MAP,method='LevelEditorSubsystem.new_level_from_template',snapshot=snapshot('Template')))
    if command.startswith('variant:'):
        guard(True);v=command.split(':')[1];assert v in VARIANTS
        assert not (OUT/('variant-'+v+'.json')).exists(),'No duplicate variant attempts'
        if v=='B':assert all((OUT/'A'/(n+'.png')).exists() for n in ['MetalGlass-90','C3-90','C2-75'])
        lib=u.MaterialEditingLibrary;materials={}
        for role,recipe in VARIANTS[v].items():
            name='M_GR01_'+v+'_'+role;path=ASSETS+'/'+name
            assert not u.EditorAssetLibrary.does_asset_exist(path)
            m=u.AssetToolsHelpers.get_asset_tools().create_asset(name,ASSETS,u.Material,u.MaterialFactoryNew());assert m
            m.set_editor_property('blend_mode',u.BlendMode.BLEND_TRANSLUCENT_COLORED_TRANSMITTANCE)
            m.set_editor_property('two_sided',False);m.set_editor_property('is_thin_surface',True)
            m.set_editor_property('screen_space_reflections',True)
            m.set_editor_property('translucency_lighting_mode',u.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
            slab=lib.create_material_expression(m,u.MaterialExpressionSubstrateSlabBSDF)
            slab.set_editor_property('sub_surface_type',u.MaterialSubSurfaceType.MSS_SIMPLE_VOLUME)
            mfp=lib.create_material_expression(m,u.MaterialExpressionSubstrateTransmittanceToMFP)
            for param,value,target,pin in [('ScatteringAlbedo',recipe['albedo'],slab,'Diffuse Albedo'),('F0',[.04]*3,slab,'F0'),('SurfaceRoughness',recipe['roughness'],slab,'Roughness'),('Transmission',recipe['transmission'],mfp,'TransmittanceColor')]:
                vector=isinstance(value,list)
                n=lib.create_material_expression(m,u.MaterialExpressionVectorParameter if vector else u.MaterialExpressionScalarParameter)
                n.set_editor_property('parameter_name',param)
                n.set_editor_property('default_value',u.LinearColor(*value,1) if vector else value)
                assert lib.connect_material_expressions(n,'',target,pin)
            assert lib.connect_material_expressions(mfp,'MFP',slab,'SSS MFP')
            assert lib.connect_material_property(slab,'',u.MaterialProperty.MP_FRONT_MATERIAL)
            lib.layout_material_expressions(m);lib.recompile_material(m)
            assert u.EditorAssetLibrary.save_loaded_asset(m)
            materials[role]=m
        mapping=[]
        for name,a in targets().items():
            comp=a.static_mesh_component;role=ROLES[name];comp.set_material(0,materials[role])
            mapping.append(dict(label=name,actor=a.get_path_name(),component=comp.get_path_name(),role=role,slot=0,mesh=comp.static_mesh.get_path_name(),original=ORIGINAL,assigned=materials[role].get_path_name()))
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
        return write('variant-'+v,dict(recipe=VARIANTS[v],mapping=mapping,renderer=settings(),state=guard(True,True)))
    if command.startswith('capture:'):
        _,folder,op,view=command.split(':')
        assert folder in ['A','B','Final'] and op in ['prepare','camera','shoot','restore']
        guard(True,pie=op in ['camera','shoot'])
        if op=='prepare':write(folder+'/settings-before',settings_read())
        if op=='shoot':assert not (OUT/folder/(view+'.png')).exists()
        with config(OUT/folder):result=getattr(c,op)(view)
        if op=='shoot':
            p=OUT/folder/(view+'-camera.json');record=json.loads(p.read_text())
            record.update(renderer=settings(),optical_variant='B' if folder=='Final' else folder);p.write_text(json.dumps(record,indent=2))
        if op=='restore':
            after=settings_read();before=json.loads((OUT/folder/'settings-before.json').read_text())
            assert before==after;write(folder+'/settings-restored',dict(before=before,after=after,passed=True))
        return result
    if command=='reopen':
        guard(True,True);assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
        return write('reopened',snapshot('Reopened'))
    if command=='shader_audit':
        guard(True,True);lib=u.MaterialEditingLibrary;rows={}
        def graph(m,n):
            if not n:return None
            row=dict(path=n.get_path_name(),class_path=n.get_class().get_path_name())
            if isinstance(n,(u.MaterialExpressionVectorParameter,u.MaterialExpressionScalarParameter)):
                row.update(parameter=str(n.get_editor_property('parameter_name')),value=str(n.get_editor_property('default_value')))
            names=list(lib.get_material_expression_input_names(n))
            sources=list(lib.get_inputs_for_material_expression(m,n))
            row['inputs']={name:graph(m,sources[i] if i<len(sources) else None) for i,name in enumerate(names)}
            if isinstance(n,u.MaterialExpressionSubstrateSlabBSDF):row['sub_surface_type']=str(n.get_editor_property('sub_surface_type'))
            return row
        for role in ['Fixed','Leaf']:
            m=u.load_asset(ASSETS+'/M_GR01_B_'+role);assert m
            slab=lib.get_material_property_input_node(m,u.MaterialProperty.MP_FRONT_MATERIAL)
            assert isinstance(slab,u.MaterialExpressionSubstrateSlabBSDF)
            assert slab.get_editor_property('sub_surface_type')==u.MaterialSubSurfaceType.MSS_SIMPLE_VOLUME
            tree=graph(m,slab)
            assert tree['inputs']['Emissive Color'] is None
            assert tree['inputs']['SSS MFP']['class_path']=='/Script/Engine.MaterialExpressionSubstrateTransmittanceToMFP'
            stats=lib.get_statistics(m)
            rows[role]=dict(path=m.get_path_name(),settings={k:str(m.get_editor_property(k)) for k in ['blend_mode','is_thin_surface','two_sided','translucency_lighting_mode','screen_space_reflections']},front_material=tree,pixel_instructions=stats.num_pixel_shader_instructions,vertex_instructions=stats.num_vertex_shader_instructions,opacity=graph(m,lib.get_material_property_input_node(m,u.MaterialProperty.MP_OPACITY)))
            assert stats.num_pixel_shader_instructions>0
        assigned={name:a.static_mesh_component.get_material(0).get_path_name() for name,a in targets().items()}
        expected={n:ASSETS+'/M_GR01_B_'+r+'.M_GR01_B_'+r for n,r in ROLES.items()}
        assert assigned==expected
        write('native-shader-audit',dict(materials=rows,assignments=assigned,passed=True))
        return dict(passed=True,materials=2,assignments=len(assigned),report='native-shader-audit.json')
    if command.startswith('transmission:'):
        guard(True,True,True);op=command.split(':')[1]
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        pawn=u.GameplayStatics.get_player_pawn(world,0);move=pawn.get_component_by_class(u.CharacterMovementComponent)
        folder=OUT/'Transmission';folder.mkdir(exist_ok=True)
        if op=='restore':
            before=json.loads((folder/'overrides-before.json').read_text())
            pawn.set_actor_location(u.Vector(*before['location']),False,True)
            pawn.set_actor_enable_collision(before['collision']);move.set_movement_mode(u.MovementMode.MOVE_WALKING)
            pc=u.GameplayStatics.get_player_controller(world,0);pc.set_control_rotation(u.Rotator(0,0,0))
            u.SystemLibrary.execute_console_command(world,'fov 90',pc)
            return write('Transmission/overrides-restored',dict(collision=pawn.get_actor_enable_collision(),movement_mode=str(move.movement_mode),location=str(pawn.get_actor_location()),gameplay_fov=90))
        if op=='camera':
            assert not (folder/'overrides-before.json').exists()
            loc=pawn.get_actor_location()
            write('Transmission/overrides-before',dict(collision=pawn.get_actor_enable_collision(),movement_mode=str(move.movement_mode),location=[loc.x,loc.y,loc.z]))
            assert move.movement_mode==u.MovementMode.MOVE_WALKING and pawn.get_actor_enable_collision()
            move.stop_movement_immediately();move.set_movement_mode(u.MovementMode.MOVE_FLYING);pawn.set_actor_enable_collision(False)
        assert op in ['camera','shoot']
        c.VIEWS['GlassTransmission-90']=(-3300,0,0,0)
        try:
            with config(folder):result=getattr(c,op)('GlassTransmission-90')
            if op=='camera':pawn.set_actor_location(u.Vector(-3300,0,90.1499996),False,True)
            if op=='shoot':
                p=folder/'GlassTransmission-90-camera.json';d=json.loads(p.read_text())
                d.update(camera_type='DIAGNOSTIC reverse-side assembly view; flying and actor collision disabled temporarily; not a playable route or approved exterior',renderer=settings(),optical_variant='B');p.write_text(json.dumps(d,indent=2))
            return result
        finally:del c.VIEWS['GlassTransmission-90']
    if command=='spawn_check':
        s=guard(True,True,True);world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        pawn=u.GameplayStatics.get_player_pawn(world,0);move=pawn.get_component_by_class(u.CharacterMovementComponent)
        capsule=pawn.get_component_by_class(u.CapsuleComponent);camera=pawn.get_component_by_class(u.CameraComponent)
        s.update(game_mode=u.GameplayStatics.get_game_mode(world).get_class().get_path_name(),movement_mode=str(move.movement_mode),speed=move.max_walk_speed,capsule_radius=capsule.get_unscaled_capsule_radius(),capsule_half_height=capsule.get_unscaled_capsule_half_height(),camera_fov=camera.field_of_view)
        assert s['possessed'] and s['game_mode']=='/Script/MeridianSquad.OpeningLobbyGameMode'
        assert move.movement_mode==u.MovementMode.MOVE_WALKING and s['speed']==360
        assert s['capsule_radius']==34 and s['capsule_half_height']==88 and s['camera_fov']==90
        return write('standing-spawn',s)
    if command=='final':
        guard(True,True);assert c._settings is None
        return write('final-state',dict(snapshot=snapshot('FinalState'),renderer=settings(),capture_settings=settings_read(),capture_restored=True))
    raise ValueError(command)

def run(command):
    try:return execute(command)
    except Exception:
        import traceback
        return write('error-'+command.replace(':','-'),dict(error=traceback.format_exc()))

def disk_before():
    import architecture01_inventory as inv
    OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'protected-inputs.json').exists()
    rows={}
    for base in ['Assets','Content','Config','Source','Docs','Scripts/OpeningLobby','Saved/OpeningLobby']:
        for p in inv.files(ROOT/base):
            if p.is_relative_to(OUT) or '__pycache__' in str(p):continue
            rows[p.relative_to(ROOT).as_posix()]=dict(bytes=p.stat().st_size,sha256=inv.digest(p))
    for p in [ROOT/'AGENTS.md',ROOT/'.codex/config.toml']:
        rows[p.relative_to(ROOT).as_posix()]=dict(bytes=p.stat().st_size,sha256=inv.digest(p))
    write('protected-inputs',rows);write('storage-before',inv.storage())
    print(json.dumps(dict(protected=len(rows))))

def disk_after():
    """Focused preservation/camera checks; reuse the existing inventory components."""
    import architecture01_inventory as inv
    import check_architecture01_evidence as evidence
    protected=json.loads((OUT/'protected-inputs.json').read_text())
    allowed=['Docs/OpeningLobbyArchitecture01.md','Scripts/OpeningLobby/architecture01_glassreview.py','Scripts/OpeningLobby/architecture01_unreal.py']
    changed=[n for n,v in protected.items() if not (ROOT/n).exists() or inv.digest(ROOT/n)!=v['sha256']]
    assert not set(changed)-set(allowed),changed
    write('preservation',dict(protected=len(protected),changed=changed,allowed_changes=allowed,passed=True,dispatch_branch_added_before_manifest=True))
    def read_snapshot(name):
        text=(OUT/name/'all-properties.json').read_text()
        return json.loads(text.replace(SOURCE.split('/')[-1],'MAP').replace(MAP.split('/')[-1],'MAP'))
    source=read_snapshot('Source');template=read_snapshot('Template');reopened=read_snapshot('Reopened');final=read_snapshot('FinalState')
    assert source==template
    assert reopened==final
    source_adjusted=json.loads(json.dumps(source))
    for n,r in ROLES.items():
        original=source_adjusted['actors'][n]['components']['StaticMeshComponent0']['properties']['overrideMaterials']
        assert original==[dict(refPath=ORIGINAL)]
        source_adjusted['actors'][n]['components']['StaticMeshComponent0']['properties']['overrideMaterials']=[dict(refPath=ASSETS+'/M_GR01_B_'+r+'.M_GR01_B_'+r)]
    assert source_adjusted==reopened,'Unexpected reflected actor/component/world/renderer difference'
    before=json.loads((OUT/'Source/construction.json').read_text().replace(SOURCE.split('/')[-1],'MAP'))
    after=json.loads((OUT/'FinalState/construction.json').read_text().replace(MAP.split('/')[-1],'MAP'))
    for n,r in ROLES.items():before['actor_bounds'][n]['materials']=[ASSETS+'/M_GR01_B_'+r+'.M_GR01_B_'+r]
    assert before==after
    write('property-preservation',dict(passed=True,actors=len(source['actors']),components=sum(len(a['components']) for a in source['actors'].values()),only_changed_fields=[n+'/StaticMeshComponent0/overrideMaterials/0' for n in ROLES],template_equal=True,reopened_equal_final=True,all_bounds_collision_gameplay_lights_world_and_renderer_equal=True,normalization='Copied map identifier only; exactly seven declared material overrides.'))
    cameras=[]
    for folder in ['A','B','Final']:
        for p in sorted((OUT/folder).glob('*-camera.json')):
            d=json.loads(p.read_text())
            # Explicitly label the selected recipe in Final metadata; no pixels change.
            if folder=='Final' and d['optical_variant']=='Final':
                d['optical_variant']='B';p.write_text(json.dumps(d,indent=2))
            old=json.loads((BASE/'LightStudy01/Final'/p.name).read_text())
            assert all(d[k]==old[k] for k in ['actual_xyz_cm','actual_rotation','actual_hfov','renderer','resolution'])
            assert d['map']==MAP
            cameras.append(p.relative_to(OUT).as_posix())
    evidence.OUT=OUT/'Final';evidence.captures()
    write('camera-renderer-preservation',dict(passed=True,matched=cameras,pose_fov_resolution_renderer_equal=True,optical_delta='A or B dedicated glass only; Final uses B',diagnostic_separate='Transmission/GlassTransmission-90-camera.json'))
    storage=inv.storage();storage['study_growth_bytes']=storage['bytes']-json.loads((OUT/'storage-before.json').read_text())['bytes']
    storage['stage2_growth_bytes']=storage['bytes']-json.loads((BASE/'storage-before.json').read_text())['bytes']
    assert storage['bytes']<250*10**9 and storage['stage2_growth_bytes']<2*10**9
    write('storage-after',storage)
    inventory={}
    paths=list(inv.files(OUT))+list(inv.files(ROOT/'Content/OpeningLobby/Architecture01/GlassReview01'))
    paths += [ROOT/'Content/Maps/L_OpeningLobby_Architecture01_GlassReview01.umap',ROOT/'Docs/OpeningLobbyArchitecture01.md',Path(__file__),ROOT/'Scripts/OpeningLobby/architecture01_unreal.py']
    for p in paths:
        if p.name in ['inventory.json','inventory-validation.json'] or '__pycache__' in str(p):continue
        inventory[p.relative_to(ROOT).as_posix()]=dict(bytes=p.stat().st_size,sha256=inv.digest(p))
    write('inventory',inventory)
    assert all((ROOT/n).stat().st_size==v['bytes'] and inv.digest(ROOT/n)==v['sha256'] for n,v in inventory.items())
    write('inventory-validation',dict(passed=True,files=len(inventory)))
    print(json.dumps(dict(protected=len(protected),allowed_changed=changed,inventory_files=len(inventory),project_bytes=storage['bytes'],stage2_growth_bytes=storage['stage2_growth_bytes'],study_growth_bytes=storage['study_growth_bytes'])))

if __name__=='__main__':
    import sys
    disk_after() if sys.argv[-1]=='after' else disk_before()
