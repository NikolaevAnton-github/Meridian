"""Guarded candidate-only B3 reflection diagnostics through official Epic MCP."""
import json,re
from pathlib import Path
import unreal as u
import architecture01_unreal as work
COR=work.OUT/'Correction02'
CVARS=['r.Lumen.TranslucencyReflections.FrontLayer.Enable','r.Lumen.TranslucencyReflections.FrontLayer.Allow','r.Lumen.TranslucencyReflections.FrontLayer.EnableForProject','r.Lumen.Reflections.Allow','r.ReflectionMethod','r.DynamicGlobalIlluminationMethod','r.ForwardShading','r.Substrate','r.RayTracing','r.Lumen.HardwareRayTracing','sg.ReflectionQuality','sg.GlobalIlluminationQuality','r.ScreenPercentage','r.ReflectionCaptureResolution','r.ReflectionCapture.Runtime']
LABEL='A01_B3_FrontLayerReflectionSupport'

def write(name,data):
    (COR/(name+'.json')).write_text(json.dumps(data,indent=2));return data

def settings():
    return {n:u.SystemLibrary.get_console_variable_int_value(n) for n in CVARS}

def snapshot(name):
    work.guard(True)
    import architecture01_correction as correction
    original=correction.COR;correction.COR=COR
    # The established audit checks every geometry/material/collision record and anchors.
    try:
        if name=='before':correction.snapshot('before')
        else:
            # New nonvisual support actor is handled separately from the original actor set.
            original_out=work.OUT;work.OUT=COR
            try:work.audit()
            finally:work.OUT=original_out
    finally:correction.COR=original
    actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
    rows={}
    for a in actors:
        row=dict(class_path=a.get_class().get_path_name(),transform=re.sub(r'0x[0-9A-Fa-f]+','POINTER',str(a.get_actor_transform())),hidden=a.is_temporarily_hidden_in_editor())
        if isinstance(a,u.PostProcessVolume):row['postprocess']=a.get_editor_property('settings').export_text()
        rows[a.get_actor_label()]=row
    data=dict(state=work.guard(True),cvars=settings(),actors=rows)
    write(name+'-reflection-state',data)
    return dict(report=name+'-reflection-state.json',actors=len(rows),state=data['state'],cvars=data['cvars'])

