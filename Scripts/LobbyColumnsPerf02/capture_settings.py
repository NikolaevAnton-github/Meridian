"""Record the hidden editor FPS clamp and lift it transiently for matched captures."""
import json
from pathlib import Path
import unreal as u
OUT=Path('D:/devgames/MeridianSquad/Saved/LobbyColumnsPerf02')
def prepare(name):
    es=u.get_editor_subsystem(u.UnrealEditorSubsystem); engine=es.get_outer()
    bounds=engine.get_editor_property('SmoothedFrameRateRange')
    prior=dict(smooth=engine.get_editor_property('bSmoothFrameRate'),
        fixed=engine.get_editor_property('bUseFixedFrameRate'),fixed_rate=engine.get_editor_property('FixedFrameRate'),
        lower=bounds.lower_bound.value,upper=bounds.upper_bound.value)
    original=OUT/'editor-cap-original.json'
    if not original.exists():original.write_text(json.dumps(prior,indent=2))
    bounds.upper_bound.value=1000.
    engine.set_editor_property('SmoothedFrameRateRange',bounds)
    assert engine.get_editor_property('SmoothedFrameRateRange').upper_bound.value==1000.
    w=es.get_game_world()
    assert w
    pc=u.GameplayStatics.get_player_controller(w,0)
    report=dict(original=prior,profile_upper_bound=1000.,viewport=list(pc.get_viewport_size()),
        cvars={k:u.SystemLibrary.get_console_variable_float_value(k) for k in [
            't.MaxFPS','t.OverrideFPS','r.VSync','r.VSyncEditor','r.ScreenPercentage','sg.ResolutionQuality',
            'sg.ViewDistanceQuality','sg.AntiAliasingQuality','sg.ShadowQuality','sg.GlobalIlluminationQuality',
            'sg.ReflectionQuality','sg.PostProcessQuality','sg.TextureQuality','sg.EffectsQuality','sg.FoliageQuality','sg.ShadingQuality']})
    (OUT/(name+'-settings.json')).write_text(json.dumps(report,indent=2))
    print(json.dumps(report))
def restore():
    engine=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_outer()
    prior=json.loads((OUT/'editor-cap-original.json').read_text())
    bounds=engine.get_editor_property('SmoothedFrameRateRange');bounds.upper_bound.value=prior['upper']
    engine.set_editor_property('SmoothedFrameRateRange',bounds)
