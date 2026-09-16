"""Guarded new Painter sample; reuse full reflected-property validator unchanged."""
import hashlib
import json
import types
from pathlib import Path
import unreal as u
from stage1_tools import state

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/OpeningLobby/PainterStone01/Worker/Correction01'
SOURCE='/Game/Maps/L_OpeningLobby_FunctionalBuild01'
MAP='/Game/Maps/L_OpeningLobby_PainterStone01'
ASSETS='/Game/OpeningLobby/PainterStone01'
SOURCE_SHA='46972ef30ef07f5a5aaa8cad0f8c026302c1269f1b5e08828e6f87795d168d31'

_legacy=types.ModuleType('painterstone01_property_validator')
_legacy.__file__=str(ROOT/'Scripts/OpeningLobby/materialintegration01_unreal.py')
exec(compile(Path(_legacy.__file__).read_text(),_legacy.__file__,'exec'),_legacy.__dict__)
_legacy.OUT=OUT
_legacy.MAP=MAP
_legacy.ASSETS=ASSETS
guard=_legacy.guard
write=_legacy.write
actors=_legacy.actors
snapshot=_legacy.snapshot
settings=_legacy.settings

def clean_project():
    s=state()
    assert Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve()==ROOT,s
    assert not s['pie'] and not s['dirty_maps'] and not s['dirty_content'],s
    assert hashlib.sha256((ROOT/'Content/Maps/L_OpeningLobby_FunctionalBuild01.umap').read_bytes()).hexdigest()==SOURCE_SHA
    return s

def action(operation,argument=''):
    OUT.mkdir(parents=True,exist_ok=True)
    if operation=='state':return state()
    if operation=='final_state':
        clean_project()
        return write('final-state',snapshot('Restored',True))
    if operation=='load_source':
        clean_project()
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(SOURCE)
        return write('source-preflight',dict(source_sha256=SOURCE_SHA,state=guard(False,True)))
    if operation=='source_snapshot':
        assert not (OUT/'Source/all-properties.json').exists()
        return snapshot('Source',False)
    if operation=='load_candidate':
        guard(False,True)
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
        return guard(True,True)
    if operation=='create':
        guard(False,True)
        assert not u.EditorAssetLibrary.does_asset_exist(MAP)
        assert (OUT/'Source/all-properties.json').exists()
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).new_level_from_template(MAP,SOURCE)
        return write('created',dict(source=SOURCE,candidate=MAP,method='new_level_from_template',template=snapshot('Template',True)))
    if operation=='reopen':
        guard(True,True)
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(SOURCE)
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
        return write('unreal-reopened',snapshot('Final',True))
    if operation.startswith('capture_'):
        import painterstone01_capture as capture
        if operation=='capture_prepare':
            assert capture.active is None
            import importlib
            capture=importlib.reload(capture)
        return capture.run(operation[8:],argument)
    if operation in ('material','audit','bind','sampling_variation'):
        import importlib
        import painterstone01_material as material
        material=importlib.reload(material)
        return getattr(material,operation)()
    raise ValueError(operation)
