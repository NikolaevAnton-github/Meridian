"""Compact saved graph evidence for implementation inspection."""
from pathlib import Path
import json, sys
root=Path(__file__).resolve().parents[2]/'Saved/GASPALSLocomotion01/Worker/SourceGraph'
data=json.loads((root/(sys.argv[1]+'.json')).read_text())
for g in data['graphs']:
    if len(sys.argv)>2 and g['name'] not in sys.argv[2:]: continue
    print('\nGRAPH '+g['name'])
    for n in g['nodes']:
        if n['name'].startswith('EdGraphNode_Comment'): continue
        print(n['name']+' '+n['title'])
        for k in ['Path','TextPath','Node','BoundGraph','CrossfadeDuration']:
            if k in n.get('properties',{}): print('  @'+k+' = '+n['properties'][k])
        for p in n['pins']:
            if p['links'] or p['value'] not in ('','0','0.0','false','None','0,0,0','0.000000'):
                print('  '+p['name']+' = '+str(p['value'])+' -> '+','.join(p['links']))
