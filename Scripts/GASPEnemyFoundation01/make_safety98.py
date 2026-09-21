"""Compose focused cases using the retained input, support and recording seams."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
base = dict(fps=30, profile=1, pilot=True, flying=True, inspection_view=True, location=[-600,60,50])
burst = [[.05,'@track','spine_03'],[.1,'LeftControl',1],[.2,'F7',1],[.3,'F7',0],[.4,'LeftControl',0],
         [.6,'V',1],[.7,'V',0],[1.2,'LeftMouseButton',1],[2.2,'LeftMouseButton',0]]
cases = [
    dict(base,name='Pilot10-FallResume',duration=12,events=burst+[[2.5,'@move',{'direction':[0,-1,0],'walk':True}],
         [2.6,'@track','pelvis'],[10,'@move',{'direction':[0,0,0]}]]),
    dict(base,name='Pilot10-Interrupt',duration=18,interrupt_and_kill=True,events=burst+[[2.6,'@track','spine_03']]),
    dict(base,name='Pilot10-Blocked',duration=13,events=burst+[[3,'@environment','ceiling'],[7.5,'@environment','clear_ceiling']]),
    dict(base,name='Pilot10-Unsupported',duration=11,platform=True,remove_support=True,follow_fall=True,
         events=burst),
    dict(base,name='Pilot10-DeathCorpse',duration=6,events=[[.05,'@track','spine_03'],[.6,'V',1],[.7,'V',0],
         [1.2,'LeftMouseButton',1],[2.2,'LeftMouseButton',0]])
]
cases[3]['location']=[30350,33060,1050]
(ROOT/'cases-pilot10.json').write_text(json.dumps(cases,indent=2),encoding='utf-8')
