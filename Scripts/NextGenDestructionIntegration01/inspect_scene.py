"""Read-only scene evidence; preserve current disk bytes before lobby edits."""
import hashlib
import json
import shutil
from pathlib import Path
import unreal as u

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/NextGenDestructionIntegration01/NGD-01/Candidate01'
LOBBY = '/Game/Maps/L_OpeningLobby_PainterStone01'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def vec(v):
    return [v.x, v.y, v.z]

def actors():
    rows = []
    for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
        row = dict(name=a.get_name(), label=a.get_actor_label(), cls=a.get_class().get_path_name(),
                   location=vec(a.get_actor_location()), rotation=str(a.get_actor_rotation()),
                   scale=vec(a.get_actor_scale3d()), folder=str(a.get_folder_path()),
                   tags=[str(t) for t in a.tags], components=[])
        for c in a.get_components_by_class(u.PrimitiveComponent):
            part = dict(name=c.get_name(), cls=c.get_class().get_path_name(),
                        transform=str(c.get_world_transform()), collision=str(c.get_collision_enabled()),
                        profile=str(c.get_collision_profile_name()),
                        materials=[m.get_path_name() if m else None for m in [c.get_material(i) for i in range(c.get_num_materials())]])
            if isinstance(c, u.StaticMeshComponent):
                part['mesh'] = c.static_mesh.get_path_name() if c.static_mesh else None
            if isinstance(c, u.GeometryCollectionComponent):
                part['gc'] = str(c.get_editor_property('rest_collection'))
            row['components'].append(part)
        if a.get_class().get_name() == 'BP_BreakableObject_C':
            row['data_asset'] = str(a.get_editor_property('DataAsset'))
        rows.append(row)
    return sorted(rows, key=lambda x: x['name'])

def capture(name):
    assert Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve() == ROOT.resolve()
    editor = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert not editor.get_game_world(), 'PIE must be stopped.'
    world = editor.get_editor_world()
    dirty = list(u.EditorLoadingAndSavingUtils.get_dirty_map_packages()) + list(u.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    record = dict(engine=u.SystemLibrary.get_engine_version(), project=str(ROOT), world=world.get_path_name(),
                  dirty=[p.get_path_name() for p in dirty], camera=str(editor.get_level_viewport_camera_info()), actors=actors())
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / (name + '.json')
    assert not target.exists(), 'Evidence is immutable: ' + str(target)
    target.write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps(dict(evidence=name, world=record['world'], dirty=record['dirty'], actors=len(record['actors']))))
    return record

def preserve():
    record = capture('editor-preflight')
    assert not record['dirty'], 'Preserve live unsaved packages before changing maps.'
    backup = OUT / 'Before'
    backup.mkdir(exist_ok=True)
    src = ROOT / 'Content/Maps/L_OpeningLobby_PainterStone01.umap'
    dst = backup / src.name
    assert not dst.exists()
    shutil.copy2(src, dst)
    paths = [src] + sorted((ROOT / 'Content/NextGenDestruction').rglob('*.uasset')) + sorted((ROOT / 'Content/NextGenDestruction').rglob('*.umap'))
    manifest = {str(p.relative_to(ROOT)).replace('\\', '/'): digest(p) for p in paths}
    (OUT / 'before-hashes.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(dict(snapshot=str(dst), files=len(manifest), map_hash=manifest['Content/Maps/L_OpeningLobby_PainterStone01.umap'])))
