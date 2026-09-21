"""Final assembly checks on one representative and the retained three slots."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
base = dict(fps=30,profile=1,pilot=False,flying=True,inspection_view=True)
moving = json.loads((ROOT/'cases-pilot09.json').read_text())[0]
moving.update(base,name='Final01-MovingRifle',location=[-600,-220,100],duration=7)
interrupt = json.loads((ROOT/'cases-pilot11.json').read_text(encoding='utf-8-sig'))[1]
interrupt.update(base,name='Final01-FallInterruptResume',location=[-600,-260,50],duration=20)
interrupt['events'] += [[2.5,'@move',{'direction':[-1,0,0],'walk':True}],[18.5,'@move',{'direction':[0,0,0]}]]
interrupt['events'].sort(key=lambda x:x[0])
death = json.loads((ROOT/'cases-pilot10.json').read_text())[-1]
death.update(base,name='Final01-DeathCorpse',location=[-600,-260,50])
cases = [
    dict(base,name='Final01-ThreeRendered',duration=3,location=[-420,0,240],look_at=[-950,0,90],events=[]),
    moving,
    dict(base,name='Final01-LegArm',duration=8,location=[-600,-200,105],events=[[.05,'@track','calf_l'],
         [1,'LeftMouseButton',1],[1.12,'LeftMouseButton',0],[1.4,'@track','pelvis'],[4,'@arm_trunk',1600]]),
    interrupt,
    death,
    dict(base,name='Final01-ControlsSlow',duration=9,inspection_view=False,location=[-600,-260,80],events=[
         [.05,'@track','spine_03'],[.1,'LeftControl',1],[.2,'F7',1],[.25,'F7',0],
         [.3,'F8',1],[.35,'F8',0],[.4,'F9',1],[.45,'F9',0],[.5,'LeftControl',0],
         [.6,'V',1],[.7,'V',0],[1,'LeftMouseButton',1],[1.3,'LeftMouseButton',0],
         [1.8,'Y',1],[1.9,'Y',0],[2,'W',1],[2.2,'W',0],
         [2.3,'LeftMouseButton',1],[3.5,'LeftMouseButton',0],
         [4,'F6',1],[4.1,'F6',0],[4.8,'Y',1],[4.9,'Y',0],
         [5.5,'F10',1],[5.6,'F10',0],[6.2,'F10',1],[6.3,'F10',0],
         [7,'LeftControl',1],[7.1,'F7',1],[7.15,'F7',0],
         [7.2,'F8',1],[7.25,'F8',0],[7.3,'F9',1],[7.35,'F9',0],[7.4,'LeftControl',0]])
]
(ROOT/'cases-final01.json').write_text(json.dumps(cases,indent=2),encoding='utf-8')
