"""Bounded MSQ-154 editor inventory and recoverable source preservation."""
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path
import unreal as u

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/ReinforcedColumn01/Candidate01'
LOBBY = '/Game/Maps/L_OpeningLobby_PainterStone01'

def write(name, data):
    path = OUT / name
    assert not path.exists(), 'Preserve existing evidence: ' + str(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')

def preserve():
    ed = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve() == ROOT
    assert not ed.get_game_world()
    assert ed.get_editor_world().get_path_name() == LOBBY + '.L_OpeningLobby_PainterStone01'
    dirty = list(u.EditorLoadingAndSavingUtils.get_dirty_map_packages()) + list(u.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    assert not dirty, 'Unsaved owner state requires separate recoverable snapshot.'
    spec = importlib.util.spec_from_file_location('inspect_ngd', ROOT/'Scripts/NextGenDestructionIntegration01/inspect_scene.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    write('editor-before.json', dict(world=ed.get_editor_world().get_path_name(), engine=u.SystemLibrary.get_engine_version(), dirty=[], camera=str(ed.get_level_viewport_camera_info()), actors=module.actors()))
    protected = ['Content/Maps/L_OpeningLobby_PainterStone01.umap', 'Config/DefaultEngine.ini', 'MeridianSquad.uproject', 'Docs/EnvironmentDestruction01ED02.md', 'AGENTS.md', 'Docs/ProjectState.md']
    paths = [ROOT/p for p in protected] + sorted((ROOT/'Content/NextGenDestruction').rglob('*.uasset')) + sorted((ROOT/'Content/NextGenDestruction').rglob('*.umap'))
    for rel in protected:
        target = OUT/'Before'/rel
        assert not target.exists()
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/rel, target)
    write('before-hashes.json', {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    print(json.dumps(dict(preserved=len(paths), actors=len(module.actors()), dirty=[])))
    inspect_sources()

def inspect_sources():
    sources = {}
    for path in ['/Game/NextGenDestruction/Blueprints/DataAssets/Destructible/DA_Pillar_Large_Concrete_Square','/Game/NextGenDestruction/GeometryCollections/Concrete/GC_ConcretePillar_Square_5m','/Game/NextGenDestruction/Meshes/Props/SM_ConcretePillar_Square_5m_REBAR','/Game/OpeningLobby/FunctionalBuild01/Meshes/SM_FB01_TallColumn','/Game/OpeningLobby/MaterialsComplete01/SlabLayout01/MI_Slabs_035']:
        obj = u.load_asset(path)
        task=u.AssetExportTask()
        for key,value in dict(object=obj, filename=str(OUT/(obj.get_name()+'.t3d')), automated=True, prompt=False, replace_identical=False).items():
            task.set_editor_property(key,value)
        result=u.Exporter.run_asset_export_task(task)
        sources[path] = dict(exported=result, class_name=obj.get_class().get_name())
    write('sources.json', sources)
    print(json.dumps(sources))

def capabilities():
    names=['GeometryCollectionLibrary','GeometryCollection','GeometryCollectionFactory','GeometryScript_AssetUtils','NGDTools']
    info={n:{k:getattr(getattr(u,n),k).__doc__ for k in dir(getattr(u,n)) if any(s in k.lower() for s in ['create','append','fracture','mesh','collision','cluster'])} for n in names if hasattr(u,n)}
    write('api-capabilities.json', info)
    print(json.dumps({n:list(v) for n,v in info.items()}))
