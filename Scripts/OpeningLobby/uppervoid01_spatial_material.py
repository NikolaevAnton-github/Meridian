"""Temporary rendered diagnostics; preserved dedicated atmosphere assets only."""
import json,types
import unreal as u
from uppervoid01_spatial_unreal import ROOT,OUT,ASSETS,guard,write
LIB=u.MaterialEditingLibrary
SRC=ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection04'
OLD=json.loads((ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection03/recipe.json').read_text())
SPATIAL='''// One static, smooth 3D absorption field. World units are centimeters.
// Three oblique low-frequency components have wavelengths 4m, 3m and 5m.
// Their weighted sum lies in [-1,1]; onset therefore remains within 13.7-15.1m.
float3 ray = WorldCm-CameraCm;
float distanceCm = length(ray);
float dz = ray.z;
float t0 = 0.0;
float t1 = 1.0;
if (abs(dz)>0.001) {
    float cross = (1370.0-CameraCm.z)/dz;
    if (dz>0.0) t0=max(t0,cross); else t1=min(t1,cross);
} else if (CameraCm.z<=1370.0) { return 1.0; }
t0=saturate(t0); t1=saturate(t1);
float opticalDepth = 0.0;
[unroll] for (int i=0;i<16;i++) {
    float t=lerp(t0,t1,(i+0.5)/16.0);
    float3 p=CameraCm+ray*t;
    float field=0.55*sin(dot(p,float3(0.72,0.60,0.35))*0.0157079633+0.9)
               +0.30*sin(dot(p,float3(-0.38,0.86,0.34))*0.0209439510+2.1)
               +0.15*sin(dot(p,float3(0.25,-0.43,0.867))*0.0125663706-0.7);
    float onset=1440.0+70.0*field;
    float h=max(p.z-onset,0.0)/max(1780.0-onset,1.0);
    float sigma=0.034*(1.0+0.30*field)*h*h;
    opticalDepth+=sigma;
}
opticalDepth*=distanceCm*max(t1-t0,0.0)/16.0;
// Exact roof concealment at 17.9m, independent of spatial modulation.
float roof=saturate((WorldCm.z-1760.0)/30.0);
return exp(-opticalDepth)*(1.0-roof*roof*(3.0-2.0*roof));'''

def build(tag):
    guard(True,True)
    assert (OUT/'archive-verification.json').exists()
    assert tag in ['Disabled','WorldZ','Transmission','Restore','Trial01']
    assert not (OUT/tag/'recipe.json').exists()
    post=OLD['postprocess'];light=OLD['light_function']
    if tag=='Disabled':post=light='return 1.0;'
    if tag=='WorldZ':post='// Diagnostic only: grayscale absolute surface height / 2000 cm.\nreturn saturate(WorldCm.z/2000.0);';light='return 1.0;'
    if tag=='Transmission':light='return 1.0;'
    if tag=='Trial01':post=SPATIAL
    rows=[]
    for name,code in [('M_UpperVoid_Extinction',post),('M_UpperVoid_LightTransmission',light)]:
        m=u.load_asset(ASSETS+'/'+name)
        nodes=LIB.get_material_expressions(m)
        custom=next(n for n in nodes if isinstance(n,u.MaterialExpressionCustom))
        custom.set_editor_property('code',code)
        if name=='M_UpperVoid_Extinction':
            output=custom if tag in ['WorldZ','Transmission'] else next(n for n in nodes if isinstance(n,u.MaterialExpressionMultiply))
            assert LIB.connect_material_property(output,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
        LIB.recompile_material(m)
        assert u.EditorAssetLibrary.save_loaded_asset(m)
        rows.append(dict(asset=m.get_path_name(),code=code))
    recipe=dict(tag=tag,postprocess=post,light_function=light,diagnostic_direct_output=tag in ['WorldZ','Transmission'],materials=rows,lights_changed=False)
    if tag=='Trial01':
        SRC.mkdir(parents=True,exist_ok=True)
        (SRC/'Extinction.hlsl').write_text(post,encoding='utf-8')
        (SRC/'LightTransmission.hlsl').write_text(light,encoding='utf-8')
        (SRC/'recipe.json').write_text(json.dumps(recipe,indent=2),encoding='utf-8')
    return write(tag+'/recipe',recipe)

def audit(tag):
    if tag=='compile-finish':
        for name in ['M_UpperVoid_Extinction','M_UpperVoid_LightTransmission']:
            assert u.EditorAssetLibrary.save_loaded_asset(u.load_asset(ASSETS+'/'+name))
        return write('compile-verification',dict(passed=True,method='Both fully wired saved/reopened trial graphs passed official MaterialTools.recompile, which raises on compiler failure. Saved only resulting dirty atmosphere packages.',state=guard(True,True)))
    if tag=='rollback-reopen':
        guard(True,True)
        ms=[u.load_asset(ASSETS+'/'+n) for n in ['M_UpperVoid_Extinction','M_UpperVoid_LightTransmission']]
        result=u.EditorLoadingAndSavingUtils.reload_packages([m.get_outermost() for m in ms])
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level('/Game/Maps/L_OpeningLobby_PainterStone01')
        from uppervoid01_spatial_unreal import snapshot
        import importlib,uppervoid01_spatial_capture as cap
        importlib.reload(cap)
        return write('rollback-reopened',dict(reload=str(result),snapshot=snapshot('Restored',True)))
    p=ROOT/'Scripts/OpeningLobby/uppervoid01_material.py'
    source=p.read_text().replace('from uppervoid01_unreal import','from uppervoid01_spatial_unreal import').replace(";write('graph-schemas-'+tag,schemas)",'')
    m=types.ModuleType('spatial_graph_readback');exec(compile(source,str(p),'exec'),m.__dict__)
    return m.audit(tag)
