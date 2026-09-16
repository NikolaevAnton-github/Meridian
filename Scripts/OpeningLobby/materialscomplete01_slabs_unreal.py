"""44 new stone overrides; original materials, geometry and scene remain protected."""
import json,types,hashlib,importlib
from pathlib import Path
import unreal as u
from stage1_tools import state
from architecture01_lightstudy import props
ROOT=Path('D:/devgames/MeridianSquad')
OUT=ROOT/'Saved/OpeningLobby/MaterialsComplete01/Worker/SlabLayout01'
ASSETS='/Game/OpeningLobby/MaterialsComplete01/SlabLayout01'
MAP=SOURCE='/Game/Maps/L_OpeningLobby_PainterStone01'
p=ROOT/'Scripts/OpeningLobby/materialintegration01_unreal.py'
legacy=types.ModuleType('slabs_properties');legacy.__file__=str(p)
exec(compile(p.read_text(),str(p),'exec'),legacy.__dict__)
legacy.OUT=OUT;legacy.MAP=MAP;legacy.SOURCE=MAP;legacy.ASSETS=ASSETS
guard=legacy.guard;write=legacy.write;snapshot=legacy.snapshot;actors=legacy.actors;settings=legacy.settings
LIB=u.MaterialEditingLibrary
STONE='/Game/OpeningLobby/PainterStone01/Materials/M_PainterStone01'
ROLES={'Column':[6,7,8,9,10,17,18,19,20,21,35,36,37,38,71,74,82,85],
 'Wall':[1,2,5,12,15,25,26,27,30,32,42,70,73,79,81,84,90],
 'Jamb':[69,80],'Band':[31,33],'Beam':[72,83],'Trim':[91,92,40]}
def check_bytes():
    p=ROOT/'Content/Maps/L_OpeningLobby_PainterStone01.umap';r=OUT/'current-map.json'
    expected=json.loads(r.read_text())['sha256'] if r.exists() else 'b4cc37e0dd8281fddd250183c5e878f20fec35babcdefc520d3b09929857cb73'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==expected
def save():
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    return write('current-map',dict(sha256=hashlib.sha256((ROOT/'Content/Maps/L_OpeningLobby_PainterStone01.umap').read_bytes()).hexdigest()))
def preflight():
    guard(True,True);check_bytes();assert not (OUT/'plan.json').exists()
    snapshot('Before',True);rows=[]
    inv=json.loads((OUT/'Before/inventory.json').read_text());assert len(inv)==108
    lookup={a.get_name():a for a in actors()}
    for role,ids in ROLES.items():
        for i in ids:
            a=lookup['StaticMeshActor_'+str(i)];c=a.static_mesh_component
            assert c.get_num_materials()==1
            old=c.get_material(0).get_path_name();assert old in [STONE+'.M_PainterStone01','/Game/OpeningLobby/MaterialsComplete01/Correction01/M_C01_BroadStone.M_C01_BroadStone']
            center,extent=a.get_actor_bounds(False)
            minimum=[round(getattr(center,k)-getattr(extent,k),2) for k in ['x','y','z']]
            maximum=[round(getattr(center,k)+getattr(extent,k),2) for k in ['x','y','z']]
            # Building axes, independent of mesh import rotation/nonuniform actor scale.
            origin=[minimum[0],minimum[1],0]
            mode=1 if role=='Beam' else 2 if i in [91,92] else 3 if i==40 else 0
            name='MI_Slabs_'+str(i).zfill(3)
            rows.append(dict(actor=a.get_name(),label=a.get_actor_label(),component=c.get_name(),slot=0,old=old,new=ASSETS+'/'+name+'.'+name,
                role=role,source_overrides=[m.get_path_name() for m in c.get_editor_property('override_materials')],
                origin_cm=origin,bounds_min_cm=minimum,bounds_max_cm=maximum,axes=[[1,0,0],[0,1,0],[0,0,1]],
                module_cm=[120,240],joint_width_cm=.5,joint_depth_cm=.075,mode=mode,course_datum_world_z=0,
                exception='Long-axis 240 cm cut pieces; no transverse grid' if mode in [1,2] else '240 cm jamb courses below 420 cm; head length cuts above 420 cm' if mode==3 else 'Vertical courses; horizontal faces use long-axis cut pieces'))
    assert len(rows)==44 and sum('PainterStone01/' in r['old'] for r in rows)==25
    return write('plan',dict(rows=rows,regular=39,trim_aware=5,module_authority='Controller working default; owner authorized large slabs, not these exact dimensions',representative_ids=[17,12,80],glazing='DEFERRED_BY_OWNER'))
