"""Print bounded source graph evidence from the native node audit."""
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2] / 'Saved/PurchasedArms02/Worker/SourceGraphs'
rows = json.loads((ROOT / sys.argv[1] / 'nodes.json').read_text())
for graph in rows:
    if len(sys.argv) > 2 and sys.argv[2] not in graph['path']:
        continue
    nodes = {n['name']: n for n in graph['nodes']}
    print('\nGRAPH', graph['path'].split(':')[-1])
    if len(sys.argv) > 3:
        visited = set()
        def walk(name, indent=''):
            if name in visited:
                return
            visited.add(name)
            n = nodes[name]
            print(indent + n['name'] + ': ' + n['type'])
            print(indent + ' INPUTS ' + str([(p['name'], p['value'], [q['node'] for q in p['links']]) for p in n['inputs'] if p['type'] != 'exec']))
            for p in n['outputs']:
                if p['type'].lower() == 'exec' and p['links']:
                    print(indent + ' -> ' + p['name'])
                    for q in p['links']:
                        walk(q['node'], indent + '  ')
        for n in nodes.values():
            if sys.argv[3] in n['type']:
                walk(n['name'])
    else:
        for n in nodes.values():
            print(n['name'], n['type'], [(p['name'], p['value']) for p in n['inputs'] if p['value']], [(p['name'], [q['node'] for q in p['links']]) for p in n['outputs'] if p['links']])
