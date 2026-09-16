"""Correction03: six optical bindings and two local front-layer flags only."""
import json,types,hashlib,importlib
from pathlib import Path
import unreal as u
from stage1_tools import state
from architecture01_lightstudy import props
ROOT=Path('D:/devgames/MeridianSquad')
OUT=ROOT/'Saved/OpeningLobby/MaterialsComplete01/Worker/Correction03'
ASSETS='/Game/OpeningLobby/MaterialsComplete01/Correction03'
MAP=SOURCE='/Game/Maps/L_OpeningLobby_PainterStone01'
p=ROOT/'Scripts/OpeningLobby/materialintegration01_unreal.py'
legacy=types.ModuleType('optics_properties');legacy.__file__=str(p)
exec(compile(p.read_text(),str(p),'exec'),legacy.__dict__)
legacy.OUT=OUT;legacy.MAP=MAP;legacy.SOURCE=MAP;legacy.ASSETS=ASSETS
guard=legacy.guard;write=legacy.write;snapshot=legacy.snapshot;actors=legacy.actors;settings=legacy.settings
LIB=u.MaterialEditingLibrary
FLAGS=['bOverride_LumenFrontLayerTranslucencyReflections','lumenFrontLayerTranslucencyReflections']
RECIPES={'Fixed':dict(albedo=.45,transmission=.90,roughness=.32,slope=.045),'Leaf':dict(albedo=.04,transmission=.94,roughness=.09,slope=.025)}

def check_bytes():
    p=ROOT/'Content/Maps/L_OpeningLobby_PainterStone01.umap'
    receipt=OUT/'current-map.json'
    expected=json.loads(receipt.read_text())['sha256'] if receipt.exists() else '27351b91d05441dbee4d75c4ef1ec3719a213ce541f60cb86a8c2566b73a4940'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==expected

def save():
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    return write('current-map',dict(sha256=hashlib.sha256((ROOT/'Content/Maps/L_OpeningLobby_PainterStone01.umap').read_bytes()).hexdigest()))

def volume():
    a=[a for a in actors() if a.get_actor_label()=='Layout03NeutralExposure']
    assert len(a)==1;return a[0]

def path_evidence(world=None):
    if world:
        a=[a for a in u.GameplayStatics.get_all_actors_of_class(world,u.PostProcessVolume) if a.get_actor_label()=='Layout03NeutralExposure'][0]
    else:a=volume()
    schemas={};p=props(a,schemas)['properties']['settings']
    names=['r.Lumen.TranslucencyReflections.FrontLayer.Enable','r.Lumen.TranslucencyReflections.FrontLayer.Allow','r.Lumen.TranslucencyReflections.FrontLayer.EnableForProject','r.Lumen.Reflections.MaxRoughnessToTrace','r.ReflectionCapture.Runtime']
    cvars={n:u.SystemLibrary.get_console_variable_float_value(n) for n in names}
    return dict(local_flags={n:p[n] for n in FLAGS},cvars=cvars,postprocess=props(a,schemas)['properties'],interpretation='Readback of inputs, not proof of rendered reflection. Compare actual frames.')

def preflight():
    guard(True,True);check_bytes();schemas={}
    pp=props(volume(),schemas);assert all(not pp['properties']['settings'][n] for n in FLAGS)
    rows=[]
    for a in actors():
        for c in a.get_components_by_class(u.MeshComponent):
            if c.get_num_materials()==1 and '/Correction01/M_C01_Glass' in c.get_material(0).get_path_name():
                old=c.get_material(0).get_path_name();role='Fixed' if old.endswith('Fixed') else 'Leaf'
                rows.append(dict(actor=a.get_name(),component=c.get_name(),old=old,new=ASSETS+'/M_C03_Glass'+role+'.M_C03_Glass'+role,source_overrides=[m.get_path_name() for m in c.get_editor_property('override_materials')]))
    assert len(rows)==6
    write('plan',dict(rows=rows,postprocess_actor=volume().get_name(),flags=FLAGS,recipes=RECIPES,allowed='Only six overrides and two local flags; no actor, light, cvar, config or existing asset changes.'))
    write('frontlayer-schema',schemas)
    return write('preflight',dict(state=state(),path=path_evidence(),map_verified=True))

def local_flag(value,tag):
    guard(True,True);check_bytes()
    assert (OUT/'plan.json').exists()
    a=volume();s=a.get_editor_property('settings')
    s.set_editor_property('override_lumen_front_layer_translucency_reflections',value)
    s.set_editor_property('lumen_front_layer_translucency_reflections',value)
    a.set_editor_property('settings',s);save()
    r=path_evidence();assert all(v==value for v in r['local_flags'].values())
    return write(tag+'/path',r)

