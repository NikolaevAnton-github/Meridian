"""MSQ-152 current-state preservation and source-demo inventory (editor Python)."""
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path
import unreal as u

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/LobbyPlaytestFix01/Candidate01'
LOBBY = '/Game/Maps/L_OpeningLobby_PainterStone01'

def write(name, value):
    path = OUT / name
    assert not path.exists(), 'Immutable evidence already exists: ' + str(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')
    return path

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def actor_inventory():
    spec = importlib.util.spec_from_file_location('ngd_inspect', ROOT / 'Scripts/NextGenDestructionIntegration01/inspect_scene.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.actors()

def preserve():
    ed = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve() == ROOT
    assert not ed.get_game_world()
    assert ed.get_editor_world().get_path_name() == LOBBY + '.L_OpeningLobby_PainterStone01'
    dirty = [p.get_path_name() for p in list(u.EditorLoadingAndSavingUtils.get_dirty_map_packages()) + list(u.EditorLoadingAndSavingUtils.get_dirty_content_packages())]
    write('editor-before.json', dict(world=ed.get_editor_world().get_path_name(), engine=u.SystemLibrary.get_engine_version(), dirty=dirty, camera=str(ed.get_level_viewport_camera_info()), actors=actor_inventory()))
    assert not dirty, 'Capture recoverable unsaved state before continuing.'
    protected = ['Content/Maps/L_OpeningLobby_PainterStone01.umap', 'Config/DefaultEngine.ini', 'MeridianSquad.uproject', 'Docs/EnvironmentDestruction01ED02.md', 'AGENTS.md', 'Docs/ProjectState.md']
    paths = [ROOT / p for p in protected] + sorted((ROOT / 'Content/NextGenDestruction').rglob('*.uasset')) + sorted((ROOT / 'Content/NextGenDestruction').rglob('*.umap'))
    for relative in protected:
        source = ROOT / relative
        target = OUT / 'Before' / relative
        assert not target.exists()
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    hashes = {p.relative_to(ROOT).as_posix(): digest(p) for p in paths}
    write('before-hashes.json', hashes)
    print(json.dumps(dict(actors=len(actor_inventory()), protected_files=len(hashes), dirty=dirty, backup=str(OUT / 'Before'))))

PROPERTIES = ['DataAsset', 'GC', 'SwitchMatOnBreak', 'MatIndicesToSwitch', 'SwitchToMat',
              'BreakSound', 'BreakSoundFreqMin', 'BreakSoundFreqMax', 'CollisionSoundFreqMin',
              'CollisionSoundFreqMax', 'MinDamageRadius', 'BulletHitSound', 'PiecesCollisionSound',
              'PhysMat', 'Damage Threshold', 'BreakingFX', 'HasKinematicPieces',
              'Override Damage Thresholds', 'Material Overrides']

def value(v):
    if v is None or isinstance(v, (str, bool, int, float)):
        return v
    if isinstance(v, u.Object):
        return v.get_path_name()
    if isinstance(v, u.Map):
        return {str(k): value(x) for k, x in v.items()}
    if isinstance(v, (u.Array, list, tuple)):
        return [value(x) for x in v]
    return v.export_text() if hasattr(v, 'export_text') else str(v)

def prop_record(a):
    gc = a.get_component_by_class(u.GeometryCollectionComponent)
    origin, extent = a.get_actor_bounds(False)
    return dict(name=a.get_name(), label=a.get_actor_label(),
                location=value(a.get_actor_location()), rotation=value(a.get_actor_rotation()),
                scale=value(a.get_actor_scale3d()), bounds=dict(origin=value(origin), extent=value(extent)),
                config={k:value(a.get_editor_property(k)) for k in PROPERTIES},
                collection=value(gc.get_editor_property('rest_collection')),
                materials=[value(gc.get_material(i)) for i in range(gc.get_num_materials())],
                gc_collision=str(gc.get_collision_profile_name()),
                gc_damage=value(gc.get_editor_property('damage_threshold')))

def inventory_demo():
    ed = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert ed.get_editor_world().get_path_name() == '/Game/NextGenDestruction/Maps/DemoMap.DemoMap'
    rows = [prop_record(a) for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
            if a.get_class().get_name() == 'BP_BreakableObject_C']
    catalog = sorted(str(a.package_name) for a in u.AssetRegistryHelpers.get_asset_registry().get_assets_by_path('/Game/NextGenDestruction/Blueprints/DataAssets/Destructible', True) if str(a.asset_name).startswith('DA_'))
    groups = {}
    for row in rows:
        signature = json.dumps([row[k] for k in ['config', 'collection', 'materials', 'scale', 'gc_collision', 'gc_damage']], sort_keys=True)
        groups.setdefault(signature, []).append(row['name'])
    write('demo-inventory.json', dict(world=ed.get_editor_world().get_path_name(), catalog=catalog, instances=rows, distinct=[dict(source_actors=names, signature=json.loads(sig)) for sig,names in groups.items()]))
    print(json.dumps(dict(instances=len(rows), distinct=len(groups), catalog=len(catalog), groups=[dict(actors=names,data=json.loads(sig)[0]['DataAsset'].split('.')[-1]) for sig,names in groups.items()])))

# Positions are in cm at source scale. The retained three actors are untouched.
# Small mugs rest on the authored coffee tabletop (63.907742 cm high).
PLACEMENTS = [
    ('LargeConcretePillar', 'DA_Pillar_Large_Concrete_Square', (-1900,700,0), 0),
    ('PlasterWall', 'DA_Wall_Plaster', (-968,-700,0), -90),
    ('LargeGlass', 'DA_Window_Large', (1680,-700,176.928711), 0),
    ('WoodWall', 'DA_Wall_Wood', (840,-700,125), -90),
    ('WoodDesk', 'DA_Desk_Wood', (-1789.323204,603.68,0), 0),
    ('DiningTable', 'DA_DiningTable_Wood', (1680,700,0), 0),
    ('WoodFrame', 'DA_Wall_WoodenBeams', (-128,-700,0), -90),
    ('MarbleMug', 'DA_Mug02', (1032,750,64.107742), 0),
    ('PlainMug', 'DA_Mug01', (988,750,64.107742), 0),
    ('CoffeeTable', 'DA_CoffeeTable_Wood', (1010,750,0), 0),
    ('SmallGlass', 'DA_Window_Small', (-1680,-700,76.102371), 0),
]

def place():
    ed = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    world = ed.get_editor_world()
    assert world.get_path_name() == LOBBY + '.L_OpeningLobby_PainterStone01' and not ed.get_game_world()
    assert not list(u.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    demo = json.loads((OUT / 'demo-inventory.json').read_text())
    prototypes = {r['config']['DataAsset'].split('.')[-1]: r for r in demo['instances']}
    existing = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
    existing = {a.get_actor_label():a for a in existing}
    placed = []
    with u.ScopedEditorTransaction('MSQ-152 distinct vendor demo assortment'):
        for identity, data_name, location, yaw in PLACEMENTS:
            source = prototypes[data_name]
            data = u.load_asset(source['config']['DataAsset'])
            overrides = source['config']['Material Overrides']
            label = 'LPF01_' + identity
            a = existing.get(label)
            if not a:
                if overrides:
                    a = u.NGDTools.spawn_prop_with_materials(world, data, u.Vector(*location), u.Rotator(pitch=0,yaw=yaw,roll=0), label, {int(k):u.load_asset(v) for k,v in overrides.items()})
                else:
                    a = u.NGDTools.spawn_prop(world, data, u.Vector(*location), u.Rotator(pitch=0,yaw=yaw,roll=0), label)
            assert a and a.get_component_by_class(u.NGDPropComponent)
            a.set_folder_path('LobbyPlaytestFix01_DemoProps')
            a.tags = list(dict.fromkeys(list(a.tags) + ['LobbyPlaytestFix01']))
            row = prop_record(a)
            for key in ['config', 'collection', 'materials', 'scale', 'gc_collision', 'gc_damage']:
                assert row[key] == source[key], (data_name, key, row[key], source[key])
            row['source_actors'] = [r['name'] for r in demo['instances'] if r['config'] == source['config']]
            placed.append(row)
    write('placement.json', placed)
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    write('editor-after-placement.json', dict(actors=actor_inventory(), props=[prop_record(a) for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if a.get_component_by_class(u.NGDPropComponent)]))
    print(json.dumps(dict(added=len(placed), saved=True)))

def spatial_check(name='spatial-check.json', start=-1950, end=1950):
    ed = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert not ed.get_game_world()
    actors = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
    bounds = {}
    for a in actors:
        center, extent = a.get_actor_bounds(True)
        bounds[a.get_name()] = dict(label=a.get_actor_label(), managed=bool(a.get_component_by_class(u.NGDPropComponent)),
            minimum=[center.x-extent.x,center.y-extent.y,center.z-extent.z], maximum=[center.x+extent.x,center.y+extent.y,center.z+extent.z])
    overlaps = []
    for key, a in bounds.items():
        if not a['managed']:
            continue
        for other, b in bounds.items():
            if other == key or (b['managed'] and other < key):
                continue
            penetration = [min(a['maximum'][i],b['maximum'][i])-max(a['minimum'][i],b['minimum'][i]) for i in range(3)]
            if min(penetration) > .25:
                overlaps.append(dict(a=a['label'], b=b['label'], penetration=penetration))
    routes = []
    for y in [0,-1000,1000]:
        result = json.loads(u.NGDTools.sweep(ed.get_editor_world(),u.Vector(start,y,100),u.Vector(end,y,100),45))
        routes.append(dict(y=y, radius=45, result=result))
    write(name,dict(bounds=bounds,conservative_overlaps=overlaps,routes=routes,start=start,end=end))
    print(json.dumps(dict(overlaps=overlaps,routes=routes)))
