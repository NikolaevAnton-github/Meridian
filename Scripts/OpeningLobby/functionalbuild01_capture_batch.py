"""Foreground capture orchestration; waits for each native image to be written."""
import json
import sys
import time
from functionalbuild01_client import call
from functionalbuild01_data import OUT

def work(operation,argument=''):
    r=call('call_tool',{'toolset_name':'Game.Scripts.OpeningLobby.functionalbuild01_tools.OpeningLobbyFunctionalBuild01Tools','tool_name':'action','arguments':{'operation':operation,'argument':argument}})
    r=json.loads(r['content'][0]['text'])['returnValue']
    r=json.loads(r) if isinstance(r,str) else r
    assert not isinstance(r,dict) or not r.get('error'),r
    return r

if __name__=='__main__':
    status=work('status');assert status['done'] and status['passed'],status
    views=sys.argv[1:] or ['entrance-90','inner-90','context-90','aisle-90','aisle-negative-90','inner-door-positive-90','inner-door-negative-90','elevator-detail-90','checkpoint-context-90','room-junction-90','column-contact-90','C1-90','C2-90']
    for view in views:
        work('capture_camera',view);time.sleep(2)
        work('capture_shoot',view)
        path=OUT/(view+'.png');deadline=time.monotonic()+15
        while not path.is_file() and time.monotonic()<deadline:time.sleep(.2)
        assert path.is_file(),view
        time.sleep(.5);print(json.dumps({'view':view,'bytes':path.stat().st_size}),flush=True)