def build():
    guard(True,True);check_bytes();assert (OUT/'plan.json').exists()
    result={}
    for role,r in RECIPES.items():
        path=ASSETS+'/M_C03_Glass'+role
        assert not u.EditorAssetLibrary.does_asset_exist(path)
        m=u.EditorAssetLibrary.duplicate_asset('/Game/OpeningLobby/MaterialsComplete01/Correction01/M_C01_Glass'+role,path);assert m
        values={}
        for n in LIB.get_material_expressions(m):
            if isinstance(n,(u.MaterialExpressionVectorParameter,u.MaterialExpressionScalarParameter)):
                key=str(n.get_editor_property('parameter_name'))
                if key in ['ScatteringAlbedo','Transmission']:
                    v=r['albedo' if key=='ScatteringAlbedo' else 'transmission'];n.set_editor_property('default_value',u.LinearColor(v,v,v,1));values[key]=v
                if key in ['SurfaceRoughness','EtchSlope']:
                    v=r['roughness' if key=='SurfaceRoughness' else 'slope'];n.set_editor_property('default_value',v);values[key]=v
        assert len(values)==4
        LIB.recompile_material(m);assert u.EditorAssetLibrary.save_loaded_asset(m)
        result[role]=dict(path=m.get_path_name(),constants=values,F0=.04,source='Duplicate native Correction01 graph; new constants, original filtered micro-slope code retained.',emission=False)
    source=ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/Correction03';source.mkdir(parents=True,exist_ok=True)
    (source/'recipe.json').write_text(json.dumps(result,indent=2))
    return write('authorship',result)

def bind():
    guard(True,True);check_bytes();rows=json.loads((OUT/'plan.json').read_text())['rows']
    lookup={(a.get_name(),c.get_name()):c for a in actors() for c in a.get_components_by_class(u.MeshComponent)}
    for r in rows:
        c=lookup[(r['actor'],r['component'])];assert c.get_material(0).get_path_name()==r['old']
        assert [m.get_path_name() for m in c.get_editor_property('override_materials')]==r['source_overrides']
        assert u.load_asset(r['new'])
    for r in rows:lookup[(r['actor'],r['component'])].set_material(0,u.load_asset(r['new']))
    save();return write('bindings',dict(changed=6,rows=rows))

def audit(tag):
    # Reuse the complete native connectivity/property/compile/dependency validator read-only.
    p=ROOT/'Scripts/OpeningLobby/materialscomplete01_correction_material.py'
    s=p.read_text().replace('from materialscomplete01_correction_unreal import','from materialscomplete01_optics_unreal import')
    m=types.ModuleType('optics_graph_audit');exec(compile(s,str(p),'exec'),m.__dict__)
    return m.audit(tag)

def action(operation,argument=''):
    if operation=='fine':
        guard(True,True);check_bytes()
        assert not (OUT/'fine-adjustment.json').exists()
        assert (OUT/'ComparisonArchive/archive.json').exists()
        result={}
        for role in RECIPES:
            m=u.load_asset(ASSETS+'/M_C03_Glass'+role)
            node=[n for n in LIB.get_material_expressions(m) if isinstance(n,u.MaterialExpressionScalarParameter) and str(n.get_editor_property('parameter_name'))=='EtchSlope'][0]
            before=node.get_editor_property('default_value');after=.0045 if role=='Fixed' else .0025
            node.set_editor_property('default_value',after);LIB.recompile_material(m)
            assert u.EditorAssetLibrary.save_loaded_asset(m)
            result[role]=dict(before=before,after=after)
        return write('fine-adjustment',dict(reason='Both NewOff and NewOn near-oblique images show coarse-looking 2 cm etch highlights. Reduce slope amplitude tenfold while retaining neutral optical preset and the filtered native field. No claim this supplies missing reflected scene structure.',changes=result))
    if operation=='state':return state()
    if operation=='preflight':return preflight()
    if operation=='flag':
        tag,value=argument.split(':');return local_flag(value=='on',tag)
    if operation=='build':return build()
    if operation=='bind':return bind()
    if operation=='audit':return audit(argument)
    if operation=='snapshot':
        check_bytes();assert not (OUT/argument/'all-properties.json').exists();return snapshot(argument,True)
    if operation=='reopen':
        guard(True,True);check_bytes()
        ms=[u.load_asset(ASSETS+'/M_C03_Glass'+r) for r in RECIPES]
        res=u.EditorLoadingAndSavingUtils.reload_packages([m.get_outermost() for m in ms])
        write('graphs-reloaded',dict(paths=[m.get_path_name() for m in ms],result=str(res)))
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
        return snapshot('Final',True)
    if operation.startswith('capture_'):
        import materialscomplete01_optics_capture as c
        if operation=='capture_prepare':c=importlib.reload(c)
        return c.run(operation[8:],argument)
    raise ValueError(operation)
