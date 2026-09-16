"""Dedicated atmosphere response correction; no surface material edits."""
import json,types
import unreal as u
from uppervoid01_soft_unreal import ROOT,OUT,ASSETS,guard,write,actors,props
LIB=u.MaterialEditingLibrary
SRC=ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection02'
POST='''float h = saturate((WorldCm.z - FadeStartCm) / max(FadeEndCm - FadeStartCm, 1.0));
// Early visible decay with a long dark tail, anchored exclusively to world height.
float tail = (1.0-h)*(1.0-h)*(1.0+2.0*h);
return exp(-8.0*h*h)*tail;'''
LIGHT='''float h = saturate((WorldCm.z - FadeStartCm) / max(FadeEndCm - FadeStartCm, 1.0));
// Broad cubic light transmission avoids duplicating the sharper extinction curve.
return (1.0-h)*(1.0-h)*(1.0+2.0*h);'''

def build(tag):
    guard(True,True)
    if tag=='Trial02':return revision()
    assert tag=='Trial01'
    assert (OUT/'archive-verification.json').exists() and not (OUT/tag/'recipe.json').exists()
    rows=[]
    for name,code in [('M_UpperVoid_Extinction',POST),('M_UpperVoid_LightTransmission',LIGHT)]:
        m=u.load_asset(ASSETS+'/'+name);changed=[]
        for n in LIB.get_material_expressions(m):
            if isinstance(n,u.MaterialExpressionScalarParameter):
                key=str(n.get_editor_property('parameter_name'))
                if key in ['FadeStartCm','FadeEndCm']:
                    v=1370. if key=='FadeStartCm' else 1780.
                    changed.append(dict(node=n.get_name(),property='defaultValue',before=n.get_editor_property('default_value'),after=v));n.set_editor_property('default_value',v)
            if isinstance(n,u.MaterialExpressionCustom):
                changed.append(dict(node=n.get_name(),property='code',before=n.get_editor_property('code'),after=code));n.set_editor_property('code',code)
        assert len(changed)==3
        LIB.recompile_material(m);assert u.EditorAssetLibrary.save_loaded_asset(m)
        rows.append(dict(asset=m.get_path_name(),changes=changed))
    lights=[]
    for a in actors():
        if isinstance(a,u.PointLight) and abs(a.get_actor_location().y)<1:
            c=a.get_component_by_class(u.PointLightComponent);old=c.get_editor_property('specular_scale')
            assert abs(old-.2)<1e-6;c.set_editor_property('specular_scale',.05)
            lights.append(dict(actor=a.get_name(),property='specularScale',before=old,after=c.get_editor_property('specular_scale')))
    assert len(lights)==6
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    recipe=dict(candidate='LobbyAtmosphere-UpperVoid01/HeightCorrection02',trial=tag,fade_start_cm=1370,fade_end_cm=1780,postprocess=POST,light_function=LIGHT,materials=rows,lights=lights,rationale='Earlier visible decline within high zone with long dark tail; broad light transmission; suppress upper central specular pool without dimming diffuse fill or changing twelve aisle lights.',fixed_exposure='Manual bias -5 unchanged')
    SRC.mkdir(parents=True,exist_ok=True)
    for name,code in [('Extinction.hlsl',POST),('LightTransmission.hlsl',LIGHT)]: (SRC/name).write_text(code)
    (SRC/'recipe.json').write_text(json.dumps(recipe,indent=2));write(tag+'/recipe',recipe)
    return dict(saved=True,fade_cm=[1370,1780],central_specular=.05)

def revision():
    assert (OUT/'Trial01/recipe.json').exists() and not (OUT/'Trial02/recipe.json').exists()
    rows=[]
    for a in actors():
        if isinstance(a,u.PointLight) and abs(a.get_actor_location().y)<1:
            c=a.get_component_by_class(u.PointLightComponent);old=c.get_editor_property('intensity')
            assert old==100000.;c.set_editor_property('intensity',20000.)
            rows.append(dict(actor=a.get_name(),property='intensity',before=old,after=c.get_editor_property('intensity')))
    assert len(rows)==6
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    recipe=json.loads((SRC/'recipe.json').read_text());recipe.update(trial='Trial02',revision_deltas=rows,revision_reason='Trial01 still showed a bright terminal pool in the exact close pose. Reduce six central diffuse fills to 20 percent, preserving their positions/radii and all twelve aisle fills.')
    (SRC/'recipe.json').write_text(json.dumps(recipe,indent=2));write('Trial02/recipe',recipe)
    return dict(saved=True,central_intensity=20000,lights=6)

def audit(tag):
    p=ROOT/'Scripts/OpeningLobby/uppervoid01_material.py'
    s=p.read_text().replace('from uppervoid01_unreal import','from uppervoid01_soft_unreal import').replace(";write('graph-schemas-'+tag,schemas)",'')
    m=types.ModuleType('soft_graph_readback');exec(compile(s,str(p),'exec'),m.__dict__)
    return m.audit(tag)
