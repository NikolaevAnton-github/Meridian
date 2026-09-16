"""Bounded height/light revision; native editable graphs retain original topology."""
import json,types
import unreal as u
from uppervoid01_height_unreal import ROOT,OUT,ASSETS,MAP,guard,write,actors,props
LIB=u.MaterialEditingLibrary
SRC=ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection01'
p=ROOT/'Scripts/OpeningLobby/uppervoid01_material.py'
base=types.ModuleType('height_existing_audit')
exec(compile(p.read_text().replace('uppervoid01_','uppervoid01_height_'),str(p),'exec'),base.__dict__)
audit=base.audit
def build(tag):
    guard(True,True);assert tag=='Trial01'
    assert (OUT/'archive-verification.json').exists() and not (OUT/'Trial01/recipe.json').exists()
    mats=[]
    for name in ['M_UpperVoid_Extinction','M_UpperVoid_LightTransmission']:
        m=u.load_asset(ASSETS+'/'+name);assert m
        parameters=[]
        for n in LIB.get_material_expressions(m):
            if isinstance(n,u.MaterialExpressionScalarParameter):
                key=str(n.get_editor_property('parameter_name'))
                if key in ['FadeStartCm','FadeEndCm']:
                    before=n.get_editor_property('default_value');assert before in [350.,850.]
                    value=1400. if key=='FadeStartCm' else 1750.
                    n.set_editor_property('default_value',value);parameters.append(dict(parameter=key,before=before,after=value))
        assert len(parameters)==2
        LIB.recompile_material(m);assert u.EditorAssetLibrary.save_loaded_asset(m)
        mats.append(dict(asset=m.get_path_name(),parameters=parameters))
    old=json.loads((ROOT/'Saved/OpeningLobby/UpperVoid01/Worker/Before/all-properties.json').read_text())['actors']
    rows=[]
    for a in actors():
        if not isinstance(a,u.PointLight):continue
        o=old[a.get_name()]['components']['LightComponent0']['properties'];c=a.get_component_by_class(u.PointLightComponent)
        central=abs(o['relativeLocation']['y'])<1
        changes=dict(intensity=o['intensity'],attenuation_radius=o['attenuationRadius'],indirect_lighting_intensity=.2 if central else 1.,specular_scale=.2)
        before=props(c,{})
        for k,v in changes.items():c.set_editor_property(k,v)
        loc=o['relativeLocation'];a.set_actor_location(u.Vector(loc['x'],loc['y'],loc['z']),False,True)
        rows.append(dict(actor=a.get_name(),label=a.get_actor_label(),before=before,after=props(c,{}),original=o))
    assert len(rows)==18
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    recipe=dict(candidate='LobbyAtmosphere-UpperVoid01/HeightCorrection01',trial=tag,fade_start_cm=1400,fade_end_cm=1750,formula=base.FADE,materials=mats,lights=rows,exposure='Existing manual bias -5 unchanged',rationale='Restore original 18 fill heights, intensity and radii. Side indirect returns to 1; central indirect stays 0.2 to limit upper reflected fill. Specular light scale remains 0.2. World-height extinction is neutral below 14m, total above 17.5m, leaving 9.2m side soffits visible.',preserved='Every surface source/material byte and all 107 bindings; dedicated atmosphere graph thresholds only.')
    SRC.mkdir(parents=True,exist_ok=True);(SRC/'HeightTransmission.hlsl').write_text(base.FADE);(SRC/'recipe.json').write_text(json.dumps(recipe,indent=2))
    write(tag+'/recipe',recipe)
    return dict(saved=True,lights=18,fade_cm=[1400,1750])
