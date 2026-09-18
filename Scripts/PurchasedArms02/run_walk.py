"""Run the retained lobby verifier to completion through official Epic MCP."""
import json
import time
from client import epic,work
assert not work('state','before-walk')['pie']
epic('EditorToolset.EditorAppToolset','StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':.5}})
work('walk')
deadline=time.monotonic()+180
while True:
    time.sleep(1)
    result=work('walk_status')
    if result['done']:
        print(json.dumps(result))
        assert result['passed'],result
        break
    assert time.monotonic()<deadline,result
epic('EditorToolset.EditorAppToolset','StopPIE')
