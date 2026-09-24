"""Check real exported source graph edges/defaults against the authored adaptation."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/GASPALSLocomotion01/Worker'
before=json.loads((OUT/'anim-graph-before.json').read_text())
after=json.loads((OUT/'anim-graph-final.json').read_text())
index=lambda graphs:{(g['name'],n['name']):n for g in graphs for n in g['nodes']}
old,new=index(before),index(after)
assert old.keys()<=new.keys(),'Original source graph nodes must be retained'
changes=[]
for key in old:
    a,b=old[key],new[key]
    if a['pins']!=b['pins']:
        changes.append(dict(graph=key[0],node=key[1],before=a['pins'],after=b['pins']))
root=old[('AnimGraph','AnimGraphNode_Root_0')]
upstream=next(p for p in root['pins'] if p['name']=='Result')['links'][0].split(':')[0]
allowed={('AnimGraph','AnimGraphNode_Root_0'),('AnimGraph',upstream)}
allowed|={('Update_CVarDrivenVariables','K2Node_CallFunction_'+n) for n in ['0','1','2','20']}
unexpected=[x for x in changes if (x['graph'],x['node']) not in allowed]
assert not unexpected,[(x['graph'],x['node']) for x in unexpected]
added=[dict(graph=k[0],node=k[1],title=new[k]['title'],properties=new[k]['properties'],pins=new[k]['pins']) for k in new.keys()-old.keys()]
assert len([x for x in added if not x['node'].startswith('EdGraphNode_Comment')])==4
result=dict(original_nodes=len(old),retained_nodes=len(old),changed_original_nodes=changes,
    added_nodes=added,unexpected_changes=unexpected,
    scope='Actual exported Blueprint edges and pin defaults. Original animation graph remains upstream of additive spine lean; four scoped cvar inputs differ.')
with (OUT/'graph-parity-check.json').open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(dict(retained_nodes=len(old),changed_nodes=[(x['graph'],x['node']) for x in changes],added=len(added),passed=True)))
