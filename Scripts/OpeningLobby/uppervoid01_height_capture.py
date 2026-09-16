"""Native standing evidence using the established capture adapter."""
import types,json
from uppervoid01_height_unreal import ROOT,OUT,MAP,SOURCE,guard,write,settings
p=ROOT/'Scripts/OpeningLobby/paintermetal01_capture.py'
s=p.read_text().replace('from paintermetal01_unreal import','from uppervoid01_height_unreal import')
s=s.replace("['Before','Trial01','Final']","['Before','Trial01','Trial02','Trial03','Final']")
s=s.replace("lighting='Original owner lights and postprocess; no adjustments'","lighting='Baseline lighting' if folder=='Before' else 'UpperVoid01 scheduled lighting and postprocess; intentionally different from baseline'")
base=types.ModuleType('uppervoid_capture');exec(compile(s,str(p),'exec'),base.__dict__)
base.cap.VIEWS={'entrance-axis-90':(-1850,0,0,10),'inner-axis-90':(1850,0,180,10),
 'east-aisle-90':(-1150,980,0,55),'west-aisle-90':(1150,-980,180,55),
 'column-up-90':(-600,180,25,65),'vertical-up-90':(0,0,0,89),
 'entrance-corner-90':(-1850,0,160,55),'inner-corner-90':(1850,0,20,55),
 'checkpoint-90':(-1690,170,198,-12),'elevator-90':(2620,-170,22,0),
 'floor-reflection-90':(-1100,0,0,-24),'stone-reflection-90':(-1570,365,47,12)}
def run(operation,argument):
    r=base.run(operation,argument)
    if operation=='shoot':
        folder,_,view=argument.partition(':')
        r['exposure']='Native fixed manual exposure, bias -5, physical camera disabled; scene-lighting changes intentional'
        write(folder+'/'+view+'-camera',r)
    return r
