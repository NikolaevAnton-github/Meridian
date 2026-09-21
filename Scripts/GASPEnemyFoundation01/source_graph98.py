"""Read source Blueprint graphs/CDOs through the installed Unreal APIs; never save."""
import json
from pathlib import Path
import unreal as u

OUT = Path('D:/devgames/MeridianSquad/Saved/CombatSlice01/GASPEnemyFoundation01/Worker/SourceGraphs01')
OUT.mkdir(exist_ok=False)


def pin_info(pin):
    return dict(name=str(pin.get_pin_name()), direction=str(pin.get_pin_direction()),
        type=str(pin.get_pin_type_display_string()), value=pin.get_pin_value(),
        connections=[dict(node=p.get_owning_node().get_name(), pin=str(p.get_pin_name())) for p in pin.list_connected_pins()])


for path in [
    '/Game/Blueprints/MovementModes/BP_MovementMode_Ragdoll',
    '/Game/Blueprints/SandboxCharacter_Mover_Ragdoll',
    '/Game/Blueprints/SandboxCharacter_Mover',
    '/Game/Blueprints/SandboxCharacter_Mover_ABP',
]:
    u.log('MSQ98_LOADING ' + path)
    bp = u.load_asset(path)
    assert bp, path
    cls = u.BlueprintEditorLibrary.generated_class(bp)
    cdo = u.get_default_object(cls)
    names = u.BlueprintEditorLibrary.list_member_variable_names(bp, False)
    defaults = {}
    for name in names:
        try:
            defaults[name] = str(cdo.get_editor_property(name))
        except Exception as error:
            defaults[name] = dict(error=str(error))
    graphs = []
    for graph in u.BlueprintEditorLibrary.list_graphs(bp):
        nodes = []
        for node in u.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes():
            item = dict(name=node.get_name(), node_class=node.get_class().get_path_name())
            try:
                item.update(title=node.get_node_title(), pins=[pin_info(p) for p in node.list_all_pins()])
            except Exception as error:
                item['inspection_error'] = str(error)
            nodes.append(item)
        graphs.append(dict(name=graph.get_name(), nodes=nodes))
    result = dict(path=path, parent=str(u.BlueprintEditorLibrary.get_blueprint_parent_class(bp)), defaults=defaults, graphs=graphs)
    with (OUT / (bp.get_name() + '.json')).open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
    u.log('MSQ98_GRAPH_DONE ' + bp.get_name() + ' graphs=' + str(len(graphs)))
u.log('MSQ98_SOURCE_AUDIT_DONE')
