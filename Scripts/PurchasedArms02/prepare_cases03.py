"""Bounded acceptance inputs for camera, clearance and action transitions."""
import json
from pathlib import Path
OUT=Path(__file__).resolve().parents[2]/'Saved/PurchasedArms02/Worker'
def case(name,duration,events,**kwargs):
    return dict(name='Interactions03-'+name,duration=duration,events=sorted(events,key=lambda e:e[0]),**kwargs)
def tap(t,key): return [[t,key,1],[t+.08,key,0]]
rows=[
 case('Ordinary',11,[[0,'W',1],[2.5,'RightMouseButton',1],[3,'W',0],[3,'S',1],[3.5,'MouseX',12],[7,'S',0],[7.5,'RightMouseButton',0]]+tap(1,'R')+tap(1.4,'R')+tap(2,'LeftMouseButton')+tap(6,'LeftMouseButton')),
 case('Empty',11,[[0,'W',1],[0,'RightMouseButton',1],[2,'RightMouseButton',0],[3,'W',0],[3,'S',1],[4,'RightMouseButton',1],[7,'S',0]]+tap(1,'E')+tap(1.5,'E')+tap(2.6,'LeftMouseButton')+tap(6,'LeftMouseButton')),
 case('QuickCanted',11,[[0,'W',1],[0,'RightMouseButton',1],[5,'W',0],[5.5,'RightMouseButton',0]]+tap(.8,'MiddleMouseButton')+tap(2,'Q')+tap(2.4,'Q')+tap(6,'C')+tap(8,'C')),
 case('Jump',5,tap(1,'SpaceBar')+tap(3,'SpaceBar')),
 case('BlockedCrouch',7,tap(.2,'C')+[[1,'@ceiling',1]]+tap(1.5,'C')+[[3,'W',1],[4.5,'W',0]]),
 case('LongFall',8,[[0,'W',1],[2,'W',0]]+tap(.3,'SpaceBar')+tap(1,'R')+tap(3,'R'),fixture='platform'),
 case('Camera',8,[[0,'W',1],[1,'RightMouseButton',1],[3,'RightMouseButton',0],[6,'W',0]]+tap(2,'L')+tap(5,'L')),
 case('InteractVariants',27,sum((tap(.5+i*2.5,'X') for i in range(10)),[])),
 case('WallRun',6,[[0,'D',1],[.4,'LeftShift',1],[4,'LeftShift',0],[4.5,'D',0]]),
 case('WallSprint',6,[[0,'D',1],[.4,'LeftAlt',1],[4,'LeftAlt',0],[4.5,'D',0]]),
 case('RunTransitions',12,[[0,'W',1],[1,'LeftShift',1],[2,'RightMouseButton',1],[3,'LeftShift',0],[4,'RightMouseButton',0],[5,'LeftAlt',1],[6,'RightMouseButton',1],[7,'LeftAlt',0],[8,'RightMouseButton',0],[10,'W',0]]+tap(8.5,'C')+tap(10.5,'C')),
]
(OUT/'interaction-cases03.json').write_text(json.dumps(rows,indent=2))