def build():
    guard(True,True);check_bytes();assert (OUT/'protected-before.json').exists()
    import materialscomplete01_slabs_material as m
    return importlib.reload(m).build()
def bind(which):
    guard(True,True);check_bytes();rows=json.loads((OUT/'plan.json').read_text())['rows']
    selected=[r for r in rows if which=='all' or r['actor'] in ['StaticMeshActor_17','StaticMeshActor_12','StaticMeshActor_80']]
    assert which in ['representative','all']
    lookup={(a.get_name(),c.get_name()):c for a in actors() for c in a.get_components_by_class(u.MeshComponent)}
    changes=[]
    for r in selected:
        c=lookup[(r['actor'],r['component'])];assert c.get_material(0).get_path_name() in [r['old'],r['new']]
        assert u.load_asset(r['new'])
    for r in selected:
        c=lookup[(r['actor'],r['component'])]
        if c.get_material(0).get_path_name()!=r['new']:c.set_material(0,u.load_asset(r['new']));changes.append(r)
    save();return write('bindings-'+which,dict(changed=len(changes),rows=changes))
def audit(tag):
    # Existing native traversal/compile/dependency checker, scoped to the new master.
    p=ROOT/'Scripts/OpeningLobby/materialscomplete01_correction_material.py'
    s=p.read_text().replace('from materialscomplete01_correction_unreal import','from materialscomplete01_slabs_unreal import')
    s=s.replace('for path in u.EditorAssetLibrary.list_assets(ASSETS,recursive=True,include_folder=False):',"for path in [ASSETS+'/M_Slabs01']:")
    m=types.ModuleType('slabs_graph_audit');exec(compile(s,str(p),'exec'),m.__dict__)
    result=m.audit(tag);schemas={};instances={}
    for r in json.loads((OUT/'plan.json').read_text())['rows']:
        a=u.load_asset(r['new']);assert a.get_editor_property('parent').get_path_name()==ASSETS+'/M_Slabs01.M_Slabs01'
        instances[r['actor']]=props(a,schemas)
    write('instances-'+tag,instances);write('instance-schemas-'+tag,schemas)
    return dict(**result,instances=len(instances))
def action(operation,argument=''):
    if operation=='state':return state()
    if operation=='resume_instances':
        guard(True,False);check_bytes();assert not (OUT/'authorship.json').exists()
        import materialscomplete01_slabs_material as m
        return importlib.reload(m).finish_instances(u.load_asset(ASSETS+'/M_Slabs01'))
    if operation=='instance_diagnostic':
        guard(True,False);schemas={};m=u.load_asset(ASSETS+'/M_Slabs01');a=u.load_asset(ASSETS+'/MI_Slabs_006')
        return write('instance-diagnostic',dict(state=state(),instance=props(a,schemas),parent=props(m,schemas),vector_names=[str(n) for n in LIB.get_vector_parameter_names(m)],scalar_names=[str(n) for n in LIB.get_scalar_parameter_names(m)],api=LIB.set_material_instance_vector_parameter_value.__doc__))
    if operation=='preflight':return preflight()
    if operation=='build':return build()
    if operation=='bind':return bind(argument)
    if operation=='audit':return audit(argument)
    if operation=='snapshot':
        check_bytes();assert not (OUT/argument/'all-properties.json').exists();return snapshot(argument,True)
    if operation=='reopen':
        guard(True,True);check_bytes()
        ms=[u.load_asset(p) for p in u.EditorAssetLibrary.list_assets(ASSETS,recursive=True,include_folder=False)]
        res=u.EditorLoadingAndSavingUtils.reload_packages([m.get_outermost() for m in ms])
        write('graphs-reloaded',dict(paths=[m.get_path_name() for m in ms],result=str(res)))
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
        return snapshot('Final',True)
    if operation.startswith('capture_'):
        import materialscomplete01_slabs_capture as c
        if operation=='capture_prepare':c=importlib.reload(c)
        return c.run(operation[8:],argument)
    raise ValueError(operation)
