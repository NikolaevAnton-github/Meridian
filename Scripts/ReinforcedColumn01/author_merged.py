"""Author the direct MSQ-156 follow-up without PIE, map edits or vendor writes."""
import json
from pathlib import Path
import unreal as u

ROOT = Path('D:/devgames/MeridianSquad')
DEST = '/Game/ReinforcedColumn01/'
LOBBY = '/Game/Maps/L_OpeningLobby_PainterStone01'


def build():
    out = ROOT / 'Saved/ColumnDebris03'
    evidence = out / 'asset-build.json'
    assert not evidence.exists()
    ed = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve() == ROOT
    assert not ed.get_game_world()
    assert ed.get_editor_world().get_path_name() == LOBBY + '.L_OpeningLobby_PainterStone01'
    assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    assert not u.EditorLoadingAndSavingUtils.get_dirty_content_packages()
    source_path = ROOT/'Assets/Source/ReinforcedColumn01/ReinforcedColumn02-Candidate01/column05.json'
    # Topology must not be rebuilt while the old collection is registered.
    u.EditorLoadingAndSavingUtils.new_blank_map(False)
    result = json.loads(u.NGDColumnAuthoring.build_column(str(source_path)))
    assert 'error' not in result, result
    gc = u.load_asset(DEST + 'GC_RC01_BondedConcrete')
    source_dir = ROOT/'Assets/Source/ReinforcedColumn01/ReinforcedColumn02-Candidate01'
    result = json.loads(u.NGDColumnAuthoring.apply_merged_collision(gc,
        str(source_dir/'collision04.json'), str(source_dir/'design05.json')))
    evidence.write_text(json.dumps(result, indent=2))
    assert 'error' not in result, result
    assert result['geometries'] == 600 and result['anchored_count'] == 120
    assert result['level_counts'] == {'0': 1, '1': 600}
    assert not result['leaves_without_convex']
    assert result['convex_hulls'] < 765
    assert result['convex_vertices'] < 9442
    fx_path = DEST + 'NS_RC03_ConcreteCrumbs'
    assert not u.EditorAssetLibrary.does_asset_exist(fx_path)
    fx = u.EditorAssetLibrary.duplicate_asset('/Game/NextGenDestruction/FX/Destruction/Spawnable/NS_Breaking_Concrete', fx_path)
    assert fx
    fx_result = json.loads(u.NGDColumnAuthoring.configure_concrete_crumbs(fx))
    (out/'crumbs-build.json').write_text(json.dumps(fx_result, indent=2))
    assert 'error' not in fx_result, fx_result
    data = u.load_asset(DEST + 'DA_RC01_Column')
    assert abs(data.get_editor_property('DamageRadius') - .48) < 1e-5
    data.set_editor_property('BreakingVFX', fx)
    allowed = {DEST+n for n in ['GC_RC01_BondedConcrete','DA_RC01_Column','NS_RC03_ConcreteCrumbs','SM_RC02_Preview_Shallow','SM_RC02_Preview_Deep']}
    dirty = u.EditorLoadingAndSavingUtils.get_dirty_content_packages()
    assert all(p.get_path_name() in allowed for p in dirty), [p.get_path_name() for p in dirty]
    for path in sorted(allowed):
        assert u.EditorAssetLibrary.save_asset(path, only_if_is_dirty=True)
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(LOBBY)
    print(json.dumps(dict(geometries=result['geometries'], anchored=result['anchored_count'],
        convex_hulls=result['convex_hulls'], convex_vertices=result['convex_vertices'], emitters=fx_result['emitters'])))
