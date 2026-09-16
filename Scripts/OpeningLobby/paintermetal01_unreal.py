"""Only the Metal01 material family and ten component overrides may mutate."""
import json
import types
import unreal as u
from stage1_tools import state
from paintermetal01_evidence import ROOT,OUT,CURRENT,TARGETS,OLD,NEW,digest
MAP='/Game/Maps/'+CURRENT
SOURCE=MAP
ASSETS='/Game/OpeningLobby/PainterMetal01'
_legacy=types.ModuleType('metal_property_validator')
_legacy.__file__=str(ROOT/'Scripts/OpeningLobby/materialintegration01_unreal.py')
exec(compile((ROOT/'Scripts/OpeningLobby/materialintegration01_unreal.py').read_text(),_legacy.__file__,'exec'),_legacy.__dict__)
_legacy.OUT=OUT;_legacy.MAP=MAP;_legacy.SOURCE=MAP;_legacy.ASSETS=ASSETS
guard=_legacy.guard;write=_legacy.write;actors=_legacy.actors;snapshot=_legacy.snapshot;settings=_legacy.settings
def baseline():
    guard(True,True)
    protected=json.loads((OUT/'protected-before.json').read_text())['entries']
    for row in protected:
        if row['path'].endswith(('.painter_lock','.lock')):continue
        if row['path']=='Content/Maps/'+CURRENT+'.umap' and (OUT/'bindings.json').exists():continue
        assert digest(ROOT/row['path'])==row['sha256'],row['path']
    return dict(protected_verified=len(protected),state=state())
def bind():
    baseline()
    assert not (OUT/'bindings.json').exists()
    inv=json.loads((OUT/'Before/inventory.json').read_text())
    lookup={(a.get_name(),c.get_name()):(a,c) for a in actors() for c in a.get_components_by_class(u.MeshComponent)}
    planned=[]
    for row in inv:
        if row['actor'] not in TARGETS:continue
        assert row['label']==TARGETS[row['actor']] and row['component']=='StaticMeshComponent0'
        assert row['materials']==[OLD] and row['overrides']==[]
        a,c=lookup[(row['actor'],row['component'])]
        assert a.get_actor_label()==row['label'] and c.get_material(0).get_path_name()==OLD
        assert list(c.get_editor_property('override_materials'))==[]
        planned.append((c,dict(actor=row['actor'],label=row['label'],component=row['component'],slot=0,old=OLD,new=NEW,source_overrides=row['overrides'])))
    assert len(planned)==10
    mat=u.load_asset(NEW);assert mat
    for c,row in planned:c.set_material(0,mat)
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    return write('bindings',dict(rows=[row for c,row in planned],changed=10,state=guard(True,True)))
def action(operation,argument=''):
    if operation=='state':return state()
    if operation=='tick_unthrottle':
        guard(True,True,pie=True)
        v=u.SystemLibrary.get_console_variable_int_value('Slate.bAllowThrottling');assert v==1
        write('tick-before',dict(value=v,reason='Final capture attempt stalled at world_seconds=0 and origin camera after level reopen. No PNG saved; explicit readiness rejected the frame.'))
        u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world(),'Slate.bAllowThrottling 0')
        return write('tick-unthrottled',dict(before=v,after=u.SystemLibrary.get_console_variable_int_value('Slate.bAllowThrottling')))
    if operation=='tick_restore':
        guard(True,True)
        v=json.loads((OUT/'tick-before.json').read_text())['value']
        u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),'Slate.bAllowThrottling '+str(v))
        return write('tick-restored',dict(value=u.SystemLibrary.get_console_variable_int_value('Slate.bAllowThrottling'),expected=v))
    if operation=='baseline':return baseline()
    if operation=='snapshot':
        assert argument in ['Before','Final','Restored','RestoredFinal']
        assert not (OUT/argument/'all-properties.json').exists()
        return snapshot(argument,True)
    if operation=='reopen':
        baseline()
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
        return write('unreal-reopened',snapshot('Final',True))
    if operation=='bind':return bind()
    if operation in ['material','audit']:
        baseline()
        import importlib,paintermetal01_material as material
        return getattr(importlib.reload(material).adapter(),operation)()
    if operation.startswith('capture_'):
        import paintermetal01_capture as cap
        return cap.run(operation[8:],argument)
    raise ValueError(operation)
