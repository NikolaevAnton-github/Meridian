"""Route only magazine display through authoritative live ammunition."""
import hashlib
import shutil
import unreal as u
from editor_toolset.toolsets.blueprint import BlueprintTools as BP
from unreal68 import ROOT, OUT, state, write

ASSET = '/Game/InfimaGames/TacticalFPSAnimations/Weapons/AssaultRifle/Meshes/ABP_TFA_AR_Magazine'

def run():
    initial = state()
    assert not initial['pie'] and not initial['dirty_maps'] and not initial['dirty_content'], initial
    source = ROOT / ('Content/' + ASSET.removeprefix('/Game/') + '.uasset')
    backup = OUT / 'Rollback' / source.relative_to(ROOT)
    backup.parent.mkdir(parents=True, exist_ok=True)
    assert not backup.exists(), 'Never replace immutable rollback bytes'
    shutil.copy2(source, backup)
    bp = u.load_asset(ASSET)
    graph = next(g for g in BP.list_graphs(bp) if g.get_name() == 'EventGraph')
    nodes = u.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes()
    before = BP.read_graph_dsl(graph)
    setter = next(n for n in nodes if n.get_name() == 'K2Node_VariableSet_0')
    ammo = next(p for p in BP.get_node_infos([setter])[0].input_pins if p.name == 'AmmoCount')
    assert len(ammo.connected_pins) == 1
    getter = BP.create_node(graph, 'Combat|Presentation|GetCombatMagazineRounds', u.IntPoint(200, 250))
    output = next(p for p in BP.get_node_infos([getter])[0].output_pins if p.name == 'ReturnValue')
    BP.break_pins(ammo.connected_pins[0], ammo.pin_id)
    BP.connect_pins(output.pin_id, ammo.pin_id)
    BP.compile_blueprint(bp, warnings_as_errors=True)
    assert u.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
    return write('magazine-adaptation', {'before': before, 'after': BP.read_graph_dsl(graph),
        'before_sha256': hashlib.sha256(backup.read_bytes()).hexdigest(),
        'after_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'state': state()})
