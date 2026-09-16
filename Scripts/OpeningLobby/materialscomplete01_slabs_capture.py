"""Reused native standing camera capture; no glass controls or cvar changes."""
import types
from materialscomplete01_slabs_unreal import ROOT,OUT,MAP,SOURCE,guard,write,settings
p=ROOT/'Scripts/OpeningLobby/paintermetal01_capture.py'
s=p.read_text().replace('from paintermetal01_unreal import','from materialscomplete01_slabs_unreal import')
base=types.ModuleType('slabs_capture');exec(compile(s,str(p),'exec'),base.__dict__)
base.cap.VIEWS={'entrance-90':(-1850,0,180,12),'inner-90':(1850,0,0,3),
 'side-aisle-90':(-1150,980,0,0),'bays-context-90':(-700,200,35,15),
 'stone-oblique-90':(-1500,420,145,18),'ceiling-up-90':(-500,180,20,55),
 'soffit-up-90':(-1710,925,165,35),'checkpoint-90':(-1690,170,198,-12),
 'elevator-90':(2620,-170,22,0),'whole-hall-90':(1800,0,180,6),
 'column-face-90':(-1260,450,90,12),'column-corner-90':(-1570,365,47,12),
 'broad-wall-90':(-740,980,90,10),'room-wall-90':(-1710,925,180,10),
 'portal-return-90':(-2690,180,144,14),'trim-head-90':(-2540,0,180,36)}
run=base.run
