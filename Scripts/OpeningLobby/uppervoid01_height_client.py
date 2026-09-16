"""Official Epic foreground client; all outputs isolated to UpperVoid01."""
import json,sys,types,time
from pathlib import Path
from functionalbuild01_client import call
OUT=Path(__file__).resolve().parents[2]/'Saved/OpeningLobby/UpperVoid01/HeightCorrection01/Worker'
def work(operation,argument=''):
    r=call('call_tool',dict(toolset_name='Game.Scripts.OpeningLobby.uppervoid01_height_tools.OpeningLobbyUpperVoid01HeightTools',tool_name='action',arguments=dict(operation=operation,argument=argument)))
    v=json.loads(r['content'][0]['text'])['returnValue']
    if isinstance(v,str):v=json.loads(v)
    assert not isinstance(v,dict) or not v.get('error'),v
    return v
def captures(folder,views):
    p=Path(__file__).with_name('materialscomplete01_client.py');m=types.ModuleType('uppervoid_capture_client');m.__file__=str(p)
    exec(compile(p.read_text(),str(p),'exec'),m.__dict__);m.OUT=OUT;m.work=work
    return m.captures(folder,views)
if __name__=='__main__':
    if sys.argv[1]=='captures':captures(sys.argv[2],sys.argv[3:])
    elif sys.argv[1]=='performance':
        tag=sys.argv[2] if len(sys.argv)>2 else 'Final'
        p=OUT/tag/'entrance-axis-90-camera.json';original=p.read_bytes()
        try:
            pose=work('capture_camera',tag+':entrance-axis-90')
            (OUT/'Performance').mkdir(exist_ok=True)
            (OUT/('Performance/'+tag+'-pose-request.json')).write_text(json.dumps(pose,indent=2))
        finally:p.write_bytes(original)
        time.sleep(3)
        work('runtime_perf_start',tag)
        deadline=time.monotonic()+40
        while True:
            time.sleep(2);s=work('runtime_perf_status')
            if s['done']:break
            assert time.monotonic()<deadline,s
        print(json.dumps(s))
    elif sys.argv[1]=='walk':
        work('runtime_walk_start');deadline=time.monotonic()+240
        while True:
            time.sleep(5);s=work('runtime_walk_status')
            print(json.dumps({k:s[k] for k in ['done','passed','elapsed','step','sample_count','error']}),flush=True)
            if s['done']:
                assert s['passed'],s;break
            assert time.monotonic()<deadline,s
    else:print(json.dumps(work(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else '')))
