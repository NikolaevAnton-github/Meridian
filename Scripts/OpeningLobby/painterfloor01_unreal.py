"""In-place floor scope; property snapshot implementation is reused unchanged."""
import hashlib
import json
import types
from pathlib import Path
import unreal as u
from stage1_tools import state
from painterfloor01_evidence import ROOT,OUT,CURRENT,RETIRED
MAP='/Game/Maps/'+CURRENT
SOURCE=MAP
ASSETS='/Game/OpeningLobby/PainterFloor01'
_legacy=types.ModuleType('floor_property_validator')
_legacy.__file__=str(ROOT/'Scripts/OpeningLobby/materialintegration01_unreal.py')
exec(compile(Path(_legacy.__file__).read_text(),_legacy.__file__,'exec'),_legacy.__dict__)
_legacy.OUT=OUT;_legacy.MAP=MAP;_legacy.SOURCE=MAP;_legacy.ASSETS=ASSETS
guard=_legacy.guard;write=_legacy.write;actors=_legacy.actors;snapshot=_legacy.snapshot;settings=_legacy.settings
def audit_maps():
    guard(True,True)
    reg=u.AssetRegistryHelpers.get_asset_registry()
    opts=u.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True,include_searchable_names=True,include_soft_management_references=True,include_hard_management_references=True)
    rows=[]
    for name in [CURRENT]+RETIRED:
        path='/Game/Maps/'+name
        rows.append(dict(package=path,exists=u.EditorAssetLibrary.does_asset_exist(path),dependencies=[str(x) for x in (reg.get_dependencies(path,opts) or [])],referencers=[str(x) for x in (reg.get_referencers(path,opts) or [])]))
    world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
    levels=[x.get_path_name() for x in u.EditorLevelUtils.get_levels(world)]
    streaming=[x for x in levels if x!=world.get_path_name()+':PersistentLevel']
    external=[str(p.relative_to(ROOT)) for folder in ['Content/__ExternalActors__','Content/__ExternalObjects__'] for p in (ROOT/folder).rglob('*') if p.is_file()]
    return write('map-dependency-audit',dict(state=state(),packages=rows,streaming_levels=streaming,external_actor_files=external))
def cleanup():
    guard(True,True)
    report=audit_maps();obsolete={'/Game/Maps/'+n for n in RETIRED}
    assert not report['streaming_levels'] and not report['external_actor_files']
    for row in report['packages']:
        if row['package'] in obsolete:assert not set(row['referencers'])-obsolete,(row,'outside referencer')
        else:assert not set(row['dependencies']) & obsolete
    archive=json.loads((OUT/'archive.json').read_text())
    for row in archive['entries']:
        assert hashlib.sha256((ROOT/row['original']['path']).read_bytes()).hexdigest()==row['archive']['sha256']
    deleted=[]
    for name in RETIRED:
        path='/Game/Maps/'+name
        assert u.EditorAssetLibrary.delete_asset(path),path
        deleted.append(path)
    assert sorted(p.stem for p in (ROOT/'Content/Maps').glob('L_OpeningLobby*.umap'))==[CURRENT]
    return write('cleanup',dict(deleted=deleted,state=guard(True,True),method='EditorAssetLibrary.delete_asset after all-category registry referencer audit; exact archives outside Content.'))
def action(operation,argument=''):
    if operation=='state':return state()
    if operation=='tick_unthrottle':
        guard(True,True,pie=True)
        v=u.SystemLibrary.get_console_variable_int_value('Slate.bAllowThrottling')
        assert v==1
        write('tick-before',dict(value=v,reason='Trial PIE remained at time zero with origin camera; no frame captured.'))
        u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world(),'Slate.bAllowThrottling 0')
        return dict(before=v,after=u.SystemLibrary.get_console_variable_int_value('Slate.bAllowThrottling'))
    if operation=='tick_restore':
        guard(True,True)
        v=json.loads((OUT/'tick-before.json').read_text())['value']
        u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),'Slate.bAllowThrottling '+str(v))
        return write('tick-restored',dict(value=u.SystemLibrary.get_console_variable_int_value('Slate.bAllowThrottling'),expected=v))
    if operation=='snapshot':
        assert argument in ['Before','Final','Restored']
        return snapshot(argument,True)
    if operation=='audit_maps':return audit_maps()
    if operation=='cleanup':return cleanup()
    if operation=='cleanup_verify':
        guard(True,True)
        reg=u.AssetRegistryHelpers.get_asset_registry();reg.scan_paths_synchronous(['/Game/Maps'],True)
        assert sorted(p.stem for p in (ROOT/'Content/Maps').glob('L_OpeningLobby*.umap'))==[CURRENT]
        remaining=[str(a.package_name) for a in reg.get_assets_by_path('/Game/Maps',recursive=True)]
        assert not set(remaining)&{'/Game/Maps/'+n for n in RETIRED},remaining
        return write('cleanup',dict(remaining=remaining,state=state(),method='All nine EditorAssetLibrary.delete_asset calls returned true and unloaded packages, but left disk files. Exact archive hashes rechecked; nine explicit LiteralPath files removed without recursion; registry rescanned.',retired=RETIRED))
    if operation=='startup_defaults':
        guard(True,True)
        from architecture01_lightstudy import props
        obj=u.get_default_object(u.load_class(None,'/Script/EngineSettings.GameMapsSettings'))
        before=props(obj,{})
        for key in ['game_default_map','editor_startup_map']:obj.set_editor_property(key,u.SoftObjectPath(MAP))
        return write('startup-defaults-live',dict(before=before,after=props(obj,{}),scope='Only GameDefaultMap and EditorStartupMap synchronized with the exact on-disk task edit. No SaveConfig call.'))
    if operation=='reopen':
        guard(True,True)
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
        return write('unreal-reopened',snapshot('Final',True))
    if operation.startswith('capture_'):
        import painterfloor01_capture as capture
        return capture.run(operation[8:],argument)
    if operation in ['material','audit','bind']:
        import importlib,painterfloor01_material as material
        return getattr(importlib.reload(material),operation)()
    raise ValueError(operation)
