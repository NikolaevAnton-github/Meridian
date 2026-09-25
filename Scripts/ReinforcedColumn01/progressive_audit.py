"""MSQ-156 immutable preservation and settings evidence (no gameplay)."""
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/ReinforcedColumn02/Candidate01'

def write(name, value):
    path = OUT / name
    assert not path.exists(), path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def preserve_disk():
    roots = ['Content/ReinforcedColumn01', 'Assets/Source/ReinforcedColumn01',
             'Scripts/ReinforcedColumn01']
    paths = [p for rel in roots for p in (ROOT/rel).rglob('*') if p.is_file() and '__pycache__' not in str(p)]
    paths += [ROOT/p for p in ['Content/Maps/L_OpeningLobby_PainterStone01.umap',
              'Source/MeridianSquad/NGDColumnAuthoring.cpp', 'Source/MeridianSquad/NGDColumnAuthoring.h',
              'Source/MeridianSquad/NGDPropComponent.cpp', 'Source/MeridianSquad/MeridianSquad.Build.cs',
              'Config/DefaultEngine.ini','MeridianSquad.uproject','Docs/EnvironmentDestruction01ED02.md',
              'AGENTS.md','Docs/ProjectState.md']]
    records = {}
    for p in paths:
        rel = p.relative_to(ROOT)
        dest = OUT/'Before'/rel
        assert not dest.exists(), dest
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
        records[rel.as_posix()] = digest(p)
    write('before-hashes.json', records)
    protected = [p for folder in ['Content/NextGenDestruction','Content/OpeningLobby',
                 'Saved/ReinforcedColumn01/Candidate01'] for p in (ROOT/folder).rglob('*')
                 if p.is_file() and '__pycache__' not in str(p)]
    protected += [ROOT/p for p in ['Config/DefaultEngine.ini','MeridianSquad.uproject',
                                  'Docs/EnvironmentDestruction01ED02.md','AGENTS.md','Docs/ProjectState.md']]
    write('protected-hashes.json', {p.relative_to(ROOT).as_posix():digest(p) for p in protected})
    print(json.dumps(dict(copied=len(paths), bytes=sum(p.stat().st_size for p in paths), protected=len(protected))))

def settings():
    config_path = ROOT/'Saved/ContextBudget02/runs/01a0d9d4-c0d2-7c77-80da-541871c978b8/native-config.json'
    config = json.loads(config_path.read_text())
    sessions = ROOT/'Saved/Multica/workspaces/meridiansqu-6f91832bf07d/msq-156-541871c978b8/codex-home/sessions'
    contexts = []
    for path in sessions.rglob('*.jsonl'):
        for line in path.open(encoding='utf-8'):
            if '"turn_context"' not in line[:150]:
                continue
            row = json.loads(line)
            if row.get('type') == 'turn_context':
                contexts.append({k:row['payload'].get(k) for k in ['model','effort','service_tier','cwd']})
    raw = subprocess.check_output(['powershell','-NoProfile','-Command',
          "Get-CimInstance Win32_Process -Filter \"Name = 'codex.exe'\" | Select-Object ProcessId,CommandLine | ConvertTo-Json"],text=True)
    native=[]
    for row in json.loads(raw):
        command=(row['CommandLine'] or '').replace('\\','').replace('"','')
        if 'model_reasoning_effort' not in command:
            continue
        native.append(dict(pid=row['ProcessId'],model=re.search(r'model=([^ ]+)',command).group(1),
                      effort=re.search(r'model_reasoning_effort=([^ ]+)',command).group(1),
                      tier=re.search(r'service_tier=([^ ]+)',command).group(1),fast_disabled='--disable fast_mode' in command))
    assert config['model_reasoning_effort']=='max' and config['service_tier']=='default'
    assert contexts and all(c['model']=='gpt-6-astra' and c['effort']=='max' for c in contexts)
    assert native and all(n['model']=='gpt-6-astra' and n['effort']=='max' and n['tier']=='default' and n['fast_disabled'] for n in native)
    write('native-settings.json',dict(config_path=config_path.relative_to(ROOT).as_posix(),config_sha256=digest(config_path),
          configured={k:config[k] for k in ['role','model_reasoning_effort','service_tier']},actual_contexts=contexts,native_arguments=native))
    print(json.dumps(dict(configured='Astra/max/default',actual_contexts=contexts,native=native)))

def editor_before():
    import unreal as u
    ed=u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve()==ROOT
    assert not ed.get_game_world()
    assert ed.get_editor_world().get_path_name()=='/Game/Maps/L_OpeningLobby_PainterStone01.L_OpeningLobby_PainterStone01'
    dirty=list(u.EditorLoadingAndSavingUtils.get_dirty_map_packages())+list(u.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    assert not dirty, 'Preserve unsaved packages before authoring.'
    spec=importlib.util.spec_from_file_location('ngd_inspect',ROOT/'Scripts/NextGenDestructionIntegration01/inspect_scene.py')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    rows=module.actors()
    write('editor-before.json',dict(world=ed.get_editor_world().get_path_name(),dirty=[],camera=str(ed.get_level_viewport_camera_info()),actors=rows))
    vendor=u.load_asset('/Game/NextGenDestruction/GeometryCollections/Concrete/GC_ConcretePillar_Square_5m')
    data=json.loads(u.NGDColumnAuthoring.inspect_collection(vendor))
    write('vendor-hierarchy-before.json',data)
    print(json.dumps(dict(actors=len(rows),vendor={k:v for k,v in data.items() if k!='hierarchy'})))

if __name__=='__main__':
    preserve_disk()
    settings()
