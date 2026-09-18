import json
from pathlib import Path
OUT=Path(__file__).resolve().parents[2]/'Saved/PurchasedArms02/Worker'
cases=[]
for label,moving,aim,key in [('MovingHipReload',True,False,'R'),('MovingAimEmpty',True,True,'E'),
    ('StandingAimReload',False,True,'R'),('StandingHipEmpty',False,False,'E')]:
    events=([[0,'W',1]] if moving else [])+([[0,'RightMouseButton',1]] if aim else [])+[[2,key,1],[2.08,key,0]]
    cases.append(dict(name='Views01-'+label,duration=11,events=events))
(OUT/'video-cases01.json').write_text(json.dumps(cases,indent=2))
events=[[.3,'V',1],[.38,'V',0],[1,'LeftMouseButton',1],[3,'LeftMouseButton',0],
    [4,'RightMouseButton',1],[4.6,'LeftMouseButton',1],[6,'LeftMouseButton',0],
    [6.5,'MiddleMouseButton',1],[6.58,'MiddleMouseButton',0],[7.3,'LeftMouseButton',1],[8.6,'LeftMouseButton',0],
    [9,'RightMouseButton',0],[9.5,'E',1],[9.58,'E',0]]
(OUT/'feedback-cases01.json').write_text(json.dumps([dict(name='Feedback01-Shooting',duration=14,events=events,audio=True)],indent=2))
