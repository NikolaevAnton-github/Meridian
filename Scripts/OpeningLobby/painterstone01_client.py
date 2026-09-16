"""Foreground calls through the existing official Epic MCP client."""
import json
import sys
import time
from pathlib import Path
from functionalbuild01_client import call

OUT=Path(__file__).resolve().parents[2]/'Saved/OpeningLobby/PainterStone01/Worker/Correction01'

def work(operation,argument=''):
    result=call('call_tool',dict(toolset_name='Game.Scripts.OpeningLobby.painterstone01_tools.OpeningLobbyPainterStone01Tools',
        tool_name='action',arguments=dict(operation=operation,argument=argument)))
    value=json.loads(result['content'][0]['text'])['returnValue']
    if isinstance(value,str):value=json.loads(value)
    assert not isinstance(value,dict) or not value.get('error'),value
    return value

def captures(folder,views):
    for view in views:
        target=OUT/folder/(view+'.png')
        assert not target.exists(),target
        work('capture_camera',folder+':'+view)
        time.sleep(3)
        deadline=time.monotonic()+20
        while True:
            ready=work('capture_ready',folder+':'+view)
            if ready['ready']:break
            assert time.monotonic()<deadline,ready
            time.sleep(1)
        work('capture_shoot',folder+':'+view)
        deadline=time.monotonic()+20
        while not target.exists() and time.monotonic()<deadline:time.sleep(.2)
        assert target.exists(),target
        print(json.dumps(dict(view=view,bytes=target.stat().st_size)),flush=True)

if __name__=='__main__':
    if sys.argv[1]=='captures':captures(sys.argv[2],sys.argv[3:])
    else:print(json.dumps(work(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else '')))
