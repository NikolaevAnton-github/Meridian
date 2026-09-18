"""Collect ordinary-speed screen video alongside uninterrupted evaluated-pose evidence."""
import json
import subprocess
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from client import epic,work
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/PurchasedArms02/Worker'

def run(case,pid):
    work('performance')
    assert not work('state','before-'+case['name'])['pie']
    epic('EditorToolset.EditorAppToolset','StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':.5,
        'startTransform':{'location':{'x':-1600,'y':0,'z':100},'rotation':{'pitch':0,'yaw':0,'roll':0},'scale':{'x':1,'y':1,'z':1}}}})
    ready=OUT/'Video'/(case['name']+'.ready.json')
    process=subprocess.Popen([sys.executable,str(ROOT/'Scripts/PurchasedArms02/capture02.py'),str(pid),case['name'],str(case['duration']+2)],
        creationflags=subprocess.CREATE_NO_WINDOW)
    deadline=time.monotonic()+10
    while not ready.exists():
        assert process.poll() is None, 'Capture stopped before becoming ready'
        assert time.monotonic()<deadline
        time.sleep(.05)
    work('verify',json.dumps(case))
    deadline=time.monotonic()+case['duration']*5+20
    while True:
        time.sleep(.8)
        result=work('verify_status')
        if result['done']:
            print(json.dumps(result),flush=True)
            assert not result['error'],result
            break
        assert time.monotonic()<deadline,result
    assert process.wait(timeout=15)==0,'Capture failed'
    epic('EditorToolset.EditorAppToolset','StopPIE')

if __name__=='__main__':
    for row in json.loads((OUT/sys.argv[1]).read_text()): run(row,int(sys.argv[2]))
