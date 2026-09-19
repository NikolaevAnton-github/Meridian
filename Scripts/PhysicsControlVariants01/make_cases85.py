"""Focused actual input cases, each in a fresh PIE session."""
import json
from pathlib import Path
OUT=Path(__file__).resolve().parents[2]/'Saved/CombatSlice01/PhysicsControlVariants01/Worker'

def case(name,events,duration=7,**kw):
    return dict(name=name,events=events,duration=duration,fps=60,**kw)

reactions=[]
for n in range(1,7):
    y=-320+((n-1)%3)*320
    x=-950+((n-1)//3)*320
    reactions.append(case(f'Candidate01-Torso{n}',[[.05,'@track','spine_03'],[1.0,'LeftMouseButton',1],[1.07,'LeftMouseButton',0]],
        profile=n,location=[x-240,y-35,100]))
(OUT/'cases-reactions01.json').write_text(json.dumps(reactions,indent=2),encoding='utf-8')
smoke=[case('Candidate01-Smoke',[[.05,'@track','spine_03'],[1,'LeftMouseButton',1],[1.07,'LeftMouseButton',0]],
    duration=6,profile=1,location=[-1190,-355,100])]
(OUT/'cases-smoke01.json').write_text(json.dumps(smoke,indent=2),encoding='utf-8')
