"""Focused enemy cases using the retained combat runner and ordinary-speed recorder."""
import json
import sys
from pathlib import Path
from client69 import epic, work as native_work
import run68

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/EnemyPrototype01/Worker'
run68.OUT = OUT
captured = set()
def work(operation, argument=''):
    result = native_work(operation, argument)
    if operation == 'verify_status' and not result.get('done') and '--stills' in sys.argv:
        for at in [1.2, 2.35, 3.5, 6.3, 12.4, 14.4]:
            key = (result['name'], at)
            if result.get('t',0) >= at and key not in captured:
                captured.add(key)
                native_work('capture', result['name'] + '-' + str(at).replace('.', '_'))
    return result
run68.work = work

if __name__ == '__main__':
    if sys.argv[1] == 'probe':
        assert not epic('EditorToolset.EditorAppToolset', 'IsPIERunning')
        work('performance')
        try:
            epic('EditorToolset.EditorAppToolset','StartPIE',{'options':dict(bSimulate=False,playMode='PlayMode_InViewPort',warmupSeconds=1)})
            print(json.dumps(work('probe',sys.argv[2])))
        finally:
            epic('EditorToolset.EditorAppToolset','StopPIE')
            work('performance','restore')
    else:
        cases = [
            dict(name='IdleHitDeathReset', duration=16, fps=60, location=[-1570,0,100],
                 events=[[.5,'@track','spine_04'],[2,'LeftMouseButton',1],[2.04,'LeftMouseButton',-1],
                         [4.5,'LeftMouseButton',1],[4.54,'LeftMouseButton',-1],
                         [5.1,'LeftMouseButton',1],[5.14,'LeftMouseButton',-1],
                         [5.8,'LeftMouseButton',1],[5.84,'LeftMouseButton',-1],
                         [6.2,'LeftMouseButton',1],[6.24,'LeftMouseButton',-1],
                         [7,'@track','pelvis'],[13,'F6',1],[13.05,'F6',-1],[13.1,'@track','spine_04']]),
            dict(name='MovingHits', duration=10, fps=30, location=[-1570,0,100],
                 events=[[.4,'@track','spine_04'],[.6,'F7',1],[.65,'F7',-1],[2.2,'LeftMouseButton',1],[2.25,'LeftMouseButton',-1],
                         [4.8,'LeftMouseButton',1],[4.85,'LeftMouseButton',-1],[7,'F6',1],[7.05,'F6',-1]]),
            dict(name='HoldFirePresentation',duration=6,fps=60,location=[-1400,100,100],
                 events=[[.4,'@track','spine_04'],[2,'@fire_pose',1]]),
            dict(name='ActiveRagdollReset',duration=13,fps=60,location=[-1570,0,100],
                 events=[[.4,'@track','spine_04'],
                         [1,'LeftMouseButton',1],[1.04,'LeftMouseButton',-1],
                         [1.4,'LeftMouseButton',1],[1.44,'LeftMouseButton',-1],
                         [1.8,'LeftMouseButton',1],[1.84,'LeftMouseButton',-1],
                         [2.2,'LeftMouseButton',1],[2.24,'LeftMouseButton',-1],
                         [2.6,'F6',1],[2.64,'F6',-1],
                         [3.4,'LeftMouseButton',1],[3.44,'LeftMouseButton',-1],
                         [3.8,'LeftMouseButton',1],[3.84,'LeftMouseButton',-1],
                         [4.2,'LeftMouseButton',1],[4.24,'LeftMouseButton',-1],
                         [4.6,'LeftMouseButton',1],[4.64,'LeftMouseButton',-1],
                         [5,'@track','pelvis'],[12,'F6',1],[12.04,'F6',-1],[12.1,'@track','spine_04']]),
        ]
        for case in cases:
            if len(sys.argv)>3 and sys.argv[3] not in case['name']: continue
            case['name'] = sys.argv[1] + '-' + case['name']
            if len(sys.argv)>2 and sys.argv[2] != '-': case['video_pid']=int(sys.argv[2])
            run68.run(case)
