"""Audit the exact build, immutable sources and saved focused evidence."""
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/DestructionScaling01'
build,after,focused,transitions=sys.argv[1:5]
def read(name):
    data=(OUT/(name+'.json')).read_bytes()
    return json.loads(data.decode('utf-16' if data.startswith(b'\xff\xfe') else 'utf-8-sig'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
checks={}
build_report=read(build)
checks['full_build']=build_report['exit_code']==0
checks['exact_build_identity']=all(digest(ROOT/p)==h for p,h in build_report['hashes'].items())
provenance=json.loads((ROOT/'Assets/Source/DestructionScaling01/Candidate01/provenance.json').read_text())
checks['immutable_sources']=all(digest(ROOT/x['path'])==x['sha256'] for x in provenance['inputs'])
checks['registry_unchanged']=read('registry-final-validate')['passed']
for name in (focused,transitions):
    evidence=read(name)
    checks[name]=bool(evidence.get('complete')) and all(evidence['checks'].values())
checks['history_and_world']=all(read('history-and-world-02').values())
checks['final_world_recreated']=read('final-world-recreated')=={
    'columns':16,'compact_sections':576,'query_errors':0,'render_errors':0,'active_fragments':0}
workloads={}
for name in ('before-02',after):
    evidence=read(name)
    checks[name+'_complete']=bool(evidence.get('complete'))
    samples=evidence['samples']
    checks[name+'_shots']=samples['settled']['rifle']['shots']-samples['intact']['rifle']['shots']==18
    for label,state in samples.items():
        checks[name+'_'+label+'_mapping']=all(c['cladding'].get('query_mapping_errors',0)==0 and
            c['cladding'].get('render_mismatches',0)==0 for c in state['columns'])
    workloads[name]={label:{'shots':s['rifle']['shots'],
        'ceramic_entries':sum(c['cladding']['debris'] for c in s['columns']),
        'compact_sections':sum(c['cladding'].get('compact_sections',0) for c in s['columns']),
        'shared_components':s['shared_components'],
        'shared_instances':s['shared_instances']} for label,s in samples.items()}
report={'passed':all(checks.values()),'checks':checks,'build':build,'workloads':workloads}
(OUT/'delivery-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
raise SystemExit(0 if report['passed'] else 1)
