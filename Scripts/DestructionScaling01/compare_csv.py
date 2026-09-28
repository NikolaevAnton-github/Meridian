"""Read-only whole-frame CSV comparison. Keep details in Saved, print a small summary."""
import csv
import json
import statistics
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
def read(name,phase):
    p=ROOT/'Saved/Profiling/CSV'/('LobbyColumnsPerf02-'+name+'-'+phase+'.csv')
    with p.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.reader(f))
    indices=[i for i,r in enumerate(rows) if r and r[0]=='EVENTS']
    header=rows[indices[-1]]
    data=[r for r in rows[indices[0]+1:indices[-1]] if r and r[0]!='EVENTS'][5:-5]
    result={}
    for i,key in enumerate(header):
        try:values=[float(r[i]) for r in data if i<len(r)]
        except ValueError:continue
        if values:result[key]=statistics.median(values)
    return result
before,after=sys.argv[1:3]
report={}
for phase in ['intact','moving','settled']:
    a,b=read(before,phase),read(after,phase)
    keys=set(a)|set(b)
    report[phase]={k:{'before':a.get(k),'after':b.get(k),'delta':b.get(k,0)-a.get(k,0)} for k in keys}
(ROOT/'Saved/DestructionScaling01'/('compare-'+before+'-'+after+'.json')).write_text(json.dumps(report,indent=2))
for phase,metrics in report.items():
    print(phase,json.dumps({k:metrics.get(k) for k in ['FrameTime','GameThreadTime','GPUTime']}))
print('settled increases',json.dumps(sorted([(k,v['delta']) for k,v in report['settled'].items()
    if any(s in k.lower() for s in ['physics','chaos','gamethread','tick','task','wait'])],key=lambda x:-x[1])[:12]))
