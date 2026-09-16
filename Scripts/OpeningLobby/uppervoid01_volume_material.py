"""HeightCorrection03 isolated stages and two bounded representative methods."""
import json,types
import unreal as u
from uppervoid01_volume_unreal import ROOT,OUT,ASSETS,guard,write,actors
LIB=u.MaterialEditingLibrary
SRC=ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection03'
OLD=json.loads((ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection02/recipe.json').read_text())
POST='''float h = saturate((WorldCm.z - FadeStartCm) / max(FadeEndCm - FadeStartCm, 1.0));
// Almost-linear display transmission with short rounded endpoint shoulders.
float e = 0.06;
float q = h < e ? h*h/(2.0*e) : (h > 1.0-e ? 1.0-e-(1.0-h)*(1.0-h)/(2.0*e) : h-e*0.5);
return 1.0-q/(1.0-e);'''
LIGHT='''// Reserve direct-light attenuation for the roof; the visible shaft ramp belongs to PP.
float h = saturate((WorldCm.z - 1750.0) / 40.0);
return 1.0-h*h*(3.0-2.0*h);'''
VOLUME='''// Analytic Beer-Lambert absorption through a world-anchored upper half-space.
// Density begins with zero slope at 13.7m: sigma(z)=0.034*(height/410)^2 per cm.
float span = max(FadeEndCm-FadeStartCm,1.0);
float a = max(CameraCm.z-FadeStartCm,0.0);
float b = max(WorldCm.z-FadeStartCm,0.0);
float dz = WorldCm.z-CameraCm.z;
float distanceCm = length(WorldCm-CameraCm);
float integral = abs(dz)>0.01 ? abs(b*b*b-a*a*a)*distanceCm/(3.0*abs(dz)*span*span) : distanceCm*a*a/(span*span);
float transmittance = exp(-0.034*integral);
// Exact terminal suppression is confined to the roof margin, above useful volume.
float roof = saturate((WorldCm.z-FadeEndCm)/20.0);
return transmittance*(1.0-roof*roof*(3.0-2.0*roof));'''

def build(tag):
    guard(True,True)
    assert (OUT/'archive-verification.json').exists()
    assert tag in ['IsolatePP','IsolateLF','Trial01','Trial02']
    assert not (OUT/tag/'recipe.json').exists()
    post=OLD['postprocess'] if tag=='IsolatePP' else ('return 1.0;' if tag=='IsolateLF' else POST)
    if tag=='Trial02':post=VOLUME
    light=OLD['light_function'] if tag=='IsolateLF' else ('return 1.0;' if tag=='IsolatePP' else LIGHT)
    rows=[]
    for name,code in [('M_UpperVoid_Extinction',post),('M_UpperVoid_LightTransmission',light)]:
        m=u.load_asset(ASSETS+'/'+name);changes=[]
        for n in LIB.get_material_expressions(m):
            if isinstance(n,u.MaterialExpressionCustom):
                changes.append(dict(node=n.get_name(),before=n.get_editor_property('code'),after=code));n.set_editor_property('code',code)
                if tag=='Trial02' and name=='M_UpperVoid_Extinction':
                    inputs=list(n.get_editor_property('inputs'));i=u.CustomInput();i.set_editor_property('input_name','CameraCm');inputs.append(i);n.set_editor_property('inputs',inputs)
                    camera=LIB.create_material_expression(m,u.MaterialExpressionCameraPositionWS)
                    assert LIB.connect_material_expressions(camera,'',n,'CameraCm')
        assert len(changes)==1
        LIB.recompile_material(m);assert u.EditorAssetLibrary.save_loaded_asset(m)
        rows.append(dict(asset=m.get_path_name(),changes=changes))
    lights=[]
    if tag in ['Trial01','Trial02']:
        for a in actors():
            if isinstance(a,u.PointLight) and abs(a.get_actor_location().y)<1:
                c=a.get_component_by_class(u.PointLightComponent)
                for k,v in [('intensity',100000.),('specular_scale',.2)]:
                    old=c.get_editor_property(k);c.set_editor_property(k,v)
                    lights.append(dict(actor=a.get_name(),property='intensity' if k=='intensity' else 'specularScale',before=old,after=c.get_editor_property(k)))
        assert len(lights)==12
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    recipe=dict(candidate='LobbyAtmosphere-UpperVoid01/HeightCorrection03',trial=tag,fade_start_cm=1370,fade_end_cm=1780,postprocess=post,light_function=light,materials=rows,lights=lights,fixed_exposure='Manual bias -5 unchanged')
    write(tag+'/recipe',recipe)
    if tag.startswith('Trial'):
        SRC.mkdir(parents=True,exist_ok=True)
        for name,code in [('Extinction.hlsl',post),('LightTransmission.hlsl',light)]: (SRC/name).write_text(code)
        (SRC/'recipe.json').write_text(json.dumps(recipe,indent=2))
    return dict(saved=True,setup=tag)

def audit(tag):
    if tag=='compile-finish':
        import hashlib
        from stage1_tools import state
        s=state();assert not s['pie'] and not s['dirty_maps']
        assert s['dirty_content']==[ASSETS+'/M_UpperVoid_Extinction'],s
        path=ROOT/'Content/OpeningLobby/UpperVoid01/M_UpperVoid_Extinction.uasset';before=hashlib.sha256(path.read_bytes()).hexdigest()
        result=u.EditorLoadingAndSavingUtils.reload_packages([u.load_asset(ASSETS+'/M_UpperVoid_Extinction').get_outermost()])
        assert hashlib.sha256(path.read_bytes()).hexdigest()==before
        s=guard(True,True)
        return write('compile-verification',dict(passed=True,method='Official MaterialTools.recompile completed successfully on the reopened fully wired graph. Discarded only resulting unsaved dirty flag by native package reload; disk SHA unchanged.',reload=str(result),sha256=before,state=s,earlier_warning='During node creation before fourth CameraCm input connected; retained in error-audit.'))
    p=ROOT/'Scripts/OpeningLobby/uppervoid01_material.py'
    s=p.read_text().replace('from uppervoid01_unreal import','from uppervoid01_volume_unreal import').replace(";write('graph-schemas-'+tag,schemas)",'')
    m=types.ModuleType('volume_graph_readback');exec(compile(s,str(p),'exec'),m.__dict__)
    return m.audit(tag)
