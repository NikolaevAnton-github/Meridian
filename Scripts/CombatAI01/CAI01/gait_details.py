"""Read-only imported movement-mode pin/default audit; no asset writes or PIE."""
import json
import unreal as u
from Scripts.CombatAI01.CAI01.editor_tools import state, OUT

current = state()
assert not current['pie']
bp = u.load_asset('/GASPEnemyFoundation01/Blueprints/MovementModes/BP_MovementMode_Walking')
cdo = u.get_default_object(u.BlueprintEditorLibrary.generated_class(bp))
result = dict(state=current, asset=bp.get_path_name(), defaults={}, graphs=[])
for name in u.BlueprintEditorLibrary.list_member_variable_names(bp, False):
    if any(x in name.lower() for x in ['speed', 'decel', 'accel']):
        result['defaults'][name] = str(cdo.get_editor_property(name))
for graph in u.BlueprintEditorLibrary.list_graphs(bp):
    nodes = []
    for node in u.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes():
        nodes.append(dict(name=node.get_name(), title=node.get_node_title(),
            pins=[dict(name=str(p.get_pin_name()), type=str(p.get_pin_type_display_string()), value=p.get_pin_value(),
                links=[c.get_owning_node().get_name()+':'+str(c.get_pin_name()) for c in p.list_connected_pins()])
                for p in node.list_all_pins()]))
    result['graphs'].append(dict(name=graph.get_name(), nodes=nodes))
result['after'] = state()
(OUT / 'gait-movement-mode.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result['defaults']))