def run(command):
    if command=='verify_restored':
        work.guard(True,True)
        before=json.loads((COR/'before-reflection-state.json').read_text())
        restored=json.loads((COR/'restored-reflection-state.json').read_text())
        assert before==restored,'Original actor transforms, postprocess or renderer state changed'
        import architecture01_correction as correction
        original=correction.COR;correction.COR=COR
        try:result=correction.snapshot('after')
        finally:correction.COR=original
        old=json.loads((COR/'console-before.json').read_text())
        assert all(u.SystemLibrary.get_console_variable_int_value(n)==v for n,v in old.items())
        return write('restoration-verification',dict(original_actor_records_identical=True,original_actor_count=len(before['actors']),anchors_unchanged=result['unchanged'],console_overrides_restored=True,map_saved=False,prior_route_seconds=112.297))
    if command=='discard_diagnostics':
        work.guard(True)
        before=json.loads((COR/'before-reflection-state.json').read_text())
        sub=u.get_editor_subsystem(u.EditorActorSubsystem)
        actors=sub.get_all_level_actors()
        added=[a for a in actors if a.get_actor_label() not in before['actors']]
        assert all(a.get_actor_label() in [LABEL,'A01_B3_HallReflectionCapture'] for a in added)
        for a in added:assert sub.destroy_actor(a)
        # Explicitly reload the unchanged disk map, discarding only this run's support actors.
        world=u.EditorLoadingAndSavingUtils.load_map(str(work.ROOT/'Content/Maps/L_OpeningLobby_Architecture01.umap'))
        assert world
        return snapshot('restored')
    if command=='probe_correct_extent':
        work.guard(True)
        a=next(a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='A01_B3_HallReflectionCapture')
        # Installed UBoxReflectionCaptureComponent uses scale directly as cm half-extents.
        a.set_actor_scale3d(u.Vector(3100,1200,900))
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
        u.SystemLibrary.execute_console_command(world,'r.ReflectionCapture.Runtime 1')
        c=a.get_component_by_class(u.BoxReflectionCaptureComponent);c.refresh_capture(True,False)
        return write('probe-corrected-extent',dict(half_extents_cm=[3100,1200,900],location_cm=[0,0,900],capture_offset_cm=[-2800,0,-725],runtime_capture=c.get_editor_property('runtime_capture'),actual_scale=str(c.get_world_scale()),source_evidence='ReflectionCaptureComponent.cpp: GetInfluenceBoundingRadius returns component scale vector length',supersedes='probe-delta.json box_scale; prior probe images did not cover entrance',saved=False))
    if command=='probe_runtime_diagnostic':
        work.guard(True)
        assert not (COR/'console-before.json').exists()
        names=['r.ReflectionCapture.Runtime','r.Lumen.TranslucencyVolume.RadianceCache']
        write('console-before',{n:u.SystemLibrary.get_console_variable_int_value(n) for n in names})
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
        u.SystemLibrary.execute_console_command(world,'r.ReflectionCapture.Runtime 1')
        a=next(a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='A01_B3_HallReflectionCapture')
        c=a.get_component_by_class(u.BoxReflectionCaptureComponent);c.set_editor_property('runtime_capture',True)
        c.refresh_capture(True,False)
        return write('probe-runtime-diagnostic',dict(runtime_capture=True,console={n:u.SystemLibrary.get_console_variable_int_value(n) for n in names},saved=False))
    if command in ['radiance_diagnostic_off','console_restore']:
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world() or u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
        original=json.loads((COR/'console-before.json').read_text())
        values={'r.Lumen.TranslucencyVolume.RadianceCache':0} if command=='radiance_diagnostic_off' else original
        for n,v in values.items():u.SystemLibrary.execute_console_command(world,n+' '+str(v))
        return write(command,{n:u.SystemLibrary.get_console_variable_int_value(n) for n in original})
    if command=='probe_schema':
        work.guard(True)
        return dict(level_methods=[n for n in dir(u.LevelEditorSubsystem) if 'build' in n or 'reflection' in n],capture_methods=[n for n in dir(u.ReflectionCaptureComponent) if 'capture' in n or 'reflection' in n],source_types=[n for n in dir(u.ReflectionSourceType) if n.isupper()])
    if command=='probe_add':
        work.guard(True)
        sub=u.get_editor_subsystem(u.EditorActorSubsystem)
        support=[a for a in sub.get_all_level_actors() if a.get_actor_label()==LABEL]
        assert len(support)==1
        assert sub.destroy_actor(support[0])
        a=sub.spawn_actor_from_class(u.BoxReflectionCapture,u.Vector(0,0,900));a.set_actor_label('A01_B3_HallReflectionCapture')
        a.set_folder_path('Architecture01/ReflectionSupport')
        a.set_actor_scale3d(u.Vector(3100,1200,900))
        c=a.get_component_by_class(u.BoxReflectionCaptureComponent)
        c.set_editor_property('box_transition_distance',10.0)
        c.set_editor_property('brightness',1.0)
        c.set_editor_property('capture_offset',u.Vector(-2800,0,-725))
        return write('probe-delta',dict(actor=a.get_path_name(),label=a.get_actor_label(),location_cm=[0,0,900],half_extents_cm=[3100,1200,900],capture_offset_cm=[-2800,0,-725],brightness=1,transition_cm=10,source=str(c.get_editor_property('reflection_source_type')),runtime=c.get_editor_property('runtime_capture'),cvars=settings(),saved=False))
    if command=='inspect':
        work.guard(True,True)
        actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
        pp={a.get_actor_label():str(a.get_editor_property('settings').get_editor_property('lumen_front_layer_translucency_reflections')) for a in actors if isinstance(a,u.PostProcessVolume)}
        m=u.load_asset(work.ASSETS+'/Materials/M_A01_Glass')
        result=dict(state=work.guard(True,True),cvars=settings(),postprocess=pp,glass={n:str(m.get_editor_property(n)) for n in ['blend_mode','translucency_lighting_mode','screen_space_reflections','is_thin_surface','two_sided']},reflection_actors=[a.get_actor_label() for a in actors if isinstance(a,u.ReflectionCapture)])
        return write('preflight',result)
    if command=='before':return snapshot('before')
    if command=='frontlayer_add':
        work.guard(True,True)
        assert settings()['r.Lumen.TranslucencyReflections.FrontLayer.Allow']==1
        sub=u.get_editor_subsystem(u.EditorActorSubsystem)
        assert not any(a.get_actor_label()==LABEL for a in sub.get_all_level_actors())
        a=sub.spawn_actor_from_class(u.PostProcessVolume,u.Vector(0,0,0));a.set_actor_label(LABEL)
        a.set_folder_path('Architecture01/ReflectionSupport')
        a.set_editor_property('unbound',True);a.set_editor_property('priority',10.0)
        pp=a.get_editor_property('settings')
        pp.set_editor_property('override_lumen_front_layer_translucency_reflections',True)
        pp.set_editor_property('lumen_front_layer_translucency_reflections',True)
        a.set_editor_property('settings',pp)
        return write('frontlayer-delta',dict(actor=a.get_path_name(),label=LABEL,unbound=True,priority=10,settings=pp.export_text(),cvars=settings(),saved=False))
    if command.startswith('capture:'):
        import architecture01_capture as capture
        _,folder,op,view=command.split(':')
        assert folder in ['LiveBefore','FrontLayer','Reopened','Probe','ProbeRuntime','GlobalDiagnostic','ProbeScoped','ProbeFallback','Final']
        assert op in ['camera','shoot'] and view in capture.VIEWS
        original=capture.OUT;capture.OUT=COR/folder;capture.OUT.mkdir(exist_ok=True)
        try:return getattr(capture,op)(view)
        finally:capture.OUT=original
    if command=='save_reopen':
        work.guard(True)
        assert not work.state()['dirty_content']
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(work.MAP)
        work.guard(True,True)
        return snapshot('reopened')
    if command=='after':return snapshot('after')
    if command=='final_state':
        import architecture01_capture as capture
        assert capture._settings is None
        return write('final-state',dict(state=work.guard(True,True),cvars=settings(),capture_restored=True))
    raise ValueError(command)
