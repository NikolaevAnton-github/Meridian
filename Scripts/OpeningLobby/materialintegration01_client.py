"""Foreground official Epic MCP calls using the existing local client."""
import json
import sys
import time
from pathlib import Path
from functionalbuild01_client import call

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/OpeningLobby/MaterialIntegration01/WorkerFresh01'

def work(operation,argument=''):
    result=call('call_tool',{'toolset_name':'Game.Scripts.OpeningLobby.materialintegration01_tools.OpeningLobbyMaterialIntegration01Tools','tool_name':'action','arguments':{'operation':operation,'argument':argument}})
    value=json.loads(result['content'][0]['text'])['returnValue']
    if isinstance(value,str):value=json.loads(value)
    assert not isinstance(value,dict) or not value.get('error'),value
    return value

def captures(folder,views):
    for view in views:
        p=OUT/folder/(view+'.png')
        assert not p.exists(),p
        work('capture_camera',folder+':'+view)
        time.sleep(3)
        deadline=time.monotonic()+25
        while True:
            ready=work('capture_ready',folder+':'+view)
            if ready['ready']:break
            assert time.monotonic()<deadline,ready
            time.sleep(1)
        work('capture_shoot',folder+':'+view)
        deadline=time.monotonic()+20
        while not p.exists() and time.monotonic()<deadline:time.sleep(.2)
        assert p.exists(),view
        time.sleep(.5)
        print(json.dumps(dict(view=view,bytes=p.stat().st_size)),flush=True)

if __name__=='__main__':
    if sys.argv[1]=='captures':captures(sys.argv[2],sys.argv[3:])
    elif sys.argv[1]=='walk_wait':
        deadline=time.monotonic()+55
        while True:
            value=work('walk_status')
            if value['done']:
                print(json.dumps(value));break
            assert time.monotonic()<deadline,value
            time.sleep(2)
    else:print(json.dumps(work(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else '')))
