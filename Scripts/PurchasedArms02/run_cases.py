"""Foreground driver for uninterrupted input checks, reusing the Epic client."""
import json
import sys
import time
from pathlib import Path
from client import epic, work
OUT = Path(__file__).resolve().parents[2] / 'Saved/PurchasedArms02/Worker'

def run(case):
    work('performance')
    state = work('state','before-'+case['name'])
    if state['pie']:
        epic('EditorToolset.EditorAppToolset','StopPIE')
    options={'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':.5}
    if case.get('spawn',True):
        options['startTransform']={'location':{'x':-1600,'y':0,'z':case.get('height',100)},'rotation':{'pitch':0,'yaw':0,'roll':0},'scale':{'x':1,'y':1,'z':1}}
    epic('EditorToolset.EditorAppToolset','StartPIE',{'options':options})
    work('performance')
    work('verify',json.dumps(case))
    deadline = time.monotonic() + case['duration'] * 5 + 20
    while True:
        time.sleep(.8)
        status = work('verify_status')
        if status['done']:
            print(json.dumps(status),flush=True)
            assert not status['error'], status
            break
        assert time.monotonic()<deadline,status
    epic('EditorToolset.EditorAppToolset','StopPIE')

if __name__ == '__main__':
    for case in json.loads((OUT / sys.argv[1]).read_text()):
        run(case)
