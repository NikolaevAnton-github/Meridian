"""One trial, save/reopen evidence, native stills and true-input walk."""
import time,json
from uppervoid01_spatial_client import work,captures,OUT
from uppervoid01_spatial_diagnostics import capture_set,start
print(json.dumps(work('snapshot','Candidate')),flush=True)
print(json.dumps(work('audit','Candidate')),flush=True)
print(json.dumps(work('reopen')),flush=True)
print(json.dumps(work('audit','Reopened')),flush=True)
capture_set('Trial01',['close-column-90','lateral-column-90','entrance-axis-90','east-aisle-90','west-aisle-90','vertical-up-90','floor-reflection-90','stone-reflection-90'])
work('capture_prepare','Final')
try:
    start();time.sleep(2)
    work('runtime_walk_start');deadline=time.monotonic()+120
    while True:
        time.sleep(5);s=work('runtime_walk_status')
        print(json.dumps({k:s[k] for k in ['done','passed','elapsed','step','sample_count','error']}),flush=True)
        if s['done']:
            assert s['passed'],s;break
        assert time.monotonic()<deadline,s
    pose=work('capture_camera','Final:entrance-axis-90')
    (OUT/'Performance').mkdir(exist_ok=True)
    (OUT/'Performance/Final-pose-request.json').write_text(json.dumps(pose,indent=2))
    time.sleep(3)
    work('runtime_perf_start','Final');deadline=time.monotonic()+40
    while True:
        time.sleep(2);s=work('runtime_perf_status')
        if s['done']:break
        assert time.monotonic()<deadline,s
    print(json.dumps(s),flush=True)
finally:
    if work('state')['pie']:work('stop');time.sleep(2)
    work('capture_restore','Final')
print(json.dumps(work('snapshot','TrialHandoff')),flush=True)
