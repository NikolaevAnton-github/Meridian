"""Compact reader for the saved source graph audit; does not use the editor."""
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[2] / 'Saved/CombatSlice01/GASPEnemyFoundation01/Worker/SourceGraphs01'
data = json.loads((root / (sys.argv[1] + '.json')).read_text())
graph = next(g for g in data['graphs'] if g['name'] == sys.argv[2])
pattern = sys.argv[3].lower() if len(sys.argv) > 3 else ''
by_name = {n['name']:n for n in graph['nodes']}
for node in graph['nodes']:
    if pattern and pattern not in (node.get('title','') + ' ' + node['name']).lower():
        continue
    print(node['name'], node.get('title', node['node_class']))
    for pin in node.get('pins', []):
        links = ', '.join(c['node'] + ':' + c['pin'] + ' (' + by_name.get(c['node'],{}).get('title','') + ')' for c in pin['connections'])
        if links or pin['value']:
            print(' ', pin['direction'].replace('EdGraphPinDirection.', ''), pin['name'], pin['type'],
                  'value=' + pin['value'] if pin['value'] else '', '-> ' + links if links else '')
