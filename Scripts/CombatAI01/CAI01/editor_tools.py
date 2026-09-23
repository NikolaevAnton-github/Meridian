"""MSQ-103 read-only gait audit and guarded native-build lifecycle, via Epic MCP."""
import json
from pathlib import Path
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration
from Scripts.CombatAI01.CAI00.editor_tools import state

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/CombatAI01/CAI-01/Worker/Candidate01'


@u.uclass()
class CombatAI01Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str) -> str:
        current = state()
        OUT.mkdir(parents=True, exist_ok=True)
        assert current['map'] == '/Game/Maps/L_OpeningLobby_PainterStone01.L_OpeningLobby_PainterStone01'
        if operation in ('before', 'after', 'close'):
            if operation == 'close':
                assert not current['pie'] and not current['dirty'], current
            (OUT / ('editor-' + operation + '.json')).write_text(json.dumps(current, indent=2))
            if operation == 'close':
                u.SystemLibrary.quit_editor()
            return json.dumps(current)
        if operation == 'gait':
            assert not current['pie'], current
            result = dict(state=current, blueprints=[])
            for name in ['SandboxCharacter_Mover', 'SandboxCharacter_Mover_ABP']:
                bp = u.load_asset('/GASPEnemyFoundation01/Blueprints/' + name)
                graphs = []
                for graph in u.BlueprintEditorLibrary.list_graphs(bp):
                    if not any(s in graph.get_name().lower() for s in ['gait', 'speed', 'input']):
                        continue
                    nodes = []
                    for node in u.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes():
                        nodes.append(dict(name=node.get_name(), title=node.get_node_title(),
                            pins=[dict(name=str(p.get_pin_name()), type=str(p.get_pin_type_display_string()),
                                value=p.get_pin_value(), links=[c.get_owning_node().get_name()+':'+str(c.get_pin_name())
                                    for c in p.list_connected_pins()]) for p in node.list_all_pins()]))
                    graphs.append(dict(name=graph.get_name(), nodes=nodes))
                result['blueprints'].append(dict(path=bp.get_path_name(), graphs=graphs))
            result['after'] = state()
            (OUT / 'gait-mapping.json').write_text(json.dumps(result, indent=2))
            return json.dumps(dict(output='gait-mapping.json', state=result['after']))
        raise ValueError(operation)


registration = Registration([CombatAI01Tools])
registration.register()
