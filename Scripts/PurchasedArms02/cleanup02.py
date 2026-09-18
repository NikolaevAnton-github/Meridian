"""Remove unused demo asset dependencies from the adapted gameplay copies."""
import json
import unreal as u
from adapt import BASE, OUT, preserve
from editor_toolset.toolsets.blueprint import BlueprintTools as BP
from stage1_tools import state

def run():
    assert not state()['pie'] and not state()['dirty_maps']
    bp = u.load_asset(BASE + 'Common/Core/Characters/BP_TFA_BaseCharacter')
    disabled = ['ToggleTutorialText','ToggleCameraPerspective','ToggleCameraAnimation','QuitGame',
        'ToggleUI','Zoom','FreezeTime','Look','Jump']
    removed = []
    for graph in BP.list_graphs(bp):
        editor = u.BlueprintGraphEditor.get_graph_editor(graph)
        for node in list(editor.list_all_nodes()):
            if node.get_class().get_name() == 'K2Node_EnhancedInputAction' and any('IA_TFA_'+n in str(node.get_node_title()) for n in disabled):
                removed.append(node.get_name())
                BP.delete_node(node)
    BP.compile_blueprint(bp)
    cdo = u.get_default_object(bp.generated_class())
    cdo.mesh.set_anim_instance_class(u.load_class(None,BASE+'Common/Core/Characters/ABP_TFA_FP_BaseCharacter.ABP_TFA_FP_BaseCharacter_C'))
    u.EditorAssetLibrary.save_loaded_asset(bp)
    mapping = u.load_asset(BASE+'Common/Core/Inputs/IMC_TFA_Default')
    old = mapping.get_editor_property('mappings')
    old_count = len(old)
    # UE 5.4's deprecated serialized array otherwise preserves unused input assets in 5.8.
    mapping.set_editor_property('mappings', [])
    u.EditorAssetLibrary.save_loaded_asset(mapping, only_if_is_dirty=False)
    current = mapping.get_editor_property('default_key_mappings').get_editor_property('mappings')
    result = {'removed_input_nodes':removed,'removed_deprecated_mapping_entries':old_count,
        'active_actions':sorted(set(m.action.get_name() for m in current))}
    (OUT/'cleanup02.json').write_text(json.dumps(result,indent=2))
    return result
