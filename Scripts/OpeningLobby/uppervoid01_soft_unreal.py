"""UpperVoid01 native scene operations, with reused guarded evidence primitives."""
import json,types,hashlib,importlib
from pathlib import Path
import unreal as u
from stage1_tools import state
from architecture01_lightstudy import props
ROOT=Path('D:/devgames/MeridianSquad')
OUT=ROOT/'Saved/OpeningLobby/UpperVoid01/HeightCorrection02/Worker'
ASSETS='/Game/OpeningLobby/UpperVoid01'
MAP=SOURCE='/Game/Maps/L_OpeningLobby_PainterStone01'
p=ROOT/'Scripts/OpeningLobby/materialintegration01_unreal.py'
legacy=types.ModuleType('uppervoid_properties');legacy.__file__=str(p)
source=p.read_text().replace("(folder / 'property-schemas.json').write_text(json.dumps(schemas, separators=(',', ':')))","pass # Immutable schema reference retained in predecessor")
source=source.replace("(folder / 'all-properties.json').write_text(json.dumps(data, separators=(',', ':')))","__import__('gzip').open(folder / 'all-properties.json.gz','wt',encoding='utf-8').write(json.dumps(data,separators=(',', ':')))")
exec(compile(source,str(p),'exec'),legacy.__dict__)
legacy.OUT=OUT;legacy.MAP=MAP;legacy.SOURCE=MAP;legacy.ASSETS=ASSETS
guard=legacy.guard;write=legacy.write;snapshot=legacy.snapshot;actors=legacy.actors;settings=legacy.settings

def action(operation,argument=''):
    if operation=='state':return state()
    if operation=='initial':
        s=guard(True,True,pie=state()['pie']);return write('initial-live-state',s)
    if operation=='stop':
        guard(True,True,pie=True);u.get_editor_subsystem(u.LevelEditorSubsystem).editor_request_end_play();return {'requested':True}
    if operation=='play':
        guard(True,True);u.get_editor_subsystem(u.LevelEditorSubsystem).editor_play_simulate();return {'requested':True}
    if operation=='inspect':
        guard(True,True);assert not (OUT/'Before/all-properties.json').exists()
        result=snapshot('Before',True);schemas={};records={}
        for a in actors():
            if isinstance(a,(u.Light,u.PostProcessVolume,u.ExponentialHeightFog)):
                records[a.get_name()]=dict(label=a.get_actor_label(),actor=props(a,schemas),components={c.get_name():props(c,schemas) for c in a.get_components_by_class(u.ActorComponent)})
        write('lights-before',records)
        names=['Material','MaterialExpressionWorldPosition','MaterialExpressionSceneTexture','MaterialExpressionCustom','PostProcessVolume','ExponentialHeightFogComponent','LightComponent']
        for n in names:
            schemas[n]=json.loads(u.ToolsetLibrary.list_struct_properties(getattr(u,n).static_class()))
        write('capabilities',schemas)
        return result
    if operation.startswith('capture_'):
        import uppervoid01_soft_capture as cap
        return cap.run(operation[8:],argument)
    if operation=='build':
        import uppervoid01_soft_material as m
        return importlib.reload(m).build(argument)
    if operation=='snapshot':return snapshot(argument,True)
    if operation=='audit':
        import uppervoid01_soft_material as m
        return importlib.reload(m).audit(argument)
    if operation=='reopen':
        guard(True,True)
        ms=[u.load_asset(p) for p in u.EditorAssetLibrary.list_assets(ASSETS,recursive=True,include_folder=False)]
        result=u.EditorLoadingAndSavingUtils.reload_packages([m.get_outermost() for m in ms])
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
        return write('reopened',dict(reload=str(result),snapshot=snapshot('Reopened',True)))
    if operation.startswith('runtime_'):
        import uppervoid01_soft_runtime as r
        return r.action(operation[8:],argument)
    raise ValueError(operation)
