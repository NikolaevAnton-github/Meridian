"""Convert only the authored ADS translation to the native mesh basis."""
import hashlib
import shutil
import unreal as u
from editor_toolset.toolsets.blueprint import BlueprintTools as BP
from unreal03 import ROOT, OUT, ANIM, audit, write
from stage1_tools import state


def run():
    initial = state()
    assert not initial['pie'] and not initial['dirty_maps'] and not initial['dirty_content'], initial
    source = ROOT / ('Content/' + ANIM.removeprefix('/Game/') + '.uasset')
    backup = OUT / 'Rollback' / source.relative_to(ROOT)
    backup.parent.mkdir(parents=True, exist_ok=True)
    if backup.exists():
        assert backup.read_bytes() == source.read_bytes(), 'Never replace the immutable starting bytes.'
    else:
        shutil.copy2(source, backup)
    before = audit()
    bp = u.load_asset(ANIM)
    graph = next(g for g in BP.list_graphs(bp) if g.get_name() == 'AnimGraph')
    nodes = u.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes()
    ads = next(n for n in nodes if n.get_name() == 'AnimGraphNode_ModifyBone_2')
    data = ads.get_editor_property('node')
    assert data.get_editor_property('translation_space') == u.BoneControlSpace.BCS_WORLD_SPACE
    assert data.get_editor_property('translation_mode') == u.BoneModificationMode.BMM_ADDITIVE
    translation = next(p for p in BP.get_node_infos([ads])[0].input_pins if p.name == 'Translation')
    assert len(translation.connected_pins) == 1
    authored = translation.connected_pins[0]
    assert authored.node.get_name() == 'K2Node_VariableGet_4'

    # The source ADS vector uses forward/right/up at zero camera yaw. The native
    # mesh anchor is yaw -90 relative to that camera. Its inverse basis is +90;
    # this is a coordinate conversion, not a new aiming offset or world heading.
    rotate = BP.create_node(graph, 'Math|Vector|RotateVector', u.IntPoint(500, -650))
    pins = BP.get_node_infos([rotate])[0]
    vector = next(p.pin_id for p in pins.input_pins if p.name == 'A')
    rotation = next(p.pin_id for p in pins.input_pins if p.name == 'B')
    result = next(p.pin_id for p in pins.output_pins if p.name == 'ReturnValue')
    BP.set_pin_value(rotation, '0,90,0')
    BP.break_pins(authored, translation.pin_id)
    BP.connect_pins(authored, vector)
    BP.connect_pins(result, translation.pin_id)
    data.set_editor_property('translation_space', u.BoneControlSpace.BCS_COMPONENT_SPACE)
    ads.set_editor_property('node', data)
    BP.arrange_nodes([rotate])
    BP.compile_blueprint(bp, warnings_as_errors=True)
    assert u.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
    after = audit()
    return write('fix', {'before': before, 'after': after,
        'conversion_node': rotate.get_name(), 'conversion_rotation': BP.get_pin_value(rotation),
        'before_sha256': hashlib.sha256(backup.read_bytes()).hexdigest(),
        'after_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'compile_warnings_as_errors': True, 'saved': True})
