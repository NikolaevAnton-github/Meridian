"""Controller-requested bounded capsule and authored camera-action checks."""
import json
from pathlib import Path
OUT=Path(__file__).resolve().parents[2]/'Saved/PurchasedArms02/Worker'
def tap(t,k): return [[t,k,1],[t+.08,k,0]]
cases=[{'name':'Correction01-Capsule','duration':12,'events':sorted(
    tap(.2,'C')+tap(.9,'C')+tap(1.8,'C')+[[2.6,'@ceiling',1]]+tap(3.2,'C')+
    [[4.3,'W',1],[5.8,'W',0],[6,'D',1],[10,'D',0]],key=lambda e:e[0])}]
for enabled in [False,True]:
    events=(tap(.1,'L') if enabled else [])+[[.5,'T',1],[1,'T',0]]+(tap(7.2,'L') if enabled else [])
    cases.append({'name':'Correction01-Camera'+('On' if enabled else 'Off'),'duration':9,'events':events})
(OUT/'correction-cases01.json').write_text(json.dumps(cases,indent=2))
